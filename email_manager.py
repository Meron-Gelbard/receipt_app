from main import SMTP_CONFIG, app
from flask import url_for, session, request
import smtplib


class EmailManager:
    @classmethod
    def send_email_confirm(cls, **kwargs):
        with smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
            host = f"{request.scheme}://{request.host}"
            confirm_link = f"{host}{url_for('email_confirm', user_name=kwargs['user_name'], subject='email confirm', sent_uuid=kwargs['uuid'])}"

            name = kwargs['name']
            subject = 'kabalar - Email Confirmation'
            body = \
                f"""Hi {name} and welcome to kabalar! - Your business document manager WebApp!
                To finish your registration please click the link below to confirm your E-mail address:
                
                    {confirm_link}
                    
                See you there!

                kabalar.
                """
            recipient = kwargs['email']
            sender = SMTP_CONFIG['smtp_username']
            message = f'Subject: {subject}\nFrom: {sender}\nTo: {recipient}\n\n{body}'

            server.sendmail(sender, recipient, message)

            print('sent')

    @classmethod
    def send_pass_recover(cls, **kwargs):
        with smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['smtp_username'], SMTP_CONFIG['smtp_password'])
            host = f"{request.scheme}://{request.host}"
            confirm_link = f"{host}{url_for('email_confirm', user_name=kwargs['user_name'], subject='password recover', sent_uuid=kwargs['uuid'])}"

            name = kwargs['name']
            subject = 'kabalar - Password Recovery'
            body = \
                f"""Hi {name} ! - This is a password recovery message from kabalar.
                Please follow the link bellow to renew your account password:

                        {confirm_link}

                    See you there!

                    kabalar.
                    """
            recipient = kwargs['email']
            sender = SMTP_CONFIG['smtp_username']
            message = f'Subject: {subject}\nFrom: {sender}\nTo: {recipient}\n\n{body}'

            server.sendmail(sender, recipient, message)

            print('sent')