import PyPDF2
import re
import matplotlib.pyplot as plt
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import StringIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

'''

	Latex XML duplicates ME info in a <mathbranch> that causes problems
	skip anything in these blocks



'''



filename = "1605.02019"

num_name_list = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

# NOTE: --> A ':'' in references becomes 'et al.''
SPECAL_REF_LIST = {
	":":"et al.",
}

SPECIAL_CHAR_LIST = {
	
	"{":"",
	"}": "",
	"^":"",
	"_":"",
	"\\mathbb": "",
	"mathcal":"",
	"displaystyle=":"",
	"displaystyle":"",
	"cdot": "periodcentered",
	" ":"",
	"leq":"lessequal",
	"geq":"greaterequal",
	"=":"equal",
	",":"comma",
	".":"period",
	"-":"Negative",
	"+":"plus",
	"\\in":"element",
	"&gt":"greater",
	"&lt;": "less",
	"&lt":"less",
	"less;": "less",
	"greater;": "greater",
	"vec":"vector",
	"/":"slash",
	"0":"zero",
	"1":"one",
	"2":"two",
	"3":"three",
	"4":"four",
	"5":"five",
	"6":"six",
	"7":"seven",
	"8":"eight",
	"9":"nine",
	"%&#10;": "",
	"(": "parenleft",
	")": "parenright",
	"\\":"",
}

class ME():
	me_latex = [] #Exact latex syntax
	me_list = [] #Me string form to match with PDFBOX
	me_static_list = [] #Does not change
	me_prev_text = {} #Text before ME (~25 characters)
	me_post_text = {} #Text after ME (~25 characters)
	me_origin_pt = {}
	me_with_ss_scripts = {}


	xml_text = "" #XLM text in seq order (same as pdf) without ME
	xml_text_list = [] #xml_text in array form

	me_ref_list = {} #ME bib cite refs
	me_cite_num = {} #ME number ref
	figure_cite_num = {} #Figure number ref

	char_bbox_list = [] #bbox for ME chars
	me_bbox_list = [] #bbox for whole ME
	pdf_string = "" #PDF string of data -- like xml but with ME
	pdf_char_list = [] #PDF string in array form

	pages = 8 #page count of PDF
	page_height = 0 #PDF page height from PDFbox

	me_find_count = 0
	me_fail_count = 0

	no_me_pages = {}


def draw_bbox(pdf_file, data):
    packet = StringIO.StringIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    for new_rec in data:

    	new_rec[0] = float(new_rec[0])
    	new_rec[1] = abs(ME.page_height - float(new_rec[1]))
    	new_rec[2] = float(new_rec[2])
    	new_rec[3] = abs(ME.page_height - float(new_rec[3]))

        can.setStrokeColorRGB(255,0,0)

        height = abs(new_rec[1]-new_rec[3])
        width = abs(new_rec[0]-new_rec[2])
        #print("new_rec", [new_rec[0],new_rec[1]-height,width,height])
        can.rect(new_rec[0],new_rec[1]-height,width,height, fill = 0, stroke=1)
        #can.rect(new_rec[0],new_rec[1],new_rec[2], new_rec[3], fill = 0, stroke=1)

            
    can.save()
    #move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(file(pdf_file+ ".pdf", "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = file("destination_" + pdf_file + ".pdf", "wb")
    output.write(outputStream)
    outputStream.close()

def me_reduction(found_me):
	found_me = found_me.replace("\\", "")
	found_me = found_me.replace("{", "")
	found_me = found_me.replace("}", "")
	found_me = found_me.replace("^", "")
	found_me = found_me.replace("_", "")
	found_me = found_me.replace("mathcal", "")
	found_me = found_me.replace("displaystyle=", "")
	found_me = found_me.replace("displaystyle", "")
	found_me = found_me.replace(" ", "")
	found_me = found_me.replace("lessequal", "l")
	found_me = found_me.replace("greaterequal", "g")
	found_me = found_me.replace("equal", "=")
	found_me = found_me.replace("comma", ",")
	found_me = found_me.replace("periodcentered", "d")
	found_me = found_me.replace("period", ".")
	found_me = found_me.replace("element", "i")
	found_me = found_me.replace("greater", "&")
	found_me = found_me.replace("less", "&")
	found_me = found_me.replace("vector", "v")
	found_me = found_me.replace("slash", "s")
	found_me = found_me.replace("beta", "b")
	found_me = found_me.replace("Sigma", "s")
	found_me = found_me.replace("sigma", "q")
	found_me = found_me.replace("equal", "e")
	found_me = found_me.replace("Negative", "-")
	found_me = found_me.replace("plus", "+")
	found_me = found_me.replace("parenleft", "(")
	found_me = found_me.replace("parenright", ")")	
	found_me = found_me.replace("lambda", "l")
	found_me = found_me.replace("alpha", "a")

	i = 0
	for num in num_name_list:
		found_me = found_me.replace(num, str(i))
		i = i + 1

	return found_me

def text_reduction(words, num_flag):
	words = re.sub('<[^>]+>', '', words)
	words = words.replace(" ", "")
	words = words.replace("(", "parenleft")
	words = words.replace(")", "parenright")
	words = words.replace("-", "hyphen")
	words = words.replace(".", "period")
	words = words.replace(",", "comma")
	words = words.replace("+", "plus")
	#words = words.replace(":", "colon")

	if(num_flag == 1):
		i = 0
		while(i < len(num_name_list)):
			words = words.replace(str(i), num_name_list[i])
			i = i + 1	

	reduction_count = 0
	if(num_flag == 2):	
		i = 0
		while(i < len(num_name_list)):
			num_of_replaces = [m.start() for m in re.finditer(num_name_list[i], words)]
			reduction_count = reduction_count + ((len(num_name_list[i])-1) * len(num_of_replaces)) 
			#if(len(num_of_replaces) > 0):
			#	print("word", num_name_list[i])
			#	print("reduction_count", reduction_count)
			#	print("num_of_replaces", len(num_of_replaces)) 
			words = words.replace(num_name_list[i], str(i))

			i = i + 1	

		words = words.replace("parenleft", "(")
		words = words.replace("parenright", ")")
		words = words.replace("hyphen", "-")
		words = words.replace("period", ".")
		words = words.replace("comma", ",")
		num_of_replaces = [m.start() for m in re.finditer("plus", words)]
		reduction_count = reduction_count + (3 * len(num_of_replaces))
		words = words.replace("plus", "+")

	return words, reduction_count

def ref_correction(words,flag):
	#Some references fail in the latex xml, so check to see if they are in the plane text
	#NOTE: Refs are in real numbers, so make sure format matches
	i = 0
	while(i < len(num_name_list)):
		words = words.replace(num_name_list[i], str(i))
		i = i + 1
	mpt = words
	new_mpt = ""
	for refs in ME.me_ref_list:
		#fffs = mpt.split("refs")
		#if(len(fffs) > 1):
		tmp_refs = ME.me_ref_list[refs].replace("et al.", ":")
		tmp_refs = tmp_refs.replace(" ", "")
		tmp_mpt = mpt.split(tmp_refs)
		if(len(tmp_mpt) > 1):
			#replace : with et al.
			i = 0
			while(i < len(tmp_mpt)-1):
				new_mpt = new_mpt + tmp_mpt[i] + ME.me_ref_list[refs] + ")"+ tmp_mpt[i+1][2:len(tmp_mpt[i+1])]
				i = i + 1

			new_mpt = new_mpt.replace(" ", "")
			plr_check = new_mpt.split("etal.")
			if(len(plr_check) == 2):
				new_mpt = plr_check[0] + "etal." + "(" + plr_check[1]
			if(flag == 1):
				new_mpt = new_mpt.replace(".", "period")
				new_mpt = new_mpt.replace("(","parenleft")
				new_mpt = new_mpt.replace(")","parenright")
				i = 0
				while(i < len(num_name_list)):
					new_mpt = new_mpt.replace(str(i), num_name_list[i])
					i = i + 1
	return new_mpt

def check_me_cite(words):
	last_char = words[-1]


	if(last_char == ")"):
		cite_name = cite_name + ")"
		i = len(words)-1
		while(i > 0):
			cite_name = words[i] + cite_name 
			if(words[i] == "("):
				return cite_name
			i = i - 1
	else:
		return "NA"


def split_pdf(filename):
	# creating a pdf file object 
	pdfFileObj = open(filename + '.pdf', 'rb') 
	  
	# creating a pdf reader object 
	pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
	  
	# printing number of pages in pdf file 
	#print(pdfReader.numPages) 

	start = 1
	end = pdfReader.numPages

	ME.pages = end
	#print start
	#print end


	pdf_writer = PyPDF2.PdfFileWriter()
	while start<=end:
	    #pdfReader.getPage(start-1)
	    pdf_writer.addPage(pdfReader.getPage(start-1))
	    output_filename = '{}_{}_page_{}.pdf'.format(filename + ".pdf",start, end)
	    with open(output_filename,'wb') as out:
	        pdf_writer.write(out)
	    pdf_writer = PyPDF2.PdfFileWriter()
	    start+=1

	#output_filename = '{}_{}_page_{}.pdf'.format(filename + ".pdf",start, end)
	#with open(output_filename,'wb') as out:
	#    pdf_writer.write(out)

def merge_pdf(filename):
	merger = PdfFileMerger()
	i = 1
	while(i <= ME.pages):
		if(i in ME.no_me_pages):
			dest_file = filename + ".pdf_" + str(i) + "_page_" + str(ME.pages) + ".pdf"
		else:
			dest_file = "destination_" + filename + ".pdf_" + str(i) + "_page_" + str(ME.pages) + ".pdf"
		merger.append(PdfFileReader(file(dest_file, 'rb')))
		i = i + 1
	merger.write("final_"+ filename + ".pdf")
		

def parse_latex_from_xml(filename):
	count = 0
	reference_flag = 0
	key = 0
	unique_me_cite_count = 0
	unique_figure_cite_count = 0
	#Need to get ref key list first
	with open(filename + ".xml") as fn:

		for line in fn:
			words = line
			words = re.sub("<[^>]+>", "", words)
			words = words.replace(" ", "")
			words = words.replace("\r", "")
			words = words.replace("\n", "")

			if(re.search("ref labelref", line)):
				#Found ME equation ref number
				cite_key = line.split("ref labelref=\"")
				cite_key = cite_key[1].split("\"")
				cite_key = cite_key[0]
				if(re.search("fig", cite_key)):
					#Figure num instead of ME
					if(cite_key not in ME.figure_cite_num):
						unique_figure_cite_count = unique_figure_cite_count + 1
						ME.figure_cite_num[cite_key] = unique_figure_cite_count				
				elif(cite_key not in ME.me_cite_num):					
					unique_me_cite_count = unique_me_cite_count + 1
					ME.me_cite_num[cite_key] = unique_me_cite_count
			if("References" in words):
				reference_flag = 1
			if(reference_flag == 1):
				#This block gets all references in the xml and their xml key
				if(re.search("bibitem key", line)):
					#Get ref key
					bibref = line.split("key=\"")
					bibref = bibref[1].split("\"")
					key = bibref[0]
					#Get ref name
				if(re.search("bibtag role", line)):
					nameref = line.split("</ERROR>")
					nameref = nameref[1].split("</bibtag>")
					nameref = nameref[0]
					ME.me_ref_list[key] = nameref	
				

	with open(filename + ".xml") as fn:
		me_found = 0
		post_data = ""
		old_words = ""
		mathbranch_found = 0
		for line in fn:
			#Check for math branch duplicate
			if(re.search("<MathBranch", line)):
				mathbranch_found = 1
			elif(re.search("</MathBranch", line)):
				mathbranch_found = 2
			if(mathbranch_found == 1):
				continue
			elif(mathbranch_found == 2):
				#End of math branch has been found
				mathbranch_found = 0

			words = line
			if(re.search("XMTok", words)):
				continue
			words = re.sub("<[^>]+>", "", words)
			words = words.replace(" ", "")
			words = words.replace("\r", "")
			words = words.replace("\n", "")
			words = words.replace("\\newcite", "")

			if(re.search("\(\)", words)):
				#print("cite ref word", words)
				cite_count = [m.start() for m in re.finditer("ref labelref=\"", line)]
				cite_keys = []
				for cites in cite_count:
					tmp_key = line[cites+14:cites+(len(line)-cites)]
					tmp_key = tmp_key.split("\"")
					cite_keys.append(tmp_key[0])
					cite_location = [m.start() for m in re.finditer("\(\)", words)]
					i = 0
					offset = 0
					#print("cite locs", len(cite_location))
					for cites in cite_location:
						if(cite_keys[i] in ME.me_cite_num):
							cite_name = ME.me_cite_num[cite_keys[i]]
						elif(cite_keys[i] in ME.figure_cite_num):
							cite_name = ME.figure_cite_num[cite_keys[i]]
						words = words[0:cites+1+offset] + SPECIAL_CHAR_LIST[str(cite_name)] + words[cites+1+offset:cites+(len(words)-cites)]
						offset = offset + len(str(cite_name))
						i = i + 1
					#print("new words", words)
<<<<<<< HEAD
					
=======

>>>>>>> ca08feaff6ab4c1fb135ea9e36d1a53e8b59fc2b
			if(re.search("\[\]", words)):
				#print("possible ref", words)
				#Check for multiple refs and store keys
				ref_count = [m.start() for m in re.finditer("bibrefs=\"", line)]
				ref_keys = []
				for refs in ref_count:
					tmp_key = line[refs+9:refs+(len(line)-refs)]
					tmp_key = tmp_key.split("\"")
					#print("data at index", tmp_key[0])
					ref_keys.append(tmp_key[0])
				#replace all empty [] in words with correct refs
				ref_location = [m.start() for m in re.finditer("\[\]", words)]
				i = 0
				offset = 0
				for refs in ref_location:
					ref_name = ME.me_ref_list[ref_keys[i]]
					for SRL in SPECAL_REF_LIST:
						ref_name = ref_name.replace(SRL, SPECAL_REF_LIST[SRL])
					#There are () after the et al. in bibrefs that the latex xml does not get
					plr_check = ref_name.split("et al.")
					if(len(plr_check) == 2):
						ref_name = plr_check[0] + "et al." + "(" + plr_check[1] + ")"
					words = words[0:refs+1+offset] + ref_name + words[refs+1+offset:refs+(len(words)-refs)]
					offset = offset + len(ref_name)
					i = i + 1
				#print("new words", words)
			ME.xml_text = ME.xml_text + words

			ME.xml_text_list.append(words)
			#print words
			if("References" in words):
				break
			if(me_found == 1):
				#print("next line", words)
				post_data = post_data + words

			if(re.search("tex=", line)):
				#ME.me_post_text[count] = post_data
				#Found a latex equation
				ME.me_post_text[count-1] = post_data
				post_data = ""
				latex = line.split("tex=\"")
				latex = latex[1].split("text")
				latex[0] = latex[0].replace("\"", "")
				#latex[0] has exact latex equation
				ME.me_latex.append(latex[0])
				#Next extract the character sequence to match with PDFBOX
				me_string = latex[0]
				for scl in SPECIAL_CHAR_LIST:
					me_string = me_string.replace(scl,SPECIAL_CHAR_LIST[scl])
				#print("me_string", me_string)
				#p = re.compile("(_{.*?}\^{.*?})")
				if(re.search("(_{.*?}\^{.*?})", latex[0])):
					ME.me_with_ss_scripts[me_string] = 1
					#print("Latex swap found", latex[0])
					#print("all matches", p.findall(latex[0]))
					#print("first group", p.search(latex[0]).group(0))
				ME.me_list.append(me_string)
				me_found = 1
				old_words = ME.me_post_text[count-1]
				if(len(ME.me_post_text[count-1]) < 5):
					ME.me_post_text[count-1] = ME.me_post_text[count-1] + me_string
				
				prev_words = ME.xml_text_list[-3] + ME.xml_text_list[-2] + words
				prev_words.replace("\n", "")
				prev_words.replace(" ", "")
				if(len(prev_words) > 3):
					ME.me_prev_text[count] = prev_words
				else:
					#The word before me is an ME, so add it and the text before that ME
					ME.me_prev_text[count] = ME.me_prev_text[count-1] + ME.me_list[count-1] + prev_words + old_words


					

				if(len(ME.me_prev_text[count]) < 9):
					ME.me_prev_text[count] = ME.me_list[count-1] + ME.me_prev_text[count]
				(ME.me_prev_text[count],reduction_count) = text_reduction(ME.me_prev_text[count],1)
				ME.me_origin_pt[count-1] = ME.me_post_text[count-1]
				(ME.me_post_text[count-1], reduction_count) = text_reduction(ME.me_post_text[count-1],1)

				#Correct failed refernces
				new_mpt = ref_correction(ME.me_prev_text[count],1)
				if(len(new_mpt) > 0):
					ME.me_prev_text[count] = ref_correction(ME.me_prev_text[count],1)

				count = count + 1
	
							
def get_PDFBox_data(filename, page_index):


	with open(filename + ".pdf." + str(page_index) +".txt") as fn:
		prev_x = 0
		line_count = 0
		for line in fn:
			if("PDFINFO" in line):
				tmp = line.split(",")
				tmp = tmp[1].split(")")
				tmp[0] = tmp[0].replace(" ", "")
				ME.page_height = float(tmp[0])

			tmp = line.split("\t")
			
			#print tmp
			if(len(tmp) > 3):
				tmp[4] = tmp[4].replace("minus", "Negative")
				#tmp[4] = tmp[4].replace("periodcentered", "dot")
				curr_char = tmp[4]
				if(curr_char == "colon"):
					curr_char = ":"
				ME.pdf_char_list.append(curr_char)
				ME.pdf_string = ME.pdf_string + curr_char
				bbox = tmp[5].split(",")
				ME.char_bbox_list.append(bbox)
				curr_x = float(bbox[2])
				#print("BBOX", bbox)
				if(prev_x !=0 ):
					if(curr_x < prev_x):
						if(ME.pdf_char_list[line_count-1] == "hyphen"):
							#Split word, latex xml does not have this
							ME.pdf_char_list[line_count-1] = "EOL"
				prev_x = curr_x
				line_count = line_count + 1

		'''
		Sometimes the latex xml line will contain more info than the page,
		because it contains all previous and post pages

		This can only happen to the first and last ME of a page


		#Soft check, needs to possibly be more defined by removing each ME
		from the top of the list once it has been drawn
		'''
		guess_check = ME.pdf_string[0:8]
		i = 0
		pml = -1
		for df in ME.me_prev_text:
			if(re.search(guess_check, ME.me_prev_text[df])):
				pml = i
				break
			i = i + 1
		if(pml != -1):
			tmp = ME.me_prev_text[pml].split(guess_check)
			ME.me_prev_text[pml] = guess_check + tmp[1]

def locate_post_text(index):
	#print("Second ME search", ME.me_list[index])
	#print("search text(post)", ME.me_post_text[index])
	new_mpt = ref_correction(ME.me_post_text[index],1)
	#print("real mpt", new_mpt)
	if(len(new_mpt) > 0):
		ME.me_post_text[index] = new_mpt
		#print("new text(post)", new_mpt)
	
	for data in ME.me_list:
		data = ME.me_list[index]
		curr_match = ""
		match_hits = 0
		find_flag = 0
		bbox_index = 0
		for pdf_char in ME.pdf_char_list:
			#print("curr_match", curr_match)
			#print("pdf_char", pdf_char)
			#print("match hit", ME.me_post_text[index][match_hits])
			if(pdf_char == ME.me_post_text[index][match_hits]):
				curr_match = curr_match + ME.me_post_text[index][match_hits]
				match_hits = match_hits + 1
				#print("curr_match", curr_match)
			elif(pdf_char in ME.me_post_text[index]):
				char_possible_location = [m.start() for m in re.finditer(pdf_char, ME.me_post_text[index])]
				i = 0
				while(i < len(char_possible_location)):
					#match hits is euqal to the location of the first character
					if(char_possible_location[i] != match_hits):
						i = i + 1
						continue
					else:
						if(pdf_char == ME.me_post_text[index][match_hits:match_hits+len(pdf_char)+i]):
							curr_match = curr_match + ME.me_post_text[index][match_hits:match_hits+len(pdf_char)+i]
							match_hits = match_hits + len(pdf_char)+i
							#print("special curr_match", curr_match)
						elif(pdf_char == ME.me_post_text[index][match_hits:match_hits+len(pdf_char)+i-1]):
							curr_match = curr_match + ME.me_post_text[index][match_hits:match_hits+len(pdf_char)+i-1]
							match_hits = match_hits + len(pdf_char)+i-1
							#print("special curr_match", curr_match)							
						else:
							match_hits = 0
							curr_match = ""
							break
					i = i + 1
			else:
				match_hits = 0
				curr_match = ""
				me_size = 0
			#print("curr_match", curr_match)
			if(curr_match == ME.me_post_text[index]):
				#Match found
				found_me = ME.me_list[index]
				found_me = me_reduction(found_me)

				(txt_reduction, reduction_count) = text_reduction(ME.me_post_text[index], 2)
				#print("txt_reduction", txt_reduction)
				#print("reduction_count", reduction_count)

				

				me_size = len(found_me)

				#print("me_size", me_size)

				#print("ME found", found_me)
				#print("ME in PDF", ME.pdf_char_list[bbox_index - len(txt_reduction)-len(found_me)-2:bbox_index - len(txt_reduction)-4])
				fail_odd_check = 0
				success_flag = 0

				#check_me_cite
				#print("found_me[0]", found_me[0])
				#print("without reduction", ME.pdf_char_list[bbox_index - len(txt_reduction)-len(found_me):bbox_index - len(txt_reduction)-len(found_me)+me_size])
				while(fail_odd_check <= reduction_count):
					print me_reduction(ME.pdf_char_list[bbox_index - len(txt_reduction)-len(found_me)-fail_odd_check])
					if(found_me[0] == me_reduction(ME.pdf_char_list[bbox_index - len(txt_reduction)-len(found_me)-fail_odd_check])):
						success_flag = 1
						break

					fail_odd_check = fail_odd_check + 1

				#print("pdf char me", ME.pdf_char_list[bbox_index - len(txt_reduction)-len(found_me)-fail_odd_check:bbox_index - len(txt_reduction)-len(found_me)-fail_odd_check+me_size])

				if(fail_odd_check >= reduction_count):
					#print("Odd ME found", found_me )
					break



				true_index = bbox_index - len(txt_reduction)-len(found_me)-fail_odd_check
				me_0 = true_index
				#Some of the PDF text is grouped with a cite number
				me_f = true_index + me_size 
				#print("fail_odd_check", fail_odd_check)
				if(data not in ME.me_with_ss_scripts):
					#This ME does not have ^ or _ to mess up order
					#print("data check", data)
					#print("me char list??", ME.pdf_char_list[true_index:me_f])
					pdf_me_data = ME.pdf_char_list[true_index:me_f]
					data_mirror = ""
					for char in pdf_me_data:
						data_mirror = data_mirror + char
					#print("data mirror", data_mirror)
					if(data != data_mirror):
						#Fail match to another page
						break
				# Match found 100%
				ME.me_find_count = ME.me_find_count + 1
				find_flag = 1
				#print("pdf_char_list", ME.pdf_char_list[true_index:me_f])
				match_check = ""

				x0 = ME.char_bbox_list[me_0][0]
				y0 = ME.char_bbox_list[me_0][1]
				x1 = ME.char_bbox_list[me_0][2]
				y1 = ME.char_bbox_list[me_0][3]

				while(me_0 < me_f):
					if(ME.char_bbox_list[me_0][1] < y0):
						y0 = ME.char_bbox_list[me_0][1]

					if(ME.char_bbox_list[me_0][3] > y1):
						y1 = ME.char_bbox_list[me_0][3]

					if(ME.char_bbox_list[me_0][0] < x0):
						x0 = ME.char_bbox_list[me_0][0]

					if(ME.char_bbox_list[me_0][2] > x1):
						x1 = ME.char_bbox_list[me_0][2]	
					me_0 = me_0 + 1

				ME.me_bbox_list.append([x0,y0,x1,y1])
				#print("ME post", data)
				#print("bbox", ME.me_bbox_list[-1])
				#print("real ME", ME.me_list[index])
				#print("post text", ME.me_post_text[index])
				#print("\n--------------------------")
				break

			bbox_index = bbox_index + 1
		#if(find_flag == 1):
		#	print("found ME on second search", data)
		#	print("post text", ME.me_post_text[index])
		#if(find_flag == 0):
		#	print("Failed on second search post text", data)
		#	print("post text", ME.me_post_text[index])
		break


def locate_prev_text():
	index = 0
	for data in ME.me_list:
		curr_match = ""
		match_hits = 0
		find_flag = 0
		bbox_index = 0

		for pdf_char in ME.pdf_char_list:
			#print("curr_match", curr_match)
			#print("pdf_char", pdf_char)
			#print("match hit", ME.me_post_text[index][match_hits])
			
			#if(ME.me_prev_text[index][match_hits] == pdf_char and pdf_char == ":"):
				#print("YES")
			if(pdf_char == "EOL"):
				bbox_index = bbox_index + 1
				continue
			elif(pdf_char == ME.me_prev_text[index][match_hits]):
				curr_match = curr_match + ME.me_prev_text[index][match_hits]
				match_hits = match_hits + 1
				#print("curr_match", curr_match)
			elif(pdf_char in ME.me_prev_text[index]):
				#print("HERE")
				char_possible_location = [m.start() for m in re.finditer(pdf_char, ME.me_prev_text[index])]
				#print("char_possible_location", char_possible_location)
				i = 0
				while(i < len(char_possible_location)):
					#match hits is euqal to the location of the first character
					if(char_possible_location[i] != match_hits):
						#print("fuk no", char_possible_location[i])
						i = i + 1
						continue
					else:
						#print("Ye boi")
						#print("pdf_char", pdf_char)
						#print("check 1", ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)+i])
						#print("check 2", ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)+i-1])
						#print("check 2, " ,ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)])
						if(pdf_char == ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)+i]):
							curr_match = curr_match + ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)+i]
							match_hits = match_hits + len(pdf_char)+i
							#print("special curr_match", curr_match)
						elif(pdf_char == ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)+i-1]):
							curr_match = curr_match + ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)+i-1]
							match_hits = match_hits + len(pdf_char)+i-1
							#print("special curr_match", curr_match)	
						elif(pdf_char == ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)]):
							curr_match = curr_match + ME.me_prev_text[index][match_hits:match_hits+len(pdf_char)]
							match_hits = match_hits + len(pdf_char)											
						else:
							match_hits = 0
							curr_match = ""
							break
					i = i + 1
			else:
				match_hits = 0
				curr_match = ""
				me_size = 0

			if(curr_match == ME.me_prev_text[index]):
				#Possible Match found
				found_me = ME.me_list[index]

				'''
					NOTE: There are some ME's that use beta, sigma,
					and other symbol names as the variable name itself ._.
					instead of the damn symbol. GG
				'''
				mirror_me = ""
				k = bbox_index+1
				while(k < bbox_index+1+len(found_me)):
					mirror_me = mirror_me + ME.pdf_char_list[k]
					k = k + 1

				if(found_me != mirror_me):
					#print("me_reducton called")
					found_me = me_reduction(found_me)
				

				me_size = len(found_me)

				fail_odd_check = 0
				success_flag = 0

				#check_me_cite

				unknown_offset = 0
				if(found_me[0] != me_reduction(ME.pdf_char_list[bbox_index+1])):
					
					'''
						#Another error that needs to be corrected.
						#the bbox_index+1 is one to far
					'''
					if(found_me[0] != me_reduction(ME.pdf_char_list[bbox_index])):
						#print("prev Odd ME found", found_me, me_reduction(ME.pdf_char_list[bbox_index]))
						#print("mm char", ME.pdf_char_list[bbox_index-15:bbox_index+15])
						break
					unknown_offset = 1

				#print("SURVIVED C1")

				me_0 = bbox_index + 1 - fail_odd_check
				me_f = me_0 + me_size
				if(data not in ME.me_with_ss_scripts):
					#This ME does not have ^ or _ to mess up order
					#print("data check", data)
					#print("me_size", me_size)
					pdf_me_data = ME.pdf_char_list[bbox_index+1-unknown_offset:bbox_index+1-unknown_offset+me_size]
					data_mirror = ""
					for char in pdf_me_data:
						data_mirror = data_mirror + char
					if(data != data_mirror):
						#print("data", data)
						#print("data_mirror", data_mirror)
						#print("me char list??", pdf_me_data)
						#print("found me??", found_me)
						break
				#print("SURVIVED C2")
					#print("data mirror", data_mirror)
				# Match found 100%
				ME.me_find_count = ME.me_find_count + 1
				find_flag = 1
				#print("Expected ME box:" , ME.pdf_char_list[me_0:me_f+1])
				#print("found_me", found_me)
				#print("me size", me_size)
				match_check = ""
				x0 = float(ME.char_bbox_list[me_0][0])
				y0 = float(ME.char_bbox_list[me_0][1])
				x1 = float(ME.char_bbox_list[me_0][2])
				y1 = float(ME.char_bbox_list[me_0][3])
				while(me_0 < me_f):
					#print("x0", ME.char_bbox_list[bbox_index+k][0])
					#print("x1", ME.char_bbox_list[bbox_index+k][2])
					if(float(ME.char_bbox_list[me_0][1]) < y0):
						y0 = float(ME.char_bbox_list[me_0][1])

					if(float(ME.char_bbox_list[me_0][3]) > y1):
						y1 = float(ME.char_bbox_list[me_0][3])

					if(float(ME.char_bbox_list[me_0][0]) < x0):
						x0 = float(ME.char_bbox_list[me_0][0])

					if(float(ME.char_bbox_list[me_0][2]) > x1):
						x1 = float(ME.char_bbox_list[me_0][2])
					me_0 = me_0 + 1
				ME.me_bbox_list.append([x0,y0,x1,y1])

				#print("me bbox", [x0,y0,x1,y1])
				break

			bbox_index = bbox_index + 1
		if(find_flag == 0):
			if(index < len(ME.me_post_text)-1):
				locate_post_text(index)
			#print("Failed to find ME prev text", data)
			#print("prev text", ME.me_prev_text[index])
		#if(find_flag == 1):
		#	print("Found ME", data)
		#	print("ME prev text", ME.me_prev_text[index])
			

			#print("\n\n----------------------------------------")
		index = index + 1



		
parse_latex_from_xml("1605.02019")
#correct : afterwords, because this can mess up references if done early
ME.me_static_list = ME.me_list
<<<<<<< HEAD
start = 3
while(start < ME.pages-4):
=======
start = 0
while(start < ME.pages):
>>>>>>> ca08feaff6ab4c1fb135ea9e36d1a53e8b59fc2b
	get_PDFBox_data("1605.02019", start)
	locate_prev_text()
	print("# of me bboxs", len(ME.me_bbox_list))
	if(len(ME.me_bbox_list) < 1):
		ME.no_me_pages[start+1] = origin_file = "destination_" + filename + ".pdf_" + str(start+1) + "_page_" + str(ME.pages) + ".pdf"
	else:
		draw_bbox("1605.02019.pdf_" + str(start+1) +"_page_8", ME.me_bbox_list)
	ME.char_bbox_list = [] 
	ME.me_bbox_list = [] 
	#print ME.pdf_string
	ME.pdf_string = "" 
	ME.pdf_char_list = [] 
	start = start + 1

print("find_count", ME.me_find_count)
print("fail_count", len(ME.me_static_list)-ME.me_find_count)


<<<<<<< HEAD
#merge_pdf(filename)
=======
merge_pdf(filename)
>>>>>>> ca08feaff6ab4c1fb135ea9e36d1a53e8b59fc2b





'''

RANDOM CODE

				tmp_post_text = ""
				if(len(ME.me_post_text[index]) > 3):
					tmp_post_text = ME.me_post_text[index][0:3]
				else:
					tmp_post_text = ME.me_post_text[index]

				tmp_post_text = re.sub('<[^>]+>', '', tmp_post_text)
				tmp_post_text= tmp_post_text.replace(" ", "")
				tmp_post_text = tmp_post_text.replace("(", "parenleft")
				tmp_post_text = tmp_post_text.replace(")", "parenright")
				tmp_post_text = tmp_post_text.replace("-", "hyphen")
				tmp_post_text = tmp_post_text.replace(".", "period")
				tmp_post_text= tmp_post_text.replace(",", "comma")
				tmp_post_text = tmp_post_text.replace("+", "plus")
				print(tmp_post_text)

				j2 = j
				start_index = 0
				rel_index = 0
				flag_index = 0
				post_mcheck = ""
				tmp_mcheck = ""
				while(j2 < len(ME.pdf_char_list)):
					post_mcheck = ME.pdf_char_list[j2]
					#print("FFFFS", tmp_mcheck)
					if(tmp_mcheck == tmp_post_text):
						print("foundzz")
						flag_index = j2-1
						break;
					if(post_mcheck == tmp_post_text[rel_index]):
						start_index = start_index + 1
						rel_index = rel_index + 1
						tmp_mcheck = tmp_mcheck + post_mcheck
					elif(post_mcheck in tmp_post_text):
						char_possible_location = [m.start() for m in re.finditer(post_mcheck, tmp_post_text)]
						i = 0
						tmp_word = tmp_post_text
						match_hits = start_index
						while(i < len(char_possible_location)):
							#match hits is euqal to the location of the first character
							if(char_possible_location[i] != match_hits):
								i = i + 1
								continue
							else:
								if(post_mcheck in tmp_post_text[match_hits:match_hits+len(post_mcheck)+i]):
									curr_match = curr_match + tmp_post_text[match_hits:match_hits+len(post_mcheck)+i]
									match_hits = match_hits + len(post_mcheck)+i
									start_index = start_index + 1
									rel_index = rel_index + len(post_mcheck)
									tmp_mcheck = tmp_mcheck + post_mcheck
									#print("FFFS", tmp_mcheck)
									break
									#print("special curr_match", curr_match)
								elif(post_mcheck in tmp_post_text[match_hits:match_hits+len(post_mcheck)+i-1]):
									curr_match = curr_match + tmp_post_text[match_hits:match_hits+len(post_mcheck)+i-1]
									match_hits = match_hits + len(post_mcheck)+i
									rel_index = rel_index + len(post_mcheck)
									start_index = start_index + 1
									rel_index = rel_index + len(post_mcheck)
									tmp_mcheck = tmp_mcheck + post_mcheck
									break
									#print("special curr_match", curr_match)							
								else:
									start_index = 0
									rel_index = 0
									curr_match = ""
									tmp_mcheck = ""
									break
							i = i + 1
					elif(post_mcheck != tmp_post_text[rel_index]):
						start_index = 0
						post_mcheck = ""
						flag_index = 0
						tmp_mcheck = ""
						rel_index = 0
					j2 = j2 + 1

'''

'''
				unknown_offset = 0
				if(found_me[0] != me_reduction(ME.pdf_char_list[bbox_index+1])):
					
					
						#Another error that needs to be corrected.
						#the bbox_index+1 is one to far
					
					if(found_me[0] != me_reduction(ME.pdf_char_list[bbox_index])):
						print("Odd ME found", found_me)
						print("mm char", ME.pdf_char_list[bbox_index+1])

						break
					unknown_offset = 1

'''