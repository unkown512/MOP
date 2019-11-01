import PyPDF2
import re
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import subprocess
import os
import math
import sys

filename = sys.argv[1]
#filename = "0304011"
#"0302007"
#"0303124"
#"0304011"
#"9602063"
#"1605.02019"
#"9610131"


#Use first column on normal ACII chars
PDF_NORM_ACII_CHARS = {
	"minus": "-",
	"zero": "0",
	"one": "1",
	"two": "2",
	"three": "3",
	"four": "4",
	"five": "5",
	"six": "6",
	"seven": "7",
	"eight": "8",
	"nine": "9",
	"period": ".",
	"comma": ",",
	"parenleft": "(",
	"parenright": ")",
	"Negative": "-",
	"equal": "=",
	"periodcentered": ".",
	"plus": "+",
	"colon": ":",
	"bracketleft": "[",
	"bracketright": "]",
	"quotedblleft": "",
	"quotedblright": "",
	"quoteleft": "",
	"quoteright": "",
	"numbersign": "#",
	"hyphen": "-",
	"slash": "/",
	"asteriskmath": "*",
	"dagger": "d",
	"exclam": "!",
	"null": "wildcard",
	#"semicolon": ";",
}

MULTI_PAREN_CASE = {
	"parenlefttp": "parenleftbt",
	"parenrighttp": "parenrightbt",
	"bracelefttp": "braceleftbt",
	"bracerighttp": "bracerightbt",
}

class PDF_DATA():
	pages = 0
	page_height = 0
	mined_data = []
	line_swap_map = {}
	possible_refnum_jump = {}

	page_xnn_space_list = {} # for each char: subtract the current min(x) cord. from the prev chars max(x) cord.
	page_line_y_space_list = {}
	euclidean_2d_list = {}
	average_chars_perline = {}

	'''page_height_variance = 0
	page_height_mean = 0
	page_max_height = 0
	page_min_height = 0

	pdf_height_variance = 0
	pdf_height_mean = 0
	pdf_min_height = 0
	pdf_max_height = 0'''


def split_pdf(filename):

	#Create temp directory for data
	directory = filename + "_data/"
	if not os.path.exists(directory):
		os.makedirs(directory)
	
	# creating a pdf file object 
	pdfFileObj = open("loading_dock/" + filename + '.pdf', 'rb') 
	  
	# creating a pdf reader object 
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 

	start = 1
	end = pdfReader.numPages
	if(end > 40):
		return "ToLarge"
	PDF_DATA.pages = end

	outfile = directory + filename
	pdf_writer = PyPDF2.PdfFileWriter()
	while start<=end:
	    pdf_writer.addPage(pdfReader.getPage(start-1))
	    output_filename = '{}_{}_page_{}.pdf'.format(outfile + ".pdf",start, end)
	    with open(output_filename,'wb') as out:
	        pdf_writer.write(out)
	    pdf_writer = PyPDF2.PdfFileWriter()
	    start+=1

	return directory

def run_PDFBOX(filename, index, data_directory):

	file = filename + ".pdf_" + str(index+1) + "_page_" + str(PDF_DATA.pages) + ".pdf"
	file = data_directory + file
	command = "java -jar PDFBox/PrintFontBoxGlyphBox.jar " + file
	os.system(command)


def get_PDFBox_data(filename, index, data_directory):
	#filename = directory + "file"
	#1605.02019.pdf_1_page_8.pdf.0
	file = data_directory + filename + ".pdf_" + str(index+1) + "_page_"
	file = file + str(PDF_DATA.pages) + ".pdf.0.txt"
	with open(file) as fn:
		prev_x = 0
		prev_bx = 0
		prev_y = 0
		prev_yx = 0
		line_count = 0
		refnum_jump = []
		special_flag = 0
		special_paren_key = ""
		special_paren_endkey = ""
		special_paren_box = []
		page_xnn_space_list = []
		page_line_y_space_list = []
		page_euclidean_2d_list = []
		char_count = 0

		for line in fn:
			curr_line = []
			#Need page hieght for proper bbox placement
			if("PDFINFO" in line):
				tmp = line.split(",")
				tmp = tmp[1].split(")")
				tmp[0] = tmp[0].replace(" ", "")
				PDF_DATA.page_height = float(tmp[0])

			tmp = line.split("\t")

			if(len(tmp) > 3):
				curr_char = tmp[4]
				if(curr_char in PDF_NORM_ACII_CHARS):
					if(len(PDF_NORM_ACII_CHARS[curr_char]) > 0):
						curr_char = PDF_NORM_ACII_CHARS[curr_char]
					else:
						curr_char = tmp[3]
				if(curr_char in MULTI_PAREN_CASE or special_flag == 1):
					tmp_box = tmp[5].split(",")
					tmp_big_box = tmp[7].rstrip()
					tmp_big_box = tmp_big_box.split(",")
					if(special_paren_key == ""):
						special_paren_key = curr_char
						special_flag = 1
						special_paren_endkey = MULTI_PAREN_CASE[curr_char]
					if(len(special_paren_box) == 0):
						special_paren_box = tmp_box
						continue
					else:
						#keep min and max y updated
						if(float(tmp_box[1]) < float(special_paren_box[1])):
							special_paren_box[1] = tmp_box[1]
						if(float(tmp_box[3]) > float(special_paren_box[3])):
							special_paren_box[3] = tmp_box[3]	
					if(curr_char == special_paren_endkey):
						curr_line.append(special_paren_key)
						for sbox in special_paren_box:
							curr_line.append(sbox)
						curr_line.append(tmp[1])
						curr_line.append(tmp[2])
						curr_line.append(tmp[3])
						if(prev_x != 0):
							page_xnn_space_list.append(abs(prev_x - float(special_paren_box[0])))
							page_line_y_space_list.append(abs(prev_y - curr_y))
							page_euclidean_2d_list.append(math.sqrt(pow(prev_x-float(special_paren_box[0]),2)+pow(prev_y-curr_y,2)))
						for tbb in tmp_big_box:
							curr_line.append(tbb)
						PDF_DATA.mined_data.append(curr_line)
						special_flag = 0
						special_paren_key = ""
						special_paren_endkey = ""
						special_paren_box = []
					else:
						continue

				elif(curr_char == "fi"):
					#Suppose to be two characters
					new_curr_line = ["f", "i"]
					bbox = tmp[5].split(",")
					tmp_big_box = tmp[7].rstrip()
					tmp_big_box = tmp_big_box.split(",")
					if(float(bbox[0]) < 33):
						continue
					first_bbox =  [str(float(bbox[0])) ,str(float(bbox[1])) ,str(float(bbox[2])-4.5) , str(float(bbox[3]))]
					second_bbox = [str(float(bbox[2])-4.5) , str(float(bbox[1])) , str(float(bbox[2])) , str(float(bbox[3]))]
					curr_line.append(new_curr_line[0])
					for fb in first_bbox:
						curr_line.append(fb)
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(prev_x - float(bbox[0])))
						page_line_y_space_list.append(abs(prev_y - float(bbox[3])))
						page_euclidean_2d_list.append(math.sqrt(pow(float(bbox[2])-4.5 - float(bbox[2])-4.5,2)+pow(prev_y - float(bbox[3]),2)))
					
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
					curr_line = []
					curr_line.append(new_curr_line[1])
					for sb in second_bbox:
						curr_line.append(sb)
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(float(bbox[2])-4.5 - float(bbox[2])-4.5))
						page_euclidean_2d_list.append(math.sqrt(pow(float(bbox[2])-4.5-float(bbox[2])-4.5,2)))
						page_line_y_space_list.append(0)
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
					curr_x = float(bbox[2])
					curr_y = float(bbox[3])
				elif(curr_char == "ff"):
					#Suppose to be two characters
					new_curr_line = ["f", "f"]
					bbox = tmp[5].split(",")
					tmp_big_box = tmp[7].rstrip()
					tmp_big_box = tmp_big_box.split(",")
					if(float(bbox[0]) < 33):
						continue
					first_bbox =  [str(float(bbox[0])) ,str(float(bbox[1])) ,str(float(bbox[2])-4.5) , str(float(bbox[3]))]
					second_bbox = [str(float(bbox[2])-4.5) , str(float(bbox[1])) , str(float(bbox[2])) , str(float(bbox[3]))]
					curr_line.append(new_curr_line[0])
					for fb in first_bbox:
						curr_line.append(fb)
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(prev_x - float(bbox[0])))
						page_line_y_space_list.append(abs(prev_y - float(bbox[3])))
						page_euclidean_2d_list.append(math.sqrt(pow(float(bbox[2])-4.5 - float(bbox[2])-4.5,2)+pow(prev_y - float(bbox[3]),2)))
					
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
					curr_line = []
					curr_line.append(new_curr_line[1])
					for sb in second_bbox:
						curr_line.append(sb)
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(float(bbox[2])-4.5 - float(bbox[2])-4.5))
						page_euclidean_2d_list.append(math.sqrt(pow(float(bbox[2])-4.5-float(bbox[2])-4.5,2)))
						page_line_y_space_list.append(0)
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
					curr_x = float(bbox[2])
					curr_y = float(bbox[3])
				elif(curr_char == "fl"):
					#Suppose to be two characters
					new_curr_line = ["f", "l"]
					bbox = tmp[5].split(",")
					tmp_big_box = tmp[7].rstrip()
					tmp_big_box = tmp_big_box.split(",")
					if(float(bbox[0]) < 33):
						continue
					first_bbox =  [str(float(bbox[0])) ,str(float(bbox[1])) ,str(float(bbox[2])-4.5) , str(float(bbox[3]))]
					second_bbox = [str(float(bbox[2])-4.5) , str(float(bbox[1])) , str(float(bbox[2])) , str(float(bbox[3]))]
					curr_line.append(new_curr_line[0])
					for fb in first_bbox:
						curr_line.append(fb)
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(prev_x - float(bbox[0])))
						page_line_y_space_list.append(abs(prev_y - float(bbox[3])))
						page_euclidean_2d_list.append(math.sqrt(pow(float(bbox[2])-4.5 - float(bbox[2])-4.5,2)+pow(prev_y - float(bbox[3]),2)))
					
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
					curr_line = []
					curr_line.append(new_curr_line[1])
					for sb in second_bbox:
						curr_line.append(sb)
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(float(bbox[2])-4.5 - float(bbox[2])-4.5))
						page_euclidean_2d_list.append(math.sqrt(pow(float(bbox[2])-4.5-float(bbox[2])-4.5,2)))
						page_line_y_space_list.append(0)
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
					curr_x = float(bbox[2])
					curr_y = float(bbox[3])
				else:
					curr_line.append(curr_char)
					bbox = tmp[5].split(",")
					tmp_big_box = tmp[7].rstrip()
					tmp_big_box = tmp_big_box.split(",")
					if(float(bbox[0]) < 33):
						continue
					for box in bbox:
						curr_line.append(box)
					curr_x = float(bbox[2])
					curr_y = float(bbox[3])
					if(prev_x !=0 ):
						if(curr_x - prev_x > 40):
							#Ref num jump possibly
							refnum_jump.append(str(len(PDF_DATA.mined_data)+1))
						if(curr_x < prev_x):
							PDF_DATA.average_chars_perline[line_count] = char_count
							char_count = 0
							PDF_DATA.line_swap_map[line_count] = line_count-1
							#print("PREV CHAR", PDF_DATA.mined_data[-1])
							if(PDF_DATA.mined_data[-1][0] == "-"):
								#PDF_DATA.mined_data[-1][0] = "EOL"
								PDF_DATA.mined_data.pop()
					curr_line.append(tmp[1])
					curr_line.append(tmp[2])
					curr_line.append(tmp[3])
					if(prev_x != 0):
						page_xnn_space_list.append(abs(prev_x - float(bbox[0])))
						page_line_y_space_list.append(abs(prev_y - curr_y))
						page_euclidean_2d_list.append(math.sqrt(pow(prev_x-float(bbox[0]),2)+pow(prev_y-curr_y,2)))					
					for tbb in tmp_big_box:
						curr_line.append(tbb)
					PDF_DATA.mined_data.append(curr_line)
				char_count = char_count+1
				prev_x = curr_x
				prev_y = curr_y
				prev_bx = 0
				prev_by = 0
				line_count = line_count + 1
	#Store to txt file
	PDF_DATA.euclidean_2d_list[index] = page_euclidean_2d_list
	PDF_DATA.page_line_y_space_list[index] = page_line_y_space_list
	PDF_DATA.page_xnn_space_list[index] = page_xnn_space_list
	PDF_DATA.possible_refnum_jump[index] = refnum_jump
	if not os.path.exists(data_directory + "pdfbox_output/"):
		os.makedirs(data_directory + "pdfbox_output/")
	os.remove(file)
	out_file = open(data_directory + "pdfbox_output/" + filename + "_page_" + str(index) + "_mined.txt", "w")
	for line_data in PDF_DATA.mined_data:
		line = ""
		for data in line_data:
			line = line + data + ","
		line = line + "\n"
		out_file.write(line)
	out_file.close()

	#print PDF_DATA.mined_data

def main():
	data_directory = split_pdf(filename)
	if(data_directory == "ToLarge"):
		return "Fail"
	start = 0
	while(start < PDF_DATA.pages):
		run_PDFBOX(filename, start, data_directory)
		get_PDFBox_data(filename, start, data_directory)
		PDF_DATA.mined_data = []
		start = start + 1
	outfile = open(data_directory + "pdfbox_output/pdf_metadata.txt", "w")
	outfile.write(str(PDF_DATA.pages) +","+ str(PDF_DATA.page_height) + "\n")
	refnum_jump_data = ""
	for page in PDF_DATA.possible_refnum_jump:
		print page
		print PDF_DATA.possible_refnum_jump[page]
		if(len(PDF_DATA.possible_refnum_jump[page])==0):
			continue
		refnum_jump_data = str(page) + "," + ','.join(PDF_DATA.possible_refnum_jump[page]) + "\n"
		outfile.write(refnum_jump_data)
	outfile.close()

	outfile = open(data_directory + "pdfbox_output/pdf_stats.txt", "w")
	#get x space diff
	total = 0
	i = 0
	total_squared = 0
	for page in PDF_DATA.page_xnn_space_list:

		for val in PDF_DATA.page_xnn_space_list[page]:
			total = total + float(val)
			total_squared = total_squared + pow(float(val),2)
			i = i + 1
	x_i = i
	x_mean = total/i
	x_std = str(math.sqrt(total_squared/i - pow(x_mean, 2)))
	outfile.write( str(x_mean) + "," + x_std + "," + str(x_i) + "\n")
	#Get line height diff
	total = 0
	i = 0
	total_squared = 0
	for page in PDF_DATA.page_line_y_space_list:

		for val in PDF_DATA.page_line_y_space_list[page]:
			total = total + float(val)
			total_squared = total_squared + pow(float(val),2)
			i = i + 1
		# page #, mean, std, total char count
	line_i = i
	line_mean = total/i
	line_std = str(math.sqrt(total_squared/i - pow(line_mean, 2)))
	outfile.write( str(line_mean) + "," + line_std + "," + str(line_i) + "\n")
	#euclidean 2d 
	total = 0
	i = 0
	total_squared = 0
	for page in PDF_DATA.euclidean_2d_list:

		for val in PDF_DATA.euclidean_2d_list[page]:
			total = total + float(val)
			total_squared = total_squared + pow(float(val),2)
			i = i + 1
		# page #, mean, std, total char count
	ed_i = i
	ed_mean = total/i
	ed_std = str(math.sqrt(total_squared/i - pow(ed_mean, 2)))
	outfile.write( str(ed_mean) + "," + ed_std + "," + str(ed_i) + "\n")
	

	char_sum = 0
	char_sum_squared = 0
	i = 0
	for char_total in PDF_DATA.average_chars_perline:
		char_sum = char_sum + PDF_DATA.average_chars_perline[char_total]
		char_sum_squared = char_sum_squared + pow(PDF_DATA.average_chars_perline[char_total],2)
		i = i + 1
	PDF_DATA.average_chars_perline = char_sum / i
	#print("average chars per line",PDF_DATA.average_chars_perline + (math.sqrt(char_sum_squared/i - pow(PDF_DATA.average_chars_perline, 2))))
	outfile.write(str(PDF_DATA.average_chars_perline + (math.sqrt(char_sum_squared/i - pow(PDF_DATA.average_chars_perline, 2)))))
	outfile.close()

main()