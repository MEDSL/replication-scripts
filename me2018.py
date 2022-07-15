import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-me-precinct-autoadapted.csv', dtype = official_dtypes)
juris_fips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2018-precincts/help-files/jurisdiction-fips-codes.csv",dtype={'jurisdiction_fips':str})
fips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2018-precincts/help-files/county-fips-codes.csv",dtype={'county_fips':str})

###
df = df.drop(columns = '""')

#previous coding error, jurisdiction name is the county name, and precinct should be jurisdiction name
# also must ffill jurisdiction name first to match certain UOCAVA votes to appropriate counties
df['jurisdiction_name'] = df['jurisdiction_name'].ffill()
df = df.fillna("")
county_map = {'AND':'ANDROSCOGGIN','ARO':'AROOSTOOK','CUM':'CUMBERLAND','FRA':'FRANKLIN','HAN':'HANCOCK',
             'KEN':'KENNEBEC','KNO':'KNOX','LIN':'LINCOLN','OXF':'OXFORD','PEN':'PENOBSCOT','PIS':'PISCATAQUIS',
              'SAG':'SAGADAHOC','SOM':'SOMERSET','WAL':'WALDO','WAS':'WASHINGTON','YOR':"YORK"}
df['county_name'] = df['jurisdiction_name'].replace(county_map)
df['jurisdiction_name'] = df['precinct']
###

### Were errors for statewide races UOCAVA votes, fix manually
# senate uocava fixes
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE')&(df['candidate']=='BLANK'), 'votes'] = 0
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE')&(df['candidate']=='OTHERS'), 'votes'] = 0
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE')&(df['candidate']=='ZAK RINGELSTEIN'), 'votes'] = 698
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE')&(df['candidate']=='ANGUS S. KING, JR.'), 'votes'] = 1475
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE')&(df['candidate']=='ERIC L. BRAKEY'), 'votes'] = 249
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE'),'precinct'] = 'STATEWIDE UOCAVA'
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='SENATE'),'jurisdiction_name'] = 'STATEWIDE UOCAVA'
# gov UOCAVA fixes
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR')&(df['candidate']=='BLANK'),'votes'] = 42
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR')&(df['candidate']=='OTHER'),'votes'] = 0 
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR')&(df['candidate']=='SHAWN H. MOODY'),'votes'] = 277 
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR')&(df['candidate']=='JANET T. MILLS'),'votes'] = 1978
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR')&(df['candidate']=='TERESEA M. HAYES'),'votes'] = 74
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR'),'precinct'] = 'STATEWIDE UOCAVA'
df.loc[(df['county_name']=='STATE UOCAVA')&(df['office']=='GOVERNOR'),'jurisdiction_name'] = 'STATEWIDE UOCAVA'

## missing gov data
def get_missing_gov_data():
    wal = pd.read_excel('/Users/declanchin/Desktop/MEDSL/2018-precincts/ME/raw/maine governor.xlsx')
    wal=wal[wal['Unnamed: 0']=='WAL']
    wal = wal.iloc[:,:7]
    wal.columns = ['county_name','precinct'] + list(wal.columns[2:])
    wal = pd.melt(wal, id_vars = ['county_name','precinct'], value_vars = wal.columns[2:],
                 value_name='votes',var_name = 'candidate')
    wal['county_name'] = wal['county_name'].replace('WAL',"WALDO")
    wal['precinct'] = wal['precinct'].str.upper()
    wal['candidate'] = wal['candidate'].str.upper()
    wal['candidate'] = [i.split(', ')[1] + ' ' + i.split(', ')[0] if ',' in i else i for i in wal['candidate']]
    wal['jurisdiction_name'] = wal['precinct']
    wal['district'] = 'STATEWIDE'
    wal['office'] = 'GOVERNOR'
    wal['dataverse'] = 'STATE'
    wal['year'] = 2018
    wal['party_detailed'] = np.where((wal['candidate']=='TERESEA M. HAYES'), 'INDEPENDENT',
                                    np.where(wal['candidate']=='JANET T. MILLS', "DEMOCRAT",
                                            np.where(wal['candidate']=='SHAWN H. MOODY', 'REPUBLICAN', "")))
    wal['party_simplified'] = np.where(wal['party_detailed'] == 'INDEPENDENT', 'OTHER', wal['party_detailed'])
    wal['writein'] = np.where(wal['candidate']=='OTHERS','TRUE','FALSE')
    wal['mode'] = 'TOTAL'
    wal['stage'] = 'GEN'
    wal['special'] ='FALSE'
    wal['state'] = df['state'].unique()[0]
    wal['state_po'] = df['state_po'].unique()[0]
    wal['state_fips'] = df['state_fips'].unique()[0]
    wal['state_cen'] = df['state_cen'].unique()[0]
    wal['state_ic'] = df['state_ic'].unique()[0]
    return wal
missing_gov = get_missing_gov_data()

df = pd.concat([df,missing_gov])

def merge_fips_codes(df):
    # add county codes
    fips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2018-precincts/help-files/county-fips-codes.csv")
    fips['state'] = fips['state'].str.upper()
    df = pd.merge(df, fips, on = ['state','county_name'],how = 'left')
    df['county_fips'] = df['county_fips'].astype(str).str.replace('\.0','', regex=True).str.zfill(5)
    df['county_fips'] = df['county_fips'].replace('00nan','23000')
    # get jurisdiction fips codes
    juris_fips = pd.read_csv("/Users/declanchin/Desktop/MEDSL/2018-precincts/help-files/jurisdiction-fips-codes.csv",dtype={'jurisdiction_fips':str})
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
# merged fips codes, but there are merge errors due to certain jurisdiction names not matching our file
# function below addresses this to best of ability, unmatchable jurisdiction names are assigned county fips


# taken from 2020 maine, address furtehr outliers after
def township_jurisdiction_crosswalk(df):
    # finds rows with no jurisdiction fips after initial merge
    to_crosswalk=df[df['jurisdiction_fips']==''][['county_fips','jurisdiction_name']].copy()
    to_crosswalk=to_crosswalk[to_crosswalk['jurisdiction_name']!=''].copy()

    # performs merge again, but retains jurisdiction names of each respective file
    fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/jurisdiction-fips-codes.csv')
    fips=fips[fips['state']=='Maine']
    fips['county_fips']=fips['jurisdiction_fips'].astype(str).str[:5].astype(int)
    crosswalk=to_crosswalk.merge(fips, on='county_fips',how='inner',suffixes=('_raw','_file'))
    # fips['county_fips']=fips['jurisdiction_fips'].astype(str).str[:5].astype(int)
    # crosswalk=to_crosswalk.merge(fips, on='county_fips',how='inner',suffixes=('_raw','_file'))

    # removes slashes and whitespace from each jurisdiction name from each file
    crosswalk['jurisdiction_first_raw']= [i[0] for i in crosswalk['jurisdiction_name_raw'].str.replace('/',' ').str.split(' ')]
    crosswalk['jurisdiction_first_file']= [i[0] for i in crosswalk['jurisdiction_name_file'].str.replace('/',' ').str.split(' ')]
    #loop to str match raw to file jurisdictions based on the first word of each 
    index_list=[]
    for i in crosswalk['jurisdiction_name_raw'].unique():
        sub = crosswalk[crosswalk['jurisdiction_name_raw']==i]
        if sum(sub['jurisdiction_first_raw']==sub['jurisdiction_first_file'])>0:
            index=list(sub[sub['jurisdiction_first_raw']==sub['jurisdiction_first_file']].index)
            index_list = index_list+index

    crosswalk_matched=crosswalk.iloc[index_list].drop_duplicates()
    # removes false positive matches, then retains the two columns needed to crosswalk
    crosswalk_matched=crosswalk_matched[~crosswalk_matched['jurisdiction_name_file'].isin(['FORT FAIRFIELD','EAST CENTRAL WASHINGTON UT'])]
    crosswalk_matched=crosswalk_matched.drop(crosswalk_matched[(crosswalk_matched['jurisdiction_name_raw'] == 'RANGELEY/ADAMSTOWN TWP') & (crosswalk_matched['jurisdiction_name_file'] == 'RANGELEY PLANTATION')].index)
    crosswalk_matched=crosswalk_matched.drop(crosswalk_matched[(crosswalk_matched['jurisdiction_name_raw'] == 'RANGELEY PLT') & (crosswalk_matched['jurisdiction_name_file'] == 'RANGELEY')].index).sort_values('jurisdiction_first_raw')
    crosswalk_matched=crosswalk_matched[['jurisdiction_name_raw','jurisdiction_name_file']].copy()

    # this creates another crosswalk from the 2018 data to be used on any remaining blank jurisdiction fips
    # after merging with the above crosswalk.
    me_2018 = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/ME/raw/2018-me-precinct.csv')
    me_2018 = me_2018[~((me_2018['precinct']=='County Totals')|(me_2018['precinct']=='STATE UOCAVA'))].copy()
    j_p_mismatches=me_2018[(me_2018['jurisdiction']!=me_2018['precinct'])][['jurisdiction','precinct']].copy()
    j_p_mismatches_unique = j_p_mismatches.drop_duplicates()
    j_p_mismatches_unique['jurisdiction']=j_p_mismatches_unique['jurisdiction'].str.upper()
    j_p_mismatches_unique['precinct']=j_p_mismatches_unique['precinct'].str.upper()
    j_p_mismatches_unique = j_p_mismatches_unique.rename(columns={'precinct':'jurisdiction_name_raw',
                                                                  'jurisdiction':'jurisdiction_name_file'})

    #this contains info from str matched precinct/jurisdiction combos (prioritized) and 2018 unique precinct/jurisdiction pairs
    complete_crosswalk=pd.concat([crosswalk_matched, j_p_mismatches_unique]).drop_duplicates('jurisdiction_name_raw', keep='first')
    complete_crosswalk=complete_crosswalk.rename(columns={'jurisdiction_name_raw':'jurisdiction_name'})
    saint_fixes=pd.DataFrame([['SAINT ALBANS','ST. ALBANS'],
                          ['SAINT AGATHA/SINCLAIR','ST. AGATHA'],
                          ['SAINT FRANCIS','ST. FRANCIS'],
                          ['SAINT JOHN PLT','ST. JOHN PLANTATION'],
                          ['SAINT GEORGE','ST. GEORGE']],columns=['jurisdiction_name','jurisdiction_name_file'])
    complete_crosswalk = pd.concat([saint_fixes,complete_crosswalk])
    complete_crosswalk=complete_crosswalk.drop_duplicates(subset = 'jurisdiction_name', keep = 'first')

    # left merger on original df using the complete crosswalk, but creates a new column to ensure no information is 
    # overided. Then only retain new jurisdiction names for rows with empty jurisdiction fips codes 
    df=df.merge(complete_crosswalk, how='left', on='jurisdiction_name')
    df['jurisdiction_name'] = np.where(df['jurisdiction_fips']=='',df['jurisdiction_name_file'],df['jurisdiction_name'])

    # now merges original fips file, and retains fips for blanks that were addressed by the two crosswalks.
    # Reassigned blanks to unmatched jurisdictions to county names. and assign blank juri-fips to county-fips
    fips_file = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/jurisdiction-fips-codes.csv')
    fips_file['state'] = fips_file['state'].str.upper()
    fips_file['county_fips'] = fips_file['jurisdiction_fips'].apply(lambda fips: str(fips)[:5])
    df = df.merge(fips_file, on=['state', 'county_fips', 'jurisdiction_name'], how="left")
    df = df.rename(columns={'jurisdiction_fips_y':'jurisdiction_fips'})
    df['jurisdiction_fips'] = df['jurisdiction_fips'].fillna('')
    df['jurisdiction_name'] = np.where(df['jurisdiction_fips']=='', df['county_name'], df['jurisdiction_name'])
    df['jurisdiction_fips'] = np.where(df['jurisdiction_fips']=='', df['county_fips'], df['jurisdiction_fips'])
    df['jurisdiction_fips'] = df['jurisdiction_fips'].replace('00nan','23000').astype(int).astype(str)
    df = df.drop(columns = 'jurisdiction_fips_x')
    print("Jurisdiction FIPS matched, outliers are matched to county FIPS")
    return df
df=township_jurisdiction_crosswalk(df)

import difflib
me_jfips=juris_fips[juris_fips['state']=="Maine"].sort_values(['jurisdiction_fips','jurisdiction_name'])
me_jfips['county_fips'] = me_jfips['jurisdiction_fips'].str[0:5]
to_match = df[df['jurisdiction_fips'].str.len()==5][['precinct','jurisdiction_name','county_fips']].drop_duplicates()
dic = {}
for county in to_match['county_fips'].unique():
    match = to_match[to_match['county_fips']==county]
    juris = list(me_jfips[me_jfips['county_fips']==county]['jurisdiction_name'])
    for precinct in match['precinct'].unique():
        if precinct in ['GREENFIELD TWP','ORNEVILLE TWP']:
            pass
        else:
            matched = difflib.get_close_matches(precinct, juris, n=2,cutoff = .5)
            if (precinct == 'MILLINOCKET PISCATAQUS TOWNSHIPS') & (county == '23021'):
                dic[precinct] = ['NORTHWEST PISCATAQUIS UT','23021']
            if (precinct == 'MILLINOCKET PISCATAQUIS TWPS') & (county == '23021'):
                dic[precinct] = ['NORTHEAST PISCATAQUIS UT','23021']
            if precinct == 'RANGELEY PLT':
                dic[precinct] = ['RANGELEY PLANTATION',county]
            if precinct == 'CENTERVILLE TWP':
                dic[precinct] = ['COLUMBIA FALLS', '23029']
            if precinct == 'MILLINOCKET PENOBSCOT TOWNSHIPS':
                dic[precinct] = ['NORTH PENOBSCOT UT',county]
            if precinct == 'THE FORKS PLT':
                dic[precinct] = ['THE FORKS PLANTATION',county]
            if precinct == 'WEST FORKS PLT':
                dic[precinct] = ['WEST FORKS PLANTATION',county]    
            if len(matched) > 0:  
                dic[precinct] = [matched[0],county]
# removing invalid matches
del dic['COUNTY TOTALS']
del dic['CENTERVILLE TWP']
del dic['FREEMAN TWP']
del dic['WASHINGTON TWP']
del dic['HERSEYTOWN TWP']
                
final_matching=pd.DataFrame(dic).T.reset_index()
final_matching.columns = ['raw_jurisdiction_name','jurisdiction_name','county_fips']
final = final_matching.merge(me_jfips.drop(columns='state'), how='left',on = ['jurisdiction_name','county_fips'])
final=final.drop(columns = 'jurisdiction_name').rename(columns={'raw_jurisdiction_name':'precinct','jurisdiction_fips':'jurisdiction_fips_finalMatches'})
df = df.merge(final, on = ['precinct','county_fips'], how = 'left')
df['jurisdiction_fips'] = np.where(df['jurisdiction_fips_finalMatches'].notnull(), df['jurisdiction_fips_finalMatches'],df['jurisdiction_fips'])
df['jurisdiction_name'] = np.where(df['jurisdiction_fips_finalMatches'].notnull(), df['precinct'],df['jurisdiction_name'])
df = df.drop(columns = 'jurisdiction_fips_finalMatches')


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1


#################################### specific ####################################

df['candidate'] = df['candidate'].str.replace('\.','',regex=True)
df['candidate'] = df['candidate'].str.replace(',','',regex=True)
df['candidate'] = df['candidate'].replace({"OTHER":'WRITEIN',"OTHERS":'WRITEIN','BLANK':"UNDERVOTES"})
df['office'] =df['office'].replace({"STATE REPRESENTATIVE":"STATE HOUSE", 'SENATE':"US SENATE",
    "REPRESENTATIVE, DISTRICT 1":"US HOUSE", 'COUNTY COMISSIONER':"COUNTY COMMISSIONER"})
df.loc[df['office']=='GOVERNOR','dataverse'] = 'STATE'
df.loc[df['office']=='STATE HOUSE','dataverse'] = 'STATE'
df.loc[df['office']=='REGISTER OF PROBATE','dataverse'] = 'LOCAL'

df['district'] = np.where(df['office'].isin(['US SENATE','GOVERNOR']), 'STATEWIDE', df['district'].str.zfill(3))
df['district'] = df['district'].replace({'000':'','00N':"N",'00S':"S"})

df['party_detailed'] = df['party_detailed'].replace('NON-PARTISAN','NONPARTISAN')
def get_party_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','NONPARTISAN',"LIBERTARIAN"]: return x
    if x == '': return ''
    else: return "OTHER"
df['party_simplified'] = df.party_detailed.apply(get_party_simplified)

df = df[~((df['writein']=='TRUE')&(df['votes']==0))]
df = df[~(df['precinct']=='COUNTY TOTALS')]

# missing district info for UOCAVA results
df.loc[(df['candidate']=='LOUISE M CARON') & (df['office'] == 'COUNTY REGISTER OF DEEDS'), 'district'] = 'N'
df.loc[(df['candidate']=='UNDERVOTES') & (df['office'] == 'COUNTY REGISTER OF DEEDS') &
(df['votes']==6) & (df['district']==""), 'district'] = 'S'
df.loc[(df['candidate']=='MELISSA L RICHARDSON') & (df['office'] == 'COUNTY REGISTER OF DEEDS'), 'district'] = 'S'
df.loc[(df['candidate']=='UNDERVOTES') & (df['office'] == 'COUNTY REGISTER OF DEEDS') &
(df['votes']==0) & (df['district']==""), 'district'] = 'N'
#################################### specific ####################################


#final general, remove whitespace
df=df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]].copy()

df=df.replace('\s+', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df.to_csv("2018-me-precinct-general-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)