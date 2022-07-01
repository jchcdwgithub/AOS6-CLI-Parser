import aos6parser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input',help='Path to the CLI file')
parser.add_argument('-o','--output',help='Path and filename for the excel file.')
parser.add_argument('-t','--template',help='File that has the template cli commands.')
parser.add_argument('-s','--show',help='Parses a file of specific show commands. All output from file should be tabular.',action=argparse.BooleanOptionalAction)
parser.add_argument('-a', '--aggregate',help="Process a directory of show run files and aggregate all information into an output file. Must use with -d or --directory option.",action=argparse.BooleanOptionalAction)
parser.add_argument('-d', '--directory',help="Path to a directory with files you'd like to process.")
args = parser.parse_args()
if not args.input:
    input_file = input('Filename of configuration file: ')
else:
    input_file = args.input
if not args.output:
    output_file = 'cli6_tables.xlsx'
else:
    output_file = args.output
if not args.template:
    template_file = 'template_cli_commands.txt'
else:
    template_file = args.template
if args.show:
    with open(input_file) as show_file:
        tables = aos6parser.group_show_information_into_tables(show_file)
        aos6parser.write_show_tables_to_excel_worksheets(tables,output_file)

elif args.aggregate:

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

    for regex in regex_list:
        aos6parser.grab_specific_lines_from_files(directory,output_file,regex)
else:
    aos6parser.populate_cli_rules(template_file)
    cli_objects = aos6parser.make_cli_objects(input_file)
    attributes_array = aos6parser.build_attributes_arrays(cli_objects)
    tables_arrays = aos6parser.build_tables_arrays(attributes_array)
    aos6parser.write_tables_to_excel_worksheets(tables_arrays,output_file)