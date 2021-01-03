import base64
import json
import logging
import os
import random
import string
from mimetypes import guess_extension, guess_type

from django import forms, template
from django.db import models
from django.urls import resolve, reverse
from dndhelper.quill_delta_to_html import quill_to_html


class QuillWidget(forms.Textarea):
    template_name = 'forms/widget/quill.html'

    def __init__(self, attrs=None):
        self.quillobject = None
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if 'placeholder' in attrs:
            context['widget']['placeholder'] = attrs['placeholder']
        if 'theme' in attrs:
            context['widget']['theme'] = attrs['theme']
        else:
            context['widget']['theme'] = 'snow'
        if 'toolbar' in self.attrs:
            context['widget']['toolbar'] = self.attrs['toolbar']
        filelink = None
        if self.quillobject is not None:
            try:
                filelink = self.quillobject.get_files_link()
            except Exception:
                filelink = None
        if 'value' in context['widget']:
            context['widget']['quill_object']=QuillObject(context['widget']['value'], filelink, clean=True)
        return context


class QuillField(forms.CharField):
    widget = QuillWidget

    def __init__(self, max_length=None, min_length=None, strip=True, empty_value='', **kwargs):
        super().__init__(max_length=max_length, min_length=min_length, strip=strip, empty_value=empty_value, **kwargs)


def check_quill_string(inputstr):
    try:
        res = json.loads(inputstr)
        if 'ops' in res:
            return True
        else:
            return False
    except Exception:
        return False

def get_quill_string(inputstr)->str:
    try:
        quilldict = get_quill_value(inputstr)
        if not isinstance(quilldict, dict):
            return None
        for operation in quilldict['ops']:
            if 'insert' in operation:
                if isinstance(operation['insert'], dict):
                    try:
                        if 'image' in operation['insert']:
                            try:
                                if isinstance(operation['insert']['image'], dict):
                                    operation['insert']['image'] = reverse(operation['insert']['image']['name'], 
                                        kwargs=operation['insert']['image']['kwargs'])
                            except Exception as err:
                                logging.error(err)
                    except:
                        pass
            if 'attributes' in operation:
                if 'link' in operation['attributes']:
                    try:
                        if isinstance(operation['attributes']['link'], dict):
                            operation['attributes']['link'] = reverse(operation['attributes']['link']['name'], 
                                kwargs=operation['attributes']['link']['kwargs'])
                    except Exception as err:
                        logging.error(err)

        return json.dumps(quilldict)
    except Exception:
        return inputstr

def get_quill_value(inputstr)->dict:
    try:
        if isinstance(inputstr, dict):
            return inputstr
        a=json.loads(inputstr)
        return a
    except Exception:
        return quillify_text(inputstr)

        
def get_quill_text(inputstr, files_link:str=None):
    try:
        if inputstr is dict:
            a = inputstr
        else:
            a=json.loads(inputstr)
        result = quill_to_html.quill_delta_to_html(a, files_link=files_link)
        if result is None:
            return inputstr
        return result
    except Exception:
        try:
            return str(inputstr)
        except Exception:
            return None

def quillify_text(inputstr:str)->dict:
    if inputstr is None:
        return None
    if not inputstr.endswith('\n'):
        return {"ops":[{"insert":inputstr+'\n'}]}
    return {"ops":[{"insert":inputstr}]}

def save_image(image:str, filepath:str)->str:
    if (not isinstance(image, str)) or (not isinstance(filepath, str)) or (image is None) or (filepath is None):
        return image
    try:
        tmp = image.find(';base64')
        if (tmp<6):
            return image
        image_type = guess_extension(image[5:tmp])
        image_binary = base64.b64decode(image[tmp+8:])
        try:
            while True:
                filename = ''.join(random.choice(string.ascii_lowercase) for i in range(10)) + image_type 
                if not os.path.exists(os.path.join(filepath, filename)):
                    break
            file = open(os.path.join(filepath, filename), 'wb')
            file.write(image_binary)
            file.close()
            return filename
        except Exception as e:
            logging.error(e)
            return image
    except Exception as e:
        logging.error(e)
        return image


def save_images_from_quill(inputstr, filepath:str, link:str='')->dict:
    if inputstr is None:
        return inputstr
    quilldict = get_quill_value(inputstr)
    if not isinstance(quilldict, dict):
        return inputstr
    for operation in quilldict['ops']:
        if 'insert' in operation:
            if isinstance(operation['insert'], dict):
                try:
                    if 'image' in operation['insert']:
                        try:
                            try:
                                tmp = resolve(save_image(operation['insert']['image'], filepath))
                            except Exception:
                                tmp = resolve(link+save_image(operation['insert']['image'], filepath))
                            kwargs = {}
                            for par in tmp.kwargs:
                                kwargs[par] = str(tmp.kwargs[par])
                            operation['insert']['image'] = {'kwargs': kwargs, 'name': tmp.url_name}
                        except Exception as err:
                            logging.error(err)
                except:
                    pass
        if 'attributes' in operation:
            if 'link' in operation['attributes']:
                try:
                    tmp = resolve(operation['attributes']['link'])
                    kwargs = {}
                    for par in tmp.kwargs:
                        kwargs[par] = str(tmp.kwargs[par])
                    operation['attributes']['link'] = {'kwargs': kwargs, 'name': tmp.url_name}
                except Exception as err:
                    logging.error(err)
    if type(quilldict) == type(inputstr):
        return quilldict
    return json.dumps(quilldict)

def load_image(filename:str, filepath:str)->str:
    if (not isinstance(filename, str)) or (not isinstance(filepath, str)) or (filename is None) or (filepath is None) or (not os.path.exists(os.path.join(filepath, filename))):
        return filename
    try:
        image_type = guess_type(filename)[0]
        try:
            file = open(os.path.join(filepath, filename), 'rb')
            image_binary = file.read()
            file.close()
            result = 'data:' + image_type + ';base64,' + str(base64.b64encode(image_binary).decode('utf-8'))
            return result
        except Exception as e:
            logging.error(e)
            return filename
    except Exception as e:
        logging.error(e)
        return filename

def load_images_from_quill(inputstr, filepath:str)->dict:
    if inputstr is None:
        return inputstr
    quilldict = get_quill_value(inputstr)
    if not isinstance(quilldict, dict):
        return inputstr
    for operation in quilldict['ops']:
        if 'insert' in operation:
            if isinstance(operation['insert'], dict):
                try:
                    if 'image' in operation['insert']:
                        operation['insert']['image'] = load_image(operation['insert']['image'], filepath)
                except:
                    pass
    if type(quilldict) == type(inputstr):
        return quilldict
    return json.dumps(quilldict)

def get_quill_text_simple(inputstr, number_of_lines:int=1):
    if inputstr is None:
        return inputstr
    if number_of_lines <1:
        return ''
    quilldict = get_quill_value(inputstr)
    if not isinstance(quilldict, dict):
        return inputstr
    result = ""
    got_lines = 0
    for operation in quilldict['ops']:
        if 'insert' in operation:
            if isinstance(operation['insert'], str):
                result += operation['insert']
                if '\n' in result:
                    got_lines += 1
                    if got_lines >= number_of_lines:
                        break
    if result[-1] == '\n':
        result = result[:-1]
    while (result.count('\n') > number_of_lines - 1):
        result = result[:-len(result)+result.rfind('\n')]
    return result
    



class QuillObject():
    def __init__(self, text="", filelink=None, clean=False):
        self.text=text
        self.filelink = filelink
        self.clean = clean

    def is_quill_content(self):
        return check_quill_string(self.text)

    def get_quill_content(self, files_link:str=None):
        if (files_link is None) and (files_link is not None):
            return get_quill_text(self.text, files_link=self.filelink)
        return get_quill_text(self.text, files_link=files_link)

    def get_quill_value(self):
        return get_quill_string(self.text)

    def get_content(self):
        return self.text

    def get_content_js(self):
        return self.text.replace("\n", "\\n")
    
    def get_content_simple_text_one_line(self):
        return get_quill_text_simple(self.text)
