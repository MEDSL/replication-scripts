#!/usr/bin/env python
# coding: utf-8

# unknown:  "district"
#         
#         
# known: ~"office"~, ~"party_detailed"~, ~"party_simplified"~, ~"mode"~, ~"votes"~, 
#     ~"dataverse"~, ~"year"~, ~"stage"~, ~"state"~, ~"special"~, ~"writein"~, ~"state_po"~,
#     ~"state_fips"~, ~"state_cen"~, ~"state_ic"~, ~"date"~, ~"readme_check"~, ~"magnitude"~, ~"precinct"~,   ~"county_name"~, ~"county_fips"~, ~"jurisdiction_name"~, 
#         ~"jurisdiction_fips"~, ~"candidate"~

# In[1]:


## Format of column 
#CraddickR__18G__State Rep 82 --> "[last name][party_info]-[2018General (stage)]-[office]"


# In[18]:


import glob
import pandas as pd
import csv
import os
import swifter

# df = pd.concat(map(pd.read_csv, glob.glob('raw_TLC/*.csv')))


# # In[3]:


# pd.set_option('display.max_columns', None)


# # In[4]:


# df = df.reset_index(drop=True)


# # In[5]:


# df['CNTYVTD'] = df['CNTYVTD'].astype(str)


# # In[6]:


# def cleanCNTYVTD(x):
#     if (x[0:2] == '00'):
#         return x[2:]
#     elif (x[0] == '0'):
#         return x[1:]
#     else: 
#         return x

# df['CNTYVTD'] = df['CNTYVTD'].swifter.apply(cleanCNTYVTD)


# # In[7]:


# cnt = pd.read_csv('vtds20g_pop.txt')  
# cnt = cnt.filter(['VTD', 'CNTYVTD', 'FENAME'])



# df=df.applymap(lambda x: x.strip() if type(x)==str else x)
# df = pd.merge(df, cnt, on = ['CNTYVTD'], 
#              how = 'left')


# # In[8]:


# df = pd.melt(df, id_vars=['CNTYVTD', 'VTD', 'VTDKEY', 'FENAME'],
#         var_name='temp', value_name='votes')


# # In[9]:


# df['CNTYVTD'] = df['CNTYVTD'].astype(str)
# df['VTDKEY'] = df['VTDKEY'].astype(str)


# In[10]:
#### DC added 12/15/21 to avoid creating massive file

os.chdir('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/TX/raw_TLC')
files = [i for i in os.listdir() if i not in  [".DS_Store",'._state rep 15.csv']]
df_list = []
for file in files:
    df = pd.read_csv(file,dtype = {'CNTYVTD': str, 'VTDKEY':str})
    df = pd.melt(df, id_vars = ['CNTYVTD','VTDKEY'], value_vars = df.columns[2:],
                value_name = 'votes', var_name = 'temp')
    df_list = df_list + [df]
df = pd.concat(df_list)

# we want to alter the cnt file to match the official precinct data, not the other way around
# we don't want to change the precinct field itself other than adding fields together with a separator.
cnt = pd.read_csv('../2021adapt/vtds20g_pop.txt', dtype = {'CNTYVTD': str,'FENAME':str, 'FIPS':str}) 
cnt['CNTYVTD'] = cnt['FIPS'].str.zfill(3) + cnt['VTD']
cnt = cnt.filter(['CNTYVTD', 'FENAME'])

df = df.merge(cnt, on = 'CNTYVTD', how='left').rename(columns = {"FENAME": 'county_name'})
print('Number of bad merges: ',len(df[df['county_name'].isnull()]))

df['precinct'] = df['CNTYVTD'] + '_' + df['VTDKEY']


# In[13]:


df = df.drop(columns=['CNTYVTD'])


# In[15]:


df = df.drop(columns=['VTDKEY'])


# In[16]:


# df = df.drop(columns=['VTD'])


# In[17]:


# df = df.drop_duplicates()


# In[18]:


# work above done, pushed as csv to save time
# df.to_csv('texastemp.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[6]:


# temp = pd.read_csv('texastemp.csv')  
# df = temp


# In[8]:


# #df['FENAME'] = df['FENAME'].fillna('~~~~~~')
# df = df.rename(columns={"FENAME": "county_name"})


# # In[27]:


# df = df.dropna()


# # In[28]:


# df


# In[29]:


def extractOffice(x):
    if '_' in x:
        index = x.rindex('_')
        return x[index+1:]
    else:
        return x

df['office'] = df['temp'].swifter.apply(extractOffice)


# In[30]:


def extractParty(x):
    if '_' in x:
        index = x.index('_')
        x = x[:index]
        return x[-1]
    else:
        return x

df['party_detailed'] = df['temp'].swifter.apply(extractParty)


# In[31]:


def extractCand(x):
    if '_' in x:
        index = x.index('_')
        if x[:index][-1] == 'R' or x[:index][-1] == 'D' or x[:index][-1] == 'L' or x[:index][-1] == 'W' or x[:index][-1] == 'I':
            return x[:index-1]
        else:
            if x == 'Voter_Registration':
                return 'VOTER REGISTRATION'
            if 'Spanish_Surname_Voter_Registration' in x:
                return 'SPANISH SURNAME VOTER REGISTRATION'
            if 'Spanish_Surname_Turnout' in x:
                return 'SPANISH SURNAME TURNOUT'
    else:
        if 'Turnout' == x:
            return 'TURNOUT'

df['candidate'] = df['temp'].swifter.apply(extractCand)


# In[32]:


df['party_detailed'] = df['party_detailed'].replace({'R': 'REPUBLICAN', 
                                                    'D': 'DEMOCRAT',
                                                    'L': 'LIBERTARIAN',
                                                    'W': 'WRITEIN',
                                                    'I': 'INDEPENDENT',
                                                    'r': '',
                                                    'Turnout': '',
                                                    'h': ''})


# In[33]:


df["date"] = "2018-11-06"
df["readme_check"] = "FALSE"
df["magnitude"] = 1
df['stage'] = "GEN"
df['year'] = "2018"
df['state'] = "TEXAS"
df['mode'] = 'TOTAL'
df['special'] = 'FALSE'
df['writein'] = 'FALSE'
df.loc[df['candidate'] == 'Write-In', 'writein'] = 'TRUE'
df.loc[df['party_detailed'] == 'WRITEIN', 'writein'] = 'TRUE'


# In[34]:


df['party_detailed'] = df['party_detailed'].replace({'WRITEIN': ''})


# In[35]:


df['state_po'] = "TX"
df['state_fips'] = "48"
df['state_cen'] = "74"
df['state_ic'] = "49"


# In[36]:


# After county name fix, append on fips codes
fips = pd.read_csv('../../../help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()
df['county_name'] = df['county_name'].replace({'DE WITT': 'DEWITT'})
df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


# In[37]:


df['jurisdiction_fips'] = df['county_fips']
df['jurisdiction_name'] = df['county_name']


# In[38]:


df['party_simplified'] = df['party_detailed']


# In[39]:


df['party_simplified'] = df['party_simplified'].replace({'INDEPENDENT': 'OTHER'})


# In[22]:


#df['votes'] = df['votes'].fillna(0)


# In[40]:


df['votes'] = df['votes'].astype(float)
df['votes'] = df['votes'].astype(int)


# In[41]:


def getDataverse(x):
    if 'State Rep' in x or 'State Sen' in x:
        return 'STATE'
    if 'U.S. Rep' in x:
        return 'HOUSE'
    if 'U.S. Sen' in x:
        return 'SENATE'
    if 'District Judge' in x:
        return 'STATE'
    if x == 'Turnout' or x == 'Registration':
        return ''
    else:
        return 'LOCAL'

df['dataverse'] = df['office'].apply(getDataverse)


# In[42]:


def getDistrict(x):
    if 'State Sen' in x or 'State Rep' in x or 'U.S. Rep' in x:
        index = x.rindex(' ')
        return x[index+1:]
    if 'District Judge' in x:
        index = x.index(' ')
        return x[:index-2]
    if 'CCA' in x and len(x)<6:
        return x[-1]
    if 'COA 13 Chief' in x:
        return '013'
    if 'COA 5 Chief' in x:
        return '005'
    if 'COA' in x and 'Chief' not in x:
        i = x.index('P')
        dis = x[4:i].zfill(4)
        return dis[:-1] + ', PLACE ' + x[-2:]
    if x.split(' ')[-1].isnumeric():
    	return x.split(' ')[-1].zfill(3)
    else:
        return ''

df['district'] = df['office'].apply(getDistrict)


# In[43]:


def cleanDistrict(x):
    return x.zfill(3)

df.district = df.district.str.replace(' +', ' ')
df['district'] = df['district'].apply(cleanDistrict)


# In[44]:


def cleanOffice(x):
    if 'District Judge' in x:
        return 'DISTRICT COURT JUDGE'
    if 'CCA' in x:
        if 'Pres Judge' in x:
            return 'CRIMINAL COURT OF APPEALS - PRESIDING JUDGE'
        else:
            return 'CRIMINAL COURT OF APPEALS'
    if 'COA' in x:
        return 'COURT OF APPEALS'
    if 'State Rep' in x:
        return 'STATE HOUSE'
    if 'State Sen' in x:
        return 'STATE SENATE'
    if 'U.S. Rep' in x:
        return 'US HOUSE'
    if 'U.S. Sen' in x:
        return 'US SENATE'
    else:
        return x.upper()
    
df['office'] = df.office.apply(cleanOffice)


# In[45]:


df = df.drop(columns=['temp'])


# In[46]:


df.candidate = df.candidate.str.upper()
df.office = df.office.str.upper()


# In[47]:


df['candidate'] = df['candidate'].replace({'WRITE-IN': 'WRITEIN'})
df['district'] = df['district'].replace({'000': ''})


# In[48]:

## FINAL FIXES ##\
# STATE BOES (SBOE #)

df.loc[df['office'].str.contains('SBOE'), 'office'] = 'STATE BOARD OF EDUCATION'
df.loc[df['office'].str.contains('SUP CT'), 'office'] = 'SUPREME COURT'

df['office'] = df['office'].replace({'ATTORNEY GEN':'ATTORNEY GENERAL',
	'AG COMM':'AGRICULTURE COMMISSIONER','LAND COMM':"PUBLIC LANDS COMMISSIONER",
	'LT. GOVERNOR':'Lieutenant governor'.upper(),'RR COMM 1':'RAILROAD COMMISSIONER'})

df.loc[df['office'].isin(['CRIMINAL COURT OF APPEALS','CRIMINAL COURT OF APPEALS - PRESIDING JUDGE',
	'COURT OF APPEALS','GOVERNOR','ATTORNEY GENERAL','AGRICULTURE COMMISSIONER',
	'Lieutenant governor'.upper(), "PUBLIC LANDS COMMISSIONER",
	'SUPREME COURT','STATE BOARD OF EDUCATION','RAILROAD COMMISSIONER','COMPTROLLER']),'dataverse'] = 'STATE'

df.loc[df['office'].isin(['CRIMINAL COURT OF APPEALS - PRESIDING JUDGE',
	'GOVERNOR','ATTORNEY GENERAL','AGRICULTURE COMMISSIONER',
	'Lieutenant governor'.upper(), "PUBLIC LANDS COMMISSIONER",
	'RAILROAD COMMISSIONER','COMPTROLLER','US SENATE']),'district'] = 'STATEWIDE'
# In[51]:


# Final step: Remove all trailing white space and put columns in correct order. 
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]]

#df = df.replace([True,False], ['TRUE','FALSE'])

df.to_csv('../2021adapt/2018-tx-precinct-general-updated.csv',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[ ]:




