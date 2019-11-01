from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import subprocess
import os
import re
import json
import string
import math
import sys

filename = sys.argv[1]
#filename = "9610131"
#"0302007"
#"0303124"
#"0304011"
#"9602063"
#"1605.02019"
#"9610131"

#To be expanded
XML_LATEX_SIZE_REDUCTION = [
	["\\end{array}\\right)", ")"],
	["(\\begin{array}[]", ""],
	["\\{", "("],
	["\\}", ")"],
	["\\;", ""],
	["\\,", ""],
	["}~", ""],
	["{",""],
	["}", ""],
	["^",""],
	["_",""],
	["\\mathbb", ""],
	["\\mathcal", ""],
	["\\displaystyle=",""],
	["\\displaystyle",""],
	["\\overleftarrow", "."],
	["\\longleftarrow", "."],
	["\\overrightarrow", "."],
	["\\longrightarrow", "."],
	["\\longdownarrow", "d"],
	["\\rightarrow", "r"],
	["\\leftarrow", "l"],
	["\\downarrow", "d"],
	["\\varepsilon", "e"],
	["\\textstyle", ""],
	["\\phantom", ""],
	["\\widetilde", "."],
	["\\stackrel", ""],
	["\\pmatrix", ""],
	["\\overset", ""],
	["\\buildrel", "-"],
	["\\mathop", ""],
	["\\over", ""],
	["\\Omega", "."],
	["\\omega", "."],
	["\\cdot", "."],
	["\\Sigma", "s"],
	["\\sigma", "s"],
	["\\Lambda", "l"],
	["\\lambda", "l"],
	["\\alpha", "a"],
	["\\beta", "b"],
	["\\qquad", ""],
	["\\Beta", "b"],
	["\\delta", "d"],
	["\\Delta", "d"],
	["\\prime", "p"],
	["\\quad", ""],
	["\\otimes", "."],
	["\\times", "."],
	["\\Gamma", "g"],
	["\\sum\\limits", "s"],
	["\\gamma", "g"],
	["\\theta", "."],
	["\\epsilon", "e"],
	["\\infty", "i"],
	["\\sqrt", "s"],
	["~\\phi", "p"],
	["~\\Phi", "p"],
	["\\phi", "p"],
	["\\Phi", "p"],
	["\\sim", "s"],
	["\\Sim", "s"],
	["\\int", "i"],
	["\\left[", "["],
	["\\right]", "]"],
	["\\left\\{", "{"],
	["\\right\\}", "{"],
	["\\left(", "("],
	["\\right)", ")"],
	["\\right.", ""],
	["\\left.", ""],
	["\\left", "("],
	["\\equiv", "v"],
	["\\prod", "."],
	["\\nabla", "a"],
	["\\right", ")"],
	["\\partial", "p"],
	["\\frac", ""],
	["\\ldots", "..."],
	["\\psi", "p"],
	["~\\bar", "b"],
	["\\bar", "b"],
	["\\ast", "."],
	["\\dot", "."],
	["\\leq","l"],
	["\\cal", ""],
	["\\geq","g"],
	["\\in","e"],
	["\\mu", "m"],
	["\\nu", "n"],
	["\\rho", "n"],
	["\\sum", "s"],
	["~\\chi", "c"],
	["\\chi", "c",],
	["\\rm", ""],
	["\\ne", "n="],
	["\\bf", ""],
	["\\to", "."],
	["\\hbox", ""],
	["\\Hbox", ""],
	["\\mbox", ""],
	["\\Mbox", ""],
	["\\Box", "b"],
	["\\not", "n"],
	["\\pm", "."],
	["\\eta~", "n"],
	["\\eta", "n"],
	["\\cr", ""],
	["~e", "e"],
	["~&gt;", "&"],
	["~&lt;", "&"],
	["~&gt","g"],
	["~&lt","l"],
	["&gt;", "g"],
	["&gt","g"],
	["&lt;", "l"],
	["&lt","l"],
	["&quot;", "."],
	["less;", "l"],
	["greater;", "g"],
	["\\pi", "."],
	["\\vec","v"],
	["/","."],
	["%&#10;", ""],
	["&amp;", ""],
	["&#10;", ""],
	["\\!", ""],
	["~\\", ""],
	["\\",""],
	[" ",""],
]

SPECIAL_CHAR_LIST = {
	"\xe2\x80\x9d" : ".",
}

ME_EQUALIZER = [
	["\\end{array}\\right)", ")"],
	["(\\begin{array}[]", ""],
	["\\{", "("],
	["\\}", ")"],
	["\\;", ""],
	["\\,", ""],
	["}~", ""],
	["{", ""],
	["}", ""],
	["^", ""],
	["_", ""],
	["integraldisplay", "i"],
	["summationdisplay", "s"],
	["summationtext", "s"],
	["periodcentered", "d"],
	["displaystyle=", ""],
	["bracketleftbigg", "["],
	["productdisplay", "."],
	["bracketrightbigg", "]"],
	["braceleftbigg", "("],
	["bracerightbigg", ")"],
	["braceleftBigg", "("],
	["bracerightBigg", ")"],
	["braceleftBig", "("],
	["bracerightBig", ")"],
	["parenleftBigg", "("],
	["parenlefttp", "("],
	["parenrighttp", ")"],
	["bracelefttp", "("],
	["bracerighttp", ")"],
	["circlemultiply", "."],
	["wildcard", "*"],
	["parenrightBigg", ")"],
	["parenleftBig", "("],
	["parenrightBig", ")"],
	["\\varepsilon", "e"],
	["asciitilde", "v"],
	["\\sum\\limits", "s"],
	["parenleftbigg", "("],
	["parenrightbigg", ")"],
	["negationslash", "n"],
	["\\longleftarrow", "."],
	["\\longrightarrow", "."],
	["\\overleftarrow", "."],
	["\\overrightarrow", "."],
	["\\longdownarrow", "d"],
	["\\downarrow", "d"],
	["\\rightarrow", "."],
	["\\leftarrow", "."],
	["\\widetilde", "."],
	["\\phantom", ""],
	["partialdiff", "p"],
	["braceleft", "("],
	["braceright", ")"],
	["arrowright", "."],
	["downarrow", "d"],
	["tildewidest", "."],
	["plusminus", "."],
	["equivalence", "v"],
	["arrowleft", "."],
	["similar", "s"],
	["delta", "d"],
	["Delta", "d"],
	["theta", "."],
	["question", "?"],
	["infinity", "i"],
	["epsilon1", "e"],
	["epsilon", "e"],
	["\\textstyle", ""],
	["\\stackrel", ""],
	["\\otimes", "."],
	["\\pmatrix", ""],
	["\\matrix", ""],
	["\\overset", ""],
	["\\buildrel", "-"],
	["\\over", ""],
	["\\qquad", ""],
	["\\quad", ""],
	["\\infty", "i"],
	["\\mathop", ""],
	["\\prod", "."],
	["\\right.", ""],
	["\\left.", ""],
	["\\left(", "("],
	["\\right)", ")"],
	["\\left[", "["],
	["\\right]", "]"],
	["\\right", ")"],
	["\\times", "."],
	["nabla", "a"],
	["\\nabla", "a"],
	["\\sim", "s"],
	["\\Sim", "s"],
	["\\ne", "n="],
	["\\epsilon", "e"],
	["\\equiv", "v"],
	["Omega", "."],
	["omega", "."],
	["endash", "-"],
	["semicolon", ";"],
	["greaterequal", "g"],
	["displaystyle", ""],
	["lessequal", "l"],
	["mathcal", ""],
	["multiply", "."],
	["mathbb", ""],
	["element", "e"],
	["greater", "g"], #DJ &
	["less", "l"], #DJ &
	["vector", "v"],
	["\\dot", "."],
	["/","."],
	["beta", "b"],
	["Sigma", "s"],
	["sigma", "s"],
	["Lambda", "l"],
	["lambda", "l"],
	["alpha", "a"],
	["prime", "p"],
	["Gamma", "g"],
	["gamma", "g"],
	["sqrt", "s"],
	["radical", "s"],
	["cdot", "."],
	["dotaccent", "."],
	["leq","l"],
	["geq","g"],
	["vec","v"],
	["macron", "b"],
	["int", "i"],
	["rho", "n"],
	["\\left", "("],
	["\\partial", "p"],
	["\\in","e"],
	["\\frac", ""],
	["\\ldots", "..."],
	["\\bf", ""],
	["\\to", "."],
	["\\hbox", ""],
	["\\Hbox", ""],
	["\\mbox", ""],
	["\\Mbox", ""],
	["\\Box", "b"],
	["~\\chi", "c"],
	["\\chi", "c",],
	["\\cal", ""],
	["\\sum", "s"],
	["\\not", "n"],
	["~\\bar", "b"],
	["\\bar", "b"],
	["\\ast", "."],
	["\\pm", "."],
	["\\eta~", "n"],
	["\\cr", ""],
	["\\rm", ""],
	["pi", "."],
	["a50", "b"],
	["psi", "p"],
	["mu", "m"],
	["rm", ""],
	["chi", "c"],
	["bar", "|"],
	["phi", "p"],
	["Phi", "p"],
	["Box", "b"],
	["eta", "n"],
	["~&gt;", "g"], #DJ &
	["~&lt;", "l"], #DJ &
	["~&gt","g"],
	["&quot;", "."],
	["~&lt","l"],
	["&gt;", "g"], #DJ &
	["&lt;", "l"], #DJ &
	["&gt","g"],
	["&lt","l"],
	["~e", "e"],
	[" ", ""],
	["%&#10;", ""],
	["&amp;", ""],
	["&#10;", ""],
	["\\!", ""],
	["~\\", ""],
	["\\", ""],
]

class ME():
	char_bbox_list = {} #bbox for ME chars
	char_big_bbox_list = {}
	pdf_string = {} #PDF string of data -- like xml but with ME
	pdf_string_reduced = {}
	pdf_char_count = {}
	pdf_char_list = {} #PDF string in array form
	pdf_spec_list = {}
	pdf_xspace_stats = []
	pdf_yspace_stats = []
	pdf_euclidean_2d_stats = []
	avg_chars_perline = 0

	me_refnum_set = {}
	me_fragmented_box_set = {}
	me_fragmented_map = {}
	me_index_list = {}
	me_list = []
	is_IME_set = {}
	is_fragment_set = {}
	me_size_list = {}
	me_reduced_list = {}
	xml_text = ""
	xml_page_text = {}
	page_with_me = {}
	find_count = 0

	ME_PDF_EXACT = {}
	ME_SPECS = {}

	me_fail_list = {}
	page_fail_list = {}

	post_page = {}
	prev_page = {}

	possible_refnum_jump = {}

	pages = 0
	max_pages = 0
	original_pages = 0
	page_height = 0

	me_bbox_list = {} #bbox for whole ME
	me_is_IME = {}
	me_char_bbox_list = {} #List of char bbox

	#Page datasets
	dataset_pages = []

	#Error occured in split pages, stop at max-1 for locate_me
	max_page = -1


def cross_area(rect1, rect2):
	dx = min(float(rect1[2]), float(rect2[2])) - max(float(rect1[0]), float(rect2[0]))
	dy = min(float(rect1[3]), float(rect2[3])) - max(float(rect1[1]), float(rect2[1]))
	if( dx >= 0 and dy >= 0):
		return dx*dy
	else:
		return 0

def get_area(rect):
    dx = rect[0] - rect[2]
    dy = rect[1] - rect[3]
    return dx*dy

def point_distance(p1, p2):
	d = math.sqrt(pow(p2[0]-p1[0],2)+pow(p2[1]-p1[1],2))
	return d

def load_pdf_metadata():
	metadata = filename + "_data/pdfbox_output/pdf_metadata.txt"
	#print metadata
	with open(metadata) as fn:
		i = 0
		for line in fn:
			if(i==0):
				tmp = line.split(",")
				ME.pages = int(tmp[0])
				ME.max_pages = int(tmp[0])
				ME.original_pages = int(tmp[0])
				ME.page_height = float(tmp[1])
			else:
				data = line.split(",")
				ME.possible_refnum_jump[int(data[0])] = data[1:len(data)]

			i = i + 1
	statdata = filename + "_data/pdfbox_output/pdf_stats.txt"
	with open(statdata) as fn:
		i = 0
		for line in fn:
			tmp = line.split(",")
			if(i == 0):
				ME.pdf_xspace_stats = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
			elif(i == 1):
				ME.pdf_yspace_stats = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
			elif(i == 2):
				ME.pdf_euclidean_2d_stats = [float(tmp[0]), float(tmp[1]), float(tmp[2])]
			elif(i==3):
				ME.avg_chars_perline = math.ceil(float(tmp[0]))
			else:
				break
			i = i + 1
			#print ME.pdf_xspace_stats[float(tmp[0])]
			

	#print("mp", ME.pages)

def get_mined_pdf_data():
	directory = filename + "_data/pdfbox_output/"
	i = 0
	while(i < ME.pages):
		file = directory + filename + "_page_" + str(i) + "_mined.txt"
		char_bbox_list = []
		char_big_bbox_list = []
		pdf_string = ""
		pdf_string_reduced = ""
		pdf_char_list = []
		pdf_spec_list = []
		with open(file) as fn:
			for line in fn:
				#print line
				data = line.split(",")
				if(data[0] == ""):
					data[0] = ","
					bbox = [data[2], data[3], data[4], data[5]]
					pdf_spec_list.append([data[6], data[7], data[8]])
					char_big_bbox_list.append([data[10], data[11], data[12], data[13]])
					if(float(data[2]) < 33):
						#Water mark
						continue
				else:
					bbox = [data[1], data[2], data[3], data[4]]
					pdf_spec_list.append([data[5], data[6], data[7]])
					#print("WHAT", data)
					char_big_bbox_list.append([data[8], data[9], data[10], data[11]])
					if(float(data[1]) < 33):
						#Water mark
						continue
				pdf_char_list.append(data[0])
				
				
				char_bbox_list.append(bbox)
				tmp_data = data[0]
				for rule in ME_EQUALIZER:
					if(tmp_data == rule[0]):				
						tmp_data = tmp_data.replace(rule[0], rule[1])
						break
				pdf_string_reduced = pdf_string_reduced + tmp_data

				pdf_string = pdf_string + data[0]
		ME.char_bbox_list[i] = char_bbox_list
		ME.pdf_string[i] = pdf_string
		ME.pdf_string_reduced[i] = pdf_string_reduced
		ME.pdf_char_list[i] = pdf_char_list
		ME.pdf_char_count[i] = len(ME.pdf_char_list[i])
		ME.pdf_spec_list[i] = pdf_spec_list
		ME.char_big_bbox_list[i] = char_big_bbox_list
		i = i + 1

def get_mined_xml_data():
	with open(filename + "_data/" + filename + "_melist.txt") as fn:
		i = 0
		for line in fn:
			line = line.rstrip()
			line = line.replace("\n", "")
			ME.me_list.append(line)
			i = i + 1

	with open(filename + "_data/" + filename + "_xmlmined.txt") as fn:
		for line in fn:
			ME.xml_text = ME.xml_text + line

	#me_refnum_set
	with open(filename + "_data/" + filename + "_merefnumlist.txt") as fn:
		for line in fn:
			line = line.split(",")
			ME.me_refnum_set[line[1].rstrip()] = line[0]
	#print("AIDS", ME.me_refnum_set)

def refactor_xml_me_text():
	tmp = ME.xml_text.split("[ME#]")
	i = 0
	xml_data = ""
	for line in tmp:
		if(i == len(tmp)-1):
			xml_data = xml_data + line
			break
		me_copy = ""
		j = 0
		'''me_reduced = ME.me_list[i]
		print("ME", ME.me_list[i])
		for rule in XML_LATEX_SIZE_REDUCTION:
			if(rule[0] == "(\\begin{array}[]"):
				#Search for cc {}
				if("(\\begin{array}[]" in me_reduced):
					p = re.compile("\{(c+)\}")
					for i in p.findall(me_reduced):
						me_reduced = me_reduced.replace("{" + i + "}", "")
			me_reduced = me_reduced.replace(rule[0], rule[1])
		print me_reduced'''
		while(j < ME.me_size_list[ME.me_list[i]]):
			me_copy = me_copy + "."
			j = j + 1
		#print("line", line)
		#print("\n")
		xml_data = xml_data + line + me_copy
		i = i + 1

	return xml_data


def splt_xml_data():
	prev_size = 0
	me_index = 0
	tmp_xml_data = refactor_xml_me_text()
	#print tmp_xml_data
	#print("\n\n\n\n\n")
	#print(tmp_xml_data[0:ME.pdf_char_count[0]])
	#print("\n\n\n\n\n")
	#print(tmp_xml_data[ME.pdf_char_count[0]:ME.pdf_char_count[0]+ME.pdf_char_count[1]])
	'''for page in ME.pdf_char_count:
		page_size = ME.pdf_char_count[page]
		print(tmp_xml_data[prev_size:prev_size+page_size])
		print("\n\n\n\n")
		prev_size = prev_size + page_size'''

def split_xml_into_pages_1():
	try:
		page_tlu_list = []
		stop = -1
		for page in ME.pdf_string:
			#Start with string size of 12
			#print ME.pdf_string[page]
			#print(" \n\n -------------------------------------", page)
			tmp = ME.pdf_string[page][0:6]
			if("(" in tmp):
				i = 0
				while(")" not in tmp):
					tmp = ME.pdf_string[page][0:6+i]
					i = i + 1
					if(i > 400):
						break
			possible_locs = [m.start() for m in re.finditer(tmp, ME.xml_text)]
			i = 0
			while(len(possible_locs) > 1):
				tmp = ME.pdf_string[page][0:6+i]
				possible_locs = [m.start() for m in re.finditer(tmp, ME.xml_text)]
				i = i + 1
				if(i > 400):
					break
			if(len(possible_locs) == 1):
				page_tlu_list.append(tmp)

			else:
				page_tlu_list.append("[Ref]")
				ME.xml_page_text[page] = "[Ref]"
				stop = page
		if(stop == -1):
			stop = len(ME.pdf_string)

		i = 0
		
		while(i != stop):
			xml_page_text = ME.xml_text.split(page_tlu_list[i])
			#print(page_tlu_list[i])
			#print("\n\n\n\n\n\n\n\n\n\n\n\n-----------------------------------------------------------")
			xml_page_text = xml_page_text[1].split(page_tlu_list[i+1])
			ME.xml_page_text[i] = page_tlu_list[i] + xml_page_text[0]
			i = i + 1
			if( i > 90000):
				break
	except:
		print("ERROR TRYING TO PARSE PAGES, TRYING METHOD 2")
		result = split_xml_into_pages_2()
		if(result == 1):
			#Retry
			return 0
	return 1


def split_xml_into_pages_2():
	page_tlu_list = []
	stop = -1
	for page in ME.pdf_string:
		try:
			#Start with string size of 12
			#print ME.pdf_string[page]
			#print(" \n start -------------------------------------", page)
			start_pos = 0
			tmp = ME.pdf_string[page][start_pos:6]
			#print("tmp", tmp.lower(), page)

			if("(" in tmp):
				i = 0
				while(")" not in tmp):
					tmp = ME.pdf_string[page][start_pos:6+i]
					i = i + 1
					if(i > 300):
						break
			possible_locs = [m.start() for m in re.finditer(tmp.lower(), ME.xml_text.lower())]
			i = 0
			error_flag = 0
			if(len(possible_locs) == 0):
				tmp = tmp.replace("(", "\\(")
				tmp = tmp.replace(")", "\\)")
				possible_locs = [m.start() for m in re.finditer(tmp.lower(), ME.xml_text.lower())]

			#print possible_locs
			if(len(possible_locs) == 0):
				#Might be text on pdf that is not in xml or it is an ME
				#Move in-till something that matches comes up
				error_flag = 1
				if(page == 0):
					tmp = ME.xml_text[0:6]
					possible_locs = [m.start() for m in re.finditer(tmp.lower(), ME.xml_text.lower())]
					ME.pdf_string[page] = ME.pdf_string[page].split(tmp)
					k = 1
					new_pdf = tmp
					while(k < len(ME.pdf_string[page])):
						new_pdf = new_pdf + ME.pdf_string[page][k]
						k = k + 1
					ME.pdf_string[page] = new_pdf
				elif(page != len(ME.pdf_string)-1):
					#Try to recover page location, stop after 12 trys
					
					k = 1
					tmp_tmp = tmp
					tmp_tmp = tmp_tmp.replace("(", "\\(")
					tmp_tmp = tmp_tmp.replace(")", "\\)")
					#print("???", tmp_tmp)
					#print("HERE", tmp.lower(), [m.start() for m in re.finditer(tmp_tmp, ME.xml_text.lower())])
					
					while(len(possible_locs) == 0 and k < 30):
						tmp = ME.pdf_string[page][k:6+i]
						#print tmp
						#print("OI", tmp)
						if("(" in tmp):
							while(")" not in tmp):
								tmp = ME.pdf_string[page][k:6+i]
								k = k + 1
								i = i + 1
								if(i > 300):
									break
						possible_locs = [m.start() for m in re.finditer(tmp.lower(), ME.xml_text.lower())]
						#print possible_locs
						#print("OI2", possible_locs)
						start_pos = k
						k = k + 1
						i = i + 1

			while(len(possible_locs) > 1):
				tmp = ME.pdf_string[page][start_pos:6+i]
				possible_locs = [m.start() for m in re.finditer(tmp.lower(), ME.xml_text.lower())]
				i = i + 1
				if(i > 300):
					break
			#print tmp
			
			#print("ME.xml", ME.xml_text.lower())
			if(len(possible_locs) == 1):
				print("one match", page, tmp)
				page_tlu_list.append(tmp)
			else:
				print("WTF", tmp)
				if(page == len(ME.pdf_string)-1):
					page_tlu_list.append("[Ref]")
					ME.xml_page_text[page] = "[Ref]"
					stop = page
				else:
					#needs a better fix in future...
					#print("HERE_SPLIT", page)
					new_tmp = ""
					if(ME.pdf_string[page-1][-1] == str(page-1)):
						#Page num that is not in xml possibly

						#print("text", ME.pdf_string[page-1][-7:-1])
						new_tmp = ME.pdf_string[page-1][-7:-1]
						j = 1
						if("(" in new_tmp):
							while(")" not in new_tmp):
								new_tmp = ME.pdf_string[page-1][-7-j:-1]
								j = j + 1
								if(j > 300):
									break
						elif(")" in new_tmp):
							while("(" not in new_tmp):
								new_tmp = ME.pdf_string[page-1][-7-j:-1]
								j = j + 1		
								if(j > 300):
									break					
					else:
						#print("text", ME.pdf_string[page-1][-7:])
						new_tmp = ME.pdf_string[page-1][-7:]
						j = 1
						if("(" in new_tmp):
							while(")" not in new_tmp):
								new_tmp = ME.pdf_string[page-1][-7-j:]
								j = j + 1
								if(j > 300):
									break
						elif(")" in new_tmp):
							while("(" not in new_tmp):
								new_tmp = ME.pdf_string[page-1][-7-j:]
								j = j + 1	
								if(j > 300):
									break
					new_tmp = new_tmp.replace(")", "\\)")
					new_tmp = new_tmp.replace("(", "\\(")
					page_tlu_list.append(new_tmp + "\[ME\#\]")
		except:
			print("LATEX XML IS NOT THE SAME AS PDF, UPLOAD CORRECT VERSION")
			ME.max_page = page-3 
			return 1
			break
	if(stop == -1):
		stop = len(ME.pdf_string)

	i = 0
	#print("WHAT", page_tlu_list)
	reduced_xml_text = ME.xml_text
	try:
		while(i < len(ME.pdf_string)):
			#print("wtf", i, page_tlu_list[i])
			if(i == len(ME.pdf_string)-1):
				xml_page_text = re.split(page_tlu_list[i], reduced_xml_text, flags=re.IGNORECASE)
				xml_page_text = page_tlu_list[i] + xml_page_text[1]
			else:
				#print("wtf", i, page_tlu_list[i])
				#flags=re.IGNORECASE
				#xml_page_text = ME.xml_text.split(page_tlu_list[i])
				xml_page_text = re.split(page_tlu_list[i], reduced_xml_text, flags=re.IGNORECASE)
				#xml_page_text = xml_page_text[1].split(page_tlu_list[i+1]
				#print(page_tlu_list)
				#print(xml_page_text)
				xml_page_text = re.split(page_tlu_list[i+1], xml_page_text[1], flags=re.IGNORECASE)
				start_text = page_tlu_list[i].replace("\[ME\#\]", "[ME#]")
				start_text = start_text.replace("\\(", "(")
				start_text = start_text.replace("\\)", ")")
				ME.xml_page_text[i] = start_text + xml_page_text[0]
				#reduced_xml_text = ME.xml_text.split(ME.xml_page_text[i])
				#print("OI", ME.xml_page_text[i])
				#print(page_tlu_list[i], i)
				#print("asdf", ME.xml_page_text[i])
				#print("\n\n\n\n\n\n\n\n\n\n\n\n-----------------------------------------------------------")
			i = i + 1
	except:
		#print("XML AND PDF DATA IS TO DISIMILAR, STARTING OVER FROM THE LAST SUCCESSFULL PAGES")
		ME.pages = i-1
		return 0

	return 1

def locate_page_me_sets():
	i = 0
	prev_count = 0
	for page in ME.xml_page_text:
		text = ME.xml_page_text[page]
		total_me_count = [m.start() for m in re.finditer("\[ME#\]", text)]
		if(len(total_me_count) > 0):
			me_list = []
			while(i < (len(total_me_count)+prev_count)):
				if(i > len(ME.me_list)-1):
					break
				me_list.append(ME.me_list[i])
				i = i + 1
			prev_count = i
			ME.page_with_me[page] = me_list

def get_prev_post_me_text():
	i = 0
	for page in ME.page_with_me:
		#Split all [me#] in text
		split_me_text = ME.xml_page_text[page].split("[ME#]")

		#print page
		j = 0
		tmp_prev_text = []
		tmp_post_text = []

		while(j < (len(split_me_text)-1)):
			tmp_prev_text.append(split_me_text[j])
			tmp_post_text.append(split_me_text[j+1])
			i = i + 1
			j = j + 1

		ME.prev_page[page] = tmp_prev_text
		ME.post_page[page] = tmp_post_text
		
	for page in ME.page_with_me:
		me_set = ME.page_with_me[page]
		prev_index = 0
		for me in me_set:
			prev_text = ME.prev_page[page][prev_index]
			#search for smallest prev text in xml--might need to be changed to pdf string---
			i = 1
			match_flag = 0
			smallest_unique_substring = prev_text[-i:]
			#Check all other prev text in ME for matching substring
			while(match_flag == 0 and len(smallest_unique_substring) < len(prev_text)):
				match_count = 0
				k = 0
				for tmp_me in me_set:
					if(k == prev_index):
						#Skip current me
						k = k + 1
						continue
					if(smallest_unique_substring == ME.prev_page[page][k][-i:]):
						match_count = match_count + 1
						break
					k = k + 1
				if(match_count == 0):
					#print("match found")
					match_flag = 1
					#print ("sus", smallest_unique_substring)
					if(len(smallest_unique_substring) < len(prev_text)-2):
						smallest_unique_substring = prev_text[-(i+2):]
					ME.prev_page[page][prev_index] = smallest_unique_substring
				else:
					i = i + 1
					smallest_unique_substring = prev_text[-i:]	
			prev_index = prev_index + 1
	
	for page in ME.page_with_me:
		me_set = ME.page_with_me[page]
		post_index = 0
		for me in me_set:
			post_text = ME.post_page[page][post_index]
			#search for smallest post text in xml--might need to be changed to pdf string---
			i = 1
			match_flag = 0
			smallest_unique_substring = post_text[0:i]
			#Check all other post text in ME for matching substring
			while(match_flag == 0 and len(smallest_unique_substring) < len(post_text)):
				match_count = 0
				k = 0
				for tmp_me in me_set:
					if(k == post_index):
						#Skip current me
						k = k + 1
						continue
					if(smallest_unique_substring == ME.post_page[page][k][0:i]):
						match_count = match_count + 1
						break
					k = k + 1
				if(match_count == 0):
					match_flag = 1
					if(len(smallest_unique_substring) < len(post_text)-1):
						smallest_unique_substring = post_text[0:i+2]
					ME.post_page[page][post_index] = smallest_unique_substring
				else:
					i = i + 1
					smallest_unique_substring = post_text[0:i]
			post_index = post_index + 1

def calc_me_xml_size():
	for me in ME.me_list:
		me_reduced = me
		for rule in XML_LATEX_SIZE_REDUCTION:
			if(rule[0] == "(\\begin{array}[]"):
				#Search for cc {}
				if("(\\begin{array}[]" in me_reduced):
					p = re.compile("\{(c+)\}")
					for i in p.findall(me_reduced):
						me_reduced = me_reduced.replace("{" + i + "}", "")
			me_reduced = me_reduced.replace(rule[0], rule[1])
		ME.me_size_list[me] = len(me_reduced)
		ME.me_reduced_list[me] = me_reduced

def unorder_check(me):
	if(re.search("(_\{.*?\}\^\{.*?\})", me)):
		return 1
	else:
		return 0

def buildrel_check(me):
	if(re.search("buildrel", me)):
		return 1
	else:
		return 0

def me_substring_matching(xml_me, pdf_me, offset_count, mr_extra):
	pdf_me_string = ""
	miss_ratio = 0 #0 for exact matching
	invalid_chars = set(string.punctuation)
	for char in pdf_me:
		if(char in SPECIAL_CHAR_LIST):
			char = "*"
		pdf_me_string = pdf_me_string + char
	pdf_me = pdf_me_string
	if(unorder_check(xml_me) == 1):
		p = re.compile("(_\{.*?\}\^\{.*?\})")
		xml_me = xml_me.replace("%&#10;", "")
		xml_me = xml_me.replace("&amp;", "")
		xml_me = xml_me.replace("&#10;", "")
		print xml_me
		for i in p.findall(xml_me):
			print "WTF := " + str(i)
			matched_case = i[i.rindex('_'):]
			matched_case = matched_case.split("^")
			#print matched_case
			if(len(matched_case)<2):

				miss_ratio = miss_ratio + len(i)
			else:
				case0 = matched_case[0]
				case1 = matched_case[1]
				case0 = case0.replace("_{", "")
				case0 = case0.replace("}", "")
				case1 = case1.replace("{", "")
				case1 = case1.replace("}", "")
				case0 = case0.replace("{", "")
				case1 = case1.replace("{", "")
				case0 = case0.replace("}", "")
				case1 = case1.replace("}", "")
				print("miss ratio i " + str(case0) + " " + str(case1))
				miss_ratio = miss_ratio + len(case0) + len(case1)
			#print("miss ratio", miss_ratio)
			#print("case ", i[i.rindex('_'):])
	if(buildrel_check(xml_me) == 1):
		print "BUILDREL CHECK"
		p = re.compile("buildrel")
		xml_me = xml_me.replace("%&#10;", "")
		xml_me = xml_me.replace("&amp;", "")
		xml_me = xml_me.replace("&#10;", "")
		for i in p.findall(xml_me):
			miss_ratio = miss_ratio + 1

	
	for rule in ME_EQUALIZER:
		#Check to see if xml has _^ in latex, the order is reversed in PDFBOX
		if(rule[0] == "(\\begin{array}[]"):
			if("(\\begin{array}[]" in xml_me):
				p = re.compile("\{(c+)\}")
				for i in p.findall(xml_me):
					xml_me = xml_me.replace("{" + i + "}", "")
		xml_me = xml_me.replace(rule[0], rule[1])
		pdf_me = pdf_me.replace(rule[0], rule[1])

	#Match ME's
	i = 0
	#if(len(xml_me) > 6):
	#	miss_ratio = miss_ratio + 2
	print("xml_me", xml_me, len(xml_me))
	print("pdf_me", pdf_me, len(pdf_me))

	if(mr_extra):
		miss_ratio = miss_ratio + len(xml_me)

	matched_count = 0
	if(len(xml_me)+offset_count != len(pdf_me)):
		return 0
	for char in xml_me:
		if(pdf_me[i] == "*"):
			#wild card
			matched_count = matched_count + 1
		elif(char == pdf_me[i]):
			matched_count = matched_count + 1
		i = i + 1

	missed_count = len(xml_me) - matched_count 

	print("missed count", missed_count)
	print("missed ratio", miss_ratio)
	if(missed_count == 0):
		return 1
	elif(missed_count <= miss_ratio):
		return 1
	else:
		print "Failed" + " " + xml_me
		return 0

def refnum_check(start, end, page):
	if(page not in ME.possible_refnum_jump):
		return False
	refnum_list = ME.possible_refnum_jump[page]
	for refnum in refnum_list:
		if(int(refnum) >= start and int(refnum) <= end):
			return True
	return False

def reduce_single_me(me):
	me_reduced = me
	for rule in XML_LATEX_SIZE_REDUCTION:
		if(rule[0] == "(\\begin{array}[]"):
			#Search for cc {}
			if("(\\begin{array}[]" in me_reduced):
				p = re.compile("\{(c+)\}")
				for i in p.findall(me_reduced):
					me_reduced = me_reduced.replace("{" + i + "}", "")
		me_reduced = me_reduced.replace(rule[0], rule[1])
	return me_reduced

def locate_me_in_pdf():
	#Needs to be from the pdf_char_list because of special chars
	me_total_index = 0
	for page in ME.page_with_me:
		print("page num", page)
		me_set = ME.page_with_me[page]
		me_box_set = []
		is_IME_set = []
		char_bbox_set = []
		me_pdf_set = []
		me_fail_set = []
		me_index_set = []
		me_index = 0
		me_page_max = len(me_set)
		me_found_count = 0
		for me in me_set:
			found = 0
			#print("\nme", me, ME.me_size_list[me])
			me_reduced = me
			for rule in XML_LATEX_SIZE_REDUCTION:
				if(rule[0] == "(\\begin{array}[]"):
					#Search for cc {}
					if("(\\begin{array}[]" in me_reduced):
						p = re.compile("\{(c+)\}")
						for i in p.findall(me_reduced):
							me_reduced = me_reduced.replace("{" + i + "}", "")
				me_reduced = me_reduced.replace(rule[0], rule[1])
				#print("CURR ME REDUCED", me_reduced)
				#print("\n")
				#print("rules", rule[0], rule[1])
				#print("me_reduced", me_reduced)
			#print("MY ME", me_reduced)
			#print("prev text", ME.prev_page[page][me_index])
			#print("post text", ME.post_page[page][me_index])

			i = 0
			result = 0

			for char in ME.pdf_char_list[page]:	
				#print(''.join(ME.pdf_char_list[page][i:i+len(ME.prev_page[page][me_index])]))
				if(''.join(ME.pdf_char_list[page][i:i+len(ME.prev_page[page][me_index])]) == ME.prev_page[page][me_index]):
					post_start = len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]
					post_end = len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]+len(ME.post_page[page][me_index])
					print("prev check passed", page, me)

					'''print("WTF", ''.join(ME.pdf_char_list[page][post_start-23:post_end+38]))
					print("WTF", (ME.pdf_char_list[page][post_start-23:post_end+38]))
					print("post text", ME.post_page[page][me_index])
					print("prev text", ME.prev_page[page][me_index])
					print("curr prev text", ''.join(ME.pdf_char_list[page][post_start:post_end]))
					#('\nme', '(j,i)')
					print("me size", ME.me_size_list[me])
					#print("prev size", len(ME.prev_page[page][me_index]))
					print("whole text", (ME.pdf_char_list[page][i:post_end]))
					print("CRY", ''.join(ME.pdf_char_list[page][post_start:post_end]))'''

					#Sometimes the latex is missing something... FFS so check to see if it is correct but slightly off

					if(''.join(ME.pdf_char_list[page][post_start:post_end]) == ME.post_page[page][me_index]):
						print("post check passed", me)
						index_list = [len(ME.prev_page[page][me_index])+i, len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]]
						found = found + 1
						result = me_substring_matching(me, ME.pdf_char_list[page][len(ME.prev_page[page][me_index])+i:post_end-len(ME.post_page[page][me_index])], 0, 0)
						if(result == 1):
							print("FOUND ME", me)
							me_found_count = me_found_count + 1
							#print("post text", ME.post_page[page][me_index])
							#print("whole text", (ME.pdf_char_list[page][i:post_end]))
							try:	
								bbox, char_bbox, is_IME = exact_me_box(index_list, me, page, me_total_index, me_index)

								print bbox
								me_index_set.append(index_list)
								is_IME_set.append(is_IME)
								me_box_set.append(bbox)
								char_bbox_set.append(char_bbox)
								me_pdf_start = i+len(ME.prev_page[page][me_index])
								me_pdf_end = len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]
								tmp_pdf_set = []
								while(me_pdf_start <= me_pdf_end):
									tmp_pdf_set.append([ME.pdf_spec_list[page][me_pdf_start][0], ME.pdf_spec_list[page][me_pdf_start][1], ME.pdf_spec_list[page][me_pdf_start][2], ME.pdf_char_list[page][me_pdf_start]] )
									me_pdf_start = me_pdf_start + 1	
								me_pdf_set.append(tmp_pdf_set)
								ME.find_count = ME.find_count + 1
								'''if(is_IME == 1):
									print("FOUND ME %s ----- is_ime", me)
									print("\n------------------------------------------------------------")'''
								break
							except:
								result = 0
						else:
							result = 0
							'''print("ME fail", me , page)
							print("prev check passed", page)
							print("WTF", ''.join(ME.pdf_char_list[page][post_start:post_end]))
							print("post text", ME.post_page[page][me_index])
							print("prev text", ME.prev_page[page][me_index])
							#('\nme', '(j,i)')
							print("me size", ME.me_size_list[me])
							print("prev size", len(ME.prev_page[page][me_index]))
							print("whole text", (ME.pdf_char_list[page][i:post_end]))
							print("\n------------------------------------------------------------")'''

						'''else:
							print("FAILED")
							print("me", me)
							print("prev", ME.prev_page[page][me_index])
							print("post", ME.post_page[page][me_index])
							print("\n\n")'''
					'''elif(refnum_check(i+len(ME.prev_page[page][me_index]), post_end-len(ME.post_page[page][me_index]), page)):
						print("TRUE")
						if(''.join(ME.pdf_char_list[page][post_start:post_end])!= ''):
							#find first char to match
							partial_post_match = ""
							
							curr_refnum = ""
							for char in ME.post_page[page][me_index]:
								curr_refnum = curr_refnum + char
								if(char == ")"):
									break
							print curr_refnum
							skipped_post_data = ME.post_page[page][me_index].split(curr_refnum)
							new_post_start = len(ME.prev_page[page][me_index])+i+ME.me_size_list[me] + len(curr_refnum)
							#new_post_end = len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]+len(new_post)
							print("old end", ''.join(ME.pdf_char_list[page][post_start:post_end]))
							print("curr end", ''.join(ME.pdf_char_list[page][new_post_start:post_end]))
							print("post text", skipped_post_data[1])

							if(''.join(ME.pdf_char_list[page][new_post_start:post_end]) == skipped_post_data[1]):
								print("post check passed")
								index_list = [len(ME.prev_page[page][me_index])+i, len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]]
								found = found + 1
								result = me_substring_matching(me, ME.pdf_char_list[page][len(ME.prev_page[page][me_index])+i:post_end-len(ME.post_page[page][me_index])], 0, 1)
								if(result == 1):
									print("FOUND ME", me)
									#print("post text", ME.post_page[page][me_index])
									#print("whole text", (ME.pdf_char_list[page][i:post_end]))
									#
									bbox = exact_me_box(index_list, me, page)
									me_box_set.append(bbox)
									me_pdf_set.append(ME.pdf_char_list[page][i+len(ME.prev_page[page][me_index]):len(ME.prev_page[page][me_index])+i+ME.me_size_list[me]])
									ME.find_count = ME.find_count + 1
									print("\n------------------------------------------------------------")
									break'''
							
				i = i + 1
			if(result == 0):
				#Check to see if only one occurence is on PDF PAGE -- Last check
				last_me_check = [m.start() for m in re.finditer(re.escape(ME.me_reduced_list[me]), ME.pdf_string_reduced[page])]
				if(len(last_me_check) == 1):
					#RECOVERED ME
					if(last_me_check[0]+ME.me_size_list[me] < len(ME.pdf_char_list[page])-1 and ME.pdf_char_list[page][last_me_check[0]] == ME.me_reduced_list[me][0] ):
						#print("LAST ME CHECK", me)
						#print ME.pdf_string_reduced[page]
						index_list = [last_me_check[0], last_me_check[0]+ME.me_size_list[me]]
						#print("TEXT--", ME.pdf_string_reduced[page][last_me_check[0]:last_me_check[0]+ME.me_size_list[me]])
						bbox, char_bbox, is_IME = exact_me_box(index_list, me, page, me_total_index, me_index)
						#if(is_IME == 1):
						#	print("c2: FOUND ME %s ----- is_ime", me)
						#	print("\n\n-------------------------------------")
						#Check to make sure this is not a smaller ME inside a big ME
						curr_rec = [bbox[0], bbox[1], bbox[2], bbox[3]]
						curr_rec_area = get_area(curr_rec)
						cross_flag = 0
						for box in me_box_set:
							#rec is of the form [min_x, min_y, max_x, max_y]
							if(box == "FAILED"):
								continue
							box_rec = [box[0], box[1], box[2], box[3]]						
							CA = cross_area(box_rec, curr_rec)
							#print("CA", CA)
							#print("ME", me)
							if(CA >= curr_rec_area):
								#print("cross_area == %d for ME %s   check failed compared to %s", CA, me)
								cross_flag = 1
								break
						if(cross_flag == 0):

							me_index_set.append(index_list)
							me_box_set.append(bbox)
							is_IME_set.append(is_IME)
							char_bbox_set.append(char_bbox)
							#print("ME CHAR LIST", ME.pdf_char_list[page][last_me_check[0]:last_me_check[0]+ME.me_size_list[me]])
							me_pdf_start = last_me_check[0]
							me_pdf_end = last_me_check[0]+ME.me_size_list[me]
							tmp_pdf_set = []
							while(me_pdf_start <= me_pdf_end):
								tmp_pdf_set.append([ME.pdf_spec_list[page][me_pdf_start][0], ME.pdf_spec_list[page][me_pdf_start][1], ME.pdf_spec_list[page][me_pdf_start][2], ME.pdf_char_list[page][me_pdf_start]] )
								me_pdf_start = me_pdf_start + 1	
							me_pdf_set.append(tmp_pdf_set)
							ME.find_count = ME.find_count + 1
							me_found_count = me_found_count + 1	
							me_fail_set.append(0)
							#print("LAST ME CHECK DONE")
						else:
							me_fail_set.append(1)
							is_IME_set.append("FAILED")
							me_box_set.append("FAILED")
							char_bbox_set.append("FAILED")
							me_pdf_set.append("FAILED")	
							me_index_set.append("FAILED")						
					else:				
						me_fail_set.append(1)
						is_IME_set.append("FAILED")
						me_box_set.append("FAILED")
						char_bbox_set.append("FAILED")
						me_pdf_set.append("FAILED")
						me_index_set.append("FAILED")
				else:				
					me_fail_set.append(1)
					is_IME_set.append("FAILED")
					me_box_set.append("FAILED")
					char_bbox_set.append("FAILED")
					me_pdf_set.append("FAILED")
					me_index_set.append("FAILED")
			else:
				me_fail_set.append(0)
			me_index = me_index + 1
			me_total_index = me_total_index + 1
		#Place pages based on their ME extraction count into folders
		if(float(me_page_max) > 0):
			me_found_ratio = float(me_found_count)/float(me_page_max)
			current_page = filename + ".pdf_" + str(page+1) + "_page_" + str(ME.max_pages) + ".pdf"
			directory = filename + "_data/"
			print "ME_FOUND_RATIO"
			print (page,ME.max_page)
			print me_found_ratio
			print me_page_max
			print ME.page_with_me[page]
			dataset_metadata = []
			create_dataset = -1
			if(ME.max_page == -1):
				create_dataset = 1
			if(ME.max_page != -1 and page <= ME.max_page):
				create_dataset = 1
			if(create_dataset):
				print "MAX ERROR PAGE CHECK WTF"
				if(me_found_ratio == 1):
					#Place in full_page folder
					print "HERE 1.0"
					#os.system("cp " + directory + current_page + " full_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " full_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("full_page/me_info.txt" , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				elif(me_found_ratio >= 0.95):
					#place in 95_page folder
					#os.system("cp " + directory + current_page + " 95_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " 95_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("95_page/me_info.txt" , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				elif(me_found_ratio >= 0.90):
					#place in 90_page folder
					#os.system("cp " + directory + current_page + " 90_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " 90_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("90_page/me_info.txt"  , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				elif(me_found_ratio >= 0.80):
					#place in 80_page folder
					#os.system("cp " + directory + current_page + " 80_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " 80_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("80_page/me_info.txt"  , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				elif(me_found_ratio >= 0.70):
					#place in 70_page folder
					#os.system("cp " + directory + current_page + " 70_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " 70_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("70_page/me_info.txt" , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				elif(me_found_ratio >= 0.50):
					#place in 70_page folder
					#os.system("cp " + directory + current_page + " 70_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " 50_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("70_page/me_info.txt" , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				elif(me_found_ratio >= 0.25):
					#place in 70_page folder
					#os.system("cp " + directory + current_page + " 70_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " 25_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("70_page/me_info.txt" , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				else:
					#place in failed_page folder
					#os.system("cp " + directory + current_page + " failed_page/" + current_page)
					dataset_metadata.append(me_found_ratio)
					dataset_metadata.append("cp " + directory + current_page + " failed_page/" + current_page)
					dataset_metadata.append(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
					#with open("failed_page/me_info.txt" , "a") as page_metadata:
					#	page_metadata.write(current_page + "," + str(me_found_count) + "," + str(me_page_max) + "," + str(ME.page_height) + "\n")
				ME.dataset_pages.append(dataset_metadata)
		ME.me_fail_list[page] = me_fail_set
		#print "ME BOX SET FOR PAGE " + str(page)
		#print me_box_set
		ME.me_bbox_list[page] = me_box_set
		ME.ME_PDF_EXACT[page] = me_pdf_set
		ME.me_char_bbox_list[page] = char_bbox_set
		ME.is_IME_set[page] = is_IME_set
		ME.me_index_list[page] = me_index_set

def exact_me_box(me_location, me, page, me_total_index, me_index):
	i = me_location[0]
	char_bbox_list = []
	while(i <= me_location[1]-1):
		j = 0
		for char in ME.char_bbox_list[page][i]:
			ME.char_bbox_list[page][i][j] = ME.char_bbox_list[page][i][j].replace(" ", "") 
			j = j + 1

		char_bbox_list.append(ME.char_bbox_list[page][i])

		i = i + 1

	x0 = float(char_bbox_list[0][0])
	y0 = float(char_bbox_list[0][1])
	x1 = float(char_bbox_list[0][2])
	y1 = float(char_bbox_list[0][3])

	me_0 = me_location[0]+1
	me_f = me_location[1]
	i = 1

	#print char_bbox_list
	while(me_0 < me_f):
		if(float(char_bbox_list[i][1]) < y0):
			y0 = float(char_bbox_list[i][1])

		if(float(char_bbox_list[i][3]) > y1):
			y1 = float(char_bbox_list[i][3])

		if(float(char_bbox_list[i][0]) < x0):
			x0 = float(char_bbox_list[i][0])

		if(float(char_bbox_list[i][2]) > x1):
			x1 = float(char_bbox_list[i][2])
		me_0 = me_0 + 1
		i = i + 1

	#check if IME
	#DJFIX
	is_IME = 0
	num_of_points = int(ME.avg_chars_perline)
	if(ME.prev_page[page][me_index] == ''):
		start_loc = me_location[0] - ME.me_size_list[ME.me_list[me_total_index-1]]	
	else:
		start_loc = me_location[0]

	if(ME.post_page[page][me_index] == ''):
		end_loc = me_location[1] + ME.me_size_list[ME.me_list[me_total_index+1]]
	else:	
		#Shift end loc if the next unseperable grouping is a reference number to the ME
		next_char = ME.pdf_char_list[page][me_location[1]]
		if(next_char == "("):
			new_location = me_location[1] 
			while(next_char != ")"):
				next_char = ME.pdf_char_list[page][new_location]
				new_location = new_location + 1
			end_loc = new_location
		else:
			end_loc = me_location[1]
	#get complete prev and post xml text with [ME#] locations

	if(str(me_total_index) in ME.me_refnum_set):
		xml_nonme_text = ME.xml_text.split("[ME#]")
		#prev_text_size = len(xml_nonme_text[me_total_index])
		#post_text_size = len(xml_nonme_text[me_total_index+1])
		#Change this to keep going back if multiple mes are infront or behind
		exact_prev = xml_nonme_text[me_total_index]
		exact_post = xml_nonme_text[me_total_index+1]
		size_of_ref = len(ME.me_refnum_set[str(me_total_index)])

		if(str(me_total_index-1) in ME.me_refnum_set):
			if(exact_prev == ME.me_refnum_set[str(me_total_index-1)]):
				start_loc = start_loc - ME.me_size_list[ME.me_list[me_total_index-1]] - size_of_ref
		if(exact_post == ME.me_refnum_set[str(me_total_index)]):
			end_loc = end_loc + ME.me_size_list[ME.me_list[me_total_index]] + len(exact_post)

	
	set_of_prev_squares = ME.char_bbox_list[page][start_loc-(num_of_points):start_loc]
	set_of_post_squares = ME.char_bbox_list[page][end_loc:end_loc+(num_of_points)]
	#Create (x,y) pairs
	prev_point_set = []
	for square in set_of_prev_squares:
		width = float(square[2]) - float(square[0])
		height = float(square[3]) - float(square[1])
		prev_point_set.append([float(square[0]), float(square[3])]) #botleft
		prev_point_set.append([float(square[2]), float(square[3])]) #botright
	post_point_set = []
	for square in set_of_post_squares:
		width = float(square[2]) - float(square[0])
		height = float(square[3]) - float(square[1])
		post_point_set.append([float(square[0]), float(square[1])]) #topleft
		post_point_set.append([float(square[2]), float(square[1])]) #topright

	isolation_radius = ME.pdf_euclidean_2d_stats[0] + ME.pdf_euclidean_2d_stats[0]

	topleft_circle = [x0, y1]
	botleft_circle = [x0, y0]
	topright_circle = [x1, y1]
	botright_circle = [x1, y0]

	nip_prev = 0
	nip_post = 0
	for point in prev_point_set:
		if(point_distance(point, topleft_circle) <= isolation_radius):
			nip_prev = nip_prev + 1
		if(point_distance(point, topright_circle) <= isolation_radius):
			nip_prev = nip_prev + 1
	#print("\n\n-----------------------------------------------------------")
	for point in post_point_set:
		if(point_distance(point, botleft_circle) <= isolation_radius):
			nip_post = nip_post + 1
		if(point_distance(point, botright_circle) <= isolation_radius):
			nip_post = nip_post + 1

	if(nip_prev == 0 and nip_post == 0):
		is_IME = 1

	'''if(is_IME == 0 and page == 5):
		print("ME", me)
		print nip_prev
		print nip_post
		print ME.post_page[page][me_index]
		print ME.prev_page[page][me_index+1]
		print("\n\n---------------------\n\n")'''
	return ([x0,y0,x1,y1], char_bbox_list, is_IME)


def draw_me_box():
	#print("DRAW ME BOX", ME.pages)
	for page in ME.me_bbox_list:
		#print("page", page)
		packet = StringIO.StringIO()
		can = canvas.Canvas(packet, pagesize=letter)
		count = 0
		#print ME.me_bbox_list[page]
		for box in ME.me_bbox_list[page]:
			if(box == "FAILED"):
				count = count + 1
				continue

			#print("BOX", box, page)
			#print("WTF", ME.is_fragment_set[page], page, count)
			if(ME.is_fragment_set[page][count] == 1):
				#draw fragmneted boxes
				new_boxes = ME.me_fragmented_box_set[page]
				#rgb(0,128,0) green
				#print("-____-")
				#print box
				for subbox in new_boxes:
					#print subbox
					x0 = float(subbox[0])
					y0 = abs(ME.page_height - float(subbox[1]))
					x1 = float(subbox[2])
					y1 = abs(ME.page_height - float(subbox[3]))
					height = abs(y0-y1)
					width = abs(x0-x1)
					can.setStrokeColorRGB(0,128,0)
					can.rect(x0,y0-height,width,height, fill = 0, stroke=1)
				count = count + 1
				continue
				
			is_IME = ME.is_IME_set[page][count]
			#print("box data", box)
			x0 = float(box[0])
			y0 = abs(ME.page_height - float(box[1]))
			x1 = float(box[2])
			y1 = abs(ME.page_height - float(box[3]))
			if(is_IME == 1):
				#Purple
				can.setStrokeColorRGB(128,0,128)
			else:
				#yellow
				can.setStrokeColorRGB(255,255,0)
			height = abs(y0-y1)
			width = abs(x0-x1)

			can.rect(x0,y0-height,width,height, fill = 0, stroke=1)
			count = count + 1			
		#print page
		try:
			pdf_page = filename + "_data/" + filename + ".pdf_" + str(page+1) + "_page_"+ str(ME.original_pages) + ".pdf"
			#print pdf_page
			can.save()
			packet.seek(0)
			new_pdf = PdfFileReader(packet)
			existing_pdf = PdfFileReader(pdf_page)
			output = PdfFileWriter()
			page = existing_pdf.getPage(0)
			page.mergePage(new_pdf.getPage(0))
			output.addPage(page)
			outputStream = file(pdf_page + "_destination.pdf", "wb")
			output.write(outputStream)
			outputStream.close()
		except:
			print("INCCORECT LATEX XML FILE ")

		#box = [119.280036, 239.236407, 203.672582, 251.367046]
		#print("\n------------------------")

def merge_pdf():
	merger = PdfFileMerger()
	i = 0
	#1605.02019.pdf_1_page_8
	#1605.02019.pdf_2_page_8.pdf_destination
	while(i < ME.pages):
		if(i not in ME.page_with_me):
			dest_file = filename + "_data/" + filename + ".pdf_" + str(i+1) + "_page_" + str(ME.original_pages) + ".pdf"
		else:
			dest_file = filename + "_data/" + filename + ".pdf_" + str(i+1) + "_page_" + str(ME.original_pages) + ".pdf_destination.pdf"
		try:
			merger.append(PdfFileReader(file(dest_file, 'rb')))
		except:
			dest_file = filename + "_data/" + filename + ".pdf_" + str(i+1) + "_page_" + str(ME.original_pages) + ".pdf"
			merger.append(PdfFileReader(file(dest_file, 'rb')))
		i = i + 1
	merger.write(filename + "_data/final_"+ filename + ".pdf")
		
def me_fragmented_boxes(me_index_set, i, page):
	#isolation threshold radius to determine iregular spaceing
	isolation_radius = ME.pdf_euclidean_2d_stats[0] + ME.pdf_euclidean_2d_stats[0]
	new_me_boxes = []
	me_0 = me_index_set[i][0]
	me_f = me_index_set[i][1]
	#print me_0
	#print me_f
	x0 = float(ME.char_bbox_list[page][me_0][0])
	y0 = float(ME.char_bbox_list[page][me_0][1])
	x1 = float(ME.char_bbox_list[page][me_0][2])
	y1 = float(ME.char_bbox_list[page][me_0][3])
	prev_right_cord = [x1, y0]
	me_0 = me_0 + 1 #Skip first char, already have values to compare
	while(me_0 < me_f):
		curr_left_cord = [float(ME.char_bbox_list[page][me_0][0]), float(ME.char_bbox_list[page][me_0][1])]
		#print curr_left_cord[0]
		#print prev_right_cord[0]
		if(point_distance(curr_left_cord, prev_right_cord) >= isolation_radius):
			#ME BREAK -- start new box
			new_me_boxes.append([x0, y0, x1, y1])
			x0 = float(ME.char_bbox_list[page][me_0][0])
			y0 = float(ME.char_bbox_list[page][me_0][1])
			x1 = float(ME.char_bbox_list[page][me_0][2])
			y1 = float(ME.char_bbox_list[page][me_0][3])
			prev_right_cord = [float(ME.char_bbox_list[page][me_0][2]), float(ME.char_bbox_list[page][me_0][1])]
			me_0 = me_0 + 1
			continue
		if(float(ME.char_bbox_list[page][me_0][1]) < y0):
			y0 = float(ME.char_bbox_list[page][me_0][1])

		if(float(ME.char_bbox_list[page][me_0][3]) > y1):
			y1 = float(ME.char_bbox_list[page][me_0][3])

		if(float(ME.char_bbox_list[page][me_0][0]) < x0):
			x0 = float(ME.char_bbox_list[page][me_0][0])

		if(float(ME.char_bbox_list[page][me_0][2]) > x1):
			x1 = float(ME.char_bbox_list[page][me_0][2])
		prev_right_cord = [float(ME.char_bbox_list[page][me_0][2]), float(ME.char_bbox_list[page][me_0][1])]
		me_0 = me_0+1
	new_me_boxes.append([x0, y0, x1, y1]) #Last box
	return new_me_boxes

def me_box_check():


	#Check for EME that needs to be split
	#print("\n\n\n\n\n**********************START FRAGMENT SERACH**********************************")
	for page in ME.page_with_me:
		me_set = ME.page_with_me[page]
		me_index_set = ME.me_index_list[page]
		me_fragment_set = []
		new_me_boxes = []
		new_me_index = 0
		i = 0
		#isolation threshold radius to determine iregular spaceing
		isolation_radius = ME.pdf_euclidean_2d_stats[0] + ME.pdf_euclidean_2d_stats[0]
		me_fragmented_map = []
		for me in me_set:
			me_size = ME.me_size_list[me]
			new_me_index_list = []
			if(ME.is_IME_set[page][i] == 1 or ME.is_IME_set[page][i] == 0):
				''' 
					Check for fragmneted EME (split)
				    In these cases one or both of the following will happen:
				    1) The left most character in the ME will not be on the left border of the full box
				    2) The right most character in the ME will not be on the right border of the full box
				    Only need the x cordinate to check
				    3) There will be more characters in the box from the PDF than the number of ME characters
				'''
				fullbox_left_xcord = float(ME.me_bbox_list[page][i][0])
				fullbox_right_xcord = float(ME.me_bbox_list[page][i][2])
				fullbox_rec = [float(ME.me_bbox_list[page][i][0]), 
					float(ME.me_bbox_list[page][i][1]), float(ME.me_bbox_list[page][i][2]), 
					float(ME.me_bbox_list[page][i][3])]

				firstme_left_xcord = float(ME.char_bbox_list[page][me_index_set[i][0]][0])
				lastme_right_xcord = float(ME.char_bbox_list[page][me_index_set[i][0]+me_size-1][2])
				lastme_top_ycord = float(ME.char_bbox_list[page][me_index_set[i][0]+me_size-1][1])

				#print("expected ME",ME.char_bbox_list[page][me_index_set[i][0]:me_index_set[i][0]+me_size-1])
				prev_nonme_set = []
				post_nonme_set = []
				post_nonme_char_set = []	

				if(firstme_left_xcord != fullbox_left_xcord):
					'''
						Check to see if any prev characters are inside the box
					'''
					stop_flag = 1
					loop_index = 1
					while(stop_flag != 0):
						curr_rec = [float(ME.char_bbox_list[page][me_index_set[i][0]-loop_index][0]), 
							float(ME.char_bbox_list[page][me_index_set[i][0]-loop_index][1]), 
							float(ME.char_bbox_list[page][me_index_set[i][0]-loop_index][2]), 
							float(ME.char_bbox_list[page][me_index_set[i][0]-loop_index][3])]
						curr_area = get_area(curr_rec)
						CA = cross_area(fullbox_rec, curr_rec)
						if(CA >= curr_area):
							prev_nonme_set.append(curr_rec)
						else:
							stop_flag = 0
						loop_index = loop_index + 1
				elif(lastme_right_xcord != fullbox_right_xcord):
					'''
						Check to see if any post characters are inside the box
					'''
					stop_flag = 1
					loop_index = me_size
					while(stop_flag != 0):
						curr_rec = [float(ME.char_bbox_list[page][me_index_set[i][0]+loop_index][0]), 
							float(ME.char_bbox_list[page][me_index_set[i][0]+loop_index][1]), 
							float(ME.char_bbox_list[page][me_index_set[i][0]+loop_index][2]), 
							float(ME.char_bbox_list[page][me_index_set[i][0]+loop_index][3])]
						curr_area = get_area(curr_rec)
						CA = cross_area(fullbox_rec, curr_rec)
						if(CA >= curr_area):
							post_nonme_set.append(curr_rec)
							post_nonme_char_set.append(ME.pdf_char_list[page][me_index_set[i][0]+loop_index])
						else:
							stop_flag = 0
						loop_index = loop_index + 1

				if(len(prev_nonme_set) != 0):
					#print("IS FRAGMENT")
					#print("ME is", me)
					fragmented_boxes = me_fragmented_boxes(me_index_set, i, page)
					for box in fragmented_boxes:
						new_me_index_list.append(new_me_index)
						new_me_boxes.append(box)
						new_me_index = new_me_index + 1
					me_fragment_set.append(1)
				elif(len(post_nonme_set) != 0):
					#Is a fragment if the next character is within normal space conditions
					'''
						post_point_set.append([float(square[0]), float(square[1])]) #topleft
						post_point_set.append([float(square[2]), float(square[1])]) #topright

					'''
					
					distance = point_distance([post_nonme_set[0][0], post_nonme_set[0][1]], [lastme_right_xcord, lastme_top_ycord])
					if(distance <= isolation_radius):
						#Make sure it is not a very close reference number
						post_text = ''.join(post_nonme_char_set[0:len(post_nonme_char_set)])
						#print("post_text", post_text)
						if(re.search("\(([0-9]+)[\.]?([0-9]+)?[\)]?", post_text)):
							#print("NOT FRAGMENT")
							me_fragment_set.append(0)
						else:
							#print("IS FRAGMENT", page)
							#print("ME is", me)	
							fragmented_boxes = me_fragmented_boxes(me_index_set, i, page)
							for box in fragmented_boxes:
								new_me_index_list.append(new_me_index)
								new_me_boxes.append(box)
								new_me_index = new_me_index + 1
							me_fragment_set.append(1)					

						#print("************************************\n\n\n")
					else:
						me_fragment_set.append(0)
				else:
					me_fragment_set.append(0)
			else:
				me_fragment_set.append(0)

			me_fragmented_map.append(new_me_index_list)
			#print("ReALLY", me_fragmented_map[i])
			i = i + 1
		ME.is_fragment_set[page] = me_fragment_set
		if(len(new_me_boxes) > 1):
			ME.me_fragmented_box_set[page] = new_me_boxes
		#print me_fragmented_map
		ME.me_fragmented_map[page] = me_fragmented_map

	n = 0
	'''Check for boxes that are inside another box. Happens when an 
	ME is not found but is found uniquley as a subset within another mE
	'''
	for page in ME.me_bbox_list:
		i = 0
		for box in ME.me_bbox_list[page]:
			if(box == "FAILED"):
				i = i + 1
				continue
			j = 0
			curr_rec = [box[0], box[1], box[2], box[3]]
			#print box
			curr_rec_area = get_area(curr_rec)
			cross_flag = 0
			for box2 in ME.me_bbox_list[page]:
				#print box2
				if(j == i or box2 == "FAILED" or ME.is_fragment_set[page][j] == 1):
					j = j + 1
					continue
				box_rec = [box2[0], box2[1], box2[2], box2[3]]						
				CA = cross_area(box_rec, curr_rec)
				if(CA >= curr_rec_area):
					ME.me_fail_list[page][i] = "FAILED"
					ME.me_bbox_list[page][i] = "FAILED"
					ME.ME_PDF_EXACT[page][i] = "FAILED"
					ME.me_char_bbox_list[page][i] = "FAILED"
					ME.is_IME_set[page][i] = "FAILED"
					ME.find_count = ME.find_count - 1
					break
				j = j + 1
			i = i + 1
			n = n + 1
		#print ME.me_fragmented_map[page]


load_pdf_metadata()				
get_mined_pdf_data()
get_mined_xml_data()
calc_me_xml_size()
#splt_xml_data()

result = split_xml_into_pages_1()
if(result == 0):
	get_mined_pdf_data()
	result = split_xml_into_pages_1()
	if(result == 0):
		print("FILE FORMAT IS BADLY ALIGNED BETWEEN LATEX-XML AND PDF")
		print ME.max_page
		#sys.exit()

locate_page_me_sets()
get_prev_post_me_text()
locate_me_in_pdf()
me_box_check()
draw_me_box()
merge_pdf()


def ground_truth_results():
	json_output = {}
	directory = filename + "_data/pdfbox_output/"
	for page in ME.page_with_me:
		me_set = ME.page_with_me[page]
		pdf_set = ME.ME_PDF_EXACT[page]
		#pdf_specs = ME.pdf_spec_list[page]
		me_info = {}
		

		me_latex_list = []
		me_pdf_list = []
		bbox_list = []
		is_IME_list = []
		char_bbox_list = []
		relationship_list = []
		me_fragment_list = []
		me_fragment_map = []
		i = 0
		for me in me_set:
			if(ME.me_fail_list[page][i] == 1):
				me_latex_list.append(me)
				me_pdf_list.append(["FAILED"])
				bbox_list.append(["FAILED"])
				is_IME_list.append("FAILED")
				char_bbox_list.append(["FAILED"])
				relationship_list.append(["FAILED"])
				me_fragment_list.append("FAILED")
				me_fragment_map.append(["FAILED"])
			else:
				me_latex_list.append(me)
				#print("pdf_specs", pdf_specs[i])
				me_pdf_list.append(pdf_set[i])
				bbox_list.append(ME.me_bbox_list[page][i])
				is_IME_list.append(ME.is_IME_set[page][i])
				char_bbox_list.append(ME.me_char_bbox_list[page][i])
				me_fragment_list.append(ME.is_fragment_set[page][i])
				me_fragment_map.append(ME.me_fragmented_map[page][i])
				'''
				   CHECK FOR SUBSCRIPT RELATION
				'''
				p = re.compile("(_\{.*?\})")
				unique_sub_list = {}
				rl_list = []
				for k in p.findall(me):
					tmp_me = me.split(k)
					if(k not in unique_sub_list):
						unique_sub_list[k] = 0
					else:
						unique_sub_list[k] = unique_sub_list[k] + 1
					tmp_me_index = 0
					prev_var_count = 0
					while(tmp_me_index <= unique_sub_list[k]):
						prev_var_count = prev_var_count + len(reduce_single_me(tmp_me[tmp_me_index]))
						tmp_me_index = tmp_me_index + 1
					sub_size = reduce_single_me(k)
					if(prev_var_count+len(sub_size)-1 != 0):
						tmp = [me, "sub", prev_var_count-1, [prev_var_count,prev_var_count+len(sub_size)-1]]
						rl_list.append(tmp)
					#count = count + 1
					#print("\n")
					unique_sub_list[k] = 1

				'''
				   CHECK FOR SUPERSCRIPT RELATION
				'''
				p = re.compile("(\^\{.*?\})")
				unique_sup_list = {}
				for k in p.findall(me):
					tmp_me = me.split(k)
					if(k not in unique_sup_list):
						unique_sup_list[k] = 0
					else:
						unique_sup_list[k] = unique_sup_list[k] + 1

					tmp_me_index = 0
					prev_var_count = 0
					while(tmp_me_index <= unique_sup_list[k]):
						prev_var_count = prev_var_count + len(reduce_single_me(tmp_me[tmp_me_index]))
						tmp_me_index = tmp_me_index + 1
						#print("prev_var loop", prev_var_count)
					sup_size = reduce_single_me(k)
					if(prev_var_count+len(sup_size)-1 != 0):
						tmp = [me, "sup", prev_var_count-1, [prev_var_count, prev_var_count+len(sup_size)-1]]
						rl_list.append(tmp)


				'''
				   CHECK FOR MATRIX RELATION
				'''
				p = re.compile("\\end{array}")
				#print("matrix end count", p.findall(me))
				p = re.compile("begin{array}\[\]")
				#print("matrix begin count", p.findall(me))
				#print("matrix me", me)
				k_index = 0
				for k in p.findall(me):
					#print("matrix", k)
					tmp_me = me.split("begin{array}[]")
					tmp_me_cpy = me
					#print("split me", tmp_me)
					tmp_me = tmp_me[k_index+1].split("end{array}")
					curr_matrix = tmp_me[0]
					p = re.compile("\{(c+)\}")
					for col_count in p.findall(curr_matrix):
						curr_matrix = curr_matrix.replace("{" + col_count + "}", "")
					p = re.compile("\{(c+)\}")
					for col_count in p.findall(tmp_me_cpy):					
						tmp_me_cpy = tmp_me_cpy.replace("{" + col_count + "}", "")
					#print("curr_matrix", curr_matrix)
					latex_matrix = curr_matrix
					prev_var_cnt = 0
					counter = 0
					while(counter < k_index+1):
						prev_data = tmp_me_cpy.split("begin{array}[]")
						prev_var_cnt = prev_var_cnt + len(reduce_single_me(prev_data[counter]))
						counter = counter+1
					#print("reduced matrix", reduce_single_me(curr_matrix))
					#print("prev var count", prev_var_cnt)
					matrix_size = len(reduce_single_me(curr_matrix))
					k_index = k_index + 1
					if(prev_var_cnt+matrix_size-1 != 0):
						#-2 to get the character before the brackets. -1 gives bracket for matrix
						tmp = [me, "matrix", prev_var_cnt-2, [prev_var_cnt-1, prev_var_cnt+matrix_size]]
						rl_list.append(tmp)
				'''
				   CHECK FOR FRACTION RELATION
				'''			
				p = re.compile("frac\{(.*?)\}\{(.*?)\}")
				match_index = 0
				for match in p.findall(me):
					#print("frac match", match)	
					tmp_me = me.split("frac")
					prev_var_cnt = 0
					counter = 0
					while(counter < match_index+1):
						prev_var_cnt = prev_var_cnt + len(reduce_single_me(tmp_me[counter]))
						counter = counter + 1
					frac_size = len(match[0]) + len(match[1])
					
					if(prev_var_cnt+frac_size-1 != 0):
						tmp = [me, "frac", prev_var_cnt-1, [prev_var_cnt, prev_var_cnt+frac_size-1]]
						rl_list.append(tmp)	
					match_index = match_index + 1					
					
				if(len(rl_list) == 0):
					relationship_list.append([me, "NO RELATION"])
				else:
					relationship_list.append(rl_list)
			i = i + 1
		me_info["page_num"] = page
		me_info["ME_LATEX"] = me_latex_list
		me_info["PDFBOX_CHARLIST"] = me_pdf_list
		me_info["FULL_BBOX"] = bbox_list
		me_info["CHAR_BBOX"] = char_bbox_list
		me_info["relationship_list"] = relationship_list
		me_info["is_IME"] = is_IME_list
		me_info["is_fragment"] = me_fragment_list
		me_info["fragment_map"] = me_fragment_map
		if(page in ME.me_fragmented_box_set):
			me_info["fragment_me_boxes"] = ME.me_fragmented_box_set[page]
		else:
			me_info["fragment_me_boxes"] = "NONE"
		#1605.02019.pdf_3_page_8.pdf_destination

		json_output[filename+".pdf_"+str(page+1)+"_page_"+str(ME.max_pages)+".pdf"] = me_info



	final_json_output = {}
	final_json_output["GLOBAL_STATISTICS"] = {"pdf_xspace": ME.pdf_xspace_stats, "pdf_yspace": ME.pdf_yspace_stats,
		 "pdf_euclidean2d": ME.pdf_euclidean_2d_stats, "avg_chars_perline":ME.avg_chars_perline}
	final_json_output["pdf_me_data"] = json_output
	with open(directory + filename + "_ground_truth.json", "w") as outfile:
		json.dump(final_json_output, outfile)

	return 1

gt_results = ground_truth_results()
if(gt_results == 1):
	#confirm all pages are in the failed_page folder
	for dsp in ME.dataset_pages:
		me_found_ratio = dsp[0]
		if(me_found_ratio == 1):
			#Place in full_page folder
			os.system(dsp[1])
			with open("full_page/me_info.txt" , "a") as page_metadata:
				page_metadata.write(dsp[2])
		elif(me_found_ratio >= 0.95):
			#place in 95_page folder
			os.system(dsp[1])
			with open("95_page/me_info.txt" , "a") as page_metadata:
				page_metadata.write(dsp[2])
		elif(me_found_ratio >= 0.90):
			#place in 90_page folder
			os.system(dsp[1])
			with open("90_page/me_info.txt"  , "a") as page_metadata:
				page_metadata.write(dsp[2])
		elif(me_found_ratio >= 0.80):
			#place in 80_page folder
			os.system(dsp[1])
			with open("80_page/me_info.txt"  , "a") as page_metadata:
				page_metadata.write(dsp[2])
		elif(me_found_ratio >= 0.70):
			#place in 70_page folder
			os.system(dsp[1])
			with open("70_page/me_info.txt" , "a") as page_metadata:
				page_metadata.write(dsp[2])
		elif(me_found_ratio >= 0.50):
			#place in 70_page folder
			os.system(dsp[1])
			with open("50_page/me_info.txt" , "a") as page_metadata:
				page_metadata.write(dsp[2])
		elif(me_found_ratio >= 0.25):
			#place in 70_page folder
			os.system(dsp[1])
			with open("25_page/me_info.txt" , "a") as page_metadata:
				page_metadata.write(dsp[2])
		else:
			#place in failed_page folder
			os.system(dsp[1])
			with open("failed_page/me_info.txt" , "a") as page_metadata:
				page_metadata.write(dsp[2])


print ME.find_count
print len(ME.me_list)


