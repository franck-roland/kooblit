
import os
import subprocess

# Fichiers
from django.core.files import File

#Models
from usr_management.models import UserKooblit, Syntheses, Demande

#Asynchrone
from celery import shared_task

@shared_task
def create_pdf(username, synth):
    try:
        user = UserKooblit.objects.get(username=username)
        if synth.user != user:
            return
    except UserKooblit.DoesNotExist:
        return
    except Syntheses.DoesNotExist:
        return

    contenu = synth.contenu_pdf()
    pdf_name = ''.join(('/tmp/synth_', str(synth.id), '_', str(synth.version)))
    html_name = ''.join((pdf_name, '.html'))
    with open(html_name,'w') as f_html:
        f_html.write(contenu)

    args = ["wkhtmltopdf",
        "--encoding", "utf-8",
        "--header-html", "127.0.0.1/static/html/pdf_header.html ",
        "--footer-html", "127.0.0.1/static/html/pdf_footer.html",
        html_name, pdf_name,]

    a = subprocess.call(args)
    if a:
        return
    with open(pdf_name, 'rb') as f_pdf:
        synth.file_pdf = File(f_pdf)
        synth.save()
    os.remove(html_name)
    os.remove(pdf_name)