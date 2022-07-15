import aos6parser
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input',help='Path to the CLI file')
parser.add_argument('-o','--output',help='Path and filename for the excel file.')
parser.add_argument('-t','--template',help='File that has the template cli commands.')
parser.add_argument('-a', '--aggregate',help="Process a directory of show run files and aggregate all information into an output file. Must use with -d or --directory option.",action=argparse.BooleanOptionalAction)
parser.add_argument('-d', '--directory',help="Path to a directory with files you'd like to process.")
args = parser.parse_args()
if not args.template:
    template_file = 'template_cli_commands.txt'
else:
    template_file = args.template

if args.aggregate:

    regex_list = [
        ['^ap-group .+'],
        ['^wlan virtual-ap .+'],
        ['^wlan virtual-ap .+', '^ +ssid-profile .+'],
        ['^wlan ssid-profile .+'],
        ['^wlan ssid-profile .+', '^ +opmode .+'],
        ['^aaa profile .+', '^ +dot1x-server-group .+'],
        ['^wlan ht-ssid-profile .+'],
        ['^ap-group .+'],
        ['^ntp server .+'],
        ['^mgmt-user .+'],
        ['^snmp-server community .+'],
        ['^snmp-server host .+'],
        ['^ip name-server .+'],
    ]

    if args.directory:
        directory = args.directory
    else:
        directory = input("Please provide the path to the directory with the files you'd like to process. ")
    if args.output:
        output_file = args.output
    else:
        output_file = 'aggregate_file.txt'
    for regex in regex_list:
        aos6parser.grab_specific_lines_from_files(directory,output_file,regex)

if args.directory:
    directory = args.directory
    show_runs = []
    show_tables = []
    for file in os.listdir(directory):
        file_name = os.path.join(directory,file)
        with open(file_name) as config_f:
            config_lines = config_f.readlines()
            empty_prompt = aos6parser.get_command_line_prompt(config_lines)
            if empty_prompt != '':
                appliance_name = aos6parser.get_appliance_name(empty_prompt)
                show_run,show_table = aos6parser.group_run_and_table_commands(config_lines)
                if len(show_run) > 0:
                    show_run.append(appliance_name)
                    show_runs.append(show_run)
                if len(show_table) > 0:
                    show_tables.append(aos6parser.new_group_show_information_into_tables(show_table))
                for show_command in show_tables[-1]:
                    table = show_tables[-1][show_command]
                    table.append(appliance_name)

    aggregated_tables = {}

    for show_table in show_tables:
        for show_command in show_table:
            if show_command in aggregated_tables:
                aggregated_tables[show_command].append(show_table[show_command])
            else:
                aggregated_tables[show_command] = [show_table[show_command]]

    aos6parser.new_write_show_tables_to_excel_worksheets(aggregated_tables)

    if len(show_runs) > 0:
        aos6parser.populate_cli_rules(template_file)

        for show_run in show_runs:
            output_file = show_run[-1] + ".xlsx"
            cli_objects = aos6parser.make_cli_objects(show_run[:-1])
            attributes_array = aos6parser.build_attributes_arrays(cli_objects)
            tables_arrays = aos6parser.build_tables_arrays(attributes_array)
            aos6parser.write_tables_to_excel_worksheets(tables_arrays,output_file)

else:
    if not args.input:
        input_file = input("Configuration file to process: ")
    else:
        input_file = args.input
    if args.output:
        if 'xlsx' in args.output:
            output_file = args.output.split('.')[0]
        else:
            output_file = args.output
    else:
        output_file = 'parsed_file'
    with open(input_file) as config_file:
        config_lines = config_file.readlines()
        empty_prompt = aos6parser.get_command_line_prompt(config_lines)
        appliance_name = aos6parser.get_appliance_name(empty_prompt)
        show_run,show_table = aos6parser.group_run_and_table_commands(config_lines)
        if len(show_table) > 0:
            show_output = output_file + '_show.xlsx'
            show_tables = aos6parser.new_group_show_information_into_tables(show_table)
            aos6parser.write_show_tables_to_excel_worksheets(show_tables,output_file=show_output)
        if len(show_run) > 0:
            run_output = output_file + '_run.xlsx'
            cli_objects = aos6parser.make_cli_objects(show_run)
            attributes_array = aos6parser.build_attributes_arrays(cli_objects)
            tables_arrays = aos6parser.build_tables_arrays(attributes_array)
            aos6parser.write_tables_to_excel_worksheets(tables_arrays,run_output)