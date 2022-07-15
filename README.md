# AOS6-CLI-Parser

This is a command line tool that takes one or more AOS6 configuration files, creates tables from the information and places them into excel file(s).

## Files that the script can process

What information can be inside the files?

Any CLI output from an AOS6 system can be placed inside the file(s) you want the script to process. Only two types of CLI commands will be processed:
    1. show run
    2. any show command that has a table as an output

Any show command that doesn't fall into the categories mentioned above will be ignored.

Do I have to separate the show run and other show commands?

No. In fact it's more efficient if you place all the CLI output you gather into one file. The script will separate the table outputs and the show run output automatically and place them into separate files.

### Usage

There are a few flags that you can supply to the script:

    -a, --aggregate: If supplied, must be used with the -d/--directory flag. The script will go through the files in the directory and gather CLI lines like ap group, ssid, ssid + opmode, etc and place them into a text file.

    -d, --directory: If supplied, the script will process all files in the directory. All the show table information will be placed into one file. The tables will be labled with the device host name. All the show run information will be placed into individual files with the device host name as the output file name.

    -i,--input: Use to process only one file. The script will separate the show running-config and other show commands into separate files.

Ex. Processing a single file:
    python a6p.py -i your-input-file-name

Ex. Processing a directory of configuration files:
    python a6p.py -d path/to/directory

Ex. Creating an aggregate file with selective CLI commands:
    python a6p.py -d path/to/directory -a

#### What CLI lines are gathered when using the aggregate flag?

This feature was written with assessments in mind so the information gathered is meant to be included in the assessment report. As such, there are only a few CLI lines that are of interest:

    1. ap group
    2. virtual ap
    3. virtual ap with ssid sub-line.
    4. wlan ssid-profile
    5. wlan ssid-profile with opmode sub-line.
    6. aaa-profile with dot1x-server-group sub-line.
    7. wlan ht-ssid-profile
    8. ntp server
    9. mgmt-user
    10. snmp-server community
    11. snmp-server host
    12. ip name-server