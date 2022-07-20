import os
import sys
import pandas as pd

# Load synthetic population for province
if __name__ == '__main__':
    path = sys.argv[1]
    year = str(sys.argv[2])

    list_pop = []
    path = path + '/' + year + '/NE_only/'
    for file in os.listdir(path):
        if file.startswith("df_after_occupation_"):
            dat = pd.read_csv(path + "/" + file)
            list_pop.append(dat)
    df_pop = pd.concat(list_pop)
    df_pop.reset_index(inplace=True)
    df_pop.to_csv(path + '/df_after_occupation.csv', encoding='utf-8', header=True)
