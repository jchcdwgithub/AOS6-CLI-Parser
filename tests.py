import aos6parser

def test_join_words_joins_array_with_correct_separator():
    words_list = ['this','and','that']
    generated = aos6parser.join_words(words_list, ' ')
    expected = 'this and that'
    assert expected == generated

def test_split_object_identifier_gives_name_underscored_name():
    words_list = ['ip','access-list','session','"Some','random','name"']
    generated = aos6parser.split_object_identifier(words_list,3) 
    expected = 'Some_random_name'
    assert expected == generated

def test_split_object_id_gives_single_word_names_correctly():
    words_list = ['ip','access-list','session','someName']
    generated = aos6parser.split_object_identifier(words_list,3) 
    expected = 'someName'
    assert expected == generated

def test_get_unique_columns_returns_dictionary_of_grouped_attributes():

    object = ['user-role name', 'captive-portal "default"', 'bw-contract "50 Mbps" upstream', 'bw-contract "50 Mbps" downstream', 'vlan 312', 'access-list session global-sacl', 'access-list session apprf-kiosk-sacl']
    generated = aos6parser.group_object_attributes(object)
    expected = {'bw-contract':['"50 Mbps" upstream', '"50 Mbps" downstream'],
                'access-list session': ['global-sacl', 'apprf-kiosk-sacl'],
                'vlan': ['312'],
                'captive-portal': ['"default"']}
    assert expected == generated

def test_add_options_returns_true_for_extended_options():

    options = ['this string', 'that string']
    added_options = ['this string extended more', 'this string extended more1', 'that string extended more', 'that string extended more1']
    generated = aos6parser.add_options(options,added_options)
    assert added_options == generated

def test_add_options_returns_false_for_unique_added_options():

    options = ['some string'] 
    added_options = ['this string extended', 'that string extended']
    generated = aos6parser.add_options(options,added_options)
    expected = ['some string', 'this string extended', 'that string extended']
    assert expected == generated

def test_process_line_processes_line_with_no_branching():

    line = "description <string>"
    generated = aos6parser.process_line(line)
    expected = ['description <string>'] 
    assert expected == generated

def test_process_line_processes_line_with_single_non_terminating_branch():

    line = "interface { fastethernet | gigabitethernet } <slot>/<module>/<port>"
    generated = aos6parser.process_line(line)
    expected = ['interface fastethernet <slot>/<module>/<port>', 'interface gigabitethernet <slot>/<module>/<port>'] 
    assert expected == generated

def test_process_line_processes_line_with_nested_expressions():

    line = "switchport { access vlan <vlan> | mode { access | trunk } | trunk { allowed vlan { <vlans> | add <vlans> | all | except <vlans> | remove <vlans> } | native vlan <vlan> } }"
    generated = aos6parser.process_line(line)
    expected = ['switchport access vlan <vlan>', 
                'switchport mode access',
                'switchport mode trunk',
                'switchport trunk allowed vlan <vlans>',
                'switchport trunk allowed vlan add <vlans>',
                'switchport trunk allowed vlan all',
                'switchport trunk allowed vlan except <vlans>',
                'switchport trunk allowed vlan remove <vlans>',
                'switchport trunk native vlan <vlan>']
    for option in generated:
        assert option in expected

def test_is_simple_parameter_returns_true_for_single_keyword_pair_line():

    line = 'switchport trunk allowed vlan <vlans>'
    generated = aos6parser.is_simple_parameter(line)
    expected = True
    assert expected == generated

def test_is_simple_parameter_returns_false_for_multi_keyword_pair_line():

    line = 'xsec point-to-point <macaddr> <key> allowed vlan <vlans>'
    generated = aos6parser.is_simple_parameter(line)
    expected = False
    assert expected == generated