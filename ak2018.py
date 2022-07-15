#!/usr/bin/env python
# coding: utf-8

# It appears Alyse Galvin—a house candidate in Alaska—is coded as democrat in district_overall_2018.csv, when according to her campaign website and ballotpedia.org page she ran as an independent.
# 
# Not sure if there are any other races miscoded in a such a way, but should presumably be looked into.
# 
# 
# ~district~, candidate, ~office~, ~readme_check~, ~magnitude~, ~special~, ~precinct~, ~dataverse~, ~mode~, ~votes~, ~party_detailed~, ~party_simplified~, ~county_name~ , ~county_fips~, ~jurisdiction_name~, ~jurisdiction_fips~, ~year~, ~stage~, ~state~, ~writein~, ~state_po~, ~state_fips~, ~state_cen~, ~state_ic~, ~date~.

# In[6]:


import pandas as pd
import numpy as np
import os
import csv

df = pd.read_csv('2018-ak-precinct-autoadapted.csv')


# In[10]:


pd.set_option('display.max_columns', None)
df


# In[8]:


df["date"] = "2018-11-06"
df["readme_check"] = "FALSE"
df["magnitude"] = 1
df = df.drop(['jurisdiction_fips'], axis=1)
df['county_name'] = ""
df['county_fips'] = ""


# In[9]:


fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/ak_jurisdiction_crosswalk.csv')

fips = fips.applymap(str)
fips['precinct'] = fips['precinct'].str.upper()
df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['precinct', 'jurisdiction_name'], 
             how = 'left')
df['jurisdiction_fips'] = df['jurisdiction_fips'].str.zfill(5).replace('00000','')


# In[11]:

 # NOTE: Will be empty for AK (from 2020-readme)
# df['county_name'] = df['jurisdiction_name']
# df['county_fips'] = df['jurisdiction_fips']


# In[12]:


df.district = df.district.str.strip()
df["district"]= df["district"].str.zfill(3)

# df.district = df.district.str.replace('000','', regex=False) #this is for US HOUSE
df.district = df.district.str.replace('00A','A', regex=False)
df.district = df.district.str.replace('00C','C', regex=False)
df.district = df.district.str.replace('00E','E', regex=False)
df.district = df.district.str.replace('00G','G', regex=False)
df.district = df.district.str.replace('00I','I', regex=False)
df.district = df.district.str.replace('00K','K', regex=False)
df.district = df.district.str.replace('00M','M', regex=False)
df.district = df.district.str.replace('00O','O', regex=False)
df.district = df.district.str.replace('00Q','Q', regex=False)
df.district = df.district.str.replace('00S','S', regex=False)


# In[16]:


# for x in df['candidate'].unique():
#     print(x)


# In[17]:
df['candidate'] = df['candidate'].replace(np.nan, "")
df['candidate'] = df['candidate'].astype(str)
def cleanCandidate(x):
    if ',' in x:
        index = x.index(',')
        x = (x[index+2:] + ' ' + x[:index])
    if '.' in x:
        x = x.replace('.', '')
    if 'BEGICH/CALL' in x:
        x = 'MARK BEGICH'
    if 'DUNLEAVY/MEYER' in x:
        x = 'MIKE DUNLEAVY'
    if 'TOIEN/CLIFT' in x:
        x = 'WILLIAM TOIEN'
    if 'WALKER/MALLOTT' in x:
        x = 'BILL WALKER'
    if 'LYLE' in x:
        index = x.index('|')
        x = 'PAUL R LYLE - ' + x[index+1:]
    if 'MCCONAHY' in x:
        index = x.index('|')
        x = 'MICHAEL P MCCONAHY - ' + x[index+1:]
    if 'SEEKINS' in x:
        index = x.index('|')
        x = 'BEN SEEKINS - ' + x[index+1:]
    if 'COREY' in x:
        index = x.index('|')
        x = 'MICHAEL COREY - ' + x[index+1:]
    if 'MORSE' in x:
        index = x.index('|')
        x = 'WILLIAM F MORSE - ' + x[index+1:]
    if 'WALKER JR.' in x:
        index = x.index('|')
        x = 'HERMAN G WALKER JR - ' + x[index+1:]
    if 'WOLVERTON' in x:
        index = x.index('|')
        x = 'MICHAEL L WOLVERTON - ' + x[index+1:]
    if 'CHUNG' in x:
        index = x.index('|')
        x = 'JO-ANN M CHUNG - ' + x[index+1:]
    if 'CLARK' in x:
        index = x.index('|')
        x = 'BRIAN K CLARK - ' + x[index+1:]
    if 'ESTELLE' in x:
        index = x.index('|')
        x = 'WILLIAM L ESTELLE - ' + x[index+1:]
    if 'ILLSLEY' in x:
        index = x.index('|')
        x = 'SHARON A S ILLSLEY - ' + x[index+1:]
    if 'WOLFE' in x:
        index = x.index('|')
        x = 'JOHN W WOLFE - ' + x[index+1:]
    if 'CAREY' in x:
        index = x.index('|')
        x = 'WILLIAM B CAREY - ' + x[index+1:]
    if 'MILLER' in x:
        index = x.index('|')
        x = 'GREGORY MILLER - ' + x[index+1:]
    if 'SWANSON' in x:
        index = x.index('|')
        x = 'KRISTEN SWANSON - ' + x[index+1:]
    if 'KATELNIKOFF-LESTER' in x:
        x = 'SANDRA KATELNIKOFF-LESTER'
    else: 
        return x.upper() 
    return x.upper()


# In[18]:


df['candidate'] = df['candidate'].apply(cleanCandidate)
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True)


# In[76]:


df['candidate'] = df['candidate'].replace(['WALKER JR|YES','WALKER JR|NO'],
 ['HERMAN G WALKER JR - YES','HERMAN G WALKER JR - NO'])


# In[84]:


df.loc[df['candidate'].str.contains('ALYSE S GALVIN'), 'party_detailed'] = "INDEPENDENT"



df.loc[df['candidate'].str.contains('NINA AHMAD') & df['office'].str.contains('ATTORNEY GENERAL'), 'office'] = "AUDITOR GENERAL"

df['party_detailed'] = df['party_detailed'].fillna("")
def get_party_simplified(x):
    if x in ["",'DEMOCRAT','REPUBLICAN',"LIBERTARIAN",'NONPARTISAN']:
        return x
    else:
        return "OTHER"
df['party_simplified'] = df['party_detailed'].apply(get_party_simplified)



#Readme Check - Setting as FALSE for now 
df["readme_check"] = "FALSE"

df = df[~((df.drop(columns = 'votes').duplicated(keep = False)) & (df['votes']==0))].copy()

# Final step: Remove all trailing white space and put columns in correct order. 
# dc addition, change candidate blank to writein
df = df.replace([True,False], ['TRUE','FALSE'])
df.loc[((df['candidate']=="")&(df['writein']=='TRUE')),'candidate'] = 'WRITEIN'
df=df.replace('  ', ' ', regex = True)
df = df.replace(np.nan, "")
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]


# In[80]:



df.to_csv('2018-ak-precinct-general-updated.csv', quoting=csv.QUOTE_NONNUMERIC,index=False)

