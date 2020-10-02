# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
This script is used for case study 1 of the paper:
A.Berquand & A.Riccardi (2020) FROM ENGINEERING MODELS TO KNOWLEDGE GRAPH: DELIVERING NEW
INSIGHTS INTO MODELS. In Proc. of SECESA 2020 (Digital Event)

After inferring new "isIncludedInMassBudget" relationships via the rules defined in EMRules.gql,
this script is used to extract from the populated Grakn KG, all data relevant to generating a dry mass budget for
each design option of the  engineering model iteration.

Pre-requisite:
- Grakn 1.8.0 installed (https://grakn.ai/),
- Grakn Workbase 1.3.0 (https://grakn.ai/),
- Grakn server running,
- Engineering Model Schema EMSchema.gql loaded into a Grakn keyspace (see README)
- Engineering Model(s) has (have) been migrated to KG through migrate_em_json.py (see README)
- Rules defined in EMRules.gql have been defined in the Grakn KG (in same keyspace) (see README)

Input: keyspace of populated Grakn KG
Output: Mass Budget for each design option of the iteration(s)
'''

from grakn.client import GraknClient
import re

# -----------------------------------------------------------------------------------------
# COMPUTE MASS BUDGETS OF EACH OPTIONS FROM ITERATION
# -----------------------------------------------------------------------------------------
# active Grakn keyspace where we have migrated the Engineering Models
keyspace_name="strathcube5"
# default system margin to use in mass budget
system_margin = 10

# Connection to Grakn session via Python client
with GraknClient(uri="localhost:48555") as client:
    with client.session(keyspace=keyspace_name) as session:
        # session = communication tunnel to a given keyspace on the running Grakn server.
        with session.transaction().read() as read_transaction:
            print("Session Opened")

            # Identify All Options
            answer_getOptions = read_transaction.query("match $x isa Option; get $x;").get()
            options = [parameter.get("x") for parameter in answer_getOptions]
            print(len(options), ' Design options found in this iteration.')

            # for each option:
            for opt in options:

                # Get option name
                for item in opt.as_remote(read_transaction).attributes():
                    if item.type().label() == "name":
                        opt_name=item.value()

                print('\n -----------------------------------------------------------------------------')
                print(' MASS BUDGET - OPTION ', opt_name)
                print('-----------------------------------------------------------------------------\n')

                #Init Budget
                MassBudget=0

                # Get all elements in option's budget
                answer_iterator = read_transaction.query("match $x id " + opt.id + "; ($x, $y) isa "
                                                         "includedInMassBudget; get $y;").get()
                elements = [parameter.get("y") for parameter in answer_iterator]

                print('Identified ', len(elements), ' mass measures part of Mass Budget of', opt_name ,'\n')
                print('ID | Element | Mass One Unit | Scale | Quantity | Margin | Total ')

                # For each ParameterValueSet:
                for el in elements:

                    # For each attribute of this ParameterValueSet:
                    for a in el.as_remote(read_transaction).attributes():

                        # get ElementDefinition name
                        answer_RelatedEntity = read_transaction.query("match $x id "+ el.id + "; ($y, $x) isa "
                                                                                               "Containement_valueSet; "
                                                                                               "($z, $y) isa Containement_parameter;get $z;").get()
                        relatedEntity = [parameter.get("z") for parameter in answer_RelatedEntity]
                        for entity in relatedEntity:
                            for attribute in entity.as_remote(read_transaction).attributes():
                                if attribute.type().label() == "name":
                                    nameEntity = attribute.value()

                        # get Scale
                        answer_GetScale = read_transaction.query(
                            "match $x id " + el.id + "; ($y, $x) isa Containement_valueSet; ($y, $z) isa Reference_scale;get $z;").get()
                        answers = [parameter.get("z") for parameter in answer_GetScale]
                        default_scale = 'kilogram'
                        scale = default_scale
                        for ans in answers:
                            for attribute in ans.as_remote(read_transaction).attributes():
                                if attribute.type().label() == "name":
                                    scale = attribute.value()

                        # get Number of Elements - Potentially Option Dependent
                        default_quantity = 1
                        quantity = default_quantity

                        answer_QuantityOptionDept = read_transaction.query(
                            "match $x id " + el.id + "; ($y, $x) isa Containement_valueSet; ($z, $y) isa Containement_parameter; "
                                                     "($z,$a) isa Containement_parameter; ($a, $b) isa Reference_parameterType; "
                                                     "$b has name 'number of items'; get $a;").get()
                        qtyOptionDep = [parameter.get("a") for parameter in answer_QuantityOptionDept]

                        for dep in qtyOptionDep:
                            for attribute in dep.as_remote(read_transaction).attributes():
                                if attribute.type().label() == 'isOptionDependent':
                                    if attribute.value() == True:
                                        answer_Quantity = read_transaction.query("match $a id " + dep.id + "; ($a, $b) isa Containement_valueSet; $c id " + opt.id + "; ($b, $c) isa Reference_actualOption; get $b;").get()
                                        qty = [parameter.get("b") for parameter in answer_Quantity]

                                        for q in qty:
                                            for item in q.as_remote(read_transaction).attributes():
                                                if item.type().label() == "published":
                                                    quantity = item.value()
                                                    quantity = quantity.replace('[', '')
                                                    quantity = quantity.replace(']', '')
                                                    quantity = int(quantity)

                                    elif attribute.value() == False:
                                        answer_Quantity = read_transaction.query("match $a id " + dep.id + "; ($a, $b) isa Containement_valueSet; get $b;").get()
                                        qty = [parameter.get("b") for parameter in answer_Quantity]
                                        for q in qty:
                                            for item in q.as_remote(read_transaction).attributes():
                                                if item.type().label() == "published":
                                                    quantity = item.value()
                                                    quantity = quantity.replace('[', '')
                                                    quantity = quantity.replace(']', '')
                                                    quantity = int(quantity)


                        # get Mass Margin - Potentially Option Dependent
                        default_margin = 20
                        massMargin = default_margin

                        answer_GetMassMargin = read_transaction.query(
                            "match $x id " + el.id + "; ($y, $x) isa Containement_valueSet; ($z, $y) isa Containement_parameter; "
                                                     "($z,$a) isa Containement_parameter; ($a, $b) isa Reference_parameterType; "
                                                     "$b has name 'mass margin'; get $a;").get()
                        marginDependency = [parameter.get("a") for parameter in answer_GetMassMargin]

                        for mDep in marginDependency:
                            for attribute in mDep.as_remote(read_transaction).attributes():
                                if attribute.type().label() == 'isOptionDependent':
                                    if attribute.value() == True:
                                        answer_MassMargin = read_transaction.query(
                                            "match $a id " + mDep.id + "; ($a, $b) isa Containement_valueSet; $c id " + opt.id + "; ($b, $c) isa Reference_actualOption; get $b;").get()
                                        mm = [parameter.get("b") for parameter in answer_MassMargin]
                                        for m in mm:
                                            for item in m.as_remote(read_transaction).attributes():
                                                if item.type().label() == "published":
                                                    massMargin = item.value()
                                                    massMargin = massMargin.replace('[', '')
                                                    massMargin = massMargin.replace(']', '')
                                                    massMargin = int(massMargin)

                                    elif attribute.value() == False:
                                        answer_MassMargin = read_transaction.query(
                                            "match $a id " + mDep.id + "; ($a, $b) isa Containement_valueSet; get $b;").get()
                                        mm = [parameter.get("b") for parameter in answer_MassMargin]
                                        for m in mm:
                                            for item in m.as_remote(read_transaction).attributes():
                                                if item.type().label() == "published":
                                                    massMargin = item.value()
                                                    massMargin = massMargin.replace('[', '')
                                                    massMargin = massMargin.replace(']', '')
                                                    massMargin = int(massMargin)
                                    else:
                                        print("Applied Default Mass Margin")

                        # get Mass Value for One Unit
                        if a.type().label() == "published":
                            massValue = a.value()
                            massValue = massValue.replace('[', '')
                            massValue = massValue.replace(']', '')
                            massValue = float(massValue)

                            Total = round(massValue * quantity * (1+massMargin/100), 5)

                            if scale != 'kilogram':
                                if scale == 'gram':
                                    Total = Total / 1000
                                if scale == 'milligram':
                                    Total = Total / 1000000
                                if scale == 'tonne':
                                    Total = Total * 1000

                            print(el.id, ' | ', nameEntity, ' | ', massValue, ' | ', scale, ' | ', quantity, ' | ', massMargin, ' | ', Total)
                            MassBudget = MassBudget + Total

                print("\n Mass Budget for Option - with equipment margin and w/o system margin)", MassBudget,
                      " kg.")
                MassBudget_systemMargin= MassBudget * (1 + system_margin/100)
                print("Mass Budget for Option - with equipment margin and with", system_margin ,"% system margin)", MassBudget_systemMargin,
                      " kg.")
