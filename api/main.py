import pika
import json
import os
from fastapi import FastAPI, Request

# --- Leemos TODAS las configuraciones desde las variables de entorno ---
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
print(f"!!  API INICIADA - TOKEN LEÍDO: {TELEGRAM_BOT_TOKEN}  !!")
print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')
QUEUE_NAME = 'drive_tasks'
# ---

app = FastAPI()

def publish_to_rabbitmq(message_body: dict):
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message_body),
            properties=pika.BasicProperties(delivery_mode=2))
        print(f" [API] Mensaje enviado a RabbitMQ: {message_body}")
        connection.close()
    except pika.exceptions.AMQPConnectionError as e:
        print(f" [API] ERROR: No se pudo conectar a RabbitMQ. {e}")

@app.post(f"/webhook/{TELEGRAM_BOT_TOKEN}")
async def process_telegram_update(request: Request):
    data = await request.json()
    if "message" in data and "text" in data["message"]:
        message_to_worker = {
            "chat_id": data["message"]["chat"]["id"],
            "text": data["message"]["text"]
        }
        publish_to_rabbitmq(message_to_worker)
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"Hello": "WAI on Telegram!"}