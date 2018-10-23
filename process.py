import os, sqlite3, datetime, re
from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint

def test_regex(bibl_info):
	pattern = re.compile('(.+) \((.+)\); (.+) Vol. (.+), Iss. (.+),\s+\((.+)\): (.+).')
	result = pattern.search(metadata)
	if result is not None:
		return({
			'publication': result[1],
			'vol': result[4],
			'issue': result[5],
			'date': result[6],
			'pages': result[7]
		})
	else:
		#print("Could not decode metadata:",metadata)
		return({
			'publication': None,
			'vol': None,
			'issue': None,
			'date': None,
			'pages': None
		})
		
def check_ad(title):
	if(" ad " in title.lower()) is True:
		return(True)
	elif(title[0:2].lower()=="ad"):
		return(True)
	else:
		return(False)


search_result_directory =		"search_results"
stopfiles = 					['.DS_Store']
savefile_csv =					"results.csv"
remove_duplicates = 			True

files = [f for f in os.listdir(search_result_directory) if os.path.isfile(os.path.join(search_result_directory, f))]
files = [x for x in files if x not in stopfiles]

i=1
insert_info = []

for file in files:
	with open(search_result_directory+"/"+file) as f:
		content = f.read()
		soup = BeautifulSoup(content,'lxml')
		search_query = soup.find("textarea", {"id": "searchTerm"}).text.lstrip()
		print("Processing file "+str(i)+" of "+str(len(files))+". Search query is '"+search_query+".' Results so far: "+str(len(insert_info)))
		results = soup.find_all("li", {"class": "resultItem"})

		for r in results:

			# get title
			if r.find("a", {"class": "previewTitle"}) is not None:
				title = r.find("a", {"class": "previewTitle"}).text
			else:
				title = None

			# get fulltext link
			if r.find("a", {"class": "format_fulltext"}) is not None:
				link_details = r.find("a", {"class": "format_fulltext"})
				link_details = link_details['href']
				link_details = link_details.split("/")
				fulltext_link = "/"+link_details[3]+"/"+link_details[4]+"/"+link_details[5]+"/"+link_details[6]+"/"+link_details[7]+"/"+link_details[8]
			else:
				fulltext_link = None

			# get pdf link
			if r.find("a", {"class": "format_pdf"}) is not None:
				link_details = r.find("a", {"class": "format_pdf"})
				link_details = link_details['href']
				link_details = link_details.split("/")
				fulltext_pdf = "/"+link_details[3]+"/"+link_details[4]+"/"+link_details[5]+"/"+link_details[6]+"/"+link_details[7]+"/"+link_details[8]
			else:
				fulltext_pdf = None

			#get all metadata
			if r.find_all("span", {"class": "titleAuthorETC"}) is not None:
				metadata = r.find_all("span", {"class": "titleAuthorETC"})
				if(len(metadata)==1):
					metadata = metadata[0].text.replace(u'\xa0', u' ')
					info = test_regex(metadata)
					author = None
				elif(len(metadata)==2):
					author = metadata[0].text.strip()
					metadata = metadata[1].text.replace(u'\xa0', u' ')
					info = test_regex(metadata)
			else:
				info = {
					'publication': None,
					'issue': None,
					'vol': None,
					'date': None,
					'pages': None
				}
			
			#add to array
			insert_info.append({
				'author': author,
				'publication': info['publication'],
				'full_date': info['date'],
				'vol': info['vol'],
				'issue': info['issue'],
				'title':str(title),
				'pages':info['pages'],
				'link_details':str(fulltext_link),
				'link_pdf':str(fulltext_pdf),
				'search_query':str(search_query),
				'ad':check_ad(title)
			})
	i+=1

df = pd.DataFrame.from_dict(insert_info)

print("Total results:"+str(len(df)))
#remove duplicates
if (remove_duplicates is True):
	df.drop_duplicates(inplace=True)

print("Total results (after duplicates removed):"+str(len(df)))

savefile_csv = savefile_csv.split(".")
savefile_csv[0] = savefile_csv[0] + "_" + str(datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S'))
savefile_csv = savefile_csv[0]+"."+savefile_csv[1]

df.to_csv(savefile_csv)