import numpy as np
import pandas as pd
import csv
import math
import os

original_path = os.getcwd()
os.chdir(original_path + '/raw/counties')
arr_of_files = os.listdir()
def fix_office(string):
    if 'President' in string:
        return 'US PRESIDENT'
    if 'U.S. House' in string:
        return 'US HOUSE'
    #Put Measures into a standard format
    if '107' in string:
        return 'MEASURE 107'
    if '108' in string:
        return 'MEASURE 108'
    if '109' in string:
        return 'MEASURE 109'
    if '110' in string:
        return 'MEASURE 110'
    if '15-197' in string:
        return 'MEASURE 15-197'
    if '23-183' in string:
        return 'MEASURE 23-183'
    if '15-199' in string:
        return 'MEASURE 15-199'
    if '15-198' in string:
        return 'MEASURE 15-198'
    if '22-182' in string:
        return 'MEASURE 22-182'
    if '22-183' in string:
        return 'MEASURE 22-183'
    if '22-184' in string:
        return 'MEASURE 22-184'
    if '22-185' in string:
        return 'MEAUSRE 22-185'
    if '8-101' in string:
        return 'MEASURE 8-101'
    if '15-196' in string:
        return 'MEASURE 15-196'
    if 'COUNCIL' in string.upper():
        fix_string = string.upper().split('COUNCIL')
        if len(fix_string) == 1:
            return fix_string[0] + '- COUNCIL'
        if '-' in fix_string[0]:
            return fix_string[0] + 'COUNCIL' + fix_string[1]
        else:
            return fix_string[0] + '- COUNCIL' + fix_string[1]
    if 'MAYOR - CITY OF ALBANY' in string.upper():
        return 'CITY OF ALBANY - MAYOR'
    if 'MAYOR' in string.upper():
        fix_string = string.upper().split('MAYOR')
        if len(fix_string) == 1:
            return fix_string[0] + '- MAYOR'
        if '-' in fix_string[0]:
            return fix_string[0] + 'MAYOR' + fix_string[1]
        else:
            return fix_string[0] + '- MAYOR' + fix_string[1]
    
    if 'DIRECTOR' in string.upper():
        return string.replace(',', '').replace('.','').upper()
    else:
        return string.replace(',', '').replace('Dir', 'Director').replace('.','').upper()

def fix_vote_for(string):
    if 'VOTE FOR' in string:
        split_string = string.split('VOTE FOR')
        return split_string[0].replace('(', '').strip()
    else:
        return string


def fix_cand(string):
    #Fixes typos which were found mostly through googling
    typos = {}
    typos['GARY.DYE'] = 'GARY DYE'
    
    typos['CHRIS HEN'] = 'CHRIS HENRY'

    typos['UNDERVOTE'] = 'UNDER VOTES'

    typos['KYLE MARKEY'] = 'KYLE MARKLEY'

    typos['LARS D H HEDBOR'] = 'LARS HEDBOR'

    typos['TESSA DANEL'] = 'TESSAH DANEL'

    typos['TOBIAS REED'] = 'TOBIAS READ'

    typos['ALEX DIBIASI'] = 'ALEX DIBLASI'

    typos['BOB NIEMEIER'] = 'BOB NIEMEYER'

    typos['LYNETTE SHAW'] = 'LYNNETTE SHAW'

    typos['DEB PATTERNSON'] = 'DEB PATTERSON'

    typos['IBRAHAM TAHER'] = 'IBRAHIM TAHER'

    typos['IBRAHIM TAHIR'] = 'IBRAHIM TAHER'

    typos['MICHAEL MARSCH'] = 'MICHAEL MARSH'

    typos['RACHEL PRUSACK'] = 'RACHEL PRUSAK'

    typos['ALEX SKARLATOS'] = 'ALEK SKARLATOS'

    typos['ELLEN ROSEBLUM'] = 'ELLEN ROSENBLUM'

    typos['NATALIE PARAVICINI'] = 'NATHALIE PARAVICINI'

    typos['NATHALIE PARAVACINI'] = 'NATHALIE PARAVICINI'

    typos['NATHALIE PARACIVINI'] = 'NATHALIE PARAVICINI'

    typos['NATHALIE PARACIVINI'] = 'NATHALIE PARAVICINI'

    typos['CLTLF BENTZ'] = 'CLIFF BENTZ'

    

    
            
    
    if isinstance(string, float):
        return string

    #escape character? above dictionary wasn't working
    if 'MARSCH' in string:
        return 'MICHAEL MARSH'

    if 'HEDBOR' in string:
        return 'LARS HEDBOR'

    if string.strip() in typos:
        return typos[string.strip()]
    if string.strip() == 'UNDER VOTES':
        return 'UNDERVOTES'
    if string.strip() == 'OVER':
        return 'OVERVOTES'
    if string.strip() == 'OVER VOTES':
        return 'OVERVOTES'
    
    if 'WRITE-IN' in string or 'WRITE-INS' in string or 'WRITEINS' in string:
        return 'WRITEIN'
    else:
        string_arr = string.replace('.', '').replace('\'', '').split('/')[0].split()
        if len(string_arr) == 3 and not ((string_arr[0] == 'JOSEPH' and string_arr[2] == 'BIDEN') or (string_arr[0] == 'DONALD' and string_arr[2] == 'TRUMP')):
            return string_arr[0]+ ' ' + string_arr[2]
        return string.replace('.', '').replace('\'', '').split('/')[0].strip()

def fix_punc(string):
    return string.replace(',', '').replace('\'', '').replace('.', '')

def get_write_in(string):
    if isinstance(string, float):
        return 'FALSE'
    if 'WRITE-INS' in string or 'WRITE-IN' in string or 'WRITEIN' in string or 'WRITEINS' in string:
        return 'TRUE'
    else:
        return 'FALSE'
    
def fix_party_det(string):
    if not isinstance(string, str):
        return string
    if 'REP' in string:
        return 'REPUBLICAN'
    if 'DEM' in string:
        return 'DEMOCRAT'
    if 'LBT' in string:
        return 'LIBERTARIAN'
    if 'LIB' in string:
        return 'LIBERTARIAN'
    if 'PGP' in string:
        return 'PACIFIC GREEN'
    if 'PRO' in string:
        return 'OREGON PROGRESSIVE'
    if 'CON' in string:
        return 'CONSTITUTION'
    if 'IND' in string:
        return 'INDEPENDENT'

def fix_party_simp(string):
    if not isinstance(string, str):
        return string
    common = {'REPUBLICAN', 'DEMOCRAT', 'LIBERTARIAN', 'NONPARTISAN', ''}
    if not string in common:
        return 'OTHER'
    else:
        return string

def get_dataverse(string):
    if 'PRESIDENT' in string:
        return 'PRESIDENT'
    if 'US HOUSE' in string:
        return 'HOUSE'
    if 'US SENATE' in string:
        return 'SENATE'
    if 'STATE' in string:
        return 'STATE'
    if 'ATTORNEY GENERAL' in string:
        return 'STATE'
    if 'SUPREME COURT' in string:
        return 'STATE'
    if 'COURT OF APPEALS' in string:
        return 'STATE'
    if 'MEASURE' in string and '-' in string:
        return 'LOCAL'
    elif 'MEASURE' in string:
        return 'STATE'
    if 'REGISTERED VOTERS' in string or 'BALLOTS CAST' in string:
        return ''
    return 'LOCAL'

digits = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}
def get_district(string):
    if 'POSITION ' in string:
        split_string = string.split('POSITION ')
        position = split_string[-1]
        office = split_string[0]
        if ' DISTRICT' in split_string[0]:
            district = split_string[0].split(' COURT ')[1].split().pop(0)
            
            ans = ''
            for character in district:
                if character in digits:
                    ans += character
            ans = [office.split(' COURT ')[0] + ' COURT', (district.replace('TH', '').replace('RD', '').zfill(3) + ', POSITION ' + position)]
            #print(ans)
            return ans
        return [office.strip(), position]
    
    if ' ZONE ' in string:
        split_string = string.split(' ZONE ')
        return [split_string[0].strip(), split_string[1]]
    if ' POS ' in string:
        split_string = string.split(' POS ')
        return [split_string[0].strip(), split_string[1]]
    if ' WARD ' in string:
        split_string = string.split(' WARD ')
        return [split_string[0].strip(), split_string[1]]
    if ' SD ' in string:
        split_string = string.split(' SD ')
        return [split_string[0].strip(), split_string[1]]
    if ' SUBDIVISION ' in string:
        split_string = string.split(' SUBDIVISION ')
        return [split_string[0].strip(), split_string[1]]
    if ' AT LARGE' in string:
        split_string = string.split(' AT LARGE')
        return [split_string[0].strip(), 'AT-LARGE']

    return [string]
    
def fix_district(string):
    if not isinstance(string, float):
        if 'JUDGE, POSITION ' in string:
            return string.split('POSITION ')[1].zfill(3)
        for digit in string.strip():
            if not digit in digits:
                return string.strip().replace('#', '')
        
    if pd.isna(string) or not string:
        return ''
    else:
        return str(int(string)).zfill(3)


def get_magnitude(string):
    if isinstance(string, float):
        return 0
    if 'BALLOTS CAST' in string or 'REGISTERED VOTERS' in string:
        return 0
    elif 'VOTE FOR' in string:
        split_string = string.split('VOTE FOR')
        for character in split_string[1]:
            if character in digits:
                return int(character)
    if 'CITY OF SWEET HOME - COUNCIL MEMBERS' in string:
        return 4
    if 'CITY OF CENTRAL POINT - COUNCIL MEMBERS AT-LARGE' in string:
        return 2
    return 1

def fix_office_order(string):
    if string.strip() == 'CITY OF CENTRAL POINT - COUNCIL MEMBERS AT-LARGE':
        return 'COUNCIL MEMBER - CITY OF CENTRAL POINT'
    else:
        if ' - ' in string:
            split_string = string.split(' - ')
            return (split_string[1] + ' - ' + split_string[0])
        return string

def fix_councilors(string):
    if 'COUNCIL' in string and ' - ' in string:
        split_string = string.split(' - ')
        return 'COUNCIL - ' + split_string[1]
    else:
        return string
        

def as_int(inp):
    if pd.isna(inp):
        return inp
    return int(inp)






df = pd.DataFrame()
for file in arr_of_files:
    if file == 'test.xlsx':
        break
    print(file)
    sheet = pd.read_csv(file)
    sheet = sheet.rename(columns = {'county':'county_name'})
    sheet['state'] = 'Oregon'
    sheet['date'] = '2020-03-11'
    sheet['stage'] = 'GEN'
    sheet['county_name'] = sheet['county_name'].str.upper()
    county_fips = pd.read_csv('../../../../help-files/county-fips-codes.csv')
    county_fips = county_fips[county_fips['state']=='Oregon'].drop(columns='state')
    sheet = sheet.merge(county_fips, on='county_name', how='left')
    sheet['county_fips'] = sheet['county_fips'].apply(as_int)
    state_codes = pd.read_csv('../../../../help-files/merge_on_statecodes.csv')
    sheet = sheet.merge(state_codes, on='state', how = 'left')
    sheet['jurisdiction_fips'] = sheet['county_fips']

    
    df = pd.concat([df, sheet])
df['party_detailed'] = df['party'].apply(fix_party_det)
df['jurisdiction_name'] = df['county_name']
df['jurisdiction_fips'] = df['jurisdiction_fips'].astype('Int64')
df['county_fips'] = df['county_fips'].astype('Int64')





df['office'] = df['office'].apply(fix_office).apply(fix_punc)
df['dataverse'] = df['office'].apply(get_dataverse)
df['candidate'] = df['candidate'].str.upper().apply(fix_cand)
df['party_simplified'] = df['party_detailed'].apply(fix_party_simp)
df['state'] = df['state'].str.upper()
df['readme_check'] = 'FALSE'
df['mode'] = 'TOTAL'
df['year'] = 2020
df['district'] = df['district'].apply(fix_district)
df['magnitude'] = df['office'].apply(get_magnitude)
df['writein'] = df['candidate'].apply(get_write_in)
df['office'] = df['office'].apply(fix_vote_for)



for j in range(len(df['office'].values)):
    arr = get_district(df['office'].values[j])
    if len(arr) > 0:
        df['office'].values[j] = arr[0]
        if len(arr) > 1:
            df['district'].values[j] = arr[1]
        else:
            continue
    else:
        continue

def fix_precinct(string):
    if isinstance(string, float) or isinstance(string, int):
        return str(string).upper()
    else:
        return string.upper()
    
df['office'] = df['office'].apply(fix_office_order)
df['precinct'] = df['precinct'].apply(fix_precinct)

arr_special = []

#Checks the one special election, fixes missing vote totals
for i in range(len(df['office'].values)):
    if df['office'].values[i] == 'STATE SENATE' and df['district'].values[i] == '010':
        arr_special.append('TRUE')
    else:
        arr_special.append('FALSE')
        
    precinct = df['precinct'].values[i]
    candidate = df['candidate'].values[i]
    office = df['office'].values[i]
    if not (isinstance(precinct, str) and isinstance(candidate, str) and isinstance(office, str)):
        continue
    elif 'PRECINCT 024' in precinct and 'UNDERVOTES' in candidate and 'JACKSON COUNTY COMMISSIONER' in office:
        df['votes'].values[i] = 107
    elif 'PRECINCT 028' in precinct and 'UNDERVOTES' in candidate and 'ATTORNEY GENERAL' in office:
        df['votes'].values[i] = 90
    elif 'PRECINCT 035' in precinct and 'UNDERVOTES' in candidate and 'US HOUSE' in office:
        df['votes'].values[i] = 107
    elif 'PRECINCT 042' in precinct and 'UNDERVOTES' in candidate and 'STATE TREASURER' in office:
        df['votes'].values[i] = 107
        

#Sets district values for offices that are elected statewide
for j in range(len(df['office'].values)):
    verse = df['dataverse'].values[j]
    if (verse == 'STATE' or verse == 'PRESIDENT' or verse == 'SENATE') and len(df['district'].values[j])==0:
        df['district'].values[j] = 'STATEWIDE'

df['district'] = df['district'].apply(fix_district)

dict_of_offices = {'CITY OF ASHLAND PARK COMMISSIONER': 'PARK COMMISSIONER - CITY OF ASHLAND',
    'CITY OF GOLD HILL MUNICIPAL JUDGE': 'MUNICIPAL JUDGE - CITY OF GOLD HILL',
    'CITY OF PORTLAND COMMISSIONER': 'COMMISSIONER - CITY OF PORTLAND',
    'CURRY COUNTY SOIL AND WATER CONSERVATION DISTRICT': 'SOIL AND WATER CONSERVATION DISTRICT - CURRY COUNTY',
    'EMERALD PUD DIRECTOR': 'PUD DIRECTOR - EMERALD',
    'INTERLACHEN WATER PUD DIRECTOR': 'WATER PUD DIRECTOR - INTERLACHEN',
    'JACKSON COUNTY ASSESSOR': 'ASSESSOR - JACKSON COUNTY',
    'JACKSON COUNTY COMMISSIONER': 'COMMISSIONER - JACKSON COUNTY',
    'JACKSON SWCD DIRECTOR': 'SOIL AND WATER CONSERVATION DISTRICT - JACKSON',
    'LINN SOIL & WATER CONSERVATION DISTRICT DIRECTOR': 'SOIL AND WATER CONSERVATION DISTRICT DIRECTOR - LINN',
    'ROCKWOOD WATER PUD DIRECTOR': 'WATER PUD DIRECTOR - ROCKWOOD'
    }


df['special'] = arr_special
df = df.drop([df.columns[5], df.columns[16], df.columns[17], df.columns[18]], axis = 1)


#Some counties didn't have party data for candidates
dict_of_parties_simp = {}
dict_of_parties_det = {}
for k in range(len(df['candidate'].values)):
    if df['party_detailed'].values[k] and not pd.isna(df['party_detailed'].values[k]):
        dict_of_parties_simp[df['candidate'].values[k]] = df['party_simplified'].values[k]
        dict_of_parties_det[df['candidate'].values[k]] = df['party_detailed'].values[k]
#print(dict_of_parties_det)
for l in range(len(df['candidate'].values)):
    if df['candidate'].values[l] in dict_of_parties_simp:
        df['party_simplified'].values[l] = dict_of_parties_simp[df['candidate'].values[l]]
        df['party_detailed'].values[l] = dict_of_parties_det[df['candidate'].values[l]]

df['office'] = df['office'].apply(fix_councilors)

arr_to_drop = []
df = df.reset_index(drop=True)
for m in range(len(df['votes'].values)):
    #if df['precinct'].values[m] == 'NAN':
    #   print(m)
    if (pd.isnull(df['votes'].values[m]) or df['precinct'].values[m] == 'NAN') and not (pd.isnull(df['county_name'].values[m])):
        arr_to_drop.append(m)


"""Check that the rest are in bunches, so that they should be part of the same election and just don't have any votes in that precinct.
for j in range(0, len(arr_to_drop)-2):
    if (not arr_to_drop[j+1] - arr_to_drop[j] == 1) and (not arr_to_drop[j+2]-arr_to_drop[j+1] == 1):
        print(arr_to_drop[j+1])"""
for j in range(len(df['office'].values)):
    office = df['office'].values[j]
    if office in dict_of_offices:
        df['office'].values[j] = dict_of_offices[office]
    else:
        continue

df['district'] = df['district'].apply(fix_district)
dict_of_districts = {'AT LARGE': 'AT-LARGE', 'HD15': '015', 'I': '001',
                     'IB': '1B', 'II': '002', 'IIB': '2B', 'III': '003',
                     'IIIB': '3B'}

for w in range(len(df['district'].values)):
    district = df['district'].values[w]
    if district in dict_of_districts:
        df['district'].values[w] = dict_of_districts[district]
    else:
        continue


df = df.drop(index = arr_to_drop)
df['votes'] = df['votes'].apply(as_int)
df = df.reset_index(drop = True)

for j in range(len(df['office'].values)):
    office = df['office'].values[j]
    if 'EMSWCD DIRECTOR AT LARGE' in office or 'WMSWCD DIRECTOR AT LARGE' in office:
        df['office'].values[j] = office.split(' AT LARGE')[0]
        df['district'].values[j] = 'AT-LARGE'
    else:
        continue


## DC 8/23/21 fixes

# format undervotes
df['candidate'] = df['candidate'].replace("UNDER VOTES", "UNDERVOTES")
# format local offices (city council instead of council + remove "city of")
# First use case essentially reads: "where office contains council, replace council with city council, otherwise leave office field the same"
df['office'] = np.where(df['office'].str.contains('COUNCIL - '), 
    df['office'].str.replace('COUNCIL', 'CITY COUNCIL'),
    df['office']) 
df['office'] = np.where(df['office'].str.contains('CITY OF'), 
    df['office'].str.replace('CITY OF ', ""), 
    df['office'])
#fix incorrect date "YYYY-MM-DD"
df['date'] = "2020-11-03"

temp = 0
for j in range(len(df['county_name'].values)):
    if 'JUDGE OF THE SUPREME COURT' in df['office'].values[j] or 'JUDGE OF THE COURT OF APPEALS' in df['office'].values[j]:
        df['party_simplified'].values[j] = 'NONPARTISAN'
        df['party_detailed'].values[j] =  'NONPARTISAN'
    if pd.isnull(df['county_name'].values[j]):
        temp = j
    else:
        continue

def as_string(string):
    return str(string)

df['county_name'].values[temp] = 'BENTON'
df['precinct'].values[temp] = '15 - NORTHWEST C4S12H23'
df['county_fips'].values[temp] = 41003
df['jurisdiction_fips'].values[temp] = 41003
df['jurisdiction_name'].values[temp] = 'BENTON'
df['county_fips'] = df['county_fips'].apply(as_string)
df['jurisdiction_fips'] = df['jurisdiction_fips'].apply(as_string)





#DC fixes 8/27/21
# Noticed blank district info for non-local, non-statistic offices (in US HOUSE)
# Confirmed that the missing district was district 005 in Clackamas using the below code on the raw data ('check')
#check[(check['county']==('Clackamas'))&(check['office']=='U.S. House')&(check['candidate'].str.contains('Votes'))]
df['district'] = np.where(((df['district']=="")&(df['dataverse']=='HOUSE')), "005", df['district'])

#fix party blank info
def blank_party_fixes(x):
    if x == 'LILY MORGAN': return "REPUBLICAN"
    if x == 'JERRY MORGAN': return "DEMOCRAT"
    if x == 'PAM MARSH': return "DEMOCRAT"
    if x == 'ASHTON SIMPSON': return "Working Families Party".upper()
    if x in ['OVERVOTES','UNDERVOTES', 'WRITEIN']: return ""
    else: return np.nan
df['fix_blank_party'] = df['candidate'].apply(blank_party_fixes)
df['party_detailed'] = np.where(df['fix_blank_party'].notnull(), df['fix_blank_party'], df['party_detailed'])
df['party_simplified'] = np.where(df['fix_blank_party'].notnull(), df['fix_blank_party'], df['party_simplified'])
# dropping fix_blank_party column
df = df[['county_name', 'precinct', 'office', 'district', 'candidate', 'votes',
       'state', 'date', 'stage', 'county_fips', 'state_po', 'state_fips',
       'state_cen', 'state_ic', 'jurisdiction_fips', 'party_detailed',
       'jurisdiction_name', 'party_simplified', 'dataverse', 'readme_check',
       'mode', 'year', 'magnitude', 'writein', 'special']].copy()

raw = df

marion = raw[raw['county_name'] == 'MARION']


ibrahim_taher_votes = list(marion[marion['candidate'] == 'GARY DYE']['votes'].values)

gary_dye_votes = [50, 88, 50, 47, 36, 0, 48, 2, 64, 2, 46, 24, 24, 24, 2, 0, 0, 85, 42, 49,
                  0, 66, 105, 62, 16, 7, 25, 0, 1, 1, 30, 11, 20, 57, 35, 0, 31, 82, 17, 43,
                  29, 61, 0, 0, 53, 40, 53, 46, 32, 59, 87, 2, 5, 13, 24, 30, 28, 34, 7, 0,
                  1, 17, 50, 8, 20, 1, 9, 0, 5, 0, 13, 10, 51, 76, 40, 66, 19, 20, 4, 56,
                  16, 6, 17, 42, 11, 17, 1, 1, 4, 0, 58, 65, 0, 19, 59, 44, 16, 38, 56, 50,
                  11, 26, 10, 5, 5, 5, 7, 44, 34, 35, 2, 38, 17, 11, 29, 26, 20, 0, 8, 2,
                  0, 5, 0]

overvotes = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
          0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0,
          0, 0, 0]

new_votes = list(raw['votes'].values)

i, j, k = 0, 0, 0

count = 0
for x in marion.index:
    if marion.loc[x, 'candidate'] == 'IBRAHIM TAHER':
        new_votes[x] = ibrahim_taher_votes[i]
        i += 1
    elif marion.loc[x, 'candidate'] == 'GARY DYE':
        new_votes[x] = gary_dye_votes[j]
        j += 1
    elif marion.loc[x, 'candidate'] == 'OVERVOTES' and marion.loc[x, 'office'] == 'US SENATE':
        new_votes[x] = overvotes[k]
        k += 1

raw['votes'] = new_votes  

### US HOUSE ###                    

raw['votes'] = np.where((raw['district'] == '002') & (raw['precinct'] == '1 RUFUS') & (raw['candidate'] == 'CLIFF BENTZ'), 126, raw['votes'])

#district 4/5

precincts = ["11 - N ALBANY C5S8H15", "12 - ADAIR VILLAGE C5S12H23", "18 - ALBANY RURAL C5S8H15", "22 - ADAIR RURAL C5S12H23"]


#daniel hoffay --> matthew rix, change district to 005 (DC adding party fixes)
raw['district'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'DANIEL HOFFAY'), '005', raw['district'])
raw['candidate'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'DANIEL HOFFAY'), 'MATTHEW RIX', raw['candidate'])
raw['party_detailed'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'MATTHEW RIX'), 'LIBERTARIAN', raw['party_detailed'])
raw['party_simplified'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'MATTHEW RIX'), 'LIBERTARIAN', raw['party_simplified'])

#peter defazio --> amy courser, change distric to 005
raw['district'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'PETER DEFAZIO'), '005', raw['district'])
raw['candidate'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'PETER DEFAZIO'), 'AMY COURSER', raw['candidate'])
raw['party_detailed'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'AMY COURSER'), 'REPUBLICAN', raw['party_detailed'])
raw['party_simplified'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'AMY COURSER'), 'REPUBLICAN', raw['party_simplified'])
#ALEK SKARLATOS --> KURT SCHRADER, change distric to 005
raw['district'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'ALEK SKARLATOS'), '005', raw['district'])
raw['candidate'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'ALEK SKARLATOS'), 'KURT SCHRADER', raw['candidate'])
raw['party_detailed'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'KURT SCHRADER'), 'DEMOCRAT', raw['party_detailed'])
raw['party_simplified'] = np.where(raw['precinct'].isin(precincts) & (raw['candidate'] == 'KURT SCHRADER'), 'DEMOCRAT', raw['party_simplified'])
#writein should be dist 005, fix assignment of extra offices
raw['district'] = np.where(raw['precinct'].isin(precincts) & (raw['office'] == 'US HOUSE') & (raw['candidate'] == 'WRITEIN'), '005', raw['district'])

df = raw.copy()

#print(type(df['jurisdiction_fips'].values[1]))
df.to_csv('../../2020-or-precinct-general.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)


