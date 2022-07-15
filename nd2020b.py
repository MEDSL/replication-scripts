#!/usr/bin/env python
# coding: utf-8

# In[261]:


import pandas as pd
import numpy as np
import os
import re
import csv
from tqdm.notebook import tqdm
pd.options.display.max_columns =37
pd.options.display.max_rows =2000


# In[277]:


os.chdir('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/ND/raw/STATELEG_new')


# In[292]:


files = [i for i in os.listdir() if '.xlsx' in i]
df_list = []
for file in files:
    xls = pd.read_excel(file, sheet_name = None)
    sheets = list(xls.keys())
    for index,sheet in zip(np.arange(len(sheets)),sheets):
        df = pd.read_excel(file, sheet_name = index, skiprows=6)
        df['office'] = df.columns[0]
        df['office'] = df['office'].replace({"State Representative":"STATE HOUSE",'State Senator':"STATE SENATE"})
        df = df.rename(columns = {"State Representative":'district','State Senator':'district','Precinct':'precinct'})
        df['district'] = df['district'].ffill().str.replace('District ','').str.zfill(3)
        df = df.iloc[:-1,:]
        df = pd.melt(df, id_vars = ['office','district','precinct'], value_vars = df.columns[2:-1],
                    value_name='votes',var_name='candidate')
        df['county_name'] = sheet.upper()
        df_list = df_list + [df]


# In[293]:


df = pd.concat(df_list)
df['precinct'] = df['precinct'].str.upper().str.strip()
df['candidate'] = df['candidate'].str.upper().str.strip().replace('WRITE-IN','WRITEIN').str.replace('\s+',' ',regex=True)
df['candidate'] = df['candidate'].replace({'EMILY O"BRIEN':"EMILY O'BRIEN"})
party1 = pd.read_excel('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/ND/CandidateListExportRep.xls')
party2 = pd.read_excel('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/ND/CandidateListExportSen.xls')
party = pd.concat([party1,party2])
party['candidate'] = np.where(party['Middle Name'].isnull(),
                             party['First Name'] + ' ' + party['Last Name'],
                             party['First Name'] + ' ' + party['Middle Name'] + ' '+ party['Last Name'])
party = party[['Contest','candidate','Party','District']].copy()
party.columns = ['office','candidate','party_detailed','district']
party['candidate'] = party['candidate'].str.replace('\.','',regex=True).str.upper()
party['candidate'] = party['candidate'].str.replace(r'\([^)]*\) ', '',regex=True)
party['office'] = party['office'].replace({"State Representative":"STATE HOUSE",'State Senator':"STATE SENATE"})
party['district'] = party['district'].str.replace('District ','').str.zfill(3)
party['party_detailed'] = party['party_detailed'].str.upper()

leg=df.merge(party, on =['office','district','candidate'],how='left')
leg['party_detailed'] = leg['party_detailed'].fillna("")

leg['state'] = 'NORTH DAKOTA'
def merge_fips_codes(df):
    # add county codes
    fips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv")
    fips['state'] = fips['state'].str.upper()
    df = pd.merge(df, fips, on = ['state','county_name'],how = 'left')
    df['county_fips'] = df['county_fips'].astype(str).str.replace('\.0','', regex=True).str.zfill(5)
    # get jurisdiction fips codes
    juris_fips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/jurisdiction-fips-codes.csv",dtype={'jurisdiction_fips':str})
    juris_fips['state'] = juris_fips['state'].str.upper()
    # get list of states with non-county jurisdiction fips codes
    states_w_juris = list(map(str.upper, juris_fips[juris_fips['jurisdiction_fips'].str.len()>5]['state'].unique()))
    if df['state'].unique()[0] not in states_w_juris:
        df['jurisdiction_fips'] = df['county_fips']
        df['jurisdiction_name'] = df['county_name']
        return df
    else: # otherwise merge unique jurisdiction fips codes
        if 'jurisdiction_name' not in df.columns:
            raise ValueError('!!! Missing column jurisdiction_name !!!')
        else:
            juris_fips['county_fips'] = juris_fips['jurisdiction_fips'].str.zfill(10).apply(lambda x: str(x)[:5])
            df = df.merge(juris_fips, on=['state', 'county_fips', 'jurisdiction_name'], how="left")
            # may require a crosswalk to fix misnamed jurisdictions, so check for null jurisdiction_fips
            if len(df[df['jurisdiction_fips'].isnull()])>0:
                print("!!! Failed Jurisdiction FIPS Merge, inspect rows where jurisdiction_fips is null !!!")
            else:
                df['jurisdiction_fips'] = df['jurisdiction_fips'].str.zfill(10)
            return df
leg = merge_fips_codes(leg)
leg['dataverse'] = 'STATE'


# In[294]:


path = '/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/ND/2020-nd-precinct-general-no-leg.csv'
official_dtypes = {'precinct':str,'office':str, 'party_detailed':str,
                   'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str,
                   'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str,
                   'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str,
                   'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str,
                   'readme_check':str,'magnitude':int}
df = pd.read_csv(path, dtype = official_dtypes)
df = df.fillna("")
df['precinct'] = df['precinct'].str.upper().str.strip()
df['office'] = df['office'].replace({"PRESIDENT":"US PRESIDENT"})
df.loc[df['office']=='US PRESIDENT','district'] = 'STATEWIDE'
df['candidate'] = df['candidate'].replace({'TRUMP AND PENCE':'DONALD J TRUMP',
                                          'JORGENSEN AND COHEN':'JO JORGENSEN',
                                          'BIDEN AND HARRIS':'JOSEPH R BIDEN'})


# In[295]:


cols=[i for i in df.columns if i not in leg.columns]
df = pd.concat([df,leg])
for col in cols:
    df[col] = df[col].ffill()


# In[296]:


df['magnitude'] = np.where(df['office']=='STATE HOUSE',2,1)
df['year'] = df['year'].astype(int)
df['writein'] = np.where(df['candidate']=="WRITEIN",'TRUE','FALSE')
df.loc[df['candidate']=='WRITEIN','party_detailed'] = ""
def get_party_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','NONPARTISAN',"LIBERTARIAN"]: return x
    if x == '': return ''
    else: return "OTHER"
df['party_simplified'] = df.party_detailed.apply(get_party_simplified)


# In[297]:


df.to_csv('../../2020-nd-precinct-general.csv',index=False, quoting=csv.QUOTE_NONNUMERIC)


# In[ ]:




