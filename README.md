# smart-nlp
Strathclyde Mechanical and Aerospace Research Toolboxes for Natural Language Processing

## Available Repositories
* [Space Lexicon Generator](#SpaceLexiconGenerator)
* [Topic Modeling](#TopicModeling)

## Space Lexicon Generator
The code stored in this repository was used to generate the results of the paper "Space mission design ontology: extraction of
domain-specific entities and concepts similarity analysis", presented at the 2020 AIAA SciTech Forum in Orlando, USA in the Invited Session on Cognitive Assistants. The paper is available on [researchgate](https://www.researchgate.net/publication/338400758_Space_mission_design_ontology_extraction_of_domain-specific_entities_and_concepts_similarity_analysis).

**The code allows to automatically extract a domain-specific lexicon from a domain-specific corpus, in this case, the corpus is related to space mission design. The lexicon items are embedded with word2vec and similar concepts are identified with cosine similarity.**

## Topic Modeling
The code stored in this repository was used to generate results presented at the International Astronautical Congress 2019, in Washington DC (USA), in the session on 'Knowledge Management for space activities in the digital era'. The original paper 'The automatic categorisation of space mission requirements for the Design Engineering Assistant' (IAC-19,D5,2,7,x51013) is available on [researchgate](https://www.researchgate.net/publication/337256904_The_automatic_categorisation_of_space_mission_requirements_for_the_Design_Engineering_Assistant).

**The code allows to train and evaluate unsupervised, supervised and updated LDA models, a common Topic Modeling method, from a wikipedia-based space mission design corpus. The models can be evaluated via the categorisation of space mission requirements, extracted from freely-available European Space Agency mission documents.**
 
The repository includes
* The functions to train an unsupervised, semi-supervised and updated LDA models,
* The functions to perform 5 cross-fold validation to optimise a model topic number,
* A first 'Space Mission Design' wikipedia corpus, the requirements corpus and the Natural Language Processing pipeline used to process them,
* Examples of unsupervised and semi-supervised topics dictionaries, labeled and validated by Human annotators,
* The 'Space' lexical priors, or seed words, used to train the semi-supervised LDA model, validated by Human annotators.
