from docx import Document
import re

cli_to_api_dict = {'ip access-list session' : 'Session ACL',
                   'user-role' : 'Role',
                   }
object_values_dict = { 'user-role' : ['access-list eth|mac|session', 'bw-contract app|appcategory|exclude', 'bw-contract web-cc-category|web-cc-reputation', 'bw-contract', 'captive-portal', 'dialer', 'dpi', 'max-sessions', 'policer-profile', 'pool l2tp|pptp', 'qos-profile', 'reauthentication-interval', 'registration-role', 'session-acl', 'sso', 'stateful-kerberos', 'stateful-ntlm', 'traffic-control-profile', 'via', 'vlan', 'voip-profile', 'webcc disable', 'wispr'],
                       'snmp-server': ['community', 'enable trap', 'engine-id', 'host', 'inform queue-length', 'source controller-ip', 'stats', 'trap', 'user']}
one_line_objects_dict = {}
multi_value_parameter = {}

def parse():
    try:
        with open('parser_test.txt') as config_file:
            objects = []
            lines = config_file.readlines()
            current_line = 0
            while current_line < len(lines):
                current_object_lines = []
                current_object_lines.append(lines[current_line].strip())
                current_line += 1
                while '!\n' != lines[current_line]: 
                    sub_line = lines[current_line].strip()
                    if sub_line != '':
                        current_object_lines.append(sub_line)
                    current_line += 1
                    if current_line == len(lines):
                        break
                current_line += 1
                objects.append(current_object_lines)
            ir_doc = Document()
            ir_doc.save('acl_parse.docx')
    except FileNotFoundError:
        print('file does not exist.')
        exit()

def group_object_attributes(object):
    groups = {}
    name_line = object[0].split(' ')
    object_name = name_line[0]
    
    for line in object[1:]:
        line_words = line.split(' ')
        is_processed = False
        for unique_object in object_values_dict[object_name]:
            unique_values = unique_object.split(' ')
            match = 0
            current_group_name = ''
            for unique_value,word in zip(unique_values,line_words):
                if word == unique_value or word in unique_value:
                    match += 1
                    if current_group_name == '':
                        current_group_name += word
                    else:
                        current_group_name += ' ' + word
                    if match == len(unique_values):
                        is_processed = True
                        if current_group_name in groups:
                            groups[current_group_name].append(line[len(current_group_name)+1:])
                        else:
                            groups[current_group_name] = [line[len(current_group_name)+1:]]
            if is_processed:
                break
    return groups

def get_max_columns(objects):
    max_columns = 0
    max_object = None 
    for object in objects:
        current_object_len = len(object)
        if current_object_len > max_columns:
            max_columns = current_object_len
            max_object = object
    return [max_columns,max_object]

def add_acl_info_to_document(doc, acl_objects):
    table = doc.add_table(cols=2,rows=len(acl_objects))
    rows = table.rows
    for row,object in zip(rows,acl_objects):
        row_cells = row.cells
        row_cells[0].text = split_object_identifier(object[0].split(' '), 3)
        row_cells[1].text = object[1]
        for ace in object[2:]:
            row_cells[1].text += f",\n{ace}"

def split_object_identifier(words_list, start):
    object_id = words_list[start:]
    object_id = [word.replace('"','') for word in object_id]
    return join_words(object_id, '_')

def join_words(word_list, seperator):
    joined_words = word_list[0]
    for word in word_list[1:]:
        joined_words += seperator + word
    return joined_words

def process_expression(line, current, origin_id):
    current_id = origin_id
    options = []
    new_options = []
    optional_index = 0
    while current < len(line):
        current_item = line[current]
        if current_item == '|':
            current += 1
            new_options = add_options([current_id],new_options)
            current_id = origin_id
        elif current_item == '{':
            current += 1
            if len(new_options) == 0:
                current, new_options = process_expression(line, current, current_id)
            else:
                current, added_opts = process_expression(line, current, current_id)
                new_options = add_options(new_options, added_opts)
        elif current_item == '}':
            current += 1
            if current == len(line):
                return [current, options]
            deep_current = current
            added_options = []
            if not current_id in new_options:
                new_options.append(current_id)
            options = add_options(options,new_options)
            if len(options) != 0 and line[current] != '|': 
                for option in options:
                    current, extended_options = process_expression(line, deep_current, option)
                    added_options += extended_options
            options = add_options(options,added_options)
            return [current, options]
        elif current_item == '[':
            if not current_id in new_options:
                new_options.append(current_id)
            current += 1
            for index, word in enumerate(line[current:]):
                if word == ']':
                    optional_index = current + index + 1
                    break
            _, extended_options = process_expression(line, optional_index, current_id)
            new_options = add_options(new_options, extended_options)
        elif current_item == ']':
            if not current_id in new_options:
                new_options.append(current_id)
            current += 1
        else:
            current_id += f' {line[current]}'
            current += 1
            if current == len(line):
                options.append(current_id)
    if len(options) == 0:
        options = new_options
    return [current, options]

def add_options(options, added_options):
    if len(options) == 0:
        return added_options
    is_subset = True
    for option in options:
        is_not_in_any = True 
        for add_option in added_options:
            if option in add_option:
                is_not_in_any = False
                break
        if is_not_in_any:
            is_subset = False
            break
    if is_subset:
        options = added_options
    else:
        for added_option in added_options:
            if not added_option in options:
                options.append(added_option)
    return options

def process_line(line):
    current = 1
    words = line.split(' ')
    options = process_expression(words, current, words[0])
    return options[1]

def populate_objects_value_dict():
    cli_commands_path = 'cli_commands.txt'
    with open(cli_commands_path) as cli_file:
        user_input = re.compile(r'<\w+>')
        lines = cli_file.readlines()
        current = 0
        while(current < len(lines)):
            if user_input.match(lines[current].split(' ')[-1]):
                object_name = join_words(lines[current].split(' ')[:-1])
                object_values_dict[object_name] = []
                current += 1
                while(current < len(lines) and lines[current] != '!\n'):
                    current_line = lines[current].lstrip()
                    if is_simple_parameter(current_line):
                        command = join_words(current_line.split(' ')[:-1])
                        object_values_dict[object_name].append(command)
                    else:
                        if object_name in multi_value_parameter:
                            multi_value_parameter[object_name].append(current_line)
                        else:
                            multi_value_parameter[object_name] = [current_line]
                    current += 1

def is_simple_parameter(line):
    words = line.split(' ')
    is_simple = True
    user_input = re.compile(r'<\w+>')
    keyword_pairs = {}
    current_keyword = ''
    for word in words:
        if user_input.match(word):
            if current_keyword in keyword_pairs:
                keyword_pairs[current_keyword].append(word)
            else:
                keyword_pairs[current_keyword] = [word]
        else:
            if current_keyword in keyword_pairs:
                current_keyword = '' 
            if current_keyword == '':
                current_keyword = word
            else:
                current_keyword += f' {word}'
    if len(keyword_pairs.keys()) > 1:
        is_simple = False
    return is_simple