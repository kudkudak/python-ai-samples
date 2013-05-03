#! /usr/bin/python

__author__="Stanislaw Jastrzebski <grimghil@gmail.com"
__date__ ="$May 02 2013"

import copy
import sys
from collections import defaultdict
import codecs


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


class IBMAllignator(object):
    """ Class for predicting allignment, using IBM Model 1 or 2 """
    def __init__(self, algorithm="IBMMODEL1"):
        self.target_sent = [] # list of sentences from the bank
        self.foreign_sent = []
        self.foreign_words = [] # auxilliary list of words from the bank
        self.target_words = []
        self.t = defaultdict(dict) # dict of default dicts for t parameter
        self.cp = defaultdict(float)
        self.count_n = defaultdict(int) # auxilliary for init of self.t
        self.bank_size = 0
        self.algorithm = algorithm

    def loadTrainingData(self, target_file, foreign_file):
        """ Loads given training data target/foreign sentence pairs """
        target_file_iterator = codecs.open(target_file, "r", 'utf-8')
        foreign_file_iterator = codecs.open(foreign_file, "r", 'utf-8')
        for sentence in target_file_iterator:
            self.target_sent.append(sentence.rstrip('\n').split(" "))

        for sentence in foreign_file_iterator:
            self.foreign_sent.append(sentence.rstrip('\n').split(" "))

        max_length_target = 0
        max_length_foreign = 0

        for i in xrange(len(self.target_sent)):
            max_length_target, max_length_foreign = max(max_length_target, len(self.target_sent[i])), max(max_length_foreign, len(self.foreign_sent[i]))
            if "" in self.foreign_sent[i] or "" in self.target_sent[i] :
                del self.foreign_sent[i]
                del self.target_sent[i]
            if i == len(self.target_sent)-1: break

        assert len(self.target_sent) == len(self.foreign_sent), "Reading error"

        self.bank_size = len(self.target_sent)

        print "File reading was successful. Bank of size {self.bank_size} was loaded with maxes : {max_length_target}, {max_length_foreign}".format(**locals())

        ### Initialize t weights aux values ###
        for i in xrange(self.bank_size):
            uniq = len(set(self.foreign_sent[i]))
            for target_word in self.target_sent[i]:
                self.count_n[target_word] += uniq
            self.count_n["NULL"] += uniq


        ### Get lists of possible words in target and foreign language ###
        target_words_dict={}
        foreign_words_dict={}

        for i in xrange(self.bank_size):
            for word in self.target_sent[i]:
                target_words_dict[word] = 1
            for word in self.foreign_sent[i]:
                foreign_words_dict[word] = 1

        self.target_words = [item for item in target_words_dict.iterkeys()]
        self.foreign_words = [item for item in foreign_words_dict.iterkeys()]
        self.target_words.append("NULL")

        ### Take memory only for neccessary t parameters ###
        for i in xrange(self.bank_size):
            for fword in self.foreign_sent[i]:
                for tword in self.target_sent[i]:
                    self.t[fword][tword] = 1.0/self.count_n[tword]
                self.t[fword]["NULL"] = 1.0/self.count_n["NULL"]



        print "Initliazed t-parameters into the memory"

        if self.algorithm == "IBMMODEL1": return

        ### Take memory only for neccessary c parameters ###
        for h in xrange(self.bank_size):
            fsentence = self.foreign_sent[h]
            tsentence = self.target_sent[h]

            for i in xrange(len(tsentence)+1): #0 is null here (different indexes)
                for j in xrange(len(fsentence)):
                    self.cp[ (i,j+1,len(tsentence),len(fsentence)) ] = 1.0/float(len(tsentence)+1)

        print "Initliazed c-parameters into the memory"

    def estimateCParams(self, iter = 5):
        pass

    def estimateTParams(self, iter = 5):
        pass

    def runEM(self, iter = 5):
        """ Estimates t(f|e) using EM algorithm """
        for s in xrange(iter):
            c = defaultdict(float)
            c2 = defaultdict(float)
            print "EM Method -- iteration {s}".format(**locals())
            for k in xrange(self.bank_size):
                if k%100 == 0: print "Sentence pair {k}".format(**locals())
                target_sentence = copy.deepcopy(self.target_sent[k])
                target_sentence.insert(0,"NULL")
                foreign_sentence = self.foreign_sent[k]

                for i in xrange(len(foreign_sentence)):
                    for j in xrange(len(target_sentence)):
                        fword = foreign_sentence[i]
                        tword = target_sentence[j]
                        flen = len(foreign_sentence)
                        tlen = len(target_sentence)-1

                        ### Calculate delta ###
                        if self.algorithm == "IBMMODEL1":
                            delta_sum = 0.0
                            for h in xrange(len(target_sentence)):
                                delta_sum += self.t[fword][target_sentence[h]]
                            delta = (self.t[fword][tword]) / delta_sum

                            c[(tword,fword)] += delta
                            c[(tword)] += delta
                        else:
                            delta_sum = 0.0
                            for h in xrange(len(target_sentence)):
                                delta_sum += self.cp[(h,i+1, tlen, flen)]*self.t[fword][target_sentence[h]]
                            delta = (self.cp[ (j,i+1,tlen,flen)]* (self.t[fword][tword])) / delta_sum
                            c2[(j,i+1,tlen, flen)] += delta
                            c2[(i+1,tlen,flen)] += delta

            ### Update parameter estimations ###
            ### Inefficient but quite high in the loop structure ###
            if self.algorithm == "IBMMODEL1":
                for i in xrange(self.bank_size):
                    for fword in self.foreign_sent[i]:
                        for tword in self.target_sent[i]:
                            self.t[fword][tword] = c[(tword,fword)]/c[(tword)]
                        self.t[fword]["NULL"] = c[("NULL",fword)]/c[("NULL")]

            if self.algorithm == "IBMMODEL2":
                for h in xrange(self.bank_size):
                    fsentence = self.foreign_sent[h]
                    tsentence = self.target_sent[h]

                    for i in xrange(len(tsentence)+1): #0 is null here (different indexes)
                        for j in xrange(len(fsentence)):
                            self.cp[ (i,j+1,len(tsentence),len(fsentence)) ] = c2[(i,j+1,len(tsentence),len(fsentence))]/c2[(j+1,len(tsentence),len(fsentence))]

    def _findAllignmentIBM2(self, sentence_foreign, sentence_target):
        """ Find [a_0 .... a_l-1] allignment foreign ---> target """

        fwords = sentence_foreign.rstrip('\n').split(" ")
        twords = sentence_target.rstrip('\n').split(" ")
        twords.insert(0,"NULL") # Each word can be alligned to the NULL
        a = [1]*len(fwords)
        for j in xrange(len(fwords)):
            # Calculate a_j
            list_temp = [self.t[fwords[j]].get(twords[i],0.0)*self.cp[ (i,j+1,len(twords)-1,len(fwords)) ] for i in xrange(len(twords))]
            a[j] = list_temp.index(max(list_temp))

        return a

    def _findAllignmentIBM1(self, sentence_foreign, sentence_target):
        """ Find [a_0 .... a_l-1] allignment foreign ---> target """

        fwords = sentence_foreign.rstrip('\n').split(" ")
        twords = sentence_target.rstrip('\n').split(" ")
        twords.insert(0,"NULL") # Each word can be alligned to the NULL
        a = [1]*len(fwords)
        for i in xrange(len(fwords)):
            # Calculate a_i
            list_temp = [self.t[fwords[i]].get(tword,0.0) for tword in twords]
            a[i] = list_temp.index(max(list_temp))

        return a

    def findAllignment(self, sentence_foreign, sentence_target):
        if self.algorithm == "IBMMODEL1": return self._findAllignmentIBM1(sentence_foreign, sentence_target)
        else: return self._findAllignmentIBM2(sentence_foreign, sentence_target)


    def writeParameters(self, output_file):
        file_handle = codecs.open(output_file,"w+","utf-8")
        for (fword, fword_dict) in self.t.iteritems():
            for (tword, cond_prob) in fword_dict.iteritems():
                file_handle.write(u"T-PARAMETER {0} {1} {2}\n".format(fword,tword,cond_prob))
        if self.algorithm=="IBMMODEL1": return
        for (tuple_pack,cond_prob) in self.cp.iteritems():
            i,j,l,m = tuple_pack[0], tuple_pack[1], tuple_pack[2], tuple_pack[3]
            file_handle.write(u"C-PARAMETER {0} {1} {2} {3} {4}\n".format(i,j,l,m,cond_prob))


    def loadTParameters(self, parameter_file):
        file_handle = codecs.open(parameter_file,"r","utf-8")
        print "Load parameters"
        for corpus in get_iterator_for_corpus_file(file_handle):
            if corpus[0] == "T-PARAMETER":
                self.t[corpus[1]][corpus[2]] = float(corpus[3])
        file_handle.close()
        print "Parameters loaded successfully"


    def loadCParameters(self, parameter_file):
        file_handle = codecs.open(parameter_file,"r","utf-8")
        print "Load parameters"
        for corpus in get_iterator_for_corpus_file(file_handle):
            if corpus[0] == "C-PARAMETER":
                self.cp[ (int(corpus[1]),int(corpus[2]),int(corpus[3]),int(corpus[4])) ] = float(corpus[5])
        file_handle.close()
        print "Parameters loaded successfully"

def usage():
    sys.stderr.write("""
        Usage : allignator.py [corpuses in target file] [corpuses in foreign file] [output file]
    """)

def question1_calculateParams():
    ibmAllignator = IBMAllignator(algorithm="IBMMODEL1")
    ibmAllignator.loadTrainingData(sys.argv[1],sys.argv[2])
    ibmAllignator.runEM()

    if len(sys.argv)==4:
        ibmAllignator.writeParameters(sys.argv[3])

def question1_calculateAllignments():
    ibmAllignator = IBMAllignator(algorithm="IBMMODEL1")
    ibmAllignator.loadTrainingData(sys.argv[1],sys.argv[2])
    ibmAllignator.loadParameters(sys.argv[3])

    output_file = codecs.open(sys.argv[6],"w+","utf-8")
    fparse_file = codecs.open(sys.argv[5],"r","utf-8")
    tparse_file = codecs.open(sys.argv[4],"r","utf-8")

    line_count = 0


    ### Bufor because codecs class doesnt support readLine method ###
    tsentences, fsentences = [], []
    for sentence in tparse_file: tsentences.append(sentence)
    for sentence in fparse_file: fsentences.append(sentence)

    ### Find allignments ###
    for line_count in xrange(len(tsentences)):
        tsentence, fsentence = tsentences[line_count], fsentences[line_count]
        if tsentence == "" or fsentence == "": continue # skip error lines
        a = ibmAllignator.findAllignment(fsentence, tsentence)
        for i in xrange(len(a)):
            output_file.write("{0} {1} {2}\n".format(line_count + 1, a[i], i + 1)) # NULL in the english sentence

def question2_calculateAllignments():
    ibmAllignator = IBMAllignator(algorithm="IBMMODEL2")
    ibmAllignator.loadTrainingData(sys.argv[1],sys.argv[2])
    ibmAllignator.loadTParameters(sys.argv[3]) # Load t-params
    ibmAllignator.loadCParameters(sys.argv[4]) # Load c-params (alignment params)

    output_file = codecs.open(sys.argv[7],"w+","utf-8")
    fparse_file = codecs.open(sys.argv[6],"r","utf-8")
    tparse_file = codecs.open(sys.argv[5],"r","utf-8")

    line_count = 0


    ### Bufor because codecs class doesnt support readLine method ###
    tsentences, fsentences = [], []
    for sentence in tparse_file: tsentences.append(sentence)
    for sentence in fparse_file: fsentences.append(sentence)

    ### Find allignments ###
    for line_count in xrange(len(tsentences)):
        tsentence, fsentence = tsentences[line_count], fsentences[line_count]
        if tsentence == "" or fsentence == "": continue # skip error lines
        a = ibmAllignator.findAllignment(fsentence, tsentence)
        for i in xrange(len(a)):
            output_file.write("{0} {1} {2}\n".format(line_count + 1, a[i], i + 1)) # NULL in the english sentence


def question2_calculateParams():
    ibmAllignator = IBMAllignator(algorithm="IBMMODEL2")
    ibmAllignator.loadTrainingData(sys.argv[1],sys.argv[2])
    ibmAllignator.loadTParameters(sys.argv[3]) #required for IBMMODEL2
    ibmAllignator.runEM()

    if len(sys.argv)==4:
        ibmAllignator.writeParameters(sys.argv[4])


def main():
#     question2_calculateParams()
    question2_calculateAllignments()

if __name__=="__main__":
    main()
