import sys
from copy import deepcopy
import numpy as np
import pylab as plt
import random
import math
import copy
from copy import deepcopy

#filename parameters
IN_FILE_FOUNDERS = 'startup_founder'
IN_FILE_STARTUP_INFO = 'startup_info'
FOLDER_PREFIX = '../data/'
OUT_FILE_COMP_FOUNDER_MATRIX = 'comp_founder_matrix'
OUT_FILE_LABELS = 'startup_labels'
OUT_FILE_COMPS = 'startup_ids'

#startup info column numbers
COL_DELTA_TIME = 8
COL_DELTA_AMT = 5
COL_TIME = 7
COL_LAST_AMT = 4

dict_comp_founder, dict_founder_comp, dict_comp_info = {}, {}, {}
cids_dataset, labels_dataset = [], []

def read_startup_info():
    for line in open(FOLDER_PREFIX+IN_FILE_STARTUP_INFO):
	line = line.strip().split(',')
	dict_comp_info[int(line[0])] = line

def write_labels():
    outf = open(FOLDER_PREFIX+OUT_FILE_LABELS,'w')
    for cid in cids_dataset:
	if dict_comp_info[cid][COL_TIME] != '0':
	    label = float(dict_comp_info[cid][COL_LAST_AMT])/ \
			float(dict_comp_info[cid][COL_TIME])
	else:
	    label = float(dict_comp_info[cid][COL_LAST_AMT])
	outf.write(str(label)+'\n')
	labels_dataset.append(label)
    outf.close()

def read_founders_file():
    for line in open(FOLDER_PREFIX+IN_FILE_FOUNDERS).readlines():
	line = line.strip().split(',')
	cid, empid, title = int(line[0]), int(line[1]), line[2]

	if cid in dict_comp_founder:
	    dict_comp_founder[cid].append(empid)
	else:
	    dict_comp_founder[cid] = [empid]

	if empid in dict_founder_comp:
	    dict_founder_comp[empid].append(cid)
	else:
	    dict_founder_comp[empid] = [cid]

def gen_labels_plots():
    ltmp = deepcopy(labels_dataset)
    ltmp.sort()
    plt.title('Startup label statistics', fontsize=17)
    plt.ylabel('Last-funding amount/No. of months')
    plt.xlabel('Companies ordered by last-funding/months')
    #plt.ylim([0,10])
    plt.yscale('log')
    plt.plot(range(1,len(ltmp)+1),ltmp)
    plt.savefig(FOLDER_PREFIX+'labels.pdf', format='PDF')
    plt.close()

def gen_founder_plots(freq_founder, freq_comp):
    freq_founder.sort(reverse=True)
    print freq_founder[0]
    freq_comp.sort(reverse=True)
    print freq_comp[0]
    plt.subplot(2, 1, 1)
    plt.title('Comp/founder statistics', fontsize=17)
    plt.legend()
    plt.ylabel('No. of companies')
    plt.xlabel('Founders ordered by no. of comp.')
    plt.ylim([0,10])
    plt.xscale('log')
    plt.plot(range(1,len(freq_founder)+1),freq_founder)
    plt.subplot(2, 1, 2)
    plt.legend()
    plt.ylabel('No. of founders')
    plt.xlabel('Comp. ordered by no. of founders')
    plt.ylim([0,150])
    plt.xscale('log')
    plt.plot(range(1,len(freq_comp)+1),freq_comp)
    plt.tight_layout()
    plt.savefig(FOLDER_PREFIX+'founders.pdf', format='PDF')
    plt.close()

def write_founders_matrix():
    outf1 = open(FOLDER_PREFIX+OUT_FILE_COMP_FOUNDER_MATRIX,'w')
    outf2 = open(FOLDER_PREFIX+OUT_FILE_COMPS,'w')
    global cids_dataset
    cids_dataset = dict_comp_founder.keys()
    cids_dataset.sort()
    for cid in cids_dataset:
	outstr = ''
	for empid in set(dict_comp_founder[cid]):
	    outstr += str(empid)+' '+str(1)+' '
	outstr = outstr.rstrip(' ')
	outf1.write(outstr+'\n')
	outf2.write(str(cid)+'\n')
    outf1.close()
    outf2.close()

def main():
    read_founders_file()
    freq_founder = []
    for empid in dict_founder_comp.keys():
	freq_founder.append(len(set(dict_founder_comp[empid])))
    freq_comp = []
    for cid in dict_comp_founder.keys():
	if len(set(dict_comp_founder[cid]))>25:
	    print cid
	freq_comp.append(len(set(dict_comp_founder[cid])))

    gen_founder_plots(freq_founder, freq_comp)
    write_founders_matrix()
    read_startup_info()
    write_labels()
    gen_labels_plots()

if __name__ == "__main__":
    main()





