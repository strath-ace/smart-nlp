# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------
import pip

def install(package):
    pip.main(['install', package])


packages = {    'grakn-client': {'Version': '1.8.0'}, # Python client for Grakn,https://github.com/graknlabs/client-python
                'gensim': {'Version': '3.7.1'}, #doc2vec model training
                'nltk': {'Version': '3.4.5'},  # Tokenization, NLP pipeline
                'sklearn': {'Version': '2.1.1'},  # Model training support
                }

list_packages = []
for k in packages.keys():
    list_packages.append(k)

for package in list_packages:
    print('\nInstalling', package, '...')
    install(package)

print('\n Ready to run!')