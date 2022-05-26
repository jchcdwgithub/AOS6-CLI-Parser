import aos6parser
import openpyxl

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

def test_is_simple_returns_false_for_line_with_multiple_user_inputs():
    
    line = 'lease <days> <hours> <seconds>'
    generated = aos6parser.is_simple_parameter(line)
    expected = False
    assert expected == generated

def test_is_simple_returns_false_for_line_with_keyword_after_user_input():

    line = 'access-group <name> in'
    generated = aos6parser.is_simple_parameter(line)
    expected = False
    assert expected == generated

def test_format_names_replaces_quoted_names_at_end_of_string():

    line = 'description "Some Name"'
    generated = aos6parser.format_names(line)
    expected = 'description Some_Name'
    assert expected == generated

def test_format_names_replaces_quoted_names_not_at_end_of_string():

    line = 'some value "this and that" other options'
    generated = aos6parser.format_names(line)
    expected = 'some value this_and_that other options'
    assert expected == generated

def test_format_names_replaces_multiple_quoted_names():

    line = 'some value "this and that" other option "that and this" trailing'
    generated = aos6parser.format_names(line)
    expected = 'some value this_and_that other option that_and_this trailing'
    assert expected == generated

def test_calculate_column_letters_returns_single_letter_correctly():

    column_index = 23
    generated = aos6parser.calculate_column_letters(column_index)
    expected = 'X'
    assert expected == generated

def test_calculate_column_letters_returns_double_letters_correctly():

    column_index = 100
    generated = aos6parser.calculate_column_letters(column_index)
    expected = 'CV'
    assert expected == generated

def test_calculate_column_letters_returns_double_boundary_correctly():

    column_index = 27
    generated = aos6parser.calculate_column_letters(column_index)
    expected = 'AA'
    assert expected == generated

def test_swap_rows_cols_swaps_correctly():

    original_array = [['this','that', 'tother'],['those','thot', 'tsther'],['me','my','moo']]
    expected = [['this','those','me'],['that','thot','my'],['tother','tsther','moo']]
    generated = aos6parser.swap_rows_and_columns(original_array)
    assert expected == generated

def test_get_column_widths_returns_widest_widths_for_simple_matrix():

    matrix = [['this','those','thematic']]
    start = 5
    expected = {'E':4,'F':5,'G':8}
    generated = aos6parser.get_widest_column_widths(start,matrix)
    assert expected == generated

def test_get_column_widths_returns_widest_widths_for_complex_matrix():

    matrix = [['this','that','those'],['expeditious','annoyingly','prophetic'],['soporific','scrumptious','fun']]
    start = 10
    expected = {'J':11,'K':11,'L':9}
    generated = aos6parser.get_widest_column_widths(start,matrix)
    assert expected == generated

def test_group_rates_returns_correct_cli_line():

    cli_line = 'a-tx-rates 12 24 36'
    expected = 'a-tx-rates 12,24,36'
    generated = aos6parser.group_rates(cli_line)
    assert expected == generated

def test_find_table_end_returns_correct_index():

    wb = openpyxl.Workbook()
    ws = wb.active
    data = [['header1','header2','header3'],['value1','value2','value3']]
    aos6parser.add_table_to_worksheet(data,ws,table_name='table')
    wb.save('example.xlsx')
    expected = 3
    generated = aos6parser.find_table_end(ws)

    assert expected == generated

def test_get_command_line_prompt_returns_correctly_prompt():

    lines = ["random(DVLWI-DC-WC1) [MDC] *#show ap database long","show","#","(DVLWI-DC-WC1) [MDC] *#show rf ht-radio-profile"]
    expected = "(DVLWI-DC-WC1) [MDC] *#"
    generated = aos6parser.get_command_line_prompt(lines)
    assert expected == generated