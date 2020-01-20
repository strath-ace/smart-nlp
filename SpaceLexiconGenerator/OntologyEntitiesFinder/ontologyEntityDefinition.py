# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

import matplotlib.pyplot as plt
import numpy as np
import pandas
import re, os
import sys
import statistics
import json
import math
import itertools

from os import listdir
from os.path import isfile, join
from sklearn.feature_extraction.text import TfidfVectorizer
from DEA_methods import *
from operator import itemgetter
from statistics import mean
from nltk import FreqDist
from nltk.collocations import *
from preprocessedCorpora.corpusInsight import corpusInsight

fileDir = os.path.dirname(os.path.abspath(__file__))  #
parentDir = os.path.dirname(fileDir)  # Directory of the Module directory

def ontologyEntityDefinition(inputPath, outputPath):
    '''
    Statistical analysis of the parsed and pre-processed texts to identify concepts (ontology candidate entities)
    specific to input Corpus: Frequency of words + Weirdness Index or tf-idf filtering, comparison with WordNet and ECSS
    glossary of terms and acronyms

    Input: .json files containing preprocessed raw text per corpus element (NLP pipeline outputs)
    Output: a .json file with all identified candidate concepts/entities: 3 lexica, one frequency-based, one frequency-based
    + TF-IDF, and one frequency-based + Weirdness Index
    '''

    fileDir = os.path.dirname(os.path.abspath(__file__))  #
    parentDir = os.path.dirname(fileDir)  # Directory of the Module directory

    # Extract all tokenized sentences from corpus
    for path in inputPath:
        print('Corpus Insight:\n')
        #corpusInsight(path)

        documents = [f for f in listdir(parentDir+path) if isfile(parentDir+path+f)]
        allCorpusTokensPerSentence=[]
        tokensPerDoc=[]

        for d in documents:
            with open(parentDir+path+ d, 'r') as infile:
                input = json.load(infile)
            tokensPerDoc.append(list(itertools.chain(*input)))
            # retrieve tokens per sentence
            for item in input:
                allCorpusTokensPerSentence.append(item)

    # Join tokenized sentences
    allTokens = list(itertools.chain(*allCorpusTokensPerSentence))
    print('Number of documents:', len(tokensPerDoc))
    print('Initial Number of tokens:', len(allTokens))

    # Corpus dictionary
    dic = set(allTokens)
    print('Initial Dictionary Size:', len(dic))

    # Filter out all POS which are not Nouns (NN)
    tags, taggedWords=tagger(dic)
    nouns = [[item[0] for item in taggedWords if item[1] == 'NN']]
    nouns.append([item[0] for item in taggedWords if item[1] == 'NNS'])
    nouns = list(itertools.chain(*nouns))

    # only use nouns for entities identification
    dic=nouns
    numberOfWords = len(dic)

    # only use tokens which are in the dictionary of nouns
    f_tokens=[token for token in allTokens if token in dic]
    print('Number of tokens, after filtering out all non-nouns:', len(f_tokens))
    print('New dictionary size after noun filtering:', numberOfWords)


    # ------------------------------------------------------------------------------------------------------------------
    # Frequency Analysis -----------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # Get all Frequencies per words over all corpus:
    fdist1 = FreqDist(f_tokens)
    allFrequencies = [frequency for (word, frequency) in fdist1.most_common(numberOfWords)]
    allWordsWithFrequency = [[word, frequency] for (word, frequency) in fdist1.most_common(numberOfWords)]

    # Frequency Average
    aveFreq = math.floor(sum(fdist1.values()) / numberOfWords)

    # Set Threshold
    freqThreshold = aveFreq

    # Frequency per word plot
    fig1 = plt.figure()
    plt.plot(sorted(fdist1.values()))
    thresholdCurve = [aveFreq for i in range(numberOfWords)]
    plt.plot(thresholdCurve)
    plt.yticks(np.arange(0, max(fdist1.values()), step=150))
    fig1.suptitle('Corpus Words Frequency-based Dictionary')
    plt.ylabel('Frequency')
    plt.grid()
    plt.xlabel('Index of Corpus Dictionary Words')
    fig1.savefig(parentDir+'/Outputs/Figures/Frequency.png')
    plt.close

    # Count how many values higher or equal to average frequency
    L = len([i for i in fdist1.values() if i >= freqThreshold])

    # ------------------------------------------------------------------------------------------------------------------
    # First filtering of candidate entities based on frequency z-score -------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # standard deviation:
    standardDev = statistics.stdev(allFrequencies)

    # Compute z-scores of all words
    allZscores = []
    wordsZscores = []

    for item in allWordsWithFrequency:
        score = zscore(item[1], standardDev, aveFreq)
        wordsZscores.append([item[0], score])
        allZscores.append(score)

    # Show z-score as histogram
    fig2 = plt.figure()
    plt.hist(allZscores, np.arange(-0.5, 6, 0.25))
    fig2.suptitle('Corpus Words Frequency Z-scores Distribution')
    plt.xlabel('Z-score')
    plt.grid()
    plt.ylabel('Number of words within range')
    fig2.savefig(parentDir + '/Outputs/Figures/FrequencyZscore.png')
    #plt.show()

    # Filter words based on z-score, only z-score >= zscoreThreshold are accepted
    zscoreThreshold = 0
    candidateEntities = [i[0] for i in wordsZscores if i[1] >= zscoreThreshold]

    print('\n---> Frequency Analysis')
    print('Initial Input of Words (dictionary):', numberOfWords)
    print('The average frequency is ', aveFreq, '. There are', L, 'words above the average frequency.')
    print('AfterFrequency Index z-score filtering (threshold of z-score:', zscoreThreshold,
      '), the number of candidate entities is:', len(candidateEntities))

    # ------------------------------------------------------------------------------------------------------------------
    # Option 1: TF-IDF Filtering ---------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    print('\n---> TF-IDF Filtering')
    # For each candidate entity from candidate entities
    allTfIdf = []
    allWords=[word for [word, f] in allWordsWithFrequency ]
    for token in candidateEntities:
        # Get Term frequency
        tf = allWordsWithFrequency[allWords.index(token)][1]

        # Get Term IDF
        df = 0
        for doc in tokensPerDoc:
            if token in doc:
                df=df+1

        idf = math.log10(len(tokensPerDoc)/df)

        # Compute and save TF-IDF
        tfidf = tf*idf
        allTfIdf.append([token, tfidf])

    # Get average TF-IDF
    # get average
    allScores = [item[1] for item in allTfIdf]
    av_tfidf = round(sum(allScores) / len(allScores), 2)

    # select all above average tf-idf, and all with average above tf
    candidateEntities2 = [item for item in allTfIdf if item[1] > av_tfidf and item[0] in candidateEntities]
    candidateEntities2 = sorted(candidateEntities2, reverse=True, key=itemgetter(1))
    print('The average tf-idf is ', av_tfidf, '. There are', len(candidateEntities2), 'words above the average TF-IDF')


    # ------------------------------------------------------------------------------------------------------------------
    # Option 2: Weirdness Indexing Filtering ---------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    print('\n---> Weirdness Index')
    input_weird = candidateEntities

    #candidateEntities3 = weirdnessIndex(candidateEntities, candidateEntitiesWithFreq, len(allTokens))
    fdist1 = FreqDist(input_weird)
    # Get all Frequencies per words:
    allWordsWithFrequency = [[word, frequency] for (word, frequency) in fdist1.most_common(len(input_weird))]
    candidateEntities3 = weirdnessIndex(input_weird, allWordsWithFrequency, len(input_weird))

    # ------------------------------------------------------------------------------------------------------------------
    # RESULTS ----------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    # Compare Original top 15 words before application of weirdness index and last 15

    print('\n ----------------------------------------------')
    print(' Top 10 Frequency Dictionary  ¦ TF-IDF Dictionary ¦  Weirdness Dictionary ')
    print(' ----------------------------------------------')
    for i in range(0, 10):
        print(candidateEntities[i], '  &  ', candidateEntities2[i][0], '  &  ', candidateEntities3[i])

    print('\n ----------------------------------------------')
    print(' Bottom 10 Frequency Dictionary  ¦ TF-IDF Dictionary ¦  Weirdness Dictionary ')
    print(' ----------------------------------------------')
    for i in range(1, 11):
        print(candidateEntities[len(candidateEntities)-i], '  &  ', candidateEntities2[len(candidateEntities2)-i][0], '  &  ', candidateEntities3[len(candidateEntities3)-i])

    # Save Outputs
    outputPath = parentDir+outputPath[0]
    print(outputPath)
    with open(outputPath, 'w') as outfile:
        json.dump({'candidateFreq': candidateEntities, 'candidateTFIDF': candidateEntities2, 'candidateWeird': candidateEntities3}, outfile)
    return

def weirdnessIndex(vocab, vocabWithFrequency, CorpusNumberOfTokens):
    '''
    Application of Weirdness Factor filtering to pre-selected set of candidate entities based on their term frequency
    Input: list of candidate entities after frequency filtering, candidate entities frequencies, total number of tokens
           in pre-processed corpus
    Output: new set of candidate entities with a weirdness index higher than threshold
    '''
    fileDir = os.path.dirname(os.path.abspath(__file__))  #
    parentDir = os.path.dirname(fileDir)  # Directory of the Module directory

    # Load BNC Corpus words frequency pairs ----------------------------------------------------------------------------
    temp = []
    bncfrequency = []

    with open(parentDir + '/AdditionalDocuments/BNCWordFrequency.txt', encoding="utf-8") as inputfile:
        for line in inputfile:
            temp.append(line.strip())  # .split('\t'))
        for item in temp:
            new=item.split(' ¦ ')
            new[1]=int(new[1])
            bncfrequency.append(new)

    # Get BNC number of tokens
    BNCNumberOfTokens = len(bncfrequency)
    print(BNCNumberOfTokens)
    j = 1 # placement of word frequency in file

    # For each tokens (pre-filtered with frequency analysis), find token frequency in the BNC --------------------------
    vocabFrequencyCorpusAndBNC = []

    for i in vocab:
        inBNC = False

        for sublist in bncfrequency:
            if i in sublist:
                inBNC = True
                vocabFrequencyCorpusAndBNC.append([i, vocabWithFrequency[vocab.index(i)][1], sublist[j]])


        if not inBNC:
            vocabFrequencyCorpusAndBNC.append([i, vocabWithFrequency[vocab.index(i)][1], 0])

    # ------------------------------------------------------------------------------------------------------------------
    # Calculate Weirdness Index of each word
    # ------------------------------------------------------------------------------------------------------------------

    # Weirdness Index is defined as "a measure of the use of a word in special language compared to its use in a
    # representative corpus of general language texts", in this case, the BNC

    weird = []
    for line in vocabFrequencyCorpusAndBNC:
        weirdnessFactor = round((BNCNumberOfTokens * line[1]) / ((1 + line[2]) * CorpusNumberOfTokens), 0)
        weird.append([line[0], weirdnessFactor])
    weird_sorted = sorted(weird, reverse=True, key=itemgetter(1))

    # Average Weirdness Index
    averageWeirdness = round(mean([row[1] for row in weird]), 0)

    # Standard Deviation
    Wscores = [score for (word, score) in weird_sorted]
    standardDev = statistics.stdev(Wscores)

    # ------------------------------------------------------------------------------------------------------------------
    # Calculate z-factor of each candidate entity
    # ------------------------------------------------------------------------------------------------------------------
    wordsZscores = []
    for item in weird_sorted:
        score = zscore(item[1], standardDev, averageWeirdness)
        wordsZscores.append([item[0], score])
    Zscores = [score for (word, score) in wordsZscores]

    # Show z-score as histogram
    fig2 = plt.figure()
    plt.hist(Zscores, np.arange(-1, 6, 0.5))
    fig2.suptitle('Corpus Words Weirdness Z-scores Distribution')
    plt.xlabel('Z-score')
    plt.grid()
    plt.ylabel('Number of words within range')
    #plt.show()

    # ------------------------------------------------------------------------------------------------------------------
    # Filter candidate entities based on Weirdness Index z-score
    # ------------------------------------------------------------------------------------------------------------------
    # only z-score >= zscoreThreshold are accepted
    zscoreThreshold = 0
    candidates = [i[0] for i in wordsZscores if i[1] >= zscoreThreshold]

    print('\n---> Weirdness Analysis')
    print('Initial Input of candidate entities:', len(vocab))
    print('After Weirdness Index z-score filtering (threshold of', zscoreThreshold,
          '), the number of candidate entities is:', len(candidates))
    print('The average weirdness is ', averageWeirdness)

    return candidates

