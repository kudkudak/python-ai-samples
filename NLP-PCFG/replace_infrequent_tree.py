#! /usr/bin/python
import sys
import json
from collections import defaultdict


class JSONTreeBank(object):

    def __init__(self):
        self.trees = []
        self.counts_words = defaultdict(int)

    def addJSONTree(self, tree):
        self.trees.append(tree)
        self.calculateJSONTreeCounts(tree)

    def calculateJSONTreeCounts(self, tree):
        if isinstance(tree, basestring): return
        if len(tree) == 3:
            self.calculateJSONTreeCounts(tree[1])
            self.calculateJSONTreeCounts(tree[2])
        if len(tree) == 2:
            self.counts_words[tree[1]]+=1
    def replaceWithinTree(self,tree):
        if isinstance(tree,basestring): return
        if len(tree) == 3:
            self.replaceWithinTree(tree[1])
            self.replaceWithinTree(tree[2])
        elif len(tree) == 2:
            if self.counts_words[ tree[1] ] < 5: tree[1] = "_RARE_"

    def writeCountsToFile(self,file_name):
        file_handle = file(file_name,"w+")
        for (key,value) in self.counts_words.iteritems():
            file_handle.write("{0} WORD {1}\n".format(value,key))

    def replaceRareWords(self):
        for t in self.trees:
            self.replaceWithinTree(t)

def main(input_file,output_file,word_counts_file):
    jsonTreeBank = JSONTreeBank()
    for l in open(input_file):
        t = json.loads(l)
        jsonTreeBank.addJSONTree(t)
    jsonTreeBank.replaceRareWords()
    output_file_handle = file(output_file,"w+")
    for t in jsonTreeBank.trees:
        json.dump(t,output_file_handle)
        output_file_handle.write("\n")
    jsonTreeBank.writeCountsToFile(word_counts_file)


if __name__ == "__main__":
    main(sys.argv[1],sys.argv[2],sys.argv[3])
