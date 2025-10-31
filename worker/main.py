import pika
import time
import json
import os
import pickle
import traceback
import sys
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import httpx
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Leemos las claves desde las variables de entorno
API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_KEY or not TELEGRAM_BOT_TOKEN:
    print("!! ERROR FATAL: Faltan las variables de entorno GEMINI_API_KEY o TELEGRAM_BOT_TOKEN !!")
    sys.exit(1)

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
QUEUE_NAME = 'drive_tasks'

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SHARED_FOLDER = '/app/shared'
CREDENTIALS_PATH = os.path.join(SHARED_FOLDER, 'credentials.json')
TOKEN_PATH = os.path.join(SHARED_FOLDER, 'token.pickle')

# ... (Las funciones get_drive_service y search_drive_files no cambian) ...
def get_drive_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds)

def search_drive_files(query):
    try:
        service = get_drive_service()
        results = service.files().list(q=query, pageSize=10, fields="files(id, name, webViewLink)").execute()
        items = results.get('files', [])
        if not items:
            return "No se encontraron archivos que coincidan con tu búsqueda."
        file_list = "He encontrado estos archivos para ti:\n"
        for item in items:
            file_list += f"- [{item['name']}]({item['webViewLink']})\n"
        return file_list
    except Exception as e:
        return f"Ha ocurrido un error al buscar en Google Drive: {e}"

def generate_drive_query(user_prompt):
    try:
        template = """
        Traduce la siguiente petición a una consulta técnica para la API de Google Drive.
        Si la petición no parece una solicitud para buscar archivos, responde con la palabra clave 'INVALID_QUERY'.
        Responde ÚNICAMENTE con la consulta técnica o con 'INVALID_QUERY'.
        No incluyas NUNCA acentos graves (`) ni ningún tipo de formato de código.

        Ejemplos:
        Petición: "búscame el informe de ventas en pdf"
        Respuesta: name contains 'informe de ventas' and mimeType='application/pdf'

        Petición: "hola como estas"
        Respuesta: INVALID_QUERY
        
        Petición: "¿qué tiempo hace?"
        Respuesta: INVALID_QUERY

        Petición: "{peticion_usuario}"
        Respuesta: 
        """
        prompt_template = PromptTemplate(input_variables=["peticion_usuario"], template=template)
        
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=API_KEY)
        
        chain = prompt_template | llm
        
        response = chain.invoke({"peticion_usuario": user_prompt})
        
        drive_query = response.content.strip()
        
        print(f"[Worker] Query de LangChain: '{drive_query}'")
        return drive_query
        
    except Exception as e:
        print(f"Error al generar query con LangChain: {e}")
        traceback.print_exc()
        return None

def send_telegram_message(chat_id, text):
    telegram_api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        with httpx.Client() as client:
            client.post(telegram_api_url, json=payload)
    except Exception as e:
        print(f"[Worker] Excepción al enviar mensaje a Telegram: {e}")

def callback(ch, method, properties, body):
    message = json.loads(body)
    chat_id = message.get("chat_id")
    user_prompt = message.get("text", "")
    print(f"\n[Worker] Mensaje recibido para chat {chat_id}: '{user_prompt}'")

    if not chat_id:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    
    drive_query = generate_drive_query(user_prompt)
    
    if drive_query is None:
        send_telegram_message(chat_id, "Lo siento, hubo un error al procesar tu petición.")
    elif drive_query == "INVALID_QUERY":
        send_telegram_message(chat_id, "No entendí tu solicitud. Por favor, pídeme que busque un archivo o documento en tu Drive.")
    else:
        send_telegram_message(chat_id, "Buscando en tu Drive, un momento...")
        search_results = search_drive_files(drive_query)
        send_telegram_message(chat_id, search_results)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    connection = None
    attempts = 10
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    for i in range(attempts):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
            print("[Worker] Conexión con RabbitMQ establecida.")
            break 
        except pika.exceptions.AMQPConnectionError:
            print(f"Falló la conexión. Reintentando en 5s ({i+1}/{attempts})")
            time.sleep(5)
    if not connection:
        return
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=False)
    print(f"[*] Worker listo. Esperando mensajes en la cola '{QUEUE_NAME}'.")
    channel.start_consuming()

if __name__ == '__main__':
    main()