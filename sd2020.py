#!/usr/bin/env python
# coding: utf-8

# In[31]:


import pandas as pd
import numpy as np
import os
import csv
# warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.display.max_columns = 30


# In[32]:


def get(xlsx):
    counties=xlsx.sheet_names
    sheet_index=np.arange(len(xlsx.sheet_names))
    sheet_to_df_map = {}
    for sheet in sheet_index:
        sheet_to_df_map[counties[sheet]] = xlsx.parse(sheet, skiprows= 6,skipfooter=1)
        sheet_to_df_map[counties[sheet]]['County']=counties[sheet]
    return sheet_to_df_map


# In[33]:


pres=pd.ExcelFile('raw/president_precinct_results.xlsx')
def format_president():
    df=pd.concat(get(pres).values()).rename(columns={'Donald J. Trump and Michael R. Pence':'DONALD J TRUMP',
                                                          'Jo  Jorgensen and Jeremy "Spike" Cohen':'JO JORGENSEN',
                                                          'Joseph R. Biden and Kamala Harris':'JOSEPH R BIDEN'})
    df = df.drop(df.columns[0],axis=1)
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=['DONALD J TRUMP','JO JORGENSEN','JOSEPH R BIDEN'])
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    conditions = [(df['candidate'] == 'DONALD J TRUMP'),(df['candidate'] == 'JOSEPH R BIDEN'),(df['candidate'] == 'JO JORGENSEN')]
    df['party_detailed'] =np.select(conditions, ['REPUBLICAN', 'DEMOCRAT', 'LIBERTARIAN'])
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='US PRESIDENT'
    df['dataverse'] = 'PRESIDENT'
    df['district'] = 'STATEWIDE'
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
president = format_president()


# In[34]:


sen=pd.ExcelFile('raw/senate_precinct_results.xlsx')
def format_senate():
    df=pd.concat(get(sen).values()).rename(columns= {'Mike Rounds':'MIKE ROUNDS','Dan  Ahlers ':'DAN AHLERS'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    conditions = [(df['candidate'] == 'MIKE ROUNDS'),(df['candidate'] == 'DAN AHLERS')]
    df['party_detailed'] =np.select(conditions, ['REPUBLICAN', 'DEMOCRAT'])
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='US SENATE'
    df['dataverse'] = 'SENATE'
    df['district'] = 'STATEWIDE'
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
us_senate = format_senate()


# In[35]:


house=pd.ExcelFile('raw/house_precinct_results.xlsx')
def format_house():
    df=pd.concat(get(house).values()).rename(columns= {'Dusty Johnson':'DUSTY JOHNSON','Randy "Uriah"  Luallin ':'RANDY "URIAH" LUALLIN'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    conditions = [(df['candidate'] == 'DUSTY JOHNSON'),(df['candidate'] == 'RANDY "URIAH" LUALLIN')]
    df['party_detailed'] =np.select(conditions, ['REPUBLICAN', 'LIBERTARIAN'])
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='US HOUSE'
    df['dataverse'] = 'HOUSE'
    df['district'] = '000'    
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
us_house = format_house()


# In[36]:


puc=pd.ExcelFile('raw/pu_precinct_results.xlsx')
def format_puc():
    df=pd.concat(get(puc).values()).rename(columns= {'Gary Hanson':'GARY HANSON','Devin Saxon':'DEVIN SAXON',
                                                   'Remi W. B. Bald Eagle':'REMI W B BALD EAGLE'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    conditions = [(df['candidate'] == 'GARY HANSON'),(df['candidate'] == 'REMI W B BALD EAGLE'),(df['candidate'] == 'DEVIN SAXON')]
    df['party_detailed'] =np.select(conditions, ['REPUBLICAN', 'DEMOCRAT','LIBERTARIAN'])
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='PUBLIC UTILITIES COMMISSIONER'
    df['dataverse'] = 'STATE'
    df['stage']='GEN'
    df['district'] = 'STATEWIDE'
    df['magnitude'] = 1
    return df
public_utilities = format_puc()


# In[37]:


m26=pd.ExcelFile('raw/measure_26.xlsx')
def format_m26():
    df=pd.concat(get(m26).values()).rename(columns= {'Yes':'YES','No':'NO'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    df['party_detailed'] = ''
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='Initiated Measure 26: An initiated measure to legalize marijuana for medical use.'
    df['office'] = df['office'].str.upper()
    df['dataverse'] = 'STATE'
    df['district'] = 'STATEWIDE'
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
measure_26 = format_m26()


# In[38]:


ammendment_a=pd.ExcelFile('raw/ammendment_A.xlsx')
def format_ammendment_a():
    df=pd.concat(get(ammendment_a).values()).rename(columns= {'Yes':'YES','No':'NO'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    df['party_detailed'] = ''
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='Constitutional Amendment A: An amendment to the South Dakota Constitution to legalize, regulate, and tax marijuana; and to require the Legislature to pass laws regarding hemp as well as laws ensuring access to marijuana for medical use.'
    df['office'] = df['office'].str.upper()
    df['dataverse'] = 'STATE'
    df['district'] = 'STATEWIDE'
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
ammendment_a = format_ammendment_a()


# In[39]:


ammendment_b=pd.ExcelFile('raw/ammendment_B.xlsx')
def format_ammendment_b():
    df=pd.concat(get(ammendment_b).values()).rename(columns= {'Yes':'YES','No':'NO'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    df['party_detailed'] = ''
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='Constitutional Amendment B: An amendment to the South Dakota Constitution authorizing the Legislature to allow sports wagering in Deadwood.'
    df['office'] = df['office'].str.upper()
    df['dataverse'] = 'STATE'
    df['district'] = 'STATEWIDE'
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
ammendment_b = format_ammendment_b()


# In[40]:


supreme_court=pd.ExcelFile('raw/supreme_court.xlsx')
def format_supreme_court():
    df=pd.concat(get(supreme_court).values()).rename(columns= {'Yes':'STEVEN JENSEN - YES','No':'STEVEN JENSEN - NO'})
    df = df.drop(df.columns[0],axis=1)
    df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
    df=pd.melt(df, id_vars=['Precinct','County'], value_vars=df.columns[2:].tolist())
    df['County']=df['County'].str.upper()
    df.columns = ['precinct','county_name','candidate','votes']
    # add party
    df['party_detailed'] = 'NONPARTISAN'
    df['party_simplified'] = df['party_detailed']
    # add office, dataverse, district
    df['office']='RETENTION FIRST SUPREME COURT DISTRICT'
    df['dataverse'] = 'STATE'
    df['district'] = 'STATEWIDE'
    df['stage']='GEN'
    df['magnitude'] = 1
    return df
state_supreme_court = format_supreme_court()


# # need each county file bleh (only one for each district race)

# In[41]:


#loops through each of the senate/house district files and concats into one df each
def get_state_congress(xlsx):
    counties=xlsx.sheet_names
    sheet_index=np.arange(len(xlsx.sheet_names))
    sheet_to_df_map = {}
    for sheet in sheet_index:
        sheet_to_df_map[counties[sheet]] = xlsx.parse(sheet, skiprows= 6,skipfooter=1)
        sheet_to_df_map[counties[sheet]]['County']=counties[sheet]
        district = sheet_to_df_map[counties[sheet]].columns[0]
        if district[-1].isalpha():
            district_num = district[-3:]
        else:
            district_num = district[-2:]
        sheet_to_df_map[counties[sheet]][district]=district_num
        sheet_to_df_map[counties[sheet]] = sheet_to_df_map[counties[sheet]].rename({district:'district'},axis=1)
    return sheet_to_df_map
state_senate_filenames=sorted([i for i in os.listdir('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/SD/raw/state_senate') if i[0].isalpha()])
senate_path = 'raw/state_senate/'
state_house_filenames=sorted([i for i in os.listdir('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/SD/raw/state_house') if i[0].isalpha()])
house_path = 'raw/state_house/'
def collapse_all_districts(filenames,path):
    nested_dict = {}
    #creates nested dictionary of each district election by county
    for i in np.arange(len(filenames)):
        xlsx_file = pd.ExcelFile(path+filenames[i])
        nested_dict[filenames[i]] = get_state_congress((xlsx_file))
    #concat all nested values so we have a dict of df
    dictionary = {}
    for district in nested_dict:
        dictionary[district] = pd.concat(nested_dict[district].values())
        df = dictionary[district]
        df = df[[df.columns[-1]]+df.columns[:-1].tolist()]
        df=pd.melt(df, id_vars=['Precinct','County','district'], value_vars=df.columns[3:].tolist())
        df['County']=df['County'].str.upper()
        df.columns = ['precinct','county_name','district','candidate','votes']
        df['candidate'] = df['candidate'].str.replace(r"\(.*\)","",regex=True).str.replace('\.','',regex=True).str.strip()
        df['candidate'] = df['candidate'].str.upper().str.replace(r"\s+"," ",regex=True)
        df['district'] = df['district'].str.zfill(3)
        df['dataverse'] = 'STATE'
        if 'senate' in district:
            df['office']= 'STATE SENATE'
        else:
            df['office']= 'STATE HOUSE'
        if 'state_house_12' in district:
            df['readme_check'] = 'TRUE'
        if 'recount' in district:
            df['stage']= 'GEN RECOUNT'
        else:
            df['stage']= 'GEN'
        if 'A' in district:
            df['magnitude'] = 1
        elif 'B' in district:
            df['magnitude'] = 1
        elif 'senate' in district:
            df['magnitude'] = 1
        else:
            df['magnitude'] = 2
        dictionary[district]= df
    return pd.concat(dictionary.values())
state_senate_df = collapse_all_districts(state_senate_filenames,senate_path)
state_house_df = collapse_all_districts(state_house_filenames,house_path)


# In[42]:


# from selenium import webdriver
# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# import time

# # scraping party info from website
# browser = webdriver.Chrome(executable_path="/Users/declanchin/Documents/chromedriver")
# url = 'https://electionresults.sd.gov/resultsSW.aspx?type=LEG&map=DIST'
# browser.get(url)
# cand_party = [i.text for i in browser.find_elements_by_class_name("display-results-box-d")]
# crosswalk = [i.split('\n') for i in cand_party]
# crosswalk = pd.DataFrame(crosswalk, columns = ['candidate', 'party_detailed'])
# crosswalk['candidate'] = crosswalk['candidate'].str.replace('\.','',regex=True).str.strip()
# crosswalk['party_detailed'] = crosswalk['party_detailed'].str.upper().str.replace('DEMOCRATIC','DEMOCRAT')
# crosswalk.to_csv('state_leg_candidate_party_crosswalk.csv',index=False)


# In[43]:


crosswalk = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/SD/state_leg_candidate_party_crosswalk.csv')
house_and_senate = pd.concat([state_house_df,state_senate_df])
house_and_senate['candidate'] = house_and_senate['candidate'].str.replace('SETH WILLIAM VAN"T HOF',"SETH WILLIAM VAN'T HOF")
crosswalk=crosswalk.merge(house_and_senate[['candidate','office']], on='candidate', how = 'left').drop_duplicates()
# two tim reeds, need to add office to differentiate for merge
crosswalk=crosswalk[~((crosswalk['candidate']=='TIMOTHY REED')&(crosswalk['party_detailed']=='DEMOCRAT')&(crosswalk['office']=='STATE HOUSE'))]
crosswalk=crosswalk[~((crosswalk['candidate']=='TIMOTHY REED')&(crosswalk['party_detailed']=='REPUBLICAN')&(crosswalk['office']=='STATE SENATE'))]
house_and_senate=house_and_senate.merge(crosswalk, on = ['candidate','office'], how = 'left')


# # wrapping up

# In[44]:


#concat all statewide and federal results
df=pd.concat([president,us_senate,us_house,public_utilities,measure_26,ammendment_a,ammendment_b,
                   state_supreme_court,house_and_senate])
#add county fips
county_fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv')
county_fips = county_fips[county_fips['state']=='South Dakota'].drop(columns='state')
df=df.merge(county_fips, on='county_name')
# add jurisdiction
df['jurisdiction_name']= df['county_name']
df['jurisdiction_fips'] = df['county_fips']
# add mode, district, magnitude, dataverse, year, stage, state, special, writein, date, office, readme_check
df['mode']='TOTAL'
df['year']= 2020
df['state'] = 'SOUTH DAKOTA'
df['special'] = 'FALSE'
df['writein'] = 'FALSE'
df['date']= '2020-11-03'
df['readme_check'] = df['readme_check'].fillna('FALSE')
# state codes
state_codes = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/merge_on_statecodes.csv')
state_codes = state_codes[state_codes['state']=='South Dakota']
state_codes['state'] = state_codes['state'].str.upper()
df=df.merge(state_codes, on='state')

# fix party_simplified issue
def get_party_simplified(x):
    if x in ['REPUBLICAN','DEMOCRAT','LIBERTARIAN','NONPARTISAN']: return x
    if x =='': return ''
    else: return 'OTHER'
df['party_simplified'] = df.party_detailed.apply(get_party_simplified)
# fix precinct
df['precinct'] = df['precinct'].str.upper().str.strip()

# reordering
df = df[['precinct', 'office', 'party_detailed', 'party_simplified', 'mode',
       'votes', 'county_name', 'county_fips', 'jurisdiction_name',
       'jurisdiction_fips', 'candidate', 'district', 'magnitude', 'dataverse',
       'year', 'stage', 'state', 'special', 'writein', 'state_po',
       'state_fips', 'state_cen', 'state_ic', 'date', 'readme_check']]
df.head()


# In[45]:


df.to_csv('2020-sd-precinct-general.csv',index=False, quoting=csv.QUOTE_NONNUMERIC)


# In[ ]:




