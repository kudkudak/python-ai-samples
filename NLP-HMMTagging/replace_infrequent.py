#! /usr/bin/python

__author__="Stanislaw Jastrzebski <grimghil@gmail.com"
__date__ ="$March 18 2013"

import sys
from collections import defaultdict
import math
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



counts = defaultdict(int)

def match_word(count,word):
	if count > 4: return word
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


def	replace_infrequent(original_file, new_file):
	replacements = defaultdict(int)
	for corpus in get_iterator_for_corpus_file(original_file):
		if corpus[0]==None: new_file.write("\n")	
		else:		
			new_file.write("{0} {1}\n".format(match_word(counts[corpus[0]],corpus[0]), corpus[1]))
	print replacements

def calculate_frequencies(corpus_file):
	for corpus in get_iterator_for_corpus_file(corpus_file):
		if corpus[0]!=None:	counts[corpus[0]]+=1

if __name__ == "__main__":
	calculate_frequencies(file(sys.argv[1],"r"))
	replace_infrequent(file(sys.argv[1],"r"),file("gene_freq_p3.train","w+"))

	
