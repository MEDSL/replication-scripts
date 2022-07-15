import enum
import pandas as pd
import csv
import numpy as np
import re

pd.set_option('display.max_columns', None)

# csv breaks: 34606, 35352, 36098
file = open('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/CT/raw/ELECTIONVOTINGDISTRICT-144.csv')
csv_reader = csv.reader(file)

# countyFipsCSV = '/Users/benjaminebanks/Documents/GitHub/2018-precincts/help-files/county-fips-codes.csv'

# saving csv file as a pandas df
df1_fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2018-precincts/help-files/county-fips-codes.csv')
# skip first two lines
next(csv_reader)
next(csv_reader)

empty_rows = [] # [34603, 35349, 36095]
biglist = []

# [0, 34603, 35349, 36095, END INDEX]
for i, row in enumerate(csv_reader):
   biglist.append(row)
   if not row:
       empty_rows.append(i+1)

# start row
empty_rows.insert(0, 0)
# end row
empty_rows.append(i+1)

dataframes_list = []
for i in range(len(empty_rows)-1):
   dataframes_list.append(pd.DataFrame(biglist[empty_rows[i]:empty_rows[i+1]]))


for i, df in enumerate(dataframes_list):
   # all dfs have extra column
   df.drop(df.columns[-1], axis=1, inplace=True)
   # df = df.iloc[1: , :]

#     # df.columns
#     df.to_csv(f'/Users/benjaminebanks/Dropbox/Mac/Downloads/testcsv_{i}.csv')
#     df1 = df.read_csv
df1, df2, df3, df4 = dataframes_list

df1 = df1.iloc[1: , :]
df1 = df1.iloc[:-1 , :]
df2 = df2.iloc[1: , :]
df2 = df2.iloc[:-1 , :]
df3 = df3.iloc[1: , :]
df3 = df3.iloc[:-1 , :]
df4 = df4.iloc[1: , :]

df1_col_names = ["ElectionName", 'jurisdiction_name', 'ElectionCategory', 'Election_Date', 'TownClerk', 'office', 'candidate', 'party_detailed','precinct', 'Machine_Count', "Absentee_Count", "Votes"]
# df2_col_names = ["ElectionName", 'TownName', 'ElectionCategory', 'Election_Date', 'TownClerk', 'OfficeName', 'CandidateName', 'PartyName','Polling_Place_Name', 'Machine_Count', "Absentee_Count", "Final_Count"]
# df3_col_names = ["ElectionName", 'TownName', 'ElectionCategory', 'Election_Date', 'TownClerk', 'OfficeName', 'CandidateName', 'PartyName','Polling_Place_Name', 'Machine_Count', "Absentee_Count", "Final_Count"]
# df1_col_names = ["ElectionName", 'TownName', 'ElectionCategory', 'Election_Date', 'TownClerk', 'OfficeName', 'CandidateName', 'PartyName','Polling_Place_Name', 'Machine_Count', "Absentee_Count", "Final_Count"]
df1.columns = df1_col_names
df1 = pd.melt(df1, id_vars = ["ElectionName", 'jurisdiction_name', 'ElectionCategory', 'Election_Date', 'TownClerk', 'office', 'candidate', 'party_detailed','precinct'], value_vars = ['Machine_Count', 'Absentee_Count'], var_name = 'mode', value_name = 'votes')
df1.loc[df1['mode'] == "Machine_Count", 'mode'] = "MACHINE"
df1.loc[df1['mode'] == "Absentee_Count", 'mode'] = "ABSENTEE"

df1['party_detailed'] = df1['party_detailed'].str.upper().map(lambda x: x.rsplit(' ', 1)[0])
df1['party_detailed'] = df1['party_detailed'].map(lambda x: x.replace('DEMOCRATIC', 'DEMOCRAT'))
df1['party_detailed'] = df1['party_detailed'].replace('NON','NONPARTISAN')

# df1 = df1.drop(['ElectionCateogry'], 1)
df1 = df1.drop(['Election_Date', 'TownClerk', 'ElectionName', "ElectionCategory"], 1)

def get_voter_statistics(path):
    stats = pd.read_excel(path,sheet_name = 1)
    stats = pd.melt(stats,
                   id_vars = ['TownName','Polling_Place_Name'],
                   value_vars = stats.columns[2:],
                   value_name = 'votes',
                   var_name= 'mode')
    stats['office'] = np.where(stats['mode'].str.contains('Total'), 'BALLOTS CAST - TOTAL', "ELECTION DAY REGISTRATION")
    mode_dic=dict(zip(['Machine/Polling Place Total', 'Absentee Total',
           'Election Day Registration (EDR)'],
    ['MACHINE', 'ABSENTEE',
           'MACHINE']))
    stats['mode'] = stats['mode'].replace(mode_dic)
    stats2 = pd.read_excel(path,sheet_name = 2)
    stats2 = pd.melt(stats2,
                   id_vars = ['TownName','Polling_Place_Name'],
                   value_vars = stats2.columns[2:],
                   value_name = 'votes',
                   var_name= 'office')
    office_dic = dict(zip(['No.of Names on Registry', 'No. Checked as Having Voted',
           'No.of Overseas Voters'],['REGISTERED VOTERS - TOTAL','TURNOUT','UOCAVA VOTERS - TOTAL']))
    stats2['office'] = stats2['office'].replace(office_dic)
    stats2['mode'] = 'TOTAL'
    stats = pd.concat([stats,stats2])
    stats['candidate'] = ""
    stats['party_detailed'] = ""
    stats = stats.rename(columns = {'TownName':'jurisdiction_name', 'Polling_Place_Name':'precinct'})
    return stats
stats = get_voter_statistics('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/CT/raw/stas-pages.xls')
df1 = pd.concat([df1,stats])

dic = pd.read_excel('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/CT/jurisdiction_to_county_map.xlsx')
df1['county_name'] = df1['jurisdiction_name'].replace(dict(zip(dic['jurisdiction_name'],dic['county_name'])))

# df1['candidate'] = df1['candidate'].str.upper().str.replace('[].,-]*', '')

df1['candidate'] = df1['candidate'].map(lambda x: x.replace('Machine/Polling Place/EDRAbsenteeTotal', ''))

df1 = df1.assign(date='2018-11-06')

df1['office'] = df1['office'].str.upper()

def get_district(x):
    if 'DISTRICT' in x: return x.split(' ')[-1]
    if x[-1].isdigit(): return re.findall('\d+',x)[0].zfill(3)
    else: return ""
df1['district'] = df1['office'].apply(get_district)
df1['district']=df1['district'].replace(dict(zip(['I', 'II', 'III', 'IV', 'V','VI'],
                       ['001','002','003','004','005','006'])))

def fix_office(x):
    if 'NON PARTISAN REPRESENTATIVE TOWN MEETING' in x: return 'NON PARTISAN REPRESENTATIVE TOWN MEETING'
    if x[-1].isdigit(): 
      x=re.sub(' \d+','',x)
    if x == 'GOVERNOR AND LIEUTENANT GOVERNOR': return 'GOVERNOR'
    if x == 'UNITED STATES SENATOR': return 'US SENATE'
    if x == 'REPRESENTATIVE IN CONGRESS': return "US HOUSE"
    if x == 'STATE SENATOR': return "STATE SENATE"
    if x == 'STATE REPRESENTATIVE': return "STATE HOUSE"
    if x == 'SECRETARY OF THE STATE': return "SECRETARY OF STATE"
    else: return x

df1['office'] = df1['office'].apply(fix_office)

def get_dataverse(x):
   if x == "US SENATE":
       return "senate".upper()
   elif x == "US HOUSE":
       return "house".upper()
   elif x in ["PUBLIC SERVICE COMMISSIONER", "STATE SENATE", "STATE HOUSE",
   'GOVERNOR','SECRETARY OF STATE','COMPTROLLER','TREASURER',"ATTORNEY GENERAL",]:
       return "state".upper()
   else:
       return "local".upper()

df1['dataverse'] = df1['office'].apply(get_dataverse)
df1['special'] = 'FALSE'

df1['magnitude'] = 1

df1['year'] = '2018'

df1['stage'] = 'GEN'

df1['writein'] = np.where(df1['party_detailed']=='WRITE','TRUE','FALSE')
df1['party_detailed'] = df1['party_detailed'].replace('WRITE',"")
def get_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','LIBERTARIAN','NONPARTISAN',""]: return x
    else: return "OTHER"
df1['party_simplified'] = df1.party_detailed.apply(get_simplified)

# setting the value of all cells in special column to "Conneticut"
df1['state'] = 'Connecticut'.upper()

# duplicating jurisdiction_name column into party_simplified column
df1['county_name'] = df1['county_name'].str.upper()
df1['jurisdiction_name'] = df1['jurisdiction_name'].str.upper()

def merge_fips_codes(df):
    # add county codes
    fips = pd.read_csv("../../help-files/county-fips-codes.csv")
    fips['state'] = fips['state'].str.upper()
    df = pd.merge(df, fips, on = ['state','county_name'],how = 'left')
    df['county_fips'] = df['county_fips'].astype(str).str.replace('\.0','', regex=True).str.zfill(5)
    # get jurisdiction fips codes
    juris_fips = pd.read_csv("../../help-files/jurisdiction-fips-codes.csv",dtype={'jurisdiction_fips':str})
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
df1 = merge_fips_codes(df1)


# setting the value of all cells in readme_check column to "False"
df1['readme_check'] = "FALSE"
# setting the value of all cells in the "state_fips", "state_ic", "state_cen", and "state_po" columns to a number/abbreviation based on the merge_on_statecode.csv
df1['state_fips'] = 9
df1['state_ic'] = 1
df1['state_cen'] = 16
df1['state_po'] = "CT"

df1['candidate'] = df1['candidate'].str.replace('*','',regex=True)
df1['candidate'] = df1['candidate'].str.replace('\.','',regex=True)
df1['candidate'] = df1['candidate'].str.replace(',','',regex=True)
df1['candidate'] = df1['candidate'].str.replace('\(','"',regex=True)
df1['candidate'] = df1['candidate'].str.replace('\)','"',regex=True)
df1=df1.applymap(lambda x: x.strip().upper() if type(x)==str else x)


df1['candidate'] = df1['candidate'].replace(dict(zip(['ALEXANDRA ALEX" BERGSTEIN"',
    'EMIL BUDDY" ALTOBELLO"',
    'PAULANN BUNNY" LESCOE"'],['ALEXANDRA "ALEX" BERGSTEIN',
    'EMIL "BUDDY" ALTOBELLO',
    'PAULANN "BUNNY" LESCOE'])))
df1 = df1[~((df1['writein']=='TRUE')&(df1['votes']==0))].copy()
# df1_final = df1_joined[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
#                       "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
#                       "state_fips", "state_cen", "state_ic", 'date', 'readme_check', 'magnitude']]

# print(df1)
# print(df2)
# print(df3)
df1.to_csv('2018-ct-precinct-general-updated.csv', index=False,quoting=csv.QUOTE_NONNUMERIC)
