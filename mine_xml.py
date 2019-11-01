import PyPDF2
import re
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import subprocess
import os
import sys

filename = sys.argv[1]
#"0302007"
#"0303124"
#"0304011"
#"9602063"
#"1605.02019"
#"9610131"
directory = "loading_dock/"

class ME():
	me_latex = [] #Exact latex syntax
	me_refnum_list = {}
	#me_list = [] #Me string form to match with PDFBOX
	me_prev_text = {} #Text before ME (~25 characters)
	me_post_text = {} #Text after ME (~25 characters)
	me_with_ss_scripts = {}

	xml_text = "" #XLM text in seq order (same as pdf) without ME
	xml_full_text = ""
	xml_lines = [] #XLM line data

	me_ref_list = {} #ME bib cite refs
	me_cite_num = {} #ME number ref
	figure_cite_num = {} #Figure number ref
	ref_recovery_location = {} #location to swap reference key with value
	ref_rec_loc_class = {} #some cite class change the [] to ()

	title_count = 1


#Some class types change how things are represented in the PDF
REF_CITE_CLASS = {
	"ltx_citemacro_cite" : ["[to(", "]to)"]
}

#Python is dumb so yeah
number_list = ["0","1","2","3","4","5","6","7","8","9"]


def format_xml_math_space():
	#Make sure the <Math mode= is on new line >>>> :( AIDS
	outfile = open(directory + filename + "_formated.xml", "w")
	with open(directory + filename + ".xml") as fn:
		for line in fn:
			multi_me_check = [m.start() for m in re.finditer("<Math mode=", line)]
			if(len(multi_me_check) > 1):
				last_pos = 0
				new_line = line.split("<Math mode=")
				i = 1
				outfile.write(new_line[0])
				while(i < len(new_line)):
					outfile.write("\n<Math mode=" + new_line[i])
					i = i + 1
					
			else:
				outfile.write(line)
	outfile.close()

def format_xml_ref_space():
	#Make sure the <Math mode= is on new line >>>> :( AIDS
	outfile = open(directory + filename + "_formated_final.xml", "w")
	with open(directory + filename + "_formated.xml") as fn:
		comment_flag = 0
		for line in fn:
			#print("line", line)
			if(comment_flag == 1 and re.search("-->", line)):
				comment_flag = 0
				new_line = line.split("-->")
				#print("OI", new_line)
				line = new_line[1]
			if(re.search("<!--", line)):
				if(re.search("-->", line)):
					print("python sucks")
				else:
					#print("wtf", line)
					comment_flag = 1
					continue
			if(comment_flag == 1):
				continue
			multi_me_check = [m.start() for m in re.finditer("<ref labelref=", line)]
			if(len(multi_me_check) > 1):
				last_pos = 0
				new_line = line.split("<ref labelref=")
				i = 1
				outfile.write(new_line[0])
				while(i < len(new_line)):
					outfile.write("\n<ref labelref=" + new_line[i])
					i = i + 1
					
			else:
				outfile.write(line)
	outfile.close()
	os.remove(directory + filename + "_formated.xml")



#Newcite fix could have bugs in future... Need to watch it close
def ref_recovery():
	for ref_loc in ME.ref_recovery_location:

		data = ME.xml_lines[ref_loc]
		if(ME.ref_recovery_location[ref_loc] == "ERROR"):
			#fix \newcite errors, figure out correct ref since it is unknown
			for ref in ME.me_ref_list:
				gues_ref = "\\\\newcite" + ref
				if(re.search(gues_ref, data)):
					data = data.split("newcite")
					data[1] = data[1].split(ref)
					data = data[0][0:len(data[0])-1] + ME.me_ref_list[ref] + data[1][1]
					ME.xml_lines[ref_loc] = data
		else:
			data = data.split(ME.ref_recovery_location[ref_loc])
			if(ref_loc in ME.ref_rec_loc_class):
				if(ME.ref_rec_loc_class[ref_loc] in REF_CITE_CLASS):
					CLASS_RULE = REF_CITE_CLASS[ME.ref_rec_loc_class[ref_loc]]
					i = 0
					for rule in CLASS_RULE:
						rule = rule.split("to")
						if(i == 0):
							if(data[0][-1] == rule[0]):
								data[0] = data[0][0:len(data[0])-1] + rule[1]
						else:
							if(data[1][0] == rule[0]):
								data[1] = rule[1] + data[1][1:len(data[1])]
						i = i + 1

			if(re.search(",", ME.ref_recovery_location[ref_loc])):
				#More than one ref
				multi_refs = ME.ref_recovery_location[ref_loc].split(",")
				new_ref = ""
				i = 0
				for mref in multi_refs:
					if(mref in ME.me_ref_list):
						new_ref = new_ref + ME.me_ref_list[mref] 
						if(i+1 < len(multi_refs)):
							new_ref = new_ref + ","
						i = i + 1
						data = data[0] + new_ref + data[1]
				ME.xml_lines[ref_loc] = data


			else:
				if(ME.ref_recovery_location[ref_loc] in ME.me_ref_list):
					data = data[0] + ME.me_ref_list[ME.ref_recovery_location[ref_loc]] + data[1]
				ME.xml_lines[ref_loc] = data

	ME.xml_text = ""
	for line in ME.xml_lines:
		if(isinstance(line,list)):
			line = line[0]
		ME.xml_text = ME.xml_text + line

def check_missmatch_sign(data):
	#< only
	le_flag = 0
	ge_flag = 0
	last_index = 0
	i = 0
	for char in data:
		if(char == "<"):
			if(le_flag == 1):
				#double <
				data = data[0:i-1] + ">" + data[i:len(data)]
				i = i + 1
				last_index = i
			else:
				le_flag = le_flag + 1
		elif(char == ">"):
			if(le_flag == 0):
				#Problem add < to start
				#print("oi1", data, i)
				data = data[0:last_index] + "<" + data[last_index+1:len(data)]
				#print("oi2", data)
				i = i + 1
				le_flag = 0
				ge_flag = 0
				last_index = i
			elif(ge_flag == 1):
				#double >>
				data = data[0:i-1] + "<" + data[i:len(data)]
				i = i + 1
				last_index = i
			else:
				ge_flag = ge_flag + 1

		if(le_flag == 1 and ge_flag == 1):
			le_flag = 0
			ge_flag = 0
			last_index = i + 1
		i = i + 1

	if(le_flag == 1):
		data = data + ">"
	if(ge_flag == 1):
		data = "<" + data

	return data


def outfile_data():
	#Write to out file
	out_file = open(filename + "_data/" + filename + "_xmlmined.txt", "w")
	out_file.write(ME.xml_text)
	out_file.close()

	out_file = open(filename + "_data/" + filename + "_melist.txt", "w")
	for me in ME.me_latex:
		me = me + "\n"
		out_file.write(me)
	out_file.close()	
	out_file = open(filename + "_data/" + filename + "_merefnumlist.txt", "w")
	for meref in ME.me_refnum_list:
		meref = ME.me_refnum_list[meref] +"," +str(meref) + "\n"
		out_file.write(meref)
	out_file.close()
			
def parse_latex_from_xml(filename):
	count = 0
	reference_flag = 0
	key = 0
	unique_me_cite_count = 0
	unique_figure_cite_count = 0
	me_count = 0
	mathbranch_found = 0
	toccation_found = 0
	picture_found = 0
	last_me_ref = ""
	last_section_ref = ""
	#Need to get ref key list first
	with open(directory + filename + "_formated_final.xml") as fn:
		for line in fn:
			words = line
			#print words
			#print("\n\n\n\n")
			#Math brank and XMtok repeat the ME in different format
			#toccaption duplicates data in xml for figure captions
			if("References" in words):
				reference_flag = 1
			if(reference_flag == 1):
				#This block gets all references in the xml and their xml key
				if(re.search("bibitem key", words)):
					#Get ref key
					bibref = words.split("key=\"")
					bibref = bibref[1].split("\"")
					key = bibref[0]
					#Get ref name
				if(re.search("<bibtag role=\"refnum\"", words)):

					if(re.search("</ERROR>", words)):
						nameref = words.split("</ERROR>")
						nameref = nameref[1].split("</bibtag>")
						nameref = nameref[0]
					else:
						nameref = words.split("bibtag role=\"refnum\">")
						nameref = nameref[1].split("</bibtag>")
						nameref = nameref[0]
					if(re.search("et al.", nameref)):
						#These refs in xml are missing () after et al.
						nameref = nameref.split("et al.")
						nameref = nameref[0] + "etal.(" + nameref[1] + ")"

					nameref = nameref.replace(" ", "")
					ME.me_ref_list[key] = nameref
					continue	
			if(re.search("<picture", line)):
				picture_found = 1
				if(re.search("</picture>", line)):
					picture_found = 0
					words = words.split("</picture>")
					if(len(words) < 1):
						continue
					words = words[1]
			elif(re.search("</picture>", line)):
				picture_found = 0
				words = words.split("</picture>")
				if(len(words) < 1):
					continue
				words = words[1]
			if(picture_found == 1):
				continue
			if(re.search("<toccaption", line)):
				toccation_found = 1
				if(re.search("</toccaption>", line)):
					toccation_found = 0
					words = words.split("</toccaption>")
					if(len(words) < 1):
						continue
					words = words[1]
			elif(re.search("</toccaption>", line)):
				toccation_found = 0
				words = words.split("</toccaption>")
				if(len(words) < 1):
					continue
				words = words[1]
			if(toccation_found == 1):
				continue

			if(re.search("<MathBranch", line)):
				mathbranch_found = 1
				if(re.search("</MathBranch>", line)):
					mathbranch_found = 0
					words = words.split("</MathBranch>")
					if(len(words) < 1):
						continue
					words = words[1]				
			elif(re.search("</MathBranch>", line)):
				mathbranch_found = 0
				words = words.split("</MathBranch>")
				if(len(words) < 1):
					continue
				words = words[1]
			if(mathbranch_found == 1):
				continue

			if(re.search("(?<=<XMath>)(.*)(?=<\/XMath>)", words)):
				tmp_words = words
				tmp_words = tmp_words.split("<XMath>")
				new_words = tmp_words[0]
				tmp_words = tmp_words[1].split("</XMath>")
				new_words = new_words + tmp_words[1]
				words = new_words
			elif(re.search("XMTok", words)):
				continue
			if(re.search("(?<=xml:id=\")(.*)(?=\")", words)):
				#p = re.compile("(?<=xml:id=\")(.*)(?=\" )")
				#replacement =  p.findall(words)[0] 
				tmp_words = words
				tmp_words = tmp_words.split("xml:id=\"")
				new_words = tmp_words[0]
				tmp_words = tmp_words[1].split("\"")
				i = 1
				while(i < len(tmp_words)):
					new_words = new_words + tmp_words[i]
					if(i <= len(tmp_words)-2):
						new_words = new_words + "\""
					i = i + 1
				#print("replacement", replacement)
				#words = words.replace(replacement, "")
				words = new_words

			if(re.search("ref labelref", words)):
				#Found ME equation ref number
				cite_key = words.split("ref labelref=\"")
				cite_key = cite_key[1].split("\"")
				cite_key = cite_key[0]
				#print("cite_key", cite_key, words)
				#print ME.me_cite_num
				words = words.split("<ref l")
				if(re.search("fig", cite_key)):
					#Figure num instead of ME
					if(cite_key not in ME.figure_cite_num):
						unique_figure_cite_count = unique_figure_cite_count + 1
						ME.figure_cite_num[cite_key] = unique_figure_cite_count	
						words = words[0] + str(unique_figure_cite_count) + "<ref l" + words[1]	
					else:
						words = words[0] + str(ME.figure_cite_num[cite_key]) + "<ref l" + words[1]	

				elif(cite_key not in ME.me_cite_num):
					print("WTF", words, cite_key)					
					unique_me_cite_count = unique_me_cite_count + 1
					ME.me_cite_num[cite_key] = unique_me_cite_count		
					print str(ME.me_cite_num[cite_key])
					words = words[0] + str(unique_me_cite_count) + "<ref l" + words[1]
				elif(cite_key in ME.me_cite_num):				
					words = words[0] + str(ME.me_cite_num[cite_key]) + "<ref l" + words[1]

			if(re.search("bibref", words)):
				words = words.split("<bibref bibrefs=\"")
				bib_key = words[1].split("\" separator")
				words = words[0] + bib_key[0] + "<" + words[1]
				ME.ref_recovery_location[count] = bib_key[0]
				if(re.search("class=\"", words)):
					cite_class = words.split("class=\"")
					cite_class = cite_class[1].split("\">")
					cite_class = cite_class[0]
					ME.ref_rec_loc_class[count] = cite_class

			if(re.search("\\\\newcite", words)):
				#Some refs fail correct format in XML and appear with \newcite</ERROR>
				#Has two \\ for some reason?!?@!? AIDS
				ME.ref_recovery_location[count] = "ERROR"


			#Check if ME has (#) ref, should be placed after ME
			if(re.search("<equation frefnum=", words)):
				print("WTFF", words)
				me_ref_num = words.split("<equation frefnum=\"")
				me_ref_num = me_ref_num[1].split("\"")
				last_me_ref = me_ref_num[0]
				print("meref_num", last_me_ref)
				if(re.search("labels=\"", words)):	
					check_label = words.split("labels=\"")
					check_label = check_label[1].split("\"")
					check_label = check_label[0]
					if(check_label not in ME.me_cite_num):
						ME.me_cite_num[check_label] = last_me_ref
						unique_me_cite_count = unique_me_cite_count + 1
				ME.me_refnum_list[me_count] = last_me_ref
			elif(re.search("<equation refnum=", words)):
				me_ref_num = words.split("<equation refnum=\"")
				me_ref_num = me_ref_num[1].split("\"")
				last_me_ref = me_ref_num[0]	
				if(re.search("labels=\"", words)):	
					check_label = words.split("labels=\"")
					check_label = check_label[1].split("\"")
					check_label = check_label[0]
					if(check_label not in ME.me_cite_num):
						ME.me_cite_num[check_label] = last_me_ref
						unique_me_cite_count = unique_me_cite_count + 1
				if(last_me_ref[0] != "("):
					last_me_ref = "(" + last_me_ref + ")"
				ME.me_refnum_list[me_count] = last_me_ref
			elif(re.search("<equation ", words)):
				if(re.search("refnum=\"", words)):
					me_ref_num = words.split("refnum=\"")
					me_ref_num = me_ref_num[1].split("\"")
					last_me_ref = me_ref_num[0]	
					if(re.search("labels=\"", words)):	
						check_label = words.split("labels=\"")
						check_label = check_label[1].split("\"")
						check_label = check_label[0]
						if(check_label not in ME.me_cite_num):
							ME.me_cite_num[check_label] = last_me_ref
							unique_me_cite_count = unique_me_cite_count + 1
					if(last_me_ref[0] != "("):
						last_me_ref = "(" + last_me_ref + ")"
					ME.me_refnum_list[me_count] = last_me_ref

				#print last_me_ref	
			if(re.search("section refnum=\"", words)):
				section_id = words.split("section refnum=\"")
				section_id = section_id[1].split("\"")
				last_section_ref = section_id[0]

			#Grab all ME in tex=""
			if(re.search("tex=", words)):
				#[m.start() for m in re.finditer(pdf_char, ME.me_post_text[index])]
				multi_me_check = [m.start() for m in re.finditer("tex=\"", words)]
				#if(len(multi_me_check) > 1):
				#	print("o shit", words)
				latex = words.split("tex=\"")
				latex = latex[1].split("\"")
				
				latex[0] = latex[0].replace("\"", "")
				if(re.search("^{}", latex[0])):
					#Not a ME, just odd format for titles
					print("AYE")
				else:
					print("MELOC", latex[0])
					ME.me_latex.append(latex[0])
					#print("ME", latex[0])
					#Replace ME with [ME#]
					me_split = words.split("tex=\"")
					#[m.start() for m in re.finditer("ref labelref=\"", line)]
					#check for xml:id and text, sometimes they are swapped
					me_split_two = me_split[1].split("\"")
					#wtf = me_split_two[1].split(">")
					#if(len(wtf) == 1):
					#	me_split_two[1] = me_split_two[1] + ">"
					i = 2
					while(i < len(me_split_two)):
						me_split_two[1] = me_split_two[1] + "\""+ me_split_two[i]
						i = i + 1
					
					#print("WTF REF NUM", last_me_ref)
					new_words = me_split[0] + ">[ME#]" + last_me_ref + "< \"" + me_split_two[1]
					#print("new words", new_words)
					#print("last_me_ref", last_me_ref)
					last_me_ref = ""
					words = new_words
					#print("words", words)
					me_count = me_count + 1

			if(reference_flag == 0):
				words = check_missmatch_sign(words)
				title_flag = 0
				if(re.search("<title>", words)):
					#Check to make sure number is before it
					title_flag = 1
				words = re.sub("<[^>]+>", "", words)
				words = words.replace(" ", "")
				words = words.replace("\r", "")
				words = words.replace("\n", "")
				if(title_flag == 1):
					id_size = len(last_section_ref)
					curr_id = words[0:id_size]
					print("exptected ID", curr_id)
					print("actual ID", last_section_ref)
					print("for words:= ", words)
					#Need special condition for <I Introduction>
					if(curr_id != last_section_ref):
						words = last_section_ref + words
					elif(last_section_ref == "I" and words[1:12] == "ntroduction"):
						words = last_section_ref + words
					#Fix for sub sections and etc
					#if(words[0] not in number_list):
					#	words = str(ME.title_count) + words 

					ME.title_count = ME.title_count + 1
				#print words

				print("\n\n")
				ME.xml_lines.append(words)
				ME.xml_text = ME.xml_text + words

				count = count + 1

	#print ME.xml_text
	#print ME.ref_rec_loc_class
	#print ME.me_ref_list
	ref_recovery()
	outfile_data()

format_xml_math_space()
format_xml_ref_space()
parse_latex_from_xml(filename)

