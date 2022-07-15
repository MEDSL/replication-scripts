#!/usr/bin/env python
# coding: utf-8

# In[332]:


import pandas as pd
import numpy as np
import os
import re
import pyreadr
import csv
pd.options.display.max_columns = 125
pd.options.display.max_rows =1500


# In[338]:


# first get data for 12 counties with same election reporting
# original cleaning results saved by JC, but missing magnitude
def get_12_counties():
    rdata=pyreadr.read_r('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/AZ/raw/az_normal_raw.Rdata')
    df=rdata[None].drop_duplicates().copy()
    df['Vote Total'] = df['Vote Total'].astype(int)
    df = df[['Precinct','Contest', 'Choice','Party', 'county','Vote Total']].copy()
    df.columns = ['precinct','office','candidate','party_detailed','county_name','votes']
    df['candidate'] = [i.split(',')[1].strip() + " " + i.split(',')[0] if (',' in i) else i for i in df['candidate']]
    df['candidate'] =df['candidate'].replace(['WRITE-IN','UNDER VOTES','OVER VOTES'],
                                            ['WRITEIN','UNDERVOTES','OVERVOTES'])
    df['writein'] = np.where(df['candidate']=='WRITEIN','TRUE','FALSE')

    # original cleaning excluded magnitude, merging on county/office
    counties = ['apache.txt',
     'cochise.txt',
     'gila.txt',
     'graham.txt',
     'greenlee.txt',
     'mohave.txt',
     'navajo.txt',
     'pima.txt',
     'pinal.txt',
     'santa_cruz.txt',
     'la_paz.txt',
     'yuma.txt']
    os.chdir('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/AZ/raw')
    dic_list = []
    for file in counties:
        t = pd.read_csv(file,
                    '\t', header = None)
        t['magnitude'] = [i[-3:-1] for i in t[0]]
        t['magnitude'] = t['magnitude'].astype(int)
        t['office'] = [i[111:167] for i in t[0]]
        t['office'] = t['office'].str.upper().str.strip()
        t['county_name'] = file.replace('.txt',"").replace("_",' ').title()
        dic = t[['county_name','office','magnitude']]
        dic_list = dic_list + [dic]
    mag_map = pd.concat(dic_list).drop_duplicates()
    df['office'] = df['office'].str.upper().str.strip()
    df = df.merge(mag_map, on = ['county_name','office'], how = 'left')
    # add mode
    df['mode'] = 'TOTAL'


    ## one office is the same name but a different contest ID, need to append contest ID to differentiate
    ## adding contest ID from raw
    df.loc[df['office'] == 'WHITE MOUNTAIN COMMUNITIES SPECIAL HEALTH CARE DIST','office'] = 'WHITE MOUNTAIN COMMUNITIES SPECIAL HEALTH CARE DISTRICT - ID 0332'
    df.loc[df['office'] == 'WHITE MOUNTAIN COMMUNITIES SPECIAL HEALTH CARE DIST.','office'] = 'WHITE MOUNTAIN COMMUNITIES SPECIAL HEALTH CARE DISTRICT - ID 0333'

    return df


# In[339]:


# Coconino different format
# delimited by commas, but commas in candidate names. So delimiter specifies commas with no trailing whitespace
def get_coconino():
    df2 = pd.read_csv('6975.Coconino.Detail.txt', skipfooter=1,
                      delimiter=',(?!\s)',index_col=False, header=None,engine = 'python')
    df2 = df2.rename(columns = {1:'precinct_id',
                               2:'precinct',
                               4:'office_id',
                               5:'office',
                               13:'candidate_id',
                               14:'candidate',
                               16:'party_id',
                               17:'party_detailed',
                               19: 'mode_id',
                               20: 'mode',
                               22:'votes'})
    df2 = df2[[
     'precinct',
     'office',
     'candidate',
     'party_detailed',
     'mode',
     'votes']]
    df2['precinct'] = df2['precinct'].str.replace('\"','',regex=True)
    df2['office'] = df2['office'].str.replace('\"','',regex=True)
    df2['candidate'] = df2['candidate'].str.replace('\"','',regex=True)
    df2['party_detailed'] = df2['party_detailed'].str.replace('\"','',regex=True)
    df2['mode'] = df2['mode'].str.replace('\"','',regex=True)
    df2 = df2[~((df2['office']=='Race Statistics')|
          (df2['candidate'].isin(['Number of Precincts for Race', 'Number of Precincts Reporting','Times Counted'])))]
    reg = df2[(df2['candidate']=='Registered Voters')&(df2['votes']!=0)].copy()
    reg['office'] = 'Registered Voters'.upper()
    reg['candidate'] = ""
    reg = reg.drop_duplicates(subset = ['precinct'])
    #add reg voters
    df2 = pd.concat([df2[~(df2['candidate']=='Registered Voters')], reg])
    # fix candidate
    df2['candidate'] = [i.split(', ')[1] + " " + i.split(', ')[0] if (', ' in i) else i.upper() for i in df2['candidate']]
    df2.loc[df2['candidate'].str.contains('WRITE'),'candidate'] = 'WRITEIN'
    df2['candidate'] = df2['candidate'].replace(['TIMES OVER VOTED', 'NUMBER OF UNDER VOTES'],
                                               ['OVERVOTES','UNDERVOTES'])
    # # get party
    df2.loc[df2['candidate'].isin(['TIMES BLANK VOTED', 'OVERVOTES', 'UNDERVOTES', 'WRITEIN','REGISTERED VOTERS']),
       'party_detailed'] = ""
    # office
    # df2['office'] = [i.split(' (')[0] if (" (" in i) else i for i in df2['office']]

    # drop various forms of double counting
    df2 = df2[~((df2['mode'].isin(['Total']))&(df2['office']!='REGISTERED VOTERS'))] 
    df2 = df2[~(df2['precinct']=='Election Total')].copy()
    df2['writein'] = np.where(df2['candidate']=='WRITEIN','TRUE','FALSE')

    def get_mag(x):
        if 'ELECT ' in x: return re.findall('\d+',x)[-1]
        if x =='REGISTERED VOTERS': return 0
        else: return 1
    df2['magnitude'] = df2['office'].apply(get_mag)
    df2['office'] = df2['office'].str.replace(' \(ELECT \d\)', "", regex=True)
    # add county
    df2['county_name'] = "COCONINO"
    return df2


# In[340]:


# maricopa different format
def get_maricopa():
    df3 = pd.read_csv('maricopa.txt',
                     delimiter = '\t')
    df3= df3[['PRECINCT_NAME','CANDIDATE_FULL_NAME','CONTEST_FULL_NAME',
        'TOTAL','contest_vote_for','IS_WRITEIN','undervote','overvote']]
    over_under = pd.melt(df3, id_vars = ['PRECINCT_NAME','CONTEST_FULL_NAME',
        'CANDIDATE_FULL_NAME','contest_vote_for','IS_WRITEIN'],
                 value_vars = ['TOTAL','overvote','undervote'],
                 value_name = 'votes',
                 var_name='mode')
    over_under = over_under[over_under['mode'].str.contains("over|under")]
    over_under = over_under.drop_duplicates(subset = ['PRECINCT_NAME','CONTEST_FULL_NAME','contest_vote_for',
                                        'mode','votes'])
    over_under['CANDIDATE_FULL_NAME'] = over_under['mode']
    over_under = over_under[~(over_under['CONTEST_FULL_NAME']=='Registration & Turnout')]

    df3 = df3.drop(columns = ['undervote','overvote'])
    df3 = df3.rename(columns = {"TOTAL":"votes"})
    df3 = pd.concat([df3,over_under])
    df3['mode']= 'TOTAL'
    df3.columns = ['precinct','candidate','office','votes','magnitude','writein','mode']
    df3['writein'] =df3['writein'].replace({0:'FALSE',1:"TRUE"})
    df3['office'] = np.where(df3['office'] == 'Registration & Turnout', df3['candidate'], df3['office'])
    df3['candidate'] = np.where(df3['candidate']==df3['office'], "", df3['candidate'])
    df3['candidate'] = df3['candidate'].str.upper()
    df3['office'] = df3['office'].str.upper()
    df3['mode'] = np.where(df3['office'].str.contains('EARLY'), 'EARLY',
                          np.where(df3['office'].str.contains('ELECTION DAY'),'ELECTION DAY',df3['mode']))
    # strip party info to new field, give apt names
    df3['party_detailed'] = [i.split(' - ')[0] for i in df3['candidate']]
    df3['party_detailed'] = df3['party_detailed'].replace(['', 'REP', 'DEM', 'GRN',
                                                           'WRITE-IN CANDIDATE', 'NON', 'IND',
                                                           'OVERVOTE', 'UNDERVOTE'],
                                                         ['', 'REPUBLICAN', 'DEMOCRAT', 'GREEN',
                                                           '', 'NONPARTISAN', 'INDEPENDENT',
                                                           '', ''])
    # get candidates without party, first name then last name
    df3['candidate'] = [i.split(' - ')[1] if (' - ' in i) else i for i in df3['candidate']]
    df3['candidate'] = [i.split(', ')[1] + " " + i.split(', ')[0] if (', ' in i) else i for i in df3['candidate']]
    df3['county_name'] = "maricopa".upper()
    df3['office'] = df3['office'].str.replace(' \(VOTE \d\)', "", regex=True)
    
    # fixing bad file format error where yes/no not included in cand name
    y_n = ['YES','NO'] * int(len(df3[(df3['office'] == 'BUCKEYE UNION HSD #201 QUESTION')&
                                     (df3['candidate']=='LEASE SALE')])/2)
    df3.loc[(df3['office'] == 'BUCKEYE UNION HSD #201 QUESTION')&(df3['candidate']=='LEASE SALE'),
           'candidate'] = y_n
    
    return df3  


# In[341]:


# yavapai different format
def get_yavapai():
    df4 = pd.read_csv('yavapai.txt',
                     delimiter = ',',skiprows=2)
    df4 = df4[['PrecinctName','VoteForValue','ContestTitle',
         'Candidate Name','Party Name','Votes','VoteType']]
    df4.columns = ['precinct','magnitude','office','candidate','party_detailed','votes','mode']
    # dropping unnecessary info
    df4=df4[:28861]
    df4['magnitude']=df4['magnitude'].fillna(0)
    df4['mode']=df4['mode'].fillna("TOTAL")
    df4['mode'] = df4['mode'].replace(['E', 'P', 'C', 'A'],['EARLY','PROVISIONAL','VOTE CENTER','ABSENTEE'])
    df4 = df4.fillna("")
    df4['votes'] = df4['votes'].astype(int)
    # get writein
    df4.loc[df4['candidate'].str.contains('WRITE'),'candidate'] = 'WRITEIN'
    df4['writein'] = np.where(df4['candidate'] == 'WRITEIN','TRUE','FALSE')

    # drop agg
    df4 = df4[~(df4['candidate']=='TotalVotes')]

    # fix cand
    df4['candidate'] = [i.split(', ')[1] + " " + i.split(', ')[0] if (', ' in i) else i.upper() for i in df4['candidate']]
    df4['candidate'] = [i.split(' ')[0] + ' "'+ i.split(' ')[1].replace('""','')+'" ' + i.split(' ')[2] if '""' in i else i for i in df4['candidate']]
    df4['county_name'] = "yavapai".upper()
    df4['office'] = np.where(df4['candidate']=='REGISTEREDVOTERS','REGISTERED VOTERS', df4['office'])
    df4.loc[df4['office']=='REGISTERED VOTERS','candidate'] = ""
    return df4


# In[342]:


def get_district(x):
    if "REP CD" in x: return re.findall('\d+',x)[0].zfill(3)
    if "DIST" in x:
        if len(re.findall('\d+',x)) == 0: return ""
        if len(re.findall('\d+',x)) == 1: return re.findall('\d+',x)[0].zfill(3)
        if x in ['BOARD MEMBER - MESCAL-J6 FIRE DIST. 20',
                 'BOUSE ELEM. DIST. 26 BOUSE ELEMENTARY SD 26',
                'QUARTZSITE ELEM. DIST. 4 QUARTZSITE ELEMENTARY SD 4']: return re.findall('\d+',x)[-1].zfill(3)
        if x in ['YAVAPAI COLLEGE DIST. 1: 6-YEAR TERM','YAVAPAI COLLEGE DIST. 3: 6-YEAR TERM']:
            return re.findall('\d+',x)[0].zfill(3)
    if "DST" in x:
        return re.findall('\d+',x)[0].zfill(3)
    if "USD" in x:
        if x == 'BOARD MEMBER 2YR LAKE HAVASU USD 1': return '001'
        if 'USD #' in x: return re.findall('\d+',x)[0].zfill(3)
        if 'YR' in x or "YEAR" in x: return ""
        if "QUESTION" not in x and "PROPOSITION" not in x:
            if len(re.findall('\d+',x)): return re.findall('\d+',x)[0].zfill(3)
            else: return ""
        else: return ""
    if "DIV" in x:
        if x in ['COURT OF APPEALS, DIVISION II-ECKERSTROM',
       'COURT OF APPEALS DIVISION II - ESPINOSA',
       'COURT OF APPEALS, DIVISION II - STARING']: return '002'
        else: return re.findall('\d+',x)[0].zfill(3)
    if x == 'APPEALS COURT SWANN, PETER': return "001"
    if "PREC" in x:
        return re.findall('\d+',x)[0].zfill(3)
    if "HSD" in x:
        if x == 'MINGUS UNION HSD: 2-YEAR TERM': return ''
        if "WARD" in x: return re.findall('\d+',x)[0].zfill(3) + ', WARD ' + re.findall('\d+',x)[-1]
        else: return re.findall('\d+',x)[0].zfill(3)
    if "PCT" in x: return re.findall('\d+',x)[0].zfill(3)
    if "ESD #" in x: return re.findall('\d+',x)[0].zfill(3)
    if "ESD" in x: 
        if len(re.findall('\d+',x)) == 0: return ""
        if "YEAR" in x: return ""
        else: return re.findall('\d+',x)[-1].zfill(3)
    if " SD " in x: return re.findall('\d+',x)[0].zfill(3)
    if x in ['BOARD MEMBER MCCD 3','BOARD MEMBER NACFD#1']: return re.findall('\d+',x)[0].zfill(3)
    else: return ""


# In[343]:


def fix_retention_offices(df):
    # fix candidate field for over/under/yes/no
    df.loc[df['candidate'].str.contains('YES'), 'candidate'] = "YES"
    df.loc[(df['candidate'].str.contains('NO ')|(df['candidate']=="NO")), 'candidate'] = "NO"
    df.loc[df['candidate'].str.contains('UNDERVOTE'), 'candidate'] = "UNDERVOTES"
    df.loc[df['candidate'].str.contains('OVERVOTE'), 'candidate'] = "OVERVOTES"

    # fix supreme court retention offices
    df['candidate'] = np.where((df['office'].str.contains("SUPREME")&(df['office'].str.contains("BOLICK"))), 
                                'CLINT BOLICK - '+df['candidate'], 
                               df['candidate'])
    df['candidate'] = np.where((df['office'].str.contains("SUPREME")&(df['office'].str.contains("PELANDER"))), 
                               df['candidate'] + ' - JOHN PELANDER', 
                               df['candidate'])

    df['office'] = np.where((df['office'].str.contains("SUPREME")), 
                               "RETENTION SUPREME COURT JUSTICE", 
                               df['office'])

    # fix retention candidates for superior court
    df['candidate'] = np.where((df['office'].str.contains("SUPERIOR")&(df['office'].str.contains("RETAIN"))), 
                               df['candidate'] + " - " + df['office'], 
                               df['candidate'])
    df['candidate'] = df['candidate'].str.replace('RETAIN SUPERIOR COURT JUDGE - ',"",regex=True)
    df['office'] = np.where((df['office'].str.contains("SUPERIOR")&(df['office'].str.contains("RETAIN"))), 
                               "RETENTION SUPERIOR COURT JUSTICE", 
                               df['office'])

    df['candidate'] = np.where((df['office'].str.contains("SUPERIOR")&(df['office'].str.contains(","))), 
                               df['candidate'] + " - " + df['office'], 
                               df['candidate'])
    df['candidate'] = df['candidate'].str.replace('SUPERIOR COURT ',"",regex=True)
    df['office'] = np.where((df['office'].str.contains("SUPERIOR")&(df['office'].str.contains(","))), 
                               "RETENTION SUPERIOR COURT JUSTICE", 
                               df['office'])
    # regorganize last name to back
    df['temp_cand'] = "temp"
    last_name=df[(df['candidate'].str.contains(' - '))&(df['candidate'].str.contains(','))]['candidate'].str.findall(r'- .+,')
    df.loc[(df['candidate'].str.contains(' - '))&(df['candidate'].str.contains(',')), 'temp_cand'] = last_name

    df['temp_cand'] = [i[0].replace('- ','').replace(',','') for i in df['temp_cand']]
    df['candidate'] = df['candidate'].str.replace(r'- .+,','- ', regex=True)
    df['candidate'] = np.where(df['temp_cand']!='t', df['candidate'] + ' ' + df['temp_cand'], df['candidate'])
    df = df.drop(columns = 'temp_cand')


    # fix court of appeals retention races
    df['candidate'] = np.where(df['office'] == 'COURT OF APPEALS, DIVISION II-ECKERSTROM', 
                               df['candidate'] + ' - PETER J ECKERSTROM', df['candidate'])

    df['candidate'] = np.where(df['office'] == 'COURT OF APPEALS DIVISION II - ESPINOSA', 
                               df['candidate'] + ' - PHILLIP G ESPINOSA', df['candidate'])

    df['candidate'] = np.where(df['office'] == 'COURT OF APPEALS, DIVISION II - STARING', 
                               df['candidate'] + ' - CHRISTOPHER STARING', df['candidate'])

    df['candidate'] = np.where(df['office'] == 'APPEALS COURT SWANN, PETER', 
                               df['candidate'] + ' - PETER SWANN', df['candidate'])

    df.loc[df['office'].str.contains('APPEALS'),'office'] = "RETENTION COURT OF APPEALS JUSTICE"

    # names not included for certain superior courts but division is kept so they are properly differentiated
    # as there is only one candidate per divions
    df.loc[df['office'].str.contains('JUDGE OF THE SUPERIOR COURT|SUPERIOR COURT JUDGE|JUDGE OF SUPERIOR COURT'),
           'office'] = 'SUPERIOR COURT JUSTICE'


    # oops did it backwards
    df.loc[df['candidate'].str.contains('YES - '),'candidate'] = df.loc[df['candidate'].str.contains('YES - '),'candidate'].replace('YES - ','',regex=True) + ' - YES'
    df.loc[df['candidate'].str.contains('NO - '),'candidate'] = df.loc[df['candidate'].str.contains('NO - '),'candidate'].replace('NO - ','',regex=True) + ' - NO'
    df.loc[df['candidate'].str.contains('OVERVOTES - '),'candidate'] = df.loc[df['candidate'].str.contains('OVERVOTES - '),'candidate'].replace('OVERVOTES - ','',regex=True) + ' - OVERVOTES'
    df.loc[df['candidate'].str.contains('UNDERVOTES - '),'candidate'] = df.loc[df['candidate'].str.contains('UNDERVOTES - '),'candidate'].replace('UNDERVOTES - ','',regex=True) + ' - UNDERVOTES'
    df.loc[df['candidate'].str.contains('TIMES BLANK VOTED - '),'candidate'] = df.loc[df['candidate'].str.contains('TIMES BLANK VOTED - '),'candidate'].replace('TIMES BLANK VOTED - ','',regex=True) + ' - TIMES BLANK VOTED'
    return df


# In[390]:


def fix_office(x):
    x = x.replace("  ",' ')
    if "REP CD" in x or 'U.S. REP' in x: return "US HOUSE"
    if x =='U.S. SENATOR' or x == 'UNITED STATES SENATOR': return "US SENATE"
    if "STATE SENAT" in x: return "STATE SENATE"
    if "STATE REP" in x: return "STATE HOUSE"
    if "PROPOSITION 125" in x: return "STATE PROPOSITION 125"
    if "PROPOSITION 126" in x: return "STATE PROPOSITION 126"
    if "PROPOSITION 127" in x: return "STATE PROPOSITION 127"
    if "PROPOSITION 305" in x: return "STATE PROPOSITION 305"
    if "PROPOSITION 306" in x: return "STATE PROPOSITION 306"
    if "JUSTICE OF THE PEACE" in x:
        if "DIST." in x: return re.sub(r' DIST\. \d',' -',x)
        if 'PREC' in x or "PCT" in x: return "JUSTICE OF THE PEACE"
        if "DISTRICT" in x or "DISTICT" in x: return "JUSTICE OF THE PEACE"
        if ':' in x: return re.sub(r': ',' - ',x)
        if "JUSTICE OF THE PEACE -" in x: return x
        else: return re.sub(r'JUSTICE OF THE PEACE ','JUSTICE OF THE PEACE - ',x)
    if "JUSTICE OF PEACE" in x: return "JUSTICE OF THE PEACE"
    if "CONSTABLE" in x:
        x = x.replace(', JUSTICE','')
        if "DIST." in x: return re.sub(r' DIST\. \d',' -',x)
        if 'PREC' in x or "PCT" in x: return "CONSTABLE"
        if "DISTRICT" in x or "DISTICT" in x: return "CONSTABLE"
        if ':' in x: return re.sub(r': ',' - ',x)
        if "CONSTABLE-" in x: return re.sub('CONSTABLE-','CONSTABLE - ', x)
        if "CONSTABLE -" in x: return x
        else: return re.sub(r'CONSTABLE ','CONSTABLE - ',x)
    if "BRD MEMBER" in x: return x.replace('BRD MEMBER','BOARD MEMBER')
    if x =='CLERK OF SUPERIOR COURT': return "CLERK OF THE SUPERIOR COURT"
    else: return x

office_map = {'SEDONA FIRE DIST.':'SEDONA FIRE DISTRICT BOARD MEMBER',
              'DAISY MOUNTAIN FIRE DIST.':'DAISY MOUNTAIN FIRE DISTRICT',
             'DAISY MOUNTAIN FIRE DIST':'DAISY MOUNTAIN FIRE DISTRICT',
             'BOARD MEMBER MESCAL J-SIX FIRE DIST.':'BOARD MEMBER MESCAL J-SIX FIRE DISTRICT',
             'BOARD MEMBER - MESCAL-J6 FIRE DIST. 20':'BOARD MEMBER MESCAL J-SIX FIRE DISTRICT',
             'BOARD MEMBER WHITERIVER UNIFIED SCHOOL DISTRICT 20':'BOARD MEMBER WHITERIVER UNIFIED SCHOOL DISTRICT',
             'BOARD MEMBER WHITERIVER USD 20':'BOARD MEMBER WHITERIVER UNIFIED SCHOOL DISTRICT',
             'WICKENBURG COUNCIL MEMBER: 4-YEAR TERM':'COUNCILMEMBER - WICKENBURG',
             'WICKENBURG-COUNCIL':'COUNCILMEMBER - WICKENBURG',
              'SUPERINTENDENT':"SUPERINTENDENT OF PUBLIC INSTRUCTION",
             'SUPERINTENDENT OF PUBLIC INSTRUCTION':"SUPERINTENDENT OF PUBLIC INSTRUCTION", 
             'SUP OF PUBLIC INSTRUCTION':"SUPERINTENDENT OF PUBLIC INSTRUCTION",
             'SUPER OF PUBLIC INSTRUCTION':"SUPERINTENDENT OF PUBLIC INSTRUCTION", 
             'SUPERINTENDENT OF PUBLIC INSTR':"SUPERINTENDENT OF PUBLIC INSTRUCTION",
             'BOARD MEMBER SUPERSTITION FIRE & MEDICAL DISTRICT':'BOARD MEMBER SUPERSTITION FIRE AND MEDICAL DISTRICT',
             'SUPERSTITION FIRE AND MED DIST':'BOARD MEMBER SUPERSTITION FIRE AND MEDICAL DISTRICT',
             'STATE MINE INPSECTOR':'STATE MINE INSPECTOR',
             'CORPORATION COMMISSION':'CORPORATION COMMISSIONER',
             'EVIT - DIST 7':'BOARD MEMBER EAST VALLEY INSTITUTE OF TECHNOLOGY',
             'BOARD MEMBER-GOLDER RANCH FIRE DIST. 12':'BOARD MEMBER GOLDER RANCH FIRE DISTRICT',
             'CLERK OF SUP COURT':'CLERK OF THE SUPERIOR COURT',
             'SUPERTENDENT OF PUBLIC INSTRUCTION':'SUPERINTENDENT OF PUBLIC INSTRUCTION'}


# In[391]:


def fix_candidate(x):
    x = x.replace('.','')
    x = x.replace(',','')
    x = x.replace("''",'"')
    x = x.replace('(','"')
    x = x.replace(')','"')
    if x == 'WRITE-IN CANDIDATE': return "WRITEIN"
    if x =='CEL� HANCOCK': return "CELE HANCOCK"
    if x =='JOE "PEP" GUZM�N': return 'JOE "PEP" GUZMAN'
    if x =='MART�N J QUEZADA': return 'MARTIN J QUEZADA'
    if x =='RAQUEL TER�N': return 'RAQUEL TERAN'
    if x =='RAÚL GRIJALVA' or x =='RA�L GRIJALVA': return 'RAUL GRIJALVA'
    if x =='TATE MICHAEL': return "MICHAEL TATE"
    if x == 'WILLIAM PIERCE': return 'WILLIAM "BILL" PIERCE'
    if x == 'WILLIAM BILL PIERCE': return 'WILLIAM "BILL" PIERCE'
    if x == 'RUBERT LUPE': return "RUBERT LUPE SR"
    if x == 'WALTER BLACKMAN': return 'WALTER "WALT" BLACKMAN'
    if x == 'ALBERT PESQUERIA': return 'ALBERT PESQUEIRA'
    if x =='DANIEL HERNANDEZ': return "DANIEL HERNANDEZ JR"
    return x


# In[392]:


def fix_party(x):
    if "DEM" in x: return "DEMOCRAT"
    if "REP" in x: return "REPUBLICAN"
    if "GREEN" in x or "GRN" in x: return "GREEN"
    if "IND" in x: return "INDEPENDENT"
    if x =='NON' or x=='NP': return "NONPARTISAN"
    if x == 'LBT': return "LIBERTARIAN"
    if x=='.': return ""
    else: return x

def fill_missing_parties():
    #creates dictionary with keys as candidates with multiple parties, values as the non-blank party
    candidate_parties = df.groupby(['candidate'])['party_detailed'].unique()
    correct_pairing = dict()
    for (candidate, parties) in candidate_parties.iteritems():
        if len(parties) > 1:
            parties = list(parties)
            correct_pairing[candidate] = parties[0]        
    candidates=list(correct_pairing.keys())
    #loops through and assigns each candidate to nonblank party
    for candidate in candidates:
        df['party_detailed']=np.where(df['candidate']==candidate, 
                                      correct_pairing[candidate],
                                     df['party_detailed'])
    df.loc[df['candidate'].isin(['WRITEIN','']),'party_detailed']=""
    
def party_simp(x):
    if x in ['DEMOCRAT','REPUBLICAN','NONPARTISAN','LIBERTARIAN',""]: return x
    else: return "OTHER"


# In[393]:


def get_dataverse(x):
    if x == 'US HOUSE': return 'HOUSE'
    if x =='US SENATE': return 'SENATE'
    if x in ['GOVERNOR', 'ATTORNEY GENERAL', 'STATE TREASURER',
 'SUPERINTENDENT OF PUBLIC INSTRUCTION', 'STATE MINE INSPECTOR',
 'CORPORATION COMMISSIONER','SECRETARY OF STATE','STATE PROPOSITION 125',
 'STATE PROPOSITION 126','RETENTION SUPREME COURT JUSTICE'
 'STATE PROPOSITION 127', 'STATE PROPOSITION 305','STATE PROPOSITION 306',
    'CLERK OF THE SUPERIOR COURT', 'SUPERIOR COURT JUSTICE',
       'RETENTION SUPREME COURT JUSTICE',
       'RETENTION COURT OF APPEALS JUSTICE',
       'RETENTION SUPERIOR COURT JUSTICE',
        "STATE HOUSE",'STATE SENATE']: 
        return 'STATE'
    if x=='REGISTERED VOTERS': return ''
    else: return 'LOCAL'


# In[394]:


# merge state codes, county fips, jurisdiction fips for any state
# takes in df (dataframe), name of state, case insensitive (string)

def merge_regional_codes(df, state_full):
    # add state column and state codes
    df['state'] = state_full.upper()
    state_codes = pd.read_csv('../../../help-files/merge_on_statecodes.csv')
    state_codes['state'] = state_codes['state'].str.upper()
    state_codes = state_codes[state_codes['state']==state_full.upper()]
    df=df.merge(state_codes, on='state')
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


# In[395]:


# parse raw
df = get_12_counties()
df2 = get_coconino()
df3 = get_maricopa()  
df4 = get_yavapai()

# concat all files together
df = pd.concat([df,df2,df3,df4])
df = df.replace('\s+'," ")
df = df.apply(lambda x: x.strip() if type(x)==str else x)
df['county_name'] = df['county_name'].str.upper()
df['precinct'] = df['precinct'].str.upper()
df['district'] = df['office'].apply(get_district)
# fix retention races, main reason for reclean
df = fix_retention_offices(df)
df['office'] = df['office'].apply(fix_office)
df['office'] = df['office'].replace(office_map).replace('\.','',regex=True)

# fix statewide district
statewide = ['GOVERNOR', 'US SENATE', 'ATTORNEY GENERAL', 'STATE TREASURER',
 'SUPERINTENDENT OF PUBLIC INSTRUCTION', 'STATE MINE INSPECTOR',
 'CORPORATION COMMISSIONER','SECRETARY OF STATE','STATE PROPOSITION 125',
 'STATE PROPOSITION 126','RETENTION SUPREME COURT JUSTICE'
 'STATE PROPOSITION 127', 'STATE PROPOSITION 305','STATE PROPOSITION 306']
df.loc[df['office'].isin(statewide),'district'] = 'STATEWIDE'
df['candidate'] = df['candidate'].apply(fix_candidate)
df['candidate'] = df['candidate'].str.replace('\s+'," ", regex=True).str.strip().str.upper()

#party
df['party_detailed'] = df['party_detailed'].fillna("").apply(fix_party)
df.loc[df['office'].isin(['RETENTION SUPREME COURT JUSTICE',
                         'RETENTION COURT OF APPEALS JUSTICE',
                         'RETENTION SUPERIOR COURT JUSTICE']),'party_detailed'] = 'NONPARTISAN'
df.loc[df['office'].str.contains('PROP'),'party_detailed'] = ""
fill_missing_parties()
df['party_simplified'] = df['party_detailed'].apply(party_simp)
# dataverse
df['dataverse'] = df['office'].apply(get_dataverse)
#MERGING regional codes
df = merge_regional_codes(df, 'Arizona')
# other
df['mode']=df['mode'].str.upper().replace('PROV',"PROVISIONAL")
df['special'] = 'FALSE'
df['year'] = 2018
df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['stage'] = "GEN"


# In[396]:


df = df.loc[:,['precinct', 'office', 'party_detailed', 'party_simplified', 'mode',
       'votes', 'county_name', 'county_fips', 'jurisdiction_name',
       'jurisdiction_fips', 'candidate', 'district', 'magnitude', 'dataverse',
       'year', 'stage', 'state', 'special', 'writein', 'state_po',
       'state_fips', 'state_cen', 'state_ic', 'date', 'readme_check']]


# In[397]:


df.to_csv('../2018-az-precinct-general-updated.csv', index=False,quoting=csv.QUOTE_NONNUMERIC)


# In[ ]:




