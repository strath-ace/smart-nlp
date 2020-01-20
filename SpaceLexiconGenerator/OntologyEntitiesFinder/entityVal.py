# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------


import os
import json
import nltk

from nltk.tokenize import word_tokenize
from DEA_methods import *

fileDir = os.path.dirname(os.path.abspath(__file__))  #
parentDir = os.path.dirname(fileDir)  # Directory of the Module directory


def entityVal(entityFinderOutput):
    '''
    Run the validation (comparison to general dictionary (WordNet) and a domain-specific dictionary (ECSS Glossary of Terms and Acronyms)),
    For all three lexica of a corpus (based on frequency only filtering, frequency + TF-IDF filtering and frequency +Weirdness Index filtering)
    Input: lexica to check
    Output: number and percentage of common items in-between lexica to check and WordNet or ECSS Terms/Acronyms
    '''
    # Store all three entities set: based on Frequency only, based on tf-idf, based on weirdness index
    with open(parentDir + entityFinderOutput, 'r') as input:
        candidates = json.load(input)

    # load glossary of terms
    inputFiles = [parentDir + '/NLPPipeline/NLPInputs/ecss_1grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_2grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_3grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_4grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_5grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_6grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_9grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_all_acronyms.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_validated_expansions.txt']

    ecssMultiwords = []

    for file in inputFiles:
        with open(file, 'r') as input:
            words = input.read().split('\n')
            words = [x for x in words if x]
            for w in words:
                ecssMultiwords.append(word_tokenize(w))

    ecssMultiwords = ['_'.join(item) for item in ecssMultiwords]


    # for each run runVal to compare to Wordnet and ECSS glossary
    print('\n ---------- \n Results for Dictionary based on Frequency only')
    cF=candidates['candidateFreq']
    runVal(cF, ecssMultiwords)

    print('\n ---------- \n Results for Dictionary based on Frequency + TF-IDF')
    rTR=candidates['candidateTFIDF']
    cTF=[word for (word, tfidf) in rTR]
    runVal(cTF, ecssMultiwords)

    print('\n ---------- \n Results for Dictionary based on Frequency + Weirdness Index')
    cW=candidates['candidateWeird']
    runVal(cW, ecssMultiwords)

    return


def runVal(entities, ecssMultiwords):
    '''
    Compare a lexicon to a general lexicon (WordNet) and a domain-specific dictionary (ECSS Glossary of Terms and Acronyms)
    Input: lexicon to check
    Output: number and percentage of common items in-between lexicon to check and WordNet or ECSS Terms/Acronyms
    '''

    print('Number of input entities:', len(entities))

    # Comparison with WordNet
    notInWordNet, inWordNet = check_wordNet(entities)
    #print('Comparison to general dictionary:')
    #print('elements of the first dictionary NOT FOUND in Wordnet:', len(notInWordNet), '(', round(len(notInWordNet)/len(entities)*100,1), '%)')
    print('FOUND in Wordnet:', len(inWordNet), '(', round(len(inWordNet)/len(entities)*100,1), '%)')

    # Comparison with ECSS glossary of terms
    notInECSS = []
    inECSS = []
    for i in entities:
        if i not in ecssMultiwords:
            notInECSS.append(i)
        else:
            inECSS.append(i)

    ecssF=[]
    for i in ecssMultiwords:
        if i in entities:
            ecssF.append(i)

    #print('\n Comparison to domain-specific dictionary:')
    #print('elements of the first dictionary NOT FOUND in ECSS glossary of terms:', len(notInECSS), '(', round(len(notInECSS) / len(entities) * 100, 1), '%)')
    print('FOUND in ECSS glossary of terms:', len(inECSS), '(',
          round(len(inECSS) / len(entities) * 100, 1), '%)')
    print('ECSS FOUND in lexicon:', len(ecssF), '(',
          round(len(ecssF) / len(ecssMultiwords) * 100, 1), '%)')
    #print(ecssF)

    return

entityVal('\Outputs\entityFinderOutputs/conceptsIdentificationWikiv1.json')