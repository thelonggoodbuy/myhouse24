from django.core.mail import send_mail, EmailMessage
from time import sleep
from celery import shared_task
import base64
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from pathlib import Path
from django.template.loader import get_template
import pdfkit



@shared_task()
def send_pdf_receipt(receipt_number, owner_fool_name, owner_email, path, context):


    reseipt_mail_object = EmailMessage(
            f'Квітанція №{ receipt_number }',
            f'Доброго дня, { owner_fool_name }\n Ви отримали квітанцію.',
            'markus1991kartal@gmail.com',
            [owner_email,]
        )
    
    prerendered_template = get_template(path)
    html = prerendered_template.render(context)
    myPdf = pdfkit.from_string(html, False)
    reseipt_mail_object.attach(f"receipt_{receipt_number}.pdf", myPdf)
    reseipt_mail_object.send()
    # return None