import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-la-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")

#date, readme, and magnitude
df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'


df['county_name'] = df['county_name'].str.replace('LASALLE','LA SALLE',regex=False)
#####
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


#################################### specific ####################################

# add magnitude (only two variations)
df['magnitude'] = np.where(df['office'].str.contains('5 TO BE ELECTED'), 5,
                           np.where(df['office'].str.contains('3 TO BE ELECTED'),3,1))
# candidate period/comma fixes (not working to find official names for nickname cands.)
df.loc[df['candidate']=='A.G. CROWE','candidate']= 'A G CROWE'
df.loc[df['candidate']=='VERSA "V.O." CLARK','candidate']= 'VERSA "V O" CLARK'
df.loc[df['candidate']=='"J.P." MORGAN','candidate']= '"J P" MORGAN'
df['candidate'] = df['candidate'].str.replace("\.","",regex=True)
df['candidate'] = df['candidate'].str.replace(",","",regex=True)

#### district fixes
df['district'] = np.where(df['district'].str.contains('\d'), df['district'].str.zfill(3),
                         df['district'])
def fix_district(x):
    if 'DISTRICT JUDGE , ES' in x: 
        return x.split(',')[1].lstrip() + ', ' + x.split(',')[2].replace('\.','').lstrip()
    if 'DISTRICT JUDGE' in x: return x.split(',')[1].replace('\.','').lstrip()
    if 'JUDGE, COURT OF APPEAL' in x: return x.split('-- ')[1].lstrip()
    if 'JUDGE -- CIVIL DISTRICT COURT' in x: return x.split(',')[1].lstrip()
    if 'ALDERMAN -- WARD' in x: return x.split(',')[0][-6:].lstrip()
    else: return ""
df['dist_append'] = df['office'].apply(fix_district)
df['dist_append'] = df['dist_append'].str.replace('\.','',regex=True)
df['dist_append'] = df['dist_append'].str.replace('DIVISION','DIV',regex=True)
df['dist_append'] = df['dist_append'].str.replace('ELEC SEC','ES',regex=True)
df['dist_append'] = df['dist_append'].str.replace('1ST CIRCUIT','CIRCUIT 1,',regex=True)
df['dist_append'] = df['dist_append'].str.replace('2ND CIRCUIT','CIRCUIT 2,',regex=True)
df['district'] = np.where(df['dist_append']!="",
                          df['district'] + ', ' + df['dist_append'],
                         df['district'])
df['district'] = df['district'].replace(', WARD','WARD',regex=True)
df = df.drop(columns = 'dist_append')

def fix_office(x):
	if 'JUDGE, COURT OF APPEAL' in x: return 'COURT OF APPEALS JUDGE'
	if "DISTRICT JUDGE" in x: return 'DISTRICT JUDGE'
	if 'CIVIL DISTRICT COURT' in x: return 'CIVIL DISTRICT COURT JUDGE'
	if 'ALDERMAN -- WARD' in x: return "ALDERMAN - CITY OF EUNICE"
	if 'ALDERMAN, TOWN OF BASILE' in x: return 'ALDERMAN - TOWN OF BASILE'
	if x =='COUNCILMAN, CITY OF SHREVEPORT': return 'COUNCILMAN - CITY OF SHREVEPORT'
	if x == 'COUNCILMAN, CITY OF BROUSSARD': return 'COUNCILMAN - CITY OF BROUSSARD'
	if 'TO BE ELECTED' in x: return x.split('(')[0].strip()
	else: return x
df['office'] = df.office.apply(fix_office).str.replace('--','-',regex=True)
df['office'] = df['office'].replace('ALDERMEN, TOWN OF BASILE', 'ALDERMAN - TOWN OF BASILE', regex=False)
#################################### specific ####################################


#final general
df = df.replace([True,False], ['TRUE','FALSE'])
df=df.replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df.to_csv("2018-la-precinct-general-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)