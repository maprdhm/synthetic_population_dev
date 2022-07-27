import glob
import pandas as pd
import numpy as np
import os
import csv
import sys


if __name__ == '__main__':
    path = sys.argv[1]
    year = str(sys.argv[2])

    # Import the csv files containing the persons and households of the area of study
    # Read CSV file containing the MSOA and OA values only from the North East of England
    df_persons_NE_Household_composition__dir = path + '/' + year + '/NE_only'  # use your path
    df_persons_NE_Household_composition__file = os.path.join(df_persons_NE_Household_composition__dir,
                                                             "df_persons_NE_Household_composition_updated.csv")
    df_persons_NE_Household_composition_updated = pd.read_csv(df_persons_NE_Household_composition__file, index_col=None,
                                                              header=0)

    # Read CSV file containing the MSOA and OA values only from the North East of England
    df_households_NE_extended__dir = path + '/' + year + '/NE_only'  # use your path
    df_households_NE_extended_file = os.path.join(df_households_NE_extended__dir, "df_households_NE_clean.csv")
    df_households_NE_extended = pd.read_csv(df_households_NE_extended_file, index_col=None, header=0)

    # Read CSV file containing the economic activities per OA level, based on sex and age
    ## This dataset contains information about the number of employed and inactive people per location (OA area), sex and range of age
    df_economic_activity_dir = path+"/Data/"  # use your path
    df_economic_activity_file = os.path.join(df_economic_activity_dir, "LC6107EW.csv")
    df_economic_activity = pd.read_csv(df_economic_activity_file, index_col=None, header=0)

    df_economic_activity = df_economic_activity[
        df_economic_activity.columns.drop(list(df_economic_activity.filter(regex='All')))]
    df_economic_activity = df_economic_activity[
        df_economic_activity.columns.drop(list(df_economic_activity.filter(regex='Employee')))]
    df_economic_activity = df_economic_activity[
        df_economic_activity.columns.drop(list(df_economic_activity.filter(regex='Part-time')))]
    df_economic_activity = df_economic_activity[
        df_economic_activity.columns.drop(list(df_economic_activity.filter(regex='Self-employed')))]
    df_economic_activity = df_economic_activity[
        df_economic_activity.columns.drop(list(df_economic_activity.filter(regex='Economically active: Total;')))]

    df_economic_activity.columns = df_economic_activity.columns.str.replace('Sex: Males; ', '1_')
    df_economic_activity.columns = df_economic_activity.columns.str.replace('Sex: Females; ', '2_')
    df_economic_activity.columns = df_economic_activity.columns.str.replace('Age: Age 16 to 24; ', '16_24_')
    df_economic_activity.columns = df_economic_activity.columns.str.replace('Age: Age 25 to 34; ', '25_34_')
    df_economic_activity.columns = df_economic_activity.columns.str.replace('Age: Age 35 to 49; ', '35_49_')
    df_economic_activity.columns = df_economic_activity.columns.str.replace('Age: Age 50 to 64; ', '50_64_')
    df_economic_activity.columns = df_economic_activity.columns.str.replace('Age: Age 65 and over; ', '65_120_')

    df_economic_activity.columns = df_economic_activity.columns.str.replace(
        'Economic Activity: Economically active: In employment: Total; measures: Value', 'Employed')
    df_economic_activity.columns = df_economic_activity.columns.str.replace(
        r"Economic Activity: Economically active: Unemployed \(including full\-time students\); measures: Value",
        'Unemployed')
    df_economic_activity.columns = df_economic_activity.columns.str.replace(
        'Economic Activity: Economically inactive; measures: Value', 'Inactive')

    df_economic_activity

    # Create a new empty column for the Economic_activity (empty string)
    df_persons_NE_Household_composition_updated["Economic_activity"] = ""

    # ## Start with inactive people:
    # - NSSEC is null or 9
    # - LC4605_C_NSSEC = 9 (students)

    # Generate a new dataframe containing only those people which NSSEC value is null or 9(students)

    df_potential_inactive_NSSECnull = df_persons_NE_Household_composition_updated.loc[
        (df_persons_NE_Household_composition_updated['NSSEC'].isnull())]
    df_potential_inactive_NSSEC_9 = df_persons_NE_Household_composition_updated.loc[
        (df_persons_NE_Household_composition_updated['NSSEC'] == 9)]

    # concatenate all persons "EMPLOYED" in one dataframe
    df_potential_inactive = (pd.concat([df_potential_inactive_NSSECnull, df_potential_inactive_NSSEC_9]))

    ############################################################################

    # ECONOMIC ACTIVITY: INACTIVE

    # This code is to run only the assignment of INACTIVE people!!!

    ############################################################################


    # List for the gender types: male (1) and female (2)
    gender_list = [1, 2]

    # List containing the range of ages
    # This values come from Regional labour market statistics: HI01 Headline indicators for the WM
    # link: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/headlinelabourforcesurveyindicatorsforthenortheasthi01
    age_range_list = [(16, 24), (25, 34), (35, 49), (50, 64), (65, 120)]

    ## LIST OF OA_AREAS that has been generated before
    # Create a list with all Households unique ID values
    AreaOA_list = df_households_NE_extended['Area_OA'].tolist()
    # Remove duplicates
    AreaOA_list = list(set(AreaOA_list))

    # Create an empty list where the small blocks of dataframes of INACTIVE people will be stored
    persons_inactive_list = []

    # Create a variable that counts the number of OA areas iterated
    OA_area_counter = 0

    # Create a variable that counts th number of iterations needed to achieve the goal of a % within +-2% when compared to 2021 values
    iteration_counter = 0

    # Inactive rate for males (1) in 2021 per range of age
    # This values come from Regional labour market statistics: HI01 Headline indicators for the WM
    # link: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/headlinelabourforcesurveyindicatorsforthenortheasthi01
    inactive_rate_1_2021_list = [42.7, 9.4, 7.7, 21.7, 88.4]
    # Save each value (males) in a variable to be compared
    inactive_rate_1_16_24_2021 = inactive_rate_1_2021_list[0]
    inactive_rate_1_25_34_2021 = inactive_rate_1_2021_list[1]
    inactive_rate_1_35_49_2021 = inactive_rate_1_2021_list[2]
    inactive_rate_1_50_64_2021 = inactive_rate_1_2021_list[3]
    inactive_rate_1_65_120_2021 = inactive_rate_1_2021_list[4]

    # Inactive rate for females (2) in 2021 per range of age
    # This values come from Regional labour market statistics: HI01 Headline indicators for the WM
    # link: https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/employmentandemployeetypes/datasets/headlinelabourforcesurveyindicatorsforthenortheasthi01
    inactive_rate_2_2021_list = [45.4, 16.4, 17.7, 30.3, 92.4]
    # Save each value (females) in a variable to be compared
    inactive_rate_2_16_24_2021 = inactive_rate_2_2021_list[0]
    inactive_rate_2_25_34_2021 = inactive_rate_2_2021_list[1]
    inactive_rate_2_35_49_2021 = inactive_rate_2_2021_list[2]
    inactive_rate_2_50_64_2021 = inactive_rate_2_2021_list[3]
    inactive_rate_2_65_120_2021 = inactive_rate_2_2021_list[4]

    # INITIAL values to transform data from 2011 to 2021 based on the relationship (2021/2011)
    # These values will be updated everytime an iteration is not within +-2% of the value of 2021
    # MEN
    inactive_conversor_1_16_24 = 1.161
    inactive_conversor_1_25_34 = 0.944
    inactive_conversor_1_35_49 = 0.833
    inactive_conversor_1_50_64 = 0.870
    inactive_conversor_1_65_120 = 0.984
    # FEMALE
    inactive_conversor_2_16_24 = 0.994
    inactive_conversor_2_25_34 = 0.638
    inactive_conversor_2_35_49 = 0.786
    inactive_conversor_2_50_64 = 0.732
    inactive_conversor_2_65_120 = 0.980

    for gender in gender_list:
        for age_range in age_range_list:

            # Set the percentage of inactive per sex and range of age to zero at the begining.
            ## This value will be updated in every iteration until value obtained is within +-2% from the 2021 value.
            (globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"]) = 0

            print('The group that is in process is the following: ')
            print(str(gender) + "_" + str(age_range[0]) + "_" + str(age_range[1]))

            # let's start assigning economic activities to the persons in the synthetic population
            ## Based on the OA level, age and sex
            while (((globals()[f"inactive_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] - 2) > (
            globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"])) or (
                           (globals()[f"inactive_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] + 2) < (
                   globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"]))):
                iteration_counter += 1
                print("Number of iteration: ", (iteration_counter))

                print('CONVERSOR Value IS', (globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"]))

                # Clear the list everytime there is a need for a new iteration
                persons_inactive_list.clear()

                # Clear the dataframe everytime there is a need for an new iteration
                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"] = pd.DataFrame()
                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"] = pd.DataFrame()
                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"] = pd.DataFrame()

                # Create a variable that counts the number of OA areas iterated
                OA_area_counter = 0

                for OA_area in AreaOA_list:

                    OA_area_counter += 1
                    # print("Number of OA areas in iteration: ", (OA_area_counter, len(AreaOA_list)))

                    # Select the row of the df_economic_activity that is related to the selected OA area:
                    df_economic_activity_area = df_economic_activity.loc[(df_economic_activity['geography'] == OA_area)]

                    # Select ALL people that live in the selected OA area and are >= 16 years old:
                    df_people_OA_area = df_persons_NE_Household_composition_updated.loc[
                        (df_persons_NE_Household_composition_updated['Area_OA_x'] == OA_area) & (
                                    df_persons_NE_Household_composition_updated['Age'] >= 16)]
                    # print(len(df_people_OA_area))

                    # Select only those that belong to a specific gender (male of female) and range of age
                    # The INACTIVE people will be chosen from this dataset. The number of them will depend on the value of variable "globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"]"
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"] = df_people_OA_area.loc[
                        (df_people_OA_area['Sex'] == gender) & (df_people_OA_area['Age'] >= age_range[0]) & (
                                    df_people_OA_area['Age'] <= age_range[1])]

                    # Calculate the total number of people with the specific gender and range of age living in that OA area:
                    globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_in_OA_2021"] = len(
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"])
                    # print(globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_in_OA_2021"])

                    # Create a variable per type of economic activity based on sex and range of age
                    col_gender_age0_age1_employed = str(gender) + "_" + str(age_range[0]) + "_" + str(
                        age_range[1]) + "_Employed"
                    col_gender_age0_age1_unemployed = str(gender) + "_" + str(age_range[0]) + "_" + str(
                        age_range[1]) + "_Unemployed"
                    col_gender_age0_age1_inactive = str(gender) + "_" + str(age_range[0]) + "_" + str(
                        age_range[1]) + "_Inactive"

                    # Identify the number of people based on sex and range of age in the selected OA area that are employed
                    # Value from 2011!!
                    # Value comming table LC6107EW that has to be updated to 2021
                    globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = df_economic_activity_area.iloc[
                        0, df_economic_activity_area.columns.get_loc(col_gender_age0_age1_employed)]

                    # Identify the number of people based on sex and range of age in the selected OA area that are unemployed
                    # Value from 2011!!
                    # Value comming table LC6107EW that has to be updated to 2021
                    globals()[f"unemployed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = \
                    df_economic_activity_area.iloc[
                        0, df_economic_activity_area.columns.get_loc(col_gender_age0_age1_unemployed)]

                    # Identify the number of people based on sex and range of age in the selected OA area that are inactive
                    # Value from 2011!!
                    # Value comming table LC6107EW that has to be updated to 2021
                    globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = df_economic_activity_area.iloc[
                        0, df_economic_activity_area.columns.get_loc(col_gender_age0_age1_inactive)]
                    # print(globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"])

                    # Value with the total number of people living in the seleted OA area (table LC6107EW)
                    globals()[f"Total_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = globals()[
                                                                                              f"employed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] + \
                                                                                          globals()[
                                                                                              f"unemployed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] + \
                                                                                          globals()[
                                                                                              f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"]

                    # Ratio of people 2021 vs 2011:
                    ## If the number of people of the selected gender and range of age is greater than 0 (e.g., there are people in the OA with this specific sex and range of age)
                    if (globals()[f"Total_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"]) > 0:

                        globals()[f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"] = (
                                    globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_in_OA_2021"] / globals()[
                                f"Total_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"])
                        ## If value > 1, it means there are more people in 2021 in the selected OA area of the specific gender and range of age

                    # If there is no people (gender and age range) in the OA area, then the ratio will be equal to 1
                    else:
                        globals()[f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"] = 1

                    # New value for 2021 =  (Value from 2011 (table LC6107EW)) * (inactive conversor value (based on age range and sex)) * (ratio of people 2021 vs 2011 (c))
                    ## This value is the number of people that will be randomly assigned "inactive" based on their OA area, range of age and sex
                    globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"] = int(round(
                        globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] * globals()[
                            f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"] * globals()[
                            f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"], 0))

                    # print('value from census 2011')
                    # print(globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"])
                    # print('inactive conversor')
                    # print(globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"])
                    # print('people rate')
                    # print(globals()[f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"])

                    # print('Number of inactive people in the OA area per gender 2021')
                    # print((globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"]))

                    # SELECT FIRST STUDENTS
                    # dataframe with those persons that are students:

                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_students"] = \
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"].loc[
                        (globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"]['LC4605_C_NSSEC_x'] == 9)]
                    # print('number of students found in the area:')
                    # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_students"]))

                    # If there are STUDENTS in the OA area:
                    if (len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_students"])) > 0:

                        if (globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"]) <= len(
                                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_students"]):

                            # Select randomly the number of people that will be assigned as inactive
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"] = globals()[
                                f"df_{gender}_{age_range[0]}_{age_range[1]}_students"].sample(
                                globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])
                            # print('all of them are students')
                            # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"]))

                            # All inavtive people were selected between the students,
                            # So, no more people need to be selected.
                            # the following dataframe is null because there is no need to select more people as INACTIVE
                            ##globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"] = pd.DataFrame()
                            ##globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"] = pd.DataFrame()


                        else:
                            # Select all people that will be assigned as inactive
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"] = globals()[
                                f"df_{gender}_{age_range[0]}_{age_range[1]}_students"]
                            # print('just a few students')
                            # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"]))
                            # print('more inactive people need to be selected')

                    # If there is not any student in the OA area:
                    else:
                        # If the dataframe does not have any remaining rows, then it will be empty.
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"] = pd.DataFrame()
                        # print('no students')

                    # Remaining NUMBER of people to be assigned as INACTIVE:
                    globals()[f"remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"] = globals()[
                                                                                                       f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"] - len(
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"])
                    # print('remaining inactive people to be assigned after students:')
                    # print(globals()[f"remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])

                    ## Now we are going to force that remaining people to be INACTIVE will be those which
                    ## NSSEC value is null or 9
                    ## but also, removing the previos selected students in (globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"])

                    # dataframe containing people of the selected OA area, sex, range of age and nssec null
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_NSCCnull"] = \
                    df_potential_inactive.loc[
                        (df_potential_inactive['Area_OA_x'] == OA_area) & (df_potential_inactive['Sex'] == gender) & (
                                    df_potential_inactive['Age'] >= age_range[0]) & (
                                    df_potential_inactive['Age'] <= age_range[1]) & (
                            df_potential_inactive['NSSEC'].isnull())]
                    # dataframe containing people of the selected OA area, sex, range of age and nssec 9 (student)
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_NSCC9"] = \
                    df_potential_inactive.loc[
                        (df_potential_inactive['Area_OA_x'] == OA_area) & (df_potential_inactive['Sex'] == gender) & (
                                    df_potential_inactive['Age'] >= age_range[0]) & (
                                    df_potential_inactive['Age'] <= age_range[1]) & (df_potential_inactive['NSSEC'] == 9)]

                    # This dataframe contains the people of the selected OA area, sex, range of age and nssec (null or 9) that will be used to select the remaining INACTIVE people
                    ## But before that, the previous selected students (globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"]) MUST be removed
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive"] = (pd.concat(
                        [globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_NSCCnull"],
                         globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_NSCC9"]]))

                    # Remaining PEOPLE in the dataframe (df_gender_age0_age1 - (number of students already selected)):
                    ## Concatenate previous selected students with the "potential inactives"
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_plus_students"] = (pd.concat(
                        [globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive"],
                         globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"]]))

                    ## Remove duplicates:
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining"] = globals()[
                        f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_plus_students"].drop_duplicates(
                        keep=False)

                    ## Now, we are ready to select the remaining INACTIVE people:
                    # print('select remaining inactive after students')

                    # Select randomly the number of people to be inactive based on age and sex:
                    if (globals()[f"remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"]) <= len(
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining"]):

                        if (len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining"])) > 0:

                            # Select randomly the number of people that will be assigned as inactive
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"] = globals()[
                                f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining"].sample(
                                globals()[f"remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])
                            # print('number of NSSEC null selected')
                            # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"]))

                            ##globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"] = pd.DataFrame()

                        else:
                            # If the dataframe does not have any remaining rows, then it will be empty.
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"] = pd.DataFrame()
                            # print('no inactive people')

                    else:
                        # Select all people that will be assigned as inactive
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"] = globals()[
                            f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining"]
                        # print('Only a few inactive people')
                        # print('number of NSSEC null selected')
                        # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"]))

                    # print('Selcted students:')
                    # print(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"])
                    # print('Selected others:')
                    # print(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"])

                    # If there are still some people to be assigned as INACTIVE, then their NSSEC can be any value

                    # Remaining NUMBER of people to be assigned as INACTIVE:
                    globals()[f"Second_remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"] = globals()[
                                                                                                              f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"] - len(
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"]) - len(
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"])

                    # print('Second_remaining_inactive_ inactive people to be assigned after students and NSSEC:')
                    # print(globals()[f"Second_remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])

                    ## Concatenate all people of the specific sex, range age, OA area with the selected students and the others wich NSSEC value is null or 9
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_plus_students_plus_null"] = (
                        pd.concat([globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"],
                                   globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"],
                                   globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"]]))

                    # Remove duplicates
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining_last"] = globals()[
                        f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_plus_students_plus_null"].drop_duplicates(
                        keep=False)

                    # Select randomly the number of people to be inactive based on age and sex:
                    if (globals()[f"Second_remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"]) <= len(
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining_last"]):

                        if (
                        len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining_last"])) > 0:

                            # Select randomly the number of people that will be assigned as inactive
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"] = globals()[
                                f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining_last"].sample(
                                globals()[f"Second_remaining_inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])
                            # print('last sampled')
                            # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"]))
                            # print('All assigned inactive people were selected')

                        else:
                            # If the dataframe does not have any remaining rows, then it will be empty.
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"] = pd.DataFrame()
                            # print('no inactive people')

                    else:
                        # Select all people that will be assigned as inactive
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"] = globals()[
                            f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_inactive_remaining_last"]
                        # print('Only a few inactive people')
                        # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"]))

                    # concatenate all persons "inactive" in one dataframe
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all_each_area"] = (pd.concat(
                        [globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_students"],
                         globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive"],
                         globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_last"]]))

                    # print('total number of people selected as INACTIVE:')
                    # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all_each_area"]))
                    # print(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all_each_area"])

                    # print('Number of inactive people from the census projected to 2021:')
                    # print(globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])

                    # print('Difference (spenser - census 2021):')
                    # print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all_each_area"]) - globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_2021"])

                    # Append the dataframe into the temporal list
                    persons_inactive_list.append(
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all_each_area"])

                # concatenate all persons "inactive" in one dataframe
                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all"] = pd.concat(persons_inactive_list,
                                                                                                 axis=0, ignore_index=True)

                print('Number of people selected INACTIVE by age range and gender')
                print(len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all"]))

                # Calculate the TOTAL number of people with the same sex and range of age:
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}"] = len(
                    df_persons_NE_Household_composition_updated.loc[
                        (df_persons_NE_Household_composition_updated['Sex'] == gender) & (
                                    df_persons_NE_Household_composition_updated['Age'] >= age_range[0]) & (
                                    df_persons_NE_Household_composition_updated['Age'] <= age_range[1])])

                print('total number of people age range and gender:')
                print(globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}"])

                # Calculate the % of people inactive with the same sex and range of age:
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"] = (len(
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_inactive_all"]) / globals()[
                                                                                                      f"total_{gender}_{age_range[0]}_{age_range[1]}"]) * 100

                # Compare the results against the ones given in table Regional labour market statistics:HI05 Headline indicators for the West Midlands related to year 2021
                # If differences obtained against data given is within 2%, then it is Ok
                if (((globals()[f"inactive_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] - 2) <= (
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"])) & (
                        (globals()[f"inactive_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] + 2) >= (
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"]))):

                    print('The value is within the tolerance of 2%')
                    print('Value obtained was',
                          (globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"]))
                    print('Now the code should continue with the other gender or age range')

                # If the difference is greater than a 2% (+/-) then a new iteration should be done updating the parameter that transform the employment rate from 2011 to 2021
                else:
                    print('The % needs to be adjusted in another iteration')
                    print('Value obtained was',
                          (globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"]))

                    # If the difference is negative, then a POSITIVE increment has to be added
                    if ((globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_inactive_percentage"]) - globals()[
                        f"inactive_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] - 1) < 0:

                        # Update the value transform data from 2011 to 2021 (increase the value):
                        (globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"]) = (
                                    globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"] + 0.025)

                        print('Conversor value should be bigger:')
                        print('NEW CONVERSOR Value is: ',
                              (globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"]))

                    # If the difference is positive, then a NEGATIVE increment has to be added
                    else:
                        # Update the value transform data from 2011 to 2021 (reduce the value):
                        (globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"]) = (
                                    globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"] - 0.025)

                        print('Conversor value should be smaller:')
                        print('NEW CONVERSOR Value is: ',
                              (globals()[f"inactive_conversor_{gender}_{age_range[0]}_{age_range[1]}"]))

    print('Job done. Check the results.')


    # Group all employed people:
    df_persons_NE_inactive = (pd.concat(
        [df_1_16_24_inactive_all, df_1_25_34_inactive_all, df_1_35_49_inactive_all, df_1_50_64_inactive_all,
         df_1_65_120_inactive_all, df_2_16_24_inactive_all, df_2_25_34_inactive_all, df_2_35_49_inactive_all,
         df_2_50_64_inactive_all, df_2_65_120_inactive_all]))


    #########################################

    ## INACTIVE RATES:
    ## Check values obtained for MALES:


    ###########################################


    # Number of inactive people grouped by sex and age range:
    total_1_16_120_NE_inactive = len(df_persons_NE_inactive.loc[
                                         (df_persons_NE_inactive['Age'] >= 16) & (df_persons_NE_inactive['Age'] <= 120) & (
                                                     df_persons_NE_inactive['Sex'] == 1)])
    total_1_16_64_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 16) & (df_persons_NE_inactive['Age'] <= 64) & (
                                                    df_persons_NE_inactive['Sex'] == 1)])
    total_1_16_24_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 16) & (df_persons_NE_inactive['Age'] <= 24) & (
                                                    df_persons_NE_inactive['Sex'] == 1)])
    total_1_25_34_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 25) & (df_persons_NE_inactive['Age'] <= 34) & (
                                                    df_persons_NE_inactive['Sex'] == 1)])
    total_1_35_49_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 35) & (df_persons_NE_inactive['Age'] <= 49) & (
                                                    df_persons_NE_inactive['Sex'] == 1)])
    total_1_50_64_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 50) & (df_persons_NE_inactive['Age'] <= 64) & (
                                                    df_persons_NE_inactive['Sex'] == 1)])
    total_1_65_120_NE_inactive = len(df_persons_NE_inactive.loc[
                                         (df_persons_NE_inactive['Age'] >= 65) & (df_persons_NE_inactive['Age'] <= 120) & (
                                                     df_persons_NE_inactive['Sex'] == 1)])

    # Total number of people in the population grouped by sex and age range
    total_1_16_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_16_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_16_24_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 24) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_25_34_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 25) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 34) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_35_49_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 35) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 49) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_50_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 50) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_65_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 65) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 1)])

    # Percentage of people inactive grouped by sex and age range:
    percentage_1_16_120_inactive = total_1_16_120_NE_inactive / total_1_16_120_NE * 100
    percentage_1_16_64_inactive = total_1_16_64_NE_inactive / total_1_16_64_NE * 100
    percentage_1_16_24_inactive = total_1_16_24_NE_inactive / total_1_16_24_NE * 100
    percentage_1_25_34_inactive = total_1_25_34_NE_inactive / total_1_25_34_NE * 100
    percentage_1_35_49_inactive = total_1_35_49_NE_inactive / total_1_35_49_NE * 100
    percentage_1_50_64_inactive = total_1_50_64_NE_inactive / total_1_50_64_NE * 100
    percentage_1_65_120_inactive = total_1_65_120_NE_inactive / total_1_65_120_NE * 100

    print(percentage_1_16_120_inactive)
    print(percentage_1_16_64_inactive)
    print(percentage_1_16_24_inactive)
    print(percentage_1_25_34_inactive)
    print(percentage_1_35_49_inactive)
    print(percentage_1_50_64_inactive)
    print(percentage_1_65_120_inactive)


    #########################################

    ## INACTIVE RATES:
    ## Check values obtained for FEMALES:


    ###########################################


    # Number of inactive people grouped by sex and age range:
    total_2_16_120_NE_inactive = len(df_persons_NE_inactive.loc[
                                         (df_persons_NE_inactive['Age'] >= 16) & (df_persons_NE_inactive['Age'] <= 120) & (
                                                     df_persons_NE_inactive['Sex'] == 2)])
    total_2_16_64_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 16) & (df_persons_NE_inactive['Age'] <= 64) & (
                                                    df_persons_NE_inactive['Sex'] == 2)])
    total_2_16_24_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 16) & (df_persons_NE_inactive['Age'] <= 24) & (
                                                    df_persons_NE_inactive['Sex'] == 2)])
    total_2_25_34_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 25) & (df_persons_NE_inactive['Age'] <= 34) & (
                                                    df_persons_NE_inactive['Sex'] == 2)])
    total_2_35_49_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 35) & (df_persons_NE_inactive['Age'] <= 49) & (
                                                    df_persons_NE_inactive['Sex'] == 2)])
    total_2_50_64_NE_inactive = len(df_persons_NE_inactive.loc[
                                        (df_persons_NE_inactive['Age'] >= 50) & (df_persons_NE_inactive['Age'] <= 64) & (
                                                    df_persons_NE_inactive['Sex'] == 2)])
    total_2_65_120_NE_inactive = len(df_persons_NE_inactive.loc[
                                         (df_persons_NE_inactive['Age'] >= 65) & (df_persons_NE_inactive['Age'] <= 120) & (
                                                     df_persons_NE_inactive['Sex'] == 2)])

    # Total number of people in the population grouped by sex and age range
    total_2_16_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_16_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_16_24_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 24) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_25_34_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 25) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 34) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_35_49_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 35) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 49) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_50_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 50) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_65_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 65) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 2)])

    # Percentage of people inactive grouped by sex and age range:
    percentage_2_16_120_inactive = total_2_16_120_NE_inactive / total_2_16_120_NE * 100
    percentage_2_16_64_inactive = total_2_16_64_NE_inactive / total_2_16_64_NE * 100
    percentage_2_16_24_inactive = total_2_16_24_NE_inactive / total_2_16_24_NE * 100
    percentage_2_25_34_inactive = total_2_25_34_NE_inactive / total_2_25_34_NE * 100
    percentage_2_35_49_inactive = total_2_35_49_NE_inactive / total_2_35_49_NE * 100
    percentage_2_50_64_inactive = total_2_50_64_NE_inactive / total_2_50_64_NE * 100
    percentage_2_65_120_inactive = total_2_65_120_NE_inactive / total_2_65_120_NE * 100

    print(percentage_2_16_120_inactive)
    print(percentage_2_16_64_inactive)
    print(percentage_2_16_24_inactive)
    print(percentage_2_25_34_inactive)
    print(percentage_2_35_49_inactive)
    print(percentage_2_50_64_inactive)
    print(percentage_2_65_120_inactive)

    # Remove the people classified as 'inactive' and select from them the 'employed' ones

    # concatenate the inactive people selected with df_persons_NE_Household_composition_updated and remove duplicates to
    # identify the employed and later on the unemployed

    # concatenate all persons "EMPLOYED" in one dataframe
    df_persons_NE_Household_composition_updated_plus_inactive = (
        pd.concat([df_persons_NE_Household_composition_updated, df_persons_NE_inactive]))

    # Remove duplicates and keep only those who were not assigned a driving licence
    df_persons_NO_inactive = df_persons_NE_Household_composition_updated_plus_inactive.drop_duplicates(keep=False)


    # Select EMPLOYED people
    # In this case, we are going to avoid selecting people which nssec is 8 (Never worked and long-term unemployed)
    #
    # - NSSEC != 8


    df_persons_potential_employed = df_persons_NO_inactive.loc[(df_persons_NO_inactive['NSSEC'] != 8)]


    # List for the gender types: male (1) and female (2)
    gender_list = [1, 2]

    # List containing the range of ages
    age_range_list = [(16, 24), (25, 34), (35, 49), (50, 64), (65, 120)]

    ## LIST OF OA_AREAS that has been generated before
    # Create a list with all Households unique ID values
    AreaOA_list = df_households_NE_extended['Area_OA'].tolist()
    # Remove duplicates
    AreaOA_list = list(set(AreaOA_list))

    # Create an empty list where the small blocks of dataframes of EMPLOYED people will be stored
    persons_employed_list = []
    # Create an empty list where the small blocks of dataframes of INACTIVE people will be stored


    # Create a variable that counts the number of OA areas iterated
    OA_area_counter = 0

    # Create a variable that counts th number of iterations needed to achieve the goal of a % within +-2% when compared to 2021 values
    iteration_counter = 0

    # Employment rate for males (1) in 2021 per range of age
    # This values come from Regional labour market statistics: HI05 Headline indicators for the WM
    employed_rate_1_2021_list = [47.1, 86.2, 89.6, 75.7, 11.5]
    # Save each value (males) in a variable to be compared
    employed_rate_1_16_24_2021 = employed_rate_1_2021_list[0]
    employed_rate_1_25_34_2021 = employed_rate_1_2021_list[1]
    employed_rate_1_35_49_2021 = employed_rate_1_2021_list[2]
    employed_rate_1_50_64_2021 = employed_rate_1_2021_list[3]
    employed_rate_1_65_120_2021 = employed_rate_1_2021_list[4]

    # Employment rate for females (2) in 2021 per range of age
    # This values come from Regional labour market statistics: HI01 Headline indicators for the WM
    employed_rate_2_2021_list = [48.7, 78.8, 79.3, 67.5, 7.5]
    # Save each value (females) in a variable to be compared
    employed_rate_2_16_24_2021 = employed_rate_2_2021_list[0]
    employed_rate_2_25_34_2021 = employed_rate_2_2021_list[1]
    employed_rate_2_35_49_2021 = employed_rate_2_2021_list[2]
    employed_rate_2_50_64_2021 = employed_rate_2_2021_list[3]
    employed_rate_2_65_120_2021 = employed_rate_2_2021_list[4]

    # INITIAL values to transform data from 2011 to 2021 based on the relationship (2021/2011)
    # These values will be updated everytime an iteration is not within +-2% of the value of 2021
    # MEN
    employed_conversor_1_16_24 = 1.066
    employed_conversor_1_25_34 = 1.055
    employed_conversor_1_35_49 = 1.045
    employed_conversor_1_50_64 = 1.072
    employed_conversor_1_65_120 = 1.168
    # FEMALE
    employed_conversor_2_16_24 = 1.119
    employed_conversor_2_25_34 = 1.185
    employed_conversor_2_35_49 = 1.084
    employed_conversor_2_50_64 = 1.191
    employed_conversor_2_65_120 = 1.377

    # Initialise the % of employed people to 0% based on sex and range of age
    for gender in gender_list:
        for age_range in age_range_list:

            # Set the percentage of employed per sex and range of age to zero at the begining.
            ## This value will be updated in every iteration until value obtained is within +-2% from the 2021 value.
            (globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"]) = 0

            print('The group that is in process is the following: ')
            print(str(gender) + "_" + str(age_range[0]) + "_" + str(age_range[1]))

            # let's start assigning economic activities to the persons in the synthetic population
            ## Based on the OA level, age and sex

            while (((globals()[f"employed_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] - 2) > (
            globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"])) or (
                           (globals()[f"employed_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] + 2) < (
                   globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"]))):
                iteration_counter += 1
                print("Number of iteration: ", (iteration_counter))

                print('CONVERSOR Value IS', (globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"]))

                # Clear the list everytime there is a need for a new iteration
                persons_employed_list.clear()

                # Clear the dataframe everytime there is a need for an new iteration
                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_selected"] = pd.DataFrame()

                # Create a variable that counts the number of OA areas iterated
                OA_area_counter = 0

                for OA_area in AreaOA_list:

                    OA_area_counter += 1
                    # print("Number of OA areas in iteration: ", (OA_area_counter, len(AreaOA_list)))

                    # Select the row of the df_economic_activity that is related to the selected OA area:
                    df_economic_activity_area = df_economic_activity.loc[(df_economic_activity['geography'] == OA_area)]

                    # Select ALL people that live in the selected OA area and are >= 16 years old:
                    df_people_OA_area = df_persons_NE_Household_composition_updated.loc[
                        (df_persons_NE_Household_composition_updated['Area_OA_x'] == OA_area) & (
                                    df_persons_NE_Household_composition_updated['Age'] >= 16)]

                    # Select only those that belong to a specific gender (male of female) and range of age
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"] = df_people_OA_area.loc[
                        (df_people_OA_area['Sex'] == gender) & (df_people_OA_area['Age'] >= age_range[0]) & (
                                    df_people_OA_area['Age'] <= age_range[1])]

                    # Calculate the number of people with the specific gender and range of age living in that OA area:
                    globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_in_OA_2021"] = len(
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"])

                    # Create a variable per type of economic activity based on sex and range of age
                    col_gender_age0_age1_employed = str(gender) + "_" + str(age_range[0]) + "_" + str(
                        age_range[1]) + "_Employed"
                    col_gender_age0_age1_unemployed = str(gender) + "_" + str(age_range[0]) + "_" + str(
                        age_range[1]) + "_Unemployed"
                    col_gender_age0_age1_inactive = str(gender) + "_" + str(age_range[0]) + "_" + str(
                        age_range[1]) + "_Inactive"

                    # Identify the number of people based on sex and range of age in the selected OA area that are employed
                    # Value from 2011!!
                    # Value comming table LC6107EW that has to be updated to 2021
                    globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = df_economic_activity_area.iloc[
                        0, df_economic_activity_area.columns.get_loc(col_gender_age0_age1_employed)]

                    # Identify the number of people based on sex and range of age in the selected OA area that are unemployed
                    # Value from 2011!!
                    # Value comming table LC6107EW that has to be updated to 2021
                    globals()[f"unemployed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = \
                    df_economic_activity_area.iloc[
                        0, df_economic_activity_area.columns.get_loc(col_gender_age0_age1_unemployed)]

                    # Identify the number of people based on sex and range of age in the selected OA area that are inactive
                    # Value from 2011!!
                    # Value comming table LC6107EW that has to be updated to 2021
                    globals()[f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = df_economic_activity_area.iloc[
                        0, df_economic_activity_area.columns.get_loc(col_gender_age0_age1_inactive)]

                    # Value with the total number of people living in the seleted OA area (table LC6107EW)
                    globals()[f"Total_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] = globals()[
                                                                                              f"employed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] + \
                                                                                          globals()[
                                                                                              f"unemployed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] + \
                                                                                          globals()[
                                                                                              f"inactive_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"]

                    # Ratio of people 2021 vs 2011:
                    ## If the number of people of the selected gender and range of age is greater than 0 (e.g., there are people in the OA with this specific sex and range of age)
                    if (globals()[f"Total_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"]) > 0:

                        globals()[f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"] = (
                                    globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_in_OA_2021"] / globals()[
                                f"Total_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"])
                        ## If value > 0, it means there are more people in 2021 in the selected OA area of the specific gender and range of age

                    # If there is no people (gender and age range) in the OA area, then the ratio will be equal to 1
                    else:
                        globals()[f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"] = 1

                    # New value for 2021 =  (Value from 2011 (table LC6107EW)) * (employed conversor value (based on age range and sex)) * (ratio of people 2021 vs 2011 (c))
                    ## This value is the number of people that will be randomly assigned "employed" based on their OA area, range of age and sex
                    globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_2021"] = int(round(
                        globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_LC6107EW"] * globals()[
                            f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"] * globals()[
                            f"ratio_people_{gender}_{age_range[0]}_{age_range[1]}_2021_2011"], 0))

                    # Select those people of the selected sex, age range and OA area that can be selected:
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_employed"] = \
                    df_persons_potential_employed.loc[(df_persons_potential_employed['Sex'] == gender) & (
                                df_persons_potential_employed['Age'] >= age_range[0]) & (
                                                                  df_persons_potential_employed['Age'] <= age_range[1]) & (
                                                      (df_persons_potential_employed['Area_OA_x'] == OA_area))]

                    # Select randomly the number of people to be employed based on age and sex:
                    if (globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_2021"]) <= len(
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_employed"]):

                        if (len(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}"])) > 0:

                            # Select randomly the number of people that will be assigned as employed
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"] = globals()[
                                f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_employed"].sample(
                                globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_2021"])

                        else:
                            # If the dataframe does not have any remaining rows, then it will be empty.
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"] = pd.DataFrame()

                    else:
                        # Select all people that will be assigned as employed
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"] = globals()[
                            f"df_{gender}_{age_range[0]}_{age_range[1]}_potential_employed"]

                    # if there are still some people in the OA area to be assigned as "EMPLOYED" but there are no more
                    # people in the selected dataframe, then we are going to consider as well those
                    ## people wich NSSEC = 8
                    if (globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_2021"] > len(
                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"])):

                        # Select people in the OA area (depending on the sex type and age range)
                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_OAarea_all"] = df_persons_NO_inactive.loc[
                            (df_persons_NO_inactive['Sex'] == gender) & (df_persons_NO_inactive['Area_OA_x'] == OA_area) & (
                                        df_persons_NO_inactive['Age'] >= age_range[0]) & (
                                        df_persons_NO_inactive['Age'] <= age_range[1])]

                        # Concatenate the selected employed with the whole people >=16 in the OA area (depending on the sex type)
                        df_persons_NO_inactive_plus_employed = (pd.concat(
                            [globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_OAarea_all"],
                             globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"]]))

                        # Drop duplicates
                        df_persons_NO_inactive_remaining = df_persons_NO_inactive_plus_employed.drop_duplicates(
                            subset='PID_AreaMSOA', keep=False)

                        # If the dataframe is not empty:
                        if (len(df_persons_NO_inactive_remaining) > 0):

                            if (len(df_persons_NO_inactive_remaining) > globals()[
                                f"employed_{gender}_{age_range[0]}_{age_range[1]}_2021"] - len(
                                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"])):

                                # Select the remaining people as "employed"
                                globals()[
                                    f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_leftovers"] = df_persons_NO_inactive_remaining.sample(
                                    globals()[f"employed_{gender}_{age_range[0]}_{age_range[1]}_2021"] - len(
                                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"]))

                            else:

                                # Select the remaining people as "employed"
                                globals()[
                                    f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_leftovers"] = df_persons_NO_inactive_remaining

                        else:

                            globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_leftovers"] = pd.DataFrame()

                    else:

                        globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_leftovers"] = pd.DataFrame()

                    # Concatenate the selected dataframes with the selected students
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_all"] = (pd.concat(
                        [globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed"],
                         globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_leftovers"]]))

                    # Append the dataframe into the temporal list
                    persons_employed_list.append(globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_all"])

                # concatenate all persons "EMPLOYED" in one dataframe
                globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_selected"] = pd.concat(persons_employed_list,
                                                                                                      axis=0,
                                                                                                      ignore_index=True)

                # Calculate the TOTAL number of people with the same sex and range of age:
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}"] = len(
                    df_persons_NE_Household_composition_updated.loc[
                        (df_persons_NE_Household_composition_updated['Sex'] == gender) & (
                                    df_persons_NE_Household_composition_updated['Age'] >= age_range[0]) & (
                                    df_persons_NE_Household_composition_updated['Age'] <= age_range[1])])

                # Calculate the % of people EMPLOYED with the same sex and range of age:
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"] = (len(
                    globals()[f"df_{gender}_{age_range[0]}_{age_range[1]}_employed_selected"]) / globals()[
                                                                                                      f"total_{gender}_{age_range[0]}_{age_range[1]}"]) * 100

                # Compare the results against the ones given in table Regional labour market statistics:HI05 Headline indicators for WM related to year 2021
                # If differences obtained against data given is within 2%, then it is Ok
                if (((globals()[f"employed_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] - 2) <= (
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"])) & (
                        (globals()[f"employed_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] + 2) >= (
                globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"]))):

                    print('The value is within the tolerance of 2%')
                    print('Value obtained was',
                          (globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"]))
                    print('Now the code should continue with the other gender or age range')

                # If the difference is greater than a 2% (+/-) then a new iteration should be done updating the parameter that transform the employment rate from 2011 to 2021
                else:
                    print('The % needs to be adjusted in another iteration')
                    print('Value obtained was',
                          (globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"]))

                    # If the difference is negative, then a POSITIVE increment has to be added
                    if ((globals()[f"total_{gender}_{age_range[0]}_{age_range[1]}_employed_percentage"]) - globals()[
                        f"employed_rate_{gender}_{age_range[0]}_{age_range[1]}_2021"] - 1) < 0:

                        # Update the value transform data from 2011 to 2021 (increase the value):
                        (globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"]) = (
                                    globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"] + 0.025)

                        print('Conversor value should be bigger:')
                        print('NEW CONVERSOR Value is: ',
                              (globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"]))

                    # If the difference is positive, then a NEGATIVE increment has to be added
                    else:
                        # Update the value transform data from 2011 to 2021 (reduce the value):
                        (globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"]) = (
                                    globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"] - 0.025)

                        print('Conversor value should be smaller:')
                        print('NEW CONVERSOR Value is: ',
                              (globals()[f"employed_conversor_{gender}_{age_range[0]}_{age_range[1]}"]))

    print('Job done. Check the results.')

    # Group all employed people:
    df_persons_NE_employed = (pd.concat(
        [df_1_16_24_employed_selected, df_1_25_34_employed_selected, df_1_35_49_employed_selected,
         df_1_50_64_employed_selected, df_1_65_120_employed_selected, df_2_16_24_employed_selected,
         df_2_25_34_employed_selected, df_2_35_49_employed_selected, df_2_50_64_employed_selected,
         df_2_65_120_employed_selected]))


    #########################################

    ## EMPLOYMENT RATES:
    ## Check values obtained for males:


    ###########################################


    # Number of employed people grouped by sex and age range:
    total_1_16_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 1)])
    total_1_16_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_16_24_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 24) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_25_34_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 25) & (df_persons_NE_employed['Age'] <= 34) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_35_49_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 35) & (df_persons_NE_employed['Age'] <= 49) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_50_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 50) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_65_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 65) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 1)])

    # Total number of people in the population grouped by sex and age range
    total_1_16_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_16_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_16_24_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 24) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_25_34_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 25) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 34) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_35_49_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 35) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 49) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_50_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 50) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 1)])
    total_1_65_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 65) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 1)])

    # Percentage of people employed grouped by sex and age range:
    percentage_1_16_120_employed = total_1_16_120_NE_employed / total_1_16_120_NE * 100
    percentage_1_16_64_employed = total_1_16_64_NE_employed / total_1_16_64_NE * 100
    percentage_1_16_24_employed = total_1_16_24_NE_employed / total_1_16_24_NE * 100
    percentage_1_25_34_employed = total_1_25_34_NE_employed / total_1_25_34_NE * 100
    percentage_1_35_49_employed = total_1_35_49_NE_employed / total_1_35_49_NE * 100
    percentage_1_50_64_employed = total_1_50_64_NE_employed / total_1_50_64_NE * 100
    percentage_1_65_120_employed = total_1_65_120_NE_employed / total_1_65_120_NE * 100

    print(percentage_1_16_120_employed)
    print(percentage_1_16_64_employed)
    print(percentage_1_16_24_employed)
    print(percentage_1_25_34_employed)
    print(percentage_1_35_49_employed)
    print(percentage_1_50_64_employed)
    print(percentage_1_65_120_employed)


    #########################################

    ## EMPLOYMENT RATES:
    ## Check values obtained for females:


    ###########################################


    # Number of employed people grouped by sex and age range:
    total_2_16_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 2)])
    total_2_16_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_16_24_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 24) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_25_34_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 25) & (df_persons_NE_employed['Age'] <= 34) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_35_49_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 35) & (df_persons_NE_employed['Age'] <= 49) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_50_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 50) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_65_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 65) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 2)])

    # Total number of people in the population grouped by sex and age range
    total_2_16_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_16_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_16_24_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 16) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 24) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_25_34_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 25) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 34) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_35_49_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 35) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 49) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_50_64_NE = len(df_persons_NE_Household_composition_updated.loc[
                               (df_persons_NE_Household_composition_updated['Age'] >= 50) & (
                                           df_persons_NE_Household_composition_updated['Age'] <= 64) & (
                                           df_persons_NE_Household_composition_updated['Sex'] == 2)])
    total_2_65_120_NE = len(df_persons_NE_Household_composition_updated.loc[
                                (df_persons_NE_Household_composition_updated['Age'] >= 65) & (
                                            df_persons_NE_Household_composition_updated['Age'] <= 120) & (
                                            df_persons_NE_Household_composition_updated['Sex'] == 2)])

    # Percentage of people employed grouped by sex and age range:
    percentage_2_16_120_employed = total_2_16_120_NE_employed / total_2_16_120_NE * 100
    percentage_2_16_64_employed = total_2_16_64_NE_employed / total_2_16_64_NE * 100
    percentage_2_16_24_employed = total_2_16_24_NE_employed / total_2_16_24_NE * 100
    percentage_2_25_34_employed = total_2_25_34_NE_employed / total_2_25_34_NE * 100
    percentage_2_35_49_employed = total_2_35_49_NE_employed / total_2_35_49_NE * 100
    percentage_2_50_64_employed = total_2_50_64_NE_employed / total_2_50_64_NE * 100
    percentage_2_65_120_employed = total_2_65_120_NE_employed / total_2_65_120_NE * 100

    print(percentage_2_16_120_employed)
    print(percentage_2_16_64_employed)
    print(percentage_2_16_24_employed)
    print(percentage_2_25_34_employed)
    print(percentage_2_35_49_employed)
    print(percentage_2_50_64_employed)
    print(percentage_2_65_120_employed)

    # Remove the people classified as 'employed' and the remaining will be considered as 'unemployed'

    ## Remove the previous selected people and keep the remaining ones
    df_persons_NE_NO_inactive_plus_employed = (pd.concat([df_persons_NO_inactive, df_persons_NE_employed]))

    # Remove duplicates and keep only those who were not selected as "Inactive" or "Employed"
    df_persons_NE_unemployed = df_persons_NE_NO_inactive_plus_employed.drop_duplicates(subset='PID_AreaMSOA', keep=False)

    #########################################


    ## UNEMPLOYMENT RATES:
    ## Check values obtained for males:


    ###########################################


    # Number of unemployed people grouped by sex and age range:
    total_1_16_120_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 16) & (
                df_persons_NE_unemployed['Age'] <= 120) & (df_persons_NE_unemployed['Sex'] == 1)])
    total_1_16_64_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 16) & (
                df_persons_NE_unemployed['Age'] <= 64) & (df_persons_NE_unemployed['Sex'] == 1)])
    total_1_16_24_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 16) & (
                df_persons_NE_unemployed['Age'] <= 24) & (df_persons_NE_unemployed['Sex'] == 1)])
    total_1_25_34_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 25) & (
                df_persons_NE_unemployed['Age'] <= 34) & (df_persons_NE_unemployed['Sex'] == 1)])
    total_1_35_49_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 35) & (
                df_persons_NE_unemployed['Age'] <= 49) & (df_persons_NE_unemployed['Sex'] == 1)])
    total_1_50_64_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 50) & (
                df_persons_NE_unemployed['Age'] <= 64) & (df_persons_NE_unemployed['Sex'] == 1)])
    total_1_65_120_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 65) & (
                df_persons_NE_unemployed['Age'] <= 120) & (df_persons_NE_unemployed['Sex'] == 1)])

    # Number of employed people grouped by sex and age range:
    total_1_16_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 1)])
    total_1_16_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_16_24_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 24) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_25_34_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 25) & (df_persons_NE_employed['Age'] <= 34) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_35_49_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 35) & (df_persons_NE_employed['Age'] <= 49) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_50_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 50) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 1)])
    total_1_65_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 65) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 1)])

    # Percentage of people unemployed grouped by sex and age range:
    percentage_1_16_120_unemployed = total_1_16_120_NE_unemployed / (
                total_1_16_120_NE_unemployed + total_1_16_120_NE_employed) * 100
    percentage_1_16_64_unemployed = total_1_16_64_NE_unemployed / (
                total_1_16_64_NE_unemployed + total_1_16_64_NE_employed) * 100
    percentage_1_16_24_unemployed = total_1_16_24_NE_unemployed / (
                total_1_16_24_NE_unemployed + total_1_16_24_NE_employed) * 100
    percentage_1_25_34_unemployed = total_1_25_34_NE_unemployed / (
                total_1_25_34_NE_unemployed + total_1_25_34_NE_employed) * 100
    percentage_1_35_49_unemployed = total_1_35_49_NE_unemployed / (
                total_1_35_49_NE_unemployed + total_1_35_49_NE_employed) * 100
    percentage_1_50_64_unemployed = total_1_50_64_NE_unemployed / (
                total_1_50_64_NE_unemployed + total_1_50_64_NE_employed) * 100
    percentage_1_65_120_unemployed = total_1_65_120_NE_unemployed / (
                total_1_65_120_NE_unemployed + total_1_65_120_NE_employed) * 100

    print(percentage_1_16_120_unemployed)
    print(percentage_1_16_64_unemployed)
    print(percentage_1_16_24_unemployed)
    print(percentage_1_25_34_unemployed)
    print(percentage_1_35_49_unemployed)
    print(percentage_1_50_64_unemployed)
    print(percentage_1_65_120_unemployed)


    #########################################


    ## UNEMPLOYMENT RATES:
    ## Check values obtained for females:


    ###########################################


    # Number of unemployed people grouped by sex and age range:
    total_2_16_120_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 16) & (
                df_persons_NE_unemployed['Age'] <= 120) & (df_persons_NE_unemployed['Sex'] == 2)])
    total_2_16_64_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 16) & (
                df_persons_NE_unemployed['Age'] <= 64) & (df_persons_NE_unemployed['Sex'] == 2)])
    total_2_16_24_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 16) & (
                df_persons_NE_unemployed['Age'] <= 24) & (df_persons_NE_unemployed['Sex'] == 2)])
    total_2_25_34_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 25) & (
                df_persons_NE_unemployed['Age'] <= 34) & (df_persons_NE_unemployed['Sex'] == 2)])
    total_2_35_49_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 35) & (
                df_persons_NE_unemployed['Age'] <= 49) & (df_persons_NE_unemployed['Sex'] == 2)])
    total_2_50_64_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 50) & (
                df_persons_NE_unemployed['Age'] <= 64) & (df_persons_NE_unemployed['Sex'] == 2)])
    total_2_65_120_NE_unemployed = len(df_persons_NE_unemployed.loc[(df_persons_NE_unemployed['Age'] >= 65) & (
                df_persons_NE_unemployed['Age'] <= 120) & (df_persons_NE_unemployed['Sex'] == 2)])

    # Number of employed people grouped by sex and age range:
    total_2_16_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 2)])
    total_2_16_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_16_24_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 16) & (df_persons_NE_employed['Age'] <= 24) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_25_34_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 25) & (df_persons_NE_employed['Age'] <= 34) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_35_49_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 35) & (df_persons_NE_employed['Age'] <= 49) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_50_64_NE_employed = len(df_persons_NE_employed.loc[
                                        (df_persons_NE_employed['Age'] >= 50) & (df_persons_NE_employed['Age'] <= 64) & (
                                                    df_persons_NE_employed['Sex'] == 2)])
    total_2_65_120_NE_employed = len(df_persons_NE_employed.loc[
                                         (df_persons_NE_employed['Age'] >= 65) & (df_persons_NE_employed['Age'] <= 120) & (
                                                     df_persons_NE_employed['Sex'] == 2)])

    # Percentage of people unemployed grouped by sex and age range:
    percentage_2_16_120_unemployed = total_2_16_120_NE_unemployed / (
                total_2_16_120_NE_unemployed + total_2_16_120_NE_employed) * 100
    percentage_2_16_64_unemployed = total_2_16_64_NE_unemployed / (
                total_2_16_64_NE_unemployed + total_2_16_64_NE_employed) * 100
    percentage_2_16_24_unemployed = total_2_16_24_NE_unemployed / (
                total_2_16_24_NE_unemployed + total_2_16_24_NE_employed) * 100
    percentage_2_25_34_unemployed = total_2_25_34_NE_unemployed / (
                total_2_25_34_NE_unemployed + total_2_25_34_NE_employed) * 100
    percentage_2_35_49_unemployed = total_2_35_49_NE_unemployed / (
                total_2_35_49_NE_unemployed + total_2_35_49_NE_employed) * 100
    percentage_2_50_64_unemployed = total_2_50_64_NE_unemployed / (
                total_2_50_64_NE_unemployed + total_2_50_64_NE_employed) * 100
    percentage_2_65_120_unemployed = total_2_65_120_NE_unemployed / (
                total_2_65_120_NE_unemployed + total_2_65_120_NE_employed) * 100

    print(percentage_2_16_120_unemployed)
    print(percentage_2_16_64_unemployed)
    print(percentage_2_16_24_unemployed)
    print(percentage_2_25_34_unemployed)
    print(percentage_2_35_49_unemployed)
    print(percentage_2_50_64_unemployed)
    print(percentage_2_65_120_unemployed)

    # update the column value in each of the obtained dataframes

    # Update the "Economic_activity" to each of the dataframes generated before:

    df_persons_NE_employed["Economic_activity"] = "Employed"

    df_persons_NE_inactive["Economic_activity"] = "Inactive"

    df_persons_NE_unemployed["Economic_activity"] = "Unemployed"

    # Export the dataframes as csv files
    df_persons_NE_employed_20211122 = df_persons_NE_employed
    df_persons_NE_inactive_20211117 = df_persons_NE_inactive
    df_persons_NE_unemployed_20211122 = df_persons_NE_unemployed

    df_persons_NE_employed_20211122.to_csv(path + '/' + year + '/NE_only/df_persons_NE_employed_20211122.csv',
        encoding='utf-8', header=True)

    df_persons_NE_inactive_20211117.to_csv(path + '/' + year + '/NE_only/df_persons_NE_inactive_20211117.csv',
        encoding='utf-8', header=True)

    df_persons_NE_unemployed_20211122.to_csv(path + '/' + year + '/NE_only/df_persons_NE_unemployed_2021112.csv',
        encoding='utf-8', header=True)
