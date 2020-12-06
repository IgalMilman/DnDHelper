from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.template import Context
from django.contrib.auth.models import User
import logging 

logger = logging.getLogger(__name__)

def sendemaileveryone(template, data, subject):
    if template[-3:] == 'htm':
        sendemaileveryonehtml(template, data, subject)
    else:
        sendemaileveryonetxt(template, data, subject)

def sendemailtoone(template, data, subject, email, name):
    if template[-3:] == 'htm':
        sendemailtoonehtml(template, data, subject, email, name)
    else:
        sendemailtoonetxt(template, data, subject, email, name)

def sendemailtosome(template, data, subject, email):
    if template[-3:] == 'htm':
        sendemailtosomehtml(template, data, subject, email)
    else:
        sendemailtosometxt(template, data, subject, email)

def sendemailtouser(template, data, subject, user):
    if template[-3:] == 'htm':
        sendemailtouserhtml(template, data, subject, user)
    else:
        sendemailtousertxt(template, data, subject, user)


def sendemaileveryonetxt(template, data, subject):
    plaintext = get_template(template)
    for user in User.objects.exclude(email__isnull=True).exclude(email__exact=''):
        try:
            data['user'] = user
            text_content = plaintext.render(data)
            msg = EmailMultiAlternatives(subject, text_content, '', [user.email])
            msg.send()
        except Exception as exc:
            logger.error('Error in sendemaileveryonetxt.\nException: ', exc_info=True)

def sendemailtoonetxt(template, data, subject, email, name):
    try:
        plaintext = get_template(template)
        data['name'] = name
        text_content = plaintext.render(data)
        msg = EmailMultiAlternatives(subject, text_content, '', [email])
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailtoonetxt.\nException: ', exc_info=True)

def sendemailtosometxt(template, data, subject, email):
    try:
        plaintext = get_template(template)
        text_content = plaintext.render(data)
        msg = EmailMultiAlternatives(subject, text_content, '', email)
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailtosometxt.\nException: ', exc_info=True)

def sendemailtousertxt(template, data, subject, user):
    try:
        plaintext = get_template(template)
        data['user'] = user
        text_content = plaintext.render(data)
        msg = EmailMultiAlternatives(subject, text_content, '', [user.email])
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailtousertxt.\nException: ', exc_info=True)


def sendemaileveryonehtml(template, data, subject):
    for user in User.objects.exclude(email__isnull=True).exclude(email__exact=''):
        try:
            data['user'] = user
            html_content = render_to_string(template, data)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(subject, text_content, '', [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as exc:
            logger.error('Error in sendemaileveryonehtml.\nException: ', exc_info=True)

def sendemailtoonehtml(template, data, subject, email, name):
    try:
        data['name'] = name
        html_content = render_to_string(template, data)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, '', [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailtoonehtml.\nException: ', exc_info=True)

def sendemailtosomehtml(template, data, subject, email):
    try:
        html_content = render_to_string(template, data)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, '', email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailtosomehtml.\nException: ', exc_info=True)

def sendemailtouserhtml(template, data, subject, user):
    try:
        data['user'] = user
        html_content = render_to_string(template, data)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, '', [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailtouserhtml.\nException: ', exc_info=True)

def sendemailhtml(template, data, subject, email):
    try:
        html_content = render_to_string(template, data)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, '', [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as exc:
        logger.error('Error in sendemailhtml.\nException: ', exc_info=True)