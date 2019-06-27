# ParseSignalPeptides
2019 - Copyright by Erika Pinheiro-Machado and Tatiana Orli Milkewitz Sandberg

ParseSignalPeptides.py was developed in order to extract a query list of peptides from a Protein database (Uniprot) and parse the results obtained, looking for a signal peptide. This program was specially tailored to use this protein database with its .xml output format and relies solely in the information provided by it. The program provides the following information for each line entry of a Uniprot accession code: signal peptide range, Uniprot “Subcellular location” annotation, the protein complete sequence and if the motif “XXEL” was found in the end of the protein sequence and the found motif sequence.

•	Software requirements

*	Python version 3.7 or earlier. We do not guarantee compatibility with previous versions.
*	Python libraries employed by this program: getopt, sys, requests, time, bs4, re and pandas.
*	Other option could be instead of installing the previous modules, to install Anaconda.
This software is compatible with all Windows and Linux systems.

•	Mandatory input file format and command syntax

The user needs to provide an excel input file in .xlsx format (the default XML-based file format for Excel 2010 and Excel 2007) with the list of proteins to parse. It must contain three columns named as: “Uniprot” (containing the Uniprot accession codes); “Protein names” and “Gene names”. When executed, the program expect the user to provide the name (and path location) of the input file. We recommend to execute this program in the same directory of the excel input file. The program also expects an output file name for latter saving the results. Syntax of the basic command:

ParseSignalPeptides.py -i [inputfile] -o [outputfile]

•	Explained software code

The program starts by importing requested modules and import pandas as panel data.
Then, it prompts the user for the input filename and output filename. It opens the excel input file and create an output file. It loads the content of the input file and creates extra columns for result handling. Then it collects the column of the list of accessions numbers for Uniprot querying and iterate in that list, using the accession to request the corresponding .xml file from the database. For each .xml file, it will parse it and collect: 1st) All the features for subcellular location information; 2nd) The raw protein sequence; 3rd) Checks if the protein presents a signal peptide, and if yes, 4th) parse the information for the start and end position of the signal peptide; 5th) Locate the XXEL end motif and collect the sequence final 4 amino acids. Last, the program will save all the results in the new excel output file.

•	Quick tutorial: command and expected output

First, install all the Python modules requested by this software. Then, download from our GitHub repository an input file named “example.xlsx” and execute this command in your preferred command line:

ParseSignalPeptides.py -i example.xlsx -o outputfile.xlsx

OBSERVATION: Empty spaces in the output file means that the provided information of that accession number for that column is also empty. For example, if a protein does not contain an annotated signal protein in Uniprot, it will appears as a blank space in the excel output file. 

•	Citing

If ParseSignalPeptides.py was used in your analysis, please issue the following citation:

