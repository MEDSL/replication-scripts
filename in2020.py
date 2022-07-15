# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 15:18:03 2021

@author: abguh
"""
import pandas as pd
import numpy as np
import os


path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/IN'
os.chdir(path)

df = pd.read_csv('raw/AllOfficeResults.csv')
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
    

df['readme_check'] = df['DataEntryLevelName'].apply(readme_locality)    
df['writein'] = df['NameonBallot'].apply(get_writein)
df['candidate']  = df['NameonBallot'].apply(fix_up)
df['dataverse'] = df['OfficeCategory'].apply(get_dataverse)
df['district'] = df['Office'].apply(get_district).apply(str)
df['district'] = df['district'].replace({'First': '001', 'Fourth': '004', 
                                'Eighth': '008', 'Fifth': '005', 'Ninth': '009', 
                                'Second': '002', 'Seventh': '007', 'Sixth':'006', 
                                'Third': '003'})
#if cell in JurisdictionName column is 'Indiana', put statewide for district
df.loc[df['JurisdictionName'] == 'Indiana', 'district'] = 'STATEWIDE'

                          
'''note'''
#for office column, will need to keep school board cells
#also need to keep circuit and superior court cells the same too 
#df.loc[df['Office'].str.contains('School Board'), 'OfficeCategory'] = df['Office']
df.loc[df['Office'].str.contains('Circuit'), 'OfficeCategory'] = df['Office']
df.loc[df['Office'].str.contains('Superior'), 'OfficeCategory'] = df['Office']

df['office'] = df['Office'].apply(schoolboard)
df['office'] = df['office'] + df['OfficeCategory']
df['office'] = df['office'].str.upper().replace({'PRESIDENTIAL ELECTORS FOR US PRESIDENT & VP': 'US PRESIDENT',
                                                         'US REPRESENTATIVE': 'US HOUSE', 
                                                         'GOVERNOR & LT. GOVERNOR': 'GOVERNOR',
                                                         'STATE REPRESENTATIVE': 'STATE HOUSE',
                                                         'STATE SENATOR': 'STATE SENATE'})

df['office'] = df['office'].apply(judge_names)
#print(sorted(df.OfficeCategory.unique()))

#df1 = df[df.Office.str.contains('Circuit')]    


df['state'] = 'Indiana' #need it like this to merge; CHANGE LATER
countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv")
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
print(af.Office.unique())

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

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df_final = df[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check","magnitude"]].copy()

df_final.to_csv("C:/Users/abguh/Desktop/urop/2020-precincts/precinct/IN/2020-in-precinct-general.csv", index = False)


'''CHECKS'''
'''
for col in df_final:
    print(col)
    print("")
    print(sorted(df_final[col].unique()))
    print("\n\n----------------\n\n")

#check dataverse
for i in ["PRESIDENT","SENATE", "HOUSE", "STATE", "LOCAL"]:
    print(i)
    print(sorted(df['office'][df.dataverse==i].unique()))
    print("\n------------------\n")

print("number of columns/variables:", len(df_final.columns)) #should be 24
print("columns are: ", df_final.columns)



df1 = df[df.DataEntryLevelName == 'Locality']
count = 0
localityList = []
for county in df['ReportingCountyName'].unique():
    df2 = df[df.ReportingCountyName == county]
    #df3 = df2[df2.Office == 'US President & Vice President']

    df4 = df2[df2.DataEntryLevelName == 'Precinct']
    df5 = df2[df2.DataEntryLevelName == 'Locality']

    pSum = sum(df4['TotalVotes'])
    lSum = sum(df5['TotalVotes'])
    print(county, ": ",pSum, lSum)
    if pSum == 0:   #if they report by locality
        count = count+1
        localityList.append(county)
    elif lSum != 0: print(county)

print(count)  #48 counties that report only by locality
print(len(df1.ReportingCountyName.unique())) #51 counties have locality entries
for county in df1.ReportingCountyName.unique(): #all counties that have locality entries
    if county not in localityList:   #if they don't report it by locality but have locality entries
        print(county)

df6 = df1[df1.ReportingCountyName == 'Shelby']

There are three counties that report all by precinct, but have locality
entries that are all zero in the votes column, and those are Boone, Delaware, Shelby. 
'''