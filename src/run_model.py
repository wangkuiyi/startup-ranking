import re
import numpy as np
from operator import itemgetter
from copy import deepcopy
import pylab as plt
import sys

#filename parameters
IN_FILE_LABELS = 'startup_labels'
IN_FILE_COMP_FOUNDER_MATRIX = 'comp_founder_matrix'
IN_FILE_FOUNDERS_LDA = 'founder_lda_model'
IN_FILE_COMPS = 'startup_ids'
IN_FILE_COMP_LI_MAPPING = 'companies_li_mapping'
FOLDER_PREFIX = '../data/'

cids, features, labels = [], [], []
dict_founder_topicd = {}
startup_ids, founders = [], []
dict_company_li = {}

def read_company_li_mapping():
    for line in open(FOLDER_PREFIX+IN_FILE_COMP_LI_MAPPING).readlines():
	line = line.strip().split('\t')
	dict_company_li[int(line[2])] = line[0]

def read_features():
    for line in open(FOLDER_PREFIX+IN_FILE_FOUNDERS_LDA).readlines():
	line = line.strip()
	line = re.split('\t| ', line)
	line = [float(item) for item in line]
	dict_founder_topicd[int(line[0])] = line[1:]
	
def read_labels():
    for line in open(FOLDER_PREFIX+IN_FILE_LABELS).readlines():
	line = line.strip()
	labels.append(float(line))	

def read_startup_ids():
    for line in open(FOLDER_PREFIX+IN_FILE_COMPS).readlines():
	line = line.strip()
	startup_ids.append(int(line))	

def read_comp_founder():
    for line in open(FOLDER_PREFIX+IN_FILE_COMP_FOUNDER_MATRIX).readlines():
	line = line.strip().split(' ')
	line = [int(line[i]) for i in xrange(len(line)) if i%2==0]
	founders.append(line)

def construct_features():
    for cindex in xrange(len(startup_ids)):
	fvec = []
	for founderid in founders[cindex]:
	    if not len(fvec):
		fvec = dict_founder_topicd[founderid]
	    else:
		first, second = fvec, dict_founder_topicd[founderid]
		fvec = [x+y for x, y in zip(first, second)]
	features.append(fvec)

def gen_plots(ltmp):
    plt.title('Prediction error statistics', fontsize=17)
    plt.ylabel('Percentage error in prediction')
    plt.xlabel('Companies ordered by prediction error')
    #plt.ylim([0,10])
    plt.yscale('log')
    plt.plot(range(1,len(ltmp)+1),ltmp)
    plt.savefig(FOLDER_PREFIX+'pred_errors.pdf', format='PDF')
    plt.close()

def learn_model():
    from sklearn.svm import SVR
    from sklearn.metrics import mean_squared_error
    from sklearn import linear_model

    #model = SVR(kernel='poly', C=1e3, degree=5)
    #model = SVR(kernel='rbf', C=1e5, gamma=0.1)
    model = linear_model.LinearRegression()
    model = model.fit(features, labels)
    #pred = model.predict(features)
    #mse = mean_squared_error(labels, labels_regr)
    #print('Coefficients: \n', regr.coef_)
    #print("Residual sum of squares: %.2f"
    #  % np.mean((regr.predict(features) - labels) ** 2))
    #print('Variance score: %.2f' % regr.score(features, labels))

    fout = open('out','w')
    pred, pred_err = [], []
    for i in xrange(len(labels)):
	pred_err.append([(model.predict(features[i])-labels[i])/labels[i], \
			startup_ids[i]])
	pred.append([model.predict(features[i]), startup_ids[i]])
    pred_err = sorted(pred_err, key=itemgetter(0))
    pred = sorted(pred, key=itemgetter(0), reverse=True)
    for item in pred:
	fout.write(str(item[0])+' '+dict_company_li[item[1]]+'\n')
    fout.close()
    #for item in pred:
	#if item[0]>= -0.1 and item[0]<= 0.1:
	    #print item[0], dict_company_li[item[1]]
    gen_plots(np.array(pred_err)[:,0].tolist())

def main():
    read_features()
    read_labels()
    read_startup_ids()
    read_comp_founder()
    construct_features()
    read_company_li_mapping()
    learn_model()

if __name__ == "__main__":
    main()
