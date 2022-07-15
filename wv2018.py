#!/usr/bin/env python
# coding: utf-8

# 1. Add columns {'readme_check', 'jurisdiction_fips', 'date', 'county_fips', 'magnitude'}.
# 2. Remove periods from candidate names. Be careful with double initial names such as D.C. OFFUTT, JR., make sure the initials remain separated, like D C OFFUTT JR.
# 3. Replace parentheses surrounding nicknames with quotation marks (e.g. BARB (LEATHERMAN) JUDY with BARB "LEATHERMAN" JUDY.
# 4. Remove double spaces from candidate names (e.g. MARK ROBINSON to MARK ROBINSON).
# 5. Move division and circuit information from judicial offices to the district column.
# 6. Zero-pad numerical districts so they have length three.
# 7. Replace office name BALLOTS_CAST with BALLOTS CAST.

# In[2]:


import pandas as pd
import numpy as np
import os
import re
import csv


# In[3]:


df = pd.read_csv('2018-wv-precinct-autoadapted.csv',index_col=False)
df = df.replace(np.nan, '', regex = True)


# In[4]:


df.office.unique()


# In[5]:


#MERGING COUNTY_FIPS
df['state'] = 'West Virginia' #need it like this to merge; CHANGE LATER
countyFips = pd.read_csv("../../help-files/county-fips-codes.csv")
#print(countyFips.head)
df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
#now can change 'state' column  back to NC
df['state'] = df['state'].str.upper()


# In[6]:


df['readme_check'] = 'FALSE'
df['date'] = '2018-11-06' #check formatting


# In[7]:


l = list()
def fix_cand(x):
    x=x.replace("''",'"')
    x=x.replace(',','')
    if x == 'AGAINST': return 'NO'
    if x == 'FOR': return 'YES'
    if '.' in x:
        if x[-1] != '.' and x[x.find('.')+1] != ' ': return x.replace('.',' ')
        else: return x.replace('.','')
    if '(' in x or '"' in x: #middle names or nick names 
        
        x=x.replace('/(','"').replace('/)','"')
        x=x.replace('(','"').replace(')','"')
        
            
        if len(x.split())>2 and len(x.split()[2]) ==1: #if it's an initial after the nickname
            return x.split()[0] +' '+ x.split()[2]+' '+x.split()[1] +' '+ ' '.join(x.split()[3:])
        else: 
            return x
    if 'WRITE' in x: return 'WRITEIN'
    
    return x

df['candidate'] = df['candidate'].apply(fix_cand)


# In[8]:


df.candidate.unique()


# 5. Move division and circuit information from judicial offices to the district column.
# 6. Zero-pad numerical districts so they have length three.
# 7. Replace office name BALLOTS_CAST with BALLOTS CAST.

# In[9]:


l = list()
def fix_office(x):
    if x == 'BALLOTS_CAST': return 'BALLOTS CAST'
    if x == "REGISTERED": return "REGISTERED VOTERS"
    elif 'CIRCUIT COURT' in x: return 'CIRCUIT COURT JUDGE'
    elif 'SUPREME COURT' in x: return 'SUPREME COURT OF APPEALS JUSTICE'
    x = x.replace('CITY OF','-')
    if x[:4] == 'CITY': return ' '.join(x.split()[:2])+' - '+x.split()[-1]
    return x
    
def fix_dist(off, dist):
    if 'CIRCUIT COURT' in off: return '013'
    elif 'SUPREME COURT' in off: return off[-1].zfill(3)
    else: return str(dist).replace('.0','').zfill(3)
    
#sorted(df.office.unique())


# In[ ]:





df['district'] = df['district'].replace(['WARD 2','WARD 4'],['002','004'])

df['district'] = df.apply(lambda x: fix_dist(x['office'],x['district']), axis=1)
df['office'] = df['office'].apply(fix_office)


# In[11]:


df['party_detailed'] = df.party_detailed.replace({'NO PARTY AFFILIATION':'INDEPENDENT'})
df['party_simplified'] = df.party_simplified.replace({'NO PARTY AFFILIATION':'OTHER'})

        


# In[12]:
# supreme court
df.loc[df['office'] == 'SUPREME COURT OF APPEALS JUSTICE', 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'] == 'SUPREME COURT OF APPEALS JUSTICE', 'party_simplified'] = 'NONPARTISAN'
# boe
df.loc[df['office'] == 'NON-PARTISAN BOARD OF EDUCATION', 'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'] == 'NON-PARTISAN BOARD OF EDUCATION', 'party_simplified'] = 'NONPARTISAN'
df.loc[df['office'] == 'NON-PARTISAN BOARD OF EDUCATION', 'office'] = 'BOARD OF EDUCATION'


# In[13]:


#df['writein'] = df.writein.replace({True:'TRUE',False:'FALSE'})
# replace every instance
df = df.replace([True,False],['TRUE','FALSE'])

# In[14]:


df.district = df.district.replace({'000':''})
df.district.unique()


# ##### get the magnitude from the raw data

# In[ ]:





# In[32]:


raw = []
folders = [f for f in os.listdir('../raw') if '.' not in f]
for folder in folders:
    file = [x for x in os.listdir('../raw/'+folder) if ('xlsx' in x.lower() and '~' not in x)]
    raw.append((folder,pd.read_excel('../raw/'+folder+'/'+file[0]))) #need to keep the county name


# In[33]:


len(raw) == len(df.county_name.unique())


# In[34]:


df_mag = [] #pd.DataFrame(columns=['office','magnitude','county_name'])
for county, r in raw:
    #r['county_name'] = county
    #r['office'] = [x[:x.find(' (')] for x in r[r.columns[-2]][2:]]
    #r['magnitude'] = [x[-2] for x in r[r.columns[-3]][2:]]
    df_mag.extend(r[r.columns[-1]].to_list())
    
    #df_mag.append(r[['office','magnitude','county_name']],ignore_index=False)

df_mag = list(set(df_mag))[1:]
df_mag[0] = 'PROSECUTING ATTORNEY - UNEXPIRED TER ( 1)' #change to 'TERM'? check if this matches raw data


# In[ ]:





# In[35]:


df_mag = [(x[:x.find(' (')],x[-2]) for x in df_mag if x[-2]!='1']
len(df_mag)


# In[36]:


for i, entry in enumerate(df_mag):
    if not entry[1].isnumeric():
        df_mag.remove(entry)
len(df_mag)


# In[21]:


#df_mag.remove(df_mag[8])
#df_mag.remove(df_mag[-2])
#df_mag.remove(df_mag[-11])


# In[37]:


df_mag #berekely county council is mag 2


# In[39]:


df_mag = pd.DataFrame(df_mag, columns=['office','magnitude'])
df_mag['magnitude'] = df_mag.magnitude.astype(int)
df_mag['district'] = df_mag['office'].apply(lambda x: x[-13:-11].strip().zfill(3) if 'DELEGATES' in x else "")
df_mag['office'] = df_mag['office'].apply(lambda x: 'STATE HOUSE' if 'DELEGATES' in x else x.upper())
#df_mag['officeclean'] = df_mag.office.apply(fix_office)
#df_mag['district'] = df_mag.officeclean.apply()


# In[40]:


df_mag = df_mag[df_mag.office != 'COUNTY COUNCIL']
df_mag


# In[41]:


df = pd.merge(df, df_mag, on = ['office','district'],how = 'left')
df['magnitude'] = df['magnitude'].replace({np.nan:1}).astype(int)
df.loc[(df.office=='COUNTY COUNCIL')&(df.county_name=='BERKELEY'),'magnitude'] = 2
df.loc[(df.office=='COUNTY COUNCIL')&(df.county_name=='BERKELEY'),'magnitude'] = 2


# In[43]:


df.loc[df.office.str.contains('REGISTER'),'magnitude'] = 0
df.loc[df.office.str.contains('BALLOTS CAST'),'magnitude'] = 0
#df.loc[df.office.str.contains('REGISTER'),'candidate'] = 'REGISTERED VOTERS'
df.loc[df['office']=='CIRCUIT COURT JUDGE','dataverse'] = 'STATE'
df.loc[df['office']=='REGISTERED VOTERS','dataverse'] = ''
df.loc[df['office']=='BALLOTS CAST','dataverse'] = ''

# In[248]:


df.magnitude.unique()


# In[249]:


df[df.magnitude>1].office.unique()


# In[250]:


df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()
print('made copy')
df = df.replace('  ', ' ', regex = True) #.replace('- ','-', regex = True) #.replace('  ', ' ', regex = True)
print('1/2')
df = df.applymap(lambda x: x.strip() if type(x) == str else x)
print('done')


# In[253]:


#df_final.to_csv("C:/Users/abguh/Desktop/urop/2020-precincts/precinct/NC/2020-nc-precinct-general.csv", index = False)
df.to_csv("2018-wv-precinct-general-updated.csv", encoding='utf-8',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[38]:


#get_ipython().system('jupyter nbconvert --to script wv_2021_updates.ipynb')


# In[ ]:




