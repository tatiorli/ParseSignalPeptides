#!/usr/bin/python3
# Welcome to ParseSignalPeptides.py. This program was developed in order to return a query list of peptides from a Protein database (Uniprot) and parse the results looking for a signal peptide.
# Copyright by Erika Pinheiro-Machado and Tatiana Orli Milkewitz Sandberg
# 2019 Version 1.8

# Starts by importing requested modules
import getopt, sys, requests, time,  bs4, re
# Import pandas as panel data
import pandas as pd

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def main(inputfile, outputfile):
    print(f"Input file is: {inputfile}")
    print(f"Output file is: {outputfile}")

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
        # print(f"Checking index: {i}\n")
        if count == 20:
            time.sleep(30)
            count = 0
        ## Create var with the data for the search and Use the acession code to get the xml file
        params = {"query": excel_new['UniProt'][i], "format": "xml"}
        response = requests.get("http://www.uniprot.org/uniprot/", params)
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        # Iterate inside the acessions's code list, stop after 19 requests and break 5 seconds (to avoid overload of Uniprot server)
        count += 1
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
        result = []
        for tag in soup.select('subcellularlocation location'):
            result.append(tag.get_text().strip())
        excel_new['locations'][i] = ', '.join(result)
        # Second, Grab the raw protein sequence
        sequence = soup.select('sequence[length]')[0].get_text().replace('\n', '')
        excel_new['full_sequence'][i] = sequence
        # If the protein has a signal peptide, parse the information
        features = soup.select('feature[type="signal peptide"]')
        if len(features) > 0:
            # Grab start and end position of the signal peptide
            feature = features[0]
            start = feature.select('begin')[0].get('position')   # Get start position
            end = feature.select('end')[0].get('position')   # Get end position
            excel_new['signal_sequence'][i] = start+" "+end
            # Last, look for the KDEL in the final 4 aminoacids
            searcher = re.compile('[ARNDCQEGHILKMFPSTWYVBZ]{2}EL')
            # Select last four characters of the full sequence
            final_aa = sequence[-4:]
            # Check if there is a match with the regular expression
            matched = searcher.match(final_aa)
            if matched:
                excel_new['kdel_found'][i] = matched.group(0)

        time.sleep(0.1)
        # Update Progress Bar
        printProgressBar(i + 1, len(excel_new.index), prefix = 'Progress:', suffix = 'Complete', length = 50)


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

if __name__ == "__main__":
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
    main(inputfile,outputfile)