from pyPdf import PdfFileWriter, PdfFileReader
import sys
import json
import os

class pdf_metadata():
	page_height = 0

def load_pdf_metadata(filename):
	metadata = filename + "_data/pdfbox_output/pdf_metadata.txt"
	#print metadata
	with open(metadata) as fn:

		for line in fn:
			tmp = line.split(",")
			pdf_metadata.page_height = float(tmp[1])
			break

def crop_image(box, pdf_page, filename, count):
	print "BOX"
	print box
	with open(filename + "_data/" + pdf_page, "rb") as in_f:
		input1 = PdfFileReader(in_f)
		output = PdfFileWriter()

		page = input1.getPage(0)

		x0 = float(box[0])
		y0 = pdf_metadata.page_height-float(box[1])
		x1 = float(box[2])
		y1 = pdf_metadata.page_height-float(box[3])

		page.trimBox.lowerLeft = (x0, y1)
		page.trimBox.upperRight = (x1, y0)
		page.cropBox.lowerLeft = (x0, y1)
		page.cropBox.upperRight = (x1, y0)
		output.addPage(page)

		with open("OCR_DATASET/" + filename + "_me_" + str(count), "wb") as out_f:
			output.write(out_f)

def ocr_fullme_to_latex_dataset(json_filename,ocr_type):
	directory = "OCR_DATASET"
	if not os.path.exists(directory):
		os.makedirs(directory)
		#pdf_me_data
	filename = json_filename.split("_ground")
	filename = filename[0]
	load_pdf_metadata(filename)
	directory = filename + "_data/pdfbox_output/"
	DATA_FILENAME = "OCR_DATASET/img_to_latex_mapping.txt"

	with open(directory+json_filename) as file:
		data = json.load(file)

	total_count = 0
	mined_data = data["pdf_me_data"]
	#ocr_full_latex_dataset = []
	count = 0
	
	for page in mined_data:
		if(os.path.isfile(filename + "_data/" + page)):

			latex_list = mined_data[page]["ME_LATEX"]
			bbox_list = mined_data[page]["FULL_BBOX"]
			#local_dataset = []
			me_count = 0
			for box in bbox_list:
				if(box[0] == "FAILED" or box == "FAILED"):
					me_count = me_count + 1
					continue
				#print latex_list[me_count]
				crop_image(box, page, filename,count)
				#local_dataset.append({filename + "_me_" + str(count):latex_list[count]})
				total_count = total_count + 1
				with open(DATA_FILENAME, "a") as ocr_source:
					ocr_source.write(filename + "_me_" + str(count) + "," + latex_list[me_count] + "\n")
				count = count + 1
				me_count = me_count + 1
		else:
			#print "WTF"
			#print page
			continue

				
def main():
	if(len(sys.argv) > 1):
		json_filename = sys.argv[1]
		#ocr_type = sys.argv[2]
		ocr_type = 1 #ignore for now
		ocr_fullme_to_latex_dataset(json_filename,ocr_type)

main()
#ocr_fullme_to_latex_dataset("1605.02019_ground_truth.json",1)