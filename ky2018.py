#!/usr/bin/env python
# coding: utf-8

# In[758]:


import pandas as pd
import numpy as np
import os
import csv
import re
pd.options.display.max_rows = 1500
pd.options.display.max_columns = 30


# In[759]:


def drop_duplicates_get_columns(df):
    df = df.loc[:,['race.id','race','candidates','party','county','precinct','type','votes']]
    df.columns = ['office.id','office','candidate','party_detailed','county_name','precinct','mode','votes']
    #str to upper
    df = df.applymap(lambda x:x.upper().strip() if type(x) == str else x) 
    #drop duplicates and empty rows for floating counties
    df=df[~(df['precinct']=='-1')]
    df['office'] = np.where(df['office'] == 'QUESTION',
                        df['office'] + ' - ' + df['office.id'].astype(str),
                        df['office'])
    return df


# In[760]:


def fix_candidate(x):
    x = x.replace('.','')
    if "  " in x: 
        x = x.replace('  ', ' ')
    if x == "MONTY O' HARA": return "MONTY O'HARA"
    if x == "Patricia'Pat'W SEIBER".upper(): return 'PATRICIA "PAT" W SEIBER'
    if x =='FOR': return 'YES'
    if x =='AGAINST': return 'NO'
    if x =='J B HINES': return 'JB HINES'
    if "/" in x: return x.split('/')[0].strip()
    if x =='WRITE-IN': return "WRITEIN"
    if "' " in x: return x.replace("' ",'" ').replace(" '",' "')
    if " '" in x: return x.replace("' ",'" ').replace(" '",' "')
    if "(" in x: return x.replace("(",'"').replace(")",'"')
    if x == 'NANCY J TATE': return "NANCY K TATE"
    if x == 'HOWARD TANKERSLY': return "HOWARD TANKERSLEY"
    else: return x


# In[761]:


def fix_district(x):
    if "COMMONWEALTH'S ATTORNEY" in x and "CIRCUIT" in x: return re.findall("\d+", x)[0].zfill(3)
    if x == 'COUNTY COMMISSIONER A DISTRICT': return 'A'
    # coodinate districts
    if ('DISTRICT' in x) and ('SCHOOL' not in x) and (("NORTH" in x) | ('SOUTH'  in x)| ('EAST'  in x)| ('WEST'  in x)| ('CENTRAL'  in x)):
        if 'SOIL' in x: return x.split(' ')[-1]
        if 'MAGISTERIAL' in x: return (x.split(' ')[1])
        else: return (x.split(' ')[-2])
    # schools with district
    if ('DISTRICT' in x) and (('SCHOOL' in x)|('EDUCATION' in x)) and (any(str.isdigit(i) for i in x)):
            return re.findall(r'\d+',x)[0]
    # district with division
    if (("DISTRICT" in x)&("DIVISION" in x)): return re.findall(r'\d+',x)[0].zfill(3) + ', DIVISION ' + re.findall(r'\d+',x)[1]
    # all other districts with numbers (missing "A")
    if (("DISTRICT" in x)|("DISTRCT" in x)) and (any(str.isdigit(i) for i in x)): return re.findall(r'\d+',x)[0].zfill(3)
    # get ward, numbers/words placed in middle and end
    if "WARD" in x: 
        location = x.split(' ').index('WARD')
        return x.split(' ')[location+1].zfill(3)
    #remaining circuit courts
    if ('CIRCUIT' in x) and ('DIVISION' not in x) and (any(str.isdigit(i) for i in x)): re.findall(r'\d+',x)[0].zfill(3)
    if ('CIRCUIT' in x) and ('DIVISION' in x) and (any(str.isdigit(i) for i in x)): return re.findall(r'\d+',x)[0].zfill(3) + ', DIVISION ' + re.findall(r'\d+',x)[1]
        # remaining DIVISION
    if ("DIVISION" in x) and (any(str.isdigit(i) for i in x)): return re.findall(r'\d+',x)[0].zfill(3)  
    else: return ""

def get_special(x):
    if "UNEXPIRED" in x: return 'TRUE'
    else: return "FALSE"


# In[762]:


#strips district from office field and adds to district. Same for circuit courts, divisions for School board
def fix_office_district(x):
    if ('DISTRICT' in x) and ('SCHOOL' not in x) and (("NORTH" in x) | ('SOUTH'  in x)| ('EAST'  in x)| ('WEST'  in x)| ('CENTRAL'  in x)):
        if 'SOIL' in x: return ' '.join(x.split(' ')[:-1])
        if 'MAGISTERIAL' in x: return (x.split(' ')[0])
        else: return ' '.join(x.split(' ')[:-2])
    # schools with district
    if ('DISTRICT' in x) and (('SCHOOL' in x)|('EDUCATION' in x)) and (any(str.isdigit(i) for i in x)):
            return 'MEMBER BOARD OF EDUCATION'
    # district with division
    if (("DISTRICT" in x)&("DIVISION" in x)): return x.split(',')[0]
    # all other districts with numbers
    if (("DISTRICT" in x)|("DISTRCT" in x)) and (any(str.isdigit(i) for i in x)): 
        if 'CONSTABLE' in x: return "CONSTABLE"
        if 'COUNTY COMMISSIONER' in x: return 'COUNTY COMMISSIONER'
        if 'JUSTICE OF THE PEACE' in x: return "JUSTICE OF THE PEACE"
        if 'LOUISVILLE METRO COUNCIL' in x: return 'LOUISVILLE METRO COUNCIL'
        if 'MAGISTRATE' in x: return 'MAGISTRATE'
        if 'URBAN COUNTY COUNCIL' in x: return 'URBAN COUNTY COUNCIL'
        if ('SCHOOL' in x) or ('EDUCATION') in x: return 'MEMBER BOARD OF EDUCATION'
        else: return x.split(',')[0]
    # get ward, numbers/words placed in middle and end
    if "WARD" in x: 
        if 'CITY COUNCIL CITY OF HOPKINSVILLE' in x: return 'CITY COUNCIL - HOPKINSVILLE'
        if 'CITY COUNCIL CITY OF SOMERSET' in x: return 'CITY COUNCIL - SOMERSET'
        if ('CITY COUNCIL' in x) and ('CITY OF MADISONVILLE' in x): return 'CITY COUNCIL - MADISONVILLE'
    #remaining circuit courts
    if ('CIRCUIT' in x) and ('DIVISION' not in x) and (any(str.isdigit(i) for i in x)): 
        if "COMMONWEALTH'S ATTORNEY" in x: return "COMMONWEALTH'S ATTORNEY"
        else: return x.split(',')[0]
    if ('CIRCUIT' in x) and ('DIVISION' in x) and (any(str.isdigit(i) for i in x)):
        if "CIRCUIT JUDGE 'FAMILY COURT'" in x: return "CIRCUIT JUDGE FAMILY COURT"
        else: return x.split(',')[0]
    # remaining DIVISION
    if ("DIVISION" in x) and (any(str.isdigit(i) for i in x)):
        if ('SCHOOL' in x) or ('EDUCATION') in x: return 'MEMBER BOARD OF EDUCATION'
    else: return x

def fix_office(x):
    if x=='US REPRESENTATIVE': return 'US HOUSE'
    if x=='STATE REPRESENTATIVE': return 'STATE HOUSE'
    if x=='US SENATOR': return 'US SENATE'
    if x=='STATE SENATOR': return 'STATE SENATE'
    if "UNEXPIRED" in x: return x.replace('(UNEXPIRED TERM)','').strip()
    if x in ['COUNTY JUDGE/EXECUTIVE','COUNTY JUDGE EXECUTIVE', 'COUNTY JUDGE / EXECUTIVE','COUNTY JUDGE EXE']:
        return 'COUNTY JUDGE EXECUTIVE'
    if "CITY COUNCIL" in x:
        if "BEREA" in x: return "CITY COUNCIL - BEREA"
        if "CITY OF" in x: return x.replace('CITY OF',"-")
        if "-" not in x: return "CITY COUNCIL - " + x.replace(' CITY COUNCIL',"")
    if "COUNCILMEMBER" in x: return "CITY COUNCIL - " + x.replace("CITY OF ",'').replace(' COUNCILMEMBER',"")
    if "CITY" in x and "COMMISSIONER" in x:
        if x == 'RICHMOND CITY COMMISSIONERS CITY OF RICHMOND': return "CITY COMMISSIONER - RICHMOND"
        if "CITY COMMISSIONERS" in x: return 'CITY COMMISSIONER - ' + x.replace('CITY COMMISSIONERS CITY OF ','')
        if x.startswith("CITY OF "): return 'CITY COMMISSIONER - ' + x.replace('CITY OF ','').replace(' COMMISSIONER',"")
        else: return 'CITY COMMISSIONER - ' + x.replace(" CITY COMMISSIONER","")
    if "MAYOR" in x:
        if 'MAYOR' == x: return x
        if x == 'MAYOR CITY OF ROCHESTER': return "MAYOR - ROCHESTER"
        if x == 'MAYOR CITY OF RICHMOND CITY OF RICHMOND': return "MAYOR - RICHMOND"
        if x == 'CLAY CITY MAYOR': return "MAYOR - CLAY"
        if x.startswith("MAYOR CITY OF"): return x.replace('CITY OF','-')
        if x.startswith("CITY OF "): return "MAYOR - " + x.replace('CITY OF ',"").replace(' MAYOR',"")
        else: return "MAYOR - " + x.replace(' MAYOR',"")
    if x == 'LOUISVILLE METRO COUNCIL': return "METRO COUNCIL - LOUISVILLE"
    if x == 'CORBIN INDEPENDENT': return 'MEMBER BOARD OF EDUCATION CORBIN INDEPENDENT SCHOOL DISTRICT'
    else: return x  


# In[763]:


def get_dataverse(x):
    if x == 'US HOUSE': return 'HOUSE'
    if x =='US SENATE': return 'SENATE'
    if x in ['STATE SENATE', 'STATE HOUSE','JUDGE OF THE COURT OF APPEALS','JUSTICE OF THE SUPREME COURT',
            'CONSTITUTIONAL AMENDMENT 1','CONSTITUTIONAL AMENDMENT 2',
            'ARE YOU IN FAVOR OF PROVIDING CONSTITUTIONAL RIGHTS TO VICTIMS OF CRIME, INCLUDING THE RIGHT TO BE TREATED FAIRLY, WITH DIGNITY AND RESPECT, AND THE RIGHT TO BE INFORMED AND TO HAVE A VOICE IN THE JUDICIAL PROCESS?',
            "COMMONWEALTH'S ATTORNEY"]: 
        return 'STATE'
    if 'CIRCUIT' in x: return 'STATE'
    if x=='REGISTERED VOTERS': return ''
    else: return 'LOCAL'


# In[764]:


# merge state codes, county fips, jurisdiction fips for any state
# takes in df (dataframe), name of state, case insensitive (string)

def merge_regional_codes(df, state_full):
    # add state column and state codes
    df['state'] = state_full.upper()
    state_codes = pd.read_csv('../../../help-files/merge_on_statecodes.csv')
    state_codes['state'] = state_codes['state'].str.upper()
    state_codes = state_codes[state_codes['state']==state_full.upper()]
    df=df.merge(state_codes, on='state')
    # add county codes
    fips = pd.read_csv("../../../help-files/county-fips-codes.csv")
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


# In[779]:


def get_party_detailed(x):
    if x == 'REP': return 'REPUBLICAN'
    if x == 'DEM': return 'DEMOCRAT'
    if x == 'IND': return 'INDEPENDENT'
    if x =='LIB': return "LIBERTARIAN"
    if x =='VET': return 'Veterans Party of America'.upper()
    if x =='AM': return 'AMERICAN'
    if x =='TEA': return "TEA"
    else: return ""

def fill_missing_parties():
    #creates dictionary with keys as candidates/office pairs with multiple parties, values as the non-blank party
    df['party_detailed'] = df['party_detailed'].fillna('')
    candidate_parties = df.groupby(['candidate','office'])['party_detailed'].unique()
    correct_pairing = dict()
    for (candidate, parties) in candidate_parties.iteritems():
        if (len(parties) > 1) and ("" in parties):
            parties = list(parties)
            parties.remove('')
            correct_pairing[candidate] = parties[0]        
    candidates=list(correct_pairing.keys())
    #loops through and assigns each candidate/office pair to nonblank party
    for candidate_office in candidates:
        df['party_detailed']=np.where((df['candidate']==candidate_office[0])&(df['office']==candidate_office[1]), 
                                      correct_pairing[candidate_office],
                                     df['party_detailed'])

def get_party_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','NONPARTISAN','LIBERTARIAN']: return x
    if x == "": return ""
    else: return "OTHER"


# In[781]:


######################### run all functions ####################################
df=pd.read_csv('../raw/KY2018_mostrecent.csv',low_memory=False)
df = drop_duplicates_get_columns(df)    
df.candidate = df.candidate.apply(fix_candidate)    
df['district'] = df.office.apply(fix_district)
df['district'] = df['district'].str.zfill(3).replace(['ONE','TWO', 'THREE', 'FOUR', 'FIVE', 'SIX',
                                         'SEVEN', 'EIGHT', 'NINE','TEN', 'ELEVEN', 'TWELVE','EASTERM','000'],
                                       ['001','002','003','004','005','006',
                                       '007','008','009','010','011','012','EASTERN','']) 

# add districts missing from raw data for commonwealth attorney
# via http://www.kycommonwealthattorneys.org/members.php
df.loc[(df['candidate'] == 'ARNOLD BRENT TURNER')&(df['office']=="COMMONWEALTH'S ATTORNEY"),
 'district'] = '031' 
df.loc[(df['candidate'] == 'EDISON G BANKS II')&(df['office']=="COMMONWEALTH'S ATTORNEY"),
 'district'] = '047' 
df.loc[(df['candidate'] == 'THOMAS B "TOM" WINE')&(df['office']=="COMMONWEALTH'S ATTORNEY"),
 'district'] = '030' 
    
df['special'] = df.office.apply(get_special)
df['office'] = df.office.apply(fix_office_district)
df['office'] = df.office.apply(fix_office)
df['dataverse'] = df.office.apply(get_dataverse)
df = merge_regional_codes(df, 'kentucky')
df['party_detailed'] = df.party_detailed.apply(get_party_detailed)
# only fills missing party if candidate and office name are the same
fill_missing_parties()
df.loc[df['office'].str.contains('JUDGE|COURT|JUSTICE'),'party_detailed'] = 'NONPARTISAN'
df['party_simplified'] = df.party_detailed.apply(get_party_simplified)

df['writein'] = 'FALSE'
df['year']= 2018
df['date']= '2018-11-06'
df['stage']='GEN'
df['magnitude']= 1
df['readme_check']= 'FALSE'
# state codes
df=df.fillna("")
######################### run all functions ####################################

df = df.loc[:,['precinct', 'office', 'party_detailed', 'party_simplified', 'mode',
       'votes', 'county_name', 'county_fips', 'jurisdiction_name',
       'jurisdiction_fips', 'candidate', 'district', 'magnitude', 'dataverse',
       'year', 'stage', 'state', 'special', 'writein', 'state_po',
       'state_fips', 'state_cen', 'state_ic', 'date', 'readme_check']].drop_duplicates()

df.to_csv('2018-ky-precinct-general-updated.csv', index=False,quoting=csv.QUOTE_NONNUMERIC)





