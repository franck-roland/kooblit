import sys
import os
import subprocess

# Fichiers
from django.core.files import File

#Models
from usr_management.models import UserKooblit, Syntheses, Demande

#Asynchrone
from celery import shared_task

# Emails
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.templatetags.static import static

@shared_task
def create_pdf(username, synth):
    try:
        user = UserKooblit.objects.get(username=username)
        if synth.user != user:
            return 1
    except UserKooblit.DoesNotExist:
        return 1
    except Syntheses.DoesNotExist:
        return 1

    contenu = synth.contenu_pdf()
    pdf_name = ''.join(('/tmp/synth_', str(synth.id), '_', str(synth.version)))
    html_name = ''.join((pdf_name, '.html'))
    with open(html_name,'w') as f_html:
        f_html.write(contenu)

    url_header = '127.0.0.1/static/html/pdf_header.html'
    url_footer = '127.0.0.1/static/html/pdf_footer.html'
    args = ["wkhtmltopdf",
        "--encoding", "utf-8",
        "--header-html", url_header,
        "--footer-html", url_footer, 
        html_name, pdf_name,]

    a = subprocess.call(args)
    if a:
        return a
    with open(pdf_name, 'rb') as f_pdf:
        synth.file_pdf = File(f_pdf)
        synth.save()
    os.remove(html_name)
    os.remove(pdf_name)

@shared_task
def computeEmail(username, book_title, alert=0):
    if not alert:
        htmly = get_template('email_demande_infos.html')
    else:
        htmly = get_template('email_synthese_dispo.html')
    email = UserKooblit.objects.get(username=username).email
    d = Context({'username': username, 'book_title': book_title})
    subject, from_email, to = ('[Kooblit] Alerte pour ' + book_title,
                               'noreply@kooblit.com', email)
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()
    print "sent"
