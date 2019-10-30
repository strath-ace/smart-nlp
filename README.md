# smart-nlp
Strathclyde Mechanical and Aerospace Research Toolboxes for Natural Language Processing

## Available Repositories
* [Topic Modeling](#TopicModeling)

## Topic Modeling
The code stored in this repository was used to generate results presented at the International Astronautical Congress 2019, in Washington DC (USA), in the session on 'Knowledge Management for space activities in the digital era'. The link to the paper,
'The automatic categorisation of space mission requirements for the Design Engineering Assistant' (IAC-19,D5,2,7,x51013), will be provided soon.

**The code presented here allows to train and evaluate unsupervised, supervised and updated LDA models, a common Topic Modeling method, from a wikipedia-based space mission design corpus. The models can be evaluated via the categorisation of space mission requirements, extracted from freely-available European Space Agency mission documents.**
 
The repository includes
* The functions to train an unsupervised, semi-supervised and updated LDA models,
* The functions to perform 5 cross-fold validation to optimise a model topic number,
* A first 'Space Mission Design' wikipedia corpus, the requirements corpus and the Natural Language Processing pipeline used to process them,
* Examples of unsupervised and semi-supervised topics dictionaries, labeled and validated by Human annotators,
* The 'Space' lexical priors, or seed words, used to train the semi-supervised LDA model, validated by Human annotators.
