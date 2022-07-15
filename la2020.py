# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 10:52:10 2021

@author: abguh
"""

#https://stackoverflow.com/questions/43367805/pandas-read-excel-multiple-tables-on-the-same-sheetname
import pandas as pd
import os
pd.options.mode.chained_assignment = None  # default='warn'

path = 'C:/Users/abguh/Desktop/urop/2020-precincts/precinct/LA/raw/'
os.chdir(path)
import numpy as np

raw = 'Election+Results+(11-03-2020).xlsx'

def make_local_tables(file, sheetname):
    print('**NOW STARTING:',sheetname.upper() , '*****\n')
    df1 = pd.DataFrame()
    xl = pd.read_excel(file, sheet_name = sheetname, header = None).iloc[5:].reset_index(drop = True)
    #now find the indices of rows that start and end tables
    ends = xl[xl.iloc[:,0] == 'Early Voting'].index.tolist()
    starts = xl[xl.iloc[:,0] == 'Total Votes'].index.tolist()
    #dfs = list()
    for i in range(len(ends)):
        start = starts[i]
        end = ends[i]
        office = xl.iloc[start-2,0]
        #print('\n\n***** OFFICE', i , office, '****')
        xl.columns = xl.iloc[start-1]
        df = xl.iloc[start : end+1,:] #start at 0 
        df = df.rename(columns = {df.columns[0]:'precinct'})
        df = df.dropna(axis=1, how='all')
        columns = df.columns.tolist()
        #print(columns)
        df = pd.melt(df, id_vars = ['precinct'], var_name = 'candidate', value_name = 'votes')
        cands = df.candidate.unique()
        for col in columns[1:]:
            if col not in cands: print(office, col)
        df['county_name'] = sheetname.upper()
        df['office'] = office.upper()
        df['dataverse'] = 'LOCAL'
        
        #dfs.append(df)
        df1 = pd.concat([df1, df], axis =0)
        
    return df1

'''statewide data'''
xl = pd.read_excel(raw, sheet_name = 'Multi-Parish(Precinct)', header = None).iloc[3:].reset_index(drop = True)
#now find the indices of rows that start and end tables
zeroes = list(np.where(~np.any(xl, axis=1))[0]) #full zero rows, starting with first row
for i, x in enumerate(zeroes):
    if x == zeroes[-1]: break
    else:
        if x == zeroes[i+1] - 1: zeroes.remove(zeroes[i+1]) #remove the next empty row
print(xl.shape)

xl = xl.append({0:'0',1:'0', 2:'0', 3:'0', 4:'0', 5:'0', 6:'0', 7:'0', 8:'0', 9:'0',
                10:'0', 11:'0', 12:'0', 13:'0', 14:'0', 15:'0', } , ignore_index=True)

#last_offices = list(np.where(xl[0].str.contains('Trust Fund')))
last_office = 50520
print(type(last_office),last_office)
add_to_start = last_office +2
add_to_end = 54585


xl = xl.astype(str)
ends = zeroes[1:]  #the blank rows excluding first one
starts = [i+4 for i in zeroes] #first row of vote data
ends.append(add_to_end)
starts.append(add_to_start)

b=list()
dfs = list()
for i in range(len(ends)):
    start = starts[i] #the 'total votes' rows
    end = ends[i]  
    print(start, end)
    
    office = xl.iloc[start-2,0]
    print(office)
    b.append(office)
    #print('\n***** SHEET', i , office, '****')
    
    xl.columns = xl.iloc[start-1] #candidate names, need to melt later
    
    df = xl.iloc[start:end+1].reset_index(drop=True) #start index at 0, last row will be blank row 
    
    df['precinct'] = df.iloc[:,0]
    name = df.columns[0]
    df= df.drop(name, axis=1)
    df= df.replace(np.nan, '', regex = True) #drop the extra blank  columns
    
    tvotesrow = df.iloc[0:1,:]
    #find all the county names
    c_starts = [row.Index for row in df.itertuples() if '0' not in row.precinct and '1' not in row.precinct and (row.precinct not in ['Early Voting', 'Provisional Votes', 'Total Votes']) and row.precinct != '']    
    c_starts = c_starts[:-1] #don't want that last blank row
    if 'CA NO. 7' in office: c_starts.append(4030)
    c_ends = [x for x in c_starts[1:]] #first end will be second start
    c_ends.append(end-start) #the blank row that ends the table, adjust bc we reset the index
    
    df_final = pd.DataFrame()
    for i in range(len(c_starts)): #for each county
        cs = c_starts[i]
        print('start and end: ')
        print(df.at[cs, 'precinct'])
        ce = c_ends[i]
        print(df.iloc[ce,-1])
        county = df.at[cs,'precinct'].upper()
        #print(' *****next county:', county)
        df0 = df.iloc[cs+1:ce,:] #exclude county name row
        df0['county_name'] = county
        print('\t'+county)
        #print(df0.tail())
        df0 = pd.melt(df0, id_vars = ['precinct', 'county_name'], var_name = 'candidate', value_name = 'votes')
        #print(df0.head())
        df_final = pd.concat([df0, df_final], axis = 0)
        
    
    df_final['office'] = office.upper()
    
    tvotesrow['county_name'] = 'OFFICE FLOATING'
    tvotesrow['office'] = office.upper()
    tvotesrow.precinct = 'OFFICE FLOATING'
    tvotesrow = pd.melt(tvotesrow, id_vars = ['precinct', 'county_name','office'], var_name = 'candidate', value_name = 'votes')
    df_final = pd.concat([df_final, tvotesrow], axis = 0)
    
    dfs.append(df_final)
     

df_final = pd.DataFrame()
for tb in dfs:
    df_final = pd.concat([df_final,tb], axis = 0)


#final = pd.DataFrame()
xl = pd.ExcelFile(raw)
for name in xl.sheet_names:
    if name not in ['Multi-Parish(Parish)', 'Multi-Parish(Precinct)']:
        table = make_local_tables(raw, name)
        df_final = pd.concat([df_final, table], axis=0)

df_final = df_final.replace(np.nan, '',regex = True)
af = df_final[df_final.candidate == np.nan]
print(sorted(df_final.candidate.unique()))

df_final['mode'] = 'ELECTION DAY'
df_final.loc[df_final.precinct == 'Early Voting', 'mode'] = 'EARLY VOTING'
df_final.loc[df_final.precinct == 'Provisional Votes', 'mode'] = 'PROVISIONAL'

df_final.loc[df_final.precinct == 'Early Voting', 'precinct'] = 'COUNTY FLOATING'
df_final.loc[df_final.precinct == 'Provisional Votes', 'precinct'] = 'COUNTY FLOATING'

def get_magnitude(x):
    if 'TO BE ELECTED' in x: return int(x[x.find(' TO BE ELEC')-1])
    else: return 1

a=list()
def get_district(x):
    if 'TO BE ELECTED' in x: x = x[:x.find(' (')]
    if 'U. S. REP' in x: return x[24].zfill(3)
    elif 'ALDERM' in x:
        if 'DISTRICT' in x: return x[x.find(',')-1]
        elif 'ELECTION SECTION' in x: return 'ELECTION SECTION 2'
        else: return ''
    elif 'ASSOCIATE JUSTICE' in x: return x[x.find(',')+2].zfill(3)
    
    elif 'CITY COURT' in x:
        if 'DIVISION' in x: return x[x.find('DIVIS'):x.find('DIVI')+10]
        elif 'DIV. ' in x: 
            return x[x.find('DIST.'):x.find(' CITY')].replace('DIST.', 'DISTRICT')
        else: return ''
    elif 'CONSTABLE' in x: 
        return x[x.find('--')+3:].replace('  ', ' ')
        '''
        if 'JUSTICE OF THE PEACE' in x: return x[x.find('PEACE')+6:]
        elif 'COURT' in x: return x[x.find('- ')+3:]
        elif 'WARD' in x: return x[13:16] + ' WARD'  
        '''
    elif 'COUNCIL MEMBER ' in x and 'AT LARGE' not in x and 'ELTON' not in x:
        return x[x.find('- ')+2:x.find(',')]
    elif 'COUNCILMAN' in x and 'DISTRICT' in x:
        if 'METRO' not in x: return x[x.find(',')-1]
        else: return x[x.find('METRO'):].replace('  ',' ')
        
    if 'DISTRICT ATTORNEY' in x and 'JUDICIAL' in x: return x[x.find('--')+3:]
    elif 'DISTRICT JUDGE' in x: return x[x.find('--')+3:] #.replace(' JUDICIAL','').replace('COURT ','')
    
    elif 'JUDGE --' in x or 'JUDGE, ' in x: 
        a.append(x)
        if 'CIVIL' in x or 'CRIMINAL' in x or 'TRAFFIC' in x: 
            if 'SECTION' in x: return x[x.find('SECTION'):]
            else: return x[x.find('DIVISION'):]
        else: return x[x.find('--')+3:]
    elif 'JUSTICE OF THE PEACE' in x or 'JUSTICE(S) OF' in x: return x[x.find('--')+3:].replace('  ', ' ')
    elif 'MAGISTRATE JUDGE' in x: return x[x.find('1'):]
    elif 'SCHOOL BOARD' in x: return x[-2:].strip().zfill(3)
    elif 'POLICE JUROR' in x: return x[-1].zfill(3)
    elif 'PSC' in x: return x[-1].zfill(3)
    elif 'SELECTMAN' in x: return x[x.find(',')-3:x.find(',')].strip('T ')
    else: return ''
    
def fix_office(x):
    x=x.replace('(S)','')
    if x == 'MAGISTRATE JUDGE -- 14TH JUDICIAL DISTRICT COURT': return 'MAGISTRATE JUDGE'
    if x == 'JUDGE -- 2ND PARISH COURT, DIVISION A': return 'PARISH COURT JUDGE'
    if x == 'MAGISTRATE -- MAGISTRATE SECTION, CRIMINAL DISTRICT COURT': return 'MAGISTRATE, MAGISTRATE SECTION, CRIMINAL DISTRICT COURT'
    elif 'ASSOCIATE JUSTICE' in x: return 'SUPREME COURT ASSOCIATE JUSTICE'
    elif 'DISTRICT JUDGE' in x: 
        return 'DISTRICT COURT JUDGE'

    if 'TO BE ELECTED' in x: x = x[:x.find('(')]
    if 'CITY JUDGE' in x: 
        #if 'ELECTION DIST' in x: x=x.replace('ELECTION DIST. 1, DIV A,','')
        if 'SHREVEPORT' in x: return 'CITY COURT JUDGE, CITY OF SHREVEPORT'
        elif 'LAFAYETTE' in x: return 'CITY COURT JUDGE, CITY OF LAFAYETTE'
        else: return x.replace('CITY JUDGE -- CITY COURT','CITY COURT JUDGE')
    elif 'CITY MARSHAL' in x: return x.replace('CITY MARSHAL -- CITY COURT', 'CITY COURT MARSHAL')
    elif 'CONSTABLE' in x: return 'CONSTABLE, JUSTICE OF THE PEACE'
    #elif 'COUNCIL MEMBER' in x: return 'COUNCIL MEMBER '+ x[x.find(','):]
    if 'PSC' in x: return 'PUBLIC SERVICE COMMISSIONER'
    elif 'PRESIDENTIAL ELECTORS' in x: return 'US PRESIDENT'
    elif 'U. S. REP' in x: return 'US HOUSE'
    elif 'SENATOR' in x: return 'US SENATE'
    elif 'SELECTMAN' in x: return 'SELECTMAN'
    if 'ALDERMAN' in x or 'ALDERMEN' in x:
        if 'DISTRICT' in x: return 'ALDERMAN,' + x[x.find(',')+1:]
        elif 'SECTION' in x: return 'ALDERMAN, TOWN OF ST FRANCISVILLE'
        else: return 'ALDERMAN, ' +x[x.find('- ')+2:]
    elif 'CHIEF OF POLICE' in x or 'MARSHAL --' in x or 'MAYOR' in x:
        return x.replace(' --',',')
    elif 'CONSTABLE' in x: return 'CONSTABLE'
    elif 'COUNCIL MEMBER' in x:
        if ',' in x: return 'COUNCIL MEMBER, '+x[x.find(',')+2:]
        else: return x.replace(' --',',')
    elif 'COUNCILMAN' in x:
        if 'METRO' not in x:
            return 'COUNCILMAN, ' +x[x.find('CITY'):]
        else: return 'COUNCILMAN'
    elif 'COUNCILMEN' in x: 
        return x.replace(' --',',')
    elif 'DISTRICT ATTORNEY' in x: 
        if 'CRIMINAL DISTRICT' in x: return x.replace(' --',',')
        else: return 'DISTRICT ATTORNEY'
    elif 'JUDGE --' in x: return x[x.find('--')+3:x.find(',')].strip('DIVISION A') + ' JUDGE'
    elif 'JUDGE, ' in x and 'CITY COURT' not in x: return x[x.find(',')+2:x.find(' --')]+' JUDGE'
    elif 'JUSTICE OF THE PEACE --' in x or 'JUSTICE(S) OF THE PEACE --' in x:
        return 'JUSTICE OF THE PEACE'
    elif 'MAGISTRATE' in x: return x.replace(' --', ',').strip(', 14TH JUDICIAL DISTRICT COURT')
    elif 'SCHOOL BOARD' in x or 'POLICE JUROR' in x: return x[:x.find(' --')]
    else: return x    

def get_dataverse(x):
    if x == 'US PRESIDENT': return 'PRESIDENT'
    elif x == 'US HOUSE': return 'HOUSE'
    elif x == 'US SENATE': return 'SENATE'
    elif x in ['PUBLIC SERVICE COMMISSIONER',
               'SUPREME COURT ASSOCIATE JUSTICE', 'JUVENILE COURT JUDGE',
               'FAMILY COURT JUDGE', 'DISTRICT COURT JUDGE', 'COURT OF APPEAL JUDGE',
               'DISTRICT ATTORNEY, CRIMINAL DISTRICT COURT', 'DISTRICT ATTORNEY', 'MAGISTRATE JUDGE',
               'CIVIL DISTRICT COURT JUDGE', 'DISTRICT ATTORNEY, CRIMINAL DISTRICT COURT',
               'MAGISTRATE, MAGISTRATE SECTION, CRIMINAL DISTRICT COURT',
               'CA NO 1 (ACT 447, 2019 - HB 425) -- RELATING TO DECLARING THERE IS NO RIGHT TO AND NO FUNDING OF ABORTION IN THE LOUISIANA CONSTITUTION',
                'CA NO 2 (ACT 368 - HB 360) -- AMENDS DETERMINATION OF FAIR MARKET VALUE OF OIL OR GAS WELL',
                'CA NO 3 (ACT 367 - HB 267) -- AMENDS USE OF BUDGET STABILIZATION FUND',
                'CA NO 4 (ACT 366 - HB 464) -- LIMITS EXPENDITURE LIMIT FOR STATE GENERAL FUND',
                'CA NO 5 (ACT 370 - SB 272) -- AUTHORIZES COOPERATIVE ENDEAVOR TAX EXEMPTIONS',
                'CA NO 6 (ACT 369 - HB 525) -- INCREASES INCOME LIMIT FOR HOMESTEAD EXEMPTION SPECIAL ASSESSMENT LEVEL',
                'CA NO 7 (ACT 38, 1ST ES - SB 12) -- CREATES LOUISIANA UNCLAIMED PROPERTY PERMANENT TRUST FUND']: return 'STATE'
    else: return 'LOCAL'
z = list()
def fix_candidate(x):
    x=x.upper()
    x=x.replace('.','')
    x=x.replace(',','')
    x=x.replace("POCHE'", 'POCHE')
    x=x.replace(' (OTHER)','')
    x=x.replace(' (REP)','')
    x=x.replace(' (DEM)','')
    x=x.replace(' (LBT)','')
    if x[0] == '"': 
        x= x.replace('"', '')
        return x[:x.find('(')-1]
        z.append(x)
    
    elif 'REPUBLICAN' in x: return x.replace(' MICHAEL PENCE REPUBLICAN','')
    elif 'LIFE LIBERTY CONSTITUTION' in x: return x.replace(' ANDY PRIOR LIFE LIBERTY CONSTITUTION','')
    elif 'AMERICAN SOLIDARITY' in x: return x.replace(' AMAR PATEL AMERICAN SOLIDARITY PARTY','')
    elif 'FREEDOM AND PROSPERITY' in x: return x.replace(' KARLA BALLARD FREEDOM AND PROSPERITY','')
    elif 'SOCIALIST WORKERS' in x: return x.replace('MALCOLM JARRETT SOCIALIST WORKERS PARTY','')
    elif 'UNITY' in x: return x.replace(' ERIC BODENSTAB UNITY PARTY AMERICA','')
    elif 'CONSTITUTION' in x: return x.replace(' WILLIAM MOHR CONSTITUTION PARTY','')
    elif 'BECOMING ONE' in x: return x.replace(' CLAUDELIAH ROZE BECOMING ONE NATION','')
    elif 'LIBERTARIAN' in x: return x.replace(' JEREMY COHEN LIBERTARIAN','')
    elif 'DEMOCRATIC' in x: return x.replace(' KAMALA HARRIS DEMOCRATIC','')
    elif 'BIRTHDAY' in x: return x.replace(' MICHELLE TIDBALL THE BIRTHDAY PARTY', '')
    elif 'CUP' in x: return x.replace('ERIC STONEHAM CUP','')
    elif 'SOCIALISM AND LIBERATION' in x: return x.replace(' SUNIL FREEMAN SOCIALISM AND LIBERATION','')
    elif x!= 'YES' and x != 'NO' and '(' in x:
        return x[:x.find('(')-1]
    else: return x

def get_party(x):
    if x!= 'YES' and x != 'NO':
        if '(' in x: return x[x.find('(')+1:].strip(')')
    elif 'SOCIALISM AND LIBERATION' in x: return 'SOCIALISM AND LIBERATION'
    elif 'REPUBLICAN' in x: return 'REPUBLICAN'
    elif 'LIFE LIBERTY CONSTITUTION' in x: return 'LIFE LIBERTY CONSTITUTION'
    elif 'AMERICAN SOLIDARITY' in x: return 'AMERICAN SOLIDARITY'
    elif 'FREEDOM AND PROSPERITY' in x: return 'FREEDOM AND PROSPERITY'
    elif 'SOCIALIST WORKERS' in x: return 'SOCIALIST WORKERS'
    elif 'UNITY' in x: return 'UNITY'
    elif 'CONSTITUTION' in x: return 'CONSTITUTION'
    elif 'BECOMING ONE' in x: return 'BECOMING ONE NATION'
    elif 'LIBERTARIAN' in x: return 'LIBERTARIAN'
    elif 'DEMOCRATIC' in x: return 'DEMOCRAT'
    elif 'BIRTHDAY' in x: return 'BIRTHDAY'
    elif 'CUP' in x: return 'CUP'
    #elif 'SOCIALISM AND LIBERATION' in x: return 'SOCIALISM AND LIBERATION'
    else: return ''

def fix_district(x):
    x = x.replace('JUSTICE OF THE PEACE & CONSTABLE DISTRICT ','').replace('ELEC SECT', 'ELECTION SECTION')
    x=x.replace('METRO DISTRICT ','')
    if 'JUSTICE' in x: 
        if 'JUSTICE OF THE PEACE COURT' in x: x=x.replace('JUSTICE OF THE PEACE COURT','JUSTICE COURT') #.strip('ND').strip('ST').zfill(3)
        elif 'JUSTICE COURT' in x: x=x #x=x.replace(' JUSTICE COURT','') #.strip('ND').strip('ST').strip('RD').strip('TH').zfill(3)
        else: x=x.replace('JUSTICE OF THE PEACE ','').strip()
    
    if 'JUDICIAL DISTRICT COURT' in x: #x= x.replace('JUDICIAL DISTRICT COURT','')
        if 'DIV' in x: x= x[:4].strip().replace('TH','').replace('ST','').replace('ND','').replace('RD','').zfill(3) + x[x.find(','):]
        else: x= x[:4].strip().replace('ST','').replace('RD','').replace('TH','').strip('ND').strip('ST').zfill(3)
    if 'JUVENILE COURT' in x: x= x.replace('JUVENILE COURT, ','')
    #if x[4:11] == 'CIRCUIT': x= x[0].zfill(3) + x[x.find(','):]
    
    if 'CIRCUIT' in x and 'DIST' in x:
        dist = x[x.find('DIST')-4]
        first = x[:x.find(dist)].replace('ST DIST,','').replace(dist,'').replace('ND DIST,','').replace('RD DIST','').strip()
        last = x[x.find('DIST')+4:]
        x = dist.zfill(3)+ ', ' + first.replace(',,',',') + last
    
    if 'DISTRICT' in x and (len(x) == 10 or len(x) == 11): x= x[-2:].strip()
    if (len(x) ==1 or len(x) ==2) and x.isnumeric(): return x.zfill(3)
    if x == '1ST ' or x == '2ND ' or x == '3RD ' or x == '4TH ':
        return x[0].zfill(3)
    elif 'WARD' in x and 'DISTRICT' in x:
        dist = x[-1].zfill(3)
        ward = x[:x.find(',')]
        return dist+', '+ward
    return x
    '''
for office in sorted(df_final.office.unique()):
    print(office)
'''
df_final['special'] = 'FALSE'
df_final.loc[df_final.office == 'ASSOCIATE JUSTICE -- SUPREME COURT, 4TH SUPREME COURT DISTRICT','special'] = 'TRUE'

df_final['district'] = df_final.office.apply(get_district).astype(str).str.replace('.','').str.replace('  ',' ')
df_final['magnitude'] = df_final.office.apply(get_magnitude).astype(int)
df_final['office'] = df_final.office.apply(fix_office).astype(str).str.replace('  ', ' ').str.replace('.','')
df_final['dataverse']= df_final.office.apply(get_dataverse)
df_final['party_detailed'] = df_final.candidate.apply(get_party).replace({
                    'REP':'REPUBLICAN', 'DEM':'DEMOCRAT', 'GRN': 'GREEN', 
                    'LBT':'LIBERTARIAN', 'NOPTY': 'INDEPENDENT',
                    'IND':'INDEPENDENT'})


df_final.candidate = df_final.candidate.apply(fix_candidate).replace('(S)','').replace(' (OTHER)','').replace("SA'TRICA' WILLIAMS","SA'TRICA WILLIAMS")
#print(sorted(df_final.district.unique()))
df_final.loc[df_final.candidate.str.contains('KANYE WEST'), 'party_detailed'] = 'BIRTHDAY'
df_final.loc[df_final.candidate.str.contains('JO JORGENSEN'), 'party_detailed'] = 'LIBERTARIAN'
df_final.loc[df_final.candidate.str.contains('JOSEPH R BIDEN'), 'party_detailed'] = 'DEMOCRAT'
df_final.loc[df_final.candidate.str.contains('BRIAN CARROLL'), 'party_detailed'] = 'AMERICAN SOLIDARITY'
df_final.loc[df_final.candidate.str.contains('BROCK PIERCE'), 'party_detailed'] = 'FREEDOM AND PROSPERITY'
df_final.loc[df_final.candidate.str.contains('DON BLANKENSHIP'), 'party_detailed'] = 'CONSTITUTION'
df_final.loc[df_final.candidate.str.contains('GLORIA LA RIVA'), 'party_detailed'] = 'SOCIALISM AND LIBERATION'
df_final.loc[df_final.candidate.str.contains('JADE SIMMONS'), 'party_detailed'] = 'BECOMING ONE NATION'
df_final.loc[df_final.candidate.str.contains('PRESIDENT BODDIE'), 'party_detailed'] = 'CUP'
df_final.loc[df_final.candidate.str.contains('TOM HOEFLING'), 'party_detailed'] = 'LIFE LIBERTY CONSTITUTION'
df_final.loc[df_final.candidate.str.contains('BILL HAMMONS'), 'party_detailed'] = 'UNITY'
df_final.loc[df_final.candidate.str.contains('DONALD J TRUMP'), 'party_detailed'] = 'REPUBLICAN'
df_final.loc[df_final.candidate.str.contains('ALYSON KENNEDY'), 'party_detailed'] = 'SOCIALIST WORKERS'

df_final.loc[df_final.office.str.contains('CA NO '), 'district'] = 'STATEWIDE'

df_final['district'] = df_final['district'].str.replace('DIVISION','DIV').str.replace('ELECTION SECTION','ES').str.replace('ELEC SEC','ES')
df_final.district = df_final['district'].str.replace(',,',',')

df_final['party_simplified'] = df_final['party_detailed'].replace({
                        'GREEN':'OTHER', 'INDEPENDENT':'OTHER',
                        'SOCIALISM AND LIBERATION':'OTHER',
                        'LIFE LIBERTY CONSTITUTION':'OTHER',
                        'AMERICAN SOLIDARITY':'OTHER',
                        'FREEDOM AND PROSPERITY':'OTHER',
                        'SOCIALIST WORKERS':'OTHER',
                        'UNITY':'OTHER','CONSTITUTION':'OTHER',
                        'BECOMING ONE NATION':'OTHER',
                        'BIRTHDAY':'OTHER', 'CUP':'OTHER'})


countyFips = pd.read_csv("C:/Users/abguh/Desktop/urop/2020-precincts/help-files/county-fips-codes.csv").astype(str)
df_final['state'] = 'Louisiana'

df_final.county_name = df_final.county_name.replace({'LASALLE': 'LA SALLE'})
df_final = pd.merge(df_final, countyFips, on = ['state','county_name'],how = 'left')
df_final.county_fips = df_final.county_fips #.astype(str).str.replace('.0','')
df_final['jurisdiction_name'] = df_final.county_name
df_final['jurisdiction_fips'] = df_final.county_fips

df_final.state = df_final.state.str.upper()
df_final['year'] = '2020'
df_final['stage'] = 'GEN'
df_final['state_po'] = 'LA'
df_final['state_fips'] = '22'
df_final['state_cen'] = '72'
df_final['state_ic'] = '45'
df_final['date'] = '2020-11-03'

df_final['readme_check'] = 'FALSE'
df_final['writein'] = 'FALSE'

#print(sorted(df_final.candidate.unique()))

#print(sorted(df_final.party_detailed.unique()))

df_final = df_final[df_final.precinct != 'OFFICE FLOATING']
df_final = df_final[df_final.precinct != 'Total Votes']

#df_final.loc[df_final.office == 'PUBLIC SERVICE COMMISSIONER','district'] = 'STATEWIDE'

df_final = df_final.applymap(lambda x: x.strip() if type(x)==str else x)
df_final.votes = df_final.votes.astype(str)
df_final.votes = df_final.votes.replace('nan',0)
df_final.votes = df_final.votes.astype(int)

df_final.district = df_final.district.apply(fix_district)
df_final.district = df_final['district'].str.replace(',,',',')


df_final.loc[df_final.office == 'US PRESIDENT', 'district'] = 'STATEWIDE'
df_final.loc[df_final.office == 'US SENATE', 'district'] = 'STATEWIDE'

df_final = df_final.replace(np.nan, '', regex = True)

df_final.to_csv("../2020-la-precinct-general.csv", index = False)


for office in sorted(df_final.office.unique()):
    df = df_final[df_final.office == office]
    tot = sum(df.votes)
    print(office , ':\t', tot)
    if 'CA NO 7' in office: break



df1 = df_final[df_final.party_detailed == 'OTHER']
print(df1.candidate.unique())
print(df_final.district.unique())
''' early voting should be 'county floating'''