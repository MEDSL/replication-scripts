#!/usr/bin/env python
# coding: utf-8
# DC 1/25/2022

import pandas as pd
import numpy as np
import re
import os
import numbers
import csv


def format_pdf_scraped_data(stacked_df, xl, office):
    # pdf scraped data are outputted as tables stacked on top of each other
    # separated by blank rows. Function unstacks the dfs and stores them in a list
    def unstack_data():
        separator_index=list(stacked_df.index[stacked_df.isna().all(axis=1)])
        stack_list = []
        for i in np.arange(len(separator_index)+1):
            if i ==0:
                df = xl.parse(0, skipfooter= (len(stacked_df)-separator_index[0]))
                stack_list = stack_list + [df]
            elif i in np.arange(len(separator_index)):
                df = xl.parse(0, skiprows=(separator_index[i-1]+2),skipfooter= len(stacked_df)-separator_index[i])
                stack_list = stack_list + [df]
            else:
                df = xl.parse(0, skiprows=(separator_index[i-1]+2))
                stack_list = stack_list + [df]
        stack_list = [i for i in stack_list if len(i)>0] #removed df created as a result of multiple null rows'
        return stack_list
    unstacked = unstack_data()
    ## statewide offices with no district info
    if (office == 'US PRESIDENT') or (office == 'US SENATE'):
        col_names = np.array(unstacked[0].loc[3].fillna('').str.upper()) + '-' + np.array(unstacked[0].fillna('').loc[4].str.upper())
        col_names[0] = 'precinct'
        df_list = []
        for df in unstacked:
            county = df.iloc[2,0].upper().replace(' COUNTY',"")
            df.columns = col_names
            df['county_name'] = county
            df['district'] = 'STATEWIDE'
            N = [i for i, x in enumerate([isinstance(i, int) for i in df.iloc[:,1]]) if x][0]
            #remove header rows and null last row
            df = df.iloc[N:-1 , :]
            df = pd.melt(df, id_vars=['precinct','county_name','district'], value_vars=list(df.columns[1:-2]),
                     value_name='votes',var_name='candidate')
            df['office'] = office
            df_list = df_list + [df]
    ## US House, district offices
    elif office == 'US HOUSE':
        df_list = []
        for df in unstacked:
            col_names=np.array(df.loc[3].fillna('').str.upper()) + '-' + np.array(df.fillna('').loc[4].str.upper())
            col_names[0] = 'precinct'
            district = df.iloc[2,0].split(' ')[-1]
            df.columns = col_names
            df['district'] = str(district).zfill(3)
            df=df.dropna(axis=1,how='all')
            N = [i for i, x in enumerate([isinstance(i, int) for i in df.iloc[:,1]]) if x][0]
            #remove header rows and null last row
            df = df.iloc[N:-2 , :]
            df['precinct'] = df['precinct'].str.upper()
            df['county_name'] = [i.replace(' TOTALS','') if 'TOTALS' in i else np.nan for i in df['precinct'].fillna('')]
            df['county_name'] = df['county_name'].bfill()
            df = pd.melt(df, id_vars=['precinct','county_name','district'], value_vars=list(df.columns[1:-2]),
                     value_name='votes',var_name='candidate')
            df['office'] = office
            df_list = df_list + [df]
    # state legislative special 
    elif office == 'STATE LEGISLATURE':
        df_list = []
        for df in unstacked:
            col_names = (np.array(unstacked[0].loc[4].ffill().fillna('').str.upper())
                 + '-' + np.array(unstacked[0].fillna('').loc[5].str.upper()) 
                 + '-' + np.array(unstacked[0].fillna('').loc[6].str.upper()) )
            col_names[0] = 'precinct'
            df.columns = col_names
            df=df.dropna(subset=[df.columns[0]]).copy()
            county = df.iloc[4,0]
            df['county_name'] = county
            df['district'] = '025'
            N = [i for i, x in enumerate([isinstance(i, numbers.Number) for i in df.iloc[:,1].fillna('')]) if x][0]
            
            #remove header rows and null last row
            df = df.iloc[N: , :]
            df = pd.melt(df, id_vars=['precinct','county_name','district'], value_vars=list(df.columns[1:-2]),
                     value_name='votes',var_name='candidate')
            df['office'] = [i.split('-')[0] for i in df['candidate']]
            df['office'] = df['office'].replace({'GENERAL ASSEMBLY':"STATE HOUSE"})
            df['candidate'] = [i.split('-')[1] + '-' + i.split('-')[2] for i in df['candidate']]
            df_list = df_list + [df]
    df = pd.concat(df_list)
    df = df.dropna(subset=['votes']).copy()
    df = df[~(df['votes']=='NJDOE-ds12/18/2020')].copy()
    df['votes'] = df['votes'].astype(int)
    return df

# scraped pdf results
pres_excel = pd.read_excel('raw/township/2020-official-general-results-president-combined.xlsx')
pres_xl =pd.ExcelFile('raw/township/2020-official-general-results-president-combined.xlsx')

sen_excel = pd.read_excel('raw/township/2020-official-general-results-us-senate-combined.xlsx')
sen_xl = pd.ExcelFile('raw/township/2020-official-general-results-us-senate-combined.xlsx')

house_excel = pd.read_excel('raw/township/2020-official-general-results-us-house-district-combined.xlsx')
house_xl = pd.ExcelFile('raw/township/2020-official-general-results-us-house-district-combined.xlsx')

state_leg_excel = pd.read_excel('raw/township/2020-official-general-results-state-senate-general-assembly-25th-ld.xlsx')
state_leg_xl = pd.ExcelFile('raw/township/2020-official-general-results-state-senate-general-assembly-25th-ld.xlsx')

# apply function
pres = format_pdf_scraped_data(pres_excel,pres_xl, "US PRESIDENT")
senate=format_pdf_scraped_data(sen_excel,sen_xl, "US SENATE")
house = format_pdf_scraped_data(house_excel,house_xl,'US HOUSE')
state_leg = format_pdf_scraped_data(state_leg_excel,state_leg_xl,'STATE LEGISLATURE')

# concat all results
df = pd.concat([pres, senate, house, state_leg])

#drop agg precincts
df['precinct'] = df['precinct'].str.upper()
df = df[~(df['precinct'].str.contains('TOTAL'))].copy()

#party
df['party_detailed'] = [party.split('-')[-1] for party in df['candidate']]
df['party_detailed'] = df['party_detailed'].replace({'DEMOCRATIC':"DEMOCRAT"}).str.replace(' PARTY','',regex=True)
def get_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','LIBERTARIAN','NONPARTISAN',""]: return x
    else: return "OTHER"
df['party_simplified'] = df.party_detailed.apply(get_simplified)

# candidate field
df['candidate'] = [cand.split('-')[0] for cand in df['candidate']]
df['candidate'] = df['candidate'].str.replace('\.','',regex=True)

#fips codes
df['state'] = "NEW JERSEY"
fips = pd.read_csv('../../help-files/county-fips-codes.csv')
fips['state'] = fips['state'].str.upper()
df=df.merge(fips, on = ['state','county_name'])
df['jurisdiction_name'] = df['county_name']
df['jurisdiction_fips'] = df['county_fips']
# state codes
state_codes=pd.read_csv('../../help-files/merge_on_statecodes.csv')
state_codes['state'] = state_codes['state'].str.upper()
df = df.merge(state_codes, on = 'state', how = 'left')

# special
df['special'] = np.where(df['office'].isin(['STATE HOUSE', 'STATE SENATE']), 'TRUE','FALSE')

# other
df['mode'] = "TOTAL"
df['dataverse'] = np.where(df['office'].isin(['STATE HOUSE', 'STATE SENATE']), 'STATE',
                                            np.where(df['office']=='US PRESIDENT', 'PRESIDENT',
                                                    np.where(df['office']=='US HOUSE', 'HOUSE', 'SENATE')))
df['year'] = 2020
df['date'] = '2020-11-03'
df['stage'] = 'GEN'
df['writein'] = 'FALSE'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1

# write csv
df.to_csv('2020-nj-precinct-general.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)

# counts all match

