# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
main.py
Semi-automatically extracts a domain-specific lexicon (laying the basis of an ontology) from unstructured data
The results generated with this code were presented in the paper "Space mission design ontology: extraction of
domain-specific entities and concepts similarity analysis" at the 2020 AIAA SciTech Forum in Orlando, USA. Part of
the results might differ as part of the corpus used in the paper could not be made public.

Input: Corpus of parsed documents: 273 wikipedia pages + 40 books (sometimes divided in parts)
Outputs: Generates a domain-specific lexicon ('candidate entities') and similar concepts based on word2vec

Get started :
--> run DEA_init.py to install all necessary packages
--> check path definitions (below)
--> go to "Select Operations" below to choose which blocks of the code to run:
main_public.py is divided in building blocks, implemented building blocks are the following:

1. "Apply_NLP_Pipeline": pre-processing of parsed documents based on a classic NLP pipeline, mostly based on Python
NLTK library. Outputs are saved as .json files, one file per document.
2. "Find_Candidate_Entities": performs statistical analysis of the processed documents to identify candidate entities.
Based on frequency analysis and TF-IDF or Weirdness Index Filtering
3. "Find_Candidate_Entities_Merging": applies word embedding to find similar concepts

To select which building blocks to run, choose True/False in "Select Operations" code below.
For new or modified Corpus (in .pdf, .doc format), a parsing step should be first implemented (suggesting to use
Apache Tika library).

--> run main.py '''

# Modules Importation
from NLPPipeline.NLP_Pipeline import applyNLPPipeline
from OntologyEntitiesFinder.ontologyEntityDefinition import ontologyEntityDefinition
from SynonymLayer.wordtovec import wordtovec
import os

fileDir = os.path.dirname(os.path.abspath(__file__))  #
parentDir = os.path.dirname(fileDir)  # Directory of the Module directory


# Path definitions:
# Location of parsed files, e.g., ./Corpora/Wiki/
NLPPipelineInput = open('./NLPPipeline/paths/NLPInputPathFiles.txt').read().split('\n')
# Location for NLP pipeline outputs, e.g., ./Outputs/NLPOutputs/
NLPOutputPath = open('./NLPPipeline/paths/NLPOutputPath.txt').read().split('\n')
# Location of the lexicon generator (OntologyEntityFinder), files pre-processed with NLP pipeline,
# e.g., /preprocessedCorpora/Wiki/
entityFinderInputs = open('./OntologyEntitiesFinder/paths/entityFinderInput.txt').read().split('\n')
# Location of the lexicon generator (OntologyEntityFinder) outputs,
# e.g., /Outputs/entityFinderOutputs/conceptsIdentificationWikiv1.json
entityFinderOutputs = open('./OntologyEntitiesFinder/paths/entityFinderOutput.txt').read().split('\n')

# #####################################################################################################################
#                                     -->  DEA Ontology Generation <--
# #####################################################################################################################

# ---------------------------------------------------------------------------------------------------------------------
# Select Operations
# ---------------------------------------------------------------------------------------------------------------------
'''
Select which building blocks of the DEA Ontology Generation to run
True = Will run block, and generate new outputs
False = Will not run block and will use previous saved outputs to run next block

Note that the outputs of the NLP Pipeline are saved into ./Outputs/NLPOutputs,
while the path of Find_CandidateEntities might be ./preprocessedCorpora
'''

print('\n ---> Welcome to the DEA Space Lexicon Generator <--- \n')
Apply_NLP_Pipeline = False
Find_Candidate_Entities = False
Find_Candidate_Entities_Merging = True

# ---------------------------------------------------------------------------------------------------------------------
# Step 1: NLP pipeline
# ---------------------------------------------------------------------------------------------------------------------
'''
Pre-processing of parsed text: tokenization, abbreviation expansion, multi words, lemmatization, removal of stop words
Input: .json files containing raw extracted text per corpus element 
Outputs: .json files containing preprocessed raw text per corpus element
'''
if Apply_NLP_Pipeline:
    print('\n <---------------')
    print('Initiating NLP Pipeline')
    applyNLPPipeline(NLPPipelineInput)
    print('\n NLP Pipeline Done')
    print('---------------> \n')

# ---------------------------------------------------------------------------------------------------------------------
# Step 2:  Entities/Concepts Identification - dictionary of words filtered by frequency and Weirdness Index
# ---------------------------------------------------------------------------------------------------------------------
'''
Frequency analysis of the pre-processed texts to identify concepts (ontology candidate entities) 
specific to input Corpus: Frequency of words + Weirdness Index Filtering or tf-idf, comparison with WordNet and ECSS terms
Input: .json files containing preprocessed raw text per corpus element (NLP pipeline outputs)
Output: a .json file with all identified candidate concepts/entities: 3 lexica, one frequency-based, one frequency-based 
+ TF-IDF, and one frequency-based + Weirdness Index 
'''
if Find_Candidate_Entities:
    print('\n <---------------')
    print(' Term Layer: generate domain specific lexica')
    ontologyEntityDefinition(entityFinderInputs, entityFinderOutputs)
    print('\n Term Layer Done')
    print('---------------> \n')

# ---------------------------------------------------------------------------------------------------------------------
# Step 3:  Merging of similar entities: HAL Space or Word2vec + CosineSimilarity
# ---------------------------------------------------------------------------------------------------------------------
'''
Applies word embedding to find similar concepts (merge similar ontology entities, which represent the same concepts)
word2vec + cosine similarity
Input:  - a .json file with all identified candidate concepts/entities [list], frequency threshold used [double]
        and the term frequency associated to each candidate concepts/entities [list]. (Find_candidate_entities Output)
        - the threshold for cosine similarity, cosThreshold, defined below by User. concepts with a cosine similarity 
        below this threshold are not considered similar.
Output: per word embedding method, a txt file identifying candidate entities' (from previous step) similar concepts 
        (with a cosine similarity above threshold)
'''
if Find_Candidate_Entities_Merging:
    # Cosine Similarity Threshold, all below not considered as similar concepts
    cosThreshold = 0.9
    print('Synonyms Layer: merge similar conceps with word2vec embedding and cosine similarity.')
    trainNewModel = 2 # if 1: will train a new model, if 0: load previously saved model
    wordtovec('/Outputs/entityFinderOutputs/conceptsIdentificationBooksWiki.json','/preprocessedCorpora/BooksWiki/', cosThreshold, trainNewModel)
    print('\n Synonym Layer Done')
    print('---------------> \n')
