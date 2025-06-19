# Holocruxe - Hoth

## Descripción General
Hoth es el microservicio encargado de gestionar el endpoint de contacto de la landing page de Holocruxe. Permite recibir información de contacto de usuarios, almacenarla en MongoDB y enviar notificaciones por correo electrónico usando SMTP.

## Estructura del Proyecto
```
Hoth/
├── handler.py                # Lambda handler principal
├── function/
│   └── contact.py            # Lógica de negocio para contacto
├── utils/
│   ├── smtp_mail.py          # Utilidad para envío de correos SMTP
│   └── db_conn.py            # Conexión a MongoDB
├── templates/                # Plantillas HTML para emails
│   └── contact.html
├── serverless.yml            # Configuración Serverless Framework
├── requirements.txt          # Dependencias Python
├── README.md                 # (Este archivo)
└── ...
```

## ¿Cómo funciona?
1. **Recepción de datos:**
   - El endpoint `/contact` recibe datos de contacto vía POST (nombre, email, teléfono, mensaje).
2. **Almacenamiento:**
   - Los datos se almacenan en la colección `landing_contact_info` de MongoDB.
3. **Notificación por email:**
   - Se envía un correo de notificación a contacto@holocruxe.com usando SMTP y una plantilla HTML.

## Endpoints disponibles
### POST /contact
- **Descripción:** Recibe la información de contacto de un usuario.
- **Body esperado (JSON):**
  ```json
  {
    "name": "Nombre del usuario",
    "email": "usuario@email.com",
    "phone": "1234567890",
    "message": "Mensaje enviado desde la landing"
  }
  ```
- **Respuesta exitosa:**
  ```json
  {
    "status": "success",
    "message": "Thank you <nombre>! Your message has been received."
  }
  ```
- **Respuesta de error:**
  ```json
  {
    "status": "error",
    "message": "Database connection failed."
  }
  ```

## Variables de entorno necesarias
Definidas en `serverless.yml`:
- `SMTP_HOST`: Host del servidor SMTP (ej: webmail.holocruxe.com)
- `SMTP_PORT`: Puerto SMTP (465 para SSL, 587 para TLS)
- `SMTP_USER`: Usuario del correo
- `SMTP_PASS`: Contraseña del correo
- `SMTP_FROM`: Email remitente
- `REGION`, `STAGE`: Variables de entorno AWS

## Plantillas de correo
Las plantillas HTML para los correos se encuentran en la carpeta `templates/` (ejemplo: `contact.html`).

## Instalación y pruebas locales
1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Crea un archivo `.env` (opcional para pruebas locales) con las variables de entorno necesarias.
3. Ejecuta el servicio en local con Serverless Offline:
   ```bash
   sls offline
   ```
4. Realiza una petición de prueba:
   ```bash
   curl -X POST http://localhost:3000/contact \
     -H 'Content-Type: application/json' \
     -d '{"name": "Test", "email": "test@correo.com", "phone": "1234567890", "message": "Hola!"}'
   ```

## Dependencias principales
- Python 3.12+
- serverless, serverless-offline, serverless-python-requirements
- pymongo, boto3, smtplib

## Notas adicionales
- El servicio implementa CORS para permitir peticiones desde cualquier origen.
- El envío de correo puede configurarse para usar SSL o TLS según el servidor SMTP.
- El almacenamiento en MongoDB requiere que las credenciales estén correctamente configuradas en AWS Secrets Manager.
- Las respuestas siempre incluyen los headers necesarios para CORS.

---

> Para más detalles, revisa los docstrings en cada archivo fuente y la configuración en `serverless.yml`.
