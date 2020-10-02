# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
This script stores all migrations templates called by migrate_em_json.py,
Each class element from the engineering model migrated to the knowledge graph requires a template:
writing the insert query to insert the migrated class instance's attributes and roles into the graph.
The relationships are committed in bulk after the entities and attributes insertion, they are stored in
tempRelationships.json in the meantime.
Class descriptions found in each template function are extracted from the ECSS-E-TM-10-25A User Manual.
'''

import json

# -------------------------------------------------------------
# Methods
# -------------------------------------------------------------

def write_relationship(relation, r1, c1, p1, r2, c2, p2 ):
    '''
    Add new parameters to tempRelationships.json to insert a relationship into Grakn keyspace
    :param relation: relationship name
    :param r1: role 1
    :param c1: class of player 1
    :param p1: player 1 title
    :param r2: role 2
    :param c2: class of player 2
    :param p2: player 2 title
    '''

    with open('tempRelationships.json', 'r') as file:
        data = json.load(file)
    data['relationship'].append(relation)
    data['role1'].append(r1)
    data['player1'].append(p1)
    data['class1'].append(c1)
    data['role2'].append(r2)
    data['class2'].append(c2)
    data['player2'].append(p2)
    with open('tempRelationships.json', 'w') as file:
        json.dump(data, file)

    return

def clean(item):
    '''
    Function to quickly remove special characters from tokens
    :param item: token to "clean"
    :return: cleaned token
    '''

    item=item.replace('\"', '')
    item=item.replace('["-"]', 'null')
    item=item.replace('-', '')
    item = item.replace('"', '')
    item=item.replace('[]', 'null')

    return item

def _template(item):
    '''
    Basic structure for template funtion
    :param item: class element from engineering model
    :return: insert query
    '''
    # class name: class definition
    # the following attributes are basic attributes each class object possesses
    graql_insert_query = 'insert $ isa , has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"
    return graql_insert_query

# -------------------------------------------------------------
# 14 Templates for Classes found in Iteration json file
# -------------------------------------------------------------
def elementDefinition_template(item):
    # Element Definition: definition of an element in a design solution for a system-of-interest
    # Insert Attributes
    graql_insert_query = 'insert $element isa ElementDefinition, has name "' + \
                         item["name"] + '", has shortName "' + item["shortName"] + '", has revisionNumber ' + \
                         str(item["revisionNumber"]) +', has classKind "' + item["classKind"] + '", has iid "' + \
                         item["iid"]+'", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    # Collect Relationships
    if item["containedElement"]:
        for i in item["containedElement"]:
            write_relationship('Containement_containedElement', 'contains_containedElement',
                               'ElementDefinition', item["iid"],'iscontained_containedElement', 'ElementUsage', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ElementDefinition',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["parameter"]:
        for i in item["parameter"]:
            write_relationship('Containement_parameter', 'contains_parameter', 'ElementDefinition',
                               item["iid"], 'iscontained_parameter', 'Parameter', i)

    if item["parameterGroup"]:
        for i in item["parameterGroup"]:
            write_relationship('Containement_parameterGroup', 'contains_parameterGroup', 'ElementDefinition', item["iid"],
                               'iscontained_parameterGroup', 'ParameterGroup', i)

    if item["referencedElement"]:
        for i in item["referencedElement"]:
            write_relationship('Reference_referencedElement', 'refers_referencedElement', 'ElementDefinition', item["iid"],
                               'isrefered_referencedElement', 'NestedElement', i)

    if item["owner"]:
        write_relationship('Reference_owner', 'refers_owner', 'ElementDefinition', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ElementDefinition',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ElementDefinition', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ElementDefinition',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def elementUsage_template(item):
    # ElementUsage: Named usage of an ElementDefinition in the context of a next higher level ElementDefinition that contains this ElementUsage
    # Insert Attributes
    graql_insert_query = 'insert $elementusage isa ElementUsage, has name "' + \
                         item["name"] + '", has shortName "' + item["shortName"] + '", has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + '", has iid "' + item[
                             "iid"] + '", has interfaceEnd "' + item["interfaceEnd"]+\
                         '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    # Collect Relationships
    # An ElementUsage always refers to an ElementDefinition
    write_relationship('Reference_elementDefinition', 'refers_elementDefinition', 'ElementUsage', item["iid"],
                       'isrefered_elementDefinition', 'ElementDefinition', item["elementDefinition"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ElementUsage',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["owner"]:
        write_relationship('Reference_owner', 'refers_owner', 'ElementUsage', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ElementUsage',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ElementUsage', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ElementUsage',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["parameterOverride"]:
        for i in item["parameterOverride"]:
            write_relationship('Containement_parameterOverride', 'contains_parameterOverride', 'ElementUsage', item["iid"],
                               'iscontained_parameterOverride', 'ParameterOverride', i)

    if item["excludeOption"]:
        for i in item["excludeOption"]:
            write_relationship('Reference_excludeOption', 'refers_excludeOption', 'ElementUsage', item["iid"],
                               'isrefered_excludeOption', 'Option ', i)

    return graql_insert_query

def Parameter_template(item):
    # Parameter: representation of a parameter that defines a characteristic or property of an ElementDefinition
    # Insert Attributes
    graql_insert_query = 'insert $parameter isa Parameter, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + '", has iid "' + item[
                             "iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '", has allowDifferentOwnerOfOverride "' + \
                         str(item["allowDifferentOwnerOfOverride"]) + '", has expectsOverride "' + str(item["expectsOverride"]) + \
                         '", has isOptionDependent "' + str(item["isOptionDependent"]) + '"'

    graql_insert_query += ";"

    # Collect Relationships
    if item["owner"]:
        write_relationship('Reference_owner', 'refers_owner', 'Parameter', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["parameterType"]:
        write_relationship('Reference_parameterType', 'refers_parameterType', 'Parameter', item["iid"],
                           'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'Parameter', item["iid"],
                           'isrefered_scale', 'MeasurementScale', item["scale"])

    if item["stateDependence"]:
        write_relationship('Reference_stateDependence', 'refers_stateDependence', 'Parameter', item["iid"],
                           'isrefered_stateDependence', 'ActualFiniteStateList', item["stateDependence"])

    if item["group"]:
        write_relationship('Reference_group', 'refers_group', 'Parameter', item["iid"],
                           'isrefered_group', 'ParameterGroup', item["group"])

    if item["valueSet"]:
        for i in item["valueSet"]:
            write_relationship('Containement_valueSet', 'contains_valueSet', 'Parameter', item["iid"],
                               'iscontained_valueSet', 'ParameterValueSet', i)

    if item["requestedBy"]:
        write_relationship('Reference_requestedBy', 'refers_requestedBy', 'Parameter', item["iid"],
                           'isrefered_requestedBy', 'DomainOfExpertise', item["requestedBy"])

    if item["parameterSubscription"]:
        for i in item["parameterSubscription"]:
            write_relationship('Containement_parameterSubscription', 'contains_parameterSubscription', 'Parameter', item["iid"],
                               'iscontained_parameterSubscription', 'ParameterSubscription', i)

    return graql_insert_query

def ParameterValueSet_template(item):
    # ParameterValueSet: representation of the switch setting and all values for a Parameter


    graql_insert_query = 'insert $parametervalueset isa ParameterValueSet, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + \
                         '", has valueSwitch "' + item["valueSwitch"] + '", has published "' + clean(item["published"]) + \
                         '", has formula "' + clean(item["formula"]) + '", has computed "' + clean(item["computed"]) + \
                         '", has manual "' + clean(item["manual"]) + '", has reference "' + clean(item["reference"]) + '"'

    graql_insert_query += ";"

    if item["actualState"]:
        write_relationship('Reference_actualState', 'refers_actualState', 'ParameterValueSet', item["iid"],
                           'isrefered_actualState', 'ActualFiniteState', item["actualState"])

    if item["actualOption"]:
        write_relationship('Reference_actualOption', 'refers_actualOption', 'ParameterValueSet', item["iid"],
                           'isrefered_actualOption', 'Option', item["actualOption"])

    return graql_insert_query

def Iteration_template(item):
    #Iteration: representation of an Iteration of an EngineeringModel
    graql_insert_query = 'insert $iteration isa Iteration, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    if item["sourceIterationIid"]:
        graql_insert_query += ', has sourceIterationIid "' + item["sourceIterationIid"] + '"'

    graql_insert_query += ";"

    if item["publication"]:
        for i in item["publication"]:
            write_relationship('Containement_publication', 'contains_publication', 'Iteration', item["iid"],
                           'iscontained_publication', 'Publication', i)

    if item["possibleFiniteStateList"]:
        for i in item["possibleFiniteStateList"]:
            write_relationship('Containement_possibleFiniteStateList', 'contains_possibleFiniteStateList', 'Iteration',
                               item["iid"],'iscontained_possibleFiniteStateList', 'PossibleFiniteStateList', i)

    if item["element"]:
        for i in item["element"]:
            write_relationship('Containement_element', 'contains_element', 'Iteration',
                               item["iid"],'iscontained_element', 'ElementDefinition', i)

    if item["relationship"]:
        for i in item["relationship"]:
            write_relationship('Containement_relation', 'contains_relation', 'Iteration',
                               item["iid"],'iscontained_relation', 'Relationship', i)

    if item["externalIdentifierMap"]:
        for i in item["externalIdentifierMap"]:
            write_relationship('Containement_externalIdentifierMap', 'contains_externalIdentifierMap', 'Iteration',
                               item["iid"],'iscontained_externalIdentifierMap', 'ExternalIdentifierMap', i)

    if item["requirementsSpecification"]:
        for i in item["requirementsSpecification"]:
            write_relationship('Containement_requirementsSpecification', 'contains_requirementsSpecification', 'Iteration',
                               item["iid"],'iscontained_requirementsSpecification', 'RequirementsSpecification', i)

    if item["domainFileStore"]:
        for i in item["domainFileStore"]:
            write_relationship('Containement_domainFileStore', 'contains_domainFileStore', 'Iteration',
                               item["iid"],'iscontained_domainFileStore', 'DomainFileStore', i)

    if item["actualFiniteStateList"]:
        for i in item["actualFiniteStateList"]:
            write_relationship('Containement_actualFiniteStateList', 'contains_actualFiniteStateList', 'Iteration',
                               item["iid"],'iscontained_actualFiniteStateList', 'ActualFiniteStateList', i)

    if item["ruleVerificationList"]:
        for i in item["ruleVerificationList"]:
            write_relationship('Containement_ruleVerificationList', 'contains_ruleVerificationList', 'Iteration',
                               item["iid"], 'iscontained_ruleVerificationList', 'RuleVerificationList', i)

    if item["iterationSetup"]:
        write_relationship('Reference_iterationSetup', 'refers_iterationSetup', 'Iteration',
                               item["iid"], 'isrefered_iterationSetup', 'IterationSetup', item["iterationSetup"])

    if item["topElement"]:
        write_relationship('Reference_topElement', 'refers_topElement', 'Iteration',
                           item["iid"], 'isrefered_topElement', 'ElementDefinition', item["topElement"])

    if item["defaultOption"]:
        write_relationship('Reference_defaultOption', 'refers_defaultOption', 'Iteration',
                           item["iid"], 'isrefered_defaultOption', 'Option', item["defaultOption"])

    if item["option"]:
        for i in item["option"]:
            write_relationship('Containement_option', 'contains_option', 'Iteration',
                               item["iid"], 'iscontained_option', 'Option', i["v"])

    return graql_insert_query

def domainFileStore_template(item):
    # domainFileStore= domain specific FileStore for use by single DomainOfExpertise

    graql_insert_query = 'insert $domainfilestore isa DomainFileStore, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has isHidden "' + str(item["isHidden"]) + '", has name "' + item["name"] + '", has createdOn "' + item["createdOn"] + '"'

    graql_insert_query += ";"

    if item["owner"]:
        write_relationship('Reference_owner', 'refers_owner', 'DomainFileStore', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["folder"]:
        for i in item["folder"]:
            write_relationship('Containement_folder', 'contains_folder', 'DomainFileStore', item["iid"],
                               'iscontained_folder', 'Folder', i)

    if item["file"]:
        for i in item["file"]:
            write_relationship('Containement_file', 'contains_file', 'DomainFileStore', item["iid"],
                               'iscontained_file','File', i)

    return graql_insert_query

def Option_template(item):
    # Option: representation of an option that is a potential design solution for the system-of-interest
    # being developed in an Iteration of an EngineeringModel

    graql_insert_query = 'insert $option isa Option, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has name "' + item["name"] + '", has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"


    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Option',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Option', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Option',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'Option',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["nestedElement"]:
        for i in item["nestedElement"]:
            write_relationship('Containement_nestedElement', 'contains_nestedElement', 'Option',
                               item["iid"], 'iscontained_nestedElement', 'NestedElement', i)
    return graql_insert_query

def Publication_template(item):
    #Publication: representation of a saved state within an Iteration where all computed values of the
    # ParameterValueSets of a selected set of Parameters and ParameterOverrides are published to (i.e. copied to)
    # the published values

    graql_insert_query = 'insert $publication isa Publication, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ";"

    if item["domain"]:
        for i in item["domain"]:
            write_relationship('Reference_domain', 'refers_domain', 'Publication',
                               item["iid"], 'isrefered_domain', 'DomainOfExpertise', i)

    if item["publishedParameter"]:
        for i in item["publishedParameter"]:
            write_relationship('Reference_publishedParameter', 'refers_publishedParameter', 'Publication',
                               item["iid"], 'isrefered_publishedParameter', 'ParameterOrOverrideBase', i)

    return graql_insert_query

def ParameterGroup_template(item):
    #ParameterGroup: representation of a group of Parameters within an ElementDefinition

    graql_insert_query = 'insert $parameterGroup isa ParameterGroup, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    if item["containingGroup"]:
        write_relationship('Reference_containingGroup', 'refers_containingGroup', 'ParameterGroup',
                           item["iid"], 'isrefered_containingGroup', 'ParameterOrOverrideBase', item["containingGroup"])

    return graql_insert_query

def Definition_template(item):
    #Definition: representation of a textual definition in a given natural language
    graql_insert_query = 'insert $definition isa Definition, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + clean(item["content"]) + '"'

    if item["note"]:
        # Combine all notes into 1 as Grakn only accepts one instance of one attribute
        combinedNotes=''
        for i in item["note"]:
            combinedNotes += clean(i["v"])+ ' ,'
        graql_insert_query += ', has note "' + combinedNotes + '"'

    if item["example"]:
        # Combine all notes into 1
        combinedEx=''
        for i in item["example"]:
            combinedEx += i["v"] + ' ,'
        graql_insert_query += ', has example "' + combinedEx + '"'

    graql_insert_query += ";"

    if item["citation"]:
        for i in item["citation"]:
            write_relationship('Containement_citation', 'contains_citation', 'Definition',
                               item["iid"], 'iscontained_citation', 'Citation', i)

    return graql_insert_query

def ParameterSubscription_template(item):
    # ParameterSubscription: representation of a subscription to a Parameter or ParameterOverride taken by
    # a DomainOfExpertise that is not the owner of the Parameter or ParameterOverride
    graql_insert_query = 'insert $parametersubscription isa ParameterSubscription, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ";"

    if item["owner"]:
        write_relationship('Reference_owner', 'refers_owner', 'ParameterSubscription', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["valueSet"]:
        for i in item["valueSet"]:
            write_relationship('Containement_valueSet', 'contains_valueSet', 'ParameterSubscription', item["iid"],
                               'iscontained_valueSet', 'ParameterValueSet', i)
    return graql_insert_query

def ParameterSubscriptionValueSet_template(item):
    # ParameterSubscriptionValueSet: representation of the switch setting and all values of a ParameterSubscription
    graql_insert_query = 'insert $parametersubscriptionvalueset isa ParameterSubscriptionValueSet, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has valueSwitch "' + item["valueSwitch"] + '"'
    #graql_insert_query += ', has computed "' + item["computed"] + '"'
    graql_insert_query += ', has manual "' + clean(item["manual"]) + '"'
    #graql_insert_query += ', has reference "' + item["reference"] + '"'
    #graql_insert_query += ', has actualValue "' + item["actualValue"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def RequirementsSpecification_template(item):
    # RequirementsSpecification: representation of a requirements specification
    graql_insert_query = 'insert $requirementsspecification isa RequirementsSpecification, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'RequirementsSpecification',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'RequirementsSpecification', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'RequirementsSpecification',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["group"]:
        for i in item["group"]:
            write_relationship('Reference_group', 'refers_group', 'RequirementsSpecification', item["iid"],
                               'isrefered_group', 'ParameterGroup', i)

    if item["owner"]:
        write_relationship('Reference_owner', 'refers_owner', 'RequirementsSpecification', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["requirement"]:
        for i in item["requirement"]:
            write_relationship('Containement_requirement', 'contains_requirement', 'RequirementsSpecification',
                               item["iid"], 'iscontained_requirement', 'Requirement', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'RequirementsSpecification',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["parameterValue"]:
        for i in item["parameterValue"]:
            write_relationship('Containement_valueSet', 'contains_valueSet', 'RequirementsSpecification', item["iid"],
                               'iscontained_valueSet', 'ParameterValueSet', i)

    return graql_insert_query

def HyperLink_template(item):
    # Hyperlink: representation of a hyperlink consisting of a URI and a descriptive text
    graql_insert_query = 'insert $hyperLink isa HyperLink, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has uri "' + item["uri"] + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

# -------------------------------------------------------------
# 39 Templates for Classes found in SiteReferenceDataLibraries json file
# -------------------------------------------------------------
def Category_template(item):
    # Category: representation of a user-defined category for categorization of instances that have common characteristics
    graql_insert_query = 'insert $category isa Category, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'

    if item["isAbstract"]:
        graql_insert_query += ', has isAbstract "' + str(item["isAbstract"]) + '"'

    if item["isDeprecated"]:
        graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["permissibleClass"]:
        combinedPermissibleClass = ''
        for i in item["permissibleClass"]:
            combinedPermissibleClass += i + ' ,'
        graql_insert_query += ', has permissibleClass "' + combinedPermissibleClass + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Category',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Category', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Category',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["superCategory"]:
        for i in item["superCategory"]:
            write_relationship('Reference_superCategory', 'refers_superCategory', 'Category',
                               item["iid"], 'isrefered_superCategory', 'Category', i)

    return graql_insert_query

def Alias_template(item):
    # Alias: representation of an alternative human-readable name for a concept
    graql_insert_query = 'insert $alias isa Alias, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has isSynonym "' + str(item["isSynonym"]) + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def Term_template(item):
    # Term: definition of a term in a Glossary of terms
    graql_insert_query = 'insert $term isa Term , has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Term',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Term', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Term',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def Citation_template(item):
    # Citation: reference with cited location to a ReferenceSource
    graql_insert_query = 'insert $citation isa Citation , has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    if item["location"]:
        graql_insert_query += ', has location "' + item["location"] + '"'

    if item["remark"]:
        graql_insert_query += ', has remark "' + item["remark"] + '"'

    graql_insert_query += ', has isAdaptation "' + str(item["isAdaptation"]) + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_source', 'refers_source', 'Citation',
                       item["iid"], 'isrefered_source', 'ReferenceSource', item["source"])

    return graql_insert_query

def QuantityKindFactor_template(item):
    # QuantityKindFactor: representation of a QuantityKind and an exponent that together define one factor in a product
    # of powers of QuantityKinds

    graql_insert_query = 'insert $quantitykindfactor isa QuantityKindFactor, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    if item["exponent"]:
        graql_insert_query += ', has exponent "' + item["exponent"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_quantityKind', 'refers_quantityKind', 'QuantityKindFactor',
                       item["iid"], 'isrefered_quantityKind', 'QuantityKind', item["quantityKind"])

    return graql_insert_query

def CyclicRatioScale_template(item):
    # CyclicRatioScale: representation of a ratio MeasurementScale with a periodic cycle
    graql_insert_query = 'insert $cyclicratioscale isa CyclicRatioScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has modulus "' + item["modulus"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
       graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'CyclicRatioScale',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'CyclicRatioScale', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'CyclicRatioScale',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'CyclicRatioScale',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containement_mappingToReferenceScale', 'contains_mappingToReferenceScale', 'CyclicRatioScale',
                               item["iid"], 'iscontained_mappingToReferenceScale', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refers_unit', 'CyclicRatioScale',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def PrefixedUnit_template(item):
    # PrefixedUnit: specialization of ConversionBasedUnit that defines a MeasurementUnit with
    # a multiple or submultiple UnitPrefix
    graql_insert_query = 'insert $prefixedunit isa PrefixedUnit, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'PrefixedUnit',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'PrefixedUnit', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'PrefixedUnit',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_referenceUnit', 'refers_referenceUnit', 'PrefixedUnit',
                       item["iid"], 'isrefered_referenceUnit', 'MeasurementUnit', item["referenceUnit"])

    write_relationship('Reference_prefix', 'refers_prefix', 'PrefixedUnit',
                       item["iid"], 'isrefered_prefix', 'UnitPrefix', item["prefix"])

    return graql_insert_query

def DecompositionRule_template(item):
    # DecompositionRule : representation of a validation rule for system-of-interest decomposition through
    # containingElement ElementDefinitions and containedElement ElementUsages
    graql_insert_query = 'insert $decompositionrule isa DecompositionRule, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has minContained ' + str(item["minContained"])

    if item["maxContained"]:
        graql_insert_query += ', has maxContained ' + str(item["maxContained"])

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DecompositionRule',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DecompositionRule', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DecompositionRule',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_containingCategory', 'refers_containingCategory', 'DecompositionRule',
                       item["iid"], 'isrefered_containingCategory', 'Category', item["containingCategory"])

    if item["containedCategory"]:
        for i in item["containedCategory"]:
            write_relationship('Reference_containedCategory', 'refers_containedCategory', 'DecompositionRule',
                               item["iid"], 'isrefered_containedCategory', 'Category', i)

    return graql_insert_query

def RatioScale_template(item):
    # RatioScale: kind of MeasurementScale that has ordered values, a measurement unit and a fixed definition of
    # the zero value on all scales for the same kind of quantity
    graql_insert_query = 'insert $ratioscale isa RatioScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'RatioScale',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'RatioScale', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'RatioScale',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'RatioScale',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containement_mappingToReferenceScale', 'contains_mappingToReferenceScale', 'RatioScale',
                               item["iid"], 'iscontained_mappingToReferenceScale', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refers_unit', 'RatioScale',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def FileType_template(item):
    # FileType: representation of the type of a File
    graql_insert_query = 'insert $filetype isa FileType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has extension "' + item["extension"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'FileType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'FileType', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'FileType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'FileType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def SimpleQuantityKind_template(item):
    # SimpleQuantityKind: specialization of QuantityKind that represents a kind of quantity that
    # does not depend on any other QuantityKind
    graql_insert_query = 'insert $simplequantitykind isa SimpleQuantityKind, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'

    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'SimpleQuantityKind',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'SimpleQuantityKind', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'SimpleQuantityKind',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'SimpleQuantityKind',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refers_possibleScale', 'SimpleQuantityKind',
                               item["iid"], 'isrefered_possibleScale', 'MeasurementScale', i)

    if item["defaultScale"]:
        write_relationship('Reference_defaultScale', 'refers_defaultScale', 'SimpleQuantityKind',
                               item["iid"], 'isrefered_defaultScale', 'MeasurementScale', item["defaultScale"])

    return graql_insert_query

def TextParameterType_template(item):
    # TextParameterType: representation of a character string valued ScalarParameterType
    graql_insert_query = 'insert $textparametertype isa TextParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'TextParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'TextParameterType', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'TextParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'TextParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def LogarithmicScale_template(item):
    # LogarithmicScale: representation of a logarithmic MeasurementScale
    graql_insert_query = 'insert $logarithmicscale isa LogarithmicScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has logarithmBase "' + item["logarithmBase"] + '"'
    graql_insert_query += ', has factor "' + item["factor"] + '"'
    graql_insert_query += ', has exponent "' + item["exponent"] + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'LogarithmicScale',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'LogarithmicScale', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'LogarithmicScale',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'LogarithmicScale',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containement_mappingToReferenceScale', 'contains_mappingToReferenceScale', 'LogarithmicScale',
                               item["iid"], 'iscontained_mappingToReferenceScale', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refers_unit', 'RatioScale',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    if item["referenceQuantityValue"]:
        for i in item["referenceQuantityValue"]:
           write_relationship('Containement_referenceQuantityValue', 'contains_referenceQuantityValue', 'LogarithmicScale',
                                   item["iid"], 'iscontained_referenceQuantityValue', 'ScaleReferenceQuantityValue', i)


    write_relationship('Reference_referenceQuantityKind', 'refers_referenceQuantityKind', 'LogarithmicScale',
                               item["iid"], 'isrefered_referenceQuantityKind', 'QuantityKind', item["referenceQuantityKind"])

    return graql_insert_query

def EnumerationValueDefinition_template(item):
    # EnumerationValueDefinition: representation of one enumeration value of an EnumerationParameterType
    graql_insert_query = 'insert $enumerationvaluedefinition isa EnumerationValueDefinition, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'EnumerationValueDefinition',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'EnumerationValueDefinition', item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'EnumerationValueDefinition',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)
    return graql_insert_query

def ParameterTypeComponent_template(item):
    # ParameterTypeComponent: representation of a component of a CompoundParameterType
    graql_insert_query = 'insert $parametertypecomponent isa ParameterTypeComponent, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refers_parameterType', 'ParameterTypeComponent', item["iid"],
                           'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'ParameterTypeComponent', item["iid"],
                           'isrefered_scale', 'MeasurementScale', item["scale"])

    return graql_insert_query

def ScaleReferenceQuantityValue_template(item):
    # ScaleReferenceQuantityValue: representation of a reference quantity with value for the definition of
    # logarithmic MeasurementScales
    graql_insert_query = 'insert $scalereferencequantityvalue isa ScaleReferenceQuantityValue, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has value "' + clean(item["value"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_scale', 'refers_scale', 'ScaleReferenceQuantityValue', item["iid"],
                           'isrefered_scale', 'MeasurementScale', item["scale"])

    return graql_insert_query

def MappingToReferenceScale_template(item):
    # MappingToReferenceScale: representation of a mapping of a value on a dependent MeasurementScale to a value on a
    # reference MeasurementScale that represents the same quantity
    graql_insert_query = 'insert $mappingtoreferencescale isa MappingToReferenceScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ";"

    write_relationship('Reference_referenceScaleValue', 'refers_referenceScaleValue', 'MappingToReferenceScale', item["iid"],
                       'isrefered_referenceScaleValue', 'ScaleValueDefinition', item["referenceScaleValue"])

    write_relationship('Reference_dependentScaleValue', 'refers_dependentScaleValue', 'MappingToReferenceScale', item["iid"],
                       'isrefered_dependentScaleValue', 'ScaleValueDefinition', item["dependentScaleValue"])

    return graql_insert_query

def BinaryRelationshipRule_template(item):
    # BinaryRelationshipRule: representation of a validation rule for BinaryRelationships
    graql_insert_query = 'insert $binaryrelationshiprule isa BinaryRelationshipRule, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'

    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has forwardrelationName "' + item["forwardRelationshipName"] + '"'
    graql_insert_query += ', has inverserelationName "' + item["inverseRelationshipName"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'BinaryRelationshipRule',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'BinaryRelationshipRule',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'BinaryRelationshipRule',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_relationCategory', 'refers_relationCategory', 'BinaryRelationshipRule',
                       item["iid"], 'isrefered_relationCategory', 'Category', item["relationshipCategory"])

    write_relationship('Reference_sourceCategory', 'refers_sourceCategory', 'BinaryRelationshipRule',
                       item["iid"], 'isrefered_sourceCategory', 'Category', item["sourceCategory"])

    write_relationship('Reference_targetCategory', 'refers_targetCategory', 'BinaryRelationshipRule',
                       item["iid"], 'isrefered_targetCategory', 'Category', item["targetCategory"])

    return graql_insert_query

def UnitFactor_template(item):
    # UnitFactor: representation of a factor in the product of powers that defines a DerivedUnit
    graql_insert_query = 'insert $unitfactor isa UnitFactor, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has exponent "' + item["exponent"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_unit', 'refers_unit', 'UnitFactor',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def ReferenceSource_template(item):
    # ReferenceSource: representation of an information source that can be referenced
    graql_insert_query = 'insert $referencesource isa ReferenceSource, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["versionIdentifier"]:
        graql_insert_query += ', has versionIdentifier "' + item["versionIdentifier"] + '"'

    if item["versionDate"]:
        graql_insert_query += ', has versionDate "' + item["versionDate"] + '"'

    if item["author"]:
        graql_insert_query += ', has author "' + item["author"] + '"'

    if item["publicationYear"]:
        graql_insert_query += ', has publicationYear ' + str(item["publicationYear"])

    if item["language"]:
        graql_insert_query += ', has language "' + item["language"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ReferenceSource',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ReferenceSource',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ReferenceSource',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ReferenceSource',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["publisher"]:
        write_relationship('Reference_publisher', 'refers_publisher', 'ReferenceSource',
                               item["iid"], 'isrefered_publisher', 'Organization', item["publisher"])

    if item["publishedIn"]:
        write_relationship('Reference_publishedIn', 'refers_publishedIn', 'ReferenceSource',
                               item["iid"], 'isrefered_publishedIn', 'ReferenceSource', item["publishedIn"])

    return graql_insert_query

def Constant_template(item):
    # Constant: representation of a named constant, typically a mathematical or physical constant
    graql_insert_query = 'insert $constant isa Constant, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has value "' + clean(item["value"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Constant',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Constant',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Constant',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_parameterType', 'refers_parameterType', 'Constant', item["iid"],
                               'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'Constant', item["iid"],
                       'isrefered_scale', 'MeasurementScale', item["scale"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'Constant',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def IntervalScale_template(item):
    # IntervalScale: kind of MeasurementScale that has ordered values, a measurement unit and an arbitrary zero value
    graql_insert_query = 'insert $intervalscale isa IntervalScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'IntervalScale',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'IntervalScale',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'IntervalScale',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'IntervalScale',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containement_mappingToReferenceScale', 'contains_mappingToReferenceScale', 'IntervalScale',
                               item["iid"], 'iscontained_mappingToReferenceScale', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refers_unit', 'IntervalScale',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def DerivedQuantityKind_template(item):
    # DerivedQuantityKind: specialization of QuantityKind that represents a kind of quantity that is defined as a
    # product of powers of one or more other kinds of quantity
    graql_insert_query = 'insert $derivedquantitykind isa DerivedQuantityKind, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DerivedQuantityKind',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DerivedQuantityKind',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DerivedQuantityKind',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'DerivedQuantityKind',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["quantityKindFactor"]:
        for i in item["quantityKindFactor"]:
            write_relationship('Containement_quantityKindFactor', 'contains_quantityKindFactor', 'DerivedQuantityKind',
                               item["iid"], 'iscontained_quantityKindFactor', 'QuantityKindFactor', i["v"])

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refers_possibleScale', 'DerivedQuantityKind',
                               item["iid"], 'isrefered_possibleScale', 'MeasurementScale', i)

    write_relationship('Reference_defaultScale', 'refers_defaultScale', 'DerivedQuantityKind',
                       item["iid"], 'isrefered_defaultScale', 'MeasurementScale', item["defaultScale"])


    '''
    # Not found in json file:
    has quantityDimensionExpression,  
    has quantityDimensionExponent, 
    has numberOfValues,  
    plays refers_allPossibleScale,
    '''

    return graql_insert_query

def BooleanParameterType_template(item):
    # BooleanParameterType: representation of a boolean valued ScalarParameterType with two permissible values
    # "true" and "false"
    graql_insert_query = 'insert $booleanparametertype isa BooleanParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'BooleanParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'BooleanParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'BooleanParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'BooleanParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def UnitPrefix_template(item):
    # UnitPrefix: representation of a multiple or submultiple prefix for MeasurementUnits as defined in ISO/IEC 80000
    graql_insert_query = 'insert $unitprefix isa UnitPrefix, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has conversionFactor "' + item["conversionFactor"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'UnitPrefix',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'UnitPrefix',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'UnitPrefix',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def LinearConversionUnit_template(item):
    # LinearConversionUnit: specialization of ConversionBasedUnit that represents a measurement unit that is defined
    # with respect to another reference measurement unit through a linear conversion relation with a conversion factor
    graql_insert_query = 'insert $linearconversionunit isa LinearConversionUnit, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has conversionFactor "' + item["conversionFactor"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'LinearConversionUnit',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'LinearConversionUnit',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'LinearConversionUnit',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_referenceUnit', 'refers_referenceUnit', 'LinearConversionUnit',
                       item["iid"], 'isrefered_referenceUnit', 'MeasurementUnit', item["referenceUnit"])

    return graql_insert_query

def TimeOfDayParameterType_template(item):
    # TimeOfDayParameterType: representation of a time of day valued ScalarParameterType
    graql_insert_query = 'insert $timeofdayparametertype isa TimeOfDayParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'TimeOfDayParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'TimeOfDayParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'TimeOfDayParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'TimeOfDayParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def DateTimeParameterType_template(item):
    # DateTimeParameterType: representation of a calendar date and time valued ScalarParameterType
    graql_insert_query = 'insert $datetimeparametertype isa DateTimeParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"


    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DateTimeParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DateTimeParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DateTimeParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'DateTimeParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def ArrayParameterType_template(item):
    # ArrayParameterType: specialization of CompoundParameterType that specifies a one-dimensional or multi-dimensional
    # array parameter type with elements (components) that are typed by other ScalarParameterTypes
    graql_insert_query = 'insert $arrayparametertype isa ArrayParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has isTensor "' + str(item["isTensor"]) + '"'
    graql_insert_query += ', has isFinalized "' + str(item["isFinalized"]) + '"'

    combinedDimension = ''
    for i in item["dimension"]:
        combinedDimension += str(i["v"]) + ' ,'
    graql_insert_query += ', has dimension "' + combinedDimension + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ArrayParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ArrayParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ArrayParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ArrayParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["component"]:
        for i in item["component"]:
            write_relationship('Containement_component', 'contains_component', 'ArrayParameterType',
                               item["iid"], 'iscontained_component', 'ParameterTypeComponent', i['v'])

    return graql_insert_query

def DerivedUnit_template(item):
    # DerivedUnit: specialization of MeasurementUnit that is defined as a product of powers of one or more other
    # measurement units
    graql_insert_query = 'insert $derivedunit isa DerivedUnit, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DerivedUnit',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DerivedUnit',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DerivedUnit',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    for i in item["unitFactor"]:
        write_relationship('Containement_unitFactor', 'contains_unitFactor', 'DerivedUnit',
                           item["iid"], 'iscontained_unitFactor', 'UnitFactor', i['v'])

    return graql_insert_query

def ScaleValueDefinition_template(item):
    # ScaleValueDefinition: representation of a particular definitional scale value of a MeasurementScale
    graql_insert_query = 'insert $scalevaluedefinition isa ScaleValueDefinition, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ScaleValueDefinition',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ScaleValueDefinition',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ScaleValueDefinition',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def DateParameterType_template(item):
    # DateParameterType: representation of a calendar date valued ScalarParameterType
    graql_insert_query = 'insert $dateparametertype isa DateParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DateParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DateParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DateParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'DateParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def ParameterizedCategoryRule_template(item):
    # ParameterizedCategoryRule: Rule that asserts that one or more parameters of a given ParameterType should be
    # defined for CategorizableThings that are a member of the associated Category
    graql_insert_query = 'insert $parameterizedcategoryrule isa ParameterizedCategoryRule, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ParameterizedCategoryRule',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ParameterizedCategoryRule',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ParameterizedCategoryRule',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_category', 'refers_category', 'ParameterizedCategoryRule', item["iid"],
                       'isrefered_category', 'Category', item["category"])

    for i in item["parameterType"]:
        write_relationship('Reference_parameterType', 'refers_parameterType', 'ParameterizedCategoryRule', item["iid"],
                       'isrefered_parameterType', 'ParameterType', i)

    return graql_insert_query

def SimpleUnit_template(item):
    # SimpleUnit: specialization of MeasurementUnit that represents a measurement unit that does not depend
    # on any other MeasurementUnit
    graql_insert_query = 'insert $simpleunit isa SimpleUnit, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'SimpleUnit',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'SimpleUnit',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'SimpleUnit',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def CompoundParameterType_template(item):
    # CompoundParameterType: representation of a non-scalar compound parameter type that is composed of
    # one or more other (component) ParameterTypes
    graql_insert_query = 'insert $compoundparametertype isa CompoundParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has isFinalized "' + str(item["isFinalized"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'CompoundParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'CompoundParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'CompoundParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'CompoundParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["component"]:
        for i in item["component"]:
            write_relationship('Containement_component', 'contains_component', 'CompoundParameterType',
                               item["iid"], 'iscontained_component', 'ParameterTypeComponent', i['v'])

    return graql_insert_query

def EnumerationParameterType_template(item):
    # EnumerationParameterType: representation of an enumeration valued ScalarParameterType with a user-defined list
    # of text values (enumeration literals) to select from
    graql_insert_query = 'insert $enumerationparametertype isa EnumerationParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has allowMultiSelect "' + str(item["allowMultiSelect"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'EnumerationParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'EnumerationParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'EnumerationParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'EnumerationParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    for i in item["valueDefinition"]:
        write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'EnumerationParameterType',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i["v"])

    return graql_insert_query

def OrdinalScale_template(item):
    # OrdinalScale: kind of MeasurementScale in which the possible valid values are ordered but
    # where the intervals between the values do not have particular significance
    graql_insert_query = 'insert $ordinalscale isa OrdinalScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has useShortNameValues "' + str(item["useShortNameValues"]) + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'OrdinalScale',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'OrdinalScale',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'OrdinalScale',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'OrdinalScale',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containement_mappingToReferenceScale', 'contains_mappingToReferenceScale',
                               'OrdinalScale',
                               item["iid"], 'iscontained_mappingToReferenceScale', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refers_unit', 'OrdinalScale',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def Glossary_template(item):
    # Glossary: representation of a glossary of terms
    graql_insert_query = 'insert $glossary isa Glossary, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Glossary',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Glossary',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Glossary',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'Glossary',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["term"]:
        for i in item["term"]:
            write_relationship('Containement_term', 'contains_term', 'Glossary',
                               item["iid"], 'iscontained_term', 'Term', i)

    return graql_insert_query

def SpecializedQuantityKind_template(item):
    # SpecializedQuantityKind: specialization of QuantityKind that represents a kind of quantity that is
    # a specialization of another kind of quantity
    graql_insert_query = 'insert $specializedquantitykind isa SpecializedQuantityKind, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'SpecializedQuantityKind',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'SpecializedQuantityKind',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'SpecializedQuantityKind',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'SpecializedQuantityKind',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refers_possibleScale', 'SpecializedQuantityKind',
                               item["iid"], 'isrefered_possibleScale', 'MeasurementScale', i)

    write_relationship('Reference_defaultScale', 'refers_defaultScale', 'SpecializedQuantityKind',
                       item["iid"], 'isrefered_defaultScale', 'MeasurementScale', item["defaultScale"])

    write_relationship('Reference_general', 'refers_general', 'SpecializedQuantityKind',
                       item["iid"], 'isrefered_general', 'QuantityKind', item["general"])

    '''
    has quantityDimensionExpression,  
    has quantityDimensionExponent, 
    has numberOfValues,        
    plays refers_allPossibleScale    
    '''

    return graql_insert_query

# -------------------------------------------------------------
# 9 Templates for Classes found in SiteDirectory json file
# -------------------------------------------------------------

'''
SiteDirectory
SiteReferenceDataLibrary
Person
ModelReferenceDataLibrary
EmailAddress
DomainOfExpertise
EngineeringModelSetup
IterationSetup
Participant
'''

def SiteDirectory_template(item):
    # SiteDirectory: resource directory that contains (references to) the data that is used across all models,
    # templates, catalogues and reference data for a specific concurrent design centre
    graql_insert_query = 'insert $sitedirectory isa SiteDirectory, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ";"

    if item["organization"]:
        for i in item["organization"]:
            write_relationship('Containement_organization', 'contains_organization', 'SiteDirectory',
                               item["iid"], 'iscontained_organization', 'Organization', i)

    if item["person"]:
        for i in item["person"]:
            write_relationship('Containement_person', 'contains_person', 'SiteDirectory',
                               item["iid"], 'iscontained_person', 'Person', i)

    if item["participantRole"]:
        for i in item["participantRole"]:
            write_relationship('Containement_participantRole', 'contains_participantRole', 'SiteDirectory',
                               item["iid"], 'iscontained_participantRole', 'ParticipantRole', i)

    if item["model"]:
        for i in item["model"]:
            write_relationship('Containement_model', 'contains_model', 'SiteDirectory',
                               item["iid"], 'iscontained_model', 'EngineeringModelSetup', i)

    if item["personRole"]:
        for i in item["personRole"]:
            write_relationship('Containement_personRole', 'contains_personRole', 'SiteDirectory',
                               item["iid"], 'iscontained_personRole', 'PersonRole', i)

    if item["logEntry"]:
        for i in item["logEntry"]:
            write_relationship('Containement_logEntry', 'contains_logEntry', 'SiteDirectory',
                               item["iid"], 'iscontained_logEntry', 'SiteLogEntry', i)

    if item["domainGroup"]:
        for i in item["domainGroup"]:
            write_relationship('Containement_domainGroup', 'contains_domainGroup', 'SiteDirectory',
                               item["iid"], 'iscontained_domainGroup', 'DomainOfExpertiseGroup', i)

    if item["domain"]:
        for i in item["domain"]:
            write_relationship('Containement_domain', 'contains_domain', 'SiteDirectory',
                               item["iid"], 'iscontained_domain', 'DomainOfExpertise', i)

    if item["naturalLanguage"]:
        for i in item["naturalLanguage"]:
            write_relationship('Containement_naturalLanguage', 'contains_naturalLanguage', 'SiteDirectory',
                               item["iid"], 'iscontained_naturalLanguage', 'NaturalLanguage', i)

    if item["siteReferenceDataLibrary"]:
        for i in item["siteReferenceDataLibrary"]:
            write_relationship('Containement_siteReferenceDataLibrary', 'contains_siteReferenceDataLibrary', 'SiteDirectory',
                               item["iid"], 'iscontained_siteReferenceDataLibrary', 'SiteReferenceDataLibrary', i)

    if item["defaultParticipantRole"]:
        write_relationship('Reference_defaultParticipantRole', 'refers_defaultParticipantRole',
                           'SiteDirectory', item["iid"], 'isrefered_defaultParticipantRole', 'ParticipantRole',
                           item["defaultParticipantRole"])

    if item["defaultPersonRole"]:
        write_relationship('Reference_defaultPersonRole', 'refers_defaultPersonRole',
                           'SiteDirectory', item["iid"], 'isrefered_defaultPersonRole', 'PersonRole', item["defaultPersonRole"])

    return graql_insert_query

def SiteReferenceDataLibrary_template(item):
    # SiteReferenceDataLibrary: ReferenceDataLibrary that can be (re-)used by multiple EngineeringModels /
    # EngineeringModelSetups
    graql_insert_query = 'insert $sitereferencedatalibrary isa SiteReferenceDataLibrary, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'SiteReferenceDataLibrary',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["definedCategory"]:
        for i in item["definedCategory"]:
            write_relationship('Containement_definedCategory', 'contains_definedCategory', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_definedCategory', 'Category', i)
    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containement_parameterType', 'contains_parameterType', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_parameterType', 'ParameterType', i)
    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containement_parameterType', 'contains_parameterType', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_parameterType', 'ParameterType', i)

    if item["scale"]:
        for i in item["scale"]:
            write_relationship('Containement_scale', 'contains_scale', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_scale', 'MeasurementScale', i)

    if item["unitPrefix"]:
        for i in item["unitPrefix"]:
            write_relationship('Containement_unitPrefix', 'contains_unitPrefix', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_unitPrefix', 'UnitPrefix', i)

    if item["unit"]:
        for i in item["unit"]:
            write_relationship('Containement_unit', 'contains_unit', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_unit', 'MeasurementUnit', i)

    if item["fileType"]:
        for i in item["fileType"]:
            write_relationship('Containement_fileType', 'contains_fileType', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_fileType', 'FileType', i)

    if item["glossary"]:
        for i in item["glossary"]:
            write_relationship('Containement_glossary', 'contains_glossary', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_glossary', 'Glossary', i)

    if item["referenceSource"]:
        for i in item["referenceSource"]:
            write_relationship('Containement_referenceSource', 'contains_referenceSource', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_referenceSource', 'ReferenceSource', i)

    if item["rule"]:
        for i in item["rule"]:
            write_relationship('Containement_rule', 'contains_rule', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_rule', 'Rule', i)

    if item["constant"]:
        for i in item["constant"]:
            write_relationship('Containement_constant', 'contains_constant', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_constant', 'Constant', i)

    if item["baseQuantityKind"]:
        for i in item["baseQuantityKind"]:
            write_relationship('Reference_baseQuantityKind', 'refers_baseQuantityKind', 'SiteReferenceDataLibrary',
                               item["iid"], 'isrefered_baseQuantityKind', 'QuantityKind', i["v"])

    if item["baseUnit"]:
        for i in item["baseUnit"]:
            write_relationship('Reference_baseUnit', 'refers_baseUnit', 'SiteReferenceDataLibrary',
                               item["iid"], 'isrefered_baseUnit', 'MeasurementUnit', i)

    if item["requiredRdl"]:
        write_relationship('Reference_requiredRdl', 'refers_requiredRdl', 'SiteReferenceDataLibrary',
                           item["iid"], 'isrefered_requiredRdl', 'SiteReferenceDataLibrary', item["requiredRdl"])


    return graql_insert_query

def Person_template(item):
    # Person: representation of a physical person that is a potential Participant in a concurrent engineering activity
    graql_insert_query = 'insert $person isa Person, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    graql_insert_query += ', has givenName "' + item["givenName"] + '"'
    graql_insert_query += ', has surname "' + item["surname"] + '"'
    if item["organizationalUnit"]:
        graql_insert_query += ', has organizationalUnit "' + item["organizationalUnit"] + '"'
    if item["password"]:
        graql_insert_query += ', has password "' + item["password"] + '"'
    graql_insert_query += ";"

    if item["emailAddress"]:
        for i in item["emailAddress"]:
            write_relationship('Containement_emailAddress', 'contains_emailAddress', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_emailAddress', 'EmailAddress', i)

    if item["telephoneNumber"]:
        for i in item["telephoneNumber"]:
            write_relationship('Containement_telephoneNumber', 'contains_telephoneNumber', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_telephoneNumber', 'TelephoneNumber', i)

    if item["userPreference"]:
        for i in item["userPreference"]:
            write_relationship('Containement_userPreference', 'contains_userPreference', 'SiteReferenceDataLibrary',
                               item["iid"], 'iscontained_userPreference', 'UserPreference', i)

    if item["organization"]:
        write_relationship('Reference_organization', 'refers_organization', 'SiteReferenceDataLibrary',
                           item["iid"], 'isrefered_organization', 'Organization', item["organization"])

    if item["defaultDomain"]:
        write_relationship('Reference_defaultDomain', 'refers_defaultDomain', 'SiteReferenceDataLibrary',
                           item["iid"], 'isrefered_defaultDomain', 'DomainOfExpertise', item["defaultDomain"])

    if item["role"]:
        write_relationship('Reference_role', 'refers_role', 'SiteReferenceDataLibrary',
                           item["iid"], 'isrefered_role', 'PersonRole', item["role"])

    if item["defaultEmailAddress"]:
        write_relationship('Reference_defaultEmailAddress', 'refers_defaultEmailAddress', 'SiteReferenceDataLibrary',
                           item["iid"], 'isrefered_defaultEmailAddress', 'EmailAddress', item["defaultEmailAddress"])

    if item["defaultTelephoneNumber"]:
        write_relationship('Reference_defaultTelephoneNumber', 'refers_defaultTelephoneNumber', 'SiteReferenceDataLibrary',
                           item["iid"], 'isrefered_defaultTelephoneNumber', 'TelephoneNumber', item["defaultTelephoneNumber"])

    return graql_insert_query

def ModelReferenceDataLibrary_template(item):
    # ModelReferenceDataLibrary: ReferenceDataLibrary that is particular to a given EngineeringModel
    # / EngineeringModelSetup
    graql_insert_query = 'insert $modelreferencedatalibrary isa ModelReferenceDataLibrary, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ModelReferenceDataLibrary',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["definedCategory"]:
        for i in item["definedCategory"]:
            write_relationship('Containement_definedCategory', 'contains_definedCategory', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_definedCategory', 'Category', i)

    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containement_parameterType', 'contains_parameterType', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_parameterType', 'ParameterType', i)

    if item["scale"]:
        for i in item["scale"]:
            write_relationship('Containement_scale', 'contains_scale', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_scale', 'MeasurementScale', i)

    if item["unitPrefix"]:
        for i in item["unitPrefix"]:
            write_relationship('Containement_unitPrefix', 'contains_unitPrefix', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_unitPrefix', 'UnitPrefix', i)

    if item["unit"]:
        for i in item["unit"]:
            write_relationship('Containement_unit', 'contains_unit', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_unit', 'MeasurementUnit', i)

    if item["fileType"]:
        for i in item["fileType"]:
            write_relationship('Containement_fileType', 'contains_fileType', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_fileType', 'FileType', i)

    if item["glossary"]:
        for i in item["glossary"]:
            write_relationship('Containement_glossary', 'contains_glossary', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_glossary', 'Glossary', i)

    if item["referenceSource"]:
        for i in item["referenceSource"]:
            write_relationship('Containement_referenceSource', 'contains_referenceSource', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_referenceSource', 'ReferenceSource', i)

    if item["rule"]:
        for i in item["rule"]:
            write_relationship('Containement_rule', 'contains_rule', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_rule', 'Rule', i)

    if item["constant"]:
        for i in item["constant"]:
            write_relationship('Containement_constant', 'contains_constant', 'ModelReferenceDataLibrary',
                               item["iid"], 'iscontained_constant', 'Constant', i)

    if item["baseQuantityKind"]:
        for i in item["baseQuantityKind"]:
            write_relationship('Reference_baseQuantityKind', 'refers_baseQuantityKind', 'ModelReferenceDataLibrary',
                               item["iid"], 'isrefered_baseQuantityKind', 'QuantityKind', i["v"])

    if item["baseUnit"]:
        for i in item["baseUnit"]:
            write_relationship('Reference_baseUnit', 'refers_baseUnit', 'ModelReferenceDataLibrary',
                               item["iid"], 'isrefered_baseUnit', 'MeasurementUnit', i)

    if item["requiredRdl"]:
        write_relationship('Reference_requiredRdl', 'refers_requiredRdl', 'ModelReferenceDataLibrary',
                           item["iid"], 'isrefered_requiredRdl', 'SiteReferenceDataLibrary', item["requiredRdl"])

    return graql_insert_query

def EmailAddress_template(item):
    # EmailAddress: representation of an e-mail address
    graql_insert_query = 'insert $emailaddress isa EmailAddress, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has vcardType "' + item["vcardType"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"
    return graql_insert_query

def DomainOfExpertise_template(item):
    # DomainOfExpertise: representation of a coherent set of experience, skills, methods, standards and tools in
    # a specific field of knowledge relevant to an engineering process
    graql_insert_query = 'insert $domainofexpertise isa DomainOfExpertise, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DomainOfExpertise',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DomainOfExpertise',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DomainOfExpertise',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'DomainOfExpertise',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def EngineeringModelSetup_template(item):
    # EngineeringModelSetup: representation of the set-up information of a concurrent engineering model
    graql_insert_query = 'insert $engineeringmodelsetup isa EngineeringModelSetup, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has kind "' + item["kind"] + '"'
    graql_insert_query += ', has studyPhase "' + item["studyPhase"] + '"'
    graql_insert_query += ', has engineeringModelIid "' + item["engineeringModelIid"] + '"'
    if item["sourceEngineeringModelSetupIid"]:
        graql_insert_query += ', has sourceEngineeringModelSetupIid "' + item["sourceEngineeringModelSetupIid"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'EngineeringModelSetup',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'EngineeringModelSetup',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'EngineeringModelSetup',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["participant"]:
        for i in item["participant"]:
            write_relationship('Containement_participant', 'contains_participant', 'EngineeringModelSetup',
                               item["iid"], 'iscontained_participant', 'Participant', i)

    write_relationship('Containement_requiredRdl', 'contains_requiredRdl', 'EngineeringModelSetup',
                       item["iid"], 'iscontained_requiredRdl', 'ModelReferenceDataLibrary', i)

    for i in item["iterationSetup"]:
        write_relationship('Containement_iterationSetup', 'contains_iterationSetup', 'EngineeringModelSetup',
                           item["iid"], 'iscontained_iterationSetup', 'IterationSetup', i)

    for i in item["activeDomain"]:
        write_relationship('Reference_activeDomain', 'refers_activeDomain', 'EngineeringModelSetup',
                           item["iid"], 'isrefered_activeDomain', 'DomainOfExpertise', i)

    return graql_insert_query

def IterationSetup_template(item):
    # IterationSetup: representation of the set-up information of an Iteration in the EngineeringModel associated
    # with the EngineeringModelSetup that contains this IterationInfo
    graql_insert_query = 'insert $iterationsetup isa IterationSetup, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has iterationIid "' + item["iterationIid"] + '"'
    graql_insert_query += ', has iterationNumber ' + str(item["iterationNumber"])
    graql_insert_query += ', has description "' + item["description"] + '"'
    graql_insert_query += ', has isDeleted "' + str(item["isDeleted"]) + '"'
    if item["frozenOn"]:
        graql_insert_query += ', has frozenOn "' + item["frozenOn"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ";"

    if item["sourceIterationSetup"]:
        write_relationship('Reference_sourceIterationSetup', 'refers_sourceIterationSetup', 'IterationSetup',
                           item["iid"], 'isrefered_sourceIterationSe', 'IterationSetup', item["sourceIterationSetup"])

    return graql_insert_query

def Participant_template(item):
    # Participant: representation of a participant in the team working in a concurrent engineering activity on
    # an EngineeringModel
    graql_insert_query = 'insert $participant isa Participant, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_role', 'refers_role', 'Participant',
                           item["iid"], 'isrefered_role', 'PersonRole', item["role"])

    write_relationship('Reference_person', 'refers_person', 'Participant',
                       item["iid"], 'isrefered_person', 'Person', item["person"])

    write_relationship('Reference_selectedDomain', 'refers_selectedDomain', 'Participant',
                       item["iid"], 'isrefered_selectedDomain', 'DomainOfExpertise', item["selectedDomain"])

    for i in item["domain"]:
        write_relationship('Reference_domain', 'refers_domain', 'Participant',
                               item["iid"], 'isrefered_domain', 'DomainOfExpertise', i)


    return graql_insert_query

# -------------------------------------------------------------
# 1 Template for Class found in Engineering Model Header json file
# -------------------------------------------------------------
def EngineeringModel_template(item):
    # EngineeringModel: representation of a parametric concurrent engineering model that specifies the problem to be
    # solved and defines one or more (possible) design solutions
    graql_insert_query = 'insert $engineeringmodel isa EngineeringModel, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    if item["logEntry"]:
        for i in item["logEntry"]:
            write_relationship('Containement_logEntry', 'contains_logEntry', 'EngineeringModel',
                               item["iid"], 'iscontained_logEntry', 'ModelLogEntry', i)

    write_relationship('Reference_engineeringModelSetup', 'refers_engineeringModelSetup', 'EngineeringModel',
                       item["iid"], 'isrefered_engineeringModelSetup', 'EngineeringModelSetup',
                       item["engineeringModelSetup"])

    if item["commonFileStore"]:
        write_relationship('Containement_commonFileStore', 'contains_commonFileStore', 'EngineeringModel',
                           item["iid"], 'iscontained_commonFileStore', 'CommonFileStore',
                           item["commonFileStore"])

    for i in item["iteration"]:
        write_relationship('Containement_iteration', 'contains_iteration', 'EngineeringModel',
                           item["iid"], 'iscontained_iteration', 'Iteration', i)

    return graql_insert_query


# -------------------------------------------------------------
# 64 Template for remaining classes
# -------------------------------------------------------------

'''
ActualFiniteState
ActualFiniteStateList
AndExpression
BinaryRelationship
BooleanExpression
BuiltInRuleVerification
CommonFileStore
CompoundParameterType
ConversionBasedUnit
DefinedThing
DomainOfExpertiseGroup

ElementBase
ExclusiveOrExpression
ExternalIdentifierMap
File
FileRevision
FileStore
Folder
IdCorrespondence
MeasurementScale
MeasurementUnit
ModelLogEntry

MultiRelationship
MultiRelationshipRule
NaturalLanguage
NestedElement
NestedParameter
NotExpression
OrExpression
Organization
ParameterBase
ParameterOrOverrideBase
ParameterOverride

ParameterOverrideValueSet
ParameterType
ParameterValueSetBase
ParametricConstraint
ParticipantPermission
ParticipantRole
PersonPermission
PersonRole
PossibleFiniteState
PossibleFiniteStateList
QuantityKind
ReferenceDataLibrary
ReferencerRule
RelationalExpression
Relationship
Requirement
RequirementsContainer
RequirementsGroup
Rule
RuleVerification
RuleVerificationList

RuleViolation
ScalarParameterType
SimpleParameterValue
SimpleParameterizableThing
SiteLogEntry
TelephoneNumber
TopContainer
UserPreference
UserRuleVerification
Thing
'''

def ActualFiniteState_template(item):
    # ActualFiniteState: representation of an actual finite state in an ActualFiniteStateList
    graql_insert_query = 'insert $actualfinitestate isa ActualFiniteState, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has kind "' + item["kind"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'ActualFiniteState', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    for i in item['possibleState']:
        write_relationship('Reference_possibleState', 'refers_possibleState', 'ActualFiniteState', item["iid"],
                           'isrefered_possibleState', 'PossibleFiniteState', i)

    return graql_insert_query

def ActualFiniteStateList_template(item):
    # ActualFiniteStateList: representation of a set of actual finite states that can be used to define a finite
    # state dependence for a Parameter
    graql_insert_query = 'insert $actualfinitestatelist isa ActualFiniteStateList, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'ActualFiniteStateList', item["iid"],
                           'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["excludeOption"]:
        for i in item["excludeOption"]:
            write_relationship('Reference_excludeOption', 'refers_excludeOption', 'ActualFiniteStateList', item["iid"],
                               'isrefered_excludeOption', 'Option', i)

    for i in item["possibleFiniteStateList"]:
        write_relationship('Reference_possibleFiniteStateList', 'refers_possibleFiniteStateList', 'ActualFiniteStateList',
                           item["iid"], 'isrefered_possibleFiniteStateList', 'PossibleFiniteStateList', i)

    if item["actualState"]:
        for i in item["actualState"]:
            write_relationship('Containement_actualState', 'contains_actualState', 'ActualFiniteStateList', item["iid"],
                               'iscontained_actualState', 'ActualFiniteState', i)
    return graql_insert_query

def AndExpression_template(item):
    # AndExpression: representation of a boolean and (conjunction) expression
    graql_insert_query = 'insert $andexpression isa AndExpression, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    for i in item["term"]:
        write_relationship('Reference_term', 'refers_term', 'AndExpression',
                           item["iid"], 'isrefered_term', 'BooleanExpression', i)
    return graql_insert_query

def BinaryRelationship_template(item):
    # BinaryRelationship: representation of a relationship between exactly two Things
    graql_insert_query = 'insert $binaryrelationship isa BinaryRelationship, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_source', 'refers_source', 'BinaryRelationship',
                       item["iid"], 'isrefered_source', 'Thing', item["source"])

    write_relationship('Reference_target', 'refers_target', 'BinaryRelationship',
                       item["iid"], 'isrefered_target', 'Thing', item["target"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'BinaryRelationship',
                               item["iid"], 'isrefered_category', 'Category', i)

    write_relationship('Reference_owner', 'refers_owner', 'BinaryRelationship', item["iid"],
                   'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def BooleanExpression_template(item):
    # BooleanExpression: abstract supertype to provide a common base for all kinds of boolean expression
    graql_insert_query = 'insert $booleanexpression isa BooleanExpression, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def BuiltInRuleVerification_template(item):
    # BuiltInRuleVerification: representation of the verification of a built-in data model rule
    graql_insert_query = 'insert $builtinruleverification isa BuiltInRuleVerification, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    if item["executedOn"]:
        graql_insert_query += ', has executedOn "' + item["executedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has status "' + item["status"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'BuiltInRuleVerification', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["violation"]:
        for i in item["violation"]:
            write_relationship('Containement_violation', 'contains_violation', 'BuiltInRuleVerification',
                               item["iid"], 'iscontained_violation', 'RuleViolation', i)

    return graql_insert_query

def CommonFileStore_template(item):
    # CommonFileStore: representation of a common FileStore for use by all Participants
    graql_insert_query = 'insert $commonfilestore isa CommonFileStore, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    if item["folder"]:
        for i in item["folder"]:
            write_relationship('Containement_folder', 'contains_folder', 'CommonFileStore', item["iid"],
                               'iscontained_folder', 'Folder', i)
    if item["file"]:
        for i in item["file"]:
            write_relationship('Containement_file', 'contains_file', 'CommonFileStore', item["iid"],
                               'iscontained_file', 'File', i)

    write_relationship('Reference_owner', 'refers_owner', 'CommonFileStore', item["iid"],
                   'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def ConversionBasedUnit_template(item):
    # ConversionBasedUnit: abstract specialization of MeasurementUnit that represents a measurement unit that is
    # defined with respect to another reference unit through an explicit conversion relation
    graql_insert_query = 'insert $conversionbasedunit isa ConversionBasedUnit, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has conversionFactor "' + item["conversionFactor"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_referenceUnit', 'refers_referenceUnit', 'ConversionBasedUnit',
                       item["iid"], 'isrefered_referenceUnit', 'MeasurementUnit', item["referenceUnit"])


    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ConversionBasedUnit',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ConversionBasedUnit',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ConversionBasedUnit',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def DefinedThing_template(item):
    # DefinedThing: abstract specialization of Thing for all classes that need a human readable definition, i.e. a name
    # and a short name, and optionally explicit textual definitions, aliases and hyperlinks
    graql_insert_query = 'insert $definedthing isa DefinedThing, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DefinedThing',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DefinedThing',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DefinedThing',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)


    return graql_insert_query

def DomainOfExpertiseGroup_template(item):
    # DomainOfExpertiseGroup: representation of a group of domains of expertise (DomainOfExpertise) defined for
    # this SiteDirectory
    graql_insert_query = 'insert $domainofexpertisegroup isa DomainOfExpertiseGroup, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'DomainOfExpertiseGroup',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'DomainOfExpertiseGroup',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'DomainOfExpertiseGroup',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    for i in item["domain"]:
        write_relationship('Reference_domain', 'refers_domain', 'DomainOfExpertiseGroup',
                               item["iid"], 'isrefered_domain', 'DomainOfExpertise', i)

    return graql_insert_query

def ElementBase_template(item):
    # ElementBase: abstract superclass of ElementDefinition, ElementUsage and NestedElement that captures
    # their common properties and allows to refer to either of them
    graql_insert_query = 'insert $elementbase isa ElementBase, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ElementBase',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ElementBase',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ElementBase',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ElementBase',
                                   item["iid"], 'isrefered_category', 'Category', i)

    write_relationship('Reference_owner', 'refers_owner', 'ElementBase', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def ExclusiveOrExpression_template(item):
    # ExclusiveOrExpression: representation of a boolean exclusive or expression
    graql_insert_query = 'insert $exclusiveorexpression isa ExclusiveOrExpression, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    for i in item["term"]:
        write_relationship('Reference_term', 'refers_term', 'ExclusiveOrExpression',
                           item["iid"], 'isrefered_term', 'BooleanExpression', i)

    return graql_insert_query

def ExternalIdentifierMap_template(item):
    # ExternalIdentifierMap: representation of a mapping that relates E-TM-10-25 instance UUIDs to identifiers of
    # corresponding items in an external tool / model
    graql_insert_query = 'insert $externalidentifiermap isa ExternalIdentifierMap, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has externalModelName "' + item["externalModelName"] + '"'
    graql_insert_query += ', has externalToolName "' + item["externalToolName"] + '"'
    if item["externalToolVersion"]:
        graql_insert_query += ', has externalToolVersion "' + item["externalToolVersion"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'ExternalIdentifierMap', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["correspondence"]:
        for i in item["correspondence"]:
            write_relationship('Containement_correspondence', 'contains_correspondence', 'ExternalIdentifierMap',
                               item["iid"], 'iscontained_correspondence', 'IdCorrespondence', i)

    if item["externalFormat"]:
        write_relationship('Reference_externalFormat', 'refers_externalFor', 'ExternalIdentifierMap', item["iid"],
                           'isrefered_externalFormat', 'ReferenceSource', item["externalFormat"])

    return graql_insert_query

def File_template(item):
    # File: representation of a computer file
    graql_insert_query = 'insert $file isa File, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'File',
                               item["iid"], 'isrefered_category', 'Category', i)

    write_relationship('Reference_owner', 'refers_owner', 'File', item["iid"],
                   'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["lockedBy"]:
        write_relationship('Reference_lockedBy', 'refers_lockedBy', 'File', item["iid"],
                           'isrefered_lockedBy', 'Person', item["lockedBy"])

    for i in item["fileRevision"]:
        write_relationship('Containement_fileRevision', 'contains_fileRevision', 'File',
                           item["iid"], 'iscontained_fileRevision', 'FileRevision', i)

    return graql_insert_query

def FileRevision_template(item):
    # FileRevision: representation of a persisted revision of a File
    graql_insert_query = 'insert $filerevision isa FileRevision, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has contentHash "' + item["contentHash"] + '"'
    graql_insert_query += ', has path "' + item["path"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_creator', 'refers_creator', 'FileRevision', item["iid"],
                       'isrefered_creator', 'Participant', item["creator"])

    if item["containingFolder"]:
        write_relationship('Reference_containingFolder', 'refers_containingFolder', 'FileRevision', item["iid"],
                           'isrefered_containingFolder', 'Folder', item["containingFolder"])

    for i in item["fileType"]:
        write_relationship('Reference_fileType', 'refers_fileType', 'FileRevision', item["iid"],
                           'isrefered_fileType', 'FileType', i)

    return graql_insert_query

def FileStore_template(item):
    # FileStore: data container that may hold zero or more (possibly nested) Folders and Files
    graql_insert_query = 'insert $filestore isa FileStore, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    if item["folder"]:
        for i in item["folder"]:
            write_relationship('Containement_folder', 'contains_folder', 'FileStore', item["iid"],
                               'iscontained_folder', 'Folder', i)
    if item["file"]:
        for i in item["file"]:
            write_relationship('Containement_file', 'contains_file', 'FileStore', item["iid"],
                               'iscontained_file', 'File', i)

    write_relationship('Reference_owner', 'refers_owner', 'FileStore', item["iid"],
                   'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def Folder_template(item):
    # Folder: representation of a named folder in a FileStore that may contain files and other folders
    graql_insert_query = 'insert $folder isa Folder, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has path "' + item["path"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_creator', 'refers_creator', 'Folder', item["iid"],
                       'isrefered_creator', 'Participant', item["creator"])

    if item["containingFolder"]:
        write_relationship('Reference_containingFolder', 'refers_containingFolder', 'Folder', item["iid"],
                           'isrefered_containingFolder', 'Folder', item["containingFolder"])

    write_relationship('Reference_owner', 'refers_owner', 'Folder', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def IdCorrespondence_template(item):
    # IdCorrespondence: representation of a correspondence mapping between a single Thing
    # (identified through its iid) and an external identifier

    graql_insert_query = 'insert $idcorrespondence isa IdCorrespondence, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has internalThing "' + item["internalThing"] + '"'
    graql_insert_query += ', has externalId "' + item["externalId"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'IdCorrespondence', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def MeasurementScale_template(item):
    # MeasurementScale: representation of a measurement scale to express quantity values for a numerical Parameter,
    # i.e. a Parameter that is typed by a QuantityKind
    graql_insert_query = 'insert $measurementscale isa MeasurementScale, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'MeasurementScale',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'MeasurementScale',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'MeasurementScale',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containement_valueDefinition', 'contains_valueDefinition', 'MeasurementScale',
                               item["iid"], 'iscontained_valueDefinition', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containement_mappingToReferenceScale', 'contains_mappingToReferenceScale',
                               'MeasurementScale',
                               item["iid"], 'iscontained_mappingToReferenceScale', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refers_unit', 'MeasurementScale',
                       item["iid"], 'isrefered_unit', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def MeasurementUnit_template(item):
    # MeasurementUnit: abstract superclass that represents the [VIM] concept of "measurement unit" that is defined as
    # "real scalar quantity, defined and adopted by convention, with which any other quantity of the same kind can be
    # compared to express the ratio of the two quantities as a number"
    graql_insert_query = 'insert $measurementunit isa MeasurementUnit, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'MeasurementUnit',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'MeasurementUnit',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'MeasurementUnit',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def ModelLogEntry_template(item):
    # ModelLogEntry: representation of a logbook entry for an EngineeringModel
    graql_insert_query = 'insert $modellogentry isa ModelLogEntry, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has level "' + item["level"] + '"'

    if item["affectedItemIid"]:
        # Combine all notes into 1
        combined=''
        for i in item["affectedItemIid"]:
            combined += i + ' ,'
        graql_insert_query += ', has affectedItemIid "' + combined + '"'

    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ModelLogEntry',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["author"]:
        write_relationship('Reference_author', 'refers_author', 'ModelLogEntry',
                           item["iid"], 'isrefered_author', 'Person', item["author"])

    return graql_insert_query

def MultiRelationship_template(item):
    # MultiRelationship: representation of a relationship between multiple Things
    graql_insert_query = 'insert $multirelationship isa MultiRelationship, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'MultiRelationship',
                               item["iid"], 'isrefered_category', 'Category', i)

    write_relationship('Reference_owner', 'refers_owner', 'MultiRelationship', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["relatedThing"]:
        for i in item["relatedThing"]:
            write_relationship('Reference_relatedThing', 'refers_relatedThing', 'MultiRelationship',
                               item["iid"], 'isrefered_relatedThing', 'Thing', i)

    return graql_insert_query

def MultiRelationshipRule_template(item):
    # MultiRelationshipRule: representation of a validation rule for MultiRelationships that relate (potentially)
    # more than two CategorizableThings
    graql_insert_query = 'insert $multirelationshiprule isa MultiRelationshipRule, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has minRelated ' + str(item["minRelated"])
    graql_insert_query += ', has maxRelated ' + str(item["maxRelated"])
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'MultiRelationshipRule',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'MultiRelationshipRule',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'MultiRelationshipRule',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_relationCategory', 'refers_relationCategory', 'MultiRelationshipRule',
                       item["iid"], 'isrefered_relationCategory', 'Category', item["relationshipCategory"])

    for i in item["relatedCategory"]:
        write_relationship('Reference_relatedCategory', 'refers_relatedCategory', 'MultiRelationshipRule',
                           item["iid"], 'isrefered_relatedCategory', 'Category', i)

    return graql_insert_query

def NaturalLanguage_template(item):
    # NaturalLanguage: representation of a known natural language
    graql_insert_query = 'insert $naturallanguage isa NaturalLanguage, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has nativeName "' + item["nativeName"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def NestedElement_template(item):
    # NestedElement: representation of an explicit element of a system-of-interest in a fully expanded architectural
    # decomposition tree for one Option
    graql_insert_query = 'insert $nestedelement isa NestedElement, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isVolatile "' + str(item["isVolatile"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'NestedElement', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["nestedParameter"]:
        for i in item["nestedParameter"]:
            write_relationship('Containement_nestedParameter', 'contains_nestedParameter', 'NestedElement',
                               item["iid"], 'iscontained_nestedParameter', 'NestedParameter', i)

    write_relationship('Reference_rootElement', 'refers_rootElement', 'NestedElement', item["iid"],
                       'isrefered_rootElement', 'ElementDefinition', item["rootElement"])

    for i in item["elementUsage"]:
        write_relationship('Reference_elementUsage', 'refers_elementUsage', 'NestedElement',
                           item["iid"], 'isrefered_elementUsage', 'ElementUsage', i)

    return graql_insert_query

def NestedParameter_template(item):
    # NestedParameter: representation of a parameter with a value of a NestedElement
    graql_insert_query = 'insert $nestedparameter isa NestedParameter, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has path "' + item["path"] + '"'
    graql_insert_query += ', has formula "' + clean(item["formula"]) + '"'
    graql_insert_query += ', has isVolatile "' + str(item["isVolatile"]) + '"'
    graql_insert_query += ', has actualValue "' + str(item["actualValue"]) + '"'
    graql_insert_query += ";"

    if item["actualState"]:
        write_relationship('Reference_actualState', 'refers_actualState', 'NestedParameter', item["iid"],
                           'isrefered_actualState', 'ActualFiniteState', item["actualState"])

    write_relationship('Reference_owner', 'refers_owner', 'NestedParameter', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    write_relationship('Reference_associatedParameter', 'refers_associatedParameter', 'NestedParameter', item["iid"],
                       'isrefered_associatedParameter', 'ParameterBase', item["associatedParameter"])

    return graql_insert_query

def NotExpression_template(item):
    # NotExpression: representation of a boolean not (negation) expression
    graql_insert_query = 'insert $notexpression isa NotExpression, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_term', 'refers_term', 'NotExpression',
                           item["iid"], 'isrefered_term', 'BooleanExpression', item["term"])

    return graql_insert_query

def OrExpression_template(item):
    # OrExpression: representation of a boolean and (disjunction) expression
    graql_insert_query = 'insert $orexpression isa OrExpression, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    for i in item["term"]:
        write_relationship('Reference_term', 'refers_term', 'OrExpression',
                           item["iid"], 'isrefered_term', 'BooleanExpression', i)

    return graql_insert_query

def Organization_template(item):
    # Organization: simple representation of an organization
    graql_insert_query = 'insert $organization isa Organization, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    return graql_insert_query

def ParameterBase_template(item):
    # ParameterBase: abstract superclass that enables a common referencing mechanism for Parameter,
    # ParameterOverride and ParameterSubscription
    graql_insert_query = 'insert $parameterbase isa ParameterBase, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isOptionDependent "' + str(item["isOptionDependent"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refers_parameterType', 'ParameterBase', item["iid"],
                           'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'ParameterBase', item["iid"],
                       'isrefered_scale', 'MeasurementScale', item["scale"])

    write_relationship('Reference_owner', 'refers_owner', 'ParameterBase', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["stateDependence"]:
        write_relationship('Reference_stateDependence', 'refers_stateDependence', 'ParameterBase', item["iid"],
                           'isrefered_stateDependence', 'ActualFiniteStateList', item["stateDependence"])

    if item["group"]:
        write_relationship('Reference_group', 'refers_group', 'ParameterBase', item["iid"],
                           'isrefered_group', 'ParameterGroup', item["group"])

    return graql_insert_query

def ParameterOrOverrideBase_template(item):
    # ParameterOrOverrideBase: abstract superclass to provide a common reference to Parameter and ParameterOverride
    graql_insert_query = 'insert $parameteroroverridebase isa ParameterOrOverrideBase, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isOptionDependent "' + str(item["isOptionDependent"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refers_parameterType', 'ParameterOrOverrideBase', item["iid"],
                       'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'ParameterOrOverrideBase', item["iid"],
                           'isrefered_scale', 'MeasurementScale', item["scale"])

    if item["stateDependence"]:
        write_relationship('Reference_stateDependence', 'refers_stateDependence', 'ParameterOrOverrideBase', item["iid"],
                           'isrefered_stateDependence', 'ActualFiniteStateList', item["stateDependence"])

    if item["group"]:
        write_relationship('Reference_group', 'refers_group', 'ParameterOrOverrideBase', item["iid"],
                           'isrefered_group', 'ParameterGroup', item["group"])

    write_relationship('Reference_owner', 'refers_owner', 'ParameterOrOverrideBase', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["parameterSubscription"]:
        for i in item["parameterSubscription"]:
            write_relationship('Containement_parameterSubscription', 'contains_parameterSubscription', 'ParameterOrOverrideBase', item["iid"],
                               'iscontained_parameterSubscription', 'ParameterSubscription', i)

    return graql_insert_query

def ParameterOverride_template(item):
    # ParameterOverride: representation of a parameter at ElementUsage level that allows to override the values of a
    # Parameter defined at ElementDefinition level
    graql_insert_query = 'insert $parameteroverride isa ParameterOverride, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"


    write_relationship('Reference_owner', 'refers_owner', 'ParameterOverride', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["valueSet"]:
        for i in item["valueSet"]:
            write_relationship('Containement_valueSet', 'contains_valueSet', 'ParameterOverride', item["iid"],
                               'iscontained_valueSet', 'ParameterOverrideValueSet', i)

    if item["parameterSubscription"]:
        for i in item["parameterSubscription"]:
            write_relationship('Containement_parameterSubscription', 'contains_parameterSubscription', 'ParameterOverride', item["iid"],
                               'iscontained_parameterSubscription', 'ParameterSubscription', i)

    write_relationship('Reference_parameter', 'refers_parameter', 'ParameterOverride', item["iid"],
                       'isrefered_parameter', 'Parameter', item["parameter"])

    return graql_insert_query

def ParameterOverrideValueSet_template(item):
    # ParameterOverrideValueSet: representation of the switch setting and all values for a ParameterOverride
    graql_insert_query = 'insert $parameteroverridevalueset isa ParameterOverrideValueSet, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has valueSwitch "' + item["valueSwitch"] + '"'
    graql_insert_query += ', has computed "' + clean(item["computed"]) + '"'
    graql_insert_query += ', has manual "' + clean(item["manual"]) + '"'
    graql_insert_query += ', has reference "' + clean(item["reference"]) + '"'
    graql_insert_query += ', has published "' + clean(item["published"]) + '"'
    graql_insert_query += ', has formula "' + clean(item["formula"]) + '"'
    graql_insert_query += ";"


    write_relationship('Reference_parameterValueSet', 'refers_parameterValueSet', 'ParameterOverrideValueSet', item["iid"],
                       'isrefered_parameterValueSet', 'ParameterValueSet', item["parameterValueSet"])


    return graql_insert_query

def ParameterType_template(item):
    # ParameterType: abstract superclass that represents the common characteristics of any parameter type
    graql_insert_query = 'insert $parametertype isa ParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberOfValues ' + str(item["numberOfValues"])
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ParameterType',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def ParameterValueSetBase_template(item):
    # ParameterValueSetBase: abstract superclass representing the switch setting and values of a Parameter or
    # ParameterOverride and serves as a common reference type for ParameterValueSet and ParameterOverrideValueSet

    graql_insert_query = 'insert $parametervaluesetbase isa ParameterValueSetBase, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has valueSwitch "' + item["valueSwitch"] + '"'
    graql_insert_query += ', has computed "' + clean(item["computed"]) + '"'
    graql_insert_query += ', has manual "' + clean(item["manual"]) + '"'
    graql_insert_query += ', has reference "' + clean(item["reference"]) + '"'
    graql_insert_query += ', has actualValue "' + clean(item["actualValue"]) + '"'
    graql_insert_query += ', has published "' + clean(item["published"]) + '"'
    graql_insert_query += ', has formula "' + clean(item["formula"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'ParameterValueSetBase', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["actualState"]:
        write_relationship('Reference_actualState', 'refers_actualState', 'ParameterValueSetBase', item["iid"],
                           'isrefered_actualState', 'ActualFiniteState', item["actualState"])

    if item["actualOption"]:
        write_relationship('Reference_actualOption', 'refers_actualOption', 'ParameterValueSetBase', item["iid"],
                           'isrefered_actualOption', 'Option', item["actualOption"])

    return graql_insert_query

def ParametricConstraint_template(item):
    # ParametricConstraint: representation of a single parametric constraint consisting of a ParameterType that acts
    # as a variable, a relational operator and a value, in the form of a mathematical equality or inequality
    graql_insert_query = 'insert $parametricconstraint isa ParametricConstraint, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"


    if item["topExpression"]:
        write_relationship('Reference_topExpression', 'refers_topExpression', 'ParametricConstraint',
                           item["iid"],
                           'isrefered_topExpression', 'BooleanExpression', item["topExpression"])

    write_relationship('Reference_owner', 'refers_owner', 'ParametricConstraint', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    for i in item["expression"]:
        write_relationship('Containement_expression', 'contains_expression', 'ParametricConstraint',
                           item["iid"], 'iscontained_expression', 'BooleanExpression', i)


    return graql_insert_query

# -----------------------------

def ParticipantPermission_template(item):
    # ParticipantPermission: representation of a permission to access a given (sub)set of data in an EngineeringModel
    graql_insert_query = 'insert $participantpermission isa ParticipantPermission, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has accessRight "' + item["accessRight"] + '"'
    graql_insert_query += ', has objectClass "' + item["objectClass"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"


    return graql_insert_query

def ParticipantRole_template(item):
    # ParticipantRole: representation of the named role of a Participant that defines the Participant's permissions
    # and access rights with respect to data in an EngineeringModel
    graql_insert_query = 'insert $participantrole isa ParticipantRole, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ParticipantRole',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ParticipantRole',
                               item["iid"],
                               'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ParticipantRole',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["participantPermission"]:
        for i in item["participantPermission"]:
            write_relationship('Containement_participantPermission', 'contains_participantPermission', 'ParticipantRole',
                               item["iid"], 'iscontained_participantPermission', 'ParticipantPermission', i)

    return graql_insert_query

def PersonPermission_template(item):
    # PersonPermission: representation of a permission to access a given (sub)set of data in a SiteDirectory
    graql_insert_query = 'insert $personpermission isa PersonPermission, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has accessRight "' + item["accessRight"] + '"'
    graql_insert_query += ', has objectClass "' + item["objectClass"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    return graql_insert_query

def PersonRole_template(item):
    # PersonRole: representation of the named role of a Person (a user) that defines the Person's permissions and
    # access rights with respect to data in a SiteDirectory
    graql_insert_query = 'insert $personrole isa PersonRole, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'PersonRole',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'PersonRole',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'PersonRole',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["personPermission"]:
        for i in item["personPermission"]:
            write_relationship('Containement_personPermission', 'contains_personPermission', 'PersonRole',
                               item["iid"], 'iscontained_personPermission', 'PersonPermission', i)

    return graql_insert_query

def PossibleFiniteState_template(item):
    # PossibleFiniteState: representation of one of the finite states of a PossibleFiniteStateList
    graql_insert_query = 'insert $possiblefinitestate isa PossibleFiniteState, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'PossibleFiniteState',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'PossibleFiniteState',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'PossibleFiniteState',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_owner', 'refers_owner', 'PossibleFiniteState', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def PossibleFiniteStateList_template(item):
    # PossibleFiniteStateList: specialization of CategorizableThing that defines a finite ordered collection of
    # one or more named States
    graql_insert_query = 'insert $possiblefinitestatelist isa PossibleFiniteStateList, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'PossibleFiniteStateList',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'PossibleFiniteStateList',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'PossibleFiniteStateList',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_owner', 'refers_owner', 'PossibleFiniteStateList', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    for i in item["possibleState"]:
        write_relationship('Containement_possibleState', 'contains_possibleState', 'PossibleFiniteStateList', item["iid"],
                           'iscontained_possibleState', 'PossibleFiniteState', i)

    if item["defaultState"]:
        write_relationship('Reference_defaultState', 'refers_defaultState', 'PossibleFiniteStateList',
                           item["iid"], 'isrefered_defaultState', 'PossibleFiniteState', item["defaultState"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'PossibleFiniteStateList',
                               item["iid"], 'isrefered_category', 'Category', i)

    return graql_insert_query

def QuantityKind_template(item):
    # QuantityKind: representation of a numerical ScalarParameterType
    graql_insert_query = 'insert $quantitykind isa QuantityKind, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberOfValues ' + str(item["numberOfValues"])
    graql_insert_query += ', has quantityDimensionExpression "' + item["quantityDimensionExpression"] + '"'
    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'
    if item["quantityDimensionExponent"]:
        combined = ''
        for i in item["quantityDimensionExponent"]:
            combined += clean(i) + ' ,'
        graql_insert_query += ', hasq uantityDimensionExponent "' + combined + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'QuantityKind',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'QuantityKind',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'QuantityKind',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'QuantityKind',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refers_possibleScale', 'QuantityKind',
                               item["iid"], 'isrefered_possibleScale', 'MeasurementScale', i)

    write_relationship('Reference_defaultScale', 'refers_defaultScale', 'SpecializedQuantityKind',
                       item["iid"], 'isrefered_defaultScale', 'MeasurementScale', item["defaultScale"])

    if item["allPossibleScale"]:
        for i in item["allPossibleScale"]:
            write_relationship('Reference_allPossibleScale', 'refers_allPossibleScale', 'QuantityKind',
                               item["iid"], 'isrefered_allPossibleScale', 'MeasurementScale', i)

    return graql_insert_query

def ReferenceDataLibrary_template(item):
    # ReferenceDataLibrary: named library that holds a set of (predefined) reference data that can be loaded at runtime
    # and used in an EngineeringModel
    graql_insert_query = 'insert $referencedatalibrary isa ReferenceDataLibrary, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["definedCategory"]:
        for i in item["definedCategory"]:
            write_relationship('Containement_definedCategory', 'contains_definedCategory', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_definedCategory', 'Category', i)

    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containement_parameterType', 'contains_parameterType', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_parameterType', 'ParameterType', i)

    if item["scale"]:
        for i in item["scale"]:
            write_relationship('Containement_scale', 'contains_scale', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_scale', 'MeasurementScale', i)

    if item["unitPrefix"]:
        for i in item["unitPrefix"]:
            write_relationship('Containement_unitPrefix', 'contains_unitPrefix', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_unitPrefix', 'UnitPrefix', i)

    if item["unit"]:
        for i in item["unit"]:
            write_relationship('Containement_unit', 'contains_unit', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_unit', 'MeasurementUnit', i)

    if item["fileType"]:
        for i in item["fileType"]:
            write_relationship('Containement_fileType', 'contains_fileType', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_fileType', 'FileType', i)

    if item["glossary"]:
        for i in item["glossary"]:
            write_relationship('Containement_glossary', 'contains_glossary', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_glossary', 'Glossary', i)

    if item["referenceSource"]:
        for i in item["referenceSource"]:
            write_relationship('Containement_referenceSource', 'contains_referenceSource', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_referenceSource', 'ReferenceSource', i)

    if item["rule"]:
        for i in item["rule"]:
            write_relationship('Containement_rule', 'contains_rule', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_rule', 'Rule', i)

    if item["constant"]:
        for i in item["constant"]:
            write_relationship('Containement_constant', 'contains_constant', 'ReferenceDataLibrary',
                               item["iid"], 'iscontained_constant', 'Constant', i)

    if item["baseQuantityKind"]:
        for i in item["baseQuantityKind"]:
            write_relationship('Reference_baseQuantityKind', 'refers_baseQuantityKind', 'ReferenceDataLibrary',
                               item["iid"], 'isrefered_baseQuantityKind', 'QuantityKind', i["v"])

    if item["baseUnit"]:
        for i in item["baseUnit"]:
            write_relationship('Reference_baseUnit', 'refers_baseUnit', 'ReferenceDataLibrary',
                               item["iid"], 'isrefered_baseUnit', 'MeasurementUnit', i)

    if item["requiredRdl"]:
        write_relationship('Reference_requiredRdl', 'refers_requiredRdl', 'ReferenceDataLibrary',
                           item["iid"], 'isrefered_requiredRdl', 'SiteReferenceDataLibrary', item["requiredRdl"])

    return graql_insert_query

def ReferencerRule_template(item):
    # ReferencerRule: representation of a validation rule for ElementDefinitions and the
    # referencedElement NestedElements
    graql_insert_query = 'insert $referencerrule isa ReferencerRule, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has minReferenced ' + str(item["minReferenced"])
    graql_insert_query += ', has maxReferenced ' + str(item["maxReferenced"])
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ReferencerRule',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ReferencerRule',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ReferencerRule',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_referencingCategory', 'refers_referencingCategory', 'ReferencerRule',
                       item["iid"], 'isrefered_referencingCategory', 'Category', item["referencingCategory"])

    for i in item["referencedCategory"]:
        write_relationship('Reference_referencedCategory', 'refers_referencedCategory', 'ReferencerRule',
                           item["iid"], 'isrefered_referencedCategory', 'Category', i)

    return graql_insert_query

def RelationalExpression_template(item):
    # RelationalExpression: representation of a mathematical equality or inequality defined by a ParameterType
    # that acts as a variable, a relational operator and a v
    graql_insert_query = 'insert $relationalexpression isa RelationalExpression, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ', has relationalOperator "' + item["relationalOperator"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refers_parameterType', 'RelationalExpression', item["iid"],
                       'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'RelationalExpression', item["iid"],
                           'isrefered_scale', 'MeasurementScale', item["scale"])

    return graql_insert_query

def Relationship_template(item):
    # Relationship: representation of a relationship between two or more Things
    graql_insert_query = 'insert $relationship isa Relationship, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'Relationship',
                               item["iid"], 'isrefered_category', 'Category', i)

    write_relationship('Reference_owner', 'refers_owner', 'Relationship', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def Requirement_template(item):
    # Requirement: representation of a requirement in a RequirementsSpecification
    graql_insert_query = 'insert $requirement isa Requirement, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Requirement',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Requirement',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Requirement',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["group"]:
        write_relationship('Reference_group', 'refers_group', 'Requirement', item["iid"],
                           'isrefered_group', 'ParameterGroup', item["group"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'Requirement',
                               item["iid"], 'isrefered_category', 'Category', i)

    write_relationship('Reference_owner', 'refers_owner', 'Requirement', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["parametricConstraint"]:
        for i in item["parametricConstraint"]:
            write_relationship('Containement_parametricConstraint', 'contains_parametricConstraint', 'Requirement',
                               item["iid"], 'iscontained_parametricConstraint', 'ParametricConstraint', i)

    if item["parameterValue"]:
        for i in item["parameterValue"]:
            write_relationship('Containement_parameterValue', 'contains_parameterValue', 'Requirement',
                               item["iid"], 'iscontained_parameterValue', 'SimpleParameterValue', i)

    return graql_insert_query

def RequirementsContainer_template(item):
    # RequirementsContainer: abstract superclass that serves as a common reference to both RequirementsSpecification
    # and RequirementsGroup
    graql_insert_query = 'insert $requirementscontainer isa RequirementsContainer, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'RequirementsContainer',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'RequirementsContainer',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'RequirementsContainer',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_owner', 'refers_owner', 'RequirementsContainer', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["group"]:
        for i in item["group"]:
            write_relationship('Containement_group', 'contains_group', 'RequirementsContainer',
                               item["iid"], 'iscontained_group', 'RequirementsGroup', i)

    return graql_insert_query

def RequirementsGroup_template(item):
    # RequirementsGroup: representation of a grouping of Requirements
    graql_insert_query = 'insert $requirementsgroup isa RequirementsGroup, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'RequirementsGroup',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'RequirementsGroup',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'RequirementsGroup',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_owner', 'refers_owner', 'RequirementsGroup', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["group"]:
        for i in item["group"]:
            write_relationship('Containement_group', 'contains_group', 'RequirementsGroup',
                               item["iid"], 'iscontained_group', 'RequirementsGroup', i)

    return graql_insert_query

def Rule_template(item):
    # Rule: representation of a validation or constraint rule for CategorizableThings and relations between them
    graql_insert_query = 'insert $rule isa Rule, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'Rule',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'Rule',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'Rule',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    return graql_insert_query

def RuleVerification_template(item):
    # RuleVerification: representation of built-in data model rule or user-defined Rule to be verified and
    # its current verification result
    graql_insert_query = 'insert $ruleverification isa RuleVerification, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    if item["executedOn"]:
        graql_insert_query += ', has executedOn "' + item["executedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has status "' + item["status"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'RuleVerification', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["violation"]:
        for i in item["violation"]:
            write_relationship('Containement_violation', 'contains_violation', 'RuleVerification',
                               item["iid"], 'iscontained_violation', 'RuleViolation', i)

    return graql_insert_query

def RuleVerificationList_template(item):
    # RuleVerificationList: representation of a list of RuleVerifications
    graql_insert_query = 'insert $ruleverificationlist isa RuleVerificationList, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'RuleVerificationList',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'RuleVerificationList',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'RuleVerificationList',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    write_relationship('Reference_owner', 'refers_owner', 'RuleVerificationList', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["ruleVerification"]:
        for i in item["ruleVerification"]:
            write_relationship('Containement_ruleVerification', 'contains_ruleVerification', 'RuleVerificationList',
                               item["iid"], 'iscontained_ruleVerification', 'RuleVerification', i)

    return graql_insert_query

def RuleViolation_template(item):
    # RuleViolation: representing of information concerning the violation of a built-in or user-defined rule
    graql_insert_query = 'insert $ruleviolation isa RuleViolation, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has description "' + item["description"] + '"'

    if item["violatingThing"]:
        # Combine all notes into 1 as Grakn only accepts one instance of one attribute
        combined = ''
        for i in item["violatingThing"]:
            combined += clean(i) + ' ,'
        graql_insert_query += ', has violatingThing "' + combined + '"'

    graql_insert_query += ";"

    return graql_insert_query

def ScalarParameterType_template(item):
    # ScalarParameterType: representation of a scalar parameter type
    graql_insert_query = 'insert $scalarparametertype isa ScalarParameterType, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberOfValues ' + str(item["numberOfValues"])
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'ScalarParameterType',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'ScalarParameterType',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'ScalarParameterType',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'ScalarParameterType',
                               item["iid"], 'isrefered_category', 'Category', i)
    return graql_insert_query

def SimpleParameterValue_template(item):
    # SimpleParameterValue: representation of a single parameter with value for a SimpleParameterizableThing
    graql_insert_query = 'insert $simpleparametervalue isa SimpleParameterValue, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refers_parameterType', 'SimpleParameterValue', item["iid"],
                       'isrefered_parameterType', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refers_scale', 'SimpleParameterValue', item["iid"],
                           'isrefered_scale', 'MeasurementScale', item["scale"])

    write_relationship('Reference_owner', 'refers_owner', 'SimpleParameterValue', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def SimpleParameterizableThing_template(item):
    # SimpleParameterizableThing: representation of a Thing that can be characterized by one or
    # more parameters with values
    graql_insert_query = 'insert $simpleparameterizablething isa SimpleParameterizableThing, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containement_alias', 'contains_alias', 'SimpleParameterizableThing',
                               item["iid"], 'iscontained_alias', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containement_definition', 'contains_definition', 'SimpleParameterizableThing',
                               item["iid"], 'iscontained_definition', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containement_hyperLink', 'contains_hyperLink', 'SimpleParameterizableThing',
                               item["iid"], 'iscontained_hyperLink', 'HyperLink', i)

    if item["parameterValue"]:
        for i in item["parameterValue"]:
            write_relationship('Containement_parameterValue', 'contains_parameterValue', 'SimpleParameterizableThing',
                               item["iid"], 'iscontained_parameterValue', 'SimpleParameterValue', i)

    write_relationship('Reference_owner', 'refers_owner', 'SimpleParameterizableThing', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def SiteLogEntry_template(item):
    # SiteLogEntry: representation of a logbook entry for a SiteDirectory
    graql_insert_query = 'insert $sitelogentry isa SiteLogEntry, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has level "' + item["level"] + '"'

    if item["affectedItemIid"]:
        # Combine all notes into 1
        combined=''
        for i in item["affectedItemIid"]:
            combined += i + ' ,'
        graql_insert_query += ', has affectedItemIid "' + combined + '"'

    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refers_category', 'SiteLogEntry',
                               item["iid"], 'isrefered_category', 'Category', i)

    if item["author"]:
        write_relationship('Reference_author', 'refers_author', 'SiteLogEntry',
                           item["iid"], 'isrefered_author', 'Person', item["author"])
    return graql_insert_query

def TelephoneNumber_template(item):
    # TelephoneNumber: representation of a telephone number
    graql_insert_query = 'insert $telephoneNumber isa TelephoneNumber, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has vcardType "' + item["vcardType"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def TopContainer_template(item):
    # TopContainer: representation of a top container
    graql_insert_query = 'insert $topcontainer isa TopContainer, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def UserPreference_template(item):
    # UserPreference: representation of a user-defined preference
    graql_insert_query = 'insert $userpreference isa UserPreference, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def UserRuleVerification_template(item):
    # UserRuleVerification: representation of the verification of a user-defined Rule in one of
    # the required ReferenceDataLibraries
    graql_insert_query = 'insert $userruleverification isa UserRuleVerification, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    if item["executedOn"]:
        graql_insert_query += ', has executedOn "' + item["executedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has status "' + item["status"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refers_owner', 'UserRuleVerification', item["iid"],
                       'isrefered_owner', 'DomainOfExpertise', item["owner"])

    if item["violation"]:
        for i in item["violation"]:
            write_relationship('Containement_violation', 'contains_violation', 'UserRuleVerification',
                               item["iid"], 'iscontained_violation', 'RuleViolation', i)

    write_relationship('Reference_rule', 'refers_rule', 'UserRuleVerification', item["iid"],
                       'isrefered_rule', 'Rule', item["rule"])


    return graql_insert_query

def Thing_template(item):
    # Thing: top level abstract superclass from which all domain concept classes in the model inherit
    graql_insert_query = 'insert $thing isa Thing, has revisionNumber ' + \
                         str(item["revisionNumber"]) + ', has classKind "' + item["classKind"] + \
                         '", has iid "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

# -------------------------------------------------------------
# END
# -------------------------------------------------------------

