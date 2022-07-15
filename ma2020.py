# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 11:33:39 2021

@author: abguh
"""
import pandas as pd
import os
import numpy as np

path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/MA/raw'
os.chdir(path)
datasets = [pd.read_csv(file) for file in os.scandir() if os.path.isfile(os.path.join(path,file))]

df_2018 = pd.read_csv('C:/Users/abguh/Desktop/urop/2020-precincts/precinct/MA/2018-ma-precinct.txt', delimiter = ',')
town_county = df_2018[['jurisdiction', 'county']].drop_duplicates() #juridiction to county names
df_final = pd.DataFrame()
df_nan = pd.DataFrame()
for i, dataset in enumerate(datasets[2:-1]): #all house & senate
    df = dataset.iloc[:,:-1] #replace(np.nan, '', regex = True) #exclude the Total Votes column
    parties = df.iloc[0:1, 3:].replace(np.nan, '', regex = True).T #get party info
    df = df.iloc[1:-1,:] #remove party info
    
    df = pd.melt(df, id_vars=['City/Town', 'Ward','Pct'], var_name = 'candidate', value_name = 'votes')
       
    df = pd.merge(df, parties, left_on = 'candidate', right_index = True).rename(columns = {0:'party_detailed'})
    
    if i == 9: #if it's senate data
        df['office'] = 'US SENATE'
        df['dataverse'] = 'SENATE'
        df['district'] = ''
        
    else: 
        df['office'] = 'US HOUSE'
        df['district'] = str(i+1).zfill(3)
        df['dataverse'] = 'HOUSE'
    df['special'] = 'False'
    df['date'] = '2020-11-03'
    df['stage'] = 'GEN'
    df['readme_check'] = 'FALSE'
    df_nan = pd.concat([df_nan, df[df.isnull()]])
    
    df.votes = df.votes.replace(np.nan, -1).astype(int)
    df_final = pd.concat([df_final, df], axis = 0)
    

#for vote in df.votes.unique():
#    if type(vote) != str : print(vote, type(vote))

for i, dataset in enumerate(datasets[0:2]): #now state votes
    df = dataset.iloc[:-1,:-1].replace(np.nan, '', regex = True) #exclude total votes column and row
    df = pd.melt(df, id_vars=['Locality', 'Ward','Pct'], var_name = 'candidate', value_name = 'votes')
    df = df.rename(columns = {'Locality': 'City/Town'})
    df['office'] = 'STATE QUESTION ' + str(i+1)
    df['district'] = 'STATEWIDE'
    df['dataverse'] = 'STATE'
    df['special'] = 'False'
    df['date'] = '2020-11-03'
    df['stage'] = 'GEN'
    df['readme_check'] = 'FALSE'
    df.votes = df.votes.replace(np.nan, -1).astype(int)
    #print(sorted(df.votes.unique())).str.replace(',','').astype(int)
    df_final = pd.concat([df_final, df], axis = 0)
      
#final President data
df = datasets[-1].iloc[:,:-2].replace(np.nan, '', regex = True)
parties = df.iloc[0:1, 3:].replace(np.nan, '', regex = True).T #get party info
df = df.iloc[1:-1,:] #get rid of party row & total vote row from bottom
df = pd.melt(df, id_vars=['City/Town', 'Ward','Pct'], var_name = 'candidate', value_name = 'votes')
df = pd.merge(df, parties, left_on = 'candidate', right_index = True).rename(columns = {0:'party_detailed'}) 
df['office'] = 'US PRESIDENT'
df['district'] = 'STATEWIDE'
df['dataverse'] = 'PRESIDENT'
df['special'] = 'False'
df['date'] = '2020-11-03'
df['stage'] = 'GEN'
df['readme_check'] = 'FALSE'
df.votes = df.votes.replace(np.nan, -1).astype(int)
#print(sorted(df.votes.unique()))
df_final = pd.concat([df_final, df], axis = 0)

#leg_datasets = [pd.read_csv(file) for file in os.scandir(path = './stateleg')]
for i, file in enumerate(os.scandir(path = './stateleg')): #state house data
    df = pd.read_csv(file).astype(str)
    parties = df.iloc[0:1, 3:].replace(np.nan, '', regex = True).T #get party info
    df = df.iloc[1:-1,:-1].replace(np.nan, '', regex = True) #exclude total votes column and row
    df = pd.melt(df, id_vars=['City/Town', 'Ward','Pct'], var_name = 'candidate', value_name = 'votes')
    df = pd.merge(df, parties, left_on = 'candidate', right_index = True).rename(columns = {0:'party_detailed'}) 
    df['office'] = 'STATE HOUSE'
    #print(df.votes.unique())
    df['votes'] = df['votes'].str.replace(',','')
    df['votes'] = df.votes.apply(lambda x: x[:-2] if '.' in x else x)

    #print(df.votes.unique())

    if 'Special' in str(file):
        print('hello 1')
        df['special'] = 'TRUE'
        df['stage'] = 'GEN'
        dist = str(str(file)[69:-35].strip('r').replace('_',' ')).upper()
        print(dist)
        df['district'] = dist
        #print(str(file)[69:-35].strip('r').replace('_',' ').zfill(3))
        if dist == '32ND MIDDLESEX': df['date'] = '2020-03-03'
        else: df['date'] = '2020-06-02'
        df['readme_check'] = 'TRUE'
    else: 
        #df['district'] = str(str(file)[41:53].replace('_',' ')).upper()
        df['special'] = 'FALSE'
        df['date'] = '2020-11-03'
        if 'Barnstable_Dukes_and_Nantucke' in str(file):
            df['district'] = 'BARNSTABLE, DUKES, AND NANTUCKET'
        else: df['district']  = str(str(file)[61:-35].replace('_',' ')).upper()
        df['stage'] = 'GEN'
        df['readme_check'] = 'FALSE'
    df['dataverse'] = 'STATE'
    print(df.office)
    print(df.district.unique())
    #df.votes = df.votes.str.replace(',','').str.replace('.0','')
    #df.votes = df.votes.replace('','0')
    
    df.votes = df.votes.astype(int)     #print(sorted(df.votes.unique())).str.replace(',','').astype(int)
    df_final = pd.concat([df_final, df], axis = 0)
    if i == 162: break

senate = [(str(file), pd.read_csv(file).astype(str)) for file in os.scandir(path = './stateleg')]
senate = senate[163:]
for file, df in senate[-42:]: #state senate data
    parties = df.iloc[0:1, 3:].replace(np.nan, '', regex = True).T #get party info
    df = df.iloc[1:-1,:-1].replace(np.nan, '', regex = True) #exclude total votes column and row
    df = pd.melt(df, id_vars=['City/Town', 'Ward','Pct'], var_name = 'candidate', value_name = 'votes')
    df = pd.merge(df, parties, left_on = 'candidate', right_index = True).rename(columns = {0:'party_detailed'}) 
    df['office'] = 'STATE SENATE'
    
    df['votes'] = df['votes'].str.replace(',','')
    df['votes'] = df.votes.apply(lambda x: x[:-2] if '.' in x else x)
    df.votes = df.votes.astype(int)

    if 'Special' not in str(file):
        df['special'] = 'FALSE'
        dist = str(file)[53:-35].upper().replace('_',' ')
        print(dist)
        if 'AND' in dist and len(dist.split(' AND ')[0]) > 1 and not dist[0].isnumeric():
            a = dist.split(' AND ')[0].split(' ')
            dist = ', '.join(a) + dist[dist.find(' AND'):]
            print(dist)
        #print(dist)
        df['district'] = dist
        df['date'] = '2020-11-03'
        df['stage'] = 'GEN'
        df['readme_check'] = 'FALSE'
    else: 
        df['special'] = 'TRUE'
        df['readme_check'] = 'TRUE'
        dist = str(file)[61:-35].upper().replace('_',' ')
        print(dist)
        if 'AND' in dist and len(dist.split(' AND ')[0]) > 1 and not dist[0].isnumeric():
            a = dist.split(' AND ')[0].split(' ')
            dist = ', '.join(a) + dist[dist.find(' AND'):]
            print(dist)
        df['district'] = dist
        df['date'] = '2020-05-19'
    df['dataverse'] = 'STATE'
    df['stage'] = 'GEN'
    #df.votes = df.votes.str.replace(',','').str.replace('.0','')
    #df.votes = df.votes.replace('','0')
    #df.votes = df.votes.astype(int)    #print(sorted(df.votes.unique())).str.replace(',','').astype(int)
    df_final = pd.concat([df_final, df], axis = 0)

#gov council
gov = [pd.read_csv(file).astype(str) for file in os.scandir(path = './govcouncil')]
for i, df in enumerate(gov): #gov council
    parties = df.iloc[0:1, 3:].replace(np.nan, '', regex = True).T #get party info
    df = df.iloc[1:-1,:-1].replace(np.nan, '', regex = True) #exclude total votes column and row
    df = pd.melt(df, id_vars=['City/Town', 'Ward','Pct'], var_name = 'candidate', value_name = 'votes')
    df = pd.merge(df, parties, left_on = 'candidate', right_index = True).rename(columns = {0:'party_detailed'}) 
    df['office'] = 'GOVERNORS COUNCIL'
    df['district'] = str(i+1).zfill(3)
    df['dataverse'] = 'STATE'
    df['special'] = 'FALSE'
    df['date'] = '2020-11-03'
    df_final['stage'] = 'GEN'
    df['readme_check'] = 'FALSE'
    
    #df['votes'] = df['votes'].str.replace(',','')
    #df['votes'] = df.votes.apply(lambda x: x[:-2] if '.' in x else x)

    df['votes'] = df['votes'].str.replace(',','')
    df['votes'] = df.votes.apply(lambda x: x[:-2] if '.' in x else x)
    df.votes = df.votes.astype(int)
    
    #print(sorted(df.votes.unique())).str.replace(',','').astype(int)
    df_final = pd.concat([df_final, df], axis = 0)

a = df_final[df_final['votes'].isnull()]

df_final = pd.merge(df_final, town_county, left_on = 'City/Town', right_on = 'jurisdiction')

df_final = df_final.replace(np.nan, '', regex = True).replace('  ', ' ', regex = True).astype(str)
df_final = df_final.applymap(lambda x: x.strip() if type(x)==str else x)
df_final = df_final.applymap(lambda x: x.upper() if type(x)==str else x)

dfa = df_final[df_final.votes == '0']

df_final.party_detailed = df_final.party_detailed.replace({'DEMOCRATIC':'DEMOCRAT', 'GREEN-RAINBOW':'GREEN-RAINBOW',
                                               'LIBERTARIAN': 'LIBERTARIAN','REPUBLICAN':'REPUBLICAN',
                                               'UNENROLLED':'INDEPENDENT'})
df_final['party_simplified'] = df_final.party_detailed.replace({'GREEN-RAINBOW':'OTHER', 'INDEPENDENT':'OTHER'})


def get_ward(precinct, ward):
    if ward != '-': return int(precinct) + '-' + ward
    else: return precinct

df_final['precinct'] = df_final.apply(lambda x: get_ward(x['Pct'], x['Ward']), axis=1)
df_final.candidate = df_final.candidate.str.replace('.', '').str.replace(',','')

#df_final.district = df_final.district.replace({'NORFOLK AND PLYMOUTH':'PLYMOUTH AND NORFOLK'})

df_final['state'] = 'Massachusetts'
df_final['mode'] = 'TOTAL'
df_final['year'] = '2020'
df_final['state_po'] = 'MA'
df_final['state_fips'] = '25'
df_final['state_cen'] = '14'
df_final['state_ic'] = '3'
df_final['writein'] = 'FALSE'
df_final.candidate = df_final.candidate.str.replace('?','I')
df_final['City/Town'] = df_final['City/Town'].str.replace('W. ', 'WEST ').str.replace('.', '').str.replace('N ','NORTH ').str.replace('E ','EAST ').str.replace('S ','SOUTH ')
df_final.votes = df_final.votes.astype(int)


writeins = ['SHIVA AYYADURAI', 'ALEX B MORSE', 'RAYLA DANELLA CAMPBELL',
            'RACHEL NICOLE MISELMAN', 'CLAUDETTE N JOSEPH', 'MICHAEL ROBBINS',
            'LEAH MERCURIO', 'ALEXANDER MENDEX', 'MICHAEL MECENAS', 'SUSANNAH WHIPPS',
            'ETHAN FLAHERTY', 'SYED HASHIMI', 'DOMINIC GIANNONE III', 'RICK MARCIANO',
            'TERRY BURKE DOTSON', 'ROBERT UNDERWOOD', 'GEORGE DARCY III', 'CHARLENE DICALOGERO',
            'CHRISTOPHER KEOHANE', 'WILLIAM BATES', 'JASON GUIDA', 'ELIZABETH HARRAH']
for cand in writeins:
    df_final.loc[df_final.candidate == cand, 'writein'] = 'TRUE'

#print(df.columns)
df_final = df_final.rename(columns = {'City/Town': 'jurisdiction_name', 'county':'county_name'})

countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv").astype(str)
jurisFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/jurisdiction-fips-codes.csv").astype(str)
jurisFips.jurisdiction_name = jurisFips.jurisdiction_name.str.replace(' TOWN', '')
#print(sorted(jurisFips.jurisdiction_name.unique()))
df_final = pd.merge(df_final, countyFips, on = ['state','county_name'],how = 'left')
df_final = pd.merge(df_final, jurisFips, on = ['state','jurisdiction_name'],how = 'left')
df_final.state = df_final.state.str.upper()
df_final['magnitude'] = 1

df_final = df_final[["precinct", "office", "party_detailed", "party_simplified", 
               "mode", "votes", "candidate", "district", "dataverse",  
               "stage", "special", "writein","date", "year","county_name", 
               "county_fips","jurisdiction_name", "jurisdiction_fips", 
               "state", "state_po","state_fips", "state_cen", 
               "state_ic", "readme_check",'magnitude']].copy()


### FIXES
def fix_precinct(x):
    a = '.0'
    if a in x: return x.replace(a,'')
    else: return x

df['precinct'] = df['precinct'].apply(fix_precinct)
df['stage'] = 'GEN'

df_final = df_final.replace('NAN','')
df_final.to_csv("C:/Users/abguh/Desktop/urop/2020-precincts/precinct/MA/2020-ma-precinct-general.csv", index = False)


df1 = df_final[df_final.office.str.contains('STATE SENATE')]
print(sorted(df1.district.unique()))
'''
for cand in sorted(df_final.candidate.unique()):
    df = df_final[df_final.candidate == cand]
    tot = sum(df.votes)
    print(cand , ':\t', tot)
'''


'''
a = df_final[df_final.votes == -1]
a = a[a.candidate != 'ALL OTHERS']
a = a[a.candidate != 'BLANKS']
print(sorted(a.candidate.unique()))


'''