from urllib2 import Request, urlopen, URLError
import pymongo
import json
import sys
import pickle
from operator import itemgetter
import numpy as np

#filename parameters
IN_FILE_LI_MAPPING = 'companies_li_mapping'
FOLDER_PREFIX = '../data/'
OUT_FILE = 'startup_info'

companies_li_ids = []
dict_ids = {}
nfundrounds_acq, nfundrounds_ipo, nfundrounds_other = [], [], []
duration_acq, duration_ipo = [], []
fundmonths_acq, fundmonths_ipo, fundmonths_other = [], [], []

def get_li_mapping():
    for line in open(FOLDER_PREFIX+IN_FILE_LI_MAPPING).readlines():
	line = line.strip().split('\t')
	for cindex in xrange(len(line)):
	    line[cindex] = line[cindex].strip()
	ckey = tuple([line[0], line[1]])
	if ckey not in dict_ids:
	    dict_ids[ckey] = line[2]

def compute_date_diff(end_year, end_month, start_year, start_month):
    diff_years = (int(end_year)-int(start_year))*12
    diff_months = int(end_month)-int(start_month)
    diff_months += diff_years
    return diff_months

def get_funding_info(doc, founded_year, founded_month):
    fundings = doc['funding_rounds']
    fund_hist, fund_rounds = [], []
    for funding in fundings:
	fund_year, fund_month, fund_amt = 0, 0, 0
	if funding['funded_year']:
	    fund_year = funding['funded_year']
	if funding['funded_month']:
	    fund_month = funding['funded_month']
	if funding['raised_amount']:
	    fund_amt = funding['raised_amount']
	if fund_amt == 0:
	    continue
	nfundmonths = compute_date_diff(fund_year, fund_month, \
					founded_year, founded_month)
	if nfundmonths < 0:
	    nfundmonths = 0
	fund_hist.append(nfundmonths)
	fund_rounds.append([fund_year, fund_month, fund_amt])
    fund_rounds = sorted(fund_rounds, key=itemgetter(0,1), reverse=True)
    return fund_hist, fund_rounds

def check_US_startup(doc):
    offices = doc['offices']
    flag = 0
    for office in offices:
	if office['country_code'] == 'USA':
	    flag = 1
    return flag

def get_last2_fundrounds_info(fund_rounds, founded_year, founded_month):
    fyear_last, fyear_seclast = founded_year, founded_year
    fmonth_last, fmonth_seclast = founded_month, founded_month
    amt_last, amt_seclast = 0, 0
    delta_months, delta_amt = 0, 0
    fund_flag = 0
    if len(fund_rounds) == 1:
	if compute_date_diff(fund_rounds[0][0], fund_rounds[0][1], \
			founded_year, founded_month)>0:
	    if founded_year>=2007:
		fyear_last, fyear_seclast = fund_rounds[0][0], \
						founded_year
		fmonth_last, fmonth_seclast = fund_rounds[0][1], \
						founded_month
		delta_months = compute_date_diff(fund_rounds[0][0], \
					fund_rounds[0][1], \
					founded_year, founded_month)
		delta_amt = fund_rounds[0][2]
		amt_last = fund_rounds[0][2]
		fund_flag = 1
    else:
	if compute_date_diff(fund_rounds[0][0], fund_rounds[0][1], \
			fund_rounds[1][0], fund_rounds[1][1])>0:
	    if founded_year>=2007 and fund_rounds[1][0]>=2007:
		fyear_last, fyear_seclast = fund_rounds[0][0], \
						fund_rounds[1][0]
		fmonth_last, fmonth_seclast = fund_rounds[0][1], \
						fund_rounds[1][1]
		delta_months = compute_date_diff(fund_rounds[0][0], \
					fund_rounds[0][1], \
					fund_rounds[1][0], \
					fund_rounds[1][1])
		delta_amt = fund_rounds[0][2]-fund_rounds[1][2]
		amt_last = fund_rounds[0][2]
		amt_seclast = fund_rounds[1][2]
		fund_flag = 1

    fyear = [fyear_last, fyear_seclast]
    fmonth = [fmonth_last, fmonth_seclast]
    amt = [amt_last, amt_seclast]
    delta = [delta_months, delta_amt]
    return fyear, fmonth, amt, delta, fund_flag

def get_acq_info(ckey, doc, fund_flag, fund_rounds, founded_year, \
					founded_month, fund_hist):
    acquisition = doc['acquisition']
    acq_year = acquisition['acquired_year']
    acq_month = 1
    if acquisition['acquired_month']:
	acq_month = acquisition['acquired_month']
    if ckey in dict_ids and fund_flag:
	nfundrounds_acq.append(len(fund_rounds))
	if acq_year:
	    duration = compute_date_diff(acq_year, acq_month, \
					founded_year, founded_month)
	    if duration < 0:
		duration = 0
	    duration_acq.append(duration)
	fundmonths_acq.extend(fund_hist)

def get_ipo_info(ckey, doc, fund_flag, fund_rounds, founded_year, \
					founded_month, fund_hist):
    ipo = doc['ipo']
    ipo_year = ipo['pub_year']
    ipo_month = 1
    if ipo['pub_month']:
	ipo_month = ipo['pub_month']
    if ckey in dict_ids and fund_flag:
	nfundrounds_ipo.append(len(fund_rounds))
	if ipo_year:
	    duration = compute_date_diff(ipo_year, ipo_month, \
					founded_year, founded_month)
	    if duration < 0:
		duration = 0
	    duration_ipo.append(duration)
	fundmonths_ipo.extend(fund_hist)

def get_other_info(ckey, fund_flag, fund_rounds, founded_year, \
					founded_month, fund_hist):
    if ckey in dict_ids and fund_flag:
	nfundrounds_other.append(len(fund_rounds))
	fundmonths_other.extend(fund_hist)

def main():
    outf = open(FOLDER_PREFIX+OUT_FILE, 'w')
    get_li_mapping()
    client = pymongo.MongoClient()
    db = client.crunch
    cursor = db.company.find()
    count = 0
    for doc in cursor:
	if doc['name'] and doc['permalink'] and doc['founded_year'] \
		    and doc['funding_rounds']: 
		    #and doc['offices']:
	    cname = doc['name'].encode('utf-8').strip()
	    cpermalink = doc['permalink'].encode('utf-8').strip()
	    #if 'hortonworks' in cpermalink or 'mapr' in cpermalink:
		#print cname, cpermalink
		#sys.exit()
	    ckey = tuple([cname, cpermalink])

	    founded_year = doc['founded_year']
	    founded_month = 1
	    if doc['founded_month']:
		founded_month = doc['founded_month']

	    if check_US_startup(doc):
		fund_hist, fund_rounds = get_funding_info(doc, founded_year, \
							founded_month)
		if len(fund_rounds)==0:
		    continue
		fyear, fmonth, amt, delta, fund_flag = \
		    	get_last2_fundrounds_info(fund_rounds, founded_year, \
							    founded_month)
		fyear_last, fyear_seclast = fyear[0], fyear[1]
		fmonth_last, fmonth_seclast = fmonth[0], fmonth[1]
		amt_last, amt_seclast = amt[0], amt[1]
		delta_months, delta_amt = delta[0], delta[1]

		duration = compute_date_diff(fund_rounds[0][0], \
					fund_rounds[0][1], \
                                        founded_year, founded_month)

		#outf format: cid, fmonth_last fyear_last, 
		# 		fmonth_seclast fyear_seclast, 
		#		founded_month founded_year, 
		#		amt_last, delta_amt, sum_amt, 
		#		duration_months, delta_months
		if ckey in dict_ids and fund_flag:
		    outstr = str(dict_ids[ckey])+','+str(fmonth_last)+' '+\
			str(fyear_last)+','+str(fmonth_seclast)+' '+ \
			str(fyear_seclast)+','+str(founded_month)+' '+\
			str(founded_year)+','+str(amt_last)+','+\
			str(delta_amt)+','+\
			str(sum(np.array(fund_rounds)[:,2].tolist()))+','+\
			str(duration)+','+\
			str(delta_months)+'\n'
		    outf.write(outstr)
				
		if doc['acquisition']:
		    get_acq_info(ckey, doc, fund_flag, fund_rounds, \
				founded_year, founded_month, fund_hist)
		elif doc['ipo']:
		    get_ipo_info(ckey, doc, fund_flag, fund_rounds, \
				founded_year, founded_month, fund_hist)
		else:
		    get_other_info(ckey, fund_flag, fund_rounds, \
				founded_year, founded_month, fund_hist)

    pickle.dump(nfundrounds_acq, open(FOLDER_PREFIX+'nfundrounds_acq','w'))
    pickle.dump(nfundrounds_ipo, open(FOLDER_PREFIX+'nfundrounds_ipo','w'))
    pickle.dump(nfundrounds_other, \
			open(FOLDER_PREFIX+'nfundrounds_other','w'))
    pickle.dump(duration_acq, open(FOLDER_PREFIX+'duration_acq','w'))
    pickle.dump(duration_ipo, open(FOLDER_PREFIX+'duration_ipo','w'))
    pickle.dump(fundmonths_acq, open(FOLDER_PREFIX+'fundmonths_acq','w'))
    pickle.dump(fundmonths_ipo, open(FOLDER_PREFIX+'fundmonths_ipo','w'))
    pickle.dump(fundmonths_other, open(FOLDER_PREFIX+'fundmonths_other','w'))
    outf.close()

if __name__ == "__main__":
    main()
