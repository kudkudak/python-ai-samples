#! /usr/bin/python

__author__="Stanislaw Jastrzebski <grimghil@gmail.com"
__date__ ="$March 31 2013"

import sys
from collections import defaultdict
import json


def get_iterator_for_corpus_file(corpus_file):
    l = corpus_file.readline()
    while l:
        line = l.strip()
        if line: # Nonempty line
            fields = line.split(" ")
            yield tuple(field for field in fields)
        else: # Empty line
            yield (None,None)
        l = corpus_file.readline()

class PCFGParser(object):

    def __init__(self):
        self.counts_words = defaultdict(int)
        self.counts = defaultdict(int)
        self.q = {} #defaultdict(float)
        self.nonterminals=[]
        self.binaryrules=[]

    def readCountsWords(self,file):
        for corpus in get_iterator_for_corpus_file(file):
            self.counts_words[corpus[2]] = int(corpus[0])

    def readCounts(self,file):
        for corpus in get_iterator_for_corpus_file(file):
            if corpus[1]=="NONTERMINAL":
                self.counts[(corpus[2])] = int(corpus[0])
                self.nonterminals.append(corpus[2])
        file.seek(0)
        for corpus in get_iterator_for_corpus_file(file):
            if corpus[1]=="BINARYRULE":
                self.q[(corpus[2],corpus[3],corpus[4])] = float(corpus[0])/float(self.counts[(corpus[2])])
                self.binaryrules.append( (corpus[2],corpus[3],corpus[4]))
            elif corpus[1]=="UNARYRULE":
                self.q[(corpus[2],corpus[3])] = float(corpus[0])/float(self.counts[(corpus[2])])


    def _getTreeList(self, bp, i, j, X):
        if i==j: return [X, bp[(i,i,X)][1]] #last level unary rule
        return [X, self._getTreeList(bp, i, bp[(i,j,X)][1],bp[(i,j,X)][0][1]),\
self._getTreeList(bp, bp[(i,j,X)][1]+1, j, bp[(i,j,X)][0][2])]

    def parseCKY(self, sentence):
        sentence = sentence.replace("\n","")
        sentence = sentence.split(" ")
        sentence_tmp = [ ("_RARE_" if self.counts_words[word]<5 else word) for word in sentence]

        sentence.insert(0,None) # dummy insert
        sentence_tmp.insert(0,None)

        sentence_tmp,sentence = sentence,sentence_tmp


        n = len(sentence)-1
        pi = defaultdict(float)
        bp = {}
        print "Parsing {sentence}".format(**locals())
        for i in xrange(1,n+1):
            for X in self.nonterminals:
                if self.q.get( (X, sentence[i]),0.0 )!=0.0:
                    pi[ (i,i,X) ] = self.q.get( (X, sentence[i]),0.0 )
                    bp[ (i,i,X) ] = (pi[ (i,i,X)], sentence_tmp[i]) #without _RARE_ tag
                    print "pi[ {0},{1},{2} ] = {3}".format(i,i,X,pi[ (i,i,X)])


        for l in xrange(1,n-1+1):  #length of the subtree
            print "=========length={l}=========\n".format(**locals())
            for i in xrange(1,n-l+1): #starting point
                j = i+l
                for X in self.nonterminals:

                    def max_s(rule):
                        lista = [(lambda s: self.q[rule]*pi.get((i,s,rule[1]),0.0)*pi.get((s+1,j,rule[2]),0.0))(s) for s in xrange(i,j-1+1)]
                        if all( [ x==0.0 for x in lista] ) : return (None,None)
                        return (max(lista), i+lista.index(max(lista))) if len(lista)!=0 else (None,None)

                    lista=[]

                    for r in self.binaryrules:
                        if r[0]==X:
                            result = max_s(r)
                            if result!=(None,None): lista.append((result,r))

                    if len(lista)==0: continue

                    pi[ (i,j,X) ] = max(lista)[0][0]
                    bp[ (i,j,X) ] = (lista[lista.index(max(lista))][1],max(lista)[0][1])
        print "Probability = {0}".format(pi[(1,n,"SBARQ")])
        return (pi[(1,n,"SBARQ")],self._getTreeList(bp,1,n,"SBARQ"))

def usage():
    sys.stderr.write("""
        Usage: solution.py [count file] [count words file] [text to parse]
    """)

def main():
    pcfgParser = PCFGParser()
    pcfgParser.readCounts(file(sys.argv[1],"r"))
    pcfgParser.readCountsWords(file(sys.argv[2],"r"))
    output_file_handle = file(sys.argv[4],"w+")
    counter = 0
    for sentence in open(sys.argv[3]):
        counter += 1
        print "Parsing {0} sentence".format(counter)
        sentence2 = raw_input()
        prob,treeList = pcfgParser.parseCKY(sentence2)
        print treeList
        output_file_handle.write(json.dumps(treeList)+"\n")

if __name__=="__main__":
    main()
