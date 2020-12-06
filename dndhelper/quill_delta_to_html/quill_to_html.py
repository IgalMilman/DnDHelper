from html import escape

QUILL_REPLACE_INLINE = [{'quill':'script', 'value': 'super', 'htmls':'<sup{}>', 'htmle':'</sup>'},
{'quill':'script', 'value': 'sub', 'htmls':'<sub{}>', 'htmle':'</sub>'},
{'quill':'underline', 'value': True, 'htmls':'<u{}>', 'htmle':'</u>'},
{'quill':'italic', 'value': True, 'htmls':'<em{}>', 'htmle':'</em>'},
{'quill':'bold', 'value': True, 'htmls':'<strong{}>', 'htmle':'</strong>'},
{'quill':'strike', 'value': True, 'htmls':'<s{}>', 'htmle':'</s>'},
]
QUILL_STYLE_INLINE = [{'quill':'color', 'style':'color:', 'value': True},
{'quill':'background', 'style':'background-color:', 'value': True},
]
QUILL_CLASSES = [{'quill':'size', 'value': True, 'class_base':'ql-size-',},
{'quill':'font', 'value': True, 'class_base':'ql-font-',},
{'quill':'align', 'value': True, 'class_base':'ql-align-',},
{'quill':'indent', 'value': True, 'class_base':'ql-indent-',},
{'quill':'direction', 'value': True, 'class_base':'ql-direction-',},
]

true = True

def read_next_operations(operation):
    text = operation['insert'].split("\n")
    result = []
    for i in range(len(text)):
        op = {}
        if 'attributes' in operation:
            op['attributes'] = operation['attributes']
        op['insert'] = escape(text[i])
        if (op['insert']!=""):
            result.append(op)
        if 'attributes' in operation:
            result.append({'insert': "\n", 'attributes': operation['attributes']})
        else:
            result.append({'insert': "\n"})
    del result[-1]
    return result

def expand_delta(delta):
    temp = []
    for operation in delta:
        if 'insert' in operation:
            text = operation['insert']
            if text != '\n':
                if '\n' in text:
                    temp += read_next_operations(operation)
                else:
                    if type(operation['insert']) is dict:
                        try:
                            if 'image' in operation['insert']:
                                operation['insert'] = "<img src='" + operation['insert']['image'] + "'>"
                            if 'video' in operation['insert']:
                                operation['insert'] = "<iframe class='ql-video' frameborder='0' allowfullscreen='true' src='" + operation['insert']['video'] + "'></iframe>"
                        except:
                            pass
                    else:
                        operation['insert']=escape(operation['insert'])
                    temp.append(operation)
            else:
                operation['insert']=escape(operation['insert'])
                temp.append(operation)
        else:
            operation['insert']=escape(operation['insert'])
            temp.append(operation)
    result = []
    text_container = []
    for i in range(len(temp)):
        if temp[i]['insert'] != '\n':
            text_container.append(temp[i])
        else:
            result += [temp[i]] + text_container
            text_container = []
    result += text_container
    return result

def quill_delta_to_html(quill_dict):
    if 'ops' in quill_dict:
        line_attributes = {}
        result = ''
        end_of_lane_tags = ''
        end_of_lane_text = ''
        end_of_block_tags = ''
        exp_delta = expand_delta(quill_dict['ops'])
        text_attributes = {}
        text_was_added = False
        for operation in exp_delta:
            if 'attributes' in operation:
                attributes = operation['attributes']
            else:
                attributes = {}

            if 'insert' in operation:
                text = operation['insert']
                if text == '\n':
                    if not text_was_added and result!='':
                        result+= "<br>"
                    result += end_of_lane_text + end_of_lane_tags
                    end_of_lane_text = ''
                    text_attributes = {}
                    line_attributes, start_tags, end_of_lane_tags, end_of_block_tags = parse_line_attributes(attributes, old_attributes = line_attributes)
                    result += start_tags
                    text_was_added = False
                else:
                    text_attributes, text_to_add, end_of_lane_text = parse_text_attributes(text, attributes, old_attributes = text_attributes)
                    result += text_to_add
                    text_was_added = True
        if not text_was_added and result!='':
            result+= "<br>"
        result += end_of_lane_text + end_of_lane_tags + end_of_block_tags
        for i in range(len(QUILL_REPLACE_INLINE)):
            repl = QUILL_REPLACE_INLINE[i]
            result = result.replace(repl['htmle'] + repl['htmls'].format(''), '')
        for i in range(len(QUILL_REPLACE_INLINE)):
            repl = QUILL_REPLACE_INLINE[i]
            result = result.replace(repl['htmle'] + repl['htmls'].format(''), '')
        return result.strip()
    else:
        return None


def parse_line_attributes(attributes, old_attributes={}):
    text_beginning_of_lane = ''
    text_ending_of_lane = ''
    text_start_block = ''
    text_end_block = ''
    end_of_block_tags = ''
    classes = ""
    styles = ""
    if 'code-block' in attributes:
        classes = "ql-syntax"
    for i in range(len(QUILL_CLASSES)):
        repl = QUILL_CLASSES[i]
        if repl['quill'] in attributes:
            if repl['value']:
                if classes == '':
                    classes = repl['class_base'] + str(attributes[repl['quill']])
                else:
                    classes += ' ' + repl['class_base'] + str(attributes[repl['quill']])
            else:
                if classes == '':
                    classes = repl['class_base']
                else:
                    classes += ' ' + repl['class_base']
    
    for i in range(len(QUILL_STYLE_INLINE)):
        repl = QUILL_STYLE_INLINE[i]
        if repl['quill'] in attributes:
            if repl['value']:
                if styles == '':
                    styles = repl['style'] + ':' + str(attributes[repl['quill']])
                else:
                    styles += ' ' + repl['style'] + ':' + str(attributes[repl['quill']])
            else:
                if styles == '':
                    styles = repl['class_base']
                else:
                    styles += ' ' + repl['class_base']
    
    attribs = ''
    if styles != '' and classes != '':
        attribs = ' style=\'' + styles + '\' class=\'' + classes + '\''
    elif styles != '':
        attribs = ' style=\'' + styles + '\''
    elif styles == '' and classes != '':
        attribs = ' class=\'' + classes + '\''

    if 'list' in attributes and 'list' in old_attributes:
        if attributes['list'] != old_attributes['list']:
            if attributes['list'] == 'ordered':
                text_start_block += '<ol>'
            else:
                text_start_block += '<ul>'
            if old_attributes['list'] == 'ordered':
                text_end_block += '</ol>'
            else:
                text_end_block += '</ul>'
        text_beginning_of_lane += '<li{}>'.format(attribs)
        text_ending_of_lane += '</li>'
        if attributes['list'] == 'ordered':
            end_of_block_tags += '</ol>'
        else:
            end_of_block_tags += '</ul>'
    elif 'list' in attributes:
        if attributes['list'] == 'ordered':
            text_start_block += '<ol>'
        else:
            text_start_block += '<ul>'
        text_beginning_of_lane += '<li{}>'.format(attribs)
        text_ending_of_lane += '</li>'
        if attributes['list'] == 'ordered':
            end_of_block_tags += '</ol>'
        else:
            end_of_block_tags += '</ul>'
    elif 'list' in old_attributes:
        if old_attributes['list'] == 'ordered':
            text_end_block += '</ol>'
        else:
            text_end_block += '</ul>'
    if 'header' in attributes:
        text_beginning_of_lane += '<h'+str(attributes['header'])+'{}>'.format(attribs)
        text_ending_of_lane += '</h'+str(attributes['header'])+'>'
    if 'blockquote' in attributes:
        text_beginning_of_lane += '<blockquote{}>'.format(attribs)
        text_ending_of_lane += '</blockquote>'
    if 'code-block' in attributes:
        text_beginning_of_lane += '<pre{} spellcheck="false">'.format(attribs)
        text_ending_of_lane += '</pre>'
    if text_beginning_of_lane == "":
        text_beginning_of_lane = "<p{}>".format(attribs)
        text_ending_of_lane = "</p>"
    return attributes, text_end_block + text_start_block + text_beginning_of_lane, text_ending_of_lane, end_of_block_tags


def parse_text_attributes(text, attributes, old_attributes={}):
    result = text
    classes = ''
    styles = ''
    begin = ''
    end = ''
    end_of_line = ''
    if 'link' in old_attributes and old_attributes['link']!='' and ('link' not in attributes or attributes['link']!=old_attributes['link']):
        result = '</a>' + result
    for i in range(len(QUILL_CLASSES)):
        repl = QUILL_CLASSES[i]
        if repl['quill'] in attributes:
            if repl['value']:
                if classes == '':
                    classes = repl['class_base'] + attributes[repl['quill']]
                else:
                    classes += ' ' + repl['class_base'] + attributes[repl['quill']]
            else:
                if classes == '':
                    classes = repl['class_base']
                else:
                    classes += ' ' + repl['class_base']
    
    for i in range(len(QUILL_STYLE_INLINE)):
        repl = QUILL_STYLE_INLINE[i]
        if repl['quill'] in attributes:
            if repl['value']:
                if styles == '':
                    styles = repl['style'] + ':' + attributes[repl['quill']]
                else:
                    styles += ' ' + repl['style'] + ':' + attributes[repl['quill']]
            else:
                if styles == '':
                    styles = repl['class_base']
                else:
                    styles += ' ' + repl['class_base']
    
    attribs = ''
    if styles != '' and classes != '':
        attribs = ' style=\'' + styles + '\' class=\'' + classes + '\''
    elif styles != '':
        attribs = ' style=\'' + styles + '\''
    elif styles == '' and classes != '':
        attribs = ' class=\'' + classes + '\''

    for i in range(len(QUILL_REPLACE_INLINE)):
        repl = QUILL_REPLACE_INLINE[i]
        if repl['quill'] in attributes and attributes[repl['quill']] == repl['value']:
            result = repl['htmls'].format(attribs) + result + repl['htmle']
            attribs=''
    if attribs != '':
        begin = "<span " + attribs + ">"
        end = "</span>"
    if 'link' in attributes and attributes['link']!='' and ('link' not in old_attributes or attributes['link']!=old_attributes['link']):
        result = '<a href="' + attributes['link'] + '" target="_blank">' + result
    if 'link' in attributes and attributes['link']!='':
        end_of_line = "</a>"
    return attributes, begin + result + end, end_of_line