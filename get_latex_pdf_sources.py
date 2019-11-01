import os
import requests
from time import sleep, time
'''ASDF AIDS

HEP TH PDF LINK https://arxiv.org/pdf/hep-th/<ID>.pdf
<ID> IS unique to each paper in each section for arxiv

run latex parser as latexml <ID> --xml --destination=<ID>.xml
Store into the loading_dock directory

'''


directory = "hep-th-1992-2003-kddcup"

year_dir_list = []
for filename in os.listdir(directory):
	year_dir_list.append(filename)

#year_dir_list = sorted(year_dir_list, reverse=True)
while(True):
	try:
		for filename in year_dir_list:
			#print filename
			for ID in os.listdir(directory + "/" + filename):
				if(os.path.isdir(str(ID) + "_data")):
					print "ID Exists: " + str(ID)
					continue
				r = requests.get("https://arxiv.org/pdf/hep-th/" + str(ID) + ".pdf", stream=True, headers={'User-agent':'Mozilla/5.0'})
				with open('loading_dock/' + str(ID) + '.pdf', 'wb') as file:
					file.write(r.content)
				print("GOT PDF")
				command = "latexml " + directory + "/" + filename + "/"+ str(ID) + " --xml --quiet --nocomments --destination=loading_dock/" + str(ID) + ".xml"
				os.system(command)
				print("Finished XML")
				command = "python mine_pdf.py " + str(ID)
				os.system(command)
				print("FINISHED MINE PDF")
				command = "python mine_xml.py " + str(ID)
				os.system(command)
				print("FINISHED MINE XML")
				command = "python locate_me.py " + str(ID)
				os.system(command)
				print("FINISHED LOCATE ME")
				command = "python img_creation.py " + str(ID) + "_ground_truth.json"
				#os.system(command)
				print("FINISHED OCR DB UPDATE")
	except:
		sleep(300)
		

