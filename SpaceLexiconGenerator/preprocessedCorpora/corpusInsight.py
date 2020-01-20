# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------
import json
import itertools
import os

from os import listdir
from os.path import isfile

def corpusInsight(path):
    '''
    Provides some information on document corpus: number of tokens, average tokens per document/sentence and dictionary
    size
    Input: list of tokenized documents
    '''

    fileDir = os.path.dirname(os.path.abspath(__file__))  #
    parentDir = os.path.dirname(fileDir)  # Directory of the Module directory

    documents = [f for f in listdir(parentDir+ path) if isfile(parentDir+path+f)]

    allTokens = []
    for d in documents:
        with open(parentDir+path +d, 'r') as infile:
               input = json.load(infile)
        allTokens.append(input)
    allTokensPerDoc = list(itertools.chain.from_iterable(allTokens))
    allTokens = list(itertools.chain.from_iterable(allTokensPerDoc))
    print('Number of Documents', len(documents))
    print('Total Number of tokens:', len(allTokens))
    print('Average number of tokens per document:', round(len(allTokens)/len(documents),0))
    dic = list(set(allTokens))
    print('Corpus Dictionary size:', len(dic))

    return
