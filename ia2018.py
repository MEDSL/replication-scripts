#!/usr/bin/env python
# coding: utf-8

# 1. Add columns {'county_fips', 'jurisdiction_fips', 'magnitude', 'date', 'readme_check'}.
# 2. Remove periods and commas from candidate names. Be careful of double initial names, make sure to keep them separated (e.g. AARON A.J. STONE to AARON A J STONE).
# 3. Make these replacements in the candidate column:
# *(BLANK), BLANK, BLANNK, NO NAME, BLANK_NO NAME, BLANK/FICTIONAL with UNDERVOTES
# *[WRITE-IN] with WRITEIN
# *KATHY SMITH (KEVIN) with KATHY "KEVIN" SMITH
# *JON (ILLEGIBLE LAST NAME) with JON "ILLEGIBLE LAST NAME"
# 4. Remove double spaces from candidate names (e.g. SHANNON PAULUS to SHANNON PAULUS), as well as extra space after dashes (e.g. KATIE SACKETT- STADHEIM to KATIE SACKETT-STADHEIM).
# 5. Replace single quotation marks surrounding nicknames with double quotation marks (e.g. ROBERTA 'BERT' SIMMONS to ROBERTA "BERT" SIMMONS).
# 6. Several candidate names appear to be similar (e.g. GARY SMITH and GARY G. SMITH, JEFF MEIER and JEFF MEYER). Investigate those and make sure similarly named candidates are labeled the same.
# 7. Standardize retention elections so they follow the new format.
# 8. Zero-pad numerical districts so they have length three.
# 9. Standardize TRUSTEE, CLERK and similar so the position name appears before the town name (e.g. ELKHART TOWNSHIP TRUSTEE to TRUSTEE - ELKHART TOWNSHIP).
# 10. Investigate RYAN MARQUARDT, who appears as running as DEMOCRAT in some rows, and with an empty party in others.
# 11. Mark rows containing negative votes as readme_check=TRUE in accordance with the decision taken in the original 2018 issue.

# In[616]:


import pandas as pd
import numpy as np
import os
import re
import csv


# In[617]:


official_dtypes = {'precinct':str,'office':str, 'party_detailed':str, 'party_simplified':str,'mode':str,'votes':int, 
                   'county_name':str, 'county_fips':str, 'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 
'district':str, 'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str, 'state_po':str, 
                   'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str, 'readme_check':str,'magnitude':int}


# In[618]:


df = pd.read_csv('2018-ia-precinct-autoadapted.csv',index_col=False, dtype = official_dtypes)
df = df.fillna('')
df = df.replace('""',"")


# In[619]:


#MERGING COUNTY_FIPS
df['state'] = 'Iowa'
countyFips = pd.read_csv("../../../help-files/county-fips-codes.csv")
df = pd.merge(df, countyFips, on = ['state','county_name'], how = 'left')
df['county_fips'] = df['county_fips'].apply(str)
df['jurisdiction_fips'] = df['county_fips']
df['county_name'] = df['jurisdiction_name']
#now can change 'state' column  back to NC
df['state'] = df['state'].str.upper()


# In[620]:


df['readme_check'] = 'FALSE'
df['date'] = '2018-11-06' 


# In[ ]:





# In[ ]:





# candidate updates

# In[621]:


def fix_cand(x):
    x=x.replace("''",'"')
    x=x.replace(',','').replace('Ã','A')
    if "'" in x and x[x.find("'")-1] == ' ': #i.e. if it is not like O'Brien, which we would want to keep as a single quote
        x=x.replace("'",'"')
    x = x.replace('Â','').replace('\xa0','').replace('©','')
    if x == 'AGAINST': return 'NO'
    if x == 'FOR': return 'YES'
    if 'BLANK' in x: return 'UNDERVOTES'
    if 'WRITE-IN' in x: return 'WRITEIN'
    if '.' in x:
        if x[-1] != '.' and x[x.find('.')+1] != ' ': return x.replace('.',' ')
        else: return x.replace('.','')
    return x
df['candidate'] = df.candidate.apply(fix_cand)
df['candidate'] = df['candidate'].apply(lambda x: re.sub("[()]",'"', x))
#df['candidate'] = df.candidate.apply(lambda x: x.replace(' "','"'))


# In[622]:


df['district'] = df.district.apply(lambda x: x.zfill(3) if type(x)==str and len(x)>=1 else x)


# In[623]:


df.district.unique()


# Several candidate names appear to be similar (e.g. GARY SMITH and GARY G. SMITH, JEFF MEIER and JEFF MEYER). Investigate those and make sure similarly named candidates are labeled the same.
# 

# Standardize retention elections so they follow the new format.
# Standardize TRUSTEE, CLERK and similar so the position name appears before the town name (e.g. ELKHART TOWNSHIP TRUSTEE to TRUSTEE - ELKHART TOWNSHIP).
#     

# In[624]:


def get_special(x):
    if 'VACANCY' in x or 'TFV' in x: return 'TRUE'
    elif ' VAC' in x: return 'TRUE'
    else: return 'FALSE'
    

df['special'] = df['office'].apply(get_special)


# In[625]:


l = list()
def standardize_office(x):
    if 'TO FILL A VACANCY' in x: x = x.replace(' TO FILL A VACANCY','')
    elif 'TO FILL VACANCY' in x: x = x.replace('TO FILL VACANCY','')
    elif 'TFV' in x: x = x.replace(' TFV','')
    elif ' VACANCY' in x: x = x.replace(' VACANCY','')
    elif ' VAC' in x: x = x.replace(' VAC','')
    if 'VOTE FOR' in x: x = x[:x.find(' VOTE FOR')]
    
    x = x.replace('TWP','TOWNSHIP').replace('.','').replace(',','').replace('-','').replace('  ',' ')
    if 'TOWNSHIP' in x:
        if 'CLERK' in x and x.split()[0] != 'TOWNSHIP':
            return 'TOWNSHIP CLERK -'+ ' '+x[:x.find(' TOWNSHIP')]
        elif 'CLERK' in x: return 'TOWNSHIP CLERK -'+' '+x.replace('TOWNSHIP CLERK ','')
        elif x.split()[0] != 'TOWNSHIP': return 'TOWNSHIP TRUSTEE -'+' '+x[:x.find(' TOWNSH')]
        else: return 'TOWNSHIP TRUSTEE -'+' '+ x.replace('TOWNSHIP TRUSTEE ','')
    if 'SUPERVISOR' in x or 'BOS' in x:
        if 'COUNTY' in x: return 'COUNTY BOARD OF SUPERVISORS'
        else: return 'BOARD OF SUPERVISORS'
        if x not in l:
            l.append(x)
            print(x)
    return x


# In[626]:


def get_district(off, dist):
    if ('SUPERVISOR' in off or 'BOS' in off) and off[-1].isnumeric(): return off[-1].zfill(3)
    elif 'AT-LARGE' in off: return 'AT-LARGE'
    elif 'NORTHWEST' in off: return 'NORTHWEST'
    elif 'NORTHEAST' in off: return 'NORTHEAST'
    else: return dist

df['district'] = df.apply(lambda x: get_district(x['office'],x['district']),axis=1)
df['office'] = df['office'].apply(standardize_office)


# In[627]:


sorted(df.office.unique())


# In[628]:


df[df.office.str.contains('SUPERVISOR')][['office','district']].drop_duplicates() 


# Investigate RYAN MARQUARDT, who appears as running as DEMOCRAT in some rows, and with an empty party in others.
# 

# In[629]:


df[df.candidate=='RYAN MARQUARDT'][['office','party_detailed','district','county_name']].drop_duplicates() #.office.unique()


# In[630]:


df[df.office.str.contains('TRUSTEE')].party_detailed.unique()
#looks like he ran for state house and township trustee/clerk, which is a nonpartisan office, or at least has no party info listed for any


# Mark rows containing negative votes as readme_check=TRUE in accordance with the decision taken in the original 2018 issue.

# In[631]:


df.loc[df.votes<0, 'readme_check'] = 'TRUE'
df[df.readme_check=='TRUE'].votes.unique()


# In[ ]:





# In[ ]:





# retention elections

# In[632]:


def fix_retention(off, cand):
    """return CANDIDATE NAME - YES/NO"""
    if 'JUDGE' in off:
        name = off[off.find(' JUDGE')+7:]
        return name + ' - '+cand
    return cand #otherwise just return candidate value

df['candidate'] = df.apply(lambda x: fix_retention(x['office'], x['candidate']),axis=1)
df['office'] = df['office'].apply(lambda x: x[:x.find('JUDGE')+5] if 'JUDGE' in x else x)


# In[633]:


df[(df.office.str.contains('JUDGE'))|(df.office.str.contains('COURT'))].candidate.unique()


# In[634]:


cands = '''   ED SMITH ||| [[TED SMITH]]
    MCINTIRE ||| [[TERRINDA MCINTIRE]]
    GENE LONG ||| [[EUGENE LONG]]
    ILLEGIBLE ||| [[JON "ILLEGIBLE LAST NAME"]]
    JOHN ROTH ||| [[JOHN GROTH]]
    JON MILLS ||| [[JOHN MILLS]]
    MARY WARD ||| [[MARY JO WARD]]
    MATT MANN ||| [[MATT MCCANN]]
    RANDY RAY ||| [[RANDY CRAY]]
    A J TAYLOR ||| [[REBECCA J TAYLOR]]
    DAN CONWAY ||| [[DIANE CONWAY]]
    DAN HANSEN ||| [[DAN HANSON]]
    DAN JENSEN ||| [[DAN JEPSEN]]
    DAN SAVERY ||| [[DEAN AVERY]]
    DAVID BEAR ||| [[DAVID BENNAR]]
    DUANE FOLZ ||| [[DUANE VOLZ]]
    GARY SMITH ||| [[GARY G SMITH]]
    GREG SMITH ||| [[KREG SMITH]]
    JEFF MEIER ||| [[JEFF MEYER]]
    JOHN GROTE ||| [[JOHN GROTH]]
    KENT BROWN ||| [[KENTON BROWN]]
    MARC SMITH ||| [[MARK SMITH]]
    MIKE OLSEN ||| [[MIKE OLSON]]
    RYAN BAKER ||| [[RYAN BAKKER]]
    STEVE GARY ||| [[STEVE VARY]]
    STEVE VARY ||| [[STEVEN VARY]]
    ALAN WILSON ||| [[ALAN M WILSON]]
    CHRIS HAGEN ||| [[CHRIS HAGENOW]]
    DALTON RASH ||| [[DALTON RASCH]]
    JAKE HANSON ||| [[JANE HANSON]]
    JULIE ORRIS ||| [[JULIE MORRIS]]
    KEN BOEHMER ||| [[KEVIN BOEHMER]]
    LARRY CLINE ||| [[LARRY KLINE]]
    MARK GANSEN ||| [[MARK HANSEN]]
    MARK MATERN ||| [[MARK MATTEN]]
    STEVE SMITH ||| [[STEVEN SMITH]]
    TERESA WOOD ||| [[TERESA WOODS]]
    ANN WILLIAMS ||| [[ANN C WILLIAMS]]
    BEN HOLLESEN ||| [[BEN HOLLESON]]
    CARLA DUMONT ||| [[CARLA S DUMONT]]
    DAVID HOWELL ||| [[DAVID POWELL]]
    DAVID MCLAIN ||| [[DAVID MCELVAIN]]
    DAVID WILSON ||| [[DAVID K WILSON]]
    DEAN EASTMAN ||| [[DEANNA EASTMAN]]
    DEBRA JENSEN ||| [[DEBRA JESSEN]]
    DENISE STORM ||| [[DENISE L STORM]]
    DON ANDERSON ||| [[JON ANDERSON]]
    ERIC SANDERS ||| [[RICK SANDERS]]
    GARY JOHNSON ||| [[MARY JOHNSON]]
    GARY SCHULTE ||| [[GARY A SCHULTE]]
    GENE GARRETT ||| [[EUGENE GARRETT]]
    GEORGE BRUCE ||| [[GEORGE A BRUCE JR]]
    JERRY PARKER ||| [[JERRY L PARKER]]
    LOREN HELTON ||| [[LORREN HELTON]]
    MARC JOHNSON ||| [[MARY JOHNSON]]
    MARK JOHNSON ||| [[MARY JOHNSON]]
    MARY JOHNSON ||| [[MARTY JOHNSON]]
    MICHAEL BOAL ||| [[MICHAEL BOKL]]
    PAT SULLIVAN ||| [[PATTI SULLIVAN]]
    PAUL KNUTSON ||| [[PAUL KNUDTSON]]
    ROBERT SCOTT ||| [[ROBERT R SCOTT]]
    STEVE WRIGHT ||| [[STEVEN WRIGHT]]
    STEVEN SMITH ||| [[STEVEN L SMITH]]
    TREVOR WHITE ||| [[TREVOR E WHITE]]
    ANDY HELGESON ||| [[RANDY HELGERSON]]
    BECKE BEENKEN ||| [[BECKY BEENKEN]]
    CRAIG JOHNSON ||| [[CRAIG JOHNSTONE]]
    DANIEL MARTIN ||| [[DANIEL MARTINSON]]
    DAVID WILLERT ||| [[DAVID RICKY WILLERT]]
    EDWARD YOTTER ||| [[EDWARD W YOTTER]]
    KEITH JOHNSON ||| [[KEITH L JOHNSON]]
    MARK ANDERSON ||| [[MARV ANDERSON]]
    MARLENE RIVAS ||| [[MARLENE E RIVAS]]
    MELISSA SMITH ||| [[MELISSA D SMITH]]
    PAUL CAMPBELL ||| [[PAUL D CAMPBELL]]
    RON MICKELSON ||| [[RONALD MICKELSON]]
    STAVEN WRIGHT ||| [[STEVEN WRIGHT]]
    BERT HENDERSON ||| [[ROBERT HENDERSON]]
    BLAKE THOMPSON ||| [[BLAINE THOMPSON]]
    BRENT ANDERSON ||| [[BRETT ANDERSON]]
    DARIN PETERSON ||| [[DARWIN PETERSEN]]
    DAVID THOMPSON ||| [[DAVID C THOMPSON]]
    DON MCCULLOUGH ||| [[JOHN MCCULLOUGH]]
    JAMES A MILLER ||| [[JAMES D MILLER]]
    KELLI TOTEMEIR ||| [[KELLI TOTEMEIER]]
    CHRISTINE BOLTE ||| [[CHRISTINE BOTHNE]]
    CONNIE THOMPSON ||| [[CONNIE E THOMPSON]]
    DENNIS ANDERSON ||| [[DENNIS M ANDERSON]]
    DONNA HALVORSEN ||| [[DONNA D HALVORSEN]]
    DOUGLAS D MONCK ||| [[DOUGLAS D HONECK]]
    JEROME D KUSTER ||| [[JEROME "J D " KUSTER]]
    BRADLEY RATCLIFF ||| [[BRADLEY E RATCLIFF]]
    MICHAEL JACOBSON ||| [[MICHAEL W JACOBSON]]
    ROY SCHWICKERATH ||| [[TONY SCHWICKERATH]]
    TRACY L MARSHALL ||| [[TRACEY J MARSHALL]] '''
cands = cands.split('\n')
cands = [c.replace(']]','').strip().split(' ||| [[') for c in cands]
cands


# In[635]:


#check if they're in the same county
for pair in cands:
    cand1 = pair[0]
    cand2 = pair[1]
    a = df[df.candidate == cand1]
    b = df[df.candidate == cand2]
    if np.any(a.county_name.unique() == b.county_name.unique()): 
        print(cand1,'--->',a.county_name.unique(), a.office.unique(), a.writein.unique())
        print(cand2,'--->',b.county_name.unique(), b.office.unique(),b.writein.unique(),'\n')


# In[636]:


df.loc[df.candidate=='JEROME "J D " KUSTER','candidate'] = 'JEROME "J D" KUSTER'
df.loc[df.candidate=='KATHY SMITH "KEVIN"','candidate'] = 'KATHY "KEVIN" SMITH'
df[df.candidate.str.contains(' "')].candidate.unique()


# In[637]:


df.writein.unique()


# 1. Replace KATHY SMITH "KEVIN" --> KATHY "KEVIN" SMITH , and "'J'" --> "J"
# 2. All these courts should be made "STATE" dataverse
# COURT OF APPEALS JUDGE: ['LOCAL']
# DISTRICT ASSOCIATE JUDGE: ['LOCAL']
# DISTRICT JUDGE: ['LOCAL']
# 3. Standardize offices like [CO ATTORNEY, CO ATTY] to "COUTNY ATTORNEY". And do a similar change for other "CO ____" office.
# 4. The magnitude values are fully available in the raw data and not reflected in our final dataset. Utilize the table of contents in the county files to map non-1 magnitudes to their office names.
# 5. Party_detailed "" should map to "" for party_simplified. It currently maps to "OTHER"
# 

# In[638]:


df.loc[df.candidate=="'J'",'candidate'] = "J"


# In[639]:


df.loc[df.office.str.contains('JUDGE'),'dataverse'] = 'STATE'


# In[640]:


l = list()
def fix_office(x):
    if 'EXTENSION' in x or 'EXT ' in x or 'AG COUNCIL' in x: return 'COUNTY AGRICULTURAL EXTENSION COUNCIL '
    elif 'SUPERVISORS' in x: return 'COUNTY BOARD OF SUPERVISORS'
    elif 'SOIL' in x: return 'COUNTY SOIL AND WATER CONSERVATION DISTRICT COMMISSIONER'
    elif 'ATTY' in x: return 'COUNTY ATTORNEY'
    elif ' REC' in x: 
        return 'COUNTY RECORDER'
    elif 'HOSPITAL' in x: return 'COUNTY PUBLIC HOSPITAL TRUSTEE'
    elif 'COUNTY TREAS' in x: return 'COUNTY TREASURER'
    if ' TOWNSHIP' in x: x = x.replace(' TOWNSHIP','')
    return x.strip()

df['office'] = df.office.apply(fix_office)
df['office'] = df.office.apply(lambda x: x.replace('CO ','COUNTY ') if 'CO ' in x else x)
df[df.office.str.contains('COUNTY')].office.unique()


# In[ ]:


### get magnitude
mags_lst = []
for county in [i for i in os.listdir('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/IA/raw-usable') if i != '.DS_Store']:
    mags = pd.DataFrame(columns = ['county_name','office','magnitude'])
    toc = pd.read_csv('/Users/declanchin/Desktop/MEDSL/2018-precincts/precinct/IA/raw-usable/' + county+ "/Table of Contents.csv",
                     skiprows = [0,1,2,3])
    mags['office'] = toc['Registered Voters'].str.upper()
    mags['county_name'] = county.upper().strip()
    mags['magnitude'] = [int(re.findall('\d+',i.split(' ')[-1])[0]) for i in mags['office']]
    mags['office'] = [i.split('(')[0].strip() for i in mags['office']]
    mags_lst = mags_lst + [mags]
magnitude=pd.concat(mags_lst)
# else magnitude can be one, 705 unique non1
magnitude=magnitude[magnitude['magnitude']>1]

# applied these office fixes
df['office'] = df['office'].str.strip()
print(df[df['office'].str.contains('AGRICULTURAL')]['office'].unique())
print(magnitude[magnitude['office'].str.contains('AGRICULTURAL')]['office'].unique())

# merge magnitude
df = df.merge(magnitude, on = ['county_name','office'], how = 'left')
df['magnitude'] = df['magnitude'].fillna(1)


# Party_detailed "" should map to "" for party_simplified.
df.loc[df.party_detailed=='', 'party_simplified'] = ""

# fix statewide district
df.loc[df['office']=='COURT OF APPEALS JUDGE','district'] = "STATEWIDE"

# In[581]:


df = df[["precinct", "office", "party_detailed", "party_simplified", "mode", "votes", "candidate", 
                     "district","dataverse","stage", "special", "writein","date", "year","county_name","county_fips",
                     "jurisdiction_name", "jurisdiction_fips","state", "state_po","state_fips", "state_cen", 
                   "state_ic", "readme_check",'magnitude']].copy()


# In[ ]:




#UGLY fixes to duplicates. Some offices are just the same with no seat # distinction, others need mag/special info
df.loc[[236406,236407,236408,236409],'office'] = 'Lakewood Recreational Lake Trustee'.upper()
df.loc[[236406,236407,236408,236409],'district'] = '002'
df.loc[[236154,236155,236156,236157],'office'] = 'Lakewood Recreational Lake Trustee'.upper()
df.loc[[236154,236155,236156,236157],'district'] = '001'

df.loc[((df['office'].isin(['TOWNSHIP TRUSTEE - FRANKLIN'])) & (df['county_name']=='LEE')),'district'] = ['001']*4 + ['002']*2
df.loc[((df['office'].isin(['TOWNSHIP TRUSTEE - HARRISON'])) &(df['county_name']=='LEE')),'district'] = ['001']*4 + ['002']*4
df.loc[((df['office'].isin(['TOWNSHIP TRUSTEE - JACKSON'])) &(df['county_name']=='LEE')),'district'] = ['001']*4 + ['002']*2
df.loc[((df['office'].isin(['TOWNSHIP TRUSTEE - MONTROSE'])) &
      (df['county_name']=='LEE')),'district'] = ['001']*2 + ['002']*2 + ['003']*2

df.loc[((df['office'].isin(['TOWNSHIP TRUSTEE - VERNON'])) &
   (df['county_name']=='VAN BUREN')),'district'] = ['001']*6 + ['002']*4

df.loc[(df['office']=='TOWNSHIP TRUSTEE - DEERFIELD') &
   (df['county_name']=='CHICKASAW'),'special'] = ['FALSE']*6 + ['TRUE']*4

df.loc[(df['office']=='TOWNSHIP TRUSTEE - STAPLETON') &
   (df['county_name']=='CHICKASAW'),'special'] = ['FALSE']*2 + ['TRUE']*4

df.loc[(df['office']=='TOWNSHIP TRUSTEE - GARNAVILLO') &
   (df['county_name']=='CLAYTON'),'special'] = ['FALSE']*6 + ['TRUE']*2

df.loc[(df['office']=='TOWNSHIP TRUSTEE - HIGHLAND') &
   (df['county_name']=='CLAYTON'),'special'] = ['FALSE']*4 + ['TRUE']*2
df = df.drop([43928,43929])

df.loc[np.arange(154152,154290),'magnitude'] = 2

df.loc[np.arange(108512,108854),'magnitude'] = 2

df = df[~((df['candidate']=='WRITEIN')&(df['votes']==0))].copy()

df = df.replace('  ', ' ', regex = True) 
df = df.fillna("")
df = df.applymap(lambda x: x.strip() if type(x) == str else x)


# In[ ]:





# In[585]:


#df = df.replace([True,False], ['TRUE','FALSE'])


# In[ ]:





# In[587]:


df.to_csv("2018-ia-precinct-general-updated.csv", encoding='utf-8',quoting=csv.QUOTE_NONNUMERIC, index=False)


# In[ ]:





# In[589]:


#get_ipython().system('jupyter nbconvert --to script ia_21_updates.ipynb')


# In[ ]:





# In[ ]:




