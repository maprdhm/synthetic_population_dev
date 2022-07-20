#!/usr/bin/env python
# coding: utf-8

import glob
import pandas as pd
import numpy as np
import os
import csv
import sys


if __name__ == '__main__':
    path = sys.argv[1]
    year = sys.argv[2]
    from_ = int(sys.argv[3])

    # Import the csv files containing the persons and households of the area of study

    # Read CSV file containing the households
    df_households_NE_extended__dir = path + year + '/NE_only'  # use your path
    df_households_NE_extended_file = os.path.join(df_households_NE_extended__dir, "df_households_NE_clean.csv")
    df_households_NE_extended = pd.read_csv(df_households_NE_extended_file, index_col=None, header=0)

    # Read CSV file containing the employed persons
    df_persons_NE_employed_dir = path + year + '/NE_only'  # use your path
    df_persons_NE_employed_file = os.path.join(df_persons_NE_employed_dir, "df_persons_NE_employed_20211122.csv")
    df_persons_NE_employed = pd.read_csv(df_persons_NE_employed_file, index_col=None, header=0)#!/usr/bin/env python

    # Read CSV file containing the unemployed persons
    df_persons_NE_unemployed_dir = path + year + '/NE_only'  # use your path
    df_persons_NE_unemployed_file = os.path.join(df_persons_NE_unemployed_dir, "df_persons_NE_unemployed_2021112.csv")
    df_persons_NE_unemployed = pd.read_csv(df_persons_NE_unemployed_file, index_col=None, header=0)

    # Import the csv file containing information about the occupations from Census 2011
    # Read CSV file containing the occupations per OA level, based on age\n",
    ## This dataset contains information about the number people in each occupation per location (OA area) and range of age
    df_occupation_dir = path +'Data'  # use your path
    df_occupation_file = os.path.join(df_occupation_dir, "LC6112EW.csv")
    df_occupation = pd.read_csv(df_occupation_file, index_col=None, header=0)


    df_occupation = df_occupation[df_occupation.columns.drop(list(df_occupation.filter(regex='All')))]

    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 1. Managers, directors and senior officials; ',
                                                              'occupation_1_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 2. Professional occupations; ', 'occupation_2_',
                                                              regex=False)
    df_occupation.columns = df_occupation.columns.str.replace(
        'Occupation: 3. Associate professional and technical occupations; ', 'occupation_3_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 4. Administrative and secretarial occupations; ',
                                                              'occupation_4_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 5. Skilled trades occupations; ',
                                                              'occupation_5_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace(
        'Occupation: 6. Caring, leisure and other service occupations; ', 'occupation_6_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 7. Sales and customer service occupations; ',
                                                              'occupation_7_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 8. Process, plant and machine operatives; ',
                                                              'occupation_8_', regex=False)
    df_occupation.columns = df_occupation.columns.str.replace('Occupation: 9. Elementary occupations; ', 'occupation_9_',
                                                              regex=False)

    df_occupation.columns = df_occupation.columns.str.replace('Age: Age 16 to 24; measures: Value', '16_24')
    df_occupation.columns = df_occupation.columns.str.replace('Age: Age 25 to 34; measures: Value', '25_34')
    df_occupation.columns = df_occupation.columns.str.replace('Age: Age 35 to 49; measures: Value', '35_49')
    df_occupation.columns = df_occupation.columns.str.replace('Age: Age 50 to 64; measures: Value', '50_64')
    df_occupation.columns = df_occupation.columns.str.replace('Age: Age 65 and over; measures: Value', '65_120')

    # Concatenate the dataframes of employed and unemployed

    ## Concatenate employed and unemployed people
    df_persons_NE_occupation = (pd.concat([df_persons_NE_employed, df_persons_NE_unemployed]))

    # Create a new column 'Occupation'

    # Create a new column for the Occupation
    df_persons_NE_occupation['Occupation'] = np.nan

    # Keep only those people older than 15. Data from the Census is only showing people >15

    ## Get only those that are >=16 years old only\n",
    df_persons_NE_occupation_16_120 = df_persons_NE_occupation.loc[(df_persons_NE_occupation['Age'] >= 16)]

    # Start developing the code to assing the different occupations to the population, based on
    #
    #     - age ranges and OA area (LC6112EW census2011 table)
    #     - occupation_conversor value (project number of each occupation from 2011 to 2021 based on data from Table 10b. Employemnt by occupation (SOC2010) and industry (SIC2007)
    #     - gender proportion (annual population survey - workplace analysis (Table 10b. Employemnt by occupation (SOC2010) and industry (SIC2007))
    #     - ratio_people_2021_2011: project the number of people in each OA area from 2011 to 2021"

    # List for the gender types: male (1) and female (2)
    gender_list = [1, 2]

    # List containing the range of ages
    age_range_list = [(16, 24), (25, 34), (35, 49), (50, 64), (65, 120)]

    ## LIST OF OA_AREAS that has been generated before
    # Create a list with all Households unique ID values
    AreaOA_list = df_households_NE_extended['Area_OA'].tolist()
    # Remove duplicates
    AreaOA_list = list(set(AreaOA_list))

    # Create an empty list where the small blocks of dataframes of INACTIVE people will be stored
    persons_NE_occupations_first_selection = []
    persons_NE_occupations_second_selection = []
    persons_NE_occupations_third_selection = []

    # Create a variable that counts the number of OA areas iterated
    OA_area_counter = 0

    # Create a variable that counts th number of iterations needed to achieve the goal of a % within +-2% when compared to 2021 values
    iteration_counter = 0

    # list containing the number of occupations in the order they are going to be assigned, per sex type


    ## VERSION WM
    occupation_list_males = [2, 3, 5, 8, 1, 9, 4, 7, 6]
    occupation_list_females = [2, 4, 6, 3, 9, 7, 1, 5, 8]


    #### ALTERNATIVE OPTION for the last two selections of occupation type
    ## VERSIONS 7
    # Unchanged for WM bc don't know what to put ...
    occupation_list_males_last = [2, 3, 9, 4, 5, 1, 8, 6, 7]
    occupation_list_females_last = [2, 3, 9, 1, 5, 7, 8, 4, 6]

    # INITIAL values to transform data from 2011 to 2021 based on the relationship (2021/2011)
    # These values will be updated everytime an iteration is not within +-1% of the value of 2021
    # There is not any difference between sex because LC6112EW census2011 table does not provide differences in sex.
    ## Values are grouped (males + females)
    ## This values were obtained from the following excel file:
    #### sheet1
    occupation_1_conversor = 1.095
    occupation_2_conversor = 1.437
    occupation_3_conversor = 1.389
    occupation_4_conversor = 1.068
    occupation_5_conversor = 0.810
    occupation_6_conversor = 1.130
    occupation_7_conversor = 0.640
    occupation_8_conversor = 1.137
    occupation_9_conversor = 0.777

    ## % of males in each occupation type
    percentage_1_occupation_1 = 66.73
    percentage_1_occupation_2 = 52.19
    percentage_1_occupation_3 = 51.18
    percentage_1_occupation_4 = 23.86
    percentage_1_occupation_5 = 95.13
    percentage_1_occupation_6 = 14.37
    percentage_1_occupation_7 = 34.41
    percentage_1_occupation_8 = 94.85
    percentage_1_occupation_9 = 54.88

    ## % of females in each occupation type
    percentage_2_occupation_1 = 33.27
    percentage_2_occupation_2 = 47.81
    percentage_2_occupation_3 = 48.82
    percentage_2_occupation_4 = 76.14
    percentage_2_occupation_5 = 4.87
    percentage_2_occupation_6 = 85.63
    percentage_2_occupation_7 = 65.59
    percentage_2_occupation_8 = 5.15
    percentage_2_occupation_9 = 45.12

    #######################################################################


    # Create a variable that counts the number of OA areas iterated
    OA_area_counter = 0

    if from_ == -1:
        from_ = 0
        to_ = len(AreaOA_list)
    else:
        to_ = min(len(AreaOA_list), from_ + 500)
    AreaOA_list.sort()
    for OA_area in AreaOA_list[from_:to_]:#for OA_area in AreaOA_list:

        OA_area_counter += 1
        print("Number of OA areas in iteration: ", (OA_area_counter, len(AreaOA_list)))

        ###########################################################################
        ############# SELECT INFORMATION FROM LC6112EW ############################
        # CENSUS 2011 INFORMATION

        # Select the row of the df_occupation that is related to the selected OA area:
        df_occupation_OAarea = df_occupation.loc[(df_occupation['geography'] == OA_area)]

        ###########################################################################
        ############ SELECT INFORMATION FROM THE SYNTHETIC POPULATION #############
        # 2021 INFORMATION

        # Select the people in the OAarea from my synthetic population:
        df_persons_NE_occupation_16_120_OAarea = df_persons_NE_occupation_16_120.loc[
            (df_persons_NE_occupation_16_120['Area_OA_x'] == OA_area)]

        ###########################################################################
        ######################## LOOP THROUGH AGE RANGES ##########################

        for age_range in age_range_list:

            # print('age_range')
            # print(age_range[0])
            # print(age_range[1])

            ###########################################################################
            ########### SELECT THOSE PEOPLE IN THE RANGE OF AGE SELECTED ##############
            ####################### SPLIT IN BOTH SEX OPTIONS #########################
            # MALES ONLY IN THE SPECIFIC OA AREA AND RANGE OF AGE
            (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_males"]) = \
            df_persons_NE_occupation_16_120_OAarea.loc[(df_persons_NE_occupation_16_120_OAarea['Age'] >= age_range[0]) & (
                        df_persons_NE_occupation_16_120_OAarea['Age'] <= age_range[1]) & (
                                                                   df_persons_NE_occupation_16_120_OAarea['Sex'] ==
                                                                   gender_list[0])]

            # FEMALES ONLY IN THE SPECIFIC OA AREA AND RANGE OF AGE
            (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_females"]) = \
            df_persons_NE_occupation_16_120_OAarea.loc[(df_persons_NE_occupation_16_120_OAarea['Age'] >= age_range[0]) & (
                        df_persons_NE_occupation_16_120_OAarea['Age'] <= age_range[1]) & (
                                                                   df_persons_NE_occupation_16_120_OAarea['Sex'] ==
                                                                   gender_list[1])]

            # Total people N THE SPECIFIC OA AREA AND RANGE OF AGE
            (globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2021"]) = (
                        len((globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_males"])) + len(
                    (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_females"])))
            # print('total people in OAarea within the age range in 2021: ', (globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2021"]))

            for gender in gender_list:

                if gender == 1:

                    occupation_list = occupation_list_males
                    (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) = (
                    globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_males"])

                else:

                    occupation_list = occupation_list_females
                    (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) = (
                    globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_females"])

                for occupation in occupation_list:
                    # print('occupation: ',occupation)

                    ################################################################################
                    ########### SELECT VALUES RELATED TO EACH OCCUPATION TYPE ###############

                    # Select the column name related to the specific OA area, range of age and occupation type(1-9)
                    (globals()[
                        f"column_occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea"]) = 'occupation_' + str(
                        occupation) + '_' + str(age_range[0]) + '_' + str(age_range[1])

                    # Get the value of each occupation based on the range of age and occupation type, in the the specific OA area.
                    globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2011"] = \
                    df_occupation_OAarea.iloc[0, df_occupation_OAarea.columns.get_loc(
                        (globals()[f"column_occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea"]))]

                    # print('number of people in occupation 2011 ', globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2011"])

                # Calculate the total number of people in the range of age that are found in the census data
                (globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2011"]) = globals()[
                                                                                             f"occupation_1_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_2_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_3_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_4_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_5_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_6_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_7_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_8_{age_range[0]}_{age_range[1]}_OAarea_2011"] + \
                                                                                         globals()[
                                                                                             f"occupation_9_{age_range[0]}_{age_range[1]}_OAarea_2011"]

                # print('total people in OAarea within the age range in 2011: ', globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2011"])

                ###########################################################################
                ######################## CALCULATE THE RATIO 2021/2011 ####################

                # Ratio of people 2021 vs 2011:
                if (globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2011"]) > 0:

                    ratio_people_2021_2011 = ((globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2021"]) / (
                    globals()[f"total_people_{age_range[0]}_{age_range[1]}_OAarea_2011"]))
                    ## If value > 0, it means there are more people in 2021 in the selected OA area of the specific gender and range of age

                # If there is no people in the OA area, then the ratio will be equal to 1
                else:
                    ratio_people_2021_2011 = 1

                for occupation in occupation_list:

                    ###############################################################################
                    ############################ UPDATE THE VALUE TO 2021 ##########################

                    # Update the value to 2021: 2021 = 2011 * occupation_"X"_conversor * ratio_people_2021_2011
                    globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021"] = int(round(
                        globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2011"] * globals()[
                            f"occupation_{occupation}_conversor"] * ratio_people_2021_2011, 0))

                    # print('Number of people to be assigned in 2021: ', globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021"])

                    # print('gender %d in the area' % (gender))

                    globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021_{gender}"] = int(round(
                        globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021"] * globals()[
                            f"percentage_{gender}_occupation_{occupation}"] / 100, 0))

                    # print(globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021_{gender}"])

                    ################################################################################
                    ########### SELECT RANDOMLY PEOPLE PER TYPE OF SEX  AND RANGE OF AGE ###########

                    if (len(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) > 0):

                        if (globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021_{gender}"] < len(
                                globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"])):

                            # Select randomly
                            (globals()[
                                f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"]) = (
                            globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]).sample(
                                globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021_{gender}"])

                        else:

                            # Select all people
                            (globals()[
                                f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"]) = (
                            globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"])

                    else:

                        (globals()[
                            f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"]) = pd.DataFrame()

                    ## Update the column value to the occupation selected:
                    (globals()[
                        f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"])[
                        'Occupation'] = occupation

                    # print('%d selected' % (gender))
                    # print((globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"]))

                    # Append the dataframe into the temporal list
                    persons_NE_occupations_first_selection.append((globals()[
                        f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"]))

                    ##############################################################################

                    # Concatenate the selected ones with the people from the same age and OA area
                    globals()[f"df_{gender_list[0]}_{age_range[0]}_{age_range[1]}_plus_{occupation}"] = (pd.concat(
                        [(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]), (globals()[
                            f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected"])]))

                    ##############################################################################
                    ##############################     IMPORTANT   ###############################

                    # Remove duplicates BUT keep the same names of the dataframes used after selecting the OAarea, age and sex

                    (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) = globals()[
                        f"df_{gender_list[0]}_{age_range[0]}_{age_range[1]}_plus_{occupation}"].drop_duplicates(
                        subset='PID_AreaMSOA', keep=False)

                    # print('remaining %d ' % (gender))

                    # print((globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]))

                    ##############################################################################

            ###########################################################################################
            # FIND PEOPLE FROM THE SYNTHETIC POPULATION THAT HAVE NOT BEEN ASSIGNED AN OCCUPATION YET
            # WHILE THERE ARE STILL SOME GAPS REMAINING TO BE OCCUPED.

            for gender in gender_list:

                if gender == 1:

                    occupation_list = occupation_list_males_last

                else:

                    occupation_list = occupation_list_females_last

                # print('gender %d' % (gender))

                # print('remaining people to be assinged an occupation:')
                # print(len(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]))

                if (len(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) > 0):

                    # If the number of people to be assinged of a specific occupation MINUS the ones already assigned for this occupation (males and females) is > 0
                    # then it means there are already some people (males in this case) that can fix this gap

                    for occupation in occupation_list:

                        # print('occupation selected: %e' % (occupation))

                        if (globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021"] - len(globals()[
                                                                                                                      f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender_list[0]}_{occupation}_selected"]) - len(
                                globals()[
                                    f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender_list[1]}_{occupation}_selected"])):

                            remaining_people_to_assign = globals()[
                                                             f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021"] - len(
                                globals()[
                                    f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender_list[0]}_{occupation}_selected"]) - len(
                                globals()[
                                    f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender_list[1]}_{occupation}_selected"])
                            # print('remaining remaining_people_to_assign : %f' %(remaining_people_to_assign))

                            if ((globals()[f"occupation_{occupation}_{age_range[0]}_{age_range[1]}_OAarea_2021"] - len(
                                    globals()[
                                        f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender_list[0]}_{occupation}_selected"]) - len(
                                    globals()[
                                        f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender_list[1]}_{occupation}_selected"])) < len(
                                    globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"])):

                                globals()[
                                    f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"] = \
                                globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"].sample(
                                    remaining_people_to_assign)
                                # print(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"])

                            else:

                                globals()[
                                    f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"] = \
                                globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]
                                # print(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"])

                        else:

                            globals()[
                                f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"] = pd.DataFrame()
                            # print(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"])

                        ## Update the column value to the occupation selected:
                        globals()[
                            f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"][
                            'Occupation'] = occupation

                        # print('%d selected' % (gender))
                        # print((globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"]))

                        # Append the dataframe into the temporal list
                        persons_NE_occupations_second_selection.append(globals()[
                                                                           f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"])

                        ##############################################################################
                        # Concatenate the selected ones with the people from the same age and OA area

                        globals()[
                            f"df_{gender_list[0]}_{age_range[0]}_{age_range[1]}_plus_{occupation}_second_selection"] = (
                            pd.concat(
                                [(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]), (
                                globals()[
                                    f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"])]))

                        ##############################################################################
                        ##############################     IMPORTANT   ###############################

                        # Remove duplicates BUT keep the same names of the dataframes used after selecting the OAarea, age and sex

                        (globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) = globals()[
                            f"df_{gender_list[0]}_{age_range[0]}_{age_range[1]}_plus_{occupation}_second_selection"].drop_duplicates(
                            subset='PID_AreaMSOA', keep=False)

                        # print('remaining gender %d ' % (gender))

                        # print((globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]))


                else:

                    # print('no need to choose more gender type %d. All of them were already selected' % (gender))

                    # Create an empty dataframe for the second selection
                    globals()[
                        f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}_{occupation}_selected_second"] = pd.DataFrame()

            ##############################################################################
            # If there are still some people to be assigned an occupation but all gaps have been used,
            ## then, allocate the people one by one base on the order occupations are given
            ## (e.g., first male will go to occupation 5, second to 8... last to 6) [based on occupation_list_males].
            ## (e.g., first female will go to occupation 6, second to 4... last to 8) [based on occupation_list_females].

            for gender in gender_list:

                if gender == 1:

                    occupation_list = occupation_list_males_last

                else:

                    occupation_list = occupation_list_females_last

                if (len(globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"]) > 0):

                    # Initialise a variable to 0
                    ## this variable will take the value of occupation_list
                    list_value = 0

                    # Iterate the dataframe with the remaining people to be assigned an occupation:
                    for idx_person_1, person_1 in globals()[
                        f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"].iterrows():

                        # print(person_1)
                        # print('occupation value to be assinged')
                        # print(occupation_list[list_value])

                        # person_1['Occupation'] = occupation_list[list_value]
                        globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"].at[
                            idx_person_1, 'Occupation'] = occupation_list[list_value]
                        # print(person_1)

                        # Increase the value in one
                        # Next person will be allocated in the second category of the occupation_list_"gender"
                        list_value += 1

                        # If the list_value is greater than 8 (there are 9 categories (0-8)), then list_value is restarted to 0
                        if (list_value == 9):
                            list_value = 0

                # Append the dataframe into the temporal list
                persons_NE_occupations_third_selection.append(
                    globals()[f"df_persons_NE_occupation_{age_range[0]}_{age_range[1]}_OAarea_{gender}"])

    # concatenate all persons (lists of the 'persons_NE_occupations_first_selection' list) in one dataframe
    globals()[f"df_persons_NE_occupation_OAarea_first_selection"] = pd.concat(persons_NE_occupations_first_selection,
                                                                              axis=0, ignore_index=True)
    print('first')
    # print(globals()[f"df_persons_NE_occupation_OAarea_first_selection"])


    # concatenate all persons (lists of the 'persons_NE_occupations_second_selection' list) in one dataframe
    globals()[f"df_persons_NE_occupation_OAarea_second_selection"] = pd.concat(persons_NE_occupations_second_selection,
                                                                               axis=0, ignore_index=True)
    print('second')
    # print(globals()[f"df_persons_NE_occupation_OAarea_second_selection"])

    # concatenate all persons (lists of the 'persons_NE_occupations_second_selection' list) in one dataframe
    globals()[f"df_persons_NE_occupation_OAarea_third_selection"] = pd.concat(persons_NE_occupations_third_selection,
                                                                              axis=0, ignore_index=True)
    print('third:')
    # print(globals()[f"df_persons_NE_occupation_OAarea_third_selection"])


    df_after_occupation = (pd.concat([globals()[f"df_persons_NE_occupation_OAarea_first_selection"],
                                      globals()[f"df_persons_NE_occupation_OAarea_second_selection"],
                                      globals()[f"df_persons_NE_occupation_OAarea_third_selection"]], ignore_index=True))

    print('Code has finished. Check the results')
    # print(df_after_occupation)


    # Calculate the percentage in each occupation type

    df_occupation_1 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 1)]
    percentage_occupation_1 = len(df_occupation_1) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_2 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 2)]
    percentage_occupation_2 = len(df_occupation_2) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_3 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 3)]
    percentage_occupation_3 = len(df_occupation_3) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_4 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 4)]
    percentage_occupation_4 = len(df_occupation_4) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_5 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 5)]
    percentage_occupation_5 = len(df_occupation_5) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_6 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 6)]
    percentage_occupation_6 = len(df_occupation_6) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_7 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 7)]
    percentage_occupation_7 = len(df_occupation_7) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_8 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 8)]
    percentage_occupation_8 = len(df_occupation_8) / len(df_persons_NE_occupation_16_120) * 100

    df_occupation_9 = df_after_occupation.loc[(df_after_occupation['Occupation'] == 9)]
    percentage_occupation_9 = len(df_occupation_9) / len(df_persons_NE_occupation_16_120) * 100

    print(percentage_occupation_1)
    print(percentage_occupation_2)
    print(percentage_occupation_3)
    print(percentage_occupation_4)
    print(percentage_occupation_5)
    print(percentage_occupation_6)
    print(percentage_occupation_7)
    print(percentage_occupation_8)
    print(percentage_occupation_9)

    # Calculate the percentage of males in each occupation type

    df_occupation_1_males = df_occupation_1.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_1_males = len(df_occupation_1_males) / len(df_occupation_1) * 100

    df_occupation_2_males = df_occupation_2.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_2_males = len(df_occupation_2_males) / len(df_occupation_2) * 100

    df_occupation_3_males = df_occupation_3.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_3_males = len(df_occupation_3_males) / len(df_occupation_3) * 100

    df_occupation_4_males = df_occupation_4.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_4_males = len(df_occupation_4_males) / len(df_occupation_4) * 100

    df_occupation_5_males = df_occupation_5.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_5_males = len(df_occupation_5_males) / len(df_occupation_5) * 100

    df_occupation_6_males = df_occupation_6.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_6_males = len(df_occupation_6_males) / len(df_occupation_6) * 100

    df_occupation_7_males = df_occupation_7.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_7_males = len(df_occupation_7_males) / len(df_occupation_7) * 100

    df_occupation_8_males = df_occupation_8.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_8_males = len(df_occupation_8_males) / len(df_occupation_8) * 100

    df_occupation_9_males = df_occupation_9.loc[(df_after_occupation['Sex'] == 1)]
    percentage_occupation_9_males = len(df_occupation_9_males) / len(df_occupation_9) * 100

    print(percentage_occupation_1_males)
    print(percentage_occupation_2_males)
    print(percentage_occupation_3_males)
    print(percentage_occupation_4_males)
    print(percentage_occupation_5_males)
    print(percentage_occupation_6_males)
    print(percentage_occupation_7_males)
    print(percentage_occupation_8_males)
    print(percentage_occupation_9_males)

    # Calculate the percentage of females in each occupation type

    df_occupation_1_females = df_occupation_1.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_1_females = len(df_occupation_1_females) / len(df_occupation_1) * 100

    df_occupation_2_females = df_occupation_2.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_2_females = len(df_occupation_2_females) / len(df_occupation_2) * 100

    df_occupation_3_females = df_occupation_3.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_3_females = len(df_occupation_3_females) / len(df_occupation_3) * 100

    df_occupation_4_females = df_occupation_4.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_4_females = len(df_occupation_4_females) / len(df_occupation_4) * 100

    df_occupation_5_females = df_occupation_5.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_5_females = len(df_occupation_5_females) / len(df_occupation_5) * 100

    df_occupation_6_females = df_occupation_6.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_6_females = len(df_occupation_6_females) / len(df_occupation_6) * 100

    df_occupation_7_females = df_occupation_7.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_7_females = len(df_occupation_7_females) / len(df_occupation_7) * 100

    df_occupation_8_females = df_occupation_8.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_8_females = len(df_occupation_8_females) / len(df_occupation_8) * 100

    df_occupation_9_females = df_occupation_9.loc[(df_after_occupation['Sex'] == 2)]
    percentage_occupation_9_females = len(df_occupation_9_females) / len(df_occupation_9) * 100

    print(percentage_occupation_1_females)
    print(percentage_occupation_2_females)
    print(percentage_occupation_3_females)
    print(percentage_occupation_4_females)
    print(percentage_occupation_5_females)
    print(percentage_occupation_6_females)
    print(percentage_occupation_7_females)
    print(percentage_occupation_8_females)
    print(percentage_occupation_9_females)

    # Export the dataframe into a csv file

    # df_after_occupation = df_after_occupation

    df_after_occupation.to_csv(path+ str(year) + '/NE_only/df_after_occupation_'+str(to_)+'_.csv', encoding='utf-8', header=True)
