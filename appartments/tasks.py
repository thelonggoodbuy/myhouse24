from django.core.mail import send_mail, EmailMessage

from celery import shared_task

from django.template.loader import get_template
import pdfkit



@shared_task()
def send_invitation(phone, email):


    owner_invitaion = EmailMessage(
            f'ПРиглашение платформы MyHouse24',
            f'Зарегистрируйтесь на нашей платформе - MyHouse24',
            'markus1991kartal@gmail.com',
            [email,]
        )

    owner_invitaion.send()