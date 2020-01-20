# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
NLPpipeline.py is a Space NLP pipeline, based on a basic NLP NLTK pipeline with
'space mission design' additional steps: expansion of acronyms and multi words
identification based on ECSS glossary of terms and acronyms.

Sources:
https://ecss.nl/home/ecss-glossary-terms/
https://ecss.nl/home/ecss-glossary-abbreviations/
'''

import pandas
import json
import re
import os
import itertools


from DEA_methods import *
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import WordNetLemmatizer
from collections import Counter
from os import listdir
from os.path import isfile, join

fileDir = os.path.dirname(os.path.abspath(__file__))  #
parentDir = os.path.dirname(fileDir)  # Directory of the Module directory

# ----------------------------------------------------------------------------------------------------------------------
#                                                 NLP METHODS
# ----------------------------------------------------------------------------------------------------------------------
def acronymExpansion(tokens, listReplacements, acronyms, exp):
    '''
    Search for acronyms within tokens, expand if acronyms are found
    Input: tokens, listReplacements: list all replacements done so far within the document
    Outputs: tokens with expanded acronyms when applicable, new replacements done added to list
    '''

    for word in acronyms:
        if word in tokens:
            # Replace by acronym expansion
            expansionToUse = exp[acronyms.index(word)]
            tokens[tokens.index(word)] = expansionToUse
            listReplacements.append(word)
    return tokens, listReplacements

def replaceMultiwords(tokens, listReplacements, ecssMultiwords):
    '''
    Find all multiwords in a list of tokens
    the multiwords list is based on the ECSS glossary and on the additional multiwords found in the Wiki corpus
    Input: list of tokens, listReplacements: list all replacements done so far within the document
    Output: new list of tokens including multiwords, new replacements done added to list
    '''

    #----------------------------------------------------------------------------------
    #                  USING ECSS GLOSSARY & ADDITIONAL VALIDATED TERMS
    #----------------------------------------------------------------------------------

    # Find and replace within corpus:
    for word in ecssMultiwords:
        # Look if an ecss multiword can be found in the tokens
        if word[0] in tokens:
            i = 1
            wordIndex = tokens.index(word[0])
            if wordIndex != len(tokens) - 1 and len(word) != 1:
                while i <= len(word)-1:
                    if word[i] == tokens[wordIndex+i] and wordIndex + i < len(tokens)-1:
                        ecssWords = True
                        i = i + 1
                    else:
                        ecssWords = False
                        break

                # If a multiword has been found, replace within tokens
                if ecssWords == True:
                    tokens = replacementAction(word, tokens)
                    listReplacements.append('_'.join(word))

    return tokens, listReplacements

def replacementAction(multiword, tokens):
    '''
    Replace tokens in a list of tokens by the equivalent multi word,
    provided the multi word is known to be within the tokens list

    Input: multi word, list of tokens
    Output: new list of tokens where the tokens of interest have been replaced by the multi word
    '''
    new_token = '_'.join(multiword)
    wordIndex = tokens.index(multiword[0])
    tokens[wordIndex] = new_token
    indices = []
    for item in multiword[1:len(multiword)]:
        indices.append(tokens.index(item))
    tokens = [v for i, v in enumerate(tokens) if i not in indices]
    return tokens

def tf_idf(tokensPerDoc):
    '''
    Generates the tf-idf ranking of each corpus dictionary item, used to filter out words with lowest tf-idf
    Input: tokens
    Outputs: .txt file with tf-idf ranking per words, starting from lowest tf-idf
    '''

    # tfidf needs a list of sentences, one sentence = one document
    vectorizer = TfidfVectorizer()
    tfidf_vectorizer_vectors = vectorizer.fit_transform(tokensPerDoc)

    terms = vectorizer.get_feature_names()
    sums = tfidf_vectorizer_vectors.sum(axis=0)

    data = []
    for col, term in enumerate(terms):
        data.append((term, sums[0, col]))

    pandas.set_option('display.max_rows', 4000)
    ranking = pandas.DataFrame(data, columns=['term', 'rank'])
    ranked = ranking.sort_values('rank', ascending=True)

    with open(parentDir + '/NLPPipeline/NLPInputs/corpusTFIDFAnalysis.txt', 'w', encoding="utf-8") as f:
        f.write(ranked.to_string(header=True, index=False))

    onlyTerms=ranked.loc[:, "term"]
    with open(parentDir + '/NLPPipeline/NLPInputs/newStopwords.txt', 'w', encoding="utf-8") as f:
        f.write(onlyTerms.to_string(header=True, index=False))
    return

def NLPPipeline(docName, path, acronyms, exp, ecssMultiwords):
    '''
    Application of NLP pipeline
    Input: path to file text
    Outputs: list of pre-processed tokens, divided by sentences, and file name
    '''

    # Import Stop Words
    with open(parentDir+"/NLPPipeline/NLPInputs/non_character_words.txt", encoding="utf-8") as Punctuation:
        filterPunctuation = word_tokenize(Punctuation.read())

    # Common words
    with open(parentDir+"/NLPPipeline/NLPInputs/common_words.txt", encoding="utf-8") as CommonWords:
        filterCommonWords = word_tokenize(CommonWords.read())

    # Manually validate extra common words -specific to study corpora
    with open(parentDir + "/NLPPipeline/NLPInputs/corpora_common_words.txt", encoding="utf-8") as CommonWords:
        filterAdditional = word_tokenize(CommonWords.read())

    stopset = stopwords.words('english')

    for i in filterPunctuation:
        stopset.append(i)

    for i in filterCommonWords:
        stopset.append(i)

    for i in filterAdditional:
        stopset.append(i)

    # Load file
    with open(parentDir+path + docName, 'r') as infile:
        input = json.load(infile)

    # Divide text into sentences
    sentences = (input["content"]).split('\n')  # string
    sentences = [x for x in sentences if x != '']  # remove empty lines
    sentences = [re.split(r'[.?!]\s*', x) for x in sentences]  # separate sentences based on punctuation
    filtered = []

    for s in sentences:
        for i in s:
            if i:
                filtered.append(i)

    sentences = filtered

    # Process each sentence
    tokenPerSentence = []
    listReplacementMW=[]
    listReplacementAcc=[]

    print('number of sentences to analyse:', len(sentences))
    for sen in sentences:

        # Tokenize
        tokens = word_tokenize(sen)

        # Trim
        tokens = [word.strip() for word in tokens]

        # Remove tokens that are only numbers
        tokens = [x for x in tokens if re.findall('[a-zA-Z]', x)]

        # Remove tokens mixing characters and numbers
        tokens = [x for x in tokens if not re.findall('[0-9]', x)]

        # Remove urls
        tokens = [re.sub(r'www.*[\r\n]*', '', token) for token in tokens]

        # Remove non English/number characters:
        tokens = [re.sub('[^A-Za-z0-9_\-/]+', '', token) for token in tokens]

        # Remove Empty tokens
        tokens = [x for x in tokens if x]

        # Replace acronyms
        tokens, listReplacementAcc = acronymExpansion(tokens, listReplacementAcc, acronyms, exp)

        # Normalise Text
        tokens = [w.lower() for w in tokens]

        # Replace multi words
        tokens, listReplacementMW = replaceMultiwords(tokens, listReplacementMW, ecssMultiwords)

        # Remove stopwords + punctuation
        tokens = [w for w in tokens if w not in stopset]

        # Lemmatization - currently based on wordnet
        wnl = WordNetLemmatizer()
        tokens = [wnl.lemmatize(word) for word in tokens]

        # Remove stopwords + punctuation
        tokens = [w for w in tokens if w not in stopset]

        # Remove very short tokens
        tokens = [x for x in tokens if len(x) > 2]

        # Tokens Output
        if tokens:
            tokenPerSentence.append(tokens)

    # ------------------------------------------------------------------------------
    # Save Pre-processed Text
    # ------------------------------------------------------------------------------

    # Get name file
    regex_name = '([\w])'
    name_file = re.findall(regex_name, docName)
    name_file = "".join(name_file)

    return tokenPerSentence, name_file, listReplacementMW, listReplacementAcc

# ----------------------------------------------------------------------------------------------------------------------
#                                                 NLP Pipeline main
# ----------------------------------------------------------------------------------------------------------------------

def applyNLPPipeline(inputPath):
    '''
    Pre-processing of parsed text
    Input: .json files containing parsed text per corpus element
    Outputs: .json files containing preprocessed text per corpus element
    '''

    fileDir = os.path.dirname(os.path.abspath(__file__))  #
    parentDir = os.path.dirname(fileDir)  # Directory of the Module directory

    # clear previous raw text extraction Outputs
    targetDirectory = parentDir + "/Outputs/NLPOutputs/"
    cleanPreviousOutputs(targetDirectory)

    # Load acronyms list, manually defined and validated
    acronymsList = []
    with open(parentDir + '/NLPPipeline/NLPInputs/acronyms.txt', 'r',
              encoding="utf-8") as inputFile:
        acLine = inputFile.read().split('\n')
        for line in acLine:
            if line:
                acronymsList.append(line.split(' | '))
    acronyms = [x[0] for x in acronymsList]
    expansions = [word_tokenize(x[1]) for x in acronymsList]
    exp= []
    for item in expansions:
        item = ' '.join(item)
        item = item.replace("-", "_")
        item = item.replace(" ", "_")
        exp.append(item)

    # Load multiwords
    # Get ECSS multiwords + additional validated terms
    inputFiles = [parentDir + '/NLPPipeline/NLPInputs/ecss_2grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_3grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_4grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_5grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_6grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/ecss_9grams.txt',
                  parentDir + '/NLPPipeline/NLPInputs/spacemissiondesign_ngrams.txt']
    ecssMultiwords = []
    for file in inputFiles:
        with open(file, 'r') as input:
            words = input.read().split('\n')
            words = [x for x in words if x]
            for w in words:
                ecssMultiwords.append(word_tokenize(w))

    # To store list of multi words and acronyms found in the processed corpus
    replacementListMW=[]
    replacementListAcc=[]

    # Extract file names
    for path in inputPath:
        documents = [f for f in listdir(parentDir+path) if isfile(join(parentDir+path, f))]

        # Apply NLP pipeline to each document
        allTokens=[]

        c = 1
        print('doc number', len(documents))
        for eachDoc in documents:
            print('\n ------- \n Applying NLP Pipeline to doc number', c,':', eachDoc)
            tokensPerDocument, name_file, MW, Acc = NLPPipeline(eachDoc, path, acronyms, exp, ecssMultiwords)
            replacementListMW.append(MW)
            replacementListAcc.append(Acc)
            # Save Preprocessed text as .json file, one per document
            with open(parentDir+'/Outputs/NLPOutputs/'+str(name_file)+'_AfterNLPPipeline.json','w') as outfile:
                json.dump(tokensPerDocument, outfile)

            tokensPerDocument=list(itertools.chain.from_iterable(tokensPerDocument))
            allTokens.append(' '.join(tokensPerDocument))
            c=c+1

    # Summary of NLP processing per document:
    replacementListMW=list(itertools.chain.from_iterable(replacementListMW))
    replacementListAcc=list(itertools.chain.from_iterable(replacementListAcc))
    countAcc=Counter(replacementListAcc)
    countMW=Counter(replacementListMW)
    print('Multi Words replaced in document:', Counter(replacementListMW))
    print('Acronyms replaced in document:', Counter(replacementListAcc))

    #Save in text document
    with open(parentDir+'/Outputs/foundMW.txt', 'w') as f:
        for key, value in countMW.items():
            f.write(str(key) + ':' + str(value) +'\n')

    with open(parentDir+'/Outputs/foundAcronyms.txt', 'w') as f:
        for key, value in countAcc.items():
            f.write(str(key) + ':' + str(value) +'\n')

    # Optional - perform tf-idf analysis to rank low informative words and manually add them to stop word list
    #tf_idf(allTokens)

    return

