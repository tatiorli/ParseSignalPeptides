#!/usr/bin/python3
# Welcome to ParseSignalPeptides.py. This program was developed in order to return a query list of peptides from a Protein database (Uniprot) and parse the results looking for a signal peptide.
# Copyright by Erika Pinheiro-Machado and Tatiana Orli Milkewitz Sandberg
# 2022 Version 1.9

# Starts by importing requested modules
import requests, bs4
import pandas as pd
import tkinter as tk
from tkinter import filedialog

input_file_path = None
output_file_path = None

def run_process():
    # Loading the excel files and create extra columns for the results

    pd.options.mode.chained_assignment = None
    xl = pd.ExcelFile(input_file_path)
    # Create an object with the name of the first sheet
    sheetname = xl.sheet_names[0]
    # load the first sheet
    excel = xl.parse(sheetname)
    # create a copied object for the inputfile
    excel_new = excel.copy()
    # create new columns for the results
    excel_new = excel_new.assign(signal_sequence = pd.Series("", index=excel_new.index))
    excel_new = excel_new.assign(locations = pd.Series("", index=excel_new.index))
    excel_new = excel_new.assign(full_sequence = pd.Series("", index=excel_new.index))

    # Create empty list for storage of results of uniprot
    datasets = []

    # Grab the acessions from Uniprot and iterate in that list
    count = 0
    failed = 0
    print("Analyzing your input list of proteins, please wait......")
    for row in excel_new.index:
        print(f"Processing {row}")
        if count == 20:
            time.sleep(30)
            count = 0
        ## Create var with the data for the search and Use the acession code to get the xml file
        params = {"query": excel_new['UniProt'][row], "format": "xml"}
        response = requests.get("http://www.uniprot.org/uniprot/", params)
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        # Iterate inside the acessions's code list, stop after 19 requests and break 5 seconds (to avoid overload of Uniprot server)
        count += 1
        # Check if the protein accession in not obsolete in Uniprot (by checking soup contents)
        if soup.contents:
            pass
        else:
            excel_new['full_sequence'][row] = "obsolete entry"
            failed += 1
            continue
        # First, Grab all the features for subcellular location information
        sub_loc = soup.select('comment[type="subcellular location"]')
        # Transform it into a string and match the string whenever appears a subcellular location
        a = str(sub_loc)
        result = []
        for tag in soup.select('subcellularlocation location'):
            result.append(tag.get_text().strip())
        excel_new['locations'][row] = ', '.join(result)
        # Second, Grab the raw protein sequence
        sequence = soup.select('sequence[length]')[0].get_text().replace('\n', '')
        excel_new['full_sequence'][row] = sequence
        # If the protein has a signal peptide, parse the information
        features = soup.select('feature[type="signal peptide"]')
        if len(features) > 0:
            # Grab start and end position of the signal peptide
            feature = features[0]
            start = feature.select('begin')[0].get('position')   # Get start position
            end = feature.select('end')[0].get('position')   # Get end position
            excel_new['signal_sequence'][row] = start+" "+end



    # Change columns final names or rename columns for clarification
    excel_new = excel_new.rename(columns={'name': 'Protein names','gene name':'Gene names','signal_sequence': 'Signal peptide', 'locations': 'Subcellular location', 'full_sequence': 'Sequence'})
    write_output(pd, excel_new)
    print(f"Total proteins retrieved: {count}, Failed requests: {failed}.")
    print("Program finished with success, click on button Close to exit. Have a nice day.")
    print("###################################################")


def write_output(pd, excel_new):
    # Create the output file for result saving using a Pandas Excel writer
    writer = pd.ExcelWriter(output_file_path)
    ## Write all the results in the new excel file
    excel_new.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()

def close_app():
    app.destroy()

# Prompt the user for the input filename
def select_input_file():
    global input_file_path
    input_file_path = filedialog.askopenfilename(filetypes=(("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("Any file", "*")))
    print("Parameters:")
    print(f"Input file is: {input_file_path}")

# Prompt the user for the output filename
def select_output_file():
    global output_file_path
    output_file_path = filedialog.asksaveasfilename(filetypes=(("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("Any file", "*")))
    print(f"Output file is: {output_file_path}")
    print("If the parameters are ok, please press the button Process and wait.")

app = tk.Tk()
app.title('Extract_proteomes_from_Uniprot')

input_button = tk.Button(app, text='Select input file', command=select_input_file)
input_button.pack()

output_button = tk.Button(app, text='Select output file', command=select_output_file)
output_button.pack()

process_button = tk.Button(app, text='Process', width=25, command=run_process)
process_button.pack()

exit_button = tk.Button(app, text='Close', width=25, command=close_app)
exit_button.pack()

app.mainloop()

## End of script
