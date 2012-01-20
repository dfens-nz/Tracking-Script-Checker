#!/usr/bin/python

import urllib
import zipfile
import tempfile
import json
import re
import datetime
from multiprocessing import Pool

number_subprocesses=2
number_hosts=10000
ghostery_list_url="http://www.ghostery.com/update/all?format=json"
alexa_url="http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
alexa_filename='top-1m.csv'


def process_host(line):
    host=line.split(',')[1].strip()
    host_id=int(line.split(',')[0])
    url='http://'+host
    print url
    try:
        u=urllib.urlopen(url)
        html=reduce(lambda x,y: x+y,u.readlines())
    except Exception, E:
        print "Error retrieving %s - %s" % (url,str(E))
        return None
    g_matches=[]
    for pattern_name in ghostery_dict.keys():
        if ghostery_dict[pattern_name].search(html)!=None:
            g_matches.append(pattern_name)
    return {"rank":host_id,"host":host,"tracking-scripts":g_matches}

try:
    ghostery_file=urllib.urlopen(ghostery_list_url)
except Exception:
    ghostery_file=open("ghostery-bugs.json")
ghostery_json=reduce(lambda x,y: x+y,ghostery_file.readlines())
ghostery_list=json.loads(ghostery_json)

ghostery_dict=dict()
for item in ghostery_list["bugs"]:
    try:
        pattern=re.compile(item['pattern'])
    except Exception:
        print("Can't compile pattern for %s" % item['name'])
        continue
    ghostery_dict[item['name']]=pattern


temp=tempfile.TemporaryFile()
urllib.urlretrieve(alexa_url,temp.name)
z=zipfile.ZipFile(temp.name, 'r')
print z.namelist()
z.extract(alexa_filename)

alexa_file=open(alexa_filename,'r')
alexa_list=[]
for i in range(number_hosts):
    alexa_list.append(alexa_file.readline())
alexa_file.close()

start_processing_time=datetime.datetime.now()

if number_subprocesses>0:
    pool = Pool(processes=number_subprocesses)
    results= pool.map(process_host, alexa_list)
else:
    results=[]
    for item in alexa_list:
        results.append(process_host(item))
print ("Proccessing time: "+str(datetime.datetime.now() - start_processing_time))

result_file=open('results.json','w')
result_file.write(json.dumps(results, sort_keys=True, indent=2))
result_file.close()
print("\nWrote file: results.json")

