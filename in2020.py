#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import os
import time


path = './'
os.chdir(path)

VERBOSE = False
HIGHLY_VERBOSE = False

df = pd.read_csv(path+'raw/AllOfficeResults.csv')
print(df.columns)
'''
upon looking @ data, it looks like DataEntryJurisdictionName is the precinct name
ReportingCountyName is the county name
DataEntryJurisdictionName is the precinct name
DataEntryLevelName has both 'precinct' and 'locality'

'''
#print(sorted(df['DataEntryLevelName'].unique()))
#print(len(df[df['DataEntryLevelName']=='Precinct']))
#print(sorted(df['PoliticalParty'].unique()))

#Uncomment to verify that near-duplicates are present in the raw data
#print(f"{sum(df.drop("votes", axis=1).duplicated())} NEAR DUPS IN RAW DATA")

df = df.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x)==str else x)
df['precinct'] = df['DataEntryJurisdictionName'].str.upper()
df['county_name'] = df['ReportingCountyName'].str.upper()

df['party_detailed'] = df['PoliticalParty'].replace({'Republican' : 'REPUBLICAN',
                                       'Democratic' : 'DEMOCRAT',
                                       'Libertarian' : 'LIBERTARIAN',
                                       'Green': 'GREEN',
                                       'American Solidarity': 'AMERICAN SOLIDARITY',
                                       'Independent': 'INDEPENDENT',
                                       'Non Partisan': 'NONPARTISAN',
                                       'Other': 'OTHER'})

df['party_simplified'] = df['PoliticalParty'].replace({'Republican' : 'REPUBLICAN',
                                       'Democratic' : 'DEMOCRAT',
                                       'Libertarian' : 'LIBERTARIAN',
                                       'Green': 'OTHER',
                                       'American Solidarity': 'OTHER',
                                       'Independent': 'OTHER',
                                       'Non Partisan': 'NONPARTISAN',
                                       'Other': 'OTHER'})
#print(len(df['ReportingCountyName'].unique())) #should be 92, since 92 counties in IN
#df['county'] = df['ReportingCountyName'].str.upper()

#print(sorted(df['Office'].unique()))
#print(sorted(df['OfficeCategory'].unique()))


def get_writein(x):
    if 'W/I' in x: return 'TRUE'
    else: return 'FALSE'
    
def fix_up(x):
    x = x.replace('.', '').replace(',', '').replace('(', '"').replace(')', '"')
    if '&' in x: return x[:x.find('&')-1].upper()
    elif 'W/I' in x: return x[:-5].upper()
    elif '-' in x: 
        if x[x.find('-')-1] == ' ': x = x[:x.find('-')-1] + x[x.find('-'):]
        if x[x.find('-')+1] == ' ': return x[:x.find('-')+1] + x[x.find('-')+2:]
        else: return x.upper()
    elif 'Edward " Michael' in x: return 'EDWARD MICHAEL'
    else: return x.upper()

def get_district(x):
    if 'United States Representative' in x:
        return x[30:-8].strip()
    elif 'State Representative' in x:
        return x[-3:]
    elif 'District 1-2' in x:
        return x[-3:]
    elif 'District' in x and x[-8] != 'D':
        start = x.find('District') +9
        if x[start].isnumeric():
            return x[start:start+2].upper().strip()
        elif x[start] == '#': return x[start+1]
        elif x[start] == x[-1]: return x[-1] #if its a lettered district
        else: return ''      
    elif 'Ward' in x and x[-8:] != 'Township':
        return x[x.find('Ward'):].upper()
    #elif 'Seat' in x and x[-5] != 'S': #to avoid the ones ending with '1 Seat'
    #    return x[x.find('Seat'):]
    elif 'Dst' in x:
        return x[-2:].strip()
    elif 'Quadrant' in x:
        return x[x.find(',')+2:].upper()
    else: return ''
    
def get_dataverse(x):   #note: IN had no US senate election in 2020
    if 'Presidential' in x:
        return 'PRESIDENT'
    elif x == "US Representative":
        return "HOUSE"
    elif x in ['State Senator', 'State Representative', 'Attorney General', 
               'Governor & Lt. Governor']:
        return "STATE"
    else: # all others are local
        return "LOCAL"

def readme_locality(x):
    if x == 'Locality': return 'TRUE'
    else: return 'FALSE'

def judge_names(x):
    if 'CLERK' not in x and 'CIRCUIT' in x:
            return (x[13:x.find('COURT')+5]+' JUDGE' + x[x.find('COURT')+5:]).replace('JUDICIAL ','')
    elif 'SUPERIOR COURT' in x:
        return x[13:x.find('COURT')+5] + ' JUDGE'+ x[x.find('COURT')+5:]  
    else: return x

def schoolboard(x):
    if 'School Board' in x:
        return x[:x.find('School Board')].upper()
    else: return x
    

df['readme_check'] = "TRUE"#df['DataEntryLevelName'].apply(readme_locality)    
df['writein'] = df['NameonBallot'].apply(get_writein)
df['candidate']  = df['NameonBallot'].apply(fix_up)
df['dataverse'] = df['OfficeCategory'].apply(get_dataverse)
#df['district'] = df['Office'].apply(get_district).apply(str)
#df['district'] = df['district'].replace({'First': '001', 'Fourth': '004', 
#                                'Eighth': '008', 'Fifth': '005', 'Ninth': '009', 
#                                'Second': '002', 'Seventh': '007', 'Sixth':'006', 
#                                'Third': '003'})
#if cell in JurisdictionName column is 'Indiana', put statewide for district
df.loc[df['JurisdictionName'] == 'INDIANA', 'district'] = 'STATEWIDE'


###############################################################################
# Office handling
###############################################################################
df['Office'] = df['Office'].str.upper()

#Split out districts
names_to_nums = {"FIRST": "001",\
                "SECOND": "002",\
                "THIRD": "003",\
                "FOURTH": "004",\
                "FIFTH": "005",\
                "SIXTH": "006",\
                "SEVENTH": "007",
                "EIGHTH": "008",\
                "NINTH": "009",\
                "OF 1ST": "001",\
                "OF 2ND": "002",\
                "OF 3RD": "003"
}
def GetLoc(currOffice, label):
    _loc = currOffice.find(label)
    if _loc != -1:
        _distStart = _loc
    return(_loc)

for i in range(len(df)):
    currOffice = df.Office[i]
    if "MIDDLE DISTRICT" in currOffice:
        df.at[i, 'Office'] = currOffice.replace('MIDDLE DISTRICT', 'DISTRICT MIDDLE')
    elif "SOUTHERN DISTRICT" in currOffice:
        df.at[i, 'Office'] = currOffice.replace('SOUTHERN DISTRICT', 'DISTRICT SOUTHERN')
for i in range(len(df)):
    currOffice = df.Office[i]
    if "DISTRICT" in df.Office[i]:
        if any(name in currOffice for name in names_to_nums.keys()):
            distStart = -1
            for label in names_to_nums.keys():
                distStart = GetLoc(currOffice = currOffice, label = label)
                if distStart != -1:
                    break
            df.at[i, 'district'] = names_to_nums[label].replace("OF ","")
            df.at[i, 'Office'] = currOffice[:distStart]
            df.at[i, 'Office'] = df.at[i,'Office'].replace(', ','')
        else:
            distStart = currOffice.find("DISTRICT")
            distEnd = distStart + len("DISTRICT ")
            dist = currOffice[distEnd:]
            pureOffice = currOffice[:distStart]
            #Write this district value to the district column
            df.at[i, 'district'] = dist
            #Remove district information from the office variable
            df.at[i, 'Office'] = pureOffice
            df.at[i, 'Office'] = df.at[i,'Office'].replace(', ','')
        if VERBOSE:
            print(i, df.Office[i], ";", df.district[i])
            if HIGHLY_VERBOSE:
                time.sleep(0.0025)
    if 'AT LARGE' in df.Office[i]:
        df.at[i, 'district'] = 'AT LARGE'
        df.at[i, 'Office'] = df.Office[i].replace(', AT LARGE','')
        df.at[i, 'Office'] = df.Office[i].replace(' AT LARGE','')
        df.at[i, 'Office'] = df.Office[i].replace('AT LARGE','')

#Correct common typos
df.Office = df.Office.str.replace("COMMISION","COMMISSION")

def CheckLocal(office):
    _terms = ["SCHOOL", "TOWN", "TREASURE", "BOARD", "COUNCIL", "COMMISSION",\
              "LAKE", "CORONER", "SURVEYOR", "RECORDER", "AUDITOR", "CLERK",\
              "JUDGE", "COURT", "LCSC", "MSD"]
    _local = False
    for term in _terms:
        if term in office:
            _local = True
    return(_local)

if VERBOSE:
    print(f"MAJOR OFFICE NAMES: {[i for i in df['Office'].unique() if not CheckLocal(i)]}")

df['office'] = df['Office'].replace({\
        'US PRESIDENT & VICE PRESIDENT': 'US PRESIDENT',\
        'UNITED STATES REPRESENTATIVE': 'US HOUSE',\
        'GOVERNOR & LT. GOVERNOR': 'GOVERNOR',\
        'STATE REPRESENTATIVE': 'STATE HOUSE',\
        'STATE SENATOR': 'STATE SENATE'})

#Now generate the dataverse values
dataverse_map = {"US PRESIDENT": "PRESIDENT",\
                 "US SENATE": "SENATE",\
                 "US HOUSE": "HOUSE"}
df.dataverse = df.office.apply(lambda _: dataverse_map.get(_))
#All non-federal races are given the value "state" in 2020 data
df.loc[df.dataverse.isnull(), 'dataverse'] = 'STATE'

df['state'] = 'Indiana' #need it like this to merge; CHANGE LATER
countyFips = pd.read_csv(path+"../../help-files/county-fips-codes.csv")
df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df['county_fips'] = df['county_fips'].apply(str).str.pad(5, side='left', fillchar='0')
df['jurisdiction_fips'] = df['county_fips']
df['state'] = df['state'].replace("Indiana", "INDIANA") #now can change 'state' column  back to NC
#print(sorted(df['county_fips'].unique()))   
#print(len(df['county_fips'].unique())) #this should be 92


df['mode'] = 'TOTAL'
df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'IN'
df['state_fips'] = '18'
df['state_cen'] = '32'
df['state_ic'] = '22'
df['date'] = '2020-11-03'
df['jurisdiction_name'] = df['ReportingCountyName'].str.upper()
df['special'] = 'FALSE'
df['votes'] = df['TotalVotes']
df['magnitude'] = int(1)

af = df[df.Office.str.contains('School Board')]
#print(af.Office.unique())

df.loc[df.Office == 'Marion Perry Township Public School Board, At Large','magnitude'] = 3
df.loc[df.Office == 'Marion Pike Township School Board, At Large','magnitude'] = 4
df.loc[df.Office == 'Marion Warren Township School Board, At Large','magnitude'] = 4
df.loc[df.Office == 'Marion Wayne Township Public School Board, At Large','magnitude'] = 3
df.loc[df.Office == 'Marion Decatur Township School Board, At Large','magnitude'] = 2



def get_magnitude(magnitudes):
    offices = df.Office.unique()
    for x in offices:
        af = df[df.Office == x]
        winners = af[af.Winner == 'Yes']
        
        num_yes = len(winners['NameonBallot'].unique())
        magnitudes = magnitudes.append({'Office':x,'magnitude':num_yes}, ignore_index = True)
    return magnitudes
'''
magnitudes = pd.DataFrame(columns = ['Office, magnitude'])
magnitudes = get_magnitude(magnitudes)

df = pd.merge(df, magnitudes, how = 'left', on='Office')
'''

#Drop exact duplicates: there is only 1, and it has 0 votes
df=df.applymap(lambda x: x.strip() if type(x)==str else x)

COUNTIES_TO_DROP = ["BENTON","CLAY","DAVIESS","DEARBORN","DUBOIS","FAYETTE","FLOYD","FOUNTAIN","GREENE","HANCOCK","HENDRICKS","JACKSON","JASPER","JAY","LAPORTE","LAWRENCE","MARSHALL","MONTGOMERY","MORGAN","NEWTON","NOBLE","ORANGE","OWEN","PARKE","PERRY","PULASKI","RANDOLPH","RIPLEY","SCOTT","SPENCER","ST. JOSEPH","TIPTON","STARKE","SWITZERLAND","TIPPECANOE","VIGO","WARREN","WARRICK","WASHINGTON"]

df = df[~df['county_name'].isin(COUNTIES_TO_DROP)]

df.drop(df.columns[0:13], axis=1, inplace = True) 

df['candidate'] = df['candidate'].str.replace(r'ELIZABETH "BETH" J KEENEY','ELIZABETH J "BETH" KEENEY')
df['candidate'] = df['candidate'].str.replace(r'GREGORY "GREG" A HOLE','GREGORY A "GREG" HOLE')
df['candidate'] = df['candidate'].str.replace(r'LESLIE "LES" C SHIVELY','LESLIE C "LES" SHIVELY')
df['candidate'] = df['candidate'].str.replace(r'MURIELLE "ELLIE" S WEBSTER BRIGHT','MURIELLE S "ELLIE" WEBSTER BRIGHT')
df['candidate'] = df['candidate'].str.replace(r'RANDALL "RANDY" D DECKER','RANDALL D "RANDY" DECKER')
df['candidate'] = df['candidate'].str.replace(r'RONALD "RON" H WEST','RONALD H "RON" WEST')
df['candidate'] = df['candidate'].str.replace(r'TIMOTHY "TIM" L WHITE','TIMOTHY L "TIM" WHITE')

df['candidate'] = df['candidate'].str.replace(r'BRITTANI M RIGGS "FLOWERS"','BRITTANI M RIGGS (FLOWERS)')
df['candidate'] = df['candidate'].str.replace(r'Laura L Stieneker-Taylo','LAURA L STIENEKER-TAYLO')
df['candidate'] = df['candidate'].str.replace(r'MICHAEL D DANT "MIKE"','MICHAEL "MIKE" D DANT')
df['candidate'] = df['candidate'].str.replace(r'Melinda Hallgarth-Klopp','MELINDA HALLGARTH-KLOPP')

df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check","magnitude"]].copy()

#Handle the one exact duplicate
df_final = df_final.drop(140819)
#The near-duplicates all have 0 votes
#df_final.loc[[i for i in range(140820,140920)], ["precinct","candidate","votes"]].to_csv("near_dups.csv")
if HIGHLY_VERBOSE:
    print(sum(df_final.drop("votes", axis=1).duplicated()))
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140798])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140802])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140806])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140810])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140814])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140822])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
df_final = df_final.drop([140826])
if HIGHLY_VERBOSE:
    print(df_final[df_final.drop("votes", axis=1).duplicated(keep=False)])
    #Make sure no real vote totals were dropped from the race that had all the near-duplicates
    df_final[(df.office == "CENTERVILLE-ABINGTON SCHOOL BOARD")].to_csv("near_dup_test.csv")

df_final = df_final.reset_index()
df_final.drop(df_final.columns[0], axis=1, inplace = True) 

#Some scattered numerical districts remain unpadded with no regularity. Just
# handle them manually.
UNPADDED = ["02","03","05","07","08","09","1","11","12","13","14","15","16",\
            "18","2","20","24","28","3","30","32","33","34","35","36","37",\
            "4","40","42","44","5","50","6","7"]
df_final.district = df_final.district.str.replace('#','')
for i in range(len(df_final)):
    currDist = df_final['district'][i]
    if currDist in UNPADDED:
        df_final.at[i, 'district'] = currDist.zfill(3)
        if HIGHLY_VERBOSE:
            print(currDist, df_final.district[i])
            time.sleep(0.0005)

print(df_final.district.unique())

df_final.to_csv("in20_20221020.csv", index=False)




