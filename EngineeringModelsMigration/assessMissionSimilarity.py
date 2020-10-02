# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
This script is used for case study 2 of the paper:
A.Berquand & A.Riccardi (2020) FROM ENGINEERING MODELS TO KNOWLEDGE GRAPH: DELIVERING NEW
INSIGHTS INTO MODELS. In Proc. SECESA 2020 (Digital)

and is partly based on the doc2vec gensim tutorial
https://radimrehurek.com/gensim/auto_examples/tutorials/run_doc2vec_lee.html#sphx-glr-auto-examples-tutorials-run-
doc2vec-lee-py

The goal is to assess the similarity between the missions loaded into the Grakn KG,
by comparing their requirements. The requirements of each mission are embedded into one representative vector
with a doc2vec model trained on ECSS requirements. The vectors of each requirements sets are then compared with cosine
similarity. The closer the requirements sets, the closer the cosine similarity is to 1.

Pre-requisite:
- For preprocessing, use the NLP_pipeline.py and DEA_methods respectively found on
git smart-nlp/SpaceLexiconGenerator/NLPPipeline/ and smart-nlp/tree/master/SpaceLexiconGenerator
and update import link from line 45. Load the files from smart-nlp/SpaceLexiconGenerator/NLPPipeline/NLPInputs/
Also update relevant filepaths in NLP_Pipeline.py, DEA_methods.py
- Grakn 1.8.0 installed (https://grakn.ai/),
- Grakn Workbase 1.3.0 (https://grakn.ai/),
- Grakn server running,
- Engineering Model Schema EMSchema.gql loaded into a Grakn keyspace (see README)
- Engineering Model(s) has (have) been migrated to KG through migrate_em_json.py

Input: keyspace of populated Grakn KG
Output: Cosine Similarity between embedded (via doc2vec model) set of engineering models' requirements.
'''

import os
import sys
import gensim
import collections
import time
import statistics
import json
sys.path.append("..")


from grakn.client import GraknClient
from NLP_Pipeline import *
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from tqdm import tqdm

# -------------------------------------------------------------
# USER INPUTS
# -------------------------------------------------------------
keyspace_name="mergedmodels3" # Name of Grakn keyspace where the Engineering Models are stored
trainNewModel = 0  # If 1, will train new model model2train  | If 0, will load model model2load
model2train = 'new_model' # Name of Model to be trained when trainNewModel = 1
model2load = 'new_ecssd2v' # Name of Model to be loaded when trainNewModel = 0
doEvaluationNewModel = 0 # To save time, set to O and evaluate your new model with the rqrmt similarity results (Part 3)
# Otherwise set to 1 - Only relevant when trainNewModel = 1.

# -------------------------------------------------------------
# Methods
# -------------------------------------------------------------
def preprocessData(sen, ecssMultiwords, stopset):
        listReplacementMW=[]
        # Tokenize
        tokens = word_tokenize(sen)
        # Trim - remove empty space start/end word
        tokens = [word.strip() for word in tokens]
        # Remove tokens with special characters: /,%
        tokens = [x for x in tokens if not re.findall('/%', x)]
        # Remove Empty tokens
        tokens = [x for x in tokens if x]
        # Replace - by _ to homogenize multi words
        tokens = [token.replace('-', '_') for token in tokens]
        # Normalise Text
        tokens = [w.lower() for w in tokens]
        # Replace multi words
        tokens, listReplacementMW = replaceMultiwords(tokens, listReplacementMW, ecssMultiwords)
        # Remove stopwords + punctuation
        tokens = [w for w in tokens if w not in stopset]

        #if listReplacementMW:
        #        print("MultiWords found:", listReplacementMW)

        return tokens


# -------------------------------------------------------------
# Main
# -------------------------------------------------------------
# Load data for Preprocessing
stopset = stopwords.words('english')
with open("NLPInputs/non_character_words.txt", encoding="utf-8") as Punctuation:
        filterPunctuation = word_tokenize(Punctuation.read())
for i in filterPunctuation:
        stopset.append(i)
acronyms, exp, ecssMultiwords, ecssMultiwordsWithAcronyms = loadAcronymsMW()

# Retrieve all requirements per iteration from Grakn KG through Python Client
importedData=[]
with GraknClient(uri="localhost:48555") as client:
    with client.session(keyspace=keyspace_name) as session:
        # session = communication tunnel to a given keyspace on the running Grakn server.
        with session.transaction().read() as read_transaction:

            print("\n Part I: Grakn Session Opened - Requirement Extraction Initiated:")
            print('-------------------------------- \n')
            # Get all Iterations, Verify not same Top Element
            answer_getIteration = read_transaction.query("match $x isa Iteration; get $x;").get()
            iterations = [parameter.get("x") for parameter in answer_getIteration]
            print(len(iterations), ' Iterations found')

            # for each iteration
            for i in iterations:
                importedRequirements = []
                # Get Iterations Number
                answer_iterationSetup = read_transaction.query(
                    "match $x id " + i.id + "; ($x, $y) isa Reference_iterationSetup; get $y;")
                iterationSetup = [parameter.get("y") for parameter in answer_iterationSetup]
                for item in iterationSetup:
                    for s in item.as_remote(read_transaction).attributes():
                        if s.type().label() == "iterationNumber":
                            iterationNum = s.value()

                # get Top Element
                answer_GetNameElement = read_transaction.query("match $x id " + i.id + "; ($x, $y) isa Reference_topElement; get $y;")
                topElement = [parameter.get("y") for parameter in answer_GetNameElement]
                for el in topElement:
                    for e in el.as_remote(read_transaction).attributes():
                        if e.type().label() == "name":
                            topElement = e.value()

                # Identify All Requirements
                answer_getRequirements = read_transaction.query("match $x id " + i.id + ";  ($x, $y) "
                                                                "isa Containement_requirementsSpecification; "
                                                                "($y, $z) isa Containement_definition; "
                                                                "get $z;").get()
                requirements = [parameter.get("z") for parameter in answer_getRequirements]

                for req in requirements:
                    for r in req.as_remote(read_transaction).attributes():
                        if r.type().label() == "content":
                            importedRequirements.append(r.value())


                answer_getRequirements2 = read_transaction.query("match $x id " + i.id + ";  ($x, $y) "
                                                                                        "isa Containement_requirementsSpecification;"
                                                                                        "($y, $z) isa Containement_requirement;"
                                                                                        "($z, $w) isa Containement_definition; "
                                                                                        "get $w;").get()
                requirements2 = [parameter.get("w") for parameter in answer_getRequirements2]

                for req in requirements2:
                    for r in req.as_remote(read_transaction).attributes():
                        if r.type().label() == "content":
                            importedRequirements.append(r.value())

                importDic = {'Spacecraft': topElement, 'Iteration Number': iterationNum,
                             'Requirements': importedRequirements}
                importedData.append(importDic)

                print(' --> ', len(importedRequirements), ' Requirements found in Iteration Number ', iterationNum, 'of ', topElement, ' spacecraft.')
                print('All requirements extracted from Graph')

# Train or Load a doc2vec model
if trainNewModel:
    start = time.time()
    print("\n Part II: Train New Doc2Vec Model")
    print('-------------------------------- \n')
    # use ECSS Requirements as training data:
    with open('datasets/ECSS_requirements.json') as infile:
        input = json.load(infile)

    if 'content' in input.keys():
        content = (input["content"]).split('\n')  # string

    # Separate Training and Testing Set (80/20%)
    data = [x for x in content if x != '']  # remove empty
    training_set, testing_set = train_test_split(data, test_size=0.2)
    print('Training set size:', len(training_set))
    print('Testing set size:', len(testing_set))

    print("Start of Model training...")
    corpus_training=[TaggedDocument(words=preprocessData(_d, ecssMultiwords, stopset), tags=[i]) for i, _d in enumerate(training_set)]
    model = gensim.models.doc2vec.Doc2Vec(vector_size=300, min_count=1, epochs=400, window=15, dm=0, negative= 5, sample= 1e-5)
    model.build_vocab(corpus_training)
    model.train(corpus_training, total_examples=model.corpus_count, epochs=model.epochs)
    model.save(model2train+".model")
    print("Model", model2train,"Saved")

    # Accuracy Evaluation
    if doEvaluationNewModel == 1:
        print("Model Evaluation 1")
        ranks = []
        for doc_id in tqdm(range(len(corpus_training))):
            inferred_vector = model.infer_vector(corpus_training[doc_id].words)
            sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
            rank = [docid for docid, sim in sims].index(doc_id)
            ranks.append(rank)
        counter = collections.Counter(ranks)
        print(counter)

        print("Model Evaluation 2")
        sims = []
        for doc in tqdm(testing_set):
            cosineSimilarity = model.docvecs.similarity_unseen_docs(model, word_tokenize(doc),
                                                                    word_tokenize(doc), alpha=None,
                                                                    min_alpha=None, steps=None)
            sims.append(cosineSimilarity)
        print('Average Self Similarity for Testing Set:', statistics.mean(sims))
        print('Model trained and evaluated in: ', round((time.time() - start) / 60, 2), 'minutes.')

else:
    print("\nPart II: Load PreTrained Doc2Vec Model")
    print('-------------------------------- \n')
    # Load saved model
    model = Doc2Vec.load( model2load+".model")
    print('Model', model2load, 'loaded')

# Embed requirements sets into representative vectors and compare with cosine similarity
print("\nPart III: Embed Spacecrafts' Requirements Set with Doc2Vec and compare with cosine similarity:")
print('-------------------------------- \n')
for item in importedData:
    req = ''.join(item["Requirements"])
    req1= preprocessData(req, ecssMultiwords, stopset)

    for itemTocompare in importedData:
        reqToCompare = ''.join(itemTocompare["Requirements"])
        req2 = preprocessData(reqToCompare, ecssMultiwords, stopset)
        sim = model.docvecs.similarity_unseen_docs(model, req1, req2, alpha=None, min_alpha=None, steps=None)
        # Results
        print('Similarity between', item["Spacecraft"], item["Iteration Number"], ' and ', itemTocompare["Spacecraft"], itemTocompare["Iteration Number"], ': ', sim)

    print('--------------------------------')

