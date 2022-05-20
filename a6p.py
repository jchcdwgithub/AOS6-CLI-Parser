import aos6parser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i','--input',help='Path to the CLI file')
parser.add_argument('-o','--output',help='Path and filename for the excel file.')
parser.add_argument('-t','--template',help='File that has the template cli commands.')
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
aos6parser.populate_cli_rules(template_file)
cli_objects = aos6parser.make_cli_objects(input_file)
attributes_array = aos6parser.build_attributes_arrays(cli_objects)
tables_arrays = aos6parser.build_tables_arrays(attributes_array)
aos6parser.write_tables_to_excel_worksheets(tables_arrays,output_file)