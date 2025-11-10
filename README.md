# 🤖 Discretas Bot

Bot de Telegram inteligente que busca archivos en Google Drive utilizando lenguaje natural. Combina la API de Telegram, Google Gemini AI y Google Drive API para proporcionar una experiencia de búsqueda conversacional.

## 📋 Características

- **Búsqueda en lenguaje natural**: Realiza consultas en Drive usando peticiones conversacionales
- **Interpretación inteligente**: Utiliza Google Gemini AI para traducir solicitudes humanas a queries técnicas de la API de Drive
- **Soporte de múltiples formatos**: PDF, Word, Excel, Google Docs, Google Sheets, imágenes y más
- **Arquitectura basada en microservicios**: API FastAPI + Worker con comunicación mediante RabbitMQ
- **Despliegue con Docker**: Configuración completa con Docker Compose y Traefik como reverse proxy
- **Búsqueda en carpetas específicas**: Opción de limitar búsquedas a una carpeta particular de Drive

## 🏗️ Arquitectura

El proyecto sigue una arquitectura de microservicios con los siguientes componentes:

- **API (FastAPI)**: Recibe webhooks de Telegram y publica mensajes en RabbitMQ
- **Worker**: Procesa mensajes de la cola, interactúa con Gemini AI y busca en Google Drive
- **RabbitMQ**: Cola de mensajes para comunicación asíncrona entre API y Worker
- **Traefik**: Reverse proxy para enrutamiento de tráfico HTTP

## 🚀 Instalación

### Prerrequisitos

- Docker y Docker Compose instalados
- Bot de Telegram creado (obtén el token desde [@BotFather](https://t.me/botfather))
- API Key de Google Gemini AI
- Credenciales OAuth2 de Google Cloud para acceso a Drive API
- **Ngrok instalado** si trabajas en local

### Configuración

1. **Clona el repositorio**:
```bash
git clone https://github.com/WBOK-GM/Discretas_Bot.git
cd Discretas_Bot
```

2. **Configura las variables de entorno**:

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Telegram
TELEGRAM_BOT_TOKEN=tu_token_de_telegram

# Google APIs
GEMINI_API_KEY=tu_api_key_de_gemini
DRIVE_FOLDER_ID=id_de_carpeta_drive_opcional

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_USER=admin
RABBITMQ_PASS=tu_contraseña_segura
```

3. **Configura las credenciales de Google Drive**:

- Ve a [Google Cloud Console](https://console.cloud.google.com/)
- Crea un proyecto y habilita la Google Drive API
- Descarga las credenciales OAuth2 como JSON
- Guarda el archivo como `shared/credentials.json`

4. **Inicia los contenedores**:
```bash
docker compose up -d
```

5. **Crea el túnel ngrok en el puerto 80**

Si trabajas en local y quieres recibir el webhook correctamente, abre un túnel ngrok:

```bash
ngrok http 80
```

Obtén la URL pública generada por ngrok.

6. **Configura el webhook de Telegram**:

Usa la URL pública de ngrok para configurar el webhook:

```bash
curl -X POST "https://api.telegram.org/bot<TU_TOKEN>/setWebhook?url=https://tu-url-ngrok/api/webhook/<TU_TOKEN>"
```

## 📦 Estructura del Proyecto

```
Discretas_Bot/
├── api/                      # Servicio API FastAPI
│   ├── Dockerfile
│   ├── main.py              # Endpoint webhook y publicación a RabbitMQ
│   └── requirements.txt
├── worker/                   # Servicio Worker
│   ├── Dockerfile
│   ├── main.py              # Procesamiento de mensajes y búsqueda en Drive
│   └── requirements.txt
├── shared/                   # Archivos compartidos (credenciales)
│   ├── credentials.json     # Credenciales OAuth2 de Google
│   └── token.pickle         # Token de autenticación (generado automáticamente)
├── docker-compose.yml        # Configuración de servicios
├── .dockerignore
├── .gitignore
└── README.md
```

## 💬 Uso

Una vez configurado el bot, puedes interactuar con él enviando mensajes como:

- "Búscame archivos PDF sobre matemáticas"
- "Encuentra documentos Word con contratos"
- "Muéstrame las fotos del proyecto"
- "Busca hojas de cálculo con presupuesto"
- "Archivos sobre inteligencia artificial"

El bot interpretará tu solicitud y buscará en tu Google Drive, devolviendo enlaces directos a los archivos encontrados.

## 🛠️ Desarrollo

### Reconstruir contenedores
```bash
docker compose up -d --build
```

### Ver logs del Worker
```bash
docker logs -f drive-worker
```

### Ver logs de la API
```bash
docker logs -f drive-api
```

### Detener servicios
```bash
docker compose down
```

## 🔐 Seguridad

- Las credenciales se gestionan mediante variables de entorno
- El token OAuth2 se almacena localmente y se refresca automáticamente
- RabbitMQ utiliza autenticación con usuario y contraseña
- Se recomienda usar HTTPS en producción con certificados SSL/TLS

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añade nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 👤 Autor

**WBOK-GM**

- GitHub: https://github.com/WBOK-GM

## 🙏 Agradecimientos

- FastAPI - Framework web moderno y rápido
- Langchain - Framework para aplicaciones con LLMs
- Google Gemini AI - Modelo de lenguaje para interpretación de consultas
- Telegram Bot API - API para bots de Telegram
- RabbitMQ - Sistema de mensajería
- Traefik - Reverse proxy moderno

---

⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub
