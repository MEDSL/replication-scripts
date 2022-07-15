#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
import csv


# In[3]:


file = '2018-vt-precinct-autoadapted.csv'
df = pd.read_csv(file)
df.fillna('', inplace=True)
agg_writein = df[df.drop(columns = 'votes').duplicated(keep = False)]
agg_writein = agg_writein.groupby(list(agg_writein.drop(columns = 'votes'))).agg(sum).reset_index()
df = df[~(df.drop(columns = 'votes').duplicated(keep = False))]
df = pd.concat([df,agg_writein])

# In[4]:


def fixBool(x):
    if x == True:
        return 'TRUE'
    else:
        return 'FALSE'
    
df['special'] = df['special'].apply(fixBool)
df['writein'] = df['writein'].apply(fixBool)


# In[6]:


df['date'] = '2018-11-06'
df['state_fips'] = '50'
df['state_cen'] = '13'
df['state_ic'] = '06'


# In[9]:

def merge_fips_codes(df):
    # add county codes
    fips = pd.read_csv("../../../help-files/county-fips-codes.csv")
    fips['county_name'] = fips['county_name'].replace('DEKALB','DE KALB')
    fips['state'] = fips['state'].str.upper()
    df = pd.merge(df, fips, on = ['state','county_name'],how = 'left')
    df['county_fips'] = df['county_fips'].astype(str).str.replace('\.0','', regex=True).str.zfill(5)
    # get jurisdiction fips codes
    juris_fips = pd.read_csv("../../../help-files/jurisdiction-fips-codes.csv",dtype={'jurisdiction_fips':str})
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
df = merge_fips_codes(df)

# # merging county_name to get county_fips
# county_fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv')
# county_fips = county_fips[county_fips['state']=='Vermont'].drop(columns='state')
# df = df.merge(county_fips, on='county_name')
# df


# # In[10]:


# # merging jurisdiction_name to get jurisdiction_fips
# jurisdiction_fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/jurisdiction-fips-codes.csv')
# jurisdiction_fips = jurisdiction_fips[jurisdiction_fips['state']=='Vermont'].drop(columns='state')
# df = df.merge(jurisdiction_fips, on='jurisdiction_name', how='left')
# df


# In[11]:


def fixJurisdictionFips(name, fips):
    if name=='SAINT JOHNSBURY':
        return '5000562200'
    if name=='SAINT GEORGE':
        return '5000762050'
    if name=='SAINT ALBANS CITY':
        return '5001161675'
    if name=='SAINT ALBANS TOWN':
        return '5001161750'
    if name=='NEWPORT CITY':
        return '5001948850'
    if name=='NEWPORT TOWN':
        return '5001948925'
    if name=='RUTLAND CITY':
        return '5002161225'
    if name=='RUTLAND TOWN':
        return '5002161300'
    if name=='BARRE CITY':
        return '5002303175'
    if name=='BARRE TOWN':
        return '5002303250'
    return fips
df['jurisdiction_fips'] = df.apply(lambda x: fixJurisdictionFips(x['jurisdiction_name'], x['jurisdiction_fips']), axis=1)
print("!!! Jurisdiction codes fixed !!!")

# In[12]:


def cleanCandidate(x):
    if '[WRITE-IN]' in x:
        return 'WRITEIN'
    if x=='WOODMAN "WOODY" H. PAGE':
        return 'WOODMAN H "WOODY" PAGE'
    if any(s in x for s in ['ACAB, TIM', 'AUTIN, GERALD', 'BABINEAU, CARLA', 'BACON, JASON', 'BERGERON, WHITNEY', 
                            'BOGIE, JEFF', 'BUTLER, MARTIN', 'CANDON, JACK', 'CANDON, TOM', 'CASHIN, EMIL', 
                            'CICCOTELLI, ERNIE', 'FRASER, DAN', 'GERE, ROBERT', 'GOODRICH, MIKE', 'GORDON, CHUCK', 
                            'HALQUIST, CHRISTINE', 'HARDY, SCOOTER', 'HENKIN, JUDY', 'HUBBARD, CARSON', 'KREIS, DON', 
                            "O'DONNELL, ROBERT", 'PAIGE, H. BROOKE', 'PINELLO, CHRISTINE', 'PIPER, ED', 'PIRO, ROBERT',
                            'RABINE, ROWLAND', 'RAKHRA, HARJIT', 'SACHS, ERNEST', 'SANDERS, BERNIE', 'SCRUGGS, MIKE', 
                            'SMITH, CHRIS', 'STANZEL, PETER', 'STANZEL, PETER', 'STERLING, TOM', 'STETTENHEIM, JOEL', 
                            'STOFFLET, SUSAN', 'STONE, DOUG', 'VOEKEL, PAMELA', 'WATSON, JASON', 'WEBSTER, GRAHAM', 
                            'WHITEHAIR, EBBEN', 'WILLIAMS, STAN']):
        x = x.split(', ')[1] + ' ' + x.split(', ')[0]
    x = x.replace(',', '')
    if any(s in x for s in ['C.LYONS', 'P.MONTE', 'S.GOLEC']):
        x = x.replace('.', ' ')
    x = x.replace('.', '')
    x = x.replace(';', '')
    if x=='TARA WARE\WICK':
        return 'TARA WAREWICK'
    return x

df['candidate'] = df['candidate'].apply(cleanCandidate)


# In[13]:


def checkSpoiled(x, y):
    if any(s==x for s in ['SPOIL', 'SPOILED', 'SPOLED']) and y==False:
        return 'UNDERVOTES'
    else:
        return x
df['candidate'] = df.apply(lambda x: checkSpoiled(x['candidate'], x['writein']), axis=1)


# In[14]:


# def cleanDistrict(x, y):
#     if x != 'STATEWIDE':
#         return y
#     return x
# df['district'] = df.apply(lambda x: cleanDistrict(x['district'], x['precinct']), axis=1)


# In[15]:

# reassign
df.loc[df['office']=='US HOUSE','district'] = '000'

# writein and overvote candidates in state house and state senate are missing district info. Scrape from precinct field
df.loc[(df['district']=="")&(df['office'].isin(['STATE HOUSE','STATE SENATE'])),
 'district'] = df.loc[(df['district']=="")&(df['office'].isin(['STATE HOUSE','STATE SENATE'])), 'precinct'].str.replace(r'.+_','',regex=True)
# df['district'] = df['district'].astype(str).str.zfill(3)


# In[16]:


# def addFloat(o, p):
#     if o == 'STATE SENATE':
#         if any(s in p for s in ['HUNTINGTON', 'WILMINGTON', 'BRADFORD',
#                                 'FAIRLEE', 'NEWBURY', 'ORANGE', 
#                                 'TOPSHAM', 'WEST FAIRLEE','MONTGOMERY',
#                                 'RICHFORD', 'WOLCOTT', 'ALBURGH', 'COLCHESTER', 'LONDONDERRY',
#                                 'MOUNT HOLLY']):
#             return p + ' - FLOAT'
#     return p
# df['precinct'] = df.apply(lambda x: addFloat(x['office'], x['precinct']), axis=1)


# In[17]:


# def readme_check(x):
#     if ' - FLOAT' in x:
#         return 'TRUE'
#     return 'FALSE'
df['readme_check'] = "FALSE" #df['precinct'].apply(readme_check)


# In[18]:


def fillMagnitude(x, p, c):
    if x=='STATE SENATE' and c=='CHITTENDEN':
        if 'HUNTINGTON' in p:
            return 2
        if 'COLCHESTER' in p:
            return 1
        return 6
    if x=='STATE SENATE' and c=='ADDISON':
        return 2
    if x=='STATE SENATE' and c=='BENNINGTON':
        return 2
    if x=='STATE SENATE' and c=='CALEDONIA':
        return 2
    if x=='STATE SENATE' and c=='ESSEX-ORLEANS':
        return 2
    if x=='STATE SENATE' and c=='FRANKLIN':
        if any(s in p for s in ['MONTGOMERY', 'RICHFORD']):
            return 2
        return 2
    if x=='STATE SENATE' and c=='WINDHAM':
        if 'WILMINGTON' in p:
            return 2
        if 'LONDONDERRY' in p:
            return 3
        return 2
    if x=='STATE SENATE' and c=='RUTLAND':
        if 'MOUNT HOLLY' in p:
            return 3
        return 3
    if x=='STATE SENATE' and c=='WASHINGTON':
        return 3
    if x=='STATE SENATE' and c=='WINDSOR':
        return 3
    if x=='STATE SENATE' and c=='GRAND ISLE':
        if 'ALBURGH' in p:
            return 2
        return 1
    if x=='STATE SENATE' and c=='LAMOILLE':
        if 'WOLCOTT' in p:
            return 2
        return 1
    if x=='STATE SENATE' and c=='ORANGE':
        if any(s in p for s in ['BRADFORD', 'FAIRLEE', 'WEST FAIRLEE',
                                'NEWBURY', 'TOPSHAM', 'ORANGE']):
            return 2
        return 1
    else:
        return 1
df['magnitude'] = df.apply(lambda x: fillMagnitude(x['office'], x['precinct'], x['county_name']), axis=1)


# In[19]:


column_names = ['precinct', 'office', 'party_detailed', 'party_simplified', 'mode', 'votes', 
                'county_name', 'county_fips', 'jurisdiction_name', 'jurisdiction_fips', 'candidate', 'district', 
                'dataverse', 'year', 'stage', 'state', 'special', 'writein', 'state_po', 
                'state_fips', 'state_cen', 'state_ic', 'date', 'readme_check', 'magnitude']
df = df.reindex(columns=column_names)
df.to_csv('2018-vt-precinct-general-updated.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)


# In[18]:


# li = []
# def test(x):
#     if '.' in x:
#         li.append(x)
# df['candidate'].apply(test)
# print(set(li))


# # In[19]:


# print(sorted(df.candidate.unique()))


# In[20]:


# dfsen = df[df['office']=='STATE SENATE']
# dfsen


# # In[21]:


# dfsen.to_csv('testss1.csv', index=False)


# In[ ]:





# 
