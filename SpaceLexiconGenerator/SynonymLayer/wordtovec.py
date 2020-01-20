# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

import time
import matplotlib.pyplot as plt
import os
import json
import numpy

from gensim.models import Word2Vec
from os import listdir
from os.path import isfile, join
from sklearn.decomposition import PCA

def wordtovec(entityFinderOutputs, preprocessedCorpus, cosTreshold, trainNewModel):
    '''
    Generate word2vec model of corpus + apply similarity metrics (cosine similarity) to find entities
    representing similar concepts

    Input:  list of candidate entities (entity finder output) and cosine similarity threshold
    Output: txt file identifying candidate entities' (from previous step) similar concepts
            (with a cosine similarity above threshold)
    '''

    start = time.time()
    fileDir = os.path.dirname(os.path.abspath(__file__))   #
    parentDir = os.path.dirname(fileDir)                   # Directory of the Module directory

    # get candidate entities + frequency threshold
    with open(parentDir+entityFinderOutputs, 'r') as infile:
        input = json.load(infile)
        candidateEntities = input["candidateFreq"]
    print('All candidate entities loaded - ', len(candidateEntities), ' entities.')

    # import NLP pipeline output
    # preprocess for word2vec input: must be in Line of sentences format
    documents = [f for f in listdir(parentDir+preprocessedCorpus) if isfile(join(parentDir+preprocessedCorpus, f))]
    parsedSentences = []
    print(len(documents), ' corpus documents found')

    for d in documents:
        # open document
        with open(parentDir + preprocessedCorpus + d, 'r') as infile:
            inputDoc = json.load(infile)

        # retrieve tokens per sentence
        for sen in inputDoc:
            parsedSentences.append(sen)

    print('Number of sentences to analyse', len(parsedSentences))

    # word2vec method with Gensim
    # ---> TRAIN A NEW MODEL <---

    if trainNewModel == 1:
        # size: number of dimensions of the embeddings (of the NN), default is 100.
        # window: maximum distance between a target word and words around a target word, default is 5
        # workers: number of partitions during training, default value is 3
        # sg: training algorithm, either 0 for CBOW or 1 for skip gram, default is CBOW
        # hs ({0, 1}, optional) – If 1, hierarchical softmax will be used for model training. If 0, and negative is non-zero, negative sampling will be used.
        # negative (int, optional) – If > 0, negative sampling will be used, the int for negative specifies how many “noise words”
        # should be drawn (usually between 5-20). If set to 0, no negative sampling is used.
        # Assign name to model
        nb_model = 'cbow_ns_bookswiki'
        model = Word2Vec(parsedSentences, min_count=2, size=200, workers=3, window=2, sg=0, hs=0, negative=5)
        model.save(parentDir + "/SynonymLayer/Savedword2vecmodels/word2vec_"+str(nb_model)+".model")
        print('New Model saved')
        print('It took', round((time.time() - start) / 60, 2),'minutes to generate the new model.')

    else:
        # ---> OR LOAD A PRE-TRAINED MODEL <---
        # model 'cbow_ns' = CBOW, negative sampling
        # model 'sg_ns' = skip-gram, negative sampling
        nb_model = 'cbow_ns_bookswiki'
        print(parentDir + "/SynonymLayer/Savedword2vecmodels/word2vec_"+str(nb_model)+".model")
        model = Word2Vec.load(parentDir + "/SynonymLayer/Savedword2vecmodels/word2vec_"+str(nb_model)+".model")
        print('\n Model', nb_model, ' loaded')

    vocabulary = model.wv.vocab

    # ---> Model evaluation <---
    candidateEntities = sorted(candidateEntities)
    print('Reminder, the cosine similarity treshold chosen is:', cosTreshold)

    # For each candidate entity, get top n similar concepts and save into .txt
    allSimilar = [[word, model.wv.most_similar(positive=word, topn=5)] for word in candidateEntities if word in vocabulary]

    aboveSimilar = []
    f = open(parentDir + '/Outputs/synonymLayerOutputs/word2vecOutputs_model'+str(nb_model)+'.txt', mode="w", encoding="utf-8")
    for i in allSimilar:
        above=[]
        for item in i[1]:
            if item[1] >= cosTreshold:
                above.append(item)
        if above:
            aboveSimilar.append([i[0], above])
            f.write('Concept: ' + str(i[0]) + ', Similar Concepts: ' + str(above))
            f.write('\n')
    f.close()

    print(len(aboveSimilar), 'concepts with synonyms above cosine threshold of ', cosTreshold)

    # sort allSimilar based on cosine similarity first closest concept value
    # allSimilar = sorted(allSimilar, reverse=True, key=lambda item: (item[1][0][1]))
    aboveSimilar = sorted(aboveSimilar, reverse=True, key=lambda item: (item[1][0][1]))

    #   ----------------------------------------------------------------------------------------------------------------
    #   Result Visualisation
    #   ----------------------------------------------------------------------------------------------------------------
    # Display top 10 most similar
    print('\nTop most similar concepts:')

    if len(aboveSimilar) >= 15:
        top = aboveSimilar[0:15]
    else:
        top = aboveSimilar[0:len(aboveSimilar)]


    topwords = []
    for item in top:
        print(item[0],':')
        topwords.append(item[0])
        for sub in item[1]:
            topwords.append(sub[0])
            print(sub[0], round(sub[1], 4))
        print('------')

    # PCA visualisation
    X = model[topwords]
    pca = PCA(n_components=2)
    result = pca.fit_transform(X)

    fig2 = plt.figure()
    plt.scatter(result[:, 0], result[:, 1])
    words = list(topwords)
    for i, word in enumerate(words):
        plt.annotate(word, xy=(result[i, 0], result[i, 1]))
    plt.show()
    return

def plotw2c():

    fileDir = os.path.dirname(os.path.abspath(__file__))  #
    parentDir = os.path.dirname(fileDir)  # Directory of the Module directory
    # load model
    model = Word2Vec.load(parentDir + "/SynonymLayer/Savedword2vecmodels/word2vec_sg_ns_bookswiki.model")
    print('Model loaded')

    # plot words of interest

    # Similar
    entities = ['pitch','yaw','roll', 'ka-band', 'c-band', 'ku-band','x-band', 'i/o-boards','processor-boards',
           'ganymede', 'callisto', 'mer', 'spirit', 'mpf', 'curiosity', 'bi-propellant', 'monopropellant', 'hydrazine']

    # PCA visualisation
    X = model[entities]
    pca = PCA(n_components=2)
    result = pca.fit_transform(X)

    fig2 = plt.figure()
    plt.scatter(result[:, 0], result[:, 1])
    words = list(entities)
    for i, word in enumerate(words):
        plt.annotate(word, xy=(result[i, 0], result[i, 1]))
    plt.show()
    plt.savefig(parentDir+'/Outputs/synonymLayerOutputs/pca.png')

    return

#plotw2c()