import numpy as np
import pandas as pd
import os
import math

path = r"C:\Users\danie\Desktop\Elections Data Repositories\2020-precincts\precinct\GA\2020-ga-precinct-general"

os.chdir(path)

df_ga = pd.read_csv("2020-ga-precinct-general.csv")

def fix_chars(string):
    if 'BOBBY WEST' in string:
        return 'BOBBY WESTON WILLIFORD'
    if 'ANTHONY PIERCE' in string:
        return 'ANTHONY PIERCE'
    if '\"' in string:
        split_string = string.split('\"')
        if len(split_string) == 3:
            return (split_string[0] + split_string[2]).replace('  ', ' ')
    
    return string.replace('\"', '')


for j in range(len(df_ga['dataverse'].values)):
    if j == math.floor(.1*len(df_ga['dataverse'].values)):
        print('10% done')
    if j == math.floor(.25 * len(df_ga['dataverse'].values)):
        print('25% done')
    if j == math.floor(.50 * len(df_ga['dataverse'].values)):
        print('50% done')
    if j == math.floor(.75 * len(df_ga['dataverse'].values)):
        print('75% done')

    district = df_ga['district'].values[j]
    office = df_ga['office'].values[j]
        
    if df_ga['office'].values[j] == 'TAX COMMISSIONER':
        df_ga['dataverse'].values[j] = 'LOCAL'

    cand_arr = df_ga['candidate'].values
        
    if cand_arr[j] == 'ALLEN BUCKLEY':
        df_ga['party_detailed'].values[j] = 'INDEPENDENT'
        df_ga['party_simplified'].values[j] = 'OTHER'
    
    dist_arr = df_ga['district'].values
    office_arr = df_ga['office'].values
    
    if dist_arr[j] == '039' and office_arr[j] == 'STATE SENATE':
        df_ga['special'].values[j] = 'TRUE'

    if cand_arr[j] == 'GARRY GUAN' or cand_arr[j] == 'SALLY HARRELL':
        df_ga['district'].values[j] = '040'
    if cand_arr[j] == 'WILLIAM PARK FREEMAN' or cand_arr[j] == 'KIM JACKSON':
        df_ga['district'].values[j] = '041'
    if cand_arr[j] == 'CLINT DIXON' or cand_arr[j] == 'MATIELYN JONES':
        df_ga['district'].values[j] = '045'
    if cand_arr[j] == 'MATT REEVES' or cand_arr[j] == 'MICHELLE AU':
        df_ga['district'].values[j] = '048'

df_ga['candidate'] = df_ga['candidate'].apply(fix_chars)

df_ga.to_csv(r"C:\Users\danie\Desktop\Elections Data Repositories\2020-precincts\precinct\GA\2020-ga-precinct-general.csv")
        
