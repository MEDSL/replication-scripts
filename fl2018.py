#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import numpy as np
import os
import re
import csv
pd.options.display.max_columns =37
pd.options.display.max_rows =1500

# fl_map ={0:'County Code (Three-character abbreviation)',
# 1:'County Name',
# 2: 'Election Number',
# 3: 'Election Date',
# 4: 'Election Name',
# 5: 'Unique Precinct Identifier',
# 6: 'Precinct Polling Location',
# 7: 'Total Registered Voters',
# 8: 'Total Registered Republicans',
# 9: 'Total Registered Democrats',
# 10: 'Total Registered All Other Parties',
# 11: 'Contest Name',
# 12:'District',
# 13:'Contest Code',
# 14:'Candidate/Retention/Issue Name/WriteInsCast/OverVotes/UnderVotes',
# 15:'Candidate Party (abbreviation)',
# 16:'Candidate Florida Voter Registration System ID Number',
# 17:'DOE Assigned Candidate Number',
# 18:'Vote Total'}

# path to raw data folders
base_path = '/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/FL/raw'
# change working directory
os.chdir(base_path)
# get list of folders
files = sorted([file for file in os.listdir() if (file not in ['.DS_Store','miami_dade_EL30A.LST','DAD_PctResults20181106.txt'])])
# create list that will store county_level dfs (one for each folder)
county_df_list = []

for file in files:
  if not file.startswith("._"):
    df = pd.read_csv(file, delimiter = '\t',header=None)
    df = df[[1,5,6,7,11,12,14,15,18]].copy()
    # add col names
    df.columns = ['county_name','precinct_code','precinct_name','registered','office','district','candidate','party_detailed','votes']
    county_df_list = county_df_list + [df]

df = pd.concat(county_df_list).reset_index(drop=True)
df = df.applymap(lambda x:x.upper() if type(x) == str else x) 
#precinct field combine
df['precinct'] = np.where(df['precinct_name'].isnull(), df['precinct_code'].astype(str),
                          df['precinct_name'].astype(str)+ '_'+df['precinct_code'].astype(str))
df = df.drop(columns = ['precinct_name','precinct_code'])

registered = df[['county_name','precinct','registered']].drop_duplicates()
registered = registered.rename(columns = {'registered':'votes'})
registered['office'] = 'REGISTERED VOTERS - TOTAL'
registered['district'] = ""
registered['candidate'] = ""
registered['party_detailed'] = ""

df = pd.concat([df,registered])

def jud_cands(x):
    if 'RETENTION' in x:
        return x.replace('RETENTION OF ','')
    else: return ""
df['candidate'] = np.where(df['office'].str.contains('RETENTION'),
                          df['office'].apply(jud_cands) + ' - ' + df['candidate'],
                          df['candidate'])
df['office'] = np.where(df['office'].str.contains('RETENTION'),
                          "RETENTION " + df['district'],
                          df['office'])

def get_magnitude(x, y):
    if 'VOTE FOR' in x:
        return int(re.findall('\d+',x)[-1])
    if 'VOTE FOR' in y:
        return int(re.findall('\d+',y)[0])
    else: return 1
df['magnitude'] = df.apply(lambda x: get_magnitude(x['district'], x['office']), axis=1)  

#district
df['district'] = df['district'].str.strip()
def fix_district(x):
    if 'FIRST' in x: return '001'
    if 'SECOND' in x: return '002'
    if 'THIRD' in x: return '003'
    if 'FOURTH' in x: return '004'
    if 'FIFTH' in x: return '005'
    if 'AT LARGE' in x: return x
    if x == 'CENTRAL DISTRICT SEAT 2': return 'CENTRAL, SEAT 2'
    if x == 'NORTHERN DISTRICT SEAT 1': return 'NORTHERN, SEAT 1'
    if 'DISTRICT' in x: return re.findall('\d+', x)[0].zfill(3)
    if 'JUDICIAL CIRCUIT' in x and 'GROUP' in x:
        return re.findall('\d+', x)[0].zfill(3) + ', GROUP ' + re.findall('\d+', x)[-1]
    if 'JUDICIAL CIRCUIT' in x: return re.findall('\d+', x)[0].zfill(3)
    if 'WATERWAY AND BEACH COMMISSION' in x: return x.split(', ')[-1]
    else: return x
df['district'] = df.district.apply(fix_district)

#candidate
df['candidate'] = df['candidate'].str.replace('\.','',regex=True)
df['candidate'] = df['candidate'].str.replace(',','',regex=True)
df['candidate'] = df['candidate'].replace({'YES FOR APPROVAL':"YES",
                                          'NO FOR REJECTION':"NO",
                                          'WRITEINVOTES':"WRITEIN",
                                          'DESANTIS / NUÑEZ':'RON DESANTIS',
                                           'FOLEY / TUTTON':'RYAN CHRISTOPHER FOLEY',
                                           'GIBSON / WILDS':'KYLE "KC" GIBSON',
                                           'GILLUM / KING':'ANDREW GILLUM',
                                           'RICHARDSON / ARGENZIANO':'DARCY G RICHARDSON',
                                           'STANLEY / MCJURY':'BRUCE STANLEY',
                                          'NARRAGANSETT (NARRIE) SMITH':'NARRAGANSETT "NARRIE" SMITH',
                                          'ROBERT (BOB) PLUMMER':'ROBERT "BOB" PLUMMER'})


def miami_dade():
    # miami dade
    with open('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/FL/raw/miami_dade_EL30A.LST') as f:
        lineList = f.readlines()
    lst = [i.strip() for i in lineList]

    # creates dictionary with index of precincts and candidates
    separator_dic = {}
    separator_list = []
    for elem, index in zip(lst, np.arange(len(lst))):
        if elem == '':
            if lst[index+1] == "":
                pass
            else:
                separator_dic[index+1] = lst[index+1]
                separator_list = separator_list + [index+1] 

    modes=["TOTAL",'ED OSS','ED IVO','VBM','EV OSS','EV IVO','PROV']
    cols = ['precinct','magnitude','office','candidate'] + modes

    # parses awful .LST file
    discard_info=lst[58:63] + ['\x1bE']
    from tqdm.notebook import tqdm
    dade_list = []
    for index,num in zip(separator_list, (np.arange(len(separator_list)))):
        if "PRECINCT" in separator_dic[index]: 
            precinct = separator_dic[index]
        else:
            if num < 35100:
                race_list = lst[separator_list[num]:separator_list[num+1]]
            else:
                race_list = lst[separator_list[num]:]
            race_list = [i for i in race_list if i not in discard_info]
            office = race_list[0]
            if race_list[1] == '*** See Addendum ***': 
                magnitude = race_list[2]
                candidates = [re.split(r'\.  \.' ,i)[0].strip() for i in race_list[3:]]
                votes = [re.findall(r'\d+[,]\d+|\d+\.\d+|\.\d+|\d+',i)  for i in race_list[3:]]
                votes = [i if len(i)==7 else [i[0]] + i[2:] for i in votes]
            else: 
                magnitude = race_list[1]
                candidates = [re.split(r'\.  \.' ,i)[0].strip() for i in race_list[2:]]
                votes = [re.findall(r'\d+[,]\d+|\d+\.\d+|\.\d+|\d+',i)  for i in race_list[2:]]
                votes = [i if len(i)==7 else [i[0]] + i[2:] for i in votes]
            for vote, candidate in zip(votes,candidates):
                dade_list = dade_list + [[precinct, magnitude, office, candidate] + vote]

    ### partial clean of parsed results ###

    # concat df + drop bad scraped rows
    dade=pd.DataFrame(dade_list, columns = cols)
    dade = dade[~((dade['candidate'].str.contains('RUN DATE:11/28/18 10:59 A'))|
               (dade['candidate']=='Total'))].copy()
    dade = dade[~(dade['magnitude']=='*** Contest not counted ***')].copy()


    # fix dtypes
    for col in modes:
        dade[col] = dade[col].str.replace(',','',regex=True).astype(int)

    #ensure vote counts match
    #dade['total_check']=dade[modes[1:]].sum(axis=1)
    #dade[dade['TOTAL']!=dade['total_check']]

    #melt
    dade = pd.melt(dade,
                  id_vars = ['precinct','office','candidate','magnitude'],
                  value_vars = modes[1:],
                  value_name = 'votes',
                  var_name = 'mode')
    # fixing formats
    dade['magnitude'] = dade['magnitude'].replace('Vote for ', '',regex=True).astype(int)
    dade['candidate'] = dade['candidate'].str.upper().replace({'OVER VOTES':"OVERVOTES",
                                                              "UNDER VOTES": "UNDERVOTES",
                                                              'WRITE-IN':'WRITEIN',
                                                              'NO/NO/NO':'NO',
                                                               'NO/NO/NON':'NO',
                                                              'YES/SI/WI':'YES'})
    dade['candidate'] = dade['candidate'].str.replace('\.','',regex=True).str.replace('\* CANDIDATE WITHDREW \*','- CANDIDATE WITHDREW',regex=True)
    dade['party_detailed'] = [i.split('(')[-1].replace(')','') if '(' in i else "" for i in dade['candidate']] 
    dade['candidate'] = [i.split('(')[0] if '(' in i else i for i in dade['candidate']] 
    dade['candidate'] = dade['candidate'].str.strip()

    def get_district(x):
        #if 'AT LARGE' in x: return x
        if ('DIST' in x) and ('COURT OF APPEAL' not in x): return re.findall('\d+', x)[0].zfill(3)
        if x == 'CIRCUIT JUDGE, 11TH JUDICIAL GROUP 14': return '011, GROUP 14'
        if 'GROUP' in x: return re.findall('\d+', x)[0].zfill(3)
        if x in ['UNITED STATES SENATOR',
           'GOVERNOR/LIEUTENANT GOVERNOR', 'ATTORNEY GENERAL',
           'CHIEF FINANCIAL OFFICER', 'COMMISSIONER OF AGRICULTURE',
           'JUSTICE OF SUPREME COURT, LAWSON',
           'DISTRICT COURT OF APPEAL, EMAS',
           'DISTRICT COURT OF APPEAL, FERNANDEZ',
           'DISTRICT COURT OF APPEAL, SHEPARD LINDSEY',
           'DISTRICT COURT OF APPEAL, LUCK',
           'CIRCUIT JUDGE, 11TH JUDICIAL GROUP 14',
           'CONST AMEND 1: HOMESTEAD PROP TAX EXEMPTION',
           'CONST AMEND 2: LIMIT PROP TAX ASSESSMENTS',
           'CONST AMEND 3: GAMBLING IN FLORIDA',
           'CONST AMEND 4: VOTING RESTORATION',
           'CONST AMEND 5: SUPERMAJORITY RAISE TAX/FEES',
           'CONST AMEND 6: RIGHTS OF CRIME VICTIMS',
           'CONST AMEND 7: RESPONDER/MILITARY BENEFITS',
           'CONST AMEND 9: OFS OIL/GAS DRILLING/VAPING',
           'CONST AMEND 10: STATE/LOCAL GOVT STRUCTURE',
           'CONST AMEND 11: PROP RIGHTS LANG/CRIM STAT',
           'CONST AMEND 12: LOBBYING & ABUSE OF OFFICE',
           'CONST AMEND 13: ENDS DOG RACING']: return "STATEWIDE"
        if 'SEAT' in x: return re.findall('\d+', x)[0].zfill(3)
        else: return ""
    dade['district'] = dade.office.apply(get_district)

    #format retentions
    def retention(office, candidate):
        if "COURT" in office: return office.split(', ')[1] + ' - ' + candidate
        else: return candidate
    dade['candidate'] = dade.apply(lambda x: retention(x['office'],x['candidate']),axis=1)

    dade['office'] = ['RETENTION ' + i.split(', ')[0] if 'COURT' in i else i for i in dade['office']]

    #add county_name
    dade['county_name'] = 'MIAMI-DADE'


    def get_voter_statistics():
      precinct = []
      reg = []
      ballots = []
      for i in lst:
          if ('PRECINCT' in i) and (i not in precinct):
              precinct = precinct + [i]
          if ('REGISTERED VOTERS - TOTAL' in i):
              reg = reg + [i]
          if ('BALLOTS CAST - TOTAL' in i):
              ballots = ballots + [i]
      stats = pd.DataFrame({'precinct':precinct, 'registered':reg,'ballots':ballots})
      stats['registered'] = [re.findall('\d+',i)[0] for i in stats['registered'].str.replace(',','')]
      ballot_modes=[re.findall('\d+',i) for i in stats['ballots'].str.replace(',','')]
      modes=["TOTAL",'ED OSS','ED IVO','VBM','EV OSS','EV IVO','PROV']
      ballots_cast=pd.DataFrame(ballot_modes,columns = modes)

      stats=stats.join(ballots_cast).drop(columns = 'ballots')
      stats = pd.melt(stats,
                              id_vars = 'precinct',
                            value_vars = modes+ ['registered'],
                            value_name = 'votes',
                            var_name = 'mode')
      stats['office'] = np.where(stats['mode']=='registered', 'REGISTERED VOTERS - TOTAL', 'BALLOTS CAST')
      stats['mode'] = stats['mode'].replace('registered','TOTAL')    
      stats['candidate'] = ""
      stats['county_name'] = 'MIAMI-DADE'
      stats['party_detailed'] = ""
      stats['district'] = ""
      return stats
    dade = pd.concat([dade, get_voter_statistics()])   

    # get mode
    mode_dic = dict(zip(['ED OSS', 'ED IVO', 'VBM', 'EV OSS', 'EV IVO', 'PROV'],
               ['ELECTION DAY - OSS', 'ELECTION DAY - IVO', "MAIL", 'EARLY VOTING - OSS',
               'EARLY VOTING - IVO', 'PROVISIONAL']))
    dade['mode'] = dade['mode'].replace(mode_dic)

    return dade
# COMMISSIONER OF AGRICULTURE off a bit
# Gov overcounted
# US SENATE off a bit

# everything else looks good
# https://www.miamidade.gov/elections/library/reports/2018-general-election-certified-results.pdf


# append miami-dade results
df = pd.concat([df, miami_dade()])

# other modes
df['mode'] = df['mode'].fillna('TOTAL')

df['candidate']=df['candidate'].str.replace('\s+', ' ',regex=True)
df['candidate'] = df['candidate'].replace({'ALFRED "MIKE" N LAWRENCE':'ALFRED N "MIKE" LAWRENCE',
'JOHN "JACK" C GORMAN':'JOHN C "JACK" GORMAN',
'STEPHEN "STEVE" R BOWEN':'STEPHEN R "STEVE" BOWEN',
'LAWSON - YES':'ALAN LAWSON - YES',
'LAWSON - NO':'ALAN LAWSON - NO',
'LAWSON - OVERVOTES':'ALAN LAWSON - OVERVOTES',
'LAWSON - UNDERVOTES':'ALAN LAWSON - UNDERVOTES',
'SHEPARD LINDSEY - NO':'NORMA SHEPARD LINDSEY - NO',
'SHEPARD LINDSEY - YES':'NORMA SHEPARD LINDSEY - YES',
'SHEPARD LINDSEY - OVERVOTES':'NORMA SHEPARD LINDSEY - OVERVOTES',
'SHEPARD LINDSEY - UNDERVOTES':'NORMA SHEPARD LINDSEY - UNDERVOTES',
'FERNANDEZ - YES':'IVAN F FERNANDEZ - YES',
'FERNANDEZ - NO':'IVAN F FERNANDEZ - NO',
'FERNANDEZ - OVERVOTES':'IVAN F FERNANDEZ - OVERVOTES',
'FERNANDEZ - UNDERVOTES':'IVAN F FERNANDEZ - UNDERVOTES',
'EMAS - YES':'KEVIN EMAS - YES',
'EMAS - NO':'KEVIN EMAS - NO',
'EMAS - OVERVOTES':'KEVIN EMAS - OVERVOTES',
'EMAS - UNDERVOTES':'KEVIN EMAS - UNDERVOTES',
'LUCK - YES':'ROBERT JOSHUA LUCK - YES',
'LUCK - NO':'ROBERT JOSHUA LUCK - NO',
'LUCK - OVERVOTES':'ROBERT JOSHUA LUCK - OVERVOTES',
'LUCK - UNDERVOTES':'ROBERT JOSHUA LUCK - UNDERVOTES',
})

df.loc[(df['candidate'].str.contains('ALAN LAWSON -')),'district'] = "STATEWIDE"
df.loc[(df['candidate'].str.contains('KEVIN EMAS -')),'district'] = "003"
df.loc[(df['candidate'].str.contains('IVAN F FERNANDEZ -')),'district'] = "003"
df.loc[(df['candidate'].str.contains('NORMA SHEPARD LINDSEY -')),'district'] = "003"
df.loc[(df['candidate'].str.contains('ROBERT JOSHUA LUCK -')),'district'] = "003"


#remaining district info scraped to district field
def finish_district(x):
  if "DISTRICT NO." in x:
    return re.findall('\d+', x)[0].zfill(3) + ', '
  else: return ""
df['district_append']  = df['office'].apply(finish_district)
df['district'] = df['district_append'] + df['district']

# office
def fix_office(x):
    if x == 'st. augustine port'.upper(): return x + ' WATERWAY AND BEACH COMMISSION'
    if 'DISTRICT COURT OF APPEAL' in x: return 'RETENTION DISTRICT COURT OF APPEAL'
    if x == 'UNITED STATES SENATOR': return 'US SENATE'
    if x == 'REPRESENTATIVE IN CONGRESS': return "US HOUSE"
    if x == 'STATE SENATOR': return "STATE SENATE"
    if x =='STATE REPRESENTATIVE': return "STATE HOUSE"
    if x == 'CIRCUIT JUDGE, 11TH JUDICIAL GROUP 14': return 'CIRCUIT JUDGE'
    if x =='GOVERNOR/LIEUTENANT GOVERNOR': return "GOVERNOR"
    if 'REPRESENTATIVE IN CONGRESS' in x: return "US HOUSE"
    if 'STATE REPRESENTATIVE' in x: return "STATE HOUSE"
    if "STATE SENATOR" in x: return "STATE HOUSE"
    if x == 'RETENTION JUSTICE OF SUPREME COURT': return 'RETENTION JUSTICE OF THE SUPREME COURT'

    # scrape out district info that has been copied over
    if " - SEAT" in x: return re.sub(r" - SEAT \d+", "", x)
    if ', GROUP ' in x: return re.sub(r", GROUP \d+", "", x)
    if ", SEAT" in x: return re.sub(r", SEAT \d+", "", x)
    if 'DISTRICT NO. ' in x: return re.sub(r"DISTRICT NO. \d+", "", x)
    else: return x
df['office'] = df.office.apply(fix_office)
amend_map = dict(zip(['CONST AMEND 1: HOMESTEAD PROP TAX EXEMPTION',
       'CONST AMEND 2: LIMIT PROP TAX ASSESSMENTS',
       'CONST AMEND 3: GAMBLING IN FLORIDA',
       'CONST AMEND 4: VOTING RESTORATION',
       'CONST AMEND 5: SUPERMAJORITY RAISE TAX/FEES',
       'CONST AMEND 6: RIGHTS OF CRIME VICTIMS',
       'CONST AMEND 7: RESPONDER/MILITARY BENEFITS',
       'CONST AMEND 9: OFS OIL/GAS DRILLING/VAPING',
       'CONST AMEND 10: STATE/LOCAL GOVT STRUCTURE',
       'CONST AMEND 11: PROP RIGHTS LANG/CRIM STAT',
       'CONST AMEND 12: LOBBYING & ABUSE OF OFFICE',
       'CONST AMEND 13: ENDS DOG RACING'],
        ['AMENDMENT NO. 1: INCREASED HOMESTEAD PROPERTY TAX EXEMPTION',
       'AMENDMENT NO. 2: LIMITATIONS ON PROPERTY TAX ASSESSMENTS',
       'AMENDMENT NO. 3: VOTER CONTROL OF GAMBLING IN FLORIDA',
       'AMENDMENT NO. 4: VOTING RESTORATION AMENDMENT',
       'AMENDMENT NO. 5: SUPERMAJORITY VOTE REQUIRED TO IMPOSE, AUTHORIZE, OR RAISE STATE TAXES OR FEES',
       'AMENDMENT NO. 6: RIGHTS OF CRIME VICTIMS; JUDGES',
       'AMENDMENT NO. 7: FIRST RESPONDER AND MILITARY MEMBER SURVIVOR BENEFITS; PUBLIC COLLEGES AND UNIVERSITIES',
       'AMENDMENT NO. 9: PROHIBITS OFFSHORE OIL AND GAS DRILLING; PROHIBITS VAPING IN ENCLOSED INDOOR WORKPLACES',
       'AMENDMENT NO. 10: STATE AND LOCAL GOVERNMENT STRUCTURE AND OPERATION',
       'AMENDMENT NO. 11: PROPERTY RIGHTS; REMOVAL OF OBSOLETE PROVISION; CRIMINAL STATUTES',
       'AMENDMENT NO. 12: LOBBYING AND ABUSE OF OFFICE BY PUBLIC OFFICERS',
       'AMENDMENT NO. 13: ENDS DOG RACING']))
df['office'] = df['office'].replace(amend_map)

#dataverse
def get_dataverse(x):
    if x =='US SENATE': return 'SENATE'
    if x =='US HOUSE': return 'HOUSE'
    if x in ['RETENTION DISTRICT COURT OF APPEAL','RETENTION JUSTICE OF THE SUPREME COURT',
            "STATE HOUSE",'STATE SENATE', 'GOVERNOR', 'ATTORNEY GENERAL',
           'CHIEF FINANCIAL OFFICER', 'COMMISSIONER OF AGRICULTURE','CIRCUIT JUDGE']: return "STATE"
    if 'AMENDMENT' in x: return 'STATE'
    else: return "LOCAL"
df['dataverse'] = df.office.apply(get_dataverse)
df.loc[(df['district']=='')&(df['dataverse']!='LOCAL'),'district'] = 'STATEWIDE'
df.loc[df['office'].str.contains('AMENDMENT'),'district'] = 'STATEWIDE'
df['district'] = df['district'].replace({'INC., SEAT 2':'SEAT 2',
  'AT LARGE, DISTRICT 6':'006, AT LARGE'})

# party
party_map = {"NOP":"NONPARTISAN",
"DEM":"DEMOCRAT",
"REP":"REPUBLICAN",
"LPF":"LIBERTARIAN",
"REF":"REFORM",
"PSL":"SOCIALIST",
"GRE":"GREEN",
"CPF":"CONSTITUTION",
"IND":"INDEPENDENT",
"ECO":"ECOLOGY",
            ' ':'',
            'NPA':'No Party Affiliation'.upper()}
df['party_detailed'] = df['party_detailed'].replace(party_map)
df.loc[(df['office'].str.contains('AMENDMENT')),'party_detailed'] = ""


def get_simplified(x):
    if x in ['DEMOCRAT','REPUBLICAN','LIBERTARIAN','NONPARTISAN',""]: return x
    else: return "OTHER"
df['party_simplified'] = df.party_detailed.apply(get_simplified)
df.loc[df['candidate'].str.contains('- YES|- NO|- UNDERVOTES|- OVERVOTES'),'party_detailed'] = 'NONPARTISAN'
df.loc[df['candidate'].str.contains('- YES|- NO|- UNDERVOTES|- OVERVOTES'),'party_simplified'] = 'NONPARTISAN'

#writein
df['writein'] = np.where(df['candidate']=='WRITEIN','TRUE','FALSE')


df['state'] = 'FLORIDA'

# After county name fix, append on fips codes
fips = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2018-precincts/help-files/county-fips-codes.csv')

fips = fips.applymap(str)
fips['state'] = fips['state'].str.upper()

df=df.applymap(lambda x: x.strip() if type(x)==str else x)
df = pd.merge(df, fips, on = ['state','county_name'], 
             how = 'left')


df['jurisdiction_name'] = df['county_name']
df['jurisdiction_fips'] = df['county_fips']
df['county_name'] = df['county_name'].str.replace('\.','',regex=True)

df['date'] = '2018-11-06'
df['special'] = 'FALSE'
df['year'] = 2018
df['stage'] = 'GEN'


# reg voters
df.loc[df['office'].isin(['REGISTERED VOTERS - TOTAL', "BALLOTS CAST"]),'dataverse'] = ""
df.loc[df['office'].isin(['REGISTERED VOTERS - TOTAL', "BALLOTS CAST"]),'magnitude'] = 0
df['magnitude'] =df['magnitude'].astype(int)


#for miami-dade
# COMMISSIONER OF AGRICULTURE off a bit
# Gov overcounted
# US SENATE off a bit
df['readme_check'] = np.where((df['county_name']=='MIAMI-DADE')&(df['office'].isin(['GOVERNOR','US SENATE','COMMISSIONER OF AGRICULTURE'])),
                             'TRUE','FALSE')

# merge state codes
state_codes=pd.read_csv('/Users/declanchin/Desktop/MEDSL/2020-precincts/help-files/merge_on_statecodes.csv')
state_codes['state'] = state_codes['state'].str.upper()
df = df.merge(state_codes, on = 'state', how = 'left')

# organize
df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()


df.to_csv('../2018-fl-precinct-general-updated.csv', index=False,quoting=csv.QUOTE_NONNUMERIC)

