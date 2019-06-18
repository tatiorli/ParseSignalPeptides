#!/usr/bin/python3
# Welcome to ParseSignalPeptides.py. This program was developed in order to return a query list of peptides from a Protein database (Uniprot) and parse the results looking for a signal peptide.
# Copyright by Erika Pinheiro-Machado and Tatiana Orli Milkewitz Sandberg
# 2019 Version 1.7

# Starts by importing requested modules
import getopt, sys, requests, time,  bs4, re
# Import pandas as panel data
import pandas as pd

# Prompt the user for the input filename and output filename
inputfile = ''
outputfile = ''
argv = sys.argv[1:]

try:
    opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
except getopt.GetoptError:
    print("ParseSignalPeptides.py -i <inputfile> -o <outputfile>")
    sys.exit(2)
for opt, arg in opts:
    if opt == "-h":
        print("ParseSignalPeptides.py -i <inputfile> -o <outputfile>")
        sys.exit()
    elif opt in ("-i", "--input"):
        inputfile = arg
    elif opt in ("-o", "--output"):
        outputfile = arg

print(f"Input file is: {inputfile}")
print(f"Output file is: {outputfile}")

# Open excel file
inputfile = "fim_out.xlsx"
# Create an output file
outputfile = "fim_out2.xlsx"
# Loading the excel files and create extra columns for the results
pd.options.mode.chained_assignment = None
xl = pd.ExcelFile(inputfile)
# Create an object with the name of the first sheet
sheetname = xl.sheet_names[0]
#load the first sheet
excel = xl.parse(sheetname)
#create a mirror object for the inputfile
excel_new = excel.copy()
#create new columns for the results
excel_new = excel_new.assign(signal_sequence = pd.Series("", index=excel_new.index))
excel_new = excel_new.assign(locations = pd.Series("", index=excel_new.index))
excel_new = excel_new.assign(full_sequence = pd.Series("", index=excel_new.index))
excel_new = excel_new.assign(kdel_found = pd.Series("", index=excel_new.index))

# Create the output file for result saving using a Pandas Excel writer
writer = pd.ExcelWriter(outputfile)

# Create empty list for storage of results of uniprot
datasets = []

# Start execution time
print("###################################################")
print("Start execution: %s" % time.ctime())
print("###################################################")

# Grab the acessions from Uniprot and iterate in that list
count = 0
failed = 0
for i in excel_new.index:
    ## Create var with the data for the search and Use the acession code to get the xml file
    params = {"query": excel_new['UniProt'][i], "format": "xml"}
    response = requests.get("http://www.uniprot.org/uniprot/", params)
    soup = bs4.BeautifulSoup(response.content, 'html.parser')
    # Iterate inside the acessions's code list, stop after 19 requests and break 5 seconds (to avoid overload of Uniprot server)
    if count < 20:
        count += 1
        print("COUNT IS:",count)
        # Check if the protein accession in not obsolete in Uniprot (by checking soup contents)
        if soup.contents:
            pass
        else:
            excel_new['full_sequence'][i] = "obsolete entry"
            failed += 1
            continue
        # First, Grab all the features for subcellular location information
        sub_loc = soup.select('comment[type="subcellular location"]')
        # Transform it into a string and match the string whenever appears a subcellular location
        a = str(sub_loc)
        # result = re.findall(r'<location evidence="\d+">([^<]+)<\/location>', a)
        result = []
        for tag in soup.select('location[evidence]'):
            result.append(tag.get_text().strip())
        excel_new['locations'][i] = ', '.join(result)
        print(excel_new['locations'][i])
        # Second, Grab the raw protein sequence
        sequence = soup.select('sequence[length]')[0].get_text().replace('\n', '')
        print(sequence)
        excel_new['full_sequence'][i] = sequence

        print("Time now: %s" % time.ctime())
        # If the protein has a signal peptide, parse the information
        features = soup.select('feature[type="signal peptide"]')
        if len(features) > 0:
            # Grab start and end position of the signal peptide
            feature = features[0]
            start = feature.select('begin')[0].get('position')   # Get start position
            print(start)
            end = feature.select('end')[0].get('position')   # Get end position
            print(end)
            excel_new['signal_sequence'][i] = start+" "+end
            # Last, look for the KDEL in the final 4 aminoacids
            searcher = re.compile('[ARNDCQEGHILKMFPSTWYVBZ][ARNDCQEGHILKMFPSTWYVBZ][E][L]')
            # Select last four characters of the full sequence
            final_aa = sequence[-4:]
            # Check if there is a match with the regular expression
            matched = searcher.match(final_aa)
            if matched:
                excel_new['kdel_found'][i] = matched.group(0)
    else:
        time.sleep(30)
        count = 0

# Change columns final names or rename columns for clarification
excel_new = excel_new.rename(columns={'name': 'Protein names','gene name':'Gene names','signal_sequence': 'Signal peptide', 'locations': 'Subcellular location', 'full_sequence': 'Sequence'})
## Write all the results in the new excel file
excel_new.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()

## End of script
print("###################################################")
print(f"Finished retrieving accession numbers. Number of failed attempts: {failed} ")
print("End execution: %s" % time.ctime())
print("###################################################")