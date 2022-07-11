import glob
import pandas as pd
import numpy as np
import os
import csv
import sys


def marital_status(LC4408_C_AHTHUK11_x, Age, Adult_Similar_age):
    if LC4408_C_AHTHUK11_x == 2 and Age >= 18 and Adult_Similar_age == True:
        Marital_status = "Married"
    elif LC4408_C_AHTHUK11_x == 3 and Age >= 18 and Adult_Similar_age == True:
        Marital_status = "Couple"
    else:
        Marital_status = "Single"
    return Marital_status


def children_dependency(LC4408_C_AHTHUK11_x, Age, Total_Children_in_household):
    if (LC4408_C_AHTHUK11_x == 2 or LC4408_C_AHTHUK11_x == 3 or LC4408_C_AHTHUK11_x == 4) and Age >= 18 and Total_Children_in_household > 0:
        Children_dependency = True
    else:
        Children_dependency = False
    return Children_dependency


if __name__ == '__main__':
    path = sys.argv[1]
    year = sys.argv[2]
    from_ = int(sys.argv[3])

    #Read CSV file containing the MSOA and OA values only from the North East of England
    df_persons_NE__dir = path + '/' + year + '/NE_only' # use your path
    df_persons_NE__file = os.path.join(df_persons_NE__dir, "df_persons_NE_clean.csv")
    df_persons_NE = pd.read_csv(df_persons_NE__file, index_col=None, header=0)

    #Read CSV file containing the MSOA and OA values only from the North East of England
    df_households_NE__dir = path + '/' + year + '/NE_only' # use your path
    df_households_NE_file = os.path.join(df_households_NE__dir, "df_households_NE_clean.csv")
    df_households_NE = pd.read_csv(df_households_NE_file, index_col=None, header=0)

    #Create new columns in the dataframe:

    #Column with the total amount of people in the household
    df_persons_NE["Total_People_in_household"] = 0

    #Column with the total amoun of children in the household
    df_persons_NE["Total_Children_in_household"] = 0

    #Column showing if in the household there is another adult with the same ethnic
    df_persons_NE["Same_ethnic"] = np.nan
    df_persons_NE["Same_ethnic"] = df_persons_NE["Same_ethnic"].astype('bool')  #False by default
    df_persons_NE["Same_ethnic"] = False

    #Column showing if in the household there is another adult with a similar age (+-10 years)
    df_persons_NE["Adult_Similar_age"] = np.nan
    df_persons_NE["Adult_Similar_age"] = df_persons_NE["Adult_Similar_age"].astype('bool')    #False by default
    df_persons_NE["Adult_Similar_age"] = False

    # Calculate for each person:
    #     the total number in the household
    #     The total number of children in the household
    #     If there are more people with the same ethnicity in the household
    #     If there is at least one more adult with a similar age


    # Create a list with all Households unique ID values
    HID_AreaOA_list = df_households_NE['HID_AreaOA'].tolist()
    HID_AreaOA_list.sort()

    # Create an empty list where the small blocks of dataframes will be stored
    df_persons_NE_OA_HID_temp = []

    # Create a variable that counts the number of households iterated
    household_counter = 0

    if from_ == -1:
        from_ = 0
        to_ = len(HID_AreaOA_list)
    else:
        to_ = min(len(HID_AreaOA_list), from_ + 100000)

    for HID_AreaOA in HID_AreaOA_list[from_:to_]:
        # Increase the value of the household_counter in 1
        household_counter += 1
        print("Number of HOUSEHOLD in iteration: ", (household_counter, (to_-from_)))

        # Get only the PERSONS that belong to the same HID_AreaOA
        df_persons_NE_OA_HID = df_persons_NE.loc[df_persons_NE['HID_AreaOA_x'] == HID_AreaOA]
        # print(df_persons_NE_OA_HID)

        ##Do the calculus just HOUSEHOLD BY HOUSEHOLD
        for idx_person_1, person_1 in df_persons_NE_OA_HID.iterrows():
            count_people = 1
            if person_1['Age'] < 18:
                count_children = 1
            else:
                count_children = 0
            for idx_person_2, person_2 in df_persons_NE_OA_HID.iterrows():
                # If person_1 is different to person_2:
                if (person_1['PID'] != person_2['PID']):
                    count_people += 1
                    # If person_1 is older than 18
                    if person_2['Age'] < 18:
                        count_children += 1
                    else:
                        # If person_1 is older than 18 and the difference of age between him/her and person_2 is below 10 years:
                        if (person_1['Age'] > 18 and (
                                (-10 <= person_2['Age'] - person_1['Age'] and person_2['Age'] - person_1['Age'] <= 10) or (
                                -10 <= person_1['Age'] - person_2['Age'] and person_1['Age'] - person_2['Age'] <= 10))):
                            df_persons_NE_OA_HID.at[idx_person_1, 'Adult_Similar_age'] = True

                    # If person_1 and person_2 have the same ethnic:
                    if person_1['Ethnic'] == person_2['Ethnic']:
                        df_persons_NE_OA_HID.at[idx_person_1, 'Same_ethnic'] = True

            # Update values in the person's row
            df_persons_NE_OA_HID.at[idx_person_1, 'Total_People_in_household'] = count_people
            df_persons_NE_OA_HID.at[idx_person_1, 'Total_Children_in_household'] = count_children

        # Append the dataframe into the temporal list
        df_persons_NE_OA_HID_temp.append(df_persons_NE_OA_HID)

    # concatenate all persons (lists of the 'df_persons_NE_OA_HID_temp' list) in one dataframe
    df_persons_NE_Household_composition = pd.concat(df_persons_NE_OA_HID_temp, axis=0, ignore_index=True)

    #Column showing if an adult has his/her own car
    df_persons_NE_Household_composition["Marital_status"] = ""

    #Column showing if an adult has children dependency
    df_persons_NE_Household_composition["Children_dependency"] = np.nan
    df_persons_NE_Household_composition["Children_dependency"] = df_persons_NE_Household_composition["Children_dependency"].astype('bool')
    df_persons_NE_Household_composition["Children_dependency"] = False

    # Run the lambda function "marital_status" to classify each person in married, couple or single, depending on their own characteristics
    df_persons_NE_Household_composition['Marital_status'] = df_persons_NE_Household_composition.apply(lambda x: marital_status(x['LC4408_C_AHTHUK11_x'], x['Age'], x['Adult_Similar_age']), axis=1)

    # Run the lambda function "Children_dependency" to identify which adults have children dependencies
    df_persons_NE_Household_composition['Children_dependency'] = df_persons_NE_Household_composition.apply(lambda x: children_dependency(x['LC4408_C_AHTHUK11_x'], x['Age'], x['Total_Children_in_household']), axis=1)

    #Export the df_persons_NE_household_composition_updated
    df_persons_NE_Household_compositions_export = df_persons_NE_Household_composition
    df_persons_NE_Household_compositions_export.to_csv(path + '/' + year + '/NE_only/df_persons_NE_Household_composition_updated_' + str(to_) + '.csv', encoding='utf-8', header=True)
