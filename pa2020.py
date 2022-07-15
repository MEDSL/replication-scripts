#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import re
import csv
pd.options.display.max_columns =37
pd.options.display.max_rows =1500


# In[45]:


#read data
df_list = []
for file in ['ERStat_2020_G(179507)_20211006.txt', 'ERStat_WRT_2020_G(38663)_20211006.txt']:
    df = pd.read_csv('raw/2020 General Precinct Returns/' + file,
                    delimiter = ',',dtype={3:str,30:str},header=None)
    df.columns = ['year','stage','county_code','precinct_code','cand_rank','district','party_rank','ballot_pos',
                 'office_code','party_code','cand_number','cand_last','cand_first','cand_middle','cand_suffix',
                 'votes','yes_votes','no_votes','cong_district','senate_district','house_district','municipality_code',
                 'jurisdiction_name','municipality_breakdown_code1','municipality_breakdown_name1',
                 'municipality_breakdown_code2','municipality_breakdown_name2','bi_county_code','mcd_code','county_fips',
                 'vtd_code','ballot_question','record_type','previous_precinct','previous_cong_district',
                 'previous_senate_district','previous_house_district']
    df = df.loc[:,['year','stage','precinct_code','district','office_code','party_code',
     'cand_last','cand_first','cand_middle','cand_suffix','votes',
     'cong_district','senate_district','house_district',
     'jurisdiction_name','county_fips','vtd_code','cand_number']]
    if file == 'ERStat_WRT_2020_G(38663)_20211006.txt':
        df['writein'] = 'TRUE'
    else:
        df['writein'] = 'FALSE'
    df_list = df_list + [df]
df = pd.concat(df_list)


# In[46]:


# get columns
df = df.loc[:,['year','stage','precinct_code','district','office_code','party_code',
 'cand_last','cand_first','cand_middle','cand_suffix','votes',
 'cong_district','senate_district','house_district',
 'jurisdiction_name','county_fips','vtd_code','writein']]
# fix stage
df['stage']='GEN'


# In[47]:


# get candidate
df['cand_first'] = df['cand_first'].fillna("")
df['cand_middle'] = df['cand_middle'].fillna("")
df['cand_last'] = df['cand_last'].fillna("")
df['cand_suffix'] = df['cand_suffix'].fillna("")
df['candidate'] = df['cand_first'] + ' ' + df['cand_middle'] + ' ' + df['cand_last'] + ' ' + df['cand_suffix']
df['candidate'] = df['candidate'].str.replace('\s+', ' ',regex=True).replace(' ','').str.strip().str.upper()
df['candidate'] =df['candidate'].str.replace('\.','',regex=True).str.replace('&','AND',regex=True)
def fix_cand(x):
    if ',' in x: return x.split(', ')[1] + ' ' + x.split(', ')[0]
    if x=='SCATTERED': return 'WRITEIN'
    if x == 'JOSEPH ROBINETTE BIDEN JR': return 'JOSEPH R BIDEN'
    if x == 'DONALD J. TRUMP': return 'DONALD J TRUMP'
    else: return x
df['candidate'] = df['candidate'].apply(fix_cand)


# In[48]:


# assign offices from readme
office_map = {"USP" : "President Of The United States",
"USS" : "United States Senator",
"USC" : "Representative In Congress",
"STS" : "Senator In The General Assembly",
"STH" : "Representative In The General Assembly",
"ATT" : "Attorney General",
"AUD" : "Auditor General",
"TRE" : "State Treasurer",
"DED" : "Delegate To Democratic National Convention",
"DER" : "Delegate To Republican National Convention", 
"ADD" : "Alt Delegate To Democratic National Convention",
"ADR" : "Alt Delegate To Republican National Convention"}
df['office'] = df['office_code'].replace(office_map)


# In[49]:


# fix district
df['district'] = df['district'].astype(str).str.zfill(3).replace('000','STATEWIDE')


# In[50]:


# get precinct field
df['precinct'] = (df['precinct_code'] + '_' + 
                  df['cong_district'].astype(str).str.zfill(3) +
                  df['senate_district'].astype(str).str.zfill(3) +
                  df['house_district'].astype(str).str.zfill(3) + '_' +
                  df['vtd_code'].astype(str))


# In[51]:


# fix votes and drop bad rows
df['votes'] = df['votes'].astype(int) 
# drop single row with votes == .1 and missing candidate
#df = df[~((df['votes']<1)&(df['votes']>0))].copy()
# drop blank candidates with 0 votes
df = df[~((df['candidate']=="")&(df['votes']==0))]
df = df[~((df['writein']=="TRUE")&(df['votes']==0))]


# In[52]:


# fix office names
df['office'] = df['office'].str.upper() 
df['office'] = df['office'].replace({'PRESIDENT OF THE UNITED STATES':'US PRESIDENT',
                                    'REPRESENTATIVE IN CONGRESS':"US HOUSE",
                                    'SENATOR IN THE GENERAL ASSEMBLY':"STATE SENATE",
                                    'REPRESENTATIVE IN THE GENERAL ASSEMBLY':'STATE HOUSE'})
# get dataverse
def get_dataverse(x):
    if x == 'US PRESIDENT':
        return 'PRESIDENT'
    elif x == "US SENATE":
        return "SENATE"
    elif x == "US HOUSE":
        return "HOUSE"
    else: return 'STATE'
df['dataverse'] = df['office'].apply(get_dataverse)


# In[53]:


# get county names and juris fips
df['county_fips'] = ['42' + str(i).zfill(3) for i in df['county_fips']]
df['state'] = 'PENNSYLVANIA'
fips = pd.read_csv("../../help-files/county-fips-codes.csv",dtype={'county_fips':str})
fips['state'] = fips['state'].str.upper()
df = df.merge(fips, on =['state','county_fips'],how='left')
df['jurisdiction_fips'] = df['county_fips']
df['jurisdiction_name'] = df['jurisdiction_name'].str.replace('\s+',' ',regex=True).str.strip().str.upper()


# In[54]:


party_map = {"DEM":"DEMOCRAT", 'REP':'REPUBLICAN', 'LIB':"LIBERTARIAN", 'GRN':"GREEN",
            'D/R':'DEMOCRATIC/REPUBLICAN','IND':'INDEPENDENT', 'ASP':'Abolitionist Society Pennsylvania Party'.upper(),
            "UNP":'United Party'.upper()}
df['party_detailed'] = df['party_code'].replace(party_map).fillna("")
def get_party_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','LIBERTARIAN','NONPARTISAN','']:
        return x
    else: return "OTHER"
df['party_simplified'] = df['party_detailed'].apply(get_party_simplified)


# In[55]:


df = df.drop(columns = ['cand_last','cand_first','cand_middle','cand_suffix','office_code',
                       'cong_district','senate_district','house_district','precinct_code','vtd_code',
                       'party_code'])


# In[56]:


# other fields
df['magnitude'] = 1
df['date'] = '2020-11-03'
state_codes=pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/merge_on_statecodes.csv')
state_codes['state'] = state_codes['state'].str.upper()
df = df.merge(state_codes, on = 'state', how = 'left')
df['readme_check'] = 'FALSE'
df['special'] = 'FALSE'
df['mode'] = 'TOTAL'




df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()


# some instances of near duplicate writein scattered rows in raw data. need to agg these votes within precinct and replace to prevent dups
multi_writein_precinct_agg = df[df.drop(columns = 'votes').duplicated(keep = False)].groupby(list(df.drop(columns = 'votes').columns)).agg(sum).reset_index()
# drop near duplicates
df = df[~(df.drop(columns = 'votes').duplicated(keep = False))].copy()
df = pd.concat([df,multi_writein_precinct_agg])

df.to_csv('2020-pa-precinct-general.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)