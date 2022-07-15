# -*- coding: utf-8 -*-
"""
Code adapted from AL 2020
"""

import pandas as pd
import os
import numpy as np
import re

path = '/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/AL/raw'
os.chdir(path)

# these counties have races for BOE where there are multiple seats up for election but no
# info to differentiate them (no district number). Leads to duplicates for WRITEIN, UNDERVOTES, OVERVOTES.
# Thus, we must add this code so as not to create duplicates. 
dups = ['MONTGOMERY', 'MADISON', 'MARSHALL', 'ESCAMBIA', 'TALLAPOOSA',
       'CLEBURNE', 'TUSCALOOSA', 'MARENGO', 'PICKENS', 'COLBERT',
       'HOUSTON', 'TALLADEGA', 'CULLMAN', 'RANDOLPH', 'BALDWIN',
       'FRANKLIN', 'FAYETTE','LAWRENCE', 'CRENSHAW','CHAMBERS', 'WASHINGTON']

df_final = []
files = [i for i in os.listdir() if '.xls' in i]
for file in files:
  df = pd.read_excel(file)
  df = df.replace(np.nan, '0', regex = True).replace('_','', regex = True)
  county=file[13:-4].upper()
  # certain offices are duplicated in county results (not differentiated by a district code)
  # creating a code to differentiate to prevent near duplicates
  if county in dups:
      count=list(df.loc[(df['Contest Title'].str.contains('COUNTY BOARD OF EDUCATION')) & 
                        (df['Contest Title'].str.contains('MEMBER'))]['Candidate'].str.strip()).count('Under Votes')
      df.loc[(df['Contest Title'].str.contains('COUNTY BOARD OF EDUCATION')) & 
             (df['Contest Title'].str.contains('MEMBER')) &
             (df['Candidate'].str.strip()=='Under Votes'),'dup_code']=np.arange(1,count+1).astype(str)
      df.loc[(df['Contest Title'].str.contains('COUNTY BOARD OF EDUCATION'))&
             (df['Contest Title'].str.contains('MEMBER')),'dup_code'] = df.loc[(df['Contest Title'].str.contains('COUNTY BOARD OF EDUCATION'))&(df['Contest Title'].str.contains('MEMBER')),'dup_code'].bfill()
      df['dup_code'] = df['dup_code'].fillna('')
  else:
      df['dup_code'] = ''
  df = pd.melt(df, id_vars = ['Contest Title','Party', 'Candidate','dup_code'], var_name = 'precinct', value_name = 'votes')
  df['county_name'] = county
  df['mode'] = 'TOTAL'
  df.votes = df.votes.replace('', '0', regex = True).astype(int)
  df.loc[df.precinct == 'ABSENTEE', 'mode'] = 'ABSENTEE'
  df.loc[df.precinct == 'PROVISIONAL', 'mode'] = 'PROVISIONAL'
  df.precinct = df.precinct.apply(lambda x: 'COUNTY FLOATING' if x == 'ABSENTEE' or x=='PROVISIONAL' else x)
  df_final = df_final + [df]
df_final = pd.concat(df_final).astype(str).applymap(lambda x: x.strip().upper() if type(x)==str else x)
df_final['votes'] = df_final['votes'].astype(int)

#print(sorted(df_final['Contest Title'].unique()))

def get_district(x):
    x = x.replace('NO. ', '')
    if 'CONGRESSIONAL' in x: return x[x.find('CONGRESS')-4].zfill(3)
    if 'CIRCUIT COURT' in x: 
        return re.findall('\d+',x)[0].zfill(3) + ', PLACE ' +re.findall('\d+',x)[1]
    if 'CIRCUIT JUDGE' in x:
        return re.findall('\d+',x)[0].zfill(3) + ', PLACE ' +re.findall('\d+',x)[1]
    elif ('RUSSELL COUNTY CONSTABLE' in x) and ('PLACE' in x):
        return re.findall('\d+', x)[0].zfill(3) + ', PLACE ' + re.findall('\d+', x)[1]
    elif 'MEMBER ST. CLAIR COUNTY BOARD OF EDUCATION' in x:
        return x.replace('MEMBER ST. CLAIR COUNTY BOARD OF EDUCATION ','')
    elif 'MEMBER ST. CLAIR COUNTY BD OF EDUCATION' in x:
        return x.replace('MEMBER ST. CLAIR COUNTY BD OF EDUCATION ',"")
    elif 'PLACE' in x: return x[x.find('PLACE'):]
    elif 'CONSTABLE' in x:
        if 'PLACE' in x: 
            #print(x)
            return x[x.find('DISTRICT'):]
        if 'PRECINCT' in x: return x[x.find('PRECINCT'):]
        elif 'DISTRICT' in x: 
           return x[x.find('DISTRICT')+9:x.find('DISTRICT')+11].strip().zfill(3)
        elif 'BEAT' in x: return x[x.find('BEAT'):]
    elif 'LIMESTONE COUNTY COMMISSION, DIST' in x:
        return x[-1].zfill(3)
    elif ('DISTRICT' in x) and ('DISTRICT COURT' not in x):
        if len(re.findall('\d+',x))>0:
            return re.findall('\d+',x)[0].zfill(3)
        else: return ""
    elif 'DIST.' in x: return re.findall('\d+',x)[0].zfill(3)
    elif 'JUDICIAL PL' in x: return re.findall('\d+',x)[0].zfill(3) + ', PLACE ' +re.findall('\d+',x)[1]
    elif "PL " in x: return re.findall('\d+',x)[0].zfill(3)
    elif ("AT-LARGE" in x) or ("AT LARGE" in x): return "AT-LARGE"
    elif x in ['GOVERNOR', 'LIEUTENANT GOVERNOR',
       'ATTORNEY GENERAL', 'CHIEF JUSTICE OF THE SUPREME COURT',
       'STATE TREASURER', 'COMMISSIONER OF AGRICULTURE AND INDUSTRIES',
       'SECRETARY OF STATE', 'STATE AUDITOR',
       'PROPOSED STATEWIDE AMENDMENT NUMBER ONE (1)',
       'PROPOSED STATEWIDE AMENDMENT NUMBER TWO (2)',
       'PROPOSED STATEWIDE AMENDMENT NUMBER THREE (3)',
       'PROPOSED STATEWIDE AMENDMENT NUMBER FOUR (4)']: return "STATEWIDE"
    else: return ''        

def fix_office(x):
    if 'CONSTABLE' in x: return 'COUNTY CONSTABLE'
    if 'STATE BOARD OF EDUCATION' in x: return 'STATE BOARD OF EDUCATION'
    elif 'MEMBER' in x and 'COMMISSION' in x: 
        return 'COUNTY COMMISSION MEMBER'
    elif 'SUPERINTENDENT' in x: return 'COUNTY BOARD OF EDUCATION SUPERINTENDENT'
    elif 'MEMBER' in x and 'COMMISSION' not in x: 
        return 'COUNTY BOARD OF EDUCATION MEMBER'
    elif 'COUNTY BOARD OF EDUCATION' in x: return "COUNTY BOARD OF EDUCATION MEMBER"
    elif 'DISTRICT COURT' in x: return 'DISTRICT COURT JUDGE'
    elif ('CIRCUIT COURT' in x) or ('CIRCUIT JUDGE' in x): return 'CIRCUIT COURT JUDGE'
    elif 'ASSOCIATE JUSTICE' in x: return 'SUPREME COURT ASSOCIATE JUSTICE'
    elif 'CIVIL APPEALS' in x: return 'COURT OF CIVIL APPEALS JUDGE'
    elif 'CRIMINAL APPEALS' in x: return 'COURT OF CRIMINAL APPEALS JUDGE'
    elif 'UNITED STATES REPRESENTATIVE' in x: return 'US HOUSE'
    elif 'STATE REPRESENTATIVE' in x: return "STATE HOUSE"
    elif 'STATE SENATOR' in x: return 'STATE SENATE'
    elif 'CHAIRMAN' in x:
        if 'EDUCATION' not in x: return 'COUNTY COMMISSION CHAIRMAN'
        else: return 'COUNTY BOARD OF EDUCATION CHAIRMAN'
    elif 'PUBLIC SERVICE COMMISSION' in x: return 'PUBLIC SERVICE COMMISSION'
    elif 'JUDGE OF PROBATE' in x: return "JUDGE OF PROBATE"
    elif "DEPUTY CIRCUIT CLERK" in x: return x
    elif 'CIRCUIT CLERK' in x: return 'CIRCUIT CLERK'
    elif 'COUNTY SHERIFF' in x: return 'COUNTY SHERIFF'
    elif 'COUNTY CORONER' in x: return 'COUNTY CORONER'
    elif 'COUNTY TAX ASSESSOR' in x: return "COUNTY TAX ASSESSOR"
    elif 'COUNTY TAX COLLECTOR' in x: return 'COUNTY TAX COLLECTOR'
    elif 'COUNTY LICENSE COMMISSIONER' in x: return "COUNTY LICENSE COMMISSIONER"
    elif 'COUNTY COMMISSION' in x and "PRESIDENT" in x: return "COUNTY COMMISSION PRESIDENT"
    elif x == 'STRAIGHT PARTY': return 'STRAIGHT TICKET'
    elif x == 'DISTRICT ATTORNEY, 10TH JUDICIAL CIRCUIT - BIRMINGHAM DI': return "DISTRICT ATTORNEY - BIRMINGHAM"
    else: return x
    
def fix_candidate(x):
    x = x.upper().replace('.','').replace('(','"').replace(')','"').replace(',','').replace(" '",' "').replace("' ",'" ')
    if 'STRAIGHT PARTY' in x: return 'STRAIGHT TICKET'
    if x == 'WRITE-IN': return 'WRITEIN'
    if ("STATEWIDE AMENDMENT" in x) and ("YES" in x): return "YES"
    if ("STATEWIDE AMENDMENT" in x) and ("NO" in x): return "NO"
    if ('NO - LOCAL AMENDMENT' in x): return "NO"
    if ('YES - LOCAL AMENDMENT' in x): return "YES"
    if x == 'LA TOYA ""MI-MI"" PELT': return 'LA TOYA "MI-MI" PELT'
    if x == '"COACH" DON JONES': return 'DON "COACH" JONES'
    if x == '"DEBRA" DEBBIE HOLLEY': return 'DEBRA "DEBBIE" HOLLEY'
    if "LIBERTARIAN" in x: return "LIBERTARIAN"
    if "DEMOCRAT" in x: return "DEMOCRAT"
    if "REPUBLICAN" in x: return "REPUBLICAN"
    return x

def get_dataverse(x):
    if 'BALLOTS CAST' in x: return ''
    if x == 'US PRESIDENT': return 'PRESIDENT'
    if x == 'US HOUSE': return 'HOUSE'
    if x == 'US SENATE': return 'SENATE'
    if x == 'STRAIGHT TICKET': return ''
    if x == 'REGISTERED VOTERS - TOTAL': return ''
    if x in ['GOVERNOR', 'LIEUTENANT GOVERNOR',
       'ATTORNEY GENERAL', 'CHIEF JUSTICE OF THE SUPREME COURT',
       'STATE TREASURER', 'COMMISSIONER OF AGRICULTURE AND INDUSTRIES',
       'SECRETARY OF STATE', 'STATE AUDITOR',
       'PROPOSED STATEWIDE AMENDMENT NUMBER ONE (1)',
       'PROPOSED STATEWIDE AMENDMENT NUMBER TWO (2)',
       'PROPOSED STATEWIDE AMENDMENT NUMBER THREE (3)',
       'PROPOSED STATEWIDE AMENDMENT NUMBER FOUR (4)',
       'STATE SENATE', 'STATE HOUSE',
       'CIRCUIT COURT JUDGE','PUBLIC SERVICE COMMISSION',
       'SUPREME COURT ASSOCIATE JUSTICE','COURT OF CIVIL APPEALS JUDGE',
       'COURT OF CRIMINAL APPEALS JUDGE','STATE BOARD OF EDUCATION']: return 'STATE'
    else: return 'LOCAL'

df_final.county_name = df_final.county_name.replace({'STCLAIR': 'ST. CLAIR'})
df_final['district'] = df_final['Contest Title'].apply(get_district).replace('  ', ' ', regex = True)
# now adding dup_code to district field to differentiate
df_final['district'] = np.where(df_final['dup_code']!="", df_final['dup_code'].str.zfill(3), df_final['district'])


df_final['office'] = df_final['Contest Title'].apply(fix_office).str.replace(',','').str.replace('  ',' ',regex=True)
df_final['candidate'] = df_final.Candidate.apply(fix_candidate)
df_final['candidate'] = df_final['candidate'].str.replace('\s+',' ', regex=True)
df_final['party_detailed'] = df_final.Party.replace({'DEM': 'DEMOCRAT','REP':'REPUBLICAN',
                                                     'LIB': 'LIBERTARIAN','IND':'INDEPENDENT', 'NON': 'NONPARTISAN'})
df_final['party_simplified'] = df_final.party_detailed.replace({'INDEPENDENT': 'OTHER'})
df_final['dataverse'] = df_final.office.apply(get_dataverse)
df_final['state'] = 'Alabama'
countyFips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/county-fips-codes.csv").astype(str)
df_final = pd.merge(df_final, countyFips, on = ['state','county_name'],how = 'left')
df_final.county_fips = df_final.county_fips.astype(str).str.upper().str.zfill(5)
df_final['jurisdiction_fips'] = df_final.county_fips

df_final.state = df_final.state.str.upper()
# df_final['mode'] = 'TOTAL'
df_final['year'] = 2018
df_final['stage'] = 'GEN'
df_final['state_po'] = 'AL'
df_final['state_fips'] = '1'
df_final['state_cen'] = '63'
df_final['state_ic'] = '41'
df_final['date'] = '2018-11-06'
df_final['special'] = np.where(df_final['office'].str.contains('SPECIAL'), "TRUE",'FALSE')
df_final['writein'] = 'FALSE'
df_final['readme_check'] = np.where(df_final['county_name'].isin(['RUSSELL',"DALLAS",'CHILTON']), "TRUE",'FALSE')
df_final['jurisdiction_name'] = df_final.county_name
df_final.loc[df_final.candidate == 'WRITEIN', 'writein'] = 'TRUE'
df_final.loc[df_final.candidate == 'WRITEIN', 'party_simplified'] = ''
df_final.loc[df_final.candidate == 'WRITEIN', 'party_detailed'] = ''

df_final['county_name'] = df_final['county_name'].str.replace('\.','',regex=True)
df_final['jurisdiction_name'] = df_final['jurisdiction_name'].str.replace('\.','',regex=True)
#editing this to set magnitude == 0 for registered/ballots cast
#in accordance with the precinct readme. Declan Chin 3/30/21
def magnitude(cand, office):
    if cand in ['BALLOTS CAST - BLANK', 'BALLOTS CAST - TOTAL', 'REGISTERED VOTERS - TOTAL',
             'STRAIGHT TICKET']: return 0
    if office == 'STRAIGHT TICKET': return 0
    else: return 1
    
df_final['magnitude'] = df_final.apply(lambda x: magnitude(x['candidate'], x['office']), axis=1)


df_final = df_final[~((df_final['candidate']=='WRITEIN')&(df_final['votes']==0))].copy()

df_final = df_final[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check", 'magnitude']].copy()

df_final.to_csv("../2018-al-precinct-general-updated.csv", index = False)