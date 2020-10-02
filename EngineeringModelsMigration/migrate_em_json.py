# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
Based on Grakn Python client tutorial https://dev.grakn.ai/docs/client-api/python,
this code provides a pipeline for loading any ECSS-E-TM-10-25A Engineering Models .json export from RHEA CDP4 or OCDT
into a Grakn Knowledge Graph

Pre-requisite:
- Grakn 1.8.0 installed (https://grakn.ai/),
- Grakn Workbase 1.3.0 (https://grakn.ai/),
- Grakn server running,
- Engineering Model Schema EMSchema.gql loaded into a Grakn keyspace (see README)

Input: set of .json files to migrate - one set per Engineering Model, this code must be run each time
you wish to migrate one Engineering Model to the KG.

Output: Populated Grakn KG
'''

import sys, os
import ijson
import json
import time

from grakn.client import GraknClient
from migrationTemplates import *
from collections import Counter
from tqdm import tqdm

# --------------------------
# Methods
# --------------------------
def build_engineering_model_graph(inputs, data_path, keyspace_name):

    """
    Commit new instances to Grakn KG
    Connects to Grakn keyspace and generate insert queries

    :param inputs: .json files containing all data on one Engineering Model
    :param data_path: file path of .json files
    :param keyspace_name: keyspace of KG based on EMSchema and where the data is migrated
    """
    with GraknClient(uri="localhost:48555") as client:
        with client.session(keyspace=keyspace_name) as session:
            # session = communication tunnel to a given keyspace on the running Grakn server.
            # Init json file containing all relationships
            init = {'relationship': [], 'role1': [], 'class1': [], 'player1': [], 'role2': [], 'class2': [],
                    'player2': []}
            with open('tempRelationships.json', 'w') as file:
                json.dump(init, file)

            # Insert all entities with their attributes, identify entities's roles and relationship partners
            i=0
            for input in inputs:
                input["file"] = input["file"].replace(data_path[i], "")
                input["file"] = data_path[i] + input["file"]
                print('------------------------------')
                print("Loading from [" + input["file"] + ".json] into Grakn ...")
                load_data_into_grakn(input, session)
                i=i+1

            # Insert all relationships
            load_relationships_into_grakn(session)

def commitRelationships(session, file):
    '''
    Insert relationships to Grakn keyspace

    :param session: running Grakn session where data is being migrated
    :param file: .json file storing information on relationships
    '''

    # Load data contained in tempRelationships.json
    with open(file, 'r') as infile:
        input = json.load(infile)
        relationship=input["relationship"]
        role1=input["role1"]
        class1=input["class1"]
        player1=input["player1"]
        role2=input["role2"]
        class2=input["class2"]
        player2=input["player2"]

    #write insert query for each relationship
    for idx in tqdm(range(len(relationship))):
        # match player 1
        graql_insert_query = 'match $player1 isa '+ class1[idx]+', has iid "' + player1[idx] + '";'
        # match player 2
        graql_insert_query += ' $player2 isa '+ class2[idx]+', has iid "' + player2[idx] + '";'
        # write insert relationship query
        graql_insert_query += " insert ("+role1[idx]+": $player1, "+role2[idx]+": $player2) isa "+relationship[idx]+";"
        # commit query
        with session.transaction().write() as transaction:
            transaction.query(graql_insert_query)
            transaction.commit()
    return

def load_relationships_into_grakn(session):
    """
    Provides an overview of detected relationships, before inserting them into Grakn KG
    :param session: running Grakn session where data is being migrated
    """
    #  Relationships
    with open('tempRelationships.json', 'r') as infile:
        input = json.load(infile)
    print("\n --------------------------------------------------------- ")
    print("Detection of", len(input["relationship"]), "relationships:")
    counter = Counter(input["relationship"])
    for key, value in counter.most_common():
        print(' | ', key, ' | ', value)
    print("Insertion of Relationships: Start...")
    commitRelationships(session, 'tempRelationships.json')
    print("Insertion of Relationships: Success!")
    return

def load_data_into_grakn(input, session):
    '''
      loads the entities and attributes data into our Grakn keyspace:
      for each item dictionary:
        a. creates a Grakn transaction
        b. constructs the corresponding Graql insert query
        c. runs the query
        d. commits the transaction

      :param input: .json file containing the classes and classes' data to parse and migrate
      :param session: running Grakn session where data is being migrated
    '''

    items = parse_data_to_dictionaries(input)
    classK=[]
    for item in items:
        classK.append(item["classKind"])

    #Print summary of classes/entities found in .json file, to migrate
    print(len(classK), ' Classes to migrate, of', len(list(set(classK))), 'different types:')
    print(*list(set(classK)), sep='\n')
    print('------------------------------')

    listAvailableTemplates = [x for x in Templates.keys()]
    classItems=[]

    # For each item, identify class and call corresponding template from 'migrationTemplates.py'
    for item in tqdm(items):
        classItems.append(item["classKind"])
        if item["classKind"] in listAvailableTemplates:
            with session.transaction().write() as transaction:
                graql_insert_query = Templates[item["classKind"]](item)
                #print("Executing Graql Query", graql_insert_query)
                transaction.query(graql_insert_query)
                transaction.commit()
        else:
            # if the template for this class has not been found (should not happen)
            print('--> Template for class ', item["classKind"], ' Missing!\n --------------\n ')

    #Print summary
    print("\n --------------------------------------------------------- ")
    print("\nInserted " + str(len(items)) + " items from [ " + input["file"] + ".json] into Grakn.\n")
    counter = Counter(classItems)
    for key, value in counter.most_common():
        print(' | ', key, ' | ', value)

    return

def parse_data_to_dictionaries(input):
    '''
    Collect each element (= class/entity element) of the .json file
    :param input: path to the data file, minus the format
    :returns items as list of dictionaries: each item representing a data item from the input file
    '''
    items = []
    with open(input["file"] + ".json", encoding='utf-8') as data:
        for item in ijson.items(data, "item"):
            items.append(item)
    return items

# --------------------------
# Main
# --------------------------
# Templates functions stored in migrationTemplates.py
Templates= {"ElementDefinition": elementDefinition_template,
            "ElementUsage": elementUsage_template,
            "Parameter": Parameter_template,
            "ParameterValueSet": ParameterValueSet_template,
            "Iteration": Iteration_template,
            "DomainFileStore": domainFileStore_template,
            "Option": Option_template,
            "Publication": Publication_template,
            "ParameterGroup": ParameterGroup_template,
            "Definition": Definition_template,
            "ParameterSubscription": ParameterSubscription_template,
            "ParameterSubscriptionValueSet": ParameterSubscriptionValueSet_template,
            "RequirementsSpecification": RequirementsSpecification_template,
            "HyperLink": HyperLink_template,
            "Category": Category_template,
            "TextParameterType": TextParameterType_template,
            "ParameterTypeComponent": ParameterTypeComponent_template,
            "ReferenceSource": ReferenceSource_template,
            "BooleanParameterType": BooleanParameterType_template,
            "BinaryRelationshipRule": BinaryRelationshipRule_template,
            "Alias": Alias_template,
            "RatioScale": RatioScale_template,
            "ArrayParameterType": ArrayParameterType_template,
            "LinearConversionUnit": LinearConversionUnit_template,
            "PrefixedUnit": PrefixedUnit_template,
            "Glossary": Glossary_template,
            "LogarithmicScale": LogarithmicScale_template,
            "DerivedUnit": DerivedUnit_template,
            "ScaleReferenceQuantityValue": ScaleReferenceQuantityValue_template,
            "UnitFactor": UnitFactor_template,
            "OrdinalScale": OrdinalScale_template,
            "DateTimeParameterType": DateTimeParameterType_template,
            "Term": Term_template,
            "TimeOfDayParameterType": TimeOfDayParameterType_template,
            "QuantityKindFactor": QuantityKindFactor_template,
            "ScaleValueDefinition": ScaleValueDefinition_template,
            "FileType": FileType_template,
            "EnumerationParameterType": EnumerationParameterType_template,
            "UnitPrefix": UnitPrefix_template,
            "Constant": Constant_template,
            "DateParameterType": DateParameterType_template,
            "IntervalScale": IntervalScale_template,
            "CyclicRatioScale": CyclicRatioScale_template,
            "EnumerationValueDefinition": EnumerationValueDefinition_template,
            "Citation": Citation_template,
            "DecompositionRule": DecompositionRule_template,
            "CompoundParameterType": CompoundParameterType_template,
            "MappingToReferenceScale": MappingToReferenceScale_template,
            "DerivedQuantityKind": DerivedQuantityKind_template,
            "ParameterizedCategoryRule": ParameterizedCategoryRule_template,
            "SpecializedQuantityKind": SpecializedQuantityKind_template,
            "SimpleUnit": SimpleUnit_template,
            "SimpleQuantityKind": SimpleQuantityKind_template,
            "SiteDirectory": SiteDirectory_template,
            "SiteReferenceDataLibrary": SiteReferenceDataLibrary_template,
            "Person": Person_template,
            "ModelReferenceDataLibrary": ModelReferenceDataLibrary_template,
            "EmailAddress": EmailAddress_template,
            "DomainOfExpertise": DomainOfExpertise_template,
            "EngineeringModelSetup": EngineeringModelSetup_template,
            "IterationSetup": IterationSetup_template,
            "Participant": Participant_template,
            "EngineeringModel": EngineeringModel_template,
            "ActualFiniteState": ActualFiniteState_template,
            "ActualFiniteStateList": ActualFiniteStateList_template,
            "AndExpression": AndExpression_template,
            "BinaryRelationship": BinaryRelationship_template,
            "BooleanExpression": BooleanExpression_template,
            "BuiltInRuleVerification": BuiltInRuleVerification_template,
            "CommonFileStore": CommonFileStore_template,
            "ConversionBasedUnit": ConversionBasedUnit_template,
            "DefinedThing": DefinedThing_template,
            "DomainOfExpertiseGroup": DomainOfExpertiseGroup_template,
            "ElementBase": ElementBase_template,
            "ExclusiveOrExpression": ExclusiveOrExpression_template,
            "ExternalIdentifierMap": ExternalIdentifierMap_template,
            "File": File_template,
            "FileRevision":  FileRevision_template,
            "FileStore": FileStore_template,
            "Folder": Folder_template,
            "IdCorrespondence": IdCorrespondence_template,
            "MeasurementScale": MeasurementScale_template,
            "MeasurementUnit": MeasurementUnit_template,
            "ModelLogEntry": ModelLogEntry_template,
            "MultiRelationship": MultiRelationship_template,
            "MultiRelationshipRule": MultiRelationshipRule_template,
            "NaturalLanguage": NaturalLanguage_template,
            "NestedElement": NestedElement_template,
            "NestedParameter": NestedParameter_template,
            "NotExpression": NotExpression_template,
            "OrExpression": OrExpression_template,
            "Organization": Organization_template,
            "ParameterBase": ParameterBase_template,
            "ParameterOrOverrideBase": ParameterOrOverrideBase_template,
            "ParameterOverride": ParameterOverride_template,
            "ParameterOverrideValueSet": ParameterOverrideValueSet_template,
            "ParameterType": ParameterType_template,
            "ParameterValueSetBase": ParameterValueSetBase_template,
            "ParametricConstraint": ParametricConstraint_template,
            "ParticipantPermission": ParticipantPermission_template,
            "ParticipantRole": ParticipantRole_template,
            "PersonPermission": PersonPermission_template,
            "PersonRole": PersonRole_template,
            "PossibleFiniteState": PossibleFiniteState_template,
            "PossibleFiniteStateList": PossibleFiniteStateList_template,
            "QuantityKind": QuantityKind_template,
            "ReferenceDataLibrary": ReferenceDataLibrary_template,
            "ReferencerRule": ReferencerRule_template,
            "RelationalExpression": RelationalExpression_template,
            "Relationship": Relationship_template,
            "Requirement": Requirement_template,
            "RequirementsContainer": RequirementsContainer_template,
            "RequirementsGroup": RequirementsGroup_template,
            "Rule": Rule_template,
            "RuleVerification": RuleVerification_template,
            "RuleVerificationList": RuleVerificationList_template,
            "RuleViolation": RuleViolation_template,
            "ScalarParameterType": ScalarParameterType_template,
            "SimpleParameterValue": SimpleParameterValue_template,
            "SimpleParameterizableThing": SimpleParameterizableThing_template,
            "SiteLogEntry": SiteLogEntry_template,
            "TelephoneNumber": TelephoneNumber_template,
            "TopContainer": TopContainer_template,
            "UserPreference": UserPreference_template,
            "UserRuleVerification": UserRuleVerification_template,
            "Thing": Thing_template}

if __name__ == "__main__":
    start = time.time()

    # User Inputs:
    # Name of Grakn keyspace where the EMSchema (aka the Knowledge Graph structure) has been loaded,
    # and where the Engineering Model data will be migrated
    # Check Read.me on how to load the EMSchema into your Grakn keyspace
    spaceName="mergedmodels3"

    # Filename and Paths of Engineering Models extracted from CDP4-CE (not open source)

    Inputs_Strathcube = [{"file": "af90770c-1282-4be3-833f-bf0ed9539b9a", "type": "iteration 5"},
                         {"file": "bff9f871-3b7f-4e57-ac82-5ab499f9baf5", "type": "SiteReferenceDataLibrary"},
                         {"file": "SiteDirectory", "type": "SiteDirectory"},
                         {"file": "52dad3b8-eee9-4faf-854d-579dc339cfef", "type": "ModelReferenceDataLibraries"},
                         {"file": "edec0cc8-9baa-4aab-b0d4-4d46763a0c97", "type": "EngineeringModelHeader"}]
    Filepath_Strathcube = ['./datasets/strathcube_it5/EngineeringModels/Iterations/',
                           './datasets/strathcube_it5/SiteReferenceDataLibraries/',
                           './datasets/strathcube_it5/',
                           './datasets/strathcube_it5/ModelReferenceDataLibraries/',
                           './datasets/strathcube_it5/EngineeringModels/']

    Inputs_Neacore = [{"file": "ffa6c039-06ca-4268-a359-304b0cb5a543", "type": "iteration"},
                         {"file": "bff9f871-3b7f-4e57-ac82-5ab499f9baf5", "type": "SiteReferenceDataLibrary"},
                         {"file": "SiteDirectory", "type": "SiteDirectory"},
                         {"file": "0cd1c94d-c803-4446-b582-c4df9f88f138", "type": "ModelReferenceDataLibraries"},
                         {"file": "b0f611a7-9ed2-4edb-9679-ea60a8f4541e", "type": "EngineeringModelHeader"}]
    Filepath_Neacore = ['./datasets/neacore_it4/EngineeringModels/Iterations/',
                           './datasets/neacore_it4/SiteReferenceDataLibraries/',
                           './datasets/neacore_it4/',
                           './datasets/neacore_it4/ModelReferenceDataLibraries/',
                           './datasets/neacore_it4/EngineeringModels/']

    Inputs_Qarman = [{"file": "e132a27a-25ef-4980-a002-3ac1c7b4d970", "type": "iteration"},
                         {"file": "bff9f871-3b7f-4e57-ac82-5ab499f9baf5", "type": "SiteReferenceDataLibrary"},
                         {"file": "SiteDirectory", "type": "SiteDirectory"},
                         {"file": "63e53a1e-7245-4588-af8d-aee201c3a30f", "type": "ModelReferenceDataLibraries"},
                         {"file": "54c7e0cd-5e0f-47f8-9d89-d08917e826a7", "type": "EngineeringModelHeader"}]
    Filepath_Qarman = ['./datasets/Qarman/EngineeringModels/Iterations/',
                           './datasets/Qarman/SiteReferenceDataLibraries/',
                           './datasets/Qarman/',
                           './datasets/Qarman/ModelReferenceDataLibraries/',
                           './datasets/Qarman/EngineeringModels/']

    print(' \n --> Make sure that your Grakn server is running and that your keyspace ', spaceName,
          ' has a loaded schema! <-- \n')

    listAvailableTemplates = [x for x in Templates.keys()]
    print(len(listAvailableTemplates), ' classes templates available')

    # Load SiteReferenceDataLibraries
    build_engineering_model_graph(inputs=Inputs_Qarman, data_path=Filepath_Qarman, keyspace_name=spaceName)

    print('Migration Duration: ', round((time.time() - start) / 60, 2), 'minutes.')

    print('Do not forget to define rules for mass budgets computations')