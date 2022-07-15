#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import numpy as np
import re
import warnings
import csv
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None  # default='warn'


# In[2]:


os.chdir('/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/NC')
path = "raw/targetdir/results_pct_20201103.txt"
old = pd.read_csv(path, delimiter = '\t')


# In[3]:


df = pd.read_csv("raw2/STATEWIDE_PRECINCT_SORT.txt",delimiter = '\t',dtype = 'unicode')

df = df.replace(np.nan, '', regex = True)
df=df.applymap(lambda x: x.strip() if type(x)==str else x)


# In[4]:


#remove one completely blank row
df = df[df.precinct_code!=""]


# In[5]:


raw = pd.read_csv("raw2/STATEWIDE_PRECINCT_SORT.txt",delimiter = '\t',dtype = 'unicode')
raw = raw.fillna('')


# In[6]:


#raw[raw.contest_title.str.contains('EDUCATION')]
#raw[['group_num','group_name','voting_method_lbl','voting_method_rslt_desc']].sort_values(by='group_num').drop_duplicates()


# In[7]:


dups = raw[raw.drop(columns = 'group_name').duplicated(keep = False)] #.sort_values(['precinct','office','candidate','mode','votes'])
dups


# In[8]:


raw.columns


# #### checks to match and align data

# In[224]:


len(df.precinct_code.unique())
df['precinct_code'] = df['precinct_code'].astype(str)
df['precinct_code'] = df['precinct_code'].replace({'53':'053','55':'055','67':'067','71':'071','73':'073','83':'083',
                                                   '91':'091','92':'092'})


# In[225]:


len(old.Precinct.unique()) == len(df.precinct_code.unique())


# #### clean

# In[9]:


#now replace big offices with just their standard office codes 
l = list()
def get_office(x):
    x=x.replace(' (UNEXPIRED)','').replace('AT-LARGE','').replace('TWP','TOWNSHIP').replace(' (UNEX)','')
    x=x.replace('AT LARGE','').replace('COUNTY-WIDE','')
    x=x.replace('COUNTY OF LEE','LEE COUNTY').replace('COUNTY OF CAMDEN','CAMDEN COUNTY')
    x=x.replace('NC ','').replace('BD OF','BOARD OF').replace(' (UNEXPIRED TERM)','')
    if re.match('US PRESIDENT',x):      return 'US PRESIDENT'
    elif re.match("STATE SENATE", x):         return "STATE SENATE"
    elif re.match("HOUSE OF REPRESENTATIVES", x): return "STATE HOUSE"
    elif re.match("US HOUSE OF REPRESENTATIVES", x): return "US HOUSE"
    elif      'DISTRICT ATTORNEY' in x:               return 'DISTRICT ATTORNEY'
    elif 'SEAT' in x and "COURT" in x:
        if 'DISTRICT' in x: return x[:x.find('E DIS')+1] 
        else: return x[:x.find('SEAT')-1]
    # if 'BOARD OF' in x:
    #     if x == 'BUNCOMBE COUNTY BOARD OF COMMISSIONERS CHAIRMAN': return 'BOARD OF COMMISSIONERS CHAIRMAN'
    #     elif x == 'HAYWOOD COUNTY BOARD OF EDUCATION CHAIRMAN': return 'BOARD OF EDUCATION CHAIRMAN'
        
    #     if 'TWP' in x or 'TOWNSHIP' in x:
    #         if 'COMMISSION' in x: return 'BOARD OF COMMISSIONERS - '+x[x.find('NERS ')+5:].replace(' TOWNSHIP','')
    #         if 'EDUCATION' in x: return 'BOARD OF EDUCATION - '+x[x.find('CATION ')+6:].replace(' TOWNSHIP','')
    #     if 'EDUCATION' in x: 
    #         if 'NORTH BUNCOMBE' in x: return 'BOARD OF EDUCATION - NORTH BUNCOMBE'
    #         elif ('PASQUOTANK' in x)and ('INSIDE' in x or 'OUTSIDE' in x): return 'BOARD OF EDUCATION - '+' '.join(x.split()[-3:])
    #         city = x[:x.find('BOARD')].replace('SCHOOLS ','')
    #         return 'BOARD OF EDUCATION - '+city
    #     elif 'COMMISSIONER' in x:
    #         if ('PASQUOTANK' in x)and ('INSIDE' in x or 'OUTSIDE' in x): return 'BOARD OF COMMISSIONERS - '+' '.join(x.split()[-2:])
    #         city = x[:x.find('BOARD')]
    #         return 'BOARD OF COMMISSIONERS - '+city
    # elif 'SOIL AND W' in x:
    #     city = x[:x.find(' SOIL A')]
    #     return 'SOIL AND WATER CONSERVATION DISTRICT SUPERVISOR - '+city
    # elif 'DEEDS' in x: return 'REGISTER OF DEEDS - '+x[:x.find('REGI')]
    # elif 'COUNTY' in x:
    #     if 'MALT' in x: return x[x.find('MALT'):] + ' - ' + x[:x.find('MALT')].strip().replace("-",', ')
    #     if 'UNFORTIFIED' in x: return x[x.find('UNF'):] + ' - ' + x[:x.find('UNF')].strip().replace("-",', ')
    #     else: return x[x.find('TY ')+3:] + ' - '+ x[:x.find('COUNTY')]+ ' COUNTY'
    # elif 'CITY OF' in x:
    #     if 'ROANOKE' in x: return 'PROPERTY TAX REFERENDUM - ROANOKE RAPIDS'
    #     else: city = x.split()[2]   #all cities are one word except for ROANOKE RAPIDS
    #     if 'COUNCIL' in x: return 'CITY COUNCIL - '+city
    #     return x[x.find(x.split()[3]):]+ ' - '+city
    # if 'DISTRICT' in x: return x[:x.find('E DIS')+1] 
    #     else: return x[:x.find('SEAT')-1]
    # elif 'TOWN OF' in x:
    #     if 'MAYOR' in x: return 'MAYOR - '+x[:x.find(' MAY')]
    #     elif 'ELEC' in x: return ' '.join(x.split()[-3:]) + ' - '+x[:x.find(x.split()[3])]
    #     elif 'TOWN C' in x: return ' '.join(x.split()[-2:])+ ' - '+x[:x.find(' TOWN C')].replace('TOWN OF ','')
    #     if 'ALDERMAN' in x: return 'TOWN ALDERMAN - BLACK MOUNTAIN'
    #     elif 'COMMISS' in x: return 'TOWN COMMISSIONER - '+ x[x.find(' OF')+4:x.find(' COM')]
    #     elif 'CARTE' in x: return 'TOWN PUBLIC IMPROVEMENT BONDS REFERENDUM - CAPE CARTERET'
    #     else: return 'TOWN PROPERTY TAX FOR FIRE PROTECTION SERVICES - GASTON'
        
    # elif '-' in x:
    #     if 'FIRE' in x: return 'FIRE DISTRICT FIRE TAX ELECTION - LIBERTY HALL, DUPLIN'
    #     else: return 'SANITARY DISTRICT BOARD '+x[x.find('-'):x.find('SAN')-1] + ', '+x[:x.find(' -')]
    # elif 'SAN' in x: return 'SANITARY DISTRICT BOARD - '+x.split()[0]
    # elif 'VILLAGE OF' in x: return ' '.join(x.split()[4:]) + ' - '+ x.split()[3]
    else:
        return x


    if x not in l:
        l.append(x)
        print(x)
                
    

        #return x[x.find('- '):x.find('SAN')] + ', '+x.find[:x.find(' -')]
        
'''
    else:
        if 'DIST' in x:     #strip off anything after 'DISTRICT'
            return x[:x.find('DIST')].strip()
        if 'WARD' in x:     #strip off anything after 'WARD'
            return x[:x.find('WARD')].strip()
        if x.startswith("NC"): #strip off 'NC'from start of state offices
            return x[2:].strip()
        if 'SEAT' in x:     
            if '(' in x:    #catch those that have (SOMETHING) after SEAT#
                return x[:x.find('SEAT')] + x[x.find('(')+1:-1]
            else: return x[:x.find('SEAT')].strip()
    
        else: return x
        '''
def get_special(x):
    return str('UNEX' in x).upper() 

l = list()
def get_district(x):
    x=x.replace('TWO','2').replace('FOUR','4').replace('TWP','TOWNSHIP')
    if 'REFERENDUM' in x: return ''
    if 'UNEX' in x: x=x[:x.find(' (UN')]
    if 'HOUSE OF REP' in x: return x[-3:]
    if ("GOVERNOR" in x or "SECRETARY OF STATE" in x or "ATTORNEY GENERAL" in x or "AUDITOR" in x 
        or "SUPERINTENDENT OF PUBLIC INSTRUCTION" in x or "COMMISSIONER OF AGRICULTURE" in x or "COMMISSIONER OF LABOR" in x 
        or "COMMISSIONER OF INSURANCE" in x  
        or 'TREASURER'in x or 'LIEUTENANT GOVERNOR' in x): return 'STATEWIDE'   #STATEWIDE label for statewide offices
    if 'AT LARGE' in x or 'AT-LARGE' in x: return 'AT-LARGE'
    elif 'COUNTY-WIDE' in x: return 'COUNTYWIDE'
    elif 'WARD' in x:
        if 'WINSTON' in x: return x.split()[-2].zfill(3)
        else: return x[-1].zfill(3)
    elif 'COURT' in x:
        if 'GE DIS' in x: return x[-11:-8].strip().zfill(3)+', '+x[x.find('SEA'):]
        elif 'SEAT' in x: return x[-2:].zfill(3)
        else: return ''
    if x.split()[-1] == 'DISTRICT': #capture districts like EAST, and other smaller dists for commisioners and other boards
        if 'COMMISSION' in x: return x[x.find('NERS ')+5:].replace(' DISTRICT','')
        if 'EDUCATION' in x: return x[x.find('CATION ')+6:].replace(' DISTRICT','')
    
    if len(x) >2 and x[-3:].isnumeric(): return x[-3:]
    elif len(x) >1 and x[-2:].isnumeric(): return x[-2:].zfill(3)
    if len(x) >1 and (x[-2] == ' ' or x[-3] == ' ' or x[-4] == ' ') and 'REFERENDUM' not in x:
        return x[-2:].strip()
    elif 'SEAT' in x: return '0'+x[x.find('0'):]
    #elif ('NORTH' in x or 'SOUTH' in x or 'EAST' in x or 'WEST' in x) and 'TOWN OF' not in x:
    #    if x not in l:
    #        l.append(x)
    #        print(x)
    return ''

def get_dataverse(x):
    if x == 'US PRESIDENT': return 'PRESIDENT'
    elif x == "US SENATE":return "SENATE"
    elif x == "US HOUSE": return "HOUSE"
    elif x in ["STATE HOUSE", "STATE SENATE", "GOVERNOR", "SECRETARY OF STATE", "ATTORNEY GENERAL",
               "AUDITOR", "SUPERINTENDENT OF PUBLIC INSTRUCTION", "COMMISSIONER OF AGRICULTURE", "COMMISSIONER OF LABOR",
               "COMMISSIONER OF INSURANCE", "SUPREME COURT ASSOCIATE JUSTICE", "SUPREME COURT JUSTICE", "SUPERIOR COURT JUDGE", 'TREASURER',
               'COURT OF APPEALS JUDGE', 'LIEUTENANT GOVERNOR'] or 'SUPREME COURT' in x or 'SUPERIOR COURT JUDGE' in x: 
        return "STATE"
    else: # all others are local
        return "LOCAL"         

def get_writein(x):
    return str('WRITE-IN' in x).upper()

l = list()
def fix_district(x):
    if '(' in x: 
        end = x[x.find(' '):].strip().replace("(",'').replace(')','')
        return x[:3]+ ' - '+end
    elif len(x)>= 1 and x[-1].isnumeric(): return x.strip().zfill(3)
    else: return x


# In[10]:


df['district'] = df['contest_title'].apply(get_district).replace({'I':'001','II':'002','IV':'004','V':'005'})
df['writein'] = df['result_type_desc'].apply(get_writein)
df['office'] = df['contest_title'].apply(get_office)
df['special'] = df['contest_title'].apply(get_special)
df['dataverse'] = df['office'].apply(get_dataverse)
df['district'] = df['district'].apply(fix_district)


# In[ ]:





# In[11]:


#df[df.contest_title=='HAYWOOD - ...'] #check what this is in office


# In[ ]:





# In[12]:


df.loc[df.contest_title.str.contains('MARVIN CHARTER AMENDMENT REFERENDUM 1'),'office'] = 'CHARTER AMENDMENT REFERENDUM 1 - VILLAGE OF MARVIN'
df.loc[df.contest_title.str.contains('MARVIN CHARTER AMENDMENT REFERENDUM 2'),'office'] = 'CHARTER AMENDMENT REFERENDUM 2 - VILLAGE OF MARVIN'


# In[13]:


df.loc[df.contest_title.str.contains('COURTHOUSE DIS'),'office'] = 'BOARD OF COMMISSIONERS - COURTHOUSE DISTRICT, CAMDEN COUNTY'


# In[ ]:





# In[14]:


df['party_detailed'] = df['candidate_party_lbl'].replace({'REP' : 'REPUBLICAN','DEM' : 'DEMOCRAT','LIB' : 'LIBERTARIAN',
                                       'GRE': 'GREEN','CST': 'CONSTITUTION','UNA': 'INDEPENDENT',' ': '', 'NON':'NONPARTISAN'})

# now create party variable
df['party_simplified'] = df['party_detailed'].replace({'GREEN':'OTHER','CONSTITUTION':'OTHER','INDEPENDENT':'OTHER'})


# In[15]:


#nonpartisan offices
nonpart = df[(df.candidate_party_lbl == '')&(df.candidate_name!='OVER VOTE')&(df.candidate_name!='UNDER VOTE')&(df.writein=='FALSE')].office.unique().tolist()
nonpart #these are just referendums and ordinances, no party info


# In[17]:


for office in nonpart:
    df.loc[df.office==office,'party_detailed'] = 'NONPARTISAN'
    df.loc[df.office==office,'party_simplified'] = 'NONPARTISAN'


# In[16]:


def fix_cand(x):
    x= x.upper().replace('.','').replace(",",'')
    if '(' in x: x = x.replace('(','"').replace(')','"')
    if 'WRITE-IN' in x: return 'WRITEIN'
    if x =="OVER VOTE": return 'OVERVOTES'
    if x == 'UNDER VOTE':return 'UNDERVOTES'
    if x == 'FOR': return 'YES'
    if x == 'AGAINST': return 'NO'
    return x

df['candidate'] = df['candidate_name'].apply(fix_cand)
df.loc[df.candidate=='WRITEIN','party_detailed'] = ""
df.loc[df.candidate=='WRITEIN','party_simplified'] = ""


# In[18]:


#combine precinct name & code for precinct variable!
def fix_precinct(name, code):
    if name == '': return code
    elif name == code: return name
    else: return name+'_'+code
df['precinct'] = df.apply(lambda x: fix_precinct(x['precinct_name'], x['precinct_code']), axis=1)


# In[19]:


#df[['precinct','precinct_name','precinct_code']].sort_values(by='precinct').drop_duplicates()


# In[20]:


df['county_name'] = df['county'].str.upper()
df['jurisdiction_name'] = df['county'].str.upper()

#MERGING COUNTY_FIPS
df['state'] = 'North Carolina' #need it like this to merge; CHANGE LATER
countyFips = pd.read_csv("../../help-files/county-fips-codes.csv")
df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
#now can change 'state' column  back to NC
df['state'] = df['state'].str.upper()


# In[21]:


#don't run
'''
modes = ['ABSENTEE','ABSENTEE SUPPLEMENTAL','ABSENTEE BY MAIL','MAIL ABSENTEE','ABSENTEE MAIL','ONE STOP','ONE STOP ONE',
        'ONE STOP TWO','ONE STOP THREE','PROVISIONAL','TRANSFER']

for c in df.county.unique():
    a = df[df.county == c]
    ofs = len(a.contest_title.unique().tolist())
    for mode in modes:
        b = a[a.precinct_code == mode]
        if b.vote_ct.unique().tolist() != ['0'] and b.vote_ct.sum()>0: 
            print(c,': ',mode,': ', 'offices:',len(b.contest_title.unique()),'/',ofs,len(b.vote_ct.unique()),'sum:',b.vote_ct.sum())
#print(len(df[df.precinct_code == 'TRANSFER'].county.unique().tolist()))
'''


# In[22]:


#don't run
'''
cs = ['BERTIE','DAVIDSON','DUPLIN','DURHAM','HALIFAX','MARTIN','PITT','STOKES','SURRY','TYRRELL','WILKES']
modes = df['mode'].unique()
big_dict = {}
for county in cs:
    print(county)
    a = df[df.county_name == county]
    ofs = a.office.unique().tolist()
    #print(len(ofs))
    cs = a.candidate.unique().tolist()
    big_dict[county] = {}
    
    for of in ofs:
        print('**',of)
        b = a[a.office==of]
        if len(b['mode'].unique().tolist()) != 5: 
            for mode in modes:
                if mode not in b['mode'].unique().tolist():
                    print('missing mode - '+mode)
        big_dict[county][of] = {}
        for mode in modes:
            c = b[b['mode']==mode]
            big_dict[county][of][mode] = c.votes.sum()
        
          

            #martin and bertie counties missing election day-transfer and electionday -curbside
'''


# In[23]:


#don't run
'''
l = {}
for mode in modes:
    x = list()
    for county in big_dict:
        sd = big_dict[county]
        l[county] = list()
        for can in sd:
            try:
                if sd[can][mode] not in x:
                    x.append(sd[can][mode])
            except:
                l[county].append(can)
        if len(x)<10:
            print(county, mode,':',x)
'''


# In[ ]:





# In[25]:


#don't run
'''
cs = ['BERTIE','DAVIDSON','DUPLIN','DURHAM','HALIFAX','MARTIN','PITT','STOKES','SURRY','TYRRELL','WILKES']
modes = df['mode'].unique()
for county in cs:
    print(county)
    a = df[df.county_name==county]
    for of in a.office.unique():
        print('  **'+of)
        b = a[a.office==of]
        #see results by office
        for m in modes:
            c = b[b['mode']==m]
            if c.votes.sum() == 0:
                print('    **'+m,':',c.votes.sum())
                

    #curbside all 0, but there wasn't a floating value for that
    #transfer is all 0 in Bertie, Duplin, Durham, Halifax, Martin, Stokes,Surry,Tyrell
    # proviional is 0 in Tyrrell
    # Wilkes is not consistent by office, some offices are 0 for provisional & transfer but its just town mayor, commissioner,
'''


# In[ ]:





# In[26]:


#print(df.voting_method_rslt_desc.unique())
df['mode'] = df['voting_method_rslt_desc'].replace({'Election Day':'ELECTION DAY', 'Absentee: One-Stop':'ABSENTEE - ONE STOP',
                                                    'Absentee: By-Mail': 'ABSENTEE - BY MAIL', 'Provisional':'PROVISIONAL',
                                                    'Election Day: Transfer':'ELECTION DAY - TRANSFER',
                                                    'Election Day: Curbside': 'ELECTION DAY - CURBSIDE'})

#add the group number to mode to keep that distinguishing variable, rn dropping it is creating a lot of duplicates
def fix_mode(mode, groupnum):
    return mode+'_'+groupnum

df['mode'] = df.apply(lambda x: fix_mode(x['mode'],x['group_num']),axis=1)


# In[27]:


#df['mode'].unique()


# In[28]:


df['votes'] = df['vote_ct']
df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'NC'
df['state_fips'] = '37'
df['state_cen'] = '56'
df['state_ic'] = '47'
df['date'] = '2020-11-03'
df['readme_check'] = 'FALSE' 
df['magnitude'] = df['contest_vote_for'].astype(int)
#df.magnitude.unique()


# In[244]:


names = '''ALICIA BRITT PIERCE: ['DEMOCRAT' '""']
    ANJALI BOYD: ['NONPARTISAN' '""']
    ANTHONY PENLAND: ['REPUBLICAN' '""']
    BEVAN J FOSTER: ['DEMOCRAT' '""']
    BILL FLETCHER: ['NONPARTISAN' '""']
    BILL SORENSON: ['REPUBLICAN' '""']
    BILL WARD: ['REPUBLICAN' '""']
    CHARLES GILLIAM: ['REPUBLICAN' '""']
    CONSTANCE BRYANT CORAM: ['DEMOCRAT' '""']
    DANIEL SPENCE: ['""' 'NONPARTISAN']
    DAVID COLLIER: ['NONPARTISAN' '""']
    DENTON LEE: ['""' 'INDEPENDENT']
    DONEVA CHAVIS: ['NONPARTISAN' '""']
    ERIC M JOHNSEN: ['INDEPENDENT' '""']
    FRED GORE: ['REPUBLICAN' '""']
    GENE JORDAN: ['NONPARTISAN' '""']
    GREG TAYLOR: ['DEMOCRAT' 'REPUBLICAN']
    JAMES E TRIPP, JR: ['NONPARTISAN' '""']
    JAMES TAYLOR: ['""' 'DEMOCRAT']
    JEFF CARPENTER: ['REPUBLICAN' '""']
    JENNA WADSWORTH: ['DEMOCRAT' '""']
    LEN HENDERSON: ['""' 'NONPARTISAN']
    MARK DAVIS: ['DEMOCRAT' '""']
    MARTHA SUE HALL: ['""' 'NONPARTISAN']
    MONIKA JOHNSON-HOSTLER: ['NONPARTISAN' '""']
    PATRICIA BURDEN: ['""' 'NONPARTISAN']
    PAUL MONCLA: ['REPUBLICAN' '""']
    REUBEN F YOUNG: ['DEMOCRAT' '""']
    ROBBIE COHEN: ['""' 'NONPARTISAN']
    ROBERT FREEMAN: ['""' 'NONPARTISAN']
    RON PAYNE: ['""' 'NONPARTISAN']
    TIM DRIVER: ['""' 'NONPARTISAN']
    TRACY WARREN: ['NONPARTISAN' '""']
    WILLIAM STINSON: ['DEMOCRAT' '""']'''

names = [x[:x.find(':')].strip() for x in names.split('\n')]


# In[30]:


#cands listed as multiple parties, want to check if they are writein where the party is ""
#checks to see if cands w similar names are running for the same office
'''
same_names = dict()
same_office = list()
not_writes = list()
for n in names:
    #print('***'+n)
    a = df[df.candidate == n]
    w = a.writein.unique().tolist()
    if len(w) != 2: not_writes.append(n) #if it's not just 
        
    o = a.contest_title.unique().tolist()
    if len(o) == 1: same_office.append({n:o}) #if they're same office but diff party
        
    x = a.candidate_id.unique().tolist()   
    if len(x) != 2: #if there are more than 2 candidate IDs listed
        same_names[n] = {'num cands':len(x)}   #number of unique cands with that name
        for of in o:
            same_names[n][of] = len(a[a.contest_title==of].candidate_id.unique().tolist()) #number of "unique" ppl with the name for that office
                 
    if not ('FALSE' in w and 'TRUE' in w):  #and len(a.office.unique().tolist()) != '':
        print(n)
        print(a.office.unique())
        print(a[['party_detailed','writein']].drop_duplicates())
        print('\n')

'''


# In[31]:


#same_office #this is empty
#not_writes
#11 names have more than 2 candidate IDs
#same_names


# In[32]:


l = list()
# def remove_county(x):
#     if 'ELECTION' in x and 'TOWN' in x: 
#         if 'TOWN OF LAKE' in x: return 'MALT BEVERAGE ELECTION - LAKE WACCAMAW'
#         x= x[:x.find('- ')+2] + x[x.find('TOWN'):] #.replace('TOWNSHIP OF ','')
#     if 'COUNTY' in x: return 'COUNTY '+x[:x.find(' -')]
#     if 'BOARD OF COMMISSIONERS' in x and 'TOWN' in x: return 'TOWN COMMISSIONER - '+x[x.find('N OF ')+5:]
#     if 'COUNCIL' in x:
#         if 'VILLAGE' in x: return 'VILLAGE COUNCIL - MISENHEIMER'
#         elif 'BADEN' in x: return 'TOWN COUNCIL - BADIN'
#         else: return x
#     if 'CITY' in x[-5:]: return x[:-5]
#     #if x not in l:
#      #       l.append(x)
#     #        print()
#         #return x[:-5].strip()
#     if 'TOWN OF' in x: return x.replace('TOWN OF ','')
#     elif 'TOWNSHIP OF' in x: return x.replace('TOWNSHIP OF ','')
#     return x

# df['office'] = df['office'].apply(remove_county).str.strip()


# In[33]:


#df[(df.contest_title.str.contains('BOARD'))&(df.contest_title.str.contains('PASQUOTANK'))][['contest_title','office','district']].drop_duplicates()#.contest_title.unique()


# In[249]:


#figure out where we're losing district info that's leading to duplicates
df[df.district!='STATEWIDE'][['county_name','contest_title','office','district']].sort_values(by='office').drop_duplicates()[250:300]


# In[34]:


#CHECK THIS!!!!
df = df[~(df.office == '')] #.contest_title.unique()


# In[35]:


df.loc[df.district=='COUNTYWIDE','district'] = 'AT-LARGE'
df.loc[df.office=='PRESIDENT','district'] = 'STATEWIDE'
df.loc[df.office=='PRESIDENT','dataverse'] = 'PRESIDENT'
df.loc[df.office=='US SENATE','district'] = 'STATEWIDE'
df.loc[df.office=='PRESIDENT','office'] = 'US PRESIDENT'


# In[36]:


df.loc[df.district=='003 - EAST','district'] = '003, EAST'
df.loc[df.district=='005 - SALISBURY','district'] = '005, SALISBURY'
df.loc[df.district=='007 - SOUTHEAST','district'] = '007, SOUTHEAST'

df[df.district.str.contains('-')].district.unique()


# In[ ]:





# In[39]:


simnames = [
('JOE JOHN', 'CASEY JOE JOHNSON',0), #diff offices
('JOAN WHITE', 'JOAN H WHITE',1), #unsure but i think the same: diff offices but county boe and soil and water
('CHRIS CLARK', 'CHRISTY CLARK',0), #diff offices
('DANIEL FURR','CURTIS DANIEL FURR',0), #same person
('MIKE CASKEY', 'MIKE CAUSEY',0), #diff offices
('BARRY B SIMS', 'BARRY C SIMS',0), # i think these are different because the offices are in diff counties?
('DAVID BARBEE', 'DAVID BARBER',0), #diff
('DAVID WILLIS', 'DAVID WILLIAMS',0), #diff
('KEVIN HAYNES', 'KEVIN H HAYNES',1), #same, second is correct
('MARK R JONES', 'MARK S JONES',0), #diff
('JOEY MCCLELLAN', 'JOEY MCLELLAN',1), #same second is correct
('JOHN CARSWELL', 'JOHNNIE CARSWELL',0), #same
('KENT WILLIAMS', 'KENT WILLIAMSON',0), #diff counties, both not writein
('WESLEY HARRIS', 'GAYLE WESLEY HARRIS',0), #diff, diff districts
('CAL CUNNINGHAM', 'CARLA CUNNINGHAM',0), #diff ppl
('DAVID WILLIAMS', 'RAYMOND DAVID WILLIAMS SR',0), # diff counties
('EVELYN BULLUCK', 'EVELYN HINES BULLUCK',1), #same?
('PETER ASCUITTO','PETER ASCIUTTO',1), #same, second is correct
('DEXTER TOWNSEND', 'DEXTER G TOWNSEND',1) #same, second is correct
]


# In[40]:


# '''
# for name1, name2, i in simnames:
#     print(name1)
#     print('\t',df[df.candidate==name1].office.unique(), df[df.candidate==name1].party_detailed.unique(),df[df.candidate==name1].county_name.unique(),df[df.candidate==name1].district.unique(),df[df.candidate==name1].writein.unique())
#     print(name2)
#     print('\t',df[df.candidate==name2].office.unique(), df[df.candidate==name2].party_detailed.unique(),df[df.candidate==name2].county_name.unique(),df[df.candidate==name2].district.unique(),df[df.candidate==name2].writein.unique())
#     print('\n')
# '''


# In[41]:


for name1, name2, i in simnames:
    if i ==1:
        df.loc[df.candidate==name1,'candidate'] = name2


# In[42]:


#Let's drop rows where df[(df['writein']=="TRUE")&(df['votes']==0)]. There are over 100k rows of this, and it should make this test more accurate.
df['votes'] = df['votes'].astype(int)
print(len(df))
indices = df[(df.writein=="TRUE")&(df.votes==0)].index
df = df.drop(index = indices)
print(len(df))


# In[43]:


# df.loc[df.office=="COUNCIL MEMBER - BADIN",'office'] ="TOWN COUNCIL - BADIN"


# In[44]:


df['district'] = np.where(df['office'] == 'US PRESIDENT', "STATEWIDE", df['district'])


# In[45]:


#check for duplicates before dropping the extra columns
dups = df[df.drop(columns = 'votes').duplicated(keep = False)].sort_values(['precinct','office','candidate','mode','votes'])
dups


# In[193]:


df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()
df = df.replace('  ', ' ', regex = True) #.replace('- ','-', regex = True) #.replace('  ', ' ', regex = True)
df = df.applymap(lambda x: x.strip() if type(x) == str else x)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


#less duplicates when keeping contest_title, none when keeping group_num


# In[51]:


df.to_csv("/Users/declanchin/Desktop/MEDSL/2020-precincts/precinct/NC/2020-nc-precinct-general-sorted.csv", quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[52]:


# get_ipython().system('jupyter nbconvert --to script nc_cleaning_script_updated_data.ipynb')


# ### Everything under here is for analysis of weird mode issue - detailed on issue page

# In[48]:


#analysis
'''
df['mode'].unique()
modes = ['PROVISIONAL','ABSENTEE','TRANSFER']


for p in df.precinct.unique():
    for mode in modes:
        if mode in p:
            print(p)
            a = df[(df.precinct == p)&(df['mode'].str.contains(mode))]
            b = df[(df.precinct == p)&~(df['mode'].str.contains(mode))]
            print('\tsame mode unique votes from modes: ',a['mode'].unique(),':',a.votes.unique())
            print('\tdiff mode unique votes from modes: ',b['mode'].unique(),':',b.votes.unique())
            if len(b)<2: print('\tdiff mode unique votes:',b)
        
#there are 7 mode-like values in precinct: ['TRANSFER','ABSENTEE','PROVISIONAL','ABSENTEE SUPPLEMENTAL','ABSENTEE BY MAIL','MAIL ABSENTEE','ABSENTEE MAIL']
#the last 4, ['ABSENTEE SUPPLEMENTAL','ABSENTEE BY MAIL','MAIL ABSENTEE','ABSENTEE MAIL'] all have 0 in the votes column for all rows.
#the other three have some votes where the 'mode' column is similar. for example, where the precinct is 'TRANSFER', there are votes where the mode is 'ELECTION DAY - TRANSFER', but not for the other modes. for 'ABSENTEE', there are votes where the mode is 'ABSENTEE - BY MAIL' but none for the others (including for the mode 'ABSENTEE - ONE STOP').Same for 'PROVISIONAL' with the mode 'PROVISIONAL'
'''


# In[36]:


#analysis
'''
ps = ['TRANSFER','ABSENTEE','PROVISIONAL','ABSENTEE SUPPLEMENTAL','ABSENTEE BY MAIL','MAIL ABSENTEE','ABSENTEE MAIL']
for p in ps:
    a = df[df.precinct==p].votes.unique()
    print(p,a)
'''


# In[ ]:





# In[ ]:





# In[ ]:





# In[369]:


#does every county have votes by mode for each candidate
'''
modes = ['ABSENTEE','ABSENTEE SUPPLEMENTAL','ABSENTEE BY MAIL','MAIL ABSENTEE','ABSENTEE MAIL','ONE STOP','ONE STOP ONE',
        'ONE STOP TWO','ONE STOP THREE','PROVISIONAL','TRANSFER']
modes = df['mode'].unique()
big_dict = {}

for county in df.county_name.unique():
    a = df[df.county_name == county]
    ofs = len(a.office.unique().tolist())
    cs = a.candidate.unique().tolist()
    big_dict[county] = {}
    
    #for of in ofs:
    #    b = a[a.office = of]
    #    big_dict[county][of] = {}
        
    for can in cs:
        b = a[a.candidate == can]
        big_dict[county][can] = {}
        
        for mode in modes:
            c = b[b['mode']==mode]
            big_dict[county][can][mode] = len(c.votes.unique().tolist())
            
        #tally = 0
        #for key in big_dict[county][can]:
        #    if big_dict[county][can][key] == '0': tally += 1
        #if tally == len(candict): print(can, county, modes) #if all the modes have 0 votes
        #print(candict)
'''


# In[49]:


'''
elecday = list()
os = list()
bm = list()
p = list()
cs = list()
tf = list()
for county in big_dict:
    sd = big_dict[county]
    for mode in modes:
        for can in sd:
            
    votes = [sd[mode] for mode in modes]
    if
'''


# In[373]:


#old_c = pd.read_csv('C:/Users/abguh/Desktop/urop/2020-precincts/precinct/NC/2020-nc-precinct-general.csv')


# In[ ]:





# In[50]:


'''
for county in old_c.county_name.unique():
    a = old_c[old_c.county_name == county]
    ofs = len(a.office.unique().tolist())
    cs = a.candidate.unique().tolist()
    big_dict[county] = {}
    
        
    for can in cs:
        b = a[a.candidate == can]
        big_dict[county][can] = {}
        if len(b['mode'].unique().tolist()) != 4: print(county, can, b['mode'].unique())
        for mode in modes:
            c = b[b['mode']==mode]
            big_dict[county][can][mode] = c.votes.sum()
    '''


# In[386]:


'''
for mode in modes:
    l = list()
    for county in big_dict:
        sd = big_dict[county]
        for can in sd:
            if sd[can][mode] not in l:
                l.append(sd[can][mode])
        if len(l)<10:
            print(county, mode,':',l)
            '''


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




