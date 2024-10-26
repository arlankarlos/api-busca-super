# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Função para enviar o e-mail
def send_email(to_email, subject, message):
    print('destinatario:', to_email)
    print('assunto:', subject)
    print('mensagem:', message)
    # Configurações do servidor Gmail
    smtp_server = "smtp.gmail.com"
    smtp_port = 465  # Porta para SMTP com SSL
    sender_email = "prfakgn@gmail.com"  # Seu e-mail Gmail
    sender_password = "gytcbkmupdklzkea"      # Sua senha do Gmail ou App Password

    # Configuração do e-mail
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Anexa a mensagem como texto simples e define a codificação correta
    msg.attach(MIMEText(message, "plain", "utf-8"))

    try:
        # Conexão ao servidor Gmail usando SMTP_SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)  # Login

            # Envia o e-mail
            server.sendmail(sender_email, 'prfakgn@gmail.com', msg.as_string())
            print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
