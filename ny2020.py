#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 07:10:43 2021

@author: darsh/declan
"""

import pandas as pd
import numpy as np
import csv
import os
cwd = os.getcwd()
df = pd.read_csv(cwd + '/raw/20201103__ny__general__precinct.csv', ',')

# data scraping errors in Lewis, fix precinct names
df.loc[(df['county']=='Lewis')&(df['office']=='U.S. House')&(df['precinct']=='New Brem'),'precinct'] = ['New Bremen 1']*8 + ['New Bremen 2']*8 + ['New Bremen 3']*8
df.loc[(df['county']=='Lewis')&(df['office']=='U.S. House')&(df['precinct']=='West Turin'), 'precinct'] = ['West Turin 1']*8 + ['West Turin 2']*8+['West Turin 3']*8+['West Turin 4']*8
df.loc[(df['county']=='Lewis')&(df['office']=='U.S. House')&(df['precinct']=='Lyonsdale'),'precinct'] = ['Lyonsdale 1']*8 + ['Lyonsdale 2']*8 + ['Lyonsdale 3']*8
# data scraping errors in Oneida, fix precinct names
df.loc[(df['county']=='ONEIDA'.title())&(df['office']=='State Senate')&(df['precinct']=='Forestport 1'),'precinct'] = ['Forestport 1','Forestport 2']*5
df.loc[(df['county']=='ONEIDA'.title())&(df['office']=='State Senate')&(df['precinct']=='Marshall 1'),'precinct'] = ['Marshall 1','Marshall 2']*5
df.loc[(df['county']=='ONEIDA'.title())&(df['office']=='State Senate')&(df['precinct']=='Sangerfield 1'),'precinct'] = ['Sangerfield 1','Sangerfield 2']*5
# data scraping errors in Monroe, fix precinct names
df.loc[(df['county']=='Monroe')&(df['office']=='State Assembly')&(df['precinct'].str.upper()=='LEG. DIST. 24 12'),'precinct'] = ['Leg. Dist. 24 12','Leg. Dist. 25 12']*8
# data scraping errors in Suffolk, fix precinct names
correct = ["Southampton " + (str(i)) for i in np.arange(1,43)]
df.loc[(df['county']=='Suffolk')&
        (df.drop(columns = 'votes').duplicated()),'precinct'] = correct*10

# data scraping errors in Washington, drop bad row
df=df.drop(df.loc[(df['county']=='WASHINGTON'.title())&(df['candidate']=='Kanye West')&
        (df['precinct']==('Kingsbury 9'))&(df['votes']==2)].index)

# before any manipulation, manually add missing precinct from albany county
df.loc[-1] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Michelle Hinchey','DEM',183,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-2] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Richard M. Amedure, Jr.','REP',275,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-3] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Richard M. Amedure, Jr.','CON',42,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-4] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Michelle Hinchey','WOR',19,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-5] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Robert D. Alft, Jr.','GRE',3,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-6] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Richard M. Amedure, Jr.','IND',11,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-7] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Write-ins','',0,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-8] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Over Votes','',0,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]
df.loc[-9] = ['Albany','0168 BERNE ED 1','State Senate', 46.0, 'Under Votes','',10,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan]

#capitalize and fillna
df = df.applymap(lambda x:x.upper() if type(x) == str else x)
df.fillna('', inplace=True)
#-----------------------------------------------------------------------------------------
#Dropping some stats that aren't necesary
to_drop = ['TOTAL','TOTALS','TOTAL VOTES','BALLOTS','BALLOTS CAST']
for term in to_drop:
    indexNames = df[(df['candidate'] == term)].index
    df.drop(indexNames, inplace = True)

#we are given mode breakdown and a total in the 'votes' column
#where mode breakdown is valid, we go as usual, where mode breakdown is null we keep the 'total' mode
def mode_type(elec,abse,earl,affi):
    #mode is total
    if elec == '' and abse == '' and earl == '' and affi == '':
        return 'total'
    else:
        return 'breakdown'
df['mode_type'] = df.apply(lambda df: mode_type(df['election_day'],df['absentee'],df['early_voting'],df['affidavit']),axis=1)
#-----------------------------------------------------------------------------------------
#making columns with numbers clean ints
def num(x):
    if x == '':
        x = 0
    x = str(x)
    x = x.replace(',','')
    x = x.replace(' ','')
    x = float(x)
    x = int(round(x))
    return abs(x)
df['total'] = df['votes'].apply(num) #changed the 'votes' column to 'total'
df['election_day'] = df['election_day'].apply(num)
df['absentee'] = df['absentee'].apply(num)
df['early_voting'] = df['early_voting'].apply(num)
df['affidavit'] = df['affidavit'].apply(num)
#-----------------------------------------------------------------------------------------
#office, only 4 offices for now
def office(x):
    if x == 'PRESIDENT':
        return 'US PRESIDENT'
    elif x == 'STATE ASSEMBLY':
        return 'STATE HOUSE'
    elif x == 'U.S. HOUSE':
        return 'US HOUSE'
    else:
        return x
df['office'] = df['office'].apply(office)
#-----------------------------------------------------------------------------------------
def district(x):
    if x != '':
        x = str(int(x))
        return x.zfill(3)
    else:
        return 'STATEWIDE'
df['district'] = df['district'].apply(district)
#-----------------------------------------------------------------------------------------
#comparing the 'total' column with sum of all modes ('mode_total') to find discrepancies

df['mode_total'] = 0
def sum_votes (a,b,c,d):
    total = sum([a,b,c,d])
    return total
df['mode_total'] = df.apply(lambda df: sum_votes(df['election_day'],df['absentee'],df['early_voting'],df['affidavit']),axis=1)

#mark mismatches with readme_check
def compare(t,mt):
    if mt != 0 and mt != t: # abs(v-t)>1: #for big differences
        return 'TRUE'
    else:
        return 'FALSE'
df['readme_check'] = df.apply(lambda df: compare(df['total'],df['mode_total']),axis=1)

# mismatch = df.loc[df['readme_check'] == 'TRUE']
# mismatch.to_csv('mismatched_totals', quoting=csv.QUOTE_NONNUMERIC)
#!!!around 12,000 rows where the modes don't add up to the total 'votes' column. 10k have diff smaller than 5!!!
#CHECKED ORIGINAL PDFs OF RAW DATA -> 4 counties have weird mode breakdown (explained in README_check)

#MONTGOMERY and HERKIMER COUNTY - missing hand counted mode from scraping
# -> given total - (sum of all other modes) = hand counted total

def handcount(c,readme_check,mt,t):
    if c == 'MONTGOMERY' or c == 'HERKIMER':
        if readme_check == 'TRUE':
            return abs(t-mt)
        #mark which rows were correct, we can drop these 'handcount' values later
        else:
            return 'drop'
    else:
        return 'drop'
df['HAND COUNTED'] = df.apply(lambda df: handcount(df['county'],df['readme_check'],df['mode_total'],df['total']),axis=1)

#Cattaraugus and NASSAU county: only absentee specified, has total votes.
# total - absentee = election day votes -> we will assume all remaining votes are election day
def elec_day(county,total,election_day,absentee,early_voting):
    if county == 'CATTARAUGUS':
        return total
    elif county == 'NASSAU':
        return total - absentee - early_voting
    else:
        return election_day
df['election_day'] = df.apply(lambda df: elec_day(df['county'],df['total'],df['election_day'],df['absentee'],df['early_voting']),axis=1)
#-----------------------------------------------------------------------------------------
#mode
#keep 'total' if mode breakdown isn't provided

#~melt~
df = pd.melt(df, id_vars = ['county','precinct','office','district','candidate','party','mode_type'],
              value_vars= ['total','election_day','absentee','early_voting','affidavit','HAND COUNTED'],
              var_name= 'mode', value_name= 'votes')

#drop rows with empty mode breakdowns
indexNames = df[(df['mode_type'] == 'total') & (df['mode'] != 'total')].index
df.drop(indexNames, inplace = True)
#drop empty 'hand counted' modes we marked in line 83
indexNames = df[(df['mode'] == 'HAND COUNTED') & (df['votes'] == 'drop')].index
df.drop(indexNames, inplace = True)
#drop totals where the mode breakdown is present. avoid double counting
indexNames = df[(df['mode_type'] == 'breakdown') & (df['mode'] == 'total')].index
df.drop(indexNames, inplace = True)
#dropping rows in STEBEN country with blank precinct value and null votes
indexNames = df[(df['county'] == 'STEUBEN') & (df['precinct'] == '')].index
df.drop(indexNames, inplace = True)
#-----------------------------------------------------------------------------------------
#UOCAVA ballots indicated in precinct. Votes only in absentee
#-> rename absentees in these rows to 'UOCAVA' and drop the rest
#-> change this precinct to 'COUNTY FLOATING'
def uocava(precinct,mode):
    if precinct == 'SPECIAL FEDERAL & SPECIAL PRESIDENTIAL' or precinct == 'MILITARY/FED/UOCAVA' or precinct == 'SPECIAL FEDERAL':
        if mode == 'absentee':
            return 'UOCAVA'
        else:
            return 'drop'
    elif 'EARLY VOTING' in precinct:
            return 'early_voting'
    else:
        return mode
df['mode'] = df.apply(lambda df: uocava(df['precinct'],df['mode']),axis=1)
indexNames = df[(df['mode'] == 'drop')].index
df.drop(indexNames, inplace = True)

def prec(precinct):
    if precinct == 'SPECIAL FEDERAL & SPECIAL PRESIDENTIAL' or precinct == 'MILITARY/FED/UOCAVA' or precinct == 'SPECIAL FEDERAL':
        return 'COUNTY FLOATING'
    elif 'EARLY VOTING' in precinct:
        return precinct[15:]
    else:
        return precinct
df['precinct'] = df['precinct'].apply(prec)
#-----------------------------------------------------------------------------------------

#standardize mode names
def mode2(m):
    if m == 'election_day':
        return 'ELECTION DAY'
    elif m == 'early_voting':
        return 'EARLY'
    elif m == 'affidavit':
        return 'PROVISIONAL'
    elif m == 'absentee':
        return 'ABSENTEE'
    elif m == 'total':
        return 'TOTAL'
    else:
        return m
df['mode'] = df['mode'].apply(mode2)
#-----------------------------------------------------------------------------------------
#parties, change names
df['party_detailed'] = df['party'].replace(['DEM','WOR','REP','CON','GRE','LBT','IND','SAM',
                                            'LIB','ECL','ROS','REF','REB','PTP','SNP','REP.',
                                            'CON.','IND.','LBN','WRITE-INS','NON','SCA','SCATTERING'],
                    ['DEMOCRAT', 'WORKING FAMILIES', 'REPUBLICAN', 'CONSERVATIVE', 'GREEN','LIBERTARIAN','INDEPENDENCE','SERVE AMERICA MOVEMENT',
                    'LIBERTARIAN','EDUCATION COMMUNITY LAW','REFORM','REFORM','REBUILD OUR STATE','PROTECT THE TAXPAYER','SAFE NEIGHBORHOODS','REPUBLICAN',
                     'CONSERVATIVE','INDEPENDENCE','LIBERTARIAN','','','',''])

def party(x):
    if x == 'DEMOCRAT' or x == 'REPUBLICAN' or x == 'LIBERTARIAN' or x == 'NON PARTISAN':
        return x
    elif x == '':
        return ''
    else:
        return 'OTHER'
df['party_simplified'] = df['party_detailed'].apply(party)
###### ADDING ALLEGANY DC (missing from openelection raw) ########

def get_allegany_data():
    os.chdir(cwd + '/raw/allegany')
    files = [i for i in os.listdir() if '.xlsx' in i]
    lst = []
    for sheet in files:
        al = pd.read_excel(sheet).fillna("")
        parties = list(al.columns)
        candidates=[cand + "-" for cand in list(al.loc[0])]
        cols = list(map(str.__add__, candidates, parties))
        cols[0] = 'precinct'
        al = al.iloc[1:]
        al.columns = cols
        al = pd.melt(al, id_vars = ['precinct'],
                value_vars= cols[1:],
                var_name = 'candidate', value_name = 'votes')
        al['office'] = sheet.replace('.xlsx',"").replace('allegany-',"")
        lst = lst + [al]
    al = pd.concat(lst)
    al = al.applymap(lambda x:x.upper() if type(x) == str else x)
    al = al[~(al['precinct']=='TOTAL')]
    al = al[~(al['votes']=='')].reset_index(drop=True)
    al['precinct'] = al['precinct'].str.strip()

    def get_party_detailed():
        al['party_detailed'] = [i.split('-')[1] for i in al['candidate']]
        party_map = {'DEM':'DEMOCRAT','REP':'REPUBLICAN','CON':'CONSERVATIVE',
                    'WOR': 'WORKING FAMILIES', 'GRE':'GREEN', 'UNNAMED: 8':"",
                    'LBT': 'LIBERTARIAN', 'IND': 'INDEPENDENCE','WRITE':""}
        al['party_detailed'] = al['party_detailed'].replace(party_map)
        al['candidate'] = [i.split('-')[0] for i in al['candidate']]
    get_party_detailed()

    def get_party_simplified(x):
        if x == 'DEMOCRAT' or x == 'REPUBLICAN' or x == 'LIBERTARIAN' or x == 'NONPARTISAN':
            return x
        elif x == '':
            return ''
        else:
            return 'OTHER'
    al['party_simplified'] = al['party_detailed'].apply(get_party_simplified)

    def fix_candidate(x):
        if x in ['IN', 'WRITE', 'INS']: return 'WRITEIN'
        if x == 'BIDEN': return 'JOSEPH R BIDEN'
        if x == 'TRUMP': return 'DONALD J TRUMP'
        if x == 'HAWKINS': return "HOWIE HAWKINS"
        if x == 'JORGENSEN': return 'JO JORGENSEN'
        if x == 'PIERCE': return "BROCK PIERCE"
        if x == 'SCOTT': return 'W ROSS SCOTT'
        if x == 'GIGLIO': return "JOSEPH M GIGLIO"
        if x == 'MITRANO': return 'TRACY MITRANO'
        if x == 'REED': return "TOM REED"
        if x == 'KOLSTEE': return 'ANDREW M KOLSTEE'
        if x == 'PUGLISI': return 'FRANK V PUGLISI'
        if x == 'BORRELLO': return 'GEORGE M BORRELLO'
        else: return x
    al['candidate'] = al.candidate.apply(fix_candidate)

    def get_district(x):
        if x == "US PRESIDENT": return 'STATEWIDE'
        else: return x.split('-')[1].zfill(3)
    al['district'] = al.office.apply(get_district)
    al['office'] = [i.split('-')[0] for i in al['office']]

    al['mode'] = 'TOTAL'
    al['county'] = 'ALLEGANY'
    os.chdir(cwd)
    return al
allegany = get_allegany_data()

df = pd.concat([df,allegany])
print(df[(df['candidate']=='GEORGE M BORRELLO')&((df['party_detailed']=='CONSERVATIVE'))&((df['county']=='ALLEGANY'))]['votes'].sum())

#-----------------------------------------------------------------------------------------
#fix county names
df['county'] = df['county'].fillna('')
df['county'] = df['county'].replace('SCHENECTEDY','SCHENECTADY').replace('Č','ALBANY')

df['county_name'] = df['county']
df['jurisdiction_name'] = df['county']
#-----------------------------------------------------------------------------------------
# adding in missing monroe data

# first remove inaccurate state house data
df=df[~((df['office']=='STATE HOUSE')&(df['county']=='MONROE')&(df['district']=='136'))]
#then remove inaccurate US House data
df=df[~((df['office']=='US HOUSE')&(df['county']=='ONEIDA')&(df['district']=='022'))]

# then add back with missing data
monroe = pd.read_csv(cwd + '/declan/monroe-missing-results.csv',dtype = {'district':str})
oneida_cg = pd.read_csv(cwd + '/declan/oneida-updated-results.csv',dtype = {'district':str})
rensselaer_state_house = pd.read_csv(cwd + '/declan/rensselaer-missing-results.csv',dtype = {'district':str})
df = pd.concat([df,monroe,oneida_cg,rensselaer_state_house])

#-----------------------------------------------------------------------------------------
#fetch county fips data as a dictionary
county_fips_path = '../../help-files/county-fips-codes.csv'
fips = pd.read_csv(county_fips_path, delimiter=',', header=0)
fips = pd.DataFrame(fips)
fips = fips.loc[fips['state']=='New York']
fips_dict = dict(zip(fips.county_name, fips.county_fips))
fips_dict['']=''

#use the dictionary to assign fips codes
def fips(x):
    code = fips_dict[x]
    return str(code)

df['county_fips'] = df['county_name'].apply(fips)
df['jurisdiction_fips'] = df['county_fips']


#-----------------------------------------------------------------------------------------
#created the list of all write-in candidates using the ones where 'party' = 'write-in' or 
# if 'candidate' contains 'write-in'

write_in_list = ['WRITE-INS','KANYE WEST','BRIAN CARROLL','GLORIA LA RIVA','JOSEPH KISHORE',
  'ROQUE "ROCKY" DE LA FUENTE','JADE SIMMONS','SHAWN HOWARD','MARK CHARLES',
  'WRITE-INS KANYE WEST','WRITE-INS BRIAN CARROLL','WRITE-INS JADE SIMMONS',
  'WRITE-INS DON BLANKENSHIP','WRITE-INS GLORIA LA RIVA','WRITE-INS MARK CHARLES','SCATTERING',
  'CHRIS JACOBS REP','BARBARA BELLER','DON BLANKENSHIP','PHIL COLLINS','PAUL HODGES','DARIO HUNTER',
  'GLORIA LARIVA','JOHN MANIMAS','DAVID A. MARTIN','JOE MCHUGH','KASEY WELLS','UNQUALIFIED WRITE-INS',
  'OLA HAWATMEH','KAYNE WEST','SCATTERING WRITE-INS','BRIAN CARROLL WRITE-INS','KEVIN COLLERY WRITE-INS',
  'PAUL CASIMANO','JILL PRATT','TIM DILLON WRITE-INS','BRANDON LYONS WRITE-INS','BRANDON LYONS','GREG GUVERA',
  'BENNY SMITH','RUTHERFORD SMITH','KANYE WEST WRITE-INS','ZENA PESTA','MATTHEW C. DUPRE','ROQUE DE LA FUENTE',
  'SCOTT MURPHY', 'KEVIN COLLERY', 'CHRISTOPHER BLAKE', 'WRITEIN',
# created for writeins in ONEIDA county updated results
  'DE SHIVA', 'NEITHER', 'TAALIB CONLEY', 'CONOR HOBBES',
       'LARRY HOGAN', 'FRANCIS WILLIAMS', 'JESUS', 'WALTER E BARRY IV',
       'GATO MAS', 'JAMES BROWN', 'SARITA RUIZ', 'BARBARA LEE RUIZ',
       'MARK BRAGER', 'SUE ARCURI FRANKFORT', 'MICKEY MOUSE', 'ABSTAIN',
       'JACKIE IZZO', 'STALIN', 'JAMES DESIRA', 'NONE', 'BERNARD HYMEN',
       'JOSH BLAIR', 'FRED ARCURI', 'MIKE GALIME', 'FRED ROBENSKI',
       'STEVE SOMNARS', 'KATCO', 'CHUCK NORRIS', 'JOE GRIFFO',
       'JAMES LEE TASIOR', 'NO CONFIDENCE', 'JOE ROGAN', 'ANYONE ELSE',
       'SUSAN ARCURI', 'RUSSELL BROOKS', 'ALAN PHIPPS']

def writein(x):
    if x in write_in_list:
        return 'TRUE'
    else:
        return 'FALSE'
df['writein'] = df['candidate'].apply(writein)


# indexNames = df[(df['writein'] == 'TRUE') & (df['votes'] == 0)].index
# df.drop(indexNames, inplace = True)



#-----------------------------------------------------------------------------------------
#standardize candidate names
def candidate(x):
    if 'KANYE WEST' in x:
        return 'KANYE WEST'
    elif 'GLORIA LA RIVA' in x:
        return 'GLORIA LA RIVA'
    elif  'JADE SIMMONS' in x:
        return 'JADE SIMMONS'
    elif 'MARK CHARLES' in x:
        return 'MARK CHARLES'
    elif 'DON BLANKENSHIP' in x:
        return 'DON BLANKENSHIP'
    elif 'BRANDON LYONS' in x:
        return 'BRANDON LYONS'
    elif 'JORGENSEN' in x:
        return 'JO JORGENSEN'
    elif 'BROCK PIERCE' in x:
        return 'BROCK PIERCE'
    if x == 'MIKE SIDERAKIS': return 'MICHAEL G SIDERAKIS'
    if x == 'ALEXIA WEIK': return 'ALEXIS WEIK'
    if x =='BILL WEBER': return 'WILLIAM J WEBER JR'
    if x =='JOE GRIFFO': return 'JOSEPH A GRIFFO'
    else:
        x = str(x)
        x = x.replace(".","")
        x = x.replace(",","")
        x = x.replace(" \'",' "')
        x = x.replace("\' ",'" ')
        x = x.replace('\xa0',' ')
    return x
df['candidate'] = df['candidate'].apply(candidate)

#fixing more names

old_format = ['WRITE-INS','SCATTERING WRITE-INS','UNQUALIFIED WRITE-INS','SCATTERING','VOIDS' , 'VOID',
              'OVER VOTES','BLANKS' ,'UNDER VOTES','BLANK','UNDER /OVER VOTES','BLANKS/VOIDS','KAYNE WEST',
              'WRITE-INS BRIAN CARROLL','BRIAN CARROLL WRITE-INS','CARROLL BRIAN','GLORIA LARIVA','ROQUE DE LA FUENTE',
              'DE LA FUENTE ROQU','BLANKENSHIP DON','PIERCE/BALLARD','ELIJAH REICHLIN- MELNICK',
              'ELIJAH REICHLIN MELNICK','JOHN KATKO','TEDRA COBB','CHAD MCEVOY', 'CHRIS JACOS',
              'CHRIS JACOBS REP','BRIAN MILLER','JAKE CORMELL','COMEGYS','KATKO','MANKTELOW','WILLIAMS',
              'HELMING','DUANE WHITMER', 'JAMES TEDISCO', 'KEVIN COLLERY WRITE-INS','THOMAS DANIEL',
              'BARBARA KIDNEY','ELISE STEFANIK','JOHN ZIELINSKI','KEITH PRICE JR','MARK GLOGOWSKI',
              'ROBERT SMULLEN','SHAUNA O TOOLE','STEPHEN HAWLEY','EDWARD RATH III','MICHAEL GENTILE',
              'NATHAN MCMURRAY','ANTHONY BRINDISI','BRIAN MANKTELOW','GEORGE M BORELLO','JACQUALINE BERGER',
              'CHELE FARLEY','TIM DILLON WRITE-INS']

new_format = ['WRITEIN','WRITEIN','UNQUALIFIED WRITEIN','WRITEIN','OVERVOTES','OVERVOTES','OVERVOTES','UNDERVOTES',
              'UNDERVOTES','UNDERVOTES','OVER/UNDER VOTES','OVER/UNDER VOTES','KANYE WEST','BRIAN CARROLL','BRIAN CARROLL','BRIAN CARROLL',
              'GLORIA LA RIVA','ROQUE "ROCKY" DE LA FUENTE','ROQUE "ROCKY" DE LA FUENTE','DON BLANKENSHIP',
              'BROCK PIERCE','ELIJAH REICHLIN-MELNICK','ELIJAH REICHLIN-MELNICK','JOHN M KATKO','TEDRA L COBB','CHAD J MCEVOY',
              'CHRIS JACOBS','CHRIS JACOBS','BRIAN D MILLER','JAKE CORNELL','SCOTT COMEGYS','JOHN M KATKO',
              'BRIAN D MANKTELOW','STEVEN WILLIAMS','PAMELA A HELMING','DUANE J WHITMER','JAMES N TEDISCO', 'KEVIN COLLERY',
              'THOMAS DANIEL QUITER','BARBARA A KIDNEY','ELISE M STEFANIK','JOHN S ZIELINSKI','KEITH D PRICE JR',
              'MARK E GLOGOWSKI','ROBERT J SMULLEN',"SHAUNA O'TOOLE",'STEPHEN M HAWLEY','EDWARD A RATH III',
              'MICHAEL C GENTILE','NATHAN D MCMURRAY','ANTHONY J BRINDISI','BRIAN D MANKTELOW','GEORGE M BORRELLO',
              'JACQUALINE G BERGER','CHELE C FARLEY','TIM DILLON']

df['candidate'] = df['candidate'].replace(old_format, new_format)
#-----------------------------------------------------------------------------------------
def dataverse(x):
    if x == 'US PRESIDENT':
        return 'PRESIDENT'
    elif x == 'US HOUSE':
        return 'HOUSE'
    elif x == 'STATE HOUSE' or x == 'STATE SENATE':
        return 'STATE'
df['dataverse'] = df['office'].apply(dataverse)
#-----------------------------------------------------------------------------------------
def readme(m):
    if m == 'HAND COUNTED':
        return 'TRUE'
    else:
        return 'FALSE'
df['readme_check'] = df['mode'].apply(readme)
#-----------------------------------------------------------------------------------------
df['stage'] = 'GEN'
df['special'] = 'FALSE'
df['date'] = '2020-11-03'
df['year'] = '2020'
df['state'] = 'NEW YORK'
df['state_po'] = 'NY'
df['state_fips'] = '36'
df['state_cen'] = '21'
df['state_ic'] = '13'
df['magnitude'] = '1'

df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes",
          "candidate", "district", "dataverse","state", "special", "writein","date","year",
          "county_name","county_fips", "jurisdiction_name","jurisdiction_fips", "stage",  "state_po",
          "state_fips", "state_cen", "state_ic", "readme_check", 'magnitude']].copy()

df = df.drop_duplicates()
df = df[~((df['writein']=='TRUE')&(df['votes']==0))].copy()

################## MANUAL FIXES OF INCORRECT VOTES ##################
df['votes'] = np.where(((df['county_name']=='ROCKLAND')&
  (df['candidate']=='JOSEPH R BIDEN')&
  (df['precinct']=='0263 RAMAPO 109')&
  (df['party_detailed']=='DEMOCRAT')), 1, df['votes'])

df['votes'] = np.where(((df['county_name']=='ROCKLAND')&
  (df['candidate']=='DONALD J TRUMP')&
  (df['precinct']=='0254 RAMAPO 100')&
  (df['party_detailed']=='REPUBLICAN')), 1, df['votes'])

# reassigning mode "TOTAL" when it appears within counities with more detailed mode breakdown
df['mode'] = np.where(((df['precinct']=='CUMULATIVE')&(df['mode']=='TOTAL')&(df['county_name']=='WYOMING')),
    'ELECTION DAY', df['mode'])

#add miscounts to readme_check, dont need to readme_check other scraping errors we handled
df['readme_check'] = np.where((df['office'] =='US PRESIDENT')&(df['county_name'].isin(['CAYUGA','PUTNAM','SUFFOLK'])),
    'TRUE','FALSE')


# weird error where overvotes are blank in state house district 117 in Jefferson
df.loc[(df['county_name']=='JEFFERSON')&(df['district']=='117')&(df['office']=='STATE HOUSE')&(df['candidate']==''),
    'candidate'] = 'OVERVOTES'

# incorrect party in raw
df.loc[(df['candidate']=='LESLIE DANKS BURKE')&(df['office']=='STATE SENATE')&(df['party_detailed']=='REFORM'),'party_detailed'] = 'SERVE AMERICA MOVEMENT'

# Putnam data updated https://putnamboe.com/wp-content/uploads/2020/12/2020-GENERAL-ELECTION-RESULTS-CERTIFIED-AMENDED-WEBPAGE-1.pdf
df.loc[(df['candidate']=='SUSAN J SERINO')&(df['party_detailed']=='REFORM')&
(df['district'] == '041'), 'party_detailed'] = 'REBUILD OUR STATE'

df.loc[(df['candidate']=='ROB ASTORINO')&(df['party_detailed']=='REFORM')&
(df['district'] == '040'), 'party_detailed'] = 'REBUILD OUR STATE'
df.loc[(df['candidate']=='ROB ASTORINO')&(df['precinct']=='CA 28')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='REBUILD OUR STATE'),'votes'] = 4

df.loc[(df['candidate']=='ROB ASTORINO')&(df['precinct']=='CA 02')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='CONSERVATIVE'),'votes'] = 46

df.loc[(df['candidate']=='ROB ASTORINO')&(df['precinct']=='CA 01')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='REPUBLICAN'),'votes'] = 191
df.loc[(df['candidate']=='ROB ASTORINO')&(df['precinct']=='CA 22')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='REPUBLICAN'),'votes'] = 401
df.loc[(df['candidate']=='ROB ASTORINO')&(df['precinct']=='PA 01')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='REPUBLICAN'),'votes'] = 386
df.loc[(df['candidate']=='ROB ASTORINO')&(df['precinct']=='SE 10')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='REPUBLICAN'),'votes'] = 354



df.loc[(df['candidate']=='PETER B HARCKHAM')&(df['precinct']=='CA 30')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='DEMOCRAT'),'votes'] = 193
df.loc[(df['candidate']=='PETER B HARCKHAM')&(df['precinct']=='CA 24')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='DEMOCRAT'),'votes'] = 210
df.loc[(df['candidate']=='PETER B HARCKHAM')&(df['precinct']=='CA 06')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='DEMOCRAT'),'votes'] = 182
df.loc[(df['candidate']=='PETER B HARCKHAM')&(df['precinct']=='CA 01')&
(df['district'] == '040')&
(df['office']=='STATE SENATE')&
(df['party_detailed']=='DEMOCRAT'),'votes'] = 145

### STATE HOUSE FIXES
df['candidate'] = df['candidate'].replace({'LAURA M JENA-SMITH':'LAURA M JENS-SMITH',
                                          'WILLIAM C VAN HELMON':'WILLIAM V VAN HELMOND',
                                          'FRED IANACCI':'ALFRED IANACCI',
                                          'MICHAEL A MARCANTONI':'MICHAEL A MARCANTONIO',
                                          'JOE SACKMAN':'JOSEPH J SACKMAN III',
                                          'HAN-KHON TO':'HAN-KOHN TO',
                                          'MIKE LAWLER':'MICHAEL V LAWLER',
                                          'JEN LUNSFORD': 'JENNIFER A LUNSFORD',
                                          'MONICA PIGA WALLACE': 'MONICA PIGA-WALLACE'})
df.loc[(df['candidate']=='CARRIE WOERNER')&(df['county_name']=='SARATOGA')&(df['party_detailed']=='SERVE AMERICAN MOVEMENT'),
      'party_detailed'] = 'INDEPENDENCE'

df.loc[(df['candidate']=='GAIL E TOSH')&(df['county_name']=='ONONDAGA'), 'district'] ='120'
df.loc[(df['candidate']=='GAIL E TOSH')&(df['county_name']=='ONONDAGA'), 'office'] ='STATE HOUSE'
df.loc[(df['candidate']=='WILLIAM A BARCLAY')&(df['county_name']=='ONONDAGA'), 'district'] = '120'
df.loc[(df['candidate']=='WILLIAM A BARCLAY')&(df['county_name']=='ONONDAGA'), 'office'] = 'STATE HOUSE'
df.loc[(df['candidate']=='DIA CARABAJAL')&(df['county_name']=='ONONDAGA'), 'district'] = '126'
df.loc[(df['candidate']=='JOHN LEMONDES JR')&(df['county_name']=='ONONDAGA'), 'district'] = '126'
df.loc[(df['candidate']=='ALBERT A STIRPE JR')&(df['county_name']=='ONONDAGA'), 'district'] = '127'
df.loc[(df['candidate']=='MARK R VENESKY')& (df['county_name']=='ONONDAGA'), 'district'] = '127'
df.loc[(df['candidate']=='PAMELA JO HUNTER')& (df['county_name']=='ONONDAGA'), 'district'] = '128'
df.loc[(df['candidate']=='STEPHANIE M JACKSON')& (df['county_name']=='ONONDAGA'), 'district'] = '128'
df.loc[(df['candidate']=='EDWARD G WEBER JR')& (df['county_name']=='ONONDAGA'), 'district'] = '129'
df.loc[(df['candidate']=='WILLIAM B MAGNARELLI')& (df['county_name']=='ONONDAGA'), 'district'] = '129'
# wrong party
df.loc[(df['candidate']=='KEVIN M BYRNE')& (df['county_name']=='WESTCHESTER') & (df['party_detailed']== 'REFORM'),'party_detailed'] = 'REBUILD OUR STATE'
df.loc[(df['candidate']=='CARRIE WOERNER')& (df['county_name']=='SARATOGA') & (df['party_detailed'] == 'WORKING FAMILIES'), 'party_detailed'] = 'INDEPENDENCE' 


df.to_csv('intermediate-2020-ny-precinct-general.csv', index = False, quoting=csv.QUOTE_NONNUMERIC)
