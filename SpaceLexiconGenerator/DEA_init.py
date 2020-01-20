# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------
# file structured inspired from smart-dog

import pip

def install(package):
    pip.main(['install', package])

DEA_packages = {'gensim': {'Version': '3.7.1'},           # Vector Space Modelling and Topic Modelling
                'inquirer': {'Version': '2.6.3'},           # Allow User interaction
                'matplotlib': {'Version': '3.0.2'},  # Data Visualization
                'nltk': {'Version': '3.4'},             # NLP Module
                'numpy': {'Version': '1.16.4'},
                'pandas': {'Version': '0.24.1'},
                'scikit-learn': {'Version': '0.21.2'},
                'scipy': {'Version': '1.3.0'},
                'sklearn': {'Version': '2.1.1'},          # Topic Modelling Visualization
                'xlrd': {'Version': '1.2.0'},
                'spacy': {'Version': '2.2.2'}                  # Allow Excel support
                }

list_packages = []
for k in DEA_packages.keys():
    list_packages.append(k)

for package in list_packages:
    print('\nInstalling', package, '...')
    install(package)

import nltk
nltk.download('all')

print('\n\n DEA Ontology Generation is now ready to run! ')
print('Select Corpus and run DEA_main.py \n')