#!/usr/bin/env python
# coding: utf-8

# Non-exhaustive list of changes needed to update to the 2021 format.
# 
# 1. Add columns {'jurisdiction_fips', 'county_fips', 'readme_check', 'date', 'magnitude'}.
# 2. Remove column "" (which seems to be an index column).
# 3. Remove periods and commas from candidate names. Be careful with double initial names, make sure they remain separated (e.g. J.C. BURRIS to J C BURRIS).
# 4. Replace all parentheses surrounding nicknames with double quotation marks (e.g. JAMES (JIM) DEMAY to JAMES "JIM" DEMAY).
# 5. Several candidates triggered the QA checker mutual similarity checks (e.g. ANNA RICHARDSON and ANNA HALL RICHARDSON). Investigate them and make sure the names are unified wherever they represent the same candidate.
# 6. Move seat, ward and district information from office to the district column.
# 7. Zero-pad numerical districts of length three.
# 8. Several candidates appear as running with one party in some rows, and no party in other rows. Investigate those and make sure they are correct.
# 9. Try and determine the source of the votes==-1 rows.
# 10. Change candidate name [WRITE-IN] to WRITEIN.
# 11. Several candidates appear as running as both writeins and not writeins. Investigate those and determine whether these are appropriate.
# 12. Remove named writein candidates that appear somewhere having received 0 votes where appropriate.

# In[93]:


import pandas as pd
import numpy as np
import os
import zipfile
import re
import csv


# In[94]:


with zipfile.ZipFile('2018-nc-precinct-autoadapted.csv.zip', 'r') as zip_ref:
        zip_ref.extractall("raw")
df = pd.read_csv('raw/2018-nc-precinct-autoadapted.csv',index_col=False)


# In[ ]:





# In[95]:


#MERGING COUNTY_FIPS
df['state'] = 'North Carolina' #need it like this to merge; CHANGE LATER
countyFips = pd.read_csv("../../../help-files/county-fips-codes.csv")
#print(countyFips.head)
df = pd.merge(df, countyFips, on = ['state','county_name'],how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
#now can change 'state' column  back to NC
df['state'] = df['state'].str.upper()


# In[96]:


df['magnitude'] = 1
df['readme_check'] = 'FALSE'
df['date'] = '2018-11-06' #check formatting


# In[97]:


l = list()
def fix_cand(x):
    x=x.replace("''",'"')
    x=x.replace(',','')
    if '.' in x:
        if x[-1] != '.' and x[x.find('.')+1] != ' ': return x.replace('.',' ')
        else: return x.replace('.','')
    if '/(' in x or '"' in x: #middle names or nick names 
        
        x=x.replace('/(','"').replace('/)','"')
        x=x.replace('(','"').replace(')','"')
        
            
        if len(x.split())>2 and len(x.split()[2]) ==1: #if it's an initial after the nickname
            return x.split()[0] +' '+ x.split()[2]+' '+x.split()[1] +' '+ ' '.join(x.split()[3:])
        else: 
            return x
    if 'WRITE' in x: return 'WRITEIN'
    
    return x
df['candidate'] = df['candidate'].apply(lambda x: re.sub("[()]",'"', x))
df['candidate'] = df['candidate'].apply(fix_cand)


# In[98]:


sorted(df.candidate.unique())[:10]


# 6. Move seat, ward and district information from office to the district column.
# 7. Zero-pad numerical districts of length three.

# In[99]:


sorted(df[df.district!='""'].office.unique())


# In[100]:


def fix_dist(x, dist): #x is the office

    if 'CITY OF LINCOLNTON CITY COUNCIL' in x: return x.replace(' (UNEXPIRED TERM)','').split()[-1].zfill(3)
    if x.split()[-2] == 'SEAT': return x.split()[-1].zfill(3)
    if (x.split()[-2]=='DISTRICT' or x.split()[-2] == 'WARD' ) and len(x.split()[-1])==1: 
        if x.split()[-1].isnumeric(): return x.split()[-1].zfill(3)
        else: return x.split()[-1]
    if x.split()[-1] =='DISTRICT' and 'FIRE' not in x:
        if 'COMMISSIONERS' in x: return x[x.find('NERS')+5:].replace(' DISTRICT','')
        else: return x.split()[-2]
    elif 'AT-LARGE' in x: return 'AT-LARGE'
    if dist.isnumeric(): return dist.zfill(3)

    return dist

def get_office(x):
    x=x.replace(' (UNEXPIRED)','').replace('AT-LARGE','').replace('TWP','TOWNSHIP')
    x=x.replace('COUNTY-WIDE','')
    x=x.replace('COUNTY OF LEE','LEE COUNTY').replace('COUNTY OF CAMDEN','CAMDEN COUNTY')
    x=x.replace('NC ','').replace('BD OF','BOARD OF').replace(' (UNEXPIRED TERM)','')
    if re.match('US PRESIDENT',x):      return 'US PRESIDENT'
    if 'DISTRICT COURT' in x: return x
    if 'BOARD OF' in x:
        if 'EDUCATION' in x: 
            city = x[:x.find('BOARD')].replace('SCHOOLS ','').strip()
            if "TOWNSHIP" in x:
                township = x.split('EDUCATION ')[-1]
                return 'BOARD OF EDUCATION - '+city + ', ' + township
            elif x.endswith('DISTRICT'):
                district = x.split('EDUCATION ')[-1]
                return 'BOARD OF EDUCATION - '+city + ', ' + district
            elif x.endswith('LIMITS'):
                limits = x.split('EDUCATION ')[-1]
                return 'BOARD OF EDUCATION - '+city + ', ' + limits 
            else: return 'BOARD OF EDUCATION - '+city
        elif 'COMMISSIONER' in x:
            city = x[:x.find('BOARD')]
            return 'BOARD OF COMMISSIONERS - '+city
    elif 'SOIL AND W' in x:
        # all county level offices
        return 'COUNTY SOIL AND WATER CONSERVATION DISTRICT SUPERVISOR'
    elif "SHERIFF" in x:
        return "COUNTY SHERIFF"
    elif "CLERK OF SUPERIOR COURT" in x:
        return "COUNTY CLERK OF SUPERIOR COURT"
    elif "REGISTER OF DEEDS" in x:
        return "COUNTY REGISTER OF DEEDS"
    elif 'CITY OF' in x:
        if 'ROANOKE' in x: return 'PROPERTY TAX REFERENDUM - ROANOKE RAPIDS'
        else: city = x.split()[2]   #all cities are one word except for ROANOKE RAPIDS
        if 'COUNCIL' in x: return 'CITY COUNCIL - '+city
        return x[x.find(x.split()[3]):]+ ' - '+city
    elif 'SEAT' in x:
        if 'DISTRICT' in x: return x[:x.find('E DIS')+1] 
        else: return x[:x.find('SEAT')-1]
    elif re.match("STATE SENATE", x):         return "STATE SENATE"
    elif re.match("HOUSE OF REPRESENTATIVES", x): return "STATE HOUSE"
    elif re.match("US HOUSE OF REPRESENTATIVES", x): return "US HOUSE"
    elif      'DISTRICT ATTORNEY' in x:               return 'DISTRICT ATTORNEY'

    elif 'VILLAGE OF' in x: return ' '.join(x.split()[4:]) + ' - '+ x.split()[3]
    return x

def remove_county(x):
    if len(x)>1 and x[0] == '-': x=x[2:]
    if 'ELECTION' in x and 'TOWN' in x: 
        if 'TOWN OF LAKE' in x: return 'MALT BEVERAGE ELECTION - LAKE WACCAMAW'
        x= x[:x.find('- ')+2] + x[x.find('TOWN'):] #.replace('TOWNSHIP OF ','')
    if 'COUNTY' in x: return 'COUNTY '+x[:x.find(' -')]
    if 'BOARD OF COMMISSIONERS' in x and 'TOWN' in x: return 'TOWN COMMISSIONER - '+x[x.find('N OF ')+5:]
    if 'COUNCIL' in x:
        if 'VILLAGE' in x: return 'VILLAGE COUNCIL - MISENHEIMER'
        elif 'BADIN' in x: return 'TOWN COUNCIL - BADIN'
        else: return x
    if 'CITY' in x[-5:]: return x[:-5]
    if 'TOWN OF' in x: return x.replace('TOWN OF ','')
    elif 'TOWNSHIP OF' in x: return x.replace('TOWNSHIP OF ','')
    return x

def get_special(x):
    return str('UNEX' in x).upper()


# In[101]:


df['special'] = df['office'].apply(get_special)
df['district'] = df.apply(lambda x: fix_dist(x['office'],x['district']),axis=1)
df['district'] = df['district'].replace(['ONE','TWO','THREE'],['001','002','003'])
df['office'] = df['office'].apply(get_office)
# df['office'] = df['office'].apply(remove_county).str.strip()
df.loc[df['office'].str.contains('DISTRICT COURT JUDGE'), 'office'] = 'DISTRICT COURT JUDGE'
#sorted(df.office.unique())


# In[102]:


#df[(df.office.str.contains('DISTRICT'))|(df.office.str.contains('WARD'))|(df.office.str.contains('SEAT'))][['office','district']].drop_duplicates()
df[df.office.str.contains('STATE')][['office','district']].drop_duplicates()


# In[103]:


df.district.unique()


# 8. Several candidates appear as running with one party in some rows, and no party in other rows. Investigate those and make sure they are correct.
# 

# In[104]:


# see which counties have nonpartisan boards of education
np = list()
cs = df.county_name.unique()
for c in cs:
    a = df[(df.office.str.contains('BOARD OF EDUCATION'))&(df.county_name ==c)].party_detailed.unique()
    
    if len(a)<1 or (len(a)==1 and a!='DEMOCRAT'): 
        # print(c,':',a)
        np.append(c)


# In[105]:


#all these are nonpartisan
df.loc[df.office.str.contains('SOIL AND WATER'),'party_detailed'] = 'NONPARTISAN'

for c in np:
    df.loc[(df.office.str.contains('BOARD OF EDUCATION'))&(df.county_name==c),'party_detailed'] = 'NONPARTISAN'
    


# In[106]:


cands = {
    #'BENTON DRY': ['DEMOCRAT', ""], #dem
    #'CHAD BROWN': ["", 'REPUBLICAN'], #BOE is nonpartisan
    #'CLAY LOGAN': ['REPUBLICAN', ""], #two offices, soil&water is nonpartisan
    #'DAVID MORGAN': ["", 'DEMOCRAT'], #district 4
    #'GREG WEST': ["" ,'DEMOCRAT'], #BOE is nonpartisan
    #'HARPER PETERSON': ['DEMOCRAT', ""], #soil and water is nonpartisan
    #'JAMES WEST': ['DEMOCRAT', ""], #BOE is nonpartisan
    #'JENNIFER GRAHAM': ["", 'DEMOCRAT'],#BOE is nonpartisan
    #'JESSICA HOLMES': ['DEMOCRAT', ""], #BOE is nonpartisan
    #'JOHN JOHNSON': ['DEMOCRAT', ""], #soil&water is nonpartisan
    #'KEVIN JONES': ['REPUBLICAN', ""], #boe is nonpartisan
    #'LESLIE COHEN': ['DEMOCRAT', ""], #soil and water is nonpartisan
    #'PAUL WRIGHT': ["", 'REPUBLICAN'], #soil and water is nonpartisan
    #'RODNEY JOHNSON': ['DEMOCRAT', ""], #soil and water is nonpartisan
    #'RONNIE SMITH': ["", 'DEMOCRAT'], #soil and water is nonpartisan
    #'SEAN LAVIN': ["", 'REPUBLICAN'], #boe is nonpartisan
    'TOM KEIGHER': ["", 'REPUBLICAN']} #boe is nonpartisan


# In[107]:




# In[ ]:





# In[108]:


#df.loc[df.candidate=='BENTON DRY','district'] = '002' ##BENTON DRY ran for albemarle city council in district 2, not at large
df.loc[df.candidate=='BENTON DRY','party_detailed'] = 'DEMOCRAT'
#df.loc[(df.candidate=='DAVID MORGAN')&(df.office=='CITY COUNCIL - ALBEMARLE'),'district'] = '004' 
df.loc[(df.candidate=='DAVID MORGAN')&(df.office=='CITY COUNCIL - ALBEMARLE'),'party_detailed'] = 'DEMOCRAT' 


# In[109]:


###Similar names
sims = """DON DAVIS ||| [[DONNA DAVIS]] 
    BILL DAVIS ||| [[BILLY DAVIS]] 
    DAVID OWEN ||| [[DAVID OWENS]] 
    JOEL DAVIS ||| [[JOEY DAVIS]]
    DAVID ADAMS ||| [[DAVID P ADAMS]]
    DAVID PRICE ||| [[DAVID J PRICE]]
    HARRY BROWN ||| [[LARRY BROWN]] 
    KEN COLLIER ||| [[KEVIN COLLIER]]
    ARIC WILHELM ||| [[ARIN WILHELM]]  
    DAVID HARRIS ||| [[DAVID HARRISON]]
    HELEN O'DALY ||| [[HELEN R O'DALY]]
    IAN MCMILIAN ||| [[IAN MCMILLAN]]
    JUSTIN DAVIS ||| [[JUSTIN N DAVIS]]
    RONALD PARKS ||| [[RONALD W PARKS]]
    VINCE ROZIER ||| [[VINCE ROZIER, JR]]
    DAVID A SMITH ||| [[DAVID T SMITH]]
    JERRY R JONES ||| [[JERRY W JONES]]
    KEVIN COLLIER ||| [[KEVIN L COLLIER]]
    DAVID WILLIAMS ||| [[RAYMOND DAVID WILLIAMS, SR]]
    RUSSELL HORTON ||| [[RUSSELL G HORTON]]
    TERRY WILLIAMS ||| [[TERRY A WILLIAMS]]
    TRACY PHILBECK ||| [[TRACY L PHILBECK]]
    ANNA RICHARDSON ||| [[ANNA HALL RICHARDSON]]
    ROBERT T REIVES ||| [[ROBERT T REIVES II]]
    TONY HOLLIFIELD ||| [[TOMMY HOLLIFIELD]]
    JENNIFER STRICKLAND ||| [[JENNIFER SMITH STRICKLAND]]
    
    """ #same, should contain smith
sims = sims.split(']]')
sims = [s.replace('\n    ','').split(' ||| [[') for s in sims]
sims = sims[:-1]


# In[110]:


# for pair in sims:
#     name1 = pair[0]
#     name2 = pair[1]
#     a = df[df.candidate==name1]
    
#     b = df[df.candidate==name2]
#     if len(a.county_name.unique()) ==1 and len(b.county_name.unique()) ==1 and a.county_name.unique() == b.county_name.unique():
#         print(name1, a.office.unique(), a.county_name.unique(), a.writein.unique(), a.party_detailed.unique())
#         print(name2, b.office.unique(), b.county_name.unique(), b.writein.unique(), b.party_detailed.unique())
#         print('\n')
#     #print(pair)
    #print('\t',a==b)


# In[111]:


correct_names = [('DAVID ADAMS','DAVID P ADAMS'), ("HELEN O'DALY","HELEN R O'DALY"),("JUSTIN DAVIS","JUSTIN N DAVIS"),
                ("RONALD PARKS","RONALD W PARKS"), ("KEVIN COLLIER",'KEVIN L COLLIER'),('TRACY PHILBECK','TRACY L PHILBECK'),
                ('ANNA RICHARDSON','ANNA HALL RICHARDSON'),('TONY HOLLIFIELD','TOMMY HOLLIFIELD'),
                ('JENNIFER STRICKLAND','JENNIFER SMITH STRICKLAND')]

for c1, c2 in correct_names:
    df.loc[df.candidate==c1,'candidate'] = c2


# In[112]:


#tommy hollifield unsure about - both in mcdowell county, one for county BOE , one for soil and water conservation district
#supervisor 


# In[113]:


##cands with multiple writein values
c_write = '''
    ANNA HALL RICHARDSON: ['True' 'False']
    BENTON DRY: ['False' 'True']
    BILL CHAPMAN: ['False' 'True']
    CAL BERRYHILL: ['True' 'False']
    CHAD BROWN: ['True' 'False']
    CHRIS WEST: ['True' 'False']
    CLAUDE E SHEW JR: ['True' 'False']
    CLAY LOGAN: ['False' 'True']
    DAVID MORGAN: ['True' 'False']
    DAVID P ADAMS: ['True' 'False']
    DONALD MIAL: ['True' 'False']
    GIL BURROUGHS: ['True' 'False']
    HARPER PETERSON: ['False' 'True']
    HEATHER SCOTT: ['True' 'False']
    HELEN R O'DALY: ['False' 'True']
    IAN MCMILLAN: ['True' 'False']
    JAMES WEST: ['False' 'True']
    JENNIFER GRAHAM: ['True' 'False']
    JESSICA HOLMES: ['False' 'True']
    JOHN JOHNSON: ['False' 'True']
    JUSTIN N DAVIS: ['False' 'True']
    KEVIN L COLLIER: ['False' 'True']
    LASHAWNDA WASHINGTON: ['False' 'True']
    LEE DEDMON: ['True' 'False']
    LESLIE COHEN: ['False' 'True']
    NANCY HEINIGER: ['True' 'False']
    NATALIE MURDOCK: ['False' 'True']
    PAUL WRIGHT: ['True' 'False']
    REGINALD SILVER: ['False' 'True']
    RICK PRIDGEN: ['True' 'False']
    ROBERT MOORE: ['True' 'False']
    RODNEY JOHNSON: ['False' 'True']
    RONALD W PARKS: ['True' 'False']
    SEAN LAVIN: ['True' 'False']
    STEVE CHAPMAN JR: ['False' 'True']
    STEVE HALL: ['True' 'False']
    TOM KEIGHER: ['True' 'False']
    TRACY L PHILBECK: ['True' 'False']
    WADE LEATHAM: ['True' 'False']
    WAYNE COOK: ['True' 'False']
    '''
c_write = c_write.split('\n')
c_write = [x[:x.find(':')].strip() for x in c_write][1:-1]
c_write


# In[114]:


# for c in c_write:
#     a = df[(df.candidate==c) & (df.writein==True)]
#     b = df[(df.candidate==c) & (df.writein==False)]
    
#     if len(a.office.unique()) != len(b.office.unique()):
#         print('unequal numbers:',c)
#     elif a.office.unique() == b.office.unique():
#         print('same office but diff writein values:',c)
    #print(a.office.unique())


# In[115]:


df[df.candidate=='DAVID MORGAN'][['precinct','candidate','office','district','writein','party_detailed','county_name']].drop_duplicates()


# In[116]:


#(df[(df.party_detailed.isnull())&(df.writein==False)].office.unique()) #null parties - which ones aren't referendums?

of = [ 'BIPARTISAN BOARD OF ETHICS AND ELECTIONS',
      'CITY COUNCIL - ARCHDALE',  'CITY COUNCIL - LOCUST',
 'COUNCIL MEMBER - BADIN','COUNTY ENGELHARD SANITARY DISTRICT SUPERVISOR','COUNTY MAGGIE VALLEY SANITARY DISTRICT BOARD MEMBE',
       'COUNTY OCRACOKE SANITARY DISTRICT SUPERVISOR', 'COUNTY SWAN QUARTER SANITARY DISTRICT SUPERVISOR',
'MAYOR - ARCHDALE',  'MAYOR - BOONVILLE',  'MAYOR - DOBSON', 'MAYOR - EAST BEND', 'MAYOR - JONESVILLE',
 'MAYOR - LOCUST', 'MAYOR - NEW LONDON', 'MAYOR - NORWOOD', 'MAYOR - OAKBORO', 'MAYOR - PILOT MOUNTAIN',
 'MAYOR - RICHFIELD', 'MAYOR - STANFIELD', 'MAYOR - STAR', 'MAYOR - TROY','SANITARY DISTRICT BOARD - HANDY',
 'SANITARY DISTRICT BOARD - MINZIES CREEK, PERQUIMANS', 'SANITARY DISTRICT BOARD - NONPARTISAN','TOWN COMMISSIONER - BOONVILLE',
 'TOWN COMMISSIONER - DOBSON', 'TOWN COMMISSIONER - EAST BEND', 'TOWN COMMISSIONER - ELKIN',
 'TOWN COMMISSIONER - JONESVILLE', 'TOWN COMMISSIONER - NEW LONDON', 'TOWN COMMISSIONER - OAKBORO',
 'TOWN COMMISSIONER - PILOT MOUNTAIN', 'TOWN COMMISSIONER - RICHFIELD', 'TOWN COMMISSIONER - STANFIELD',
 'TOWN COMMISSIONER - STAR', 'TOWN COMMISSIONER - TROY', 'TOWN COUNCIL - NORWOOD', 'TOWN COUNCIL - RED CROSS']

# for o in of:
#     a = df[df.office==o].party_detailed.unique()
#     print(o, a)


# In[ ]:





# In[117]:


##they're all nan, so all nonpartisan
for o in of:
    df.loc[df.office==o,'party_detailed'] = 'NONPARTISAN'


# In[118]:


##final fixes to party columns
df['party_detailed'] = df['party_detailed'].replace({'UNAFFILIATED':'INDEPENDENT'})
df.loc[df.candidate=='WRITEIN','party_detailed'] = ""
df['party_simplified'] = df['party_detailed'].replace({'CONSTITUTION':'OTHER','GREEN':'OTHER'})
df.party_simplified.unique()


# In[119]:


df['writein'] = df.writein.replace({True:'TRUE',False:'FALSE'})


# In[120]:


indices = df[(df.writein=='TRUE')&(df.votes==0)].index
print(len(df))
df.drop(index=indices, inplace=True)
print(len(df))


# In[121]:


df[df.votes==-1].dataverse.unique()


# ##### 10/19 fixes
# 12. Remove rows where candidates are blank and the votes are zero.
# 13. df['candidate'] = df['candidate'].str.replace("CARLOS JANE'","CARLOS JANE",regex=False)
# 14. df.loc[df['office']=='SUPERIOR COURT JUDGE','dataverse'] = 'STATE
# 15. Name outputted files with "2018-nc-precinct-general-updated.csv"
# 16. Replace "FOR"/"AGAINST" with yes/no
# 
# 

# In[122]:


len(df[df.candidate=='""'])


# In[123]:


#12
indices = df[(df.candidate=='""')&(df.votes==0)].index
print(len(df))
df.drop(index=indices, inplace=True)
print(len(df))


# In[124]:


#13&14&16
df['candidate'] = df['candidate'].str.replace("CARLOS JANE'","CARLOS JANE",regex=False)
df.loc[df['office']=='SUPERIOR COURT JUDGE','dataverse'] = 'STATE'
df['candidate'] = df['candidate'].replace({'FOR':'YES','AGAINST':'NO'})
df[df.candidate=='AGAINST']


# In[ ]:


df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()
print('made copy')
df = df.fillna("")
df = df.replace('  ', ' ', regex = True).replace('""',"",regex = True)
print('1/2')
df = df.applymap(lambda x: x.strip() if type(x) == str else x)
print('done')


# In[ ]:


df.to_csv("2018-nc-precinct-general-updated.csv", quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[ ]:


#get_ipython().system('jupyter nbconvert --to script nc_2021_updates.ipynb')


# In[ ]:





# In[ ]:




