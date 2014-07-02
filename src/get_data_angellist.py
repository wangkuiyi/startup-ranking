from urllib2 import Request, urlopen, URLError
import pymongo
import json
import sys
import pickle

#should probably query startup ids in the range 1-450000
#script performs the following:
# 1) query angellist api for all startup ids in the range 
#    [start_startup_id-startup_ids]
# 2) store document for each startup id in mongodb in the database 'angellist'
#    and the collection 'startups'
# 3) dump visible and hidden startup ids into local files

#mongo client
client = pymongo.MongoClient()
#angellist startup web address
startup_info_link = 'https://api.angel.co/1/startups'
#start id for querying angellist api
start_startup_id = 1
#end id for querying angellist api
end_startup_id = 100

startup_ids = []
startup_ids_hidden = []

"""
gets startup info from angellist and stores startup info in mongodb
"""
def get_startup_info():
    for startup_id in xrange(start_startup_id, end_startup_id+1):
	silink = startup_info_link + '/' + str(startup_id)
	request = Request(silink)
	try:
	    response = urlopen(request)
	    startup_info = response.read()
	    if '"hidden":false' in startup_info:
		startup_info_json = json.loads(startup_info)
		startup_ids.append(startup_id)
	        db = client.angellist
		find_dict = {"id": startup_id}
		if int(db.startups.find(find_dict).count()) == 0:
		    db.startups.insert(startup_info_json)
		else:
		    print startup_id,'already exists in mongodb.'
	    else:
		startup_ids_hidden.append(startup_id)
	except URLError, e:
	    print startup_id,':No startup. Got an error code:', e

#gets startup info from angellist
get_startup_info()

#stores visible and hidden startup ids
pickle.dump(startup_ids, open('startup_ids','w'))
pickle.dump(startup_ids_hidden, open('startup_ids_hidden','w'))

