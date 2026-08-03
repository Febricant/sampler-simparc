################################################################################
# PARSE HPXML INPUTS
# to create a dictionary of arguments from the HPXML measure.xml file
# and create ../HPXMLArg.py file
################################################################################

# LIBRARIES
import xml.etree.ElementTree as ET
import pandas as pd
import os
import json

PROJECT_DIR = os.getcwd()

def parse_xml_string(xml_string):
	"""
	Parse an XML string and return the root element.
	
	Args:
		xml_string (str): XML content as a string.
	
	Returns:
		Element: Root element of the parsed XML string.
	"""

	arguments = xml_string.findall('.//argument')
	ListDictArgs = []
	for argument in arguments:
		argdict = {}
		if argument.find('name') is not None:
			argdict['Name'] = argument.find('name').text
		if argument.find('display_name') is not None:
			argdict['Display Name'] = argument.find('display_name').text
		if argument.find('description') is not None:
			argdict['Description'] = argument.find('description').text
		if argument.find('type') is not None:
			argdict['Type'] = argument.find('type').text
		if argument.find('units') is not None:
			argdict['Units'] = argument.find('units').text
		if argument.find('default_value') is not None:
			argdict['Default Value'] = argument.find('default_value').text
		if argument.find('choices') is not None:
			choices = argument.find('choices').findall('.//choice')
			listChoices = []
			for choice in choices:
				listChoices.append(choice.find('value').text)
			argdict['Choices'] = listChoices
		if argument.find('required') is not None:
			argdict['Required'] = argument.find('required').text
		ListDictArgs.append(argdict)
	return ListDictArgs
# PARSE XML FILE FUNCTION
def parse_xml_file(file_path):
	"""
	Parse the XML file and return the root element.
	
	Args:
		file_path (str): Path to the XML file.
	
	Returns:
		Element: Root element of the parsed XML file.
	"""
	try:
		tree = ET.parse(file_path)
		root = tree.getroot()
		return parse_xml_string(root)
	
	except ET.ParseError as e:
		print(f"Error parsing XML file: {e}")
		return None
# PARSE XML FILE

def print_argument_fromfile(file_path):
	ListDictArgs = parse_xml_file(file_path)
	print("")
	print("arguments = {")
	for i in ListDictArgs:
		name = i['Name']
		print(json.dumps(name) + " : " + json.dumps(i,indent=4)+",")

	print("}")

def save_argument_fromfile(file_path, output_file):
	ListDictArgs = parse_xml_file(file_path)
	with open(output_file, 'w') as f:
		f.write("class HPXMLArguments:\n")
		f.write("    ")
		f.write("arguments = {\n")
		for i in ListDictArgs:
			name = i['Name']
			f.write("        "+ json.dumps(name) + " : {\n")
			for k,v in i.items():
				f.write("            " + json.dumps(k) +" : "+ json.dumps(v)+",\n")
			f.write("        " + "},\n")
		f.write("    }\n")

if __name__ == "__main__":
	save_argument_fromfile(PROJECT_DIR+"/data/hpxml/measure.xml", PROJECT_DIR+"/src/utils/hpxml/HPXMLArg.py")

