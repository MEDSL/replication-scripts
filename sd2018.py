#!/usr/bin/env python
# coding: utf-8

# 1. 2018 issue is still open. Resolve issues there first.
# 2. Add columns {'readme_check', 'county_fips', 'jurisdiction_fips', 'date', 'magnitude'}.
# 3. Remove periods from candidate names. BVe careful of double initial names such as V.J. SMITH, make sure the names remain separated (in that case V J SMITH).
# 4. Remove extra spaces in candidate names KRIS K. LANGER and R. BLAKE CURD.
# 5. Several candidates triggered the mutual similarity check (e.g. RYAN RYDER and RYAN A. RYDER). Make sure if they represent the same candidate that they have the same name.
# 6. Some office=="PUBLIC UTILITIES COMMISSIONER" currently indicate dataverse=="". Investigate those and make sure they should/shouldn't be replaced with dataverse=="STATE".
# 7. Zero-pad numerical districts so they have length three.
# 8. KRISTIE FIEGEN and RAYNE FREDERICK appearas running for both PUBLIC UTILITIES COMMISSIONER and COMMISSIONER OF SCHOOL AND PUBLIC LANDS. Similarly, RYAN BRUNNER and WOODY HOUSER appear as running for COMMISSIONER OF SCHOOL AND PUBLIC LANDS and SCHOOL AND LANDS. Make sure the offices, if they represent the same race, have a unique name.
# 9. Several candidates appear as running with multiple parties (e.g. TIM BJORKMAN and FAITH SPOTTED EAGLE). Make sure these multiple denominations are correct.

# In[321]:


import pandas as pd
import numpy as np
import os
import re
import csv


# In[322]:


df = pd.DataFrame()
official_dtypes = {'precinct':str,'office':str,'mode':str,'votes':int, 'candidate':str, 'district':str}
files = [i for i in os.listdir("../raw/counties-fixed-columns") if '.csv' in i]
for file in files:
    df1 = pd.read_csv("../raw/counties-fixed-columns/"+file) #dtype = official_dtypes)
    df1['votes'] = df1['votes'].fillna(0)
    df1 = df1[df1['precinct'].notnull()]
    df1['precinct'] = df1['precinct'].astype(str)
    #missing results in butte county that need manual addition
    if file == '20181106__sd__general__butte__precinct.csv':
        df1.loc[-1] = ['Butte','Precinct-08 (Precinct-13, Precinct-14)','State Senate', 29, 'REP', 
                'Gary Cammack',339]
        df1.loc[-2] = ['Butte','Precinct-08 (Precinct-13, Precinct-14)','State Senate', 29, 'DEM', 
                        'Matt Kammerer',104]
        df1.loc[-3] = ['Butte','Precinct-08 (Precinct-13, Precinct-14)','State House', 29, 'REP', 
                        'Kirk Chaffee',312]
        df1.loc[-4] = ['Butte','Precinct-08 (Precinct-13, Precinct-14)','State House', 29, 'REP', 
                        'Thomas Brunner',310]
        df1.loc[-5] = ['Butte','Precinct-08 (Precinct-13, Precinct-14)','State House', 29, 'DEM', 
                        'Michael McManus',72]
        df1.loc[-6] = ['Butte','Precinct-08 (Precinct-13, Precinct-14)','State House', 29, 'DEM', 
                        'Jade Addison',70]
    if file == '20181106__sd__general__codrington__precinct.csv':
        # state house district 4 missing precinct
        df1.loc[-1] = ['Codington','GRACELAND, HENRY, HENRY','State House', 4, 
        'LIB', 'Darl Root',7]
        df1.loc[-2] = ['Codington','GRACELAND, HENRY, HENRY','State House', 4, 
        'REP', 'Fred Deutsch',114]
        df1.loc[-3] = ['Codington','GRACELAND, HENRY, HENRY','State House', 4, 
        'REP', 'John Mills',85]
        df1.loc[-4] = ['Codington','GRACELAND, HENRY, HENRY','State House', 4, 
        'DEM', 'John Chilson',67]
        df1.loc[-5] = ['Codington','GRACELAND, HENRY, HENRY','State House', 4, 
        'DEM', 'Kathy Tyler',51]
        
    df1 = df1.iloc[:,:7]
    df = df.append(df1,ignore_index=True)


df['precinct'] = df['precinct'].str.upper().str.strip()
df = df[df['precinct']!="TOTAL"]
todrop = ['MEADE SD', 'MINNEHAHA SD', 'OGLALA SD','PENNINGTON SD']
df = df[~(df.precinct.isin(todrop))]
df = df.fillna("")

# In[324]:


#MERGING COUNTY_FIPS
df['state'] = 'South Dakota'
countyFips = pd.read_csv("../../../help-files/county-fips-codes.csv")
df['county_name'] = df['county'].str.upper()
df = pd.merge(df, countyFips, on = ['state','county_name'], how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
df['state'] = df['state'].str.upper()
df['state_po'] = 'SD'
df['state_fips'] = 46
df['state_cen'] = 45
df['state_ic'] = 37


df.office.unique()


# In[326]:


# print(len(df))
df = df[~(df.office==0)]
len(df) #150 rows


# In[327]:


def fix_office(x):
    if 'U.S.' in x or x=='US House': return 'US HOUSE'
    if 'GOVERNOR' in x.upper(): return 'GOVERNOR AND LIEUTENANT GOVERNOR' #CHECK on standardizing cand names, removing lieutant 
    elif 'UTILITIES' in x.upper(): return 'PUBLIC UTILITIES COMMISSIONER'
    elif 'STATE SENA' in x.upper(): return 'STATE SENATE'
    elif 'SCHOOL AND' in x.upper(): return 'COMMISSIONER OF SCHOOL AND PUBLIC LANDS'
    else: return x.upper()

df['office'] = df['office'].apply(fix_office)
sorted(df.office.unique())


# In[328]:


def get_dataverse(x):
    if x in ['ATTORNEY GENERAL', 'COMMISSIONER OF SCHOOL AND PUBLIC LANDS', 'GOVERNOR', 'GOVERNOR AND LIEUTENANT GOVERNOR',
             'PUBLIC UTILITIES COMMISSIONER', 'SCHOOL AND LANDS','SECRETARY OF STATE','STATE AUDITOR',
             'STATE HOUSE', 'STATE SENATE','STATE TREASURER']: return 'STATE'
    elif x == 'US HOUSE': return 'HOUSE'
    
df['dataverse'] = df['office'].apply(get_dataverse)


# In[329]:


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
            
        if len(x.split())>2 and len(x.split()[2]) ==1: #if it's an initial after the nickname
            return x.split()[0] +' '+ x.split()[2]+' '+x.split()[1] +' '+ ' '.join(x.split()[3:])
        else: 
            return x
    if 'WRITE' in x: return 'WRITEIN'
    if ' AND ' in x: return x[:x.find(' AND')]
    
    return x

df['candidate'] = df['candidate'].apply(lambda x: re.sub("[()]",'"', x))
df['candidate'] = df['candidate'].apply(fix_cand).apply(lambda x: x.upper())
df['candidate'] = df['candidate'].replace('DUSTY JOHNSON','DUSTIN "DUSTY" JOHNSON')
df['candidate'] = df['candidate'].replace('JOHN WIIK','JOHN WILK')
df['candidate'] = df['candidate'].replace('ANNA ANDERSON','ANNA KERNER ANDERSSON')
df['candidate'] = df['candidate'].replace('DARYL ROOT','DARYL LAMAR ROOT')
df['candidate'] = df['candidate'].replace('JOHN CHILSON','JIM CHILSON')
# In[330]:


sorted(df.candidate.unique())


# In[ ]:





# In[ ]:





# In[331]:


df18 = pd.read_csv("2018-sd-precinct-autoadapted.csv")
df18.office.unique()


# In[332]:


#use unique names from cleaned 2018 file as groundtruth 
sorted(df.candidate.unique())


# In[333]:


df['date'] = '2018-11-06'
df['mode'] = 'TOTAL'
df['year'] = '2018'
df['jurisdiction_name'] = df['county_name']
df['stage'] = 'GEN'
df['writein'] = 'FALSE'
df['special'] = 'FALSE'


# In[334]:


df.party.unique()


# In[335]:


df['party_detailed'] = df.party.replace({'LIB':'LIBERTARIAN','REP':'REPUBLICAN','DEM':'DEMOCRAT','IND':'INDEPENDENT',
                                        'Lbt':'LIBERTARIAN','Rep':'REPUBLICAN','Dem':'DEMOCRAT','Ind':'INDEPENDENT',0:""})
df.party_detailed.unique()


# In[336]:


df.loc[df.candidate=='FAITH SPOTTED EAGLE','party_detailed'] = 'DEMOCRAT'
df.loc[df.candidate=='JAMES WHITE','party_detailed'] = 'REPUBLICAN'


# In[337]:


df['district'] = df.district.apply(lambda x: str(int(x)).zfill(3) if type(x)!=str else x.zfill(3))
df.district.unique()


# In[338]:


df.loc[df.district=='000','district'] = 'STATEWIDE'


# In[339]:


#there are some house offices that have '000' as district - need to investigate
#df[(df.office=='US HOUSE')&(df.district=='000')].candidate.unique()

df.loc[(df.candidate=='GEORGE HENDRICKSON'),'district'] = '012'
df.loc[(df.candidate=='DUSTY JOHNSON')|(df.candidate=='TIM BJORKMAN')|(df.candidate=='RON WIECZOREK'),'district'] = 'AT-LARGE'


# In[340]:


cands = '''JOHN GORS ||| [[JOHN A GORS]]
    JOHN LAKE ||| [[JOHN A LAKE]]
    BLAKE CURD ||| [[R BLAKE CURD]]
    JASON HILL ||| [[JASON D HILL]]
    KURT EVANS ||| [[KURT EVANS AND RICHARD SHELATZ]]
    MARY DUVAL ||| [[MARY DUVALL]]
    RYAN MAHER ||| [[RYAN M MAHER]]
    RYAN RYDER ||| [[RYAN A RYDER]]
    KRISTI NOEM ||| [[KRISTI NOEM AND LARRY RHODEN]]
    ROCKY BLARE ||| [[ROCKY DALE BLARE]]
    RYAN BRUNER ||| [[RYAN BRUNNER]]
    GARY CAMMACK ||| [[GARY L CAMMACK]]
    GIDEON OAKES ||| [[A GIDEON OAKES]]
    HUGH BARTELS ||| [[HUGH M BARTELS]]
    MARGARET ANN ||| [[MARGARET ANN WALSH]]
    PAUL DENNERT ||| [[H PAUL DENNERT]]
    RANDY SEILER ||| [[RANDY SELLER]]
    RONWIECZOREK ||| [[RON WIECZOREK]]
    SUSAN WISMER ||| [[SUSAN M WISMER]]
    WOODY HAUSER ||| [[WOODY HOUSER]]
    BILLIE SUTTON ||| [[BILLIE SUTTON AND MICHELLE LAVALLEE]]
    JUSTIN CRONIN ||| [[JUSTIN R CRONIN]]
    KRISTI FIEGEN ||| [[KRISTIE FIEGEN]]
    LARRY ZIKMUND ||| [[LARRY P ZIKMUND]]
    MARGARET MOSS ||| [[MARGARET ROSS]]
    RICH SATTGAST ||| [[RICH SATTGAST"]]
    RICH SATTQAST ||| [[RICH SATTGAST"]]
    AMANDA BACHMAN ||| [[AMANDA BACHMANN]]
    BRIAN WATERSON ||| [[BRIAN WATTERSON]]
    MARGARET WALSH ||| [[MARGARET ANN WALSH]]
    MARK WILLADSEN ||| [[MARK K WILLADSEN]]
    SCOTT PETERSEN ||| [[SCOTT C PETERSEN]]
    SHERYL JOHNSON ||| [[SHERYL L JOHNSON]]
    THOMAS BRUNNER ||| [[THOMAS J BRUNNER]]
    HOWARD GRINAGAR ||| [[HOWARD GRINAGER]]
    MICHAEL MCMANUS ||| [[MICHAEL S MCMANUS]]
    TIMOTHY GOODWIN ||| [[TIMOTHY RAY GOODWIN]]
    JORDAN YOUNGBERG ||| [[JORDAN YOUNGBERT]]
    MARGARET KUIPERS ||| [[MARGARET KULPERS]]
    PAUL R MISKIMINS ||| [[PAUL R MISKIMMINS]]
    STEVEN MCCLEEREY ||| [[STEVEN D MCCLEEREY]]
    STEVEN D MCCLEERY ||| [[STEVEN D MCCLEEREY]]
    GEORGE HENDRICKSON ||| [[GEORGE D HENDRICKSON]]
    FAITH SPOTTED EAGLE ||| [[FAITH SPOTTED EAQLE]]
    ANNA KERNER ANDERSON ||| [[ANNA KERNER ANDERSSON]]'''
    
cands = cands.split('\n')
cands = [c.replace(']]','').strip().split(' ||| [[') for c in cands]
cands


# In[341]:


df18cands = [cand.replace('.','') for cand in df18.candidate.unique()]
for pair in cands: 
    #print(pair)
    
    if pair[0] in df18cands: pair.append(pair[0]) #if it's the correct name, append it as last item for easy access
    elif pair[1] in df18cands: pair.append(pair[1])
    else: print(pair)
        
    if len(pair) >3: print(pair)
    
    #now fix those rows to update with the correct name that we just appended 
    df.loc[(df.candidate==pair[0])|(df.candidate==pair[1]),'candidate'] = pair[-1]


# In[342]:


df.loc[df.candidate.str.contains('RICH SATT'),'candidate'] = 'RICH SATTGAST'
df.loc[df.candidate.str.contains('MCCLEER'),'candidate'] = 'STEVEN D MCCLEERY'


# In[343]:


##cands with mutliple parties

cands = [('ANNA KERNER ANDERSSON', 'DEMOCRAT'),#dem
         ('CHRIS FRANCIS','DEMOCRAT'),#dem 
         ('FAITH SPOTTED EAGLE','DEMOCRAT'),#dem
         ('JAMES WHITE','REPUBLICAN'), #repub
         ('JULIE FRYE-MUELLER','REPUBLICAN'), #repub
         ('KAREN MCGREGOR','DEMOCRAT'), #dem
         ('MARGARET ROSS','DEMOCRAT'), #dem
         ('NICK REID','INDEPENDENT'), #independent
         ('RED DAWN FOSTER','DEMOCRAT'), #dem
         ('TIM BJORKMAN','DEMOCRAT')] #dem

for cand, party in cands:
    #a = df[(df.candidate==cand)][['office','district','writein','party_detailed']].drop_duplicates()
    df.loc[df.candidate==cand,'party_detailed'] = party
    #print(a,'\n')




df.loc[df.candidate=='MARGARET MOSS','candidate'] = 'MARGARET ROSS' #error in raw data


# In[345]:


df['party_simplified'] = df['party_detailed'].replace({'INDEPENDENT':'OTHER'})
df.party_simplified.unique()


# In[346]:
# ##### DC FIXES ###############
df['county_fips'] = df['county_fips'].str.replace('\.0','',regex = True)
df['jurisdiction_fips'] = df['county_fips']
df['votes'] = df['votes'].fillna(0)
df['votes'] = df['votes'].astype(str).str.replace(',','',regex=True).astype(float).astype(int)
df = df.replace([True,False],['TRUE','FALSE'])

# https://ballotpedia.org/South_Dakota_House_of_Representatives_elections,_2018
df['magnitude'] = np.where((df['office']=='STATE HOUSE')&(~df['district'].str.contains('A|B')),
    2, 1)
# many undercounts in county compared to official SOS, but correct according to 
# https://www.minnehahacounty.org/dept/au/election/election_returns/2018GeneralElectionResults.pdf
df['readme_check'] = np.where(df['county_name']=='MINNEHAHA',"TRUE","FALSE")

##### MANUAL CORRECTIONS #####################
# districts wrong Senate
df.loc[(df['candidate']=='LEE SCHOENBECK')&
(df['office']=='STATE HOUSE')&
(df['district']=='005'), 'office'] = "STATE SENATE"

df.loc[(df['office']=='STATE SENATE')&
(df['district']=='28A'), 'district'] = "028"

#wrong district
df.loc[(df['county_name']=='YANKTON')&
(df['office']=='STATE SENATE')&
(df['district']=='008'), 'district'] = "018"

# wrong cand and district Senate
df.loc[(df['candidate']=='ROCKY DALE BLARE')&
(df['office']=='STATE SENATE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'candidate'] = "BROCK L GREENFIELD"
df.loc[(df['candidate']=="BROCK L GREENFIELD")&
(df['office']=='STATE SENATE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'district'] = "002"

df.loc[(df['candidate']=='JULIE BARTLING')&
(df['office']=='STATE SENATE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'candidate'] = "PAUL REGISTER"
df.loc[(df['candidate']=="PAUL REGISTER")&
(df['county_name']=='CLARK')&
(df['office']=='STATE SENATE')&
(df['district']=='021'), 'district'] = "002"

#wrong precinct vote total
#https://github.com/openelections/openelections-sources-sd/blob/master/2018/Codington.pdf
df.loc[(df['precinct']=='PRECINCT-B1 (PRECINCT-B4, PRECINCT-E5)') &
(df['office']=='STATE SENATE')&
(df['county_name']=='CODINGTON')&
(df['district']=='005') &
(df['candidate']=='LEE SCHOENBECK'), 'votes'] = 509


# STATE HOUSE FIXES

# wrong cand and district House
df.loc[(df['candidate']=='LEE QUALM')&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'candidate'] = "LANA J GREENFIELD"
df.loc[(df['candidate']=="LANA J GREENFIELD")&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'district'] = "002"

df.loc[(df['candidate']=='CALEB FINCK')&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'candidate'] = "KALEB W WEIS"
df.loc[(df['candidate']=="KALEB W WEIS")&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'district'] = "002"

df.loc[(df['candidate']=='FAITH SPOTTED EAGLE')&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'candidate'] = "JENAE HANSEN"
df.loc[(df['candidate']=="JENAE HANSEN")&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'district'] = "002"

df.loc[(df['candidate']=='ANNA KERNER ANDERSSON')&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'candidate'] = "MIKE MCHUGH"
df.loc[(df['candidate']=="MIKE MCHUGH")&
(df['office']=='STATE HOUSE')&
(df['county_name']=='CLARK')&
(df['district']=='021'), 'district'] = "002"

#wrong district
#wrong office
df.loc[(df['county_name']=='YANKTON')&
(df['office']=='STATE HOUSE')&
(df['district']=='008'), 'district'] = "018"

# missnamed office for these candidates in one county
df.loc[df['candidate'].isin(['KRISTIE FIEGEN', 'WAYNE FREDERICK']),'office'] = 'PUBLIC UTILITIES COMMISSIONER'
#wrong party cand https://sdsos.gov/elections-voting/assets/2018GeneralElectionCanvassPDF.pdf
df.loc[df['candidate'] == 'MARGARET ROSS','party_detailed'] = "DEMOCRAT"
df.loc[df['candidate'] == 'MARGARET ROSS','party_simplified'] = "DEMOCRAT"


df['district'] = df['district'].replace(['26A','26B','28A','28B'],
    ['026A','026B','028A','028B'])

df.loc[df['office']=='US HOUSE', 'district'] = '000'

##### MANUAL CORRECTIONS #####################


df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()


# In[ ]:


df = df.replace('  ', ' ', regex = True) 
df = df.fillna("")
df = df.applymap(lambda x: x.strip() if type(x) == str else x)



df.to_csv("2018-sd-precinct-general-updated.csv", encoding='utf-8',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[ ]:





# In[ ]:





# # ignore everything under this, this was from cleaning autoadapted

# # In[113]:


# df = pd.read_csv('2018-sd-precinct-autoadapted.csv',index_col=False)
# df = df.fillna('')


# # In[114]:


# #MERGING COUNTY_FIPS
# df['state'] = 'South Dakota' #need it like this to merge; CHANGE LATER
# countyFips = pd.read_csv("../../help-files/county-fips-codes.csv")
# #print(countyFips.head)
# df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
# df['county_fips'] = df['county_fips'].apply(str)
# df['jurisdiction_fips'] = df['county_fips']
# df['county_name'] = df['jurisdiction_name']
# #now can change 'state' column  back to NC
# df['state'] = df['state'].str.upper()


# # In[115]:


# df['readme_check'] = 'FALSE'
# df['date'] = '2018-11-06' #check formatting
# df['magnitude'] = 1


# # In[218]:


# l = list()
# def fix_cand(x):
#     x=x.upper()
#     x=x.replace("''",'"')
#     x=x.replace(',','')
#     if x == 'AGAINST': return 'NO'
#     if x == 'FOR': return 'YES'
#     if '.' in x:
#         if x[-1] != '.' and x[x.find('.')+1] != ' ': return x.replace('.',' ')
#         else: return x.replace('.','')
#     if '(' in x or '"' in x: #middle names or nick names         
            
#         if len(x.split())>2 and len(x.split()[2]) ==1: #if it's an initial after the nickname
#             return x.split()[0] +' '+ x.split()[2]+' '+x.split()[1] +' '+ ' '.join(x.split()[3:])
#         else: 
#             return x
#     if 'WRITE' in x: return 'WRITEIN'

    
#     return x

# df['candidate'] = df['candidate'].apply(lambda x: re.sub("[()]",'"', x))
# df['candidate'] = df['candidate'].apply(fix_cand)


# # In[ ]:





# # ##### Similar values in candidate
# # SIMILAR VALUES IN candidate: 
# # 
# #     BLAKE CURD ||| [[R BLAKE  CURD]]
# #     RYAN RYDER ||| [[RYAN A RYDER]]
# #     GIDEON OAKES ||| [[A GIDEON OAKES]]
# #     PAUL DENNERT ||| [[H PAUL DENNERT]]
# #     RANDY SEILER ||| [[RANDY SELLER]]
# #     MARGARET MOSS ||| [[MARGARET ROSS]]

# # In[118]:


# cands = [('BLAKE CURD','R BLAKE  CURD'),('RYAN RYDER','RYAN A RYDER'),('GIDEON OAKES','A GIDEON OAKES'),
#         ('PAUL DENNERT','H PAUL DENNERT'),('RANDY SEILER','RANDY SELLER'),('MARGARET MOSS','MARGARET ROSS')]
# for n1, n2 in cands:
#     print('\n****',n1,',', n2)
#     a = df[(df.candidate==n1)][['office','district','writein','party_detailed','county_name']].drop_duplicates()
#     b = df[(df.candidate==n2)][['office','district','writein','party_detailed','county_name']].drop_duplicates()
#     #print(a)
#     #print(b)
#     print('\toffice match?',a.office.unique() == b.office.unique(),a.office.unique())
#     print('\tdistrict match?',a.district.unique() == b.district.unique(),a.district.unique(),'&',b.district.unique())
#     print('\tcounty match?',a.county_name.unique() == b.county_name.unique())


# # In[119]:


# #did some research into correct names
# df.loc[df.candidate.str.contains('CURD'),'candidate'] = 'R BLAKE CURD'
# df.loc[df.candidate.str.contains('RYDER'),'candidate'] = 'RYAN RYDER'
# df.loc[df.candidate.str.contains('OAKES'),'candidate'] = 'GIDEON OAKES'
# df.loc[df.candidate.str.contains('PAUL DENNERT'),'candidate'] = 'H PAUL DENNERT'
# df.loc[df.candidate.str.contains('RANDY S'),'candidate'] = 'RANDY SEILER'
# df.loc[df.candidate.str.contains('OSS') & df.candidate.str.contains('MARGARET'),'candidate'] = 'MARGARET ROSS'


# # ##### Cands with multiple parties
# # CANDIDATES WITH MULTIPLE PARTIES:
# # 
# #     ANNA KERNER ANDERSSON: ['""' 'DEMOCRAT']
# #     CHRIS FRANCIS: ['REPUBLICAN' 'DEMOCRAT']
# #     FAITH SPOTTED EAGLE: ['""' 'DEMOCRAT']
# #     JAMES WHITE: ['""' 'REPUBLICAN']
# #     JULIE FRYE-MUELLER: ['DEMOCRAT' 'REPUBLICAN']
# #     KAREN MCGREGOR: ['REPUBLICAN' 'DEMOCRAT']
# #     MARGARET ROSS: ['DEMOCRAT' 'REPUBLICAN']
# #     NICK REID: ['DEMOCRAT' 'INDEPENDENT']
# #     RED DAWN FOSTER: ['DEMOCRAT' 'REPUBLICAN']
# #     TIM BJORKMAN: ['DEMOCRAT' 'REPUBLICAN']

# # In[120]:


# cands = ['ANNA KERNER ANDERSSON',#dem
#          'CHRIS FRANCIS',#dem 
#          'FAITH SPOTTED EAGLE',#dem
#          'JAMES WHITE', #repub
#          'JULIE FRYE-MUELLER', #repub
#          'KAREN MCGREGOR', #dem
#          'MARGARET ROSS', #dem
#          'NICK REID', #independent
#          'RED DAWN FOSTER', #dem
#          'TIM BJORKMAN'] #dem
# for cand in cands:
#     print('****',cand)
#     a = df[(df.candidate==cand)][['office','district','writein','party_detailed']].drop_duplicates()
#     #df.loc[df.candidate==cand,'party_detailed'] = cands.get(cand)
#     print(a,'\n')
        


# # In[121]:


# cands = [('ANNA KERNER ANDERSSON', 'DEMOCRAT'),#dem
#          ('CHRIS FRANCIS','DEMOCRAT'),#dem 
#          ('FAITH SPOTTED EAGLE','DEMOCRAT'),#dem
#          ('JAMES WHITE','REPUBLICAN'), #repub
#          ('JULIE FRYE-MUELLER','REPUBLICAN'), #repub
#          ('KAREN MCGREGOR','DEMOCRAT'), #dem
#          ('MARGARET ROSS','DEMOCRAT'), #dem
#          ('NICK REID','INDEPENDENT'), #independent
#          ('RED DAWN FOSTER','DEMOCRAT'), #dem
#          ('TIM BJORKMAN','DEMOCRAT')] #dem

# for cand, party in cands:
#     #a = df[(df.candidate==cand)][['office','district','writein','party_detailed']].drop_duplicates()
#     df.loc[df.candidate==cand,'party_detailed'] = party
#     #print(a,'\n')


# # In[122]:


# df['party_simplified'] = df.party_detailed.replace({'INDEPENDENT':'OTHER'})


# # In[123]:


# df.party_simplified.unique()


# # 7. Zero-pad numerical districts so they have length three.
# # 

# # In[124]:


# ## south dakota  has an at-large house district, rn it's marked as district 0
# df.loc[df.district=='0','district'] = 'AT-LARGE'


# # In[125]:


# df.district.unique()


# # In[126]:


# df['district'] = df.district.apply(lambda x: x.zfill(3) if type(x)==str else x)


# # In[127]:


# df.district.unique()


# # 6. Some office=="PUBLIC UTILITIES COMMISSIONER" currently indicate dataverse=="". Investigate those and make sure they should/shouldn't be replaced with dataverse=="STATE".
# # 

# # In[128]:


# df[df.office=='PUBLIC UTILITIES COMMISSIONER'][['candidate','office','district','dataverse','party_detailed']].drop_duplicates()


# # In[129]:


# #looks like this office should be STATE dataverse
# df.loc[df.office=='PUBLIC UTILITIES COMMISSIONER','dataverse'] = 'STATE'


# # 8. KRISTIE FIEGEN and RAYNE FREDERICK appearas running for both PUBLIC UTILITIES COMMISSIONER and COMMISSIONER OF SCHOOL AND PUBLIC LANDS. Similarly, RYAN BRUNNER and WOODY HOUSER appear as running for COMMISSIONER OF SCHOOL AND PUBLIC LANDS and SCHOOL AND LANDS. Make sure the offices, if they represent the same race, have a unique name.
# # 

# # In[130]:


# df[df.candidate=='RYAN BRUNNER'][['candidate','office','district','dataverse','party_detailed']].drop_duplicates()


# # In[131]:


# # the 'SCHOOL AND LANDS' office is the same as the 'COMMISSIONER OF SCHOOL AND PUBLIC LANDS'
# df.loc[df.office.str.contains('LANDS'),'office'] = 'COMMISSIONER OF SCHOOL AND PUBLIC LANDS'


# # Unsure about this issue (#8). On Ballotpedia, Kristie Fiegen is only listed as running for PUC, not Commissioner of School and Public Lands. 
# # public lands commissioner: https://ballotpedia.org/South_Dakota_Public_Lands_Commissioner_election,_2018
# # 
# # public utilities commissioner: https://ballotpedia.org/South_Dakota_Public_Utilities_Commission_election,_2018

# # In[ ]:





# # 11. There appears to be double counting in [BEADLE, MEADE, OGLALA LAKOTA, PENNINGTON]. probably an aggregate precinct that needs to be dropped.

# # In[132]:


# counties = ['BEADLE', 'MEADE', 'OGLALA LAKOTA', 'PENNINGTON']
# dfc = df[df.county_name.isin(counties)]
# dfc.county_name.unique()


# # In[133]:


# dfc.precinct.unique() #looks like there is a precinct called 'TOTAL'
# print(len(dfc.precinct.unique()))
# len(dfc[dfc.precinct=='TOTAL'])


# # In[134]:


# print(len(df))
# df = df[df.precinct!='TOTAL']
# len(df)


# # 12. There are large discrepancies in MINNEHAHA due to double counting (precinct = 'MINNEHAHA SD'), but also additional precincts that are not in the raw pdfs? could you try dropping these and we will see if the counts match? I have no idea where these came from.
# # 
# # Precinct-VP06
# # Precinct-VP07
# # Precinct-VP08
# # Precinct-VP09
# # Precinct-VP10
# # Precinct-VP11
# # Precinct-VP12
# # Precinct-VP13
# # Precinct-VP15
# # Precinct-VP16
# # Precinct-VP17
# # Precinct-VP21
# # 

# # In[135]:


# #Changes copied from declan's edits to script 
# '''
# todrop = ['VP06','VP07','VP08','VP09','VP10','VP11',
#           'VP12','VP13','VP15','VP16','VP17','VP21']

# a = len(df.precinct.unique())
# df = df[~(df.precinct.isin(todrop))]
# b = len(df.precinct.unique())
# print('dropped',a-b,'precincts')
# '''


# # In[ ]:





# # In[136]:


# df[df.precinct.str.contains('SD')].precinct.unique()


# # In[137]:


# for c in df[df.precinct.str.contains('SD')].county_name.unique():
#     print(c)
#     dfm = df[df.county_name==c]
#     if c == 'OGLALA LAKOTA': p = 'OGLALA SD'
#     else: p = (c+' SD')
#     x = dfm[dfm.precinct== p].votes.sum()
#     y = dfm[dfm.precinct!= p].votes.sum()
#     print('\t',x==y & x!=0, x, y)


# # There are three counties where there is an aggregator precinct: MEADE, MINNEHAHA, OGLALA LAKOTA. the precincts are 'MEADE SD','MINNEHAHA SD',and 'OGLALA SD', respectively. There is another one PENNINGTON SD where the vote is almost a perfect double count but not quite, so I didn't drop them (427,204 vs 428,259).

# # In[138]:


# todrop = ['MEADE SD', 'MINNEHAHA SD', 'OGLALA SD','PENNINGTON SD']

# a = len(df.precinct.unique())
# df = df[~(df.precinct.isin(todrop))]
# b = len(df.precinct.unique())
# print('dropped',a-b,'precincts')


# # ##### Fixing non-unique precinct issue 

# # non-unique precincts for ["BRULE", "BUFFALO", "CAMPBELL", "HYDE"]

# # In[160]:


# #HYDE doesn't have this issue of the 1s??
# df[(df.county_name =='BUFFALO')] #.precinct.unique() # & (df.office=='US HOUSE')]


# # In[156]:


# df[df.precinct=='26B'].county_name.unique()


# # In[ ]:





# # In[140]:


# def get_len(subset):
#     return len(subset) / len(list(subset.candidate.unique()))




# #BRULE should have 5 precincts, BUFFALO 3, CAMPBELL 5
# counties = {'BRULE':5,'BUFFALO':3,'CAMPBELL':5}
# for county in counties.keys():
#     print(county)
#     indices = df[(df.county_name ==county) & (df.office=='US HOUSE')&(df.precinct=='1')].index
#     print(len(indices))
#     subset = df[(df.county_name ==county) & (df.office=='US HOUSE')&(df.precinct=='1')]
    
#     i = get_len(subset) ##how long we need to repeat the item 
    
#     l = []
#     for i in range(20):l.extend(list(np.arange(start=1, stop=counties.get(county)+1, step=1)))
#     subset['precinct'] = l

#     subset = subset.drop_duplicates()
#     df = df.drop(indices)
#     df = df.append(subset, ignore_index=True)


# # In[71]:


# #need to keep the indices bc need to drop them from df
# indices = df[(df.county_name =='BRULE') & (df.office=='US HOUSE')&(df.precinct=='1')].index

# subset = df[(df.county_name =='BRULE') & (df.office=='US HOUSE')&(df.precinct=='1')]
# l = []
# for i in range(20):l.extend(list(np.arange(start=1, stop=6, step=1)))
# subset['precinct'] = l

# subset = subset.drop_duplicates()
# subset


# # In[ ]:





# # In[142]:


# #10 Drop duplicates
# print(len(df))
# df = df.drop_duplicates()
# print(len(df))


# # In[ ]:
# ##### DC FIXES ###############
# df['county_fips'] = df['county_fips'].str.replace('\.0','',regex = True)
# df['jurisdiction_fips'] = df['county_fips']
# df['precinct'] = df['precinct'].str.upper().str.strip()
# df = df.replace([True,False],['TRUE','FALSE'])

# # In[36]:


# df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
#                      "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
#                      "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
#                    "state_ic", "readme_check",'magnitude']].copy()


# # In[282]:


# df = df.replace('  ', ' ', regex = True) #.replace('- ','-', regex = True) #.replace('  ', ' ', regex = True)
# print('1/2')
# df = df.applymap(lambda x: x.strip() if type(x) == str else x)
# print('done')


# # In[283]:


# #df_final.to_csv("C:/Users/abguh/Desktop/urop/2020-precincts/precinct/NC/2020-nc-precinct-general.csv", index = False)
# df.to_csv("2018-sd-precinct-general-updated.csv", encoding='utf-8',quoting=csv.QUOTE_NONNUMERIC, index=False)


# # In[ ]:




