import pandas as pd
import numpy as np
import csv

raw = pd.read_csv('raw/2020GEPrecinctLevelResultsPosted.csv')

#I want to get YES and NO as candidates based on the yes/no/candidate votes.
#This is the best way I can think of doing this.

precinct = []
county = []
office = []
candidate = []
party = []
votes = []
def extract(raw): 
    raw_precinct = list(raw['Precinct'].values)
    raw_county = list(raw['County'].values)
    raw_office = list(raw['Office/Issue/Judgeship'].values)
    raw_candidate = list(raw['Candidate'].values)
    raw_party = list(raw['Party'].values)
    raw_votes = list(raw['Candidate Votes'].values)
    raw_yes = list(raw['Yes Votes'].values)
    raw_no = list(raw['No Votes'].values)



    seen = set()
    '''
    maybe = set()
    blanks = set()

    #
    for i in range(len(raw_precinct)):
        ### not part of cleaning
        if raw_yes[i] > 0 or raw_no[i] > 0:
            maybe.add(raw_office[i])

    for i in range(len(raw_precinct)):
        ### not part of cleaning
        if raw_yes[i] == 0 and raw_no[i] == 0 and raw_votes[i] == 0 and raw_office[i] in maybe and raw_office[i] not in blanks:
            blanks.add(raw_office[i])
            print(raw_office[i])
        ###     '''

    retentions = ['Supreme Court', 'Court of Appeals', 'District Court, 18th Judicial District',
                  'County Court, Arapahoe', 'District Court, 19th Judicial District']
    
    for i in range(len(raw_precinct)):
        
        if (raw_votes[i] == 0 and (raw_yes[i] > 0 or raw_no[i] > 0)) or raw_office[i] in retentions:
            precinct.append(str(raw_precinct[i]))
            precinct.append(str(raw_precinct[i]))
            
            county.append(raw_county[i])
            county.append(raw_county[i])

            if 'Court' in raw_office[i]:
                office.append('RETENTION ' + raw_office[i])
                office.append('RETENTION ' + raw_office[i])
            else:
                office.append(raw_office[i])
                office.append(raw_office[i])

            if 'Court' in raw_office[i]:
                candidate.append(raw_candidate[i] + ' - YES')
                candidate.append(raw_candidate[i] + ' - NO')
            else:
                candidate.append('YES')
                candidate.append('NO')

            party.append(raw_party[i])
            party.append(raw_party[i])

            votes.append(raw_yes[i])
            votes.append(raw_no[i])
        else:
            precinct.append(str(raw_precinct[i]))
            county.append(raw_county[i])            
            office.append(raw_office[i])
            candidate.append(raw_candidate[i])
            party.append(raw_party[i])
            votes.append(raw_votes[i])
extract(raw)

#COUNTY TO FIPS DICTIONARY
county_file = open('counties.txt', 'r')
counties = []
for line in county_file:
    line = line.replace('\n', '')
    counties.append(line)

fips_file = open('fips.txt', 'r')
fips = []
for line in fips_file:
    line = line.replace('\n', '')
    fips.append(line)

county_to_fips = {}
for i in range(len(counties)):
    county_to_fips[counties[i]] = fips[i]

def get_dist(office):
    if 'DISTRICT' in office and 'DISTRICT' != office.split()[-1]:
        dist = office.split()[-1]
    elif 'JUDICIAL DISTRICT' in office:
        dist = office.split()[-3][:-2]
    elif office.split()[0] == 'DISTRICT' and len(office.split()[1]) == 1:
        return office.split()[1]
    else:
        return ''

    if len(dist) == 1:
        dist = '00' + dist
    elif len(dist) == 2:
        dist = '0' + dist
    return dist

def get_fips(county):
    return county_to_fips[county]

def fix_party_detailed(party):
    party = str(party)
    if 'ffiliat' in party: return 'NONPARTISAN'
    elif 'nan' in party: return 'NONPARTISAN'
    
    party = party.upper()
    party = party.replace(' PARTY', '')
    
    if party == 'DEMOCRATIC': party = 'DEMOCRAT'
    return party

def get_party_simplified(party):
    if party not in ['DEMOCRAT', 'REPUBLICAN', 'LIBERTARIAN', 'OTHER', 'NONPARTISAN']:
        return 'OTHER'
    return party

def delete_after(word1, word2):
    if word2 not in word1:
        return word1

    n = len(word2)

    for i in range(len(word1)):
        if word1[i:i+n] == word2:
            return word1[:i]
    
def fix_office(name):
    name = name.replace('STATE REPRESENTATIVE', 'STATE HOUSE')
    name = name.replace(',', ' -')

    if ' - DISTRICT' in name or 'JUDICIAL DISTRICT' in name:
        name = delete_after(name, ' -')

    split = name.split()
    if split[0] == 'DISTRICT' and len(split[1]) == 1:
        name = name[11:]

    name = name.strip()
    if name == 'UNITED STATES SENATOR': return 'US SENATE'
    elif name == 'UNITED STATES REPRESENTATIVE': return 'US HOUSE'
    elif 'PRESIDENT' in name: return 'US PRESIDENT'
    elif 'RETENTION COUNTY COURT' in name: return 'RETENTION COUNTY COURT'

    return name

def fix_candidate(name):
    name = str(name)
    name = name.upper()
    name = name.replace('.', '')
    name = delete_after(name, ' /')
    name = name.replace('Á', 'A')
    name = name.replace('Í', 'I')
    name = name.replace('Ñ', 'N')
    if name == "NAN": 
        name = name.replace('NAN', "") #null rows are currently named "NAN" rather than blank (only for referenda)

    return name

def get_verse(office):
    if 'PRESIDENT' in office: return 'PRESIDENT'
    elif 'US SENATE' in office: return 'SENATE'
    elif 'US HOUSE' in office: return 'HOUSE'
    elif 'STATE' in office: return 'STATE'
    elif 'COUNTY' in office: return 'LOCAL'
    elif 'COURT' in office and 'DENVER' not in office: return 'STATE'
    elif 'PROPOSITION' in office or 'AMENDMENT' in office: return 'STATE'
    return 'LOCAL'

writeins = ['MICHAEL SANCHEZ', 'VERN RICHARDSON','KASEY WELLS','DANNY SKELLY','STEVE ZORN',"ANDREW J O'CONNOR",
            'BRUCE LOHMILLER','RACHEL WELLS','TODD CELLA','ANDY PRIOR','TIMOTHY BRYAN CELLA','TOM HOEFLING']

def get_writein(name):
    if name in writeins: return 'TRUE'
    return 'FALSE'
    
df = pd.DataFrame({})
#precinct
df['precinct'] = precinct
df['precinct'] = df['precinct'].astype(str)

#office
df['office'] = office
df['office'] = df['office'].str.upper()

#district + fix office
df['district'] = df['office'].apply(get_dist)
df['district'] = df['district'].astype(str)
df['office'] = df['office'].apply(fix_office)

#dataverse
df['dataverse'] = df['office'].apply(get_verse)

#party
df['party_detailed'] = party
df['party_detailed'] = df['party_detailed'].apply(fix_party_detailed)
df['party_simplified'] = df['party_detailed'].apply(get_party_simplified)

df['party_detailed'] = df['party_detailed'].astype(str)
df['party_simplified'] = df['party_simplified'].astype(str)

#mode not present!
df['mode'] = 'TOTAL'

#votes
df['votes'] = votes

#county/county fips
df['county_name'] = county
df['county_name'] = df['county_name'].str.upper()
df['county_fips'] = df['county_name'].apply(get_fips)

#jurisdiction/jurisdiction fips
df['jurisdiction_name'] = df['county_name']
df['jurisdiction_fips'] = df['county_fips']

#candidate
df['candidate'] = candidate
df['candidate'] = df['candidate'].apply(fix_candidate)

#magnitude
df['magnitude'] = '1'

#year
df['year'] = '2020'

#stage
df['stage'] = 'GEN'

#state
df['state']  = 'COLORADO'

#special
df['special'] = 'FALSE'

#writein + unmark those parties
df['writein'] = df['candidate'].apply(get_writein)
df['writein'] = df['writein'].astype(str)

df['party_detailed'] = np.where((df['writein'] == 'TRUE') & (df['party_detailed'] == 'NONPARTISAN'), "", df['party_detailed'])
df['party_simplified'] = np.where((df['writein'] == 'TRUE') & (df['party_simplified'] == 'NONPARTISAN'), "", df['party_simplified'])

#state po
df['state_po'] = 'CO'

#date
df['date'] = '2020-11-03'

#year
df['year'] = '2020'

#state fips
df['state_fips'] = '08'
df['state_fips'] = df['state_fips'].astype(str)

#state cen
df['state_cen'] = '84'

#state ic
df['state_ic'] = '62'

#readme
df['readme_check'] = 'FALSE'

# DC changes 8/25/21
statewide_offices = ['US PRESIDENT','US SENATE','SUPREME COURT','COURT OF APPEALS',
    'AMENDMENT B (CONSTITUTIONAL)','AMENDMENT C (CONSTITUTIONAL)',
    'AMENDMENT 76 (CONSTITUTIONAL)','AMENDMENT 77 (CONSTITUTIONAL)',
    'PROPOSITION EE (STATUTORY)','PROPOSITION 113 (STATUTORY)','PROPOSITION 114 (STATUTORY)',
    'PROPOSITION 115 (STATUTORY)','PROPOSITION 116 (STATUTORY)','PROPOSITION 117 (STATUTORY)',
    'PROPOSITION 118 (STATUTORY)']
    # where office is in statewide offices, make district statewide, else leave alone
df['district'] = np.where(df['office'].isin(statewide_offices), "STATEWIDE", df['district'])

#drop renfernda rows that are accidentally included because of "0" in the votes column 
#(in addition to yes/no votes)
df = df[~((df['candidate']=="")&((df['office'].str.contains("STATUTORY"))|(df['office'].str.contains("CONSTITUTIONAL"))))].copy()

# added quote numeric
df.to_csv('cleaned/2020-co-precinct-general.csv', index = None, quoting=csv.QUOTE_NONNUMERIC)
    
    
