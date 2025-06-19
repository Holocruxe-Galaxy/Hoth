import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class SMTPMailSender:
    def __init__(self, smtp_host, smtp_port, username, password, from_email, use_tls=True, use_ssl=False):
        """
        Inicializa el manejador SMTP para envío de mails.

        :param smtp_host: Host del servidor SMTP (ej: 'mail.tudominio.com')
        :param smtp_port: Puerto del servidor SMTP (ej: 465 para SSL, 587 para TLS)
        :param username: Usuario del email (ej: 'usuario@tudominio.com')
        :param password: Contraseña del email
        :param from_email: Email desde el que se envía
        :param use_tls: Usar TLS (por defecto True)
        :param use_ssl: Usar SSL (por defecto False)
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.use_tls = use_tls
        self.use_ssl = use_ssl

    def send(self, to_email, content, subject=""):
        """from .email import Email
        Envía un email a través de SMTP.

        :param to_email: Email de destino
        :param content: Contenido del email (HTML o texto plano)
        :param subject: Asunto del email (opcional)
        """
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Detecta si el contenido es HTML
        if "<html" in content.lower():
            print("[SMTPMailSender] Adjuntando contenido HTML")
            msg.attach(MIMEText(content, 'html'))
        else:
            print("[SMTPMailSender] Adjuntando contenido plano")
            msg.attach(MIMEText(content, 'plain'))

        try:
            if self.use_ssl:
                print(f"[SMTPMailSender] Usando SMTP_SSL a {self.smtp_host}:{self.smtp_port}")
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                print(f"[SMTPMailSender] Usando SMTP normal a {self.smtp_host}:{self.smtp_port}")
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.use_tls:
                    print("[SMTPMailSender] Iniciando TLS")
                    server.starttls()
            print(f"[SMTPMailSender] Iniciando sesión SMTP con usuario {self.username}")
            server.login(self.username, self.password)
            print(f"[SMTPMailSender] Enviando mensaje a {to_email} desde {self.from_email}")
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()
            print("[SMTPMailSender] Mensaje enviado y conexión cerrada")
            return True
        except Exception as e:
            self.last_error = str(e)
            print(f"[SMTPMailSender] Error al enviar: {self.last_error}")
            return False