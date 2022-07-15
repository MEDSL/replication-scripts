import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-ks-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")

def merge_fips_codes(df):
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
df = merge_fips_codes(df)


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = np.where(df['office'] == 'BALLOTS CAST', 0, 1)


#################################### specific ####################################

def fix_district(x):
    if 'JUDGE DIVISION' in x: 
        return '029, ' + 'DIVISION ' + x.split(' ')[-1].strip()
    if 'COURT OF APPEALS' in x:
        return re.findall('\d+',x)[0].zfill(3)
    else: return ""
df['interim_district'] = df.office.apply(fix_district)
df['district'] = np.where(df['interim_district']!= "",
    df['interim_district'],df['district'].str.zfill(3))
df = df.drop(columns = 'interim_district')



df['candidate'] = df['candidate'].replace('[WRITE-IN]','WRITEIN',regex=False)
df['candidate'] = df['candidate'].replace('\.',"", regex=True)
df['candidate'] = df['candidate'].replace('\(','"', regex=True)
df['candidate'] = df['candidate'].replace('\)','"', regex=True)
#manual candidates
df['candidate'] = df['candidate'].replace('ADAM J SR LUSKER','ADAM J LUSKER SR',regex=False)
df['candidate'] = df['candidate'].replace('JOHN P JR WHEELER','JOHN P WHEELER JR',regex=False)
df['candidate'] = df['candidate'].replace('OVER VOTES','OVERVOTES',regex=False)
df['candidate'] = df['candidate'].replace('UNDER VOTES','UNDERVOTES',regex=False)

#judicial fixes
df.loc[df['office'].str.contains('JUDGE DIVISION'),'office'] = 'DISTRICT COURT JUDGE'
df.loc[df['office'].str.contains('COURT OF APPEALS'),'office'] = 'COURT OF APPEALS JUDGE'
state_dataverse = ['DISTRICT COURT JUDGE','COURT OF APPEALS JUDGE']
df.loc[df['office'].isin(state_dataverse),'dataverse'] = 'STATE'


df = df.replace([True,False], ['TRUE','FALSE'])
df.loc[df['candidate']=='WRITEIN','writein'] = 'TRUE'
df['office'] = df['office'].replace('GOVERNOR / LT. GOVERNOR','GOVERNOR')

df = df.replace('""',"")
#################################### specific ####################################

## Finally fix duplicate issue
## writein and over/undervotes in district 38 State house were accidentally assigned to district 30
## (raw file contained no districts so original cleaner must have assigned manually)
def fix_duplicate_issue():

    # diplay problem
    sh = df[(df['office']=='STATE HOUSE')&(df['county_name']=='JOHNSON')]
    for i in sh['district'].unique():
        sub = sh[sh['district']==i]
        if 'WRITEIN' not in list(sub['candidate'].unique()):
            print("Unique candidates for state house districts missing WRITEIN")
            print(i,sub['candidate'].unique())

    raw = pd.read_excel('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/KS/raw/2018_General_Election_Kansas_House_of_Representatives_Precinct_Level.xlsx',
                     sheet_name = 'JOHNSON',skiprows = 2)
    d30 = raw[['Unnamed: 1','Write-in.17','OVER VOTES.17','UNDER VOTES.17']].copy()
    d30.columns = ['precinct',"WRITEIN",'OVERVOTES',"UNDERVOTES"]
    d30['district'] = '030'
    d38 = raw[['Unnamed: 1','Write-in.18','OVER VOTES.18','UNDER VOTES.18']].copy()
    d38.columns = ['precinct',"WRITEIN",'OVERVOTES',"UNDERVOTES"]
    d38['district'] = '038'
    append = pd.concat([d30,d38])
    append['precinct'] = append['precinct'].str.upper().str.strip()
    append = pd.melt(append,
                    id_vars = ['precinct','district'],
                    value_vars = ['WRITEIN','OVERVOTES','UNDERVOTES'],
                    value_name='votes',
                    var_name = 'candidate')
    append = append[~(append['precinct']=='COUNTY TOTALS')].copy()
    append_info = sh[sh['district'].isin(['030','038'])][[i for i in sh.columns if i not in ['votes','candidate','party_simplified','party_detailed','writein']]]
    append_info = append_info.drop_duplicates()
    append = append.merge(append_info, on = ['precinct','district'], how ='left')
    return append
# drop undervotes, overvote, writein data in dist 30 (contains district 38 info also)
df = df[~((df['office']=='STATE HOUSE')&(df['district']=='030')&
          (df['candidate'].isin(['OVERVOTES','UNDERVOTES','WRITEIN'])))].copy()

df = pd.concat([df, fix_duplicate_issue()])


#final general
df=df.replace('\s+', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df.to_csv("2018-ks-precinct-general-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)