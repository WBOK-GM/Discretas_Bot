import pika
import json
import os
from fastapi import FastAPI, Request

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
print(f"API iniciada - TOKEN: {TELEGRAM_BOT_TOKEN}")

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'admin')
QUEUE_NAME = 'drive_tasks'

app = FastAPI()

def create_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )

try:
    connection = create_connection()
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    print("[API] Conectado a RabbitMQ correctamente.")
except Exception as e:
    print(f"[API] ERROR al conectar con RabbitMQ: {e}")
    connection = None
    channel = None

def publish_to_rabbitmq(message_body: dict):
    global connection, channel
    try:
        if not connection or connection.is_closed:
            connection = create_connection()
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message_body),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"[API] Mensaje enviado a RabbitMQ: {message_body}")
    except Exception as e:
        print(f"[API] Error al publicar en RabbitMQ: {e}")

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
    return {"Hello": "TAI on Telegram!"}
