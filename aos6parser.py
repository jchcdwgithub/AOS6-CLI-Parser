from docx import Document
from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.table import Table
from openpyxl.styles import PatternFill, Font
from openpyxl.utils import get_column_letter
import re

cli_to_api_dict = {'ip access-list session' : 'Session ACL',
                   'user-role' : 'Role',
                   'aaa authentication-server radius' : { 'aaa authentication-server radius' :'Radius Server Name',
                                                          'acctport' : 'Rad Server Acctport',
                                                          'authport' : 'Rad Server Authport',
                                                          'use-md5' : 'Rad Server MD5',
                                                          'enable-radsec' : 'Radsec',
                                                          'radsec-client-cert-name' : 'Radsec Client Cert Name',
                                                          'radsec-port' : 'Radsec Port',
                                                          'radsec-trusted-cacert-name' : 'Radsec Trusted CA Cert Name',
                                                          'radsec-trusted-servercert-name' : 'Radsec Trusted Server Cert Name',
                                                          'retransmit' : 'Rad Server Retransmit',
                                                          'service-type-framed-user' : 'Service Type Framed User',
                                                          'timeout' : 'Rad Server Timeout',
                                                          'use-ip-for-calling-station' : 'Use IP For Calling Station',
                                                          'enable-ipv6' : 'Enable IPv6',
                                                          'host' : 'Rad Server Host',
                                                          'called-station-id type' : 'Called-station-ID Type',
                                                          'called-station-id delimiter' : 'Called-station-ID Delimiter',
                                                          'called-station-id include-ssid' : 'Called-station-ID Include SSID',
                                                          'cppm username' : 'CPPM Username',
                                                          'cppm password' : 'CPPM PW',
                                                          'source-interface vlan' : 'Source Interface VLAN',
                                                          'source-interface ip6addr' : 'Source Interface IPv6 Addr',
                                                          'key' : 'Rad Server Key',
                                                          'nas-identifier' : 'Rad Server NAS-ID',
                                                        },
                    'aaa server-group' : { 'aaa server-group' : 'Server Group',
                                           'auth-server' : 'SG Server Name',},
                    'aaa profile' : { 'aaa profile': 'AAA Profile',
                                      'rfc-3576-server' : 'AAA RFC3576 IP',
                                      'dot1x-default-role' : 'AAA 1X Default Role',
                                      'dot1x-server-group': 'AAA 1X Server Group',
                                      'authentication-dot1x' : 'AAA 1X Profile',
                                      'authentication-mac' : 'AAA MAC Profile',
                                      'initial-role' : 'AAA Initial Role',
                                      'mac-default-role' : 'AAA MAC Default Role',
                                      'mac-server-group' : 'AAA MAC Server Group',
                                      'download-role': 'AAA DL Role',
                                      'l2-auth-fail-through': 'AAA L2 Auth Failthrough',},
                    'ap system-profile' : { 'ap system-profile' : 'AP System Profile',
                                            'lms-ip' : 'AP Sys LMS IP',
                                            'bkup-lms-ip' : 'AP Sys Bkup LMS IP',
                                            'shell-passwd' : 'AP Sys AP Console PW'},
                    'ap regulatory-domain-profile' : { 'ap regulatory-domain-profile' : 'Reg Domain Profile',
                                                       'valid-11a-channel' : '5 GHz Channels',
                                                       'valid-11g-channel' : '2.4 GHz Channels',
                                                       'valid-11a-40mhz-channel-pair' : '5 GHz 40 MHz Channels',
                                                       'valid-11g-40mhz-channel-pair' : '2.4 GHz 40 MHz Channels',
                                                       'valid-11a-80mhz-channel-group': '5 GHz 80 MHz Channels',
                                                       'country-code' : 'Reg Domain Country Code',
                                                       },
                    'rf arm-profile' : { 'rf arm-profile' : 'RF ARM Profile',
                                         '40MHz-allowed-bands' : '40 MHz Allowed Bands',
                                         '80MHz support' : '80 MHz Support',
                                         'acceptable-coverage-index' : 'Acceptable Coverage Index',
                                         'active-scan' : 'Active Scan',
                                         'aggressive-scan' : 'Aggressive Scan',
                                         'assignment' : 'Assignment',
                                         'backoff-time' : 'ARM Backoff Time',
                                         'cellular-handoff-assist' : 'Cellular Handoff Assist',
                                         'channel-quality-aware-arm' : 'Channel Quality Aware ARM',
                                         'channel-quality-aware-threshold' : 'Channel Quality Aware Threshold',
                                         'channel-quality-wait-time' : 'Channel Quality Wait Time',
                                         'client-aware' : 'ARM Client Aware',
                                         'client-match' : 'ARM Client Match',
                                         'cm-band-a-min-signal' : 'CM Band A Min Sig',
                                         'cm-band-g-max-signal' : 'CM Band G Max Sig',
                                         'cm-lb-client-thresh' : 'CM LB Client Threshold',
                                         'cm-lb-signal-delta' : 'CM LB Sig Delta',
                                         'cm-lb-thresh' : 'CM LB Threshold',
                                         'cm-max-steer-fails' : 'CM Max Steer Fails',
                                         'cm-mu-client-thresh' : 'CM MU Client Threshold',
                                         'cm-mu-snr-thresh' : 'CM MU SNR Threshold',
                                         'cm-report-interval' : 'CM Report Interval',
                                         'cm-stale-age' : 'CM Stale Age',
                                         'cm-steer-timeout' : 'CM Steer Timeout',
                                         'cm-sticky-check_intvl' : 'CM Sticky Check Interval',
                                         'cm-sticky-min-signal' : 'CM Sticky Min Signal',
                                         'cm-sticky-snr' : 'CM Sticky SNR',
                                         'cm-sticky-snr-delta' : 'CM Sticky SNR Delta',
                                         'cm-update-interval' : 'CM Update Interval',
                                         'error-rate-threshold' : 'Error Rate Threshold',
                                         'error-rate-wait-time' : 'Error Rate Wait Time',
                                         'free-channel-index' : 'Free Channel Index',
                                         'ideal-coverage-index' : 'Ideal Coverage Index',
                                         'load-aware-scan-threshold' : 'Load Aware Scan Threshold',
                                         'max-tx-power' : 'Max TX Power',
                                         'min-scan-time' : 'Min Scan Time',
                                         'min-tx-power' : 'Min TX Power',
                                         'mode-aware' : 'Mode Aware',
                                         'multi-band-scan' : 'Multi-Band Scan',
                                         'ota-updates' : 'OTA Updates',
                                         'ps-aware-scan' : 'PS Aware Scan',
                                         'rogue-ap-aware' : 'Rogue AP Aware',
                                         'scan mode' : 'ARM Scan Mode',
                                         'scan-interval' : 'ARM Scan Interval',
                                         'scanning' : 'ARM Scanning',
                                         'video-aware-scan' : 'ARM Video Aware Scan',
                                         'voip-aware-scan' : 'ARM VOIP Aware Scan',

                    },
                    'rf optimization-profile' : { 'rf optimization-profile' : 'RF Opt Profile',
                                                  'handoff-assist' : 'Handoff Assist',
                                                  'low-rssi-threshold' : 'Low RSSI Threshold',
                                                  'rssi-check-frequency' : 'RSSI Check Freq',
                                                  'rssi-falloff-wait-time' : 'RSSI Falloff Wait Time',

                    },
                    'rf event-thresholds-profile' : { 'rf event-thresholds-profile' : 'RF Event Thresholds Profile',
                                                      'bwr-high-wm' : 'BWR High WM',
                                                      'bwr-low-wm' : 'BWR Low WM',
                                                      'detect-frame-rate-anomalies' : 'Detect Frame Rate Anomalies',
                                                      'fer-high-wm' : 'FER High WM',
                                                      'fer-low-wm' : 'FER Low WM',
                                                      'frr-high-wm' : 'FRR High WM',
                                                      'frr-low-wm' : 'FRR Low WM',
                                                      'flsr-high-wm' : 'FLSR High WM',
                                                      'flsr-low-wm' : 'FLSR Low WM',
                                                      'fnur-high-wm' : 'FNUR High WM',
                                                      'fnur-low-wm' : 'FNUR Low WM',
                                                      'frer-high-wm' : 'FRER High WM',
                                                      'frer-low-wm' : 'FRER Low WM',
                    },
                    'rf am-scan-profile' : { 'rf am-scan-profile' : 'RF AM Scan Prof',
                                             'dwell-time-active-channel' : 'Dwell Time Active Chan',
                                             'dwell-time-other-reg-domain-channel' : 'Dwell Time Other Reg Dom Chan',
                                             'dwell-time-reg-domain-channel' : 'Dwell Time Reg Dom Chan',
                                             'scan-mode' : 'AM Scan Prof Scan Mode',

                    },
                    'rf dot11a-radio-profile' : {'rf dot11a-radio-profile' : '5 GHz Radio Prof',
                                                 'am-scan-profile' : '5 GHz AM Scan Prof',
                                                 'arm-profile' : '5 GHz ARM Prof',
                                                 'beacon-period' : '5 GHz Beacon Period',
                                                 'cap-reg-eirp' : '5 GHz Cap Reg EIRP',
                                                 'cell-size-reduction' : 'Cell Size Reduction',
                                                 'channel' : '5 GHz Prof Channel',
                                                 'channel-reuse' : '5 GHz Prof Chan Reuse',
                                                 'csa-count' : 'CSA Count',
                                                 'ht-radio-profile' : 'HT Radio Profile',
                                                 'maximum-distance' : 'Max Distance',
                                                 'mgmt-frame-throttle-interval' : 'MGMT Frame Throttle Interval',
                                                 'mgmt-frame-throttle-limit' : 'MGMT Frame Throttle Limit',
                                                 'mode' : '5 GHz Radio Mode',
                                                 'slb-mode' : 'SLB Mode',
                                                 'slb-update-interval' : 'SLB Update Interval',
                                                 'tpc-power' : 'TPC Power',
                                                 'tx-power' : '5 GHz Radio TX Power',
                    },
                    'rf dot11g-radio-profile' : {'rf dot11g-radio-profile' : '11g Radio Prof',
                                                 'am-scan-profile' : '11g AM Scan Prof',
                                                 'arm-profile' : '11g ARM Prof',
                                                 'beacon-period' : '11g Beacon Period',
                                                 'cap-reg-eirp' : '11g Cap Reg EIRP',
                                                 'cell-size-reduction' : 'Cell Size Reduction',
                                                 'channel' : '11g Prof Channel',
                                                 'channel-reuse' : '11g Prof Chan Reuse',
                                                 'csa-count' : 'CSA Count',
                                                 'ht-radio-profile' : 'HT Radio Profile',
                                                 'maximum-distance' : 'Max Distance',
                                                 'mgmt-frame-throttle-interval' : 'MGMT Frame Throttle Interval',
                                                 'mgmt-frame-throttle-limit' : 'MGMT Frame Throttle Limit',
                                                 'mode' : '11g Radio Mode',
                                                 'slb-mode' : 'SLB Mode',
                                                 'slb-update-interval' : 'SLB Update Interval',
                                                 'tpc-power' : 'TPC Power',
                                                 'tx-power' : '11g Radio TX Power',
                                                 },
                    'wlan ht-ssid-profile' : {'wlan ht-ssid-profile' : 'HT SSID Profile',
                                              '40MHz-enable' : '40 MHz Enable',
                                              '80MHz-enable' : '80 MHz Enable',
                                              'ba-amsdu-enable' : 'BA AMSDU Enable',
                                              'high-throughput-enable' : 'HT enable',
                                              'ldpc' : 'LDPC',
                                              'legacy-stations' : 'Legacy Stations',
                                              'max-rx-ampdu-size' : 'Max RX AMPDU Size',
                                              'max-tx-ampdu-size' : 'Max TX AMPDU Size',
                                              'max-tx-ampdu-count-be' : 'Max TX AMPDU Count BE',
                                              'max-tx-ampdu-count-bk' : 'Max TX AMPDU Count BK',
                                              'max-tx-ampdu-count-vi' : 'Max TX AMPDU Count VI',
                                              'max-tx-ampdu-count-vo' : 'Max TX AMPDU Count VO',
                                              'max-vht-mpdu-size' : 'Max VHT MPDU Size',
                                              'min-mpdu-start-spacing' : 'Min MPDU Start Spacing',
                                              'mpdu-agg' : 'MPDU AGG',
                                              'short-guard-intvl-20MHz' : 'Short GI 20 MHz',
                                              'short-guard-intvl-40MHz' : 'Short GI 40 MHz',
                                              'short-guard-intvl-80MHz' : 'Short GI 80 MHz',
                                              'stbc-rx-streams' : 'STBC RX Streams',
                                              'stbc-tx-streams' : 'STBC TX Streams',
                                              'supported-mcs-set' : 'Supported MCS Set',
                                              'temporal-diversity' : 'Temporal Diversity',
                                              'very-high-throughput-enable' : 'VHT Enable',
                                              'vht-mu-txbf-enable' : 'VHT MU TXBF Enable',
                                              'vht-supported-mcs-map' : 'VHT Supported MCS Map',
                                              'vht-txbf-explicit-enable' : 'VHT TXBF Exp Enable',
                                              'vht-txbf-sounding-interval' : 'VHT TXBF Sounding Interval'
                                              },
                    'wlan ssid-profile' : {'wlan ssid-profile' : 'SSID Profile',
                                           'a-basic-rates' : 'A Rates Required',
                                           'a-tx-rates' : 'A Rates Allowed',
                                           'ageout' : 'Station Ageout',
                                           'auth-req-thresh' : 'Auth Request Threshold',
                                           'dtim-period' : 'DTIM Period',
                                           'edca-parameters-profile ap' : 'EDCA Profile AP',
                                           'edca-parameters-profile station' : 'EDCA Profile Client STA',
                                           'essid' : 'ESSID',
                                           'g-basic-rates' : 'G Rates Required',
                                           'g-tx-rates' : 'G Rates Allowed',
                                           'ht-ssid-profile' : 'HT SSID Prof',
                                           'max-clients' : 'SSID Max Clients',
                                           'max-retries' : 'SSID Max Retries',
                                           'max-tx-fails' : 'SSID Max TX Fails',
                                           'opmode' : 'WLAN OPMODE',
                                           'rts-threshold' : 'RTS Threshold',
                                           'wepkey1' : 'SSID WEPKEY1',
                                           'wepkey2' : 'SSID WEPKEY2',
                                           'wepkey3' : 'SSID WEPKEY3',
                                           'wepkey4' : 'SSID WEPKEY4',
                                           'weptxkey' : 'SSID WEP TX KEY',
                                           'wmm-be-dscp' : 'WMM BE DSCP',
                                           'wmm-bk-dscp' : 'WMM BK DSCP',
                                           'wmm-ts-min-inact-int' : 'WMM TS MIN Inactivty Interval',
                                           'wmm-vi-dscp' : 'WMM VI DSCP',
                                           'wmm-vo-dscp' : 'WMM VO DSCP',
                                           'wpa-hexkey' : 'WPA Hexkey',
                                           'wpa-passphrase' : 'WPA PW',
                                           },
                   
                   }
object_values_dict = {}                    
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

def gather_objects(lines):
    
    current = 0
    objects = {}
    while current < len(lines):
        current_line = lines[current]
        current_object = [current_line]
        current_object_name = get_object_name_from_line(current_line)
        current += 1
        if current == len(lines):
            break
        while lines[current].strip() != '!':
            current_object.append(lines[current])
            current += 1
            if current == len(lines):
                break
        if current_object_name in objects:
            objects[current_object_name].append(current_object)
        else:
            objects[current_object_name] = [current_object]
        current += 1
    return objects

def process_objects(objects):

    objects_attributes = {} 
    for object_name in objects:
        object_list = objects[object_name]
        object_attributes = []
        for object in object_list:
            object_attributes.append(group_object_attributes(object))
        objects_attributes[object_name] = object_attributes
    return objects_attributes 

def build_attributes_arrays(objects_attributes):

    attributes_arrays = []
    for objects in objects_attributes:
        attributes_object = add_keys_to_attributes_object(objects_attributes[objects]) 
        for object_attributes in objects_attributes[objects]:
            for attribute in object_attributes:
                processed_attribute_list = process_attribute_list(object_attributes[attribute])
                attributes_object[attribute].append(processed_attribute_list)
            for attribute in attributes_object:
                if not attribute in object_attributes:
                    attributes_object[attribute].append('')
        attributes_arrays.append(attributes_object)
    return attributes_arrays
            
def add_keys_to_attributes_object(objects):
    attributes_object = {}
    for object in objects:
        for key in object:
            if not key in attributes_object:
                attributes_object[key] = []
    return attributes_object

def process_attribute_list(list):

    if len(list) == 0:
        return ''
    processed_list = list[0]
    for word in list[1:]:
        processed_list += f' ,{word}'
    return processed_list

def get_object_name_from_line(object):
    words = object.strip().split(' ')
    return join_words(words[:-1], ' ') 

def group_object_attributes(object):
    groups = {}
    name_line = join_words(object[0].split(' ')[:-1], ' ')
    input_name = object[0].strip().split(' ')[-1].replace('"','')
    object_name = name_line
    groups[object_name] = [input_name]

    if object_name in object_values_dict:    
        for line in object[1:]:
            line = line.strip().replace('"', '')
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
    elif object_name in special_objects_dict:
        groups = special_objects_dict[object_name](object[1:], groups)
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
    words = line.strip().split(' ')
    options = process_expression(words, current, words[0])
    return options[1]

def create_expanded_cli_commands():
    cli_commands_path = 'test_cli_commands.txt'
    expanded_cli_commands = 'expanded_cli_commands.txt'
    cli_lines = []
    with open(cli_commands_path) as cli_file:
        cli_lines = cli_file.readlines()
    with open(expanded_cli_commands, 'w') as expanded_file:
        indentation = '    '
        for line in cli_lines:
            if line == '!\n' or line == '!':
                expanded_file.write(line)
            else:
                if ' ' != line[0]:
                    indentation = ''
                processed_line = process_line(line)
                for new_line in processed_line:
                    expanded_file.write(f'{indentation}{new_line}\n')

def populate_objects_value_dict():
    cli_commands_path = 'expanded_cli_commands.txt'
    with open(cli_commands_path) as cli_file:
        user_input = re.compile(r'<.+>')
        lines = cli_file.readlines()
        current = 0
        while(current < len(lines)):
            if user_input.match(lines[current].split(' ')[-1]):
                object_name = join_words(lines[current].strip().split(' ')[:-1], ' ')
                object_values_dict[object_name] = []
                current += 1
                while(current < len(lines) and lines[current] != '!\n'):
                    current_line = lines[current].strip()
                    if is_simple_parameter(current_line):
                        keywords = current_line.split(' ')
                        if len(keywords) > 1:
                            keywords = keywords[:-1]
                        command = join_words(keywords, ' ')
                        object_values_dict[object_name].append(command)
                    else:
                        if object_name in multi_value_parameter:
                            multi_value_parameter[object_name].append(current_line.split(' ')[0])
                        else:
                            multi_value_parameter[object_name] = [current_line.split(' ')[0]]
                    current += 1
                current += 1

def is_simple_parameter(line):
    words = line.split(' ')
    is_simple = True
    multiple_user_input = False
    user_input = re.compile(r'<\w+>')
    keyword_pairs = {}
    current_keyword = ''
    for word in words:
        if user_input.match(word):
            if current_keyword in keyword_pairs:
                is_simple = False
                multiple_user_input = True
                break
            else:
                keyword_pairs[current_keyword] = [word]
        else:
            if current_keyword in keyword_pairs:
                current_keyword = '' 
            if current_keyword == '':
                if len(keyword_pairs.keys()) == 1:
                    is_simple = False
                    break
                else:
                    current_keyword = word
            else:
                current_keyword += f' {word}'
    if len(keyword_pairs.keys()) > 1 or multiple_user_input:
        is_simple = False
    return is_simple

def process_bandwidth_contract(bwc_line):
    bwc_words = bwc_line.strip().split(' ')
    bwc_dict = {}
    base_name = bwc_words[0]
    current = 0
    current_word = bwc_words[current]
    if current_word == 'app' or current_word == 'appcategory':
        current_name = base_name + ' ' + 'application'
        bwc_dict[current_name] = current_word
        current_name = base_name + ' ' + current_word
        current += 1
        bwc_dict[current_name] = bwc_words[current]
        current += 1
        bwc_dict[base_name] = bwc_words[current]
        current += 1
        current_name = current_name + ' ' + bwc_words[current]
        bwc_dict[current_name] = bwc_words[current]
    else:
        bwc_dict[base_name] = bwc_words[current]
        current += 1
        current_name = base_name + ' direction'
        bwc_dict[current_name] = bwc_words[current]
    return bwc_dict

def process_int_access_group(ag_line):
    ag_words = ag_line.strip().split(' ')
    ag_dict = {}
    base_name = ag_words[0] + ' ' + ag_words[1]
    current = 2
    ag_name = ag_words[current]
    current += 1
    current_word = ag_words[current]
    name = base_name + ' ' + current_word
    ag_dict[name] = ag_name
    return ag_dict

def is_in_multi_value_dict(object, line):
    word = line.strip().split(' ')[0]
    return word in multi_value_parameter[object]

def process_acl(aces, group):
    joined_aces = []
    for ace in aces:
        joined_aces.append(ace.strip())
    group['acl session aces'] = joined_aces
    return group

def transform_attribute_array_to_array_tables(object_name, attribute_array):
    table_headers = []
    #object_dict = cli_to_api_dict[object_name]
    arrays = []
    for key in attribute_array:
        table_headers.append(key)
        arrays.append(attribute_array[key])
    number_of_objects = len(arrays[0])
    current = 0
    zipped_arrays = [table_headers]
    while current < number_of_objects:
        current_array = []
        for array in arrays:
            current_array.append(array[current])
        current += 1
        zipped_arrays.append(current_array)
    return zipped_arrays

def write_to_excel(title, data, workbook, start):
    
    current_ws = workbook.create_sheet(title=title)
    title_row_color = 'C0504D'

    for row in data:
        current_ws.append(row)

    colors = ['E6B8B7', 'F2DCDB']
    color_index = 0
    rows = current_ws.rows
    for row in rows:
        if color_index == 0:
            for cell in row:
                cell.fill = PatternFill('solid', fgColor = title_row_color)
                cell.font = Font(color='FFFFFF')
        else:
            for cell in row:
                cell.fill = PatternFill('solid', fgColor=colors[color_index%2])
                cell.font = Font(color='000000')
        color_index += 1
    
    column_widths = []
    for row in data:
        for i, cell in enumerate(row):
            if len(column_widths) > i:
                if len(cell) > column_widths[i]:
                    column_widths[i] = len(cell)
            else:
                column_widths += [len(cell)]
    
    for i, column_width in enumerate(column_widths,1):  # ,1 to start at 1
        current_ws.column_dimensions[get_column_letter(i)].width = column_width + 5

    table = Table(displayName='SSID',ref=f'A{start}:F{start + len(data)}')
    current_ws.add_table(table)

def add_table_to_worksheet(data,worksheet,table_name='',start=1):
    
    title_row_color = 'C0504D'
    cell_letter = [letter.upper() for letter in 'abcdefghijklmnopqrstuvwxyz']
    end_cell_number = start + len(data) - 1
    end_cell = cell_letter[len(data[0])-1]
    num_columns = len(data[0])

    current = start
    data_index = 0
    while current <= end_cell_number:
        current_column = 0
        current_row_cells = []
        while current_column < num_columns:
            current_row_cells.append(worksheet[f'{cell_letter[current_column]}{current}'])
            current_column += 1
        current_data_row = data[data_index]
        for cell,data_value in zip(current_row_cells,current_data_row):
            cell.value = data_value
        current += 1
        data_index += 1 

    colors = ['E6B8B7', 'F2DCDB']
    color_index = 0
    rows = worksheet[start:end_cell_number]
    for row in rows:
        if color_index == 0:
            for cell in row:
                cell.fill = PatternFill('solid', fgColor = title_row_color)
                cell.font = Font(color='FFFFFF')
        else:
            for cell in row:
                cell.fill = PatternFill('solid', fgColor=colors[color_index%2])
                cell.font = Font(color='000000')
        color_index += 1
    
    column_widths = []
    for row in data:
        for i, cell in enumerate(row):
            if len(column_widths) > i:
                if len(cell) > column_widths[i]:
                    column_widths[i] = len(cell)
            else:
                column_widths += [len(cell)]
    
    for i, column_width in enumerate(column_widths,1):  
        worksheet.column_dimensions[get_column_letter(i)].width = column_width + 5

    table = Table(displayName=table_name,ref=f'A{start}:{end_cell}{end_cell_number}')
    worksheet.add_table(table)

special_objects_dict = {'ip access-list session' : process_acl }