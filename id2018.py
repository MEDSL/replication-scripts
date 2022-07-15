import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-id-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")
fips = pd.read_csv("../../help-files/county-fips-codes.csv")
fips['state'] = fips['state'].str.upper()


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
df = merge_fips_codes(df)


df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1


#################################### specific ####################################

df.loc[df['office']=='JUDGE - 5TH JUDICIAL DISTRICT', 'dataverse'] = 'STATE'
df.loc[df['office']=='JUDGE - 5TH JUDICIAL DISTRICT', 'office'] = 'DISTRICT COURT JUDGE'

df['district'] = df['district'].str.zfill(3)

df['candidate'] = df['candidate'].replace('\.',"", regex=True)

df = df.replace([True,False], ['TRUE','FALSE'])
df=df[~((df['writein']=='TRUE')&(df['votes']==0))]

#################################### specific ####################################


#final general, remove whitespace
df=df.replace('\s+', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df.to_csv("2018-id-precinct-general-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)