import pandas as pd
import numpy as np
import os
import csv
import re

official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}
df = pd.read_csv('2018-wa-precinct-autoadapted.csv', dtype = official_dtypes)
df = df.fillna("")
df = df.replace('""',"")

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
df['magnitude'] = 1


#################################### specific ####################################

df['candidate'] = df['candidate'].replace({'[WRITE-IN]':'WRITEIN',
	'KATY BUTLER (RAPACZ)':'KATY BUTLER RAPACZ',
    '"SKA JE TAH LO" LONA WILBUR':'LONA "SKA JE TAH LO" WILBUR',
    "APPROVED":"YES",'REJECTED?':"NO",
    'A) LOCATED AT THE PRESENT SITE OF ALBI STADIUM':'A - LOCATED AT THE PRESENT SITE OF ALBI STADIUM',
    "B) LOCATED ON PROPERTY OWNED BY THE PFD ON THE NORTH BANK OF THE SPOKANE RIVER":"B - LOCATED ON PROPERTY OWNED BY THE PFD ON THE NORTH BANK OF THE SPOKANE RIVER",
    'NICHOLAS( NICK) HENDERSON':'NICHOLAS "NICK" HENDERSON',
    'ELIZABETH (BETH) A. FRASER':'ELIZABETH A "BETH" FRASER',
    "OVERVOTE":"OVERVOTES",
    "UNDERVOTE":"UNDERVOTES"})
df['candidate'] = df['candidate'].str.replace('\.',"",regex=True)
df['candidate'] = df['candidate'].str.replace(',',"",regex=True)
df['candidate'] = df['candidate'].str.replace(" '",' "',regex=True)
df['candidate'] = df['candidate'].str.replace("' ",'" ',regex=True)
df['candidate'] = df['candidate'].str.replace(' \(',' "',regex=True)
df['candidate'] = df['candidate'].str.replace('\) ','" ',regex=True)

#### URG Need to inspect offices with non-blank districts first because previous cleaner removed the info
def fix_district(x):
    if ('POSITION NO. ' in x) and ("PROPOSITION" not in x): 
    	if ("NORTH" in x) or ("SOUTH" in x) or ("EAST" in x) or ("WEST" in x) or ("SHORELINE" in x):
    		return x.split(' ')[0] + ", POSITION " + x.split('POSITION NO. ')[-1]
    	else: 
    		return "POSITION " + x.split('POSITION NO. ')[-1]
    if "NORTH DISTRICT" in x:
        return "NORTH"
    if "SOUTH DISTRICT" in x:
        return "SOUTH"
    if "EAST DISTRICT" in x:
        return "EAST"
    if "WEST DISTRICT" in x:
    	return "WEST"
    if ('UPPER' in x) and ('COURT' in x):
    	return 'UPPER'
    if ('LOWER' in x) and ('COURT' in x):
    	return 'LOWER'
    if 'COURT OF APPEALS, DIVISION' in x:
        return "DIVISION " + x.split(',')[1][-1] + ', ' + x.split(',')[2].replace(' JUDGE','')
    if ('DISTRICT COURT NO' in x) or ('DEPARTMENT NO.' in x):
        return x.split(' ')[-1].zfill(3)
    if ('JUSTICE POSITION' in x) or ('JUDGE POSITION' in x):
    	return "POSITION " + x.split(' ')[-1]
    if 'SUB-DIST' in x: #x.split(' ')[2].zfill(3) +
        return 'SUB-DISTRICT ' + x.split(' ')[4] + ', POSITION ' + x.split(' ')[-1]
    if ('COUNTY WIDE DISTRICT COURT' in x) and (x[-1].isdigit()):
        return x[-1].zfill(3)
    if "STATE HOUSE" in x:
        return 'POSITION ' + x[-1]
    if ("POSITION" in x) and ('AT-LARGE' in x):
        return "AT-LARGE, POSITION " + x[-1]
    if ("POSITION" in x) and ("PROPOSITION" not in x):
        return "POSITION " + x.split(' ')[-1]
    if ('COUNTY DISTRICT' in x) and (x[-1].isdigit()):
        return x[-1].zfill(3)
    if "DEPARTMENT" in x: return x[-1].zfill(3)
    if x == 'PUBLIC UTILITY DISTRICT COMMISSIONER 2':
        return 'POSITION 2'
    if x == 'PUBLIC UTILITY DISTRICT COMMISSIONER #1':
        return "POSITION 1"
    if ('COMMISSIONER' in x) & (x[-1].isdigit()):
        return "COMMISSIONER " + x[-1]
    if ('COMMISSIONER DISTICT B' in x) or ('COMMISSIONER B' in x):
        return "B"
    if ('COMMISSIONER' in x) and (x.split(' ')[-2].isdigit()):
        return "DIST " + x.split(' ')[-2]
    if ('DISTRICT COURT' in x) and (x[-1].isdigit()):
        return x[-1].zfill(3)
    if 'PARK DIST. POS.' in x:
        return x[-1].zfill(3)
    if 'PUD DISTRICT' in x:
        return re.findall('\d+', x)[0].zfill(3)
    if x == 'SAN JUAN COUNTY COUNCIL RESIDENCY DISTRICT 3':
        return '003'
    if 'AT-LARGE' in x:
        return 'AT-LARGE'
    else: return ''
df['district_preserve'] = df['district'].str.zfill(3)
df['district_append'] = df['office'].apply(fix_district)
df['district'] = np.where((df['district']!="")&(df['district_append']!=""),
                                df['district'].str.zfill(3) + ', ' + df['district_append'],
                                df['district_append'])

df['district'] = np.where(df['office'].isin(['US HOUSE', 'STATE SENATE']), 
    df['district_preserve'],
    df['district'])

df.loc[df['office'].isin(['STATE INITIATIVE MEASURE NO. 1631',
       'STATE INITIATIVE MEASURE NO. 1634',
       'STATE INITIATIVE MEASURE NO. 1639',
       'STATE INITIATIVE MEASURE NO. 940', 'US SENATE']), 'district'] = 'STATEWIDE'

# standardizing state dataverse offices, leave local alone
def fix_office(x):
	if 'STATE HOUSE' in x: return "STATE HOUSE"
	if 'SUPREME COURT' in x: return "SUPREME COURT JUSTICE"
	if "COURT OF APPEALS" in x: return "COURT OF APPEALS JUDGE"
	else: return x
df['office'] = df['office'].apply(fix_office)

df.loc[(df['office'].isin(["SUPREME COURT JUSTICE","COURT OF APPEALS JUDGE"]))|(df['office'].str.contains('STATE INITIATIVE'))
,'dataverse'] = 'STATE'

# party fixes
df.loc[df['office'].str.contains('COURT|JUDGE'),'party_detailed'] = "NONPARTISAN"
df.loc[df['candidate'].isin(['YES','NO','WRITEIN','OVERVOTES','UNDERVOTES','REPEALED','REJECTED','MAINTAINED']),'party_detailed'] = ""

def get_party_simplified(x):
	if x in ['REPUBLICAN','DEMOCRAT','NONPARTISAN','LIBERTARIAN',""]:
		return x
	else:
		return "OTHER"
df['party_simplified'] = df.party_detailed.apply(get_party_simplified)

#2 james harts, RICK TYLERs verified https://sos-tn-gov-files.tnsosfiles.com/Nov%202018%20General%20Totals.pdf

print(len(df))
df = df[~((df['writein']=="TRUE")&(df['votes']==0))]
print(len(df))

#################################### specific ####################################

df=df[["precinct","office", "party_detailed", "party_simplified", "mode", "votes", "county_name", "county_fips", "jurisdiction_name",
                      "jurisdiction_fips", "candidate", "district", "dataverse", "year", "stage", "state", "special", "writein", "state_po",
                      "state_fips", "state_cen", "state_ic", "date", "readme_check", "magnitude"]].copy()
df = df.replace([True,False], ['TRUE','FALSE'])
#final general
df=df.replace('\s+', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)

df.to_csv("2018-wa-precinct-general-updated.csv",quoting=csv.QUOTE_NONNUMERIC,index=False)