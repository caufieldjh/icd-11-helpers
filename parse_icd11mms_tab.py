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

URI_A	CodeA	TitleA	ChapterA	is_a	URI_A	CodeB	TitleB	ChapterB

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
	'''Store the parsed data.
	A node_count is assigned internally to keep track of where
	we are in the file, but nodes are also assigned their linearization
	unique release ID (URI) as well as their plaintext
	chapter membership.'''
	
	infile.readline() #Skip the header
	
	all_nodes = {}
	
	node_count = -1
	previous_level = 0
	most_recent_id_at_level = {} #levels are keys, node_count is value
	
	for line in infile:
		node_count = node_count +1
		
		splitline = line.split("\t")
		
		uri = (splitline[1].split("/"))[-1]
		if uri in ["other","unspecified"]:
			cleanuri = (splitline[1].split("/"))[-2] + "/" + uri
		else:
			cleanuri = uri
		
		chapterno = splitline[9]
		
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
		
		#Now let's figure out what the parent is.
		#Keep track of the node_count of the previous level was
		if level == 0:
			parent = "None"
		else:
			parent = most_recent_id_at_level[level - 1]
		
		all_nodes[node_count] = {"uri":cleanuri,"code":code,"title":cleantitle,
								"chapter":chapterno,"parent":parent} #parent is a node_count
		
		previous_level = level
		
		most_recent_id_at_level[level] = node_count
		
	return all_nodes
		
def write_out(node_dict):
	'''Writes the output'''
	
	with open("outfile.tsv", "w") as outfile:
		for node in node_dict:
			parent_id = node_dict[node]["parent"]
			uriA = node_dict[node]["uri"]
			codeA = node_dict[node]["code"]
			titleA = node_dict[node]["title"]
			chapterA = node_dict[node]["chapter"]
				
			if parent_id == "None":
				pass
			else:
				uriB = node_dict[parent_id]["uri"]
				codeB = node_dict[parent_id]["code"]
				titleB = node_dict[parent_id]["title"]
				chapterB = node_dict[parent_id]["chapter"]
				
				if codeA == "":
					codeA = "NA"
				if codeB == "":
					codeB = "NA"
				
				out_string = "%s\t%s\t%s\t%s\tis_a\t%s\t%s\t%s\t%s\t\n" % (uriA, codeA, 
																titleA, chapterA, uriB,
																codeB, titleB, chapterB)
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
