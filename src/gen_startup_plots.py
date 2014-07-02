import numpy as np
import pylab as plt
import random
import sys
import math
import copy
import pickle

#filename parameters
FOLDER_PREFIX = '../data/'

nfundrounds_acq = pickle.load(open(FOLDER_PREFIX+'nfundrounds_acq','r'))
nfundrounds_ipo = pickle.load(open(FOLDER_PREFIX+'nfundrounds_ipo','r'))
nfundrounds_other = pickle.load(open(FOLDER_PREFIX+'nfundrounds_other','r'))
duration_acq = pickle.load(open(FOLDER_PREFIX+'duration_acq','r'))
duration_ipo = pickle.load(open(FOLDER_PREFIX+'duration_ipo','r'))
fundmonths_acq = pickle.load(open(FOLDER_PREFIX+'fundmonths_acq','r'))
fundmonths_ipo = pickle.load(open(FOLDER_PREFIX+'fundmonths_ipo','r'))
fundmonths_other = pickle.load(open(FOLDER_PREFIX+'fundmonths_other','r'))

### Number of funding rounds of startups ###
f, axarr = plt.subplots(2)
axarr[0].set_title('Number of funding rounds of startups', fontsize=20)
axarr[0].hist([nfundrounds_acq,nfundrounds_ipo,nfundrounds_other],  \
                histtype='bar', color=['chartreuse', 'burlywood', 'crimson'],
                            label=['Acquired', 'IPO', 'Other'])
axarr[0].legend()
axarr[0].set_ylabel('No. of companies')
axarr[1].hist([nfundrounds_acq,nfundrounds_ipo,nfundrounds_other], normed=1, \
                histtype='bar', color=['chartreuse', 'burlywood', 'crimson'],
                            label=['Acquired', 'IPO', 'Other'])
axarr[1].legend()
axarr[1].set_ylim([0,0.6])
axarr[1].set_ylabel('Percentage of companies')
axarr[1].set_xlabel('No. of funding rounds')
plt.savefig(FOLDER_PREFIX+'nfundrounds.pdf', format='PDF')
plt.close()

### Duration of startups before being acquired/IPO ###
f, axarr = plt.subplots(2)
axarr[0].set_title('Duration of startups before being acquired/IPO', fontsize=20)
axarr[0].hist([duration_acq, duration_ipo], \
                histtype='bar', color=['chartreuse', 'burlywood'],
                            label=['Acquired', 'IPO'])
axarr[0].legend()
axarr[0].set_ylabel('No. of companies')
axarr[1].hist([duration_acq, duration_ipo], normed=1, \
                histtype='bar', color=['chartreuse', 'burlywood'],
                            label=['Acquired', 'IPO'])
axarr[1].legend()
axarr[1].set_ylim([0,0.05])
axarr[1].set_ylabel('Percentage of companies')
axarr[1].set_xlabel('No. of months')
plt.savefig(FOLDER_PREFIX+'duration.pdf', format='PDF')
plt.close()

### Startup funding after \'x\' months of being founded ###
f, axarr = plt.subplots(2)
axarr[0].set_title('Startup funding after \'x\' months of being founded', fontsize=20)
axarr[0].hist([fundmonths_acq,fundmonths_ipo,fundmonths_other],  \
                histtype='bar', color=['chartreuse', 'burlywood', 'crimson'],
                            label=['Acquired', 'IPO', 'Other'])
axarr[0].legend()
axarr[0].set_ylabel('No. of companies')
axarr[1].hist([fundmonths_acq,fundmonths_ipo,fundmonths_other], normed=1, \
                histtype='bar', color=['chartreuse', 'burlywood', 'crimson'],
                            label=['Acquired', 'IPO', 'Other'])
axarr[1].legend()
axarr[1].set_ylim([0,0.05])
axarr[1].set_ylabel('Percentage of companies')
axarr[1].set_xlabel('x\'th month after company founded')
plt.savefig(FOLDER_PREFIX+'fundmonths.pdf', format='PDF')
plt.close()

