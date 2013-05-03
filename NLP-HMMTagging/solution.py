#! /usr/bin/python

__author__="Stanislaw Jastrzebski <grimghil@gmail.com"
__date__ ="$March 18 2013"

import sys
from collections import defaultdict
import math
from decimal import Decimal
import re

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


class HMMTagger(object):
	def __init__(self):
		self.counts = defaultdict(int)
		self.emissions = defaultdict(float)
		self.transitions = defaultdict(float)


	def calculateWordCounts(self,train_file):
		for corpus in get_iterator_for_corpus_file(train_file):
			if corpus[0]!=None: self.counts[corpus[0]]+=1


	def calculateEmissions(self,count_file):
		counts_tag = defaultdict(int)
		for corpus in get_iterator_for_corpus_file(count_file):
			if corpus[1]=="1-GRAM": counts_tag[corpus[2]] = int(corpus[0])
		count_file.seek(0)
		for corpus in get_iterator_for_corpus_file(count_file):
			if corpus[1]=="WORDTAG": self.emissions[ (corpus[3], corpus[2]) ] = float(corpus[0])/float(counts_tag[corpus[2]])



	def calculateTransitions(self,count_file):
		counts_bigrams = defaultdict(int)
		for corpus in get_iterator_for_corpus_file(count_file):
			if corpus[1]=="2-GRAM": counts_bigrams[(corpus[2],corpus[3])] = int(corpus[0])
		count_file.seek(0)
		for corpus in get_iterator_for_corpus_file(count_file):
			if corpus[1]=="3-GRAM": self.transitions[ (corpus[4], corpus[2],corpus[3]) ] = float(corpus[0])/float(counts_bigrams[(corpus[2],corpus[3])])

	def match_word(self,word):
		if self.counts[word] > 4: return word
		match_numeric = re.match(".*[0-9].*",word)
		if match_numeric is not None and len(match_numeric.group())==len(word):
			return "_NUMERIC_"
		else:
			match_all_caps = re.match("[A-Z]*",word)
			if match_all_caps is not None and len(match_all_caps.group())==len(word):
				return "_ALL_CAPS_"
			else:
				match_last_caps = re.match(".*[A-Z]",word)
				if match_last_caps is not None and len(match_last_caps.group())==len(word):
					return "_LAST_CAP_"

		return "_RARE_"



	def tagFile(self, tag_file, output_file):
		sentence=[]
		sentence_without_rare=[]
		for corpus in get_iterator_for_corpus_file(tag_file):
			if(corpus[0]!=None):
				sentence.append(corpus[0])

			else:
				tags = self.tagSentence(" ".join(sentence))
				for k in range(len(tags)): #tags[k+2] bo pomijam *
					output_file.write(sentence[k]+" "+tags[k][1]+"\n")
				output_file.write("\n")
				sentence=[]

	## tagged_sentence = [ (wyraz, tag) ]
	def getProbability(self, tagged_sentence):
		probability = self.transitions[tagged_sentence[0][1],"*","*"]*self.emissions[tagged_sentence[0][0],tagged_sentence[0][1]]
		if len(tagged_sentence)==1: return probability*self.transitions["STOP","*",tagged_sentence[0][1]]


		probability *= self.transitions[tagged_sentence[1][1],"*",tagged_sentence[0][1]]*self.emissions[tagged_sentence[1][0],tagged_sentence[1][1]]

		for k in range(2,len(tagged_sentence)):
			probability *= self.transitions[(tagged_sentence[k][1],tagged_sentence[k-2][1],tagged_sentence[k-1][1])]*self.emissions[(tagged_sentence[k][0],tagged_sentence[k][1])]
			print self.transitions[(tagged_sentence[k][1],tagged_sentence[k-2][1],tagged_sentence[k-1][1])]
			print self.emissions[(tagged_sentence[k][0],tagged_sentence[k][1])]
			print (tagged_sentence[k][0],tagged_sentence[k][1])

		probability *= self.transitions[("STOP",tagged_sentence[-2][1],tagged_sentence[-1][1])]
		return probability

	def tagSentence(self, sentence):
		pi = defaultdict(float)
		bp = defaultdict(str)
		pi[ (0,"*","*") ] = 1.0

		tags_normal = ["O","I-GENE"]

		tags_pairs_first = [ ("*","I-GENE"), ("*","O") ]
		tags_pairs_normal = [ ("I-GENE","O"),("O","I-GENE"),("I-GENE","I-GENE"),("O","O") ]

		sentence = sentence.split(" ")

		for k in range(len(sentence)):
			sentence[k]=self.match_word(sentence[k])

		#print sentence

		for k in range(1,len(sentence)+1):
			if k==1: tags = tags_pairs_first
			else: tags = tags_pairs_normal

			for tagpair in tags:
				if k<3 : tags_list_previous = ["*"]
				else: tags_list_previous = tags_normal
				#print sentence[k-1]
				#print self.emissions[(sentence[k-1],"I-GENE")]
				#print self.emissions[(sentence[k-1],"O")]
				#sentence[k-1]f poniewaz numeruje k 1...n
				l = [ (lambda t: pi[ (k-1,t,tagpair[0])]*self.emissions[(sentence[k-1],tagpair[1])]*self.transitions[ (tagpair[1],t,tagpair[0])])(t) for t in tags_list_previous ]
				#print l

				pi[ (k,tagpair[0],tagpair[1]) ] = max(l)
				bp[ (k,tagpair[0],tagpair[1]) ] = tags_list_previous[l.index(max(l))]
				#print "pi[{0},{1}]={2},{3}".format(k,tagpair,max(l),tags_list_previous[l.index(max(l))])


		#Pobierz optymalne rozwiazanie (ostatnia linijka Viterbi)
		l = [ (lambda tp: pi[ (len(sentence),tp[0],tp[1]) ]*self.transitions[("STOP",tp[0],tp[1])])(tp) for tp in tags_pairs_normal ]
		#print max(l)
		#print len(sentence)
		#print tags_pairs_normal[l.index(max(l))]



		#Uzyj tablicy backpointerow
		tag0,tag1 = tags_pairs_normal[l.index(max(l))]
		k=len(sentence)
		tagging = [tag0,tag1]
		while (tag0,tag1) != ("*","*"):
			tag0,tag1,k = bp[ (k,tag0,tag1) ], tag0, k-1
			if tag0=="*": break
			tagging.insert(0,tag0)

		tagged_sentence = [ (sentence[k],tagging[k]) for k in range(len(sentence)) ]
		#print tagged_sentence
		#print tagging
		#print self.getProbability(tagged_sentence)


		return tagged_sentence




class SimpleTagger(object):
	def __init__(self, hmm):
		self.hmm = hmm
	def tag(self, count_file, tag_file, output_file):

		tags = ["O","I-GENE"]
		counts = defaultdict(int)
		for corpus in get_iterator_for_corpus_file(count_file):
			if corpus[0]!=None: counts[corpus[0]]+=1


		for corpus in get_iterator_for_corpus_file(tag_file):
			if(corpus[0]!=None):
				if counts[corpus[0]]<5: word = "_RARE_"
				else: word = corpus[0]
				#print counts[corpus[0]]
				f = lambda x: self.hmm.emissions[(word,x)]
				l = [f(t) for t in tags]
				output_file.write("{0} {1}\n".format(corpus[0],tags[l.index(max(l))]))
			else: output_file.write("\n")



def debug_with_key(hmmModel,key_file):
	sentence=[]
	original_tagging=[]
	sentence_without_rare=[]
	for corpus2 in get_iterator_for_corpus_file(key_file):
		corpus = corpus2[0]
		tag = corpus2[1]
		if(corpus!=None):
			if hmmModel.counts[corpus]<5: word = "_RARE_"
			else: word = corpus
			sentence.append(word)
			sentence_without_rare.append(corpus)
			original_tagging.append( (word, tag) )

		else:
			tags = hmmModel.tagSentence(" ".join(sentence))
			#for k in range(len(tags)): #tags[k+2] bo pomijam *
			#	output_file.write(sentence_without_rare[k]+" "+tags[k][1]+"\n")
			#output_file.write("\n")
			sentence=[]
			sentence_without_rare=[]

			if hmmModel.getProbability(tags)<hmmModel.getProbability(original_tagging) :
				print tags
				print original_tagging
				print "{0}<{1}\n".format(hmmModel.getProbability(tags),hmmModel.getProbability(original_tagging))
				if len(tags)<10: return

			#print "{0}=={1}\n".format(hmmModel.getProbability(tags),hmmModel.getProbability(original_tagging))
			original_tagging=[]

if __name__ == "__main__":
	hmmModel = HMMTagger()


	#part2 usage: [zliczone 2,3-gramy i emisje], [plik do otagowania], [plik out], [plik uczacy]
	#part2 usage: [zliczone] [plik uczacy] [plik do otagowania] [plik out]
	hmmModel.calculateEmissions(file(sys.argv[1],"r"))
	hmmModel.calculateTransitions(file(sys.argv[1],"r"))
	hmmModel.calculateWordCounts(file(sys.argv[2],"r"))
	#debug_with_key(hmmModel, file(sys.argv[5],"r"))

	#print hmmModel.tagSentence("A _RARE_ motor domain in a cytoplasmic dynein .")

	#debug sie zgadza
	#print hmmModel.tagSentence("STAT5A mutations in the Src homology 2")
	#debug sie zgadza
	#print hmmModel.tagSentence("More importantly , this fusion converted a less effective vaccine into one with significant potency against established E7 - expressing metastatic tumors .")
	#print hmmModel.tagSentence("Therefore , we suggested that both proteins might belong to the PLTP family .")

	#print hmmModel.tagSentence("We investigate the reaction kinetics of small spherical particles with inertia , obeying coalescence type of reaction , B + B --> B , and being advected by hydrodynamical flows with time - periodic forcing .")
	print hmmModel.tagFile(file(sys.argv[3],"r"),file(sys.argv[4],"w+"))

	#Part 1, usage: gene.counts, [plik do otagowania], [plik out], [plik uczacy (zeby zliczyc county)]
	#simpleTagger = SimpleTagger(hmmModel)
	#simpleTagger.tag(file(sys.argv[4],"r"),file(sys.argv[2],"r"),file(sys.argv[3],"w+"))




