#!/usr/bin/env python
# coding: utf-8

# In[167]:


import pandas as pd
import os
import numpy as np
import re
import warnings
import csv
#warnings.simplefilter(action='ignore', category=FutureWarning)
#pd.options.mode.chained_assignment = None  # default='warn'


# In[168]:


official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,#'votes':int, 
                   'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 
'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 
                   'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}


# In[ ]:





# In[169]:


df = pd.read_csv('../20181106__ut__general__precinct.csv',index_col=False, dtype = official_dtypes)
df = df.fillna('')
df = df.replace('""',"")

#add missing precinct votes for cand
df.loc[-1] = ['Summit','Park West','STATE SENATE','026','CATHY CALLOW-HEISER','UNITED UTAH',23]
# In[170]:

### add missing box elder precinct
def get_missing_precinct():
    box = pd.read_csv('ut-QA/0pen-elections-source/Box Elder UT 2018 General Precinct Results.csv')
    box=box.loc[8075:8121,].copy()
    box.columns = ['candidate','votes1','votes2','drop']
    box['precinct'] = 'WILLARD'
    box = box.drop(columns = 'drop').fillna('')
    box['votes'] = box['votes1'] + box['votes2']
    box = box[~(box['votes']=='')].copy().drop(columns=['votes1','votes2'])

    # breaks at TOTAL,STRAIGHT PARTY, US SENATE, US HOUSE, STATE SENATE, STATE HOUSE
    # assign offices
    box['office'] = (box['votes'] =='TOTAL')
    offices = ['TOTAL','STRAIGHT PARTY', 'US SENATE', 'US HOUSE', 'STATE SENATE', 'STATE HOUSE']
    for index, office in zip(box.index[box['office']].tolist(), offices):
        box.loc[index,'office'] = office
    box['office'] = box['office'].replace(False,np.nan).ffill()
    box = box[~(box['votes'].str.contains('TOTAL|OFFICIAL RESULTS|Box Elder|%'))].copy()
    box['office'] = np.where(box['office'] == 'TOTAL', box['candidate'].str.upper(), box['office'])
    box['votes'] = box['votes'].str.replace(',','').astype(int)

    box['candidate'] = box['candidate'].replace({'Write-In Totals':'WRITEIN',
                                                'Registered Voters - Total':'',
                                                'Ballots Cast - Total':'',
                                                'Ballots Cast - Blank':''}).str.upper()
    # isolate party code
    box['party'] = np.where(box['office'].isin(['US SENATE', 'US HOUSE', 'STATE SENATE', 'STATE HOUSE']),
                                    box['candidate'].str.split(' '),'')
    box['party']= [i[0] if len(i)>0 else '' for i in box['party']]
    parties = dict(zip(list(box['party'].unique()),['','CONSTITUTION', 'LIBERTARIAN', 'INDEPENDENT AMERICAN', 'DEMOCRAT',
           'REPUBLICAN', '', 'UNITED UTAH', 'GREEN']))
    box['party'] = box['party'].replace(parties)
    # isolate candidate
    box['candidate'] = np.where(box['office'].isin(['US SENATE', 'US HOUSE', 'STATE SENATE', 'STATE HOUSE']),
                                    box['candidate'].str.split(' '),'')
    box['candidate']= [' '.join(i[1:]) if len(i)>1 else 'WRITEIN' if len(i)==1 else '' for i in box['candidate']]
    box['candidate'] = box['candidate'].str.replace('\.','',regex=True)
    #district
    def get_dist(x):
        if x =='US SENATE': return 'STATEWIDE'
        if x == "US HOUSE": return '001'
        if x == 'STATE SENATE': return '017'
        if x =='STATE HOUSE': return '029'
        else: return ''
    box['district'] = box['office'].apply(get_dist)

    box['county'] = 'BOX ELDER'
    box['office'] = box['office'].replace({'BALLOTS CAST - TOTAL': 'BALLOTS CAST',
        'REGISTERED VOTERS - TOTAL':'REGISTERED VOTERS'})
    return box
df = pd.concat([df, get_missing_precinct()])






# In[171]:


#there is a missing district value for a US house office
df[(df.office.str.contains('House'))&(df['district']=='')]
df.loc[(df.office.str.contains('House'))&(df['district']==''),'district'] = '001'


# In[172]:


def fix_office(x):
    if 'Senate' in x and 'State' not in x: return 'US SENATE'
    elif 'House' in x and 'State' not in x: return 'US HOUSE'
    elif 'State House' in x: return 'STATE HOUSE'
    else: return x.upper() 

df['office'] = df['office'].apply(fix_office)
df.office.unique()


# In[173]:


df['district'] = df['district'].apply(lambda x: x.zfill(3) if len(x)>0 else '')
df.loc[df.office=='US SENATE','district'] = 'STATEWIDE'
df.loc[df.office=='US PRESIDENT','district'] = 'STATEWIDE'
df.district.unique()


# In[175]:


df[df.district==""].office.unique()


# In[176]:


def get_writein(x):
    return str('(W)' in x).upper()

def fix_cand(x):
    x=x.replace("''",'"').replace(',','').upper()
    x = x.replace(' (W)','')
    if "'" in x and x[x.find("'")-1] == ' ': #i.e. if it is not like O'Brien, which we would want to keep as a single quote
        x=x.replace("'",'"')
    if x == 'AGAINST': return 'NO'
    if x == 'FOR': return 'YES'
    if 'BLANK' in x: return 'UNDERVOTES'
    if 'WRITE' in x and 'IN' in x: return 'WRITEIN'
    if '.' in x:
        if x[-1] != '.' and x[x.find('.')+1] != ' ': return x.replace('.',' ')
        else: return x.replace('.','')
    return x

def get_dataverse(x):
    if x in ['STATE SENATE','STATE HOUSE']: return 'STATE'
    elif x == 'US SENATE': return 'SENATE'
    elif x == 'US HOUSE': return 'HOUSE'
    else: return ''

df['writein'] = df['candidate'].apply(get_writein)
df['candidate'] = df.candidate.apply(fix_cand)
df['candidate'] = df['candidate'].apply(lambda x: re.sub("[()]",'"', x))
df['dataverse'] = df['office'].apply(get_dataverse)

#df.candidate.unique()


# In[177]:


df.loc[df.office=='STRAIGHT PARTY','office'] = 'STRAIGHT TICKET'
df.loc[df.office=='STRAIGHT TICKET','candidate'] = 'STRAIGHT TICKET'


# In[178]:


df['party_detailed'] = df['party'].str.upper().replace({'CON':'CONSTITUTION','LBT':'LIBERTARIAN','DEM':'DEMOCRAT',
                                                        'LIB':'LIBERTARIAN', 'IAP':'INDEPENDENT AMERICAN',
                                                        'REP':'REPUBLICAN', 'CON':'CONSTITUTION', 'GRN':'GREEN',
                                                        'UUP':'UNITED UTAH','UNITED UTAH PARTY':'UNITED UTAH',
                                                        'GREEN PARTY':'GREEN','LBT':'LIBERTARIAN','WRITE-IN':'',
                                                        'UNA':'INDEPENDENT','NONE':'INDEPENDENT'})

df.party_detailed.unique()


# In[179]:


df['party_simplified'] = df['party_detailed'].replace({'INDEPENDENT AMERICAN':'OTHER', 'CONSTITUTION':'OTHER',
                                                       'UNITED UTAH':'OTHER','GREEN':'OTHER','INDEPENDENT':'OTHER'})
df.party_simplified.unique()


# In[180]:


#MERGING COUNTY_FIPS
df['state'] = 'Utah'
df['county_name'] = df['county'].str.upper()
countyFips = pd.read_csv("../../../help-files/county-fips-codes.csv")
df = pd.merge(df, countyFips, on = ['state','county_name'], how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
df['jurisdiction_name'] = df['county_name']
#now can change 'state' column  back to NC
df['state'] = df['state'].str.upper()


# In[181]:


df.jurisdiction_fips.unique()


# In[182]:


df['readme_check'] = 'FALSE'
df['date'] = '2018-11-06'
df['year'] = '2018'
df['state_fips'] = '49'
df['state_po'] = 'UT'
df['state_ic'] = '87'
df['state_cen'] = '67'
df['special'] = 'FALSE'
df['stage'] = 'GEN'
df['mode'] = 'TOTAL'


# In[183]:


def get_magnitude(x):
    if x in ['BALLOTS CAST','REGISTERED VOTERS','STRAIGHT TICKET']: return 0
    else: return 1

df['magnitude'] = df['office'].apply(get_magnitude)


# In[184]:


#similar values in candidate
cands = '''MIA LOVE ||| [[MIA B LOVE]] #2nd
    LEE PERRY ||| [[LEE B PERRY]] #2nd 
    BRIAN KING ||| [[BRIAN S KING]]
    SCOTT CHEW ||| [[SCOTT H CHEW]]
    JASON ALLEN ||| [[JASON M ALLEN]]
    KELLY MILES ||| [[KELLY B MILES]]
    KERRY WAYNE ||| [[KERRY M WAYNE]]
    KEVIN BRYAN ||| [[KEVIN L BRYAN]]
    CRAIG BOWDEN ||| [[CRAIG R BOWDEN]]
    KIRK PEARSON ||| [[KIRK D PEARSON]]
    MICHAEL KEIL ||| [[MICHAEL A KEIL]]
    CARL ALBRECHT ||| [[CARL R ALBRECHT]]
    MARSHA HOLLAND ||| [[MARSHA M HOLLAND]]
    JEFFERY WHIPPLE ||| [[JEFFREY WHIPPLE]]
    REED MCCANDLESS ||| [[REED C MCCANDLESS]]
    CHRISTINE WATKINS ||| [[CHRISTINE F WATKINS]]
    JONATHAN PETERSON ||| [[JONATHAN L PETERSON]]
    CATHY CALLOW-HEISER ||| [[CATHY CALLOW-HEUSER]]
    CATHY CALLOW-HEUSER ||| [[CATHY CALLOW-HEUSSER]]'''


# In[ ]:





# In[189]:


cands = cands.split('\n')
cands = [c.replace(']]','').strip().split(' ||| [[') for c in cands]
cands


# In[190]:


# #check if they're in the same county
# for pair in cands:
#     cand1 = pair[0]
#     cand2 = pair[1]
#     a = df[df.candidate == cand1]
#     b = df[df.candidate == cand2]
#     #if np.any(a.county_name.unique() == b.county_name.unique()): 
#     print(cand1, '--->', a.county_name.unique(), a.office.unique(),a.district.unique(), a.writein.unique())
#     print(cand2, '--->', b.county_name.unique(), b.office.unique(),b.district.unique(),b.writein.unique(),'\n')


# # In[192]:


df.loc[df.candidate=='JEFFERY WHIPPLE','candidate'] = 'JEFFREY WHIPPLE'
df.loc[df.candidate.str.contains('CATH CALLOW-'),'candidate'] = 'CATHY CALLOW-HEUSSER'

for cand in cands:
    if len(cand[0].split()) == 2 and len(cand[1].split()) ==3:
        df.loc[df.candidate==cand[0],'candidate'] = cand[1]


# In[194]:


#mistake where 'KERRY M WAYNE' is in 009 but should be 029
df.loc[df.candidate=='KERRY M WAYNE','district'] = '029'



##### DC #####
df['votes'] = df['votes'].replace('*', -1).astype(int)

df.loc[df.candidate=='MARSHA M HOLLAND','party_detailed'] = 'INDEPENDENT'
df.loc[df.candidate=='MARSHA M HOLLAND','party_simplified'] = 'OTHER'
# verified all multi-writein column candidates are supposed to be writein
true_writeins = ['ABE KORB',
'CALEB DAN REEVE',
'CODY JUDY',
'GLADE G FITZGERALD',
'HEKTOR REIKSTHEGN',
'RYAN DANIEL JACKSON',
'TYRONE JENSEN']
df.loc[df['candidate'].isin(true_writeins), 'writein'] = 'TRUE'
# then drop writeins with 0 votes to reduce file size
df = df[~((df['writein']=='TRUE')&(df['votes']==0))].copy()
# drop aggregate precincts
df = df[~(df['precinct'].str.contains('TOTAL| UT'))].copy()

df['precinct'] = df['precinct'].str.upper().str.strip()


## vote fixes
#duchesne
df.loc[(df['county_name']=='DUCHESNE')&(df['precinct']=='RO12')&(df['candidate']=='MITT ROMNEY'),
'votes'] = 104

# emery
df.loc[(df['county_name']=='EMERY')&(df['precinct']=='orangeville 5'.upper())&(df['candidate']=='MITT ROMNEY'),
'votes'] = 461
# juab
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.4')&(df['candidate']=='MIA B LOVE'),
'votes'] = 261
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.4')&(df['candidate']=='BEN MCADAMS'),
'votes'] = 56
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.5')&(df['candidate']=='MITT ROMNEY'),
'votes'] = 123
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.5')&(df['candidate']=='JENNY WILSON'),
'votes'] = 9
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.5')&(df['candidate']=='REED C MCCANDLESS'),
'votes'] = 1
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.5')&(df['candidate']=='CRAIG R BOWDEN'),
'votes'] = 0
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.5')&(df['candidate']=='TIM AALDERS'),
'votes'] = 1
df.loc[(df['county_name']=='JUAB')&(df['precinct']=='NE02.5')&(df['candidate']=='GLADE G FITZGERALD'),
'votes'] = 0

# Kane
df.loc[(df['county_name']=='KANE')&(df['candidate']=='MARSHA M HOLLAND'),
'office'] = 'STATE HOUSE'

# summit
    # South Summit East, Christopher neville 163
    # Peoa 15:32, logan wilde 101
    # DEER VALLEY NORTH, TIM QUINN 64
    # add PARK WEST, CATHY CALLOW-HEISER 23
    # HOYTSVILLE, ADAM DAVIS 6
    # SILVER SPRINGS, ADAM DAVIS 7
df.loc[(df['county_name']=='SUMMIT')&(df['precinct']=='South Summit East'.upper())&(df['candidate']=='Christopher neville'.upper()),
'votes'] = 163
df.loc[(df['county_name']=='SUMMIT')&(df['precinct']=='Peoa 15:32'.upper())&(df['candidate']=='Logan Wilde'.upper()),
'votes'] = 101
df.loc[(df['county_name']=='SUMMIT')&(df['precinct']=='DEER VALLEY NORTH')&(df['candidate']=='TIM QUINN'),
'votes'] = 64
df.loc[(df['county_name']=='SUMMIT')&(df['precinct']=='HOYTSVILLE')&(df['candidate']=='ADAM DAVIS'),
'votes'] = 6
df.loc[(df['county_name']=='SUMMIT')&(df['precinct']=='SILVER SPRINGS')&(df['candidate']=='ADAM DAVIS'),
'votes'] = 7

#iron 
df.loc[(df['county_name']=='IRON')&(df['precinct']=='CC07')&(df['candidate']=='Rex Shipp'.upper()),
'votes'] = 168
df.loc[(df['county_name']=='IRON')&(df['precinct']=='CC25')&(df['candidate']=='JEFFREY WHIPPLE'),
'votes'] = 54

#cache
df.loc[(df['county_name']=='CACHE')&(df['precinct']=='LOG01-1')&(df['candidate']=='DAN JOHNSON'),
'votes'] = 124

# beaver
df.loc[(df['county_name']=='BEAVER')&(df['precinct']=='BEAVER 3')&(df['candidate']=='PHIL LYMAN'),
'votes'] = 235

# weber totals off because of masked votes in small 


df = df[~((df['office']=='STRAIGHT TICKET')&(df['precinct']=='WILLARD')&(df['county_name']=='BOX ELDER'))].copy()

# readme check remaining scraping errors. All very small <5 votes, or accounted for (weber/salt lake)
non = pd.read_csv('ut-QA/utah_misses.csv')
non_match=non[(~(non['county'].isin(['WEBER'])))&(non['whose']=='ours')]
non_match = non_match[['county','cand','office']].drop_duplicates()
non_match.columns = ['county_name','candidate','office']
non_match['readme'] = 'TRUE'
df = df.merge(non_match, how = 'left', on = ['county_name','candidate','office'])
df['readme_check'] = np.where(df['readme']=='TRUE', 'TRUE', 'FALSE')
df = df.drop(columns = 'readme')
#also readme check masked votes
df['readme_check'] = np.where(df['votes']==-1,'TRUE',df['readme_check'])



df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()


# In[187]:


df = df.replace('  ', ' ', regex = True) 
df = df.fillna("")
df = df.applymap(lambda x: x.strip() if type(x) == str else x)


# In[188]:


df.to_csv("2018-ut-precinct-general-updated.csv", encoding='utf-8',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[109]:


#get_ipython().system('jupyter nbconvert --to script ut_2021_updates.ipynb')


# In[ ]:




