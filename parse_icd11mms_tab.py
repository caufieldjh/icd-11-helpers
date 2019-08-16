#!/usr/bin/python
#parse_icd11_mms_tab.py

'''
A simple parser for the tab file ("spreadsheet file") provided
by WHO for the ICD-11 MMS linearization.
The original file is in xlsx format.
For simplicity, this script will accept a tsv version as input,
from the same directory as the script, provided as a command line
argument.
It outputs a tsv file of the following format:

CodeA	TitleA	is_a	CodeB	TitleB

where is_a relations are defined by the hierarchy defined by the input.
Residual children ("other" and "unspecified") are included.
Titles without codes are assigned the code "NA" upon writing.
'''

__author__= "Harry Caufield"
__email__ = "jcaufield@mednet.ucla.edu"

import sys, argparse

## Constants and Options

parser = argparse.ArgumentParser()
parser.add_argument("infile", help="file for input")
args = parser.parse_args()

## Classes

## Functions
def parse(infile):
	'''Store the parsed data'''
	
	infile.readline() #Skip the header
	
	all_nodes = {}
	
	node_id = -1
	previous_level = 0
	most_recent_id_at_level = {} #levels are keys, node_id is value
	
	for line in infile:
		node_id = node_id +1
		
		splitline = line.split("\t")
		code = splitline[2]
		title = splitline[4]
		
		cleantitle = ""			#The title indicates the level
		level = 0				#But we just want the text in the title
		counting = True
		
		for char in title:		#There are other ways to do this, yes
			if char == "-" and counting:
				level = level +1
			if char not in ["-"," "]:
				counting = False
			if not counting:
				cleantitle = cleantitle + char
				
		cleantitle = cleantitle.lstrip()
		code_and_title = [code,cleantitle]
		
		#Now let's figure out what the parent is.
		#Keep track of the node_id of the previous level was
		if level == 0:
			parent = "None"
		else:
			parent = most_recent_id_at_level[level - 1]
		
		all_nodes[node_id] = [code_and_title, parent] #parent is a node_id
		
		previous_level = level
		
		most_recent_id_at_level[level] = node_id
		
	return all_nodes
		
def write_out(node_dict):
	'''Writes the output'''
	
	with open("outfile.tsv", "w") as outfile:
		for node in node_dict:
			parent_id = node_dict[node][1]
			codeA = node_dict[node][0][0]
			titleA = node_dict[node][0][1]
				
			if parent_id == "None":
				pass
			else:
				codeB = node_dict[parent_id][0][0]
				titleB = node_dict[parent_id][0][1]
				
				if codeA == "":
					codeA = "NA"
				if codeB == "":
					codeB = "NA"
				
				out_string = "%s\t%s\tis_a\t%s\t%s\n" % (codeA, titleA, codeB, titleB)
				outfile.write(out_string)
	
## Main
def main():
	print("Opening %s" % args.infile)
	with open(args.infile) as infile:
		output = parse(infile)
	write_out(output)
	print("Done.")
	
if __name__ == "__main__":
	sys.exit(main())
