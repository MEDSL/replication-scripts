import pandas as pd
import csv

raw = pd.read_csv('AZ_precinct_v2.csv')

def fix_precinct(precinct):
    fixed = precinct.upper()
    fixed = fixed.strip()
    return fixed

def fix_office(office):

    if 'U.S. REPRESENTATIVE' in office: return 'US HOUSE'
    elif 'STATE SENATOR' in office: return 'STATE SENATE'
    elif 'STATE REPRESENTATIVE' in office: return 'STATE HOUSE'
    elif 'U.S. SENATOR' in office: return 'US SENATE'
    elif 'PRESIDENT' in office: return 'US PRESIDENT'
    elif 'RETENTION' in office and 'DIVISION' in office: return 'RETENTION COURT OF APPEALS'
    else: return office
    
    
def fix_party_detailed(name):

    string = str(name).upper()

    if string == 'DEM': return 'DEMOCRAT'
    elif string == 'REP': return 'REPUBLICAN'
    elif string == 'NAN': return 'NONPARTISAN'
    elif string == 'NONE': return ""
    elif string == 'IRP': return 'INDEPENDENT REPUBLICAN PARTY'
    elif string == 'LBT': return 'LIBERTARIAN'
    elif string == 'IND': return 'INDEPENDENT'
    elif string == 'ACN': return 'CONSTITUTION'
    elif string == 'CSM': return 'COMMON SENSE MODERATE'
    elif string == 'UPA': return 'UNITY'
    elif string == 'GREEN': return "GREEN"
    elif string == 'PARTY FOR SOCIALISM AND LIBERATION': return "PARTY FOR SOCIALISM AND LIBERATION"
    else: return string

def fix_party_simplified(detailed):
    if detailed == 'REPUBLICAN': return 'REPUBLICAN'
    elif detailed == 'DEMOCRAT': return 'DEMOCRAT'
    elif detailed == 'LIBERTARIAN': return 'LIBERTARIAN'
    elif detailed == 'NONPARTISAN': return 'NONPARTISAN'
    elif detailed == '': return ""
    else: return 'OTHER'

    
    

def fix_candidate(name):
    
    title = name.replace('.', '')
    title = title.replace('""', '"') #seth ""marcus"" sifuentes
    title = title.replace('  ', ' ')
    title = title.strip()
    title = title.replace('É', "E")
    title = title.replace('Í', "I")
    title = title.replace('Á', "A")
    title = title.replace('Ú', "U")
    title = title.replace('Ó', "O")
    title = title.replace('Ñ', "N")
    if title == 'KIMBERLY "KIM" BEACH - MOSCHETTI':
        return 'KIMBERLY "KIM" BEACH-MOSCHETTI'
    return title.upper()

def get_div(title):
    if 'DIVISION II' in title:
        if 'OTHER' in title:
            return '002, OTHER'
        elif 'PIMA' in title:
            return '002, PIMA'
    elif 'DIVISION I' in title:
        if 'OTHER' in title:
            return '001, OTHER'
        elif 'MARICOPA' in title:
            return '001, MARICOPA'
    return title
        
        

def fix_district(dist):

    title = dist.upper()
    title = title.strip()

    if 'DISTRICT' in title:
        num = title[-2:]

        if num[0] == ' ':
            return '00' + num[1]
        return '0' + num

    if title == 'ARIZONA SUPREME COURT':
        return 'STATEWIDE'
    
    elif 'DIVISION' in title:
        return get_div(title)

    return title

def get_dataverse(office):

    if office == 'US HOUSE': return 'HOUSE'
    elif office == 'US SENATE': return 'SENATE'
    elif office == 'US PRESIDENT': return 'PRESIDENT'
    else: return 'STATE'

def fix_special(office):
    if office == 'US SENATE': return 'TRUE'
    return 'FALSE'

def fix_writein(name):
    if str(name) == 'True': return 'TRUE'
    return 'FALSE'

def fix_stage(string):
    return string.upper()

def fix_magnitude(magnitude):
    if str(magnitude) == 'nan':
        return 1
    return int(magnitude)

def fix_mode(mode):
    if mode == 'EARLY BALLOTS': return 'EARLY'
    elif mode == 'POLLING PLACE': return 'ELECTION DAY'
    elif mode == 'PROVISIONAL BALLOTS': return 'PROVISIONAL'
    return mode

fips = {
    'MARICOPA': '04013',
    'PINAL': '04021',
    'YUMA': '04027',
    'COCONINO': '04005',
    'COCHISE': '04003',
    'MOHAVE': '04015',
    'GRAHAM': '04009',
    'SANTA CRUZ': '04023',
    'APACHE': '04001',
    'LA PAZ': '04012',
    'YAVAPAI': '04025',
    'NAVAJO': '04017',
    'GREENLEE': '04011',
    'PIMA': '04019',
    'GILA': '04007'
    
    }

def fix_fips(county):
    return fips[county]


raw['precinct'] = raw['precinct'].apply(fix_precinct)
raw['office'] = raw['office'].apply(fix_office)
raw['party_detailed'] = raw['party_detailed'].apply(fix_party_detailed)
raw['party_simplified'] = raw['party_detailed'].apply(fix_party_simplified)
raw['candidate'] = raw['candidate'].apply(fix_candidate)
raw['district'] = raw['district'].apply(fix_district)
raw['district'] = raw['district'].astype(str)
raw['dataverse'] = raw['office'].apply(get_dataverse)
raw['stage'] = raw['stage'].apply(fix_stage)
raw['magnitude'] = raw['magnitude'].apply(fix_magnitude)
raw['date'] = '2020-11-03' ### fix date format
raw['mode'] = raw['mode'].apply(fix_mode)
raw['special'] = raw['office'].apply(fix_special)
raw['special'] = raw['special'].astype(str)


raw['writein'] = raw['writein'].apply(fix_writein)

raw['special'] = raw['special'].astype(str)
raw['writein'] = raw['writein'].astype(str)

raw['county_fips'] = raw['county_name'].apply(fix_fips)
raw['jurisdiction_fips'] = raw['county_fips']
raw['county_fips'] = raw['county_fips'].astype(str)
raw['jurisdiction_fips'] = raw['jurisdiction_fips'].astype(str)

raw['readme_check'] = 'FALSE'
raw['readme_check'] = raw['readme_check'].astype(str)

# temporarily removing writein candidates with 0 votes
raw = raw[~((raw['writein']=='TRUE')&(raw['votes']==0))]

raw.to_csv('2020-az-precinct-general.csv', index = None, quoting=csv.QUOTE_NONNUMERIC )
