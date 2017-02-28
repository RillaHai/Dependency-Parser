#!usr/bin/python
# encoding:utf-8
import sys
import os
from liblinearutil import *

class Token(object):
    #represents necessary info in the data
    def __init__(self,line):
        entries = line.strip().split('\t')
        self.id = entries[0]
        self.form = entries[1]
        self.lemma = entries[2]
        self.pos = entries[3]
        self.head = entries[6]
        self.label = entries[7]

def read_conll06_sentence(filestream):
    #read file and return sentences list tokens
    #iterate function returning the data sentence by sentence
    sentence = []
    for line in filestream:
        line = line.strip()
        if line != '':
            sentence.append(Token(line))
        elif sentence != []:
            yield sentence  #stay at the status it calls next when need
            sentence = []
    if sentence != []:
        yield sentence




class State ():
    def __init__(self):
#basic configuration for parser
        self.bufferlist =[] #input buffer
        self.stacklist = []#stack
        self.head = []#integer assigned head
        self.t= []#integer rightmost dependent
        self.golden_arc = []#list for storing goldren arc
        self.parse = {}#storing transition
    def can_left_arc (self):
        if len(self.stacklist)>0 and (self.bufferlist[0],self.stacklist[-1]) in self.golden_arc:
            return True
        else:
            return False

    def do_left_arc(self):
        self.golden_arc.remove((self.bufferlist[0],self.stacklist[-1]))
        self.stacklist.pop(-1)


    def first_buffer_no_children(self):
        for head,_ in self.golden_arc:
            if self.bufferlist[0] == head:
                return False
        return True
    
    def can_right_arc(self):
        if len(self.stacklist)>0 and (self.stacklist[-1],self.bufferlist[0]) in self.golden_arc and self.first_buffer_no_children() :
            return True
        return False

    def do_right_arc(self):
        self.golden_arc.remove((self.stacklist[-1],self.bufferlist[0]) )
        self.bufferlist.pop(0)
        self.bufferlist.insert(0,self.stacklist[-1])
        self.stacklist.pop(-1)

    def do_shift(self):
        self.stacklist.append(self.bufferlist[0])
        self.bufferlist.pop(0)    
		
    def save_transition(self,filename):
        print >> filename, self.t[-1]

class FeatureTable(object):
    def __init__ (self):
        self.featuremap = {}
        self.lablemap = {}#mapping lable to pos
    
    def save_table (self,filename):
        with open (filename,mode='w') as outstream:
            for key, value in self.featuremap.iteritems():
                 print >> outstream, key, value
	    print >> outstream
	    for key, value in self.lablemap.iteritems():
                 print >> outstream, key, value
    
    def load_table (self,filename):
        with open (filename,mode='r') as outstream:
            lablemap = False
	    for line in outstream:
	        line = line.strip()
	        if line == '':
	            lablemap = True
	        else:
	            key,_,value = line.partition(' ')
		    if not lablemap:
		        self.featuremap[key] = int(value)
		    else:
                        self.lablemap[key] = int(value)
				
		        
				 	 
    #register feature if new ,otherwise return index
    #for training scenario
    def register_feature(self,feature):
        if feature not in self.featuremap:
            self.featuremap[feature] = self.numfeatures()
        return self.featuremap[feature]
    
    #map feature to index or return None for unseen feature
    #for testing scenario	
    def map_feature (self,feature):#for test
        return self.featuremap.get(feature,None)
	
    def numfeatures (self):
    #number of pairs
        return len(self.featuremap) 
			
    def register_lable (self, lable):
        if lable not in self.lablemap:
            self.lablemap[lable] = self.numlables()
        return self.lablemap[lable] 	
	
    def map_lable (self,lable):
        return self.lablemap.get(lable,-1)#None
        
    def numlables(self):
        return len(self.lablemap)

    def int2lable (self):
        return {v:k for (k,v)in self.lablemap.items()}
            
#create all feature for a givem token()list of string
def instantiate_feature_templates(stacklist,bufferlist,sentence):
    featurestringlist = []
    bid = int(state.bufferlist[0])-1 if len(state.bufferlist)>1 else 0 
    bid2 = int(state.bufferlist[1])-1 if len(state.bufferlist)>1 else 0 
    bid3 = int(state.bufferlist[2])-1 if len(state.bufferlist)>2 else 0
    bform = sentence[bid].form if bid >= 0 else "ROOT"
    bform2 = sentence[bid2].form if bid2 > 0 else "empty"
    bform3 = sentence[bid3].form if bid3 > 0 else "empty"
    bpos = sentence[bid].pos if bid>= 0 else "root_pos"
    bpos2 = sentence[bid2].pos if bid2 > 0 else "empty"
    bpos3 = sentence[bid3].pos if bid3 > 0 else "empty"
    blabel = sentence[bid].label if bid>= 0 else "root_label"
    blabel2 = sentence[bid2].label if bid2 > 0 else "empty"
    blabel3 = sentence[bid3].label if bid3 > 0 else "empty"
    
    sid = int (state.stacklist[-1])-1  if len(state.stacklist)>0 else -2 #not empty
    #print 'sid: ' ,sid
    sid2 = int (state.stacklist[-2])-1 if len(state.stacklist)>1 else -2 #no second
    #print 'sid2: ' ,sid2
    sform1 = sentence[sid].form if sid >= 0 else "ROOT"
    sform = "empty" if sid == -2 else sform1
    sform3 = sentence[sid2].form if sid2 >=0 else "ROOT"
    sform2 = "empty" if sid2 ==-2  else sform3
    spos1 = sentence[sid].pos if sid >= 0 else "root_pos"
    spos =  "empty" if sid ==-2  else spos1
    spos3 = sentence[sid2].pos if sid2 >=0 else "root_pos"
    spos2 = "empty" if sid2 ==-2  else spos3
    slabel1 = sentence[sid].label if sid>= 0 else "root_label"
    slabel = "empty" if sid ==-2 else slabel1
    slabel3 = sentence[sid2].label if sid2 >= 0 else "root_label"
    slabel2 = "empty" if sid2 ==-2  else slabel3

    distance = (bid+1)-(sid+1)
    
    #tran = state.parse[-1] if len(state.parse)>0 
    #print "tran: ",tran
    #hid = int(tran[0]) if tran[0].isdigit() else -2
    #print "hid: ",hid
    #did = int(tran[1]) if tran[1].isdigit() else -2
    #print "did: ",did
    #hform1 = sentence[hid-1].form if hid > 0 else "ROOT"
    #hform = "shift" if hid==-2 else hform1
    #print "hform:",hform
    #hpos1 = sentence[hid-1].pos if hid>0 else "root-pos"
    #hpos = "shift-pos" if hid==-2 else hpos1
    #print "hpos: ",hpos
    #dform = sentence[did-1].form if did >= 0 else "shift"
    #dpos = sentence[did-1].pos if did>=0 else "shift-pos"
   
    featurestringlist.append('FORM-B1=%s'%bform)
    featurestringlist.append('FORM-B2=%s'%bform2)
    featurestringlist.append('FORM-B3=%s'%bform3)
    featurestringlist.append('FORM-S1=%s'%sform)
    featurestringlist.append('FORM-S2=%s'%sform2)
    featurestringlist.append('POS-B1=%s'%bpos)
    featurestringlist.append('POS-B2=%s'%bpos2)
    featurestringlist.append('POS-B3=%s'%bpos3)
    featurestringlist.append('POS-S1=%s'%spos)
    featurestringlist.append('POS-S2=%s'%spos2)
    #featurestringlist.append('DISTANCE=%s'%distance)
    
    
    #featurestringlist.append('LABEL-B1=%s'%blabel)
    #featurestringlist.append('LABEL-B2=%s'%blabel2)
    #featurestringlist.append('LABEL-B3=%s'%blabel3)
    #featurestringlist.append('LABEL-S1=%s'%slabel)
    #featurestringlist.append('LABEL-S2=%s'%slabel2)
    
    
    
    #featurestringlist.append('FORM-H=%s'%hform)
    #featurestringlist.append('FORM-D=%s'%dform)
    #featurestringlist.append('POS-D=%s'%dpos)
    #featurestringlist.append('POS-H=%s'%hpos)
    #featurestringlist.append('HformDpos=%s%s'%(hform,dpos))
    #featurestringlist.append('HposDform=%s%s'%(hpos,dform))
    #print featurestringlist
    return featurestringlist


def map_to_numbers(stringlist,mapfunc):
    indexvector = []
    for featurestring in stringlist:
        indexvector.append(mapfunc(featurestring))
    indexvector = [ind for ind in indexvector if ind != None]	
    return indexvector
def make_feature_vector (sentence,bufferlist,stacklist,mapfunc):
    stringlist = instantiate_feature_templates(stacklist,bufferlist,sentence)
    indexvector = map_to_numbers(stringlist,mapfunc)
    return indexvector
	
def write_indexvector_to_file(lableindex,indexvector,outputfile):
    print>> outputfile,'%d %s'% (lableindex,' '.join(['%d:1'% (i+1) for i in sorted(indexvector)]))

if __name__ =='__main__':#when import the following won't work
    import argparse 
	
    argpar = argparse.ArgumentParser(description = 'Create feature representation in libsvm format')
    mode = argpar.add_mutually_exclusive_group(required=True)
    mode.add_argument('-t','--train',dest='train',action='store_true',help='run in training mode')
    mode.add_argument('-p','--predict',dest='predict',action='store_true',help='run in test mode')
    argpar.add_argument('-i','--input',dest='inputfile',required=True,help='the file containing training/test data')
    argpar.add_argument('-o','--output',dest='outputfile',required=True,help='the file that the feature representation is written to')
    argpar.add_argument('-f','--featmap',dest='featmapfile',required=True,help='the file from which to read or from which to write the feature')

    args = argpar.parse_args()

    feattable = FeatureTable()
    instream = open(args.inputfile)
    outstream = open(args.outputfile,mode='w')





    #testtran = open("test.tran","w")
     #training case
     #fill feature table and learn about new feature
    if args.train:
        for sentence in read_conll06_sentence(instream):
            state = State()
            state.stacklist=["0"]
            state.t = [] #transition list
            for token in sentence:
                state.golden_arc.append((token.head,token.id))
                state.bufferlist.append(token.id)
            
            while state.stacklist != []:
                #print 'buffer:', state.bufferlist
                #print 'stack:', state.stacklist 
                if state.can_left_arc():
	            indexvector = make_feature_vector(sentence,state.stacklist,state.bufferlist,feattable.register_feature) #register features
                    lableindex = feattable.register_lable("LeftArc") #register label
	            write_indexvector_to_file(lableindex,indexvector,outstream)
                    state.do_left_arc() #change stack & buffer
                elif state.can_right_arc():
	            indexvector = make_feature_vector(sentence,state.stacklist,state.bufferlist,feattable.register_feature)
                    lableindex = feattable.register_lable("RightArc")
	            write_indexvector_to_file(lableindex,indexvector,outstream)
                    state.do_right_arc()
                else:
	            indexvector = make_feature_vector(sentence,state.stacklist,state.bufferlist,feattable.register_feature)
                    lableindex = feattable.register_lable("Shift")
	            write_indexvector_to_file(lableindex,indexvector,outstream)
                    state.do_shift()
             
	feattable.save_table(args.featmapfile)
        
        #liblinear train
        y, x = svm_read_problem('train.libsvm')
        print "get feature"
        m = train(y, x)
        print "get model"
        save_model('libtrain.model', m)
        print "model saved"

    elif args.predict:
        m = load_model('libtrain.model')
    	feattable.load_table(args.featmapfile)
        p=0
    	for sentence in read_conll06_sentence(instream):
	    state = State()
	    state.stacklist=["0"]
    	    state.t = []
            p=p+1
            print p
	    for token in sentence:
	        state.bufferlist.append(token.id)
            while state.stacklist != []:
		state.parse = {}
		features = {}#store mapped feature
		labels = []#store mapped lable
		flist = []
		#print state.bufferlist
		#print state.stacklist
		indexvector = make_feature_vector(sentence,state.stacklist,state.bufferlist,feattable.map_feature)
		indexvector = [(i+1) for i in sorted(indexvector)]
		lableindex = feattable.map_lable("ToBePredict")
		for i in indexvector:
		    features[i]=1
		labels.append(lableindex)
		flist.append(features)
		
                # liblinear prediction
    	  	p_label, p_acc, p_val = predict(labels,flist, m)
		p_label = p_label[0] 
		features ={}#empty storage
		labels=[]
		flist = []
    	  	int2lable = feattable.int2lable()
    	  	predictlabel = int2lable.get(int(p_label))
    	  	if predictlabel == "LeftArc":
		    #print "LeftArc"
                    state.golden_arc.append((state.bufferlist[0],state.stacklist[-1]))
		    print >> outstream, "%d:%d"%(int(state.bufferlist[0]),int(state.stacklist[-1]))
		    state.do_left_arc()
		elif predictlabel == "RightArc":
		    #print "RightArc"
                    state.golden_arc.append((state.stacklist[-1],state.bufferlist[0]))
	            print >> outstream, "%d:%d"%(int(state.stacklist[-1]),int(state.bufferlist[0]))
    	  	    state.do_right_arc()
		elif predictlabel == "Shift":
		    #print "Shift"
    	  	    state.do_shift()
	    print >> outstream
       
   
