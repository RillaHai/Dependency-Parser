#!usr/bin/python
# encoding:utf-8
import sys

headlst = []
headdict = {}
input1 = open("test.tran")

for line in input1:
    line = line.strip()
    if line != '':
	n = line.split(":")
	headdict [n[1]] = n[0]
    else:
	headlst.append(headdict)
	headdict = {}
#print headlst
		    
i=0			
with open(sys.argv[1])as fin:
    with open(sys.argv[1]+".predict",'w')as fout:
        for line in fin:
            line = line.strip()
            if line != '':
	        #print i
                lst = line.split("\t")
		#print headlst[i]
		head = headlst[i]
		#print head
		#print lst[6]
		#print lst[0]
		if lst[0] in head:
                    lst[6] = head[lst[0]]
		else:
		    lst[6] = "_"
                print >> fout,'\t'.join(lst)
            else :
	        i+=1
                print >> fout
print "done"
