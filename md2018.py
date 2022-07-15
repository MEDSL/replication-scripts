#!/usr/bin/env python
# coding: utf-8

# 1. Add columns {'readme_check', 'jurisdiction_fips', 'county_fips', 'date', 'magnitude'}.
# 2. Remove periods and commas from candidate names. Make sure double initial names remain separated (e.g. C.A. DUTCH RUPPERSBERGER to C A DUTCH RUPPERSBERGER).
# 3. Replace [WRITE-IN] with WRITEIN in the candidate column.
# 4. A few retention-like candidates appear without - YES or - NO (e.g. MATTHEW J. FADER and MATTHEW J. FADER - YES). Investigate whether this is intended, and if not, fix the necessary candidate names.
# 5. Unify JUDGE OF THE CIRCUIT COURT and JUDGE COURT OF APPEALS (and similar) in the office column
# 6. Move AT LARGE from the office column to the district column where appropriate
# 7. Unify the format of county commissioner and council office names.
# 8. Zero-pad numerical districts so they have length three.
# 9. Make sure writein candidates have empty party information where appropriate.
# 10. Remove rows with named writein candidates wherever they appear as having received 0 votes

# In[210]:


import pandas as pd
import numpy as np
import os
import re
import csv


# In[211]:


official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 
                   'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 
'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 
                   'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}


# In[212]:


df = pd.read_csv('2018-md-precinct-autoadapted.csv',index_col=False, dtype = official_dtypes)
df = df.fillna('')
df = df.replace('""',"")


# In[213]:


#error in raw data 
df[df.district=='CU'].office.unique()


# In[214]:


#MERGING COUNTY_FIPS
df['state'] = 'Maryland'
countyFips = pd.read_csv("../../../help-files/county-fips-codes.csv")
df = pd.merge(df, countyFips, on = ['state','county_name'], how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
df['county_name'] = df['jurisdiction_name']
df['state'] = df['state'].str.upper()


# In[215]:


df['readme_check'] = 'FALSE'
df['date'] = '2018-11-06' 


# In[216]:

# 2. Remove periods and commas from candidate names. Make sure double initial names remain separated (e.g. C.A. DUTCH RUPPERSBERGER to C A DUTCH RUPPERSBERGER).
# 

# In[217]:


def fix_cand(x):
    x=x.replace("''",'"')
    x=x.replace(',','').replace('Ã','A')
    if "'" in x and x[x.find("'")-1] == ' ': #i.e. if it is not like O'Brien, which we would want to keep as a single quote
        x=x.replace("'",'"')
    if x == 'AGAINST': return 'NO'
    if x == 'FOR': return 'YES'
    if 'BLANK' in x: return 'UNDERVOTES'
    if 'WRITE-IN' in x: return 'WRITEIN'
    if '.' in x:
        if x[-1] != '.' and x[x.find('.')+1] != ' ': return x.replace('.',' ')
        else: return x.replace('.','')
    return x
df['candidate'] = df.candidate.apply(fix_cand)
df['candidate'] = df['candidate'].apply(lambda x: re.sub("[()]",'"', x))


# In[218]:


#declan's function
cand_wo_middle = [i for i in df['candidate'].unique() if len(i.split(' ')) <= 2]
cand_w_middle =[i for i in df['candidate'].unique() if len(i.split(' ')) > 2]
for cand in cand_w_middle:
    first = cand.split(' ')[0]
    last = cand.split(' ')[-1]
    full = ' '.join([first,last])
    if full in cand_wo_middle:
        print(cand)


# In[193]:


sorted(df.candidate.unique())


# 5. Unify JUDGE OF THE CIRCUIT COURT and JUDGE COURT OF APPEALS (and similar) in the office column
# 6. Move AT LARGE from the office column to the district column where appropriate
# 7. Unify the format of county commissioner and council office names.
# 

# In[194]:


df.office.unique()


# In[195]:


def add_dist(off, dist):
    if 'AT LARGE' in off: return 'AT-LARGE'
    else: return dist

l = list
def fix_office(x):
    x = x.replace(' AT LARGE','')
    if 'GOVERNOR' in x: return 'GOVERNOR'
    elif 'JUDGE' in x: 
        x=x.replace('OF THE ','')
        return 'JUDGE - '+ ' '.join(x.split()[1:])
    #print(x)
    if 'COUNCIL' in x: 
        if 'CITY' in x: return x
        elif 'PRES' in x: return 'COUNTY COUNCIL PRESIDENT'
        else: return 'COUNTY COUNCIL'
        #print(x)
        #if x not in l:
        #    print(x)
        #    l.append(x)
    
    elif x == 'PRES COUNTY COMMISSION': return 'COUNTY COMMISSION PRESIDENT'
    elif 'COMMISSION' in x: return 'COUNTY COMMISSIONER'
    elif 'ATTORNEY' in x: return 'STATE ATTORNEY'
    elif 'TREASURER' in x: return 'COUNTY TREASURER'
    return x

df['district'] = df.apply(lambda x: add_dist(x['office'],x['district']),axis=1)
df['office'] = df['office'].apply(fix_office)


# In[196]:


df['district'] = df['district'].apply(lambda x: x.zfill(3) if x.isnumeric() else x)
df.district.unique()


# In[197]:


df.loc[df.district=='CU','district'] = ""


# In[198]:


sorted(df.office.unique())


# 9. Make sure writein candidates have empty party information where appropriate.
# 10. Remove rows with named writein candidates wherever they appear as having received 0 votes

# In[199]:


df.loc[df.writein=='TRUE','party_detailed'] = "" 
df.loc[df.party_detailed=='OTHER/NONPARTISAN','party_detailed'] = "NONPARTISAN"
df.loc[df.party_detailed=='NONPARTISAN','party_simplified'] = "NONPARTISAN"
df.loc[df.writein=='TRUE','party_simplified'] = "" 


# In[200]:


indices = df[(df.writein=='TRUE')&(df.votes==0)].index
print(len(df))
df.drop(indices,inplace=True)
print(len(df))


# In[201]:


cands = [('JOSEPH M GETTY','JOSEPH M GETTY - YES'),('MATTHEW J FADER','MATTHEW J FADER - YES'),
         ('DONALD E BEACHLEY','DONALD E BEACHLEY - YES'), ('MELANIE SHAW GETER','MELANIE SHAW GETER - YES'),
         ('JOSEPH M GETTY', 'JOSEPH M GETTY - YES')]
'''
for c1, c2 in cands:
    a = df[df.candidate==c1]
    b = df[df.candidate==c2]
    print(a.district.unique(), b.district.unique())
    print('\n')
'''

for c1, c2 in cands:
    df.loc[df.candidate==c1,'candidate'] = c2 #should all be retention


# In[202]:


df[df.candidate=='JOSEPH M GETTY']


# In[203]:


#fix modes in precinct column
modes = ['ABSENTEE','EARLY VOTING','PROVISIONAL',"2ND ABSENTEE"]
for mode in modes:
    df.loc[df.precinct==mode,'mode'] = mode
    df.loc[df.precinct==mode,'precinct'] = 'COUNTY FLOATING'

df[df.precinct=='PROVISIONAL'].votes.unique()


# In[205]:


df['mode'].unique()


# In[206]:


#fix dataverse
state_offices = ['STATE ATTORNEY', 'JUDGE - CIRCUIT COURT','CLERK CIRCUIT COURT']
for office in state_offices:
    df.loc[df.office==office,'dataverse'] = 'STATE'

#### DC Fixes #################
# typo
def district_padding(x):
    if x == '':
        return x
    if (x[-1].isalpha()) and (len(x)>1) and (x not in ['AT-LARGE','STATEWIDE']):
        return re.split(r"[A-Z]",x)[0].zfill(3) + x[-1]
    else: 
        return x
df['district'] = df['district'].apply(district_padding)

# creating magnitude field
def get_magnitude_from_raw(dataframe):
    #utilizes winner column to get magnitude (if more than one cand wins for a particular office magnitude is greater than one)
    counties=[i for i in os.listdir('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/MD/raw/county') if '.csv' in i]
    mag_lst = []
    for county in counties:
        c = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/MD/raw/county/' + county)
        c['Winner'] = c['Winner'].replace('Y',1).fillna(0)
        c['Office District'] = c['Office District'].fillna("").astype(str).str.replace('\.0',"",regex=True).str.zfill(3).replace('000','',regex=False)
        c = c.rename(columns = {'Winner':'magnitude','Office District':'district','Office Name':'office'})
        c['office'] = c['office'].str.upper().str.strip()
        c['county_name'] = county.replace('.csv','').replace('_'," ").upper()
        mag=c.groupby(['county_name','office','district']).agg(sum)[['magnitude']]
        mag = mag[mag['magnitude']>1]
        mag_lst = mag_lst + [mag]
    magnitude=pd.concat(mag_lst).reset_index()
    ##### manipulations to get offices/districts to match for merging with df ####
    magnitude['district'] = np.where((magnitude['office'].str.contains('AT LARGE')), 'AT-LARGE',magnitude['district'])
    # judge special appeals has two winners but they are unique races
    magnitude = magnitude[~(magnitude['office']==('JUDGE SPECIAL APPEALS AT LARGE'))]
    # apply office and district fixes 
    magnitude.office = magnitude.office.apply(fix_office).replace('HOUSE OF DELEGATES','STATE HOUSE')
    magnitude.district = magnitude.district.apply(district_padding).replace('000U','')
    #match county name punctuation
    magnitude['county_name'] = magnitude['county_name'].replace(['ST. MARYS', 'QUEEN ANNES', 'PRINCE GEORGES'],
                                                ["ST. MARY'S", "QUEEN ANNE'S", "PRINCE GEORGE'S"])
    # merge on identifying fields
    dataframe = dataframe.merge(magnitude, on = ['county_name','office','district'], how='left')
    # remaining offices are mag = 1, convert to int
    dataframe['magnitude'] = dataframe['magnitude'].fillna(1).astype(int)
    return dataframe
print(len(df))
df=get_magnitude_from_raw(df)
print(len(df))

df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()


# In[208]:


df = df.replace('  ', ' ', regex = True) 
df = df.fillna("")
df = df.applymap(lambda x: x.strip() if type(x) == str else x)


# In[209]:


df.to_csv("2018-md-precinct-general-updated.csv", encoding='utf-8',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[ ]:




