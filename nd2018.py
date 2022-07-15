import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-nd-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")
fips = pd.read_csv("../../help-files/county-fips-codes.csv")
fips['state'] = fips['state'].str.upper()
#print(countyFips.head)
df = pd.merge(df, fips, on = ['state','county_name'],how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
#date, readme, and magnitude
df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['magnitude'] = 1

#string pad
df['district'] = df['district'].str.zfill(3)

#################################### specific ####################################

# writein
df['candidate'] = df['candidate'].str.replace("[WRITE-IN]", "WRITEIN", regex=False)
df = df.replace('""',"", regex=False)
df.loc[(df['party_detailed']=="")&(df['party_simplified']=="OTHER"), 'party_simplified'] = ""

#################################### specific ####################################


#final general
df = df.replace([True,False], ['TRUE','FALSE'])
df=df.replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df.to_csv("2018-nd-precinct-general-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)