# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------
import math
import os
import nltk

from scipy.spatial import distance
from nltk.corpus import wordnet as wn
from numpy import dot
from numpy.linalg import norm
from os import listdir
from os.path import isfile, join

'''
---> Methods summary <---

NLP Pipeline methods:
    - tagger: Part-Of-Speech Tagging, with nltk tagger
 
WordNet related methods:
    - check_wordNet: Check how many items from a word list are in WordNet or not
    - findWordNetSynonyms: Returns synonyms of word x by using WordNet database
    
Miscellaneous:
    - cleanPreviousOutputs: clear previous Outputs (only .json files)
    - zscore: compute z-score of parameter (either frequency of weirdness index usually) 

'''

#######################################################################################
# NLP Pipeline methods
#######################################################################################

def tagger(tokens):
    '''
    Part-Of-Speech Tagging, with nltk tagger
    Input: list of tokens to tag
    Outputs: tags per tokens
    '''

    taggedWords = nltk.pos_tag(tokens)

    # Get all tags
    tags = [tag for (word, tag) in taggedWords]
    tag_fd = nltk.FreqDist(tags)

    # Optional
    print('Show distribution of tags for document')
    tag_fd.tabulate()
    #tag_fd.plot()

    return tags, taggedWords


#######################################################################################
# WordNet related methods
#######################################################################################

def check_wordNet(dictionary):
    '''
    DESCRIPTION: Check how many items from a word list are in WordNet or not
    INPUT: list of terms (dictionary) to check
    OUTPUT: list of terms found in WordNet and list of terms not found in WordNet  '''
    notInWordNet = []
    inWordNet = []

    for i in dictionary:
        synonyms = []
        for syn in wn.synsets(i):
            for l in syn.lemmas():
                synonyms.append(l.name())
        if not synonyms:
            notInWordNet.append(i)
        else:
            inWordNet.append(i)
    return notInWordNet, inWordNet

def findWordNetSynonyms(x):
    '''
    DESCRIPTION: Returns synonyms of word x by using WordNet database
    INPUT: term to check
    OUTPUT: list of term's WordNet synonyms  '''
    synonyms = []
    for syn in wn.synsets(x):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return synonyms

#######################################################################################
# Miscellaneous
#######################################################################################
def zscore(input, stdDev, averageInputs):
    '''
    DESCRIPTION: compute z-score
    INPUT: Value of parameter (either frequency of weirdness index) for one item of the population, standard Deviation
    and average of parameter over the whole population
    OUTPUT: z-score value '''
    score = (input - averageInputs)/stdDev
    return score

def cleanPreviousOutputs(targetDirectory):
    '''
    DESCRIPTION: clear previous Outputs (only .json files)
    INPUT: target directory to "clean"
    OUTPUT: target directory empty from .json files '''
    # clear previous Outputs, only remove .json files, e.g., Extracted Text with Tika and NLP Pipeline Outputs
    documents = [f for f in listdir(targetDirectory) if (isfile(join(targetDirectory, f)) and f.endswith('.json'))]
    for d in documents:
        os.remove(targetDirectory+d)
    return

