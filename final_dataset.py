import os
import json

directory = "full_page"

page_dir_list = []
for filename in os.listdir(directory):
	page_dir_list.append(filename)


total_me_count = 0
total_ime_count = 0
total_isfrag_count = 0

max_count = 0

year_dist = [0,0,0,0,0,0,0,0,0,0,0,0]
for filename in page_dir_list:
	if(filename == "me_info.txt"):
		continue
	file_data = filename.split(".pdf")
	if(filename[0:2] == "92"):
		year_dist[0] = year_dist[0] + 1
	elif(filename[0:2] == "93"):
		year_dist[1] = year_dist[1] + 1
	elif(filename[0:2] == "94"):
		year_dist[2] = year_dist[2] + 1
	elif(filename[0:2] == "95"):
		year_dist[3] = year_dist[3] + 1
	elif(filename[0:2] == "96"):
		year_dist[4] = year_dist[4] + 1
	elif(filename[0:2] == "97"):
		year_dist[5] = year_dist[5] + 1
	elif(filename[0:2] == "98"):
		year_dist[6] = year_dist[6] + 1
	elif(filename[0:2] == "99"):
		year_dist[7] = year_dist[7] + 1
	elif(filename[0:2] == "00"):
		year_dist[8] = year_dist[8] + 1
	elif(filename[0:2] == "01"):
		year_dist[9] = year_dist[9] + 1
	elif(filename[0:2] == "02"):
		year_dist[10] = year_dist[10] + 1
	elif(filename[0:2] == "03"):
		year_dist[11] = year_dist[11] + 1
	file_id = file_data[0]
	file_page = file_data[1].split("_")
	file_page = file_page[1]
	json_dir = str(file_id) + "_data" + "/" + "pdfbox_output/" 
	json_dir = json_dir + str(file_id) + "_ground_truth.json"
	with open(json_dir) as jdata:
		data = json.load(jdata)
		data = data['pdf_me_data'][filename]
		local_count = 0
		for p in data['ME_LATEX']:
			total_me_count = total_me_count + 1
			local_count = local_count + 1
		if(local_count > max_count):
			max_count = local_count
			print filename
		for p in data['is_IME']:
			if(p==1):
				total_ime_count = total_ime_count + 1
		for p in data['is_fragment']:

			if(p==1):
				total_isfrag_count = total_isfrag_count + 1

print total_me_count
print total_ime_count
print total_isfrag_count
print max_count
print year_dist
