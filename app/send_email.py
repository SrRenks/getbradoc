from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from email.mime.text import MIMEText
import smtplib


# your support email address
email = 'example@example.com'
# your recipient emails
to = ['exampledest1@example.com', 'exampledest2@example.com']
# server and server port.
server = 'example.server.com'
port = 25  # example port


# send email notification when expiration date is coming soon
def expiration_coming(pem, remaining_days, expiration_date):
    # connect to server
    s = smtplib.SMTP(server, port)
    s.connect(server, port)
    s.ehlo()
    # edit strings to send message to emails
    pem = pem.replace('certificates/', '').replace('.pem', '.pfx')
    body = f'O seguinte certificado:\n"{pem}"\nVai expirar em {remaining_days} dias ({expiration_date}).\nContate o desenvolvedor o mais breve possível.\n'
    # send email for every email in recipient email list
    for dest in to:
        try:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body))
            msg['To'] = dest
            msg['Subject'] = 'ALERTA: Certificado digital próximo da data de expiração'
            msg['From'] = email
            s.sendmail(email, [dest], msg.as_string())
        except Exception as ex:
            print("Something went wrong….", ex)

def error_status(message):
    # connect to server
    s = smtplib.SMTP(server, port)
    s.connect(server, port)
    s.ehlo()
    body = f'Log de erro:\n\n{message}\n\nContate o desenvolvedor o mais breve possível.'
    # send email for every email in recipient email list
    for dest in to:
        try:
            msg = MIMEMultipart()
            msg.attach(MIMEText(body))
            msg['To'] = dest
            msg['Subject'] = 'ALERTA: erros durante a execução'
            msg['From'] = email
            s.sendmail(email, [dest], msg.as_string())
        except Exception as ex:
            print("Something went wrong….", ex)
