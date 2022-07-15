

import pandas as pd
import csv


official_dtypes = {'district':str,'precinct':str,'office':str, 'party_detailed':str,
                   'party_simplified':str,'mode':str,'votes':int, 'county_name':str, 'county_fips':str,
                   'jurisdiction_name':str,'jurisdiction_fips':str, 'candidate':str, 'district':str,
                   'dataverse':str,'year':int, 'stage':str, 'state':str, 'special':str, 'writein':str,
                   'state_po':str, 'state_fips':str, 'state_cen':str, 'state_ic':str, 'date':str,
                   'readme_check':str,'magnitude':int}

df = pd.read_csv('raw/ELECTIONVOTINGDISTRICT-152.csv',index_col=False,header=2) #,dtype=official_dtypes)
df = df.fillna("")

prez = df[:12760].reset_index()


stats1 = df[12760:13516].reset_index()
stats1.columns = stats1.iloc[0] 
stats1 = stats1.iloc[1:,1:]

stats2 = df[13516:14272].reset_index()
stats2.columns = stats2.iloc[0]
stats2 = stats2.iloc[1:,1:]

#NOTE: WE ARE NOT CLEANING/INCLUDING QUESTIONS
'''
qs = df.iloc[14272:].reset_index()
qs.columns = qs.iloc[0] #stats.rename(columns=)
qs = qs.iloc[1:,1:]

qs = qs.replace('-','')
'''

#clean prez first
def get_district(x):
    if 'Congress' in x: return x[-2:].zfill(3)
    elif 'State Represen' in x: return x[-3:].strip().zfill(3)
    elif 'State Senator' in x: return x[-2:].zfill(3)
    elif 'Presidential' in x: return 'STATEWIDE'
    elif 'Town Meeting' in x: return x.split()[-1]
    else: return ''

def get_office(x):
    if 'Vacancy' in x or 'Full Term' in x: x = x.replace(' To Fill Vacancy ','').replace(' Full Term','')
    if 'Congress' in x: return 'US HOUSE'
    elif 'State Represen' in x: return 'STATE HOUSE'
    elif 'State Senator' in x: return 'STATE SENATE'
    elif 'Presidential' in x: return 'US PRESIDENT'
    elif 'Probate' in x: return 'JUDGE OF PROBATE'
    elif 'Town Meeting' in x: return 'TOWN MEETING MEMBERS'
    return x.strip().upper()
    


# In[14]:


prez['district'] = prez['OfficeName'].apply(get_district)
prez['district'] = prez['district'].replace({'One':'001','Two':'002','Three':'003','Four':'004','Five':'005','Six':'006'})
prez['office'] = prez['OfficeName'].apply(get_office).apply(lambda x: x.strip())
#prez['office'] = prez['OfficeName'].apply(get_district)


# In[15]:

# In[17]:


prez['precinct'] = prez['Polling_Place_Name'].str.upper()

prez['writein'] = 'FALSE'
prez['special'] = 'FALSE'
prez.loc[prez.OfficeName.str.contains('Vacancy'),'special'] = 'TRUE'
prez.loc[prez.PartyName=='Write In','writein'] = 'TRUE'

prez['party_detailed'] = prez['PartyName'].str.replace(' Party', '').str.upper().replace({'DEMOCRATIC' : 'DEMOCRAT',
                                       'WRITE IN' : '','NON PARTISAN':'NONPARTISAN', 'PETITIONING CANDIDATE':''})
prez['party_simplified'] = prez.party_detailed.replace({'EPIC': 'OTHER', 'GREEN' : 'OTHER',
                                       'SOCIALIST RESURGENCE' : 'OTHER', 'WORKING FAMILIES' : 'OTHER',
                                       'RECLAIM': 'OTHER', 'PETITIONING CANDIDATE':'OTHER','VOICES FOR ENFIELD':'OTHER',
                                                        'THE BOTTOM LINE':'OTHER', 'OPEN':'OTHER',
                                       'INDEPENDENT': 'OTHER'})



# In[20]:


prez['candidate'] = prez['CandidateName'].str.replace('Machine/Polling Place/EDRAbsenteeTotal','')
prez['candidate'] = prez['candidate'].str.replace('Machine/Polling Place/EDRAbsenteeTotal"','')
prez['candidate'] = prez.candidate.apply(lambda x: x.replace('.','').replace(',','').upper())





def fix_cand(x):
    if '"' in x:
        nickname = x.split()[1][:-1]
        last = x.split()[-1].strip('"')
        return x.split()[0]+ ' "'+nickname+'" '+last
    x = x.replace('  ',' ')
    return x
prez['candidate'] = prez['candidate'].apply(fix_cand)
prez['candidate'] = prez['candidate'].replace({'BIDEN AND HARRIS':'JOSEPH R BIDEN','TRUMP AND PENCE':'DONALD J TRUMP',
                                               'JORGENSEN AND COHEN':'JO JORGENSEN','HAWKINS AND WALKER':'HOWIE HAWKINS',
                                               'WEST AND TIDBALL':'KANYE WEST',
                                               'CHARLES AND WALLACE': 'MARK CHARLES',
                                               'CARROLL AND PATEL':'BRIAN CARROLL',
                                               'SIMMONS AND ROZE':'JADE SIMMONS',
                                               'DE LA FUENTA AND RICHARDSON':'ROQUE "ROCKY" DE LA FUENTE',
                                               'WEINSTEIN AND WEINSTEIN': 'KARYNN WEINSTEIN',
                                               'WELLS AND WELLS':'KASEY WELLS',
                                               'SIMMONS AND DOW': 'MARY RUTH CARO SIMMONS',
                                               'HOWARD AND HOWARD':'SHAWN HOWARD'})


# In[23]:

# In[25]:


prez['dataverse'] = prez.office.replace({'US HOUSE': 'HOUSE', 'US PRESIDENT': 'PRESIDENT',
                                     'STATE HOUSE': 'STATE', 'STATE SENATE':'STATE',
                                     'JUDGE OF PROBATE': 'STATE','BOARD OF EDUCATION':'LOCAL',
                                    'MAYOR':'LOCAL','TOWN MEETING MEMBERS':'LOCAL','REGISTRAR OF VOTERS':'LOCAL'})


# In[26]:


cols_keep = ['precinct', 'TownName',
# 'OfficeName',
# 'CandidateName',
# 'PartyName',
# 'Polling_Place_Name',
 'district',  'office',
 'writein',
 'party_detailed',
 'party_simplified',
 'candidate','dataverse']
modes = ['Machine_Count','Absentee_Count']


# In[27]:


df1 = prez.melt(id_vars = cols_keep, value_vars=modes, var_name='mode', value_name='votes')
#df1['mode'] = df1['mode']

print(len(df1))
df1 = df1[df1['mode']!='Final_Count'].copy()
len(df1)


# ## Clean Stats

# In[29]:


stats1.head()
print(len(stats1))
print(len(stats1.drop_duplicates()))


# In[30]:


#stats[stats.duplicated(subset=['Polling_Place_Name','TownName'],keep=False)].sort_values(['TownName','Polling_Place_Name'])
stats1 = stats1.drop_duplicates(subset=['TownName', 'Polling_Place_Name'],keep='first')
stats2 = stats2.drop_duplicates(subset=['TownName', 'Polling_Place_Name'],keep='first')


# In[31]:

stats1['precinct'] = stats1['Polling_Place_Name']
stats2['precinct'] = stats2['Polling_Place_Name']
stats1.drop(columns=['Polling_Place_Name', '', '', '', '', '', '', ''],inplace=True)
stats2.drop(columns=['Polling_Place_Name', '', '', '', '', '', '', ''],inplace=True)

s1 = stats1.melt(id_vars = ['TownName','precinct'], value_vars=['No.of Names on Registry','No. Checked as Having Voted',
                                                             'No.of Overseas Voters'], 
               var_name='office', value_name='votes')


s2 = stats2.melt(id_vars = ['TownName','precinct'], value_vars=['Machine/Polling Place Total','Absentee Total',
                                                             'Election Day Registration (EDR)'], 
               var_name='office', value_name='votes')


# In[33]:


s = s1.append(s2)


# In[34]:


s


# In[35]:


s['mode'] = 'TOTAL'
s.loc[s['office'] == 'Machine/Polling Place Total','mode'] = 'ELECTION DAY'
s.loc[s['office'] == 'Absentee Total','mode'] = 'ABSENTEE'
s.loc[s['office'] == 'Machine/Polling Place Total','mode'] = 'ELECTION DAY'


# In[36]:


s['office'] = s['office'].replace({'No.of Names on Registry':'REGISTERED VOTERS','No. Checked as Having Voted':'TURNOUT',
                                                             'No.of Overseas Voters':'OVERSEAS VOTERS',
                                   'Machine/Polling Place Total':'BALLOTS CAST','Absentee Total': 'BALLOTS CAST',
                                                             'Election Day Registration (EDR)':'ELECTION DAY REGISTRATION'})
cols = ['party_detailed','party_simplified','candidate','district','dataverse','special']
for col in cols:
    s[col] = ""


# In[37]:


s.head()


# In[ ]:





# In[38]:


s['writein'] = 'FALSE'
s = s[['precinct', 'TownName', 'district', 'office', 'writein',
       'party_detailed', 'party_simplified', 'candidate', 'dataverse', 'mode',
       'votes','special']].copy()
#df.columns


# In[ ]:





# In[39]:


df = df1.append(s)


# ## Clean Questions DF

# In[40]:

'''
def add_yes_no(question, yes, no):
    if yes == "": return 'NO'
    else: return 'YES'

qs['candidate'] = qs.apply(lambda x: add_yes_no(x['Question'],x['Yes Votes'], x['No Votes']),axis=1)


# In[41]:


qs['votes'] = qs['Yes Votes'] + qs['No Votes']


# In[42]:


q = qs[qs.Election == 'NOVEMBER 03, 2020 STATE ELECTION  ']
q.head()


# In[43]:


q['precinct'] = 'JURISDICTION FLOATING'
q['TownName'] = q.Town
q['district'] = ''
q['office'] = q.Question
q['writein'] = 'FALSE'
q['party_detailed'] = ''
q['party_simplified'] = ''
q['dataverse'] = 'LOCAL'
q['mode'] = 'TOTAL'
q['special'] = 'FALSE'


# In[44]:


def clean_q_office(x):
    x = x[x.upper().find('SHALL'):].strip('"').upper()   
    if 'YES_____ NO' in x: x = x[:x.find('  ')]
    elif 'YES OR NO?:' in x: x = x[:x.find(' YES')]
    
    return x.strip()

q['office'] = q['office'].apply(clean_q_office)


# In[45]:


q = q[['precinct', 'TownName', 'district', 'office', 'writein',
       'party_detailed', 'party_simplified', 'candidate', 'dataverse', 'mode',
       'votes', 'special']]


# In[46]:


df = df.append(q)
'''

# ## Final Editing

# In[47]:


df['mode'] = df['mode'].replace({'Machine_Count':'ELECTION DAY','Absentee_Count':'ABSENTEE','Final_Count':'TOTAL'})
df['jurisdiction_name'] = df['TownName'].str.upper()
df['state'] = 'Connecticut'
df['year'] = '2020'
df['stage'] = 'GEN'
df['state_po'] = 'CT'
df['state_fips'] = '9'
df['state_cen'] = '16'
df['state_ic'] = '1'
df['date'] = '2020-11-03'
df['special'] = 'FALSE'

df['mode'].unique()


# In[48]:




jurisFips = pd.read_csv("../../help-files/jurisdiction-fips-codes.csv")
df = pd.merge(df, jurisFips, on = ['state','jurisdiction_name'],how = 'left')

#use old data to make a crosswalk for jurisdiction_name to county name and fips 
old = pd.read_csv('../../../2018-precincts/precinct/CT/2018-ct-precinct-general-updated.csv')
c = old[['jurisdiction_name','county_name','county_fips']].drop_duplicates()
df = pd.merge(df, c, on = ['jurisdiction_name'],how = 'left')


df['county_fips'] = df.county_fips.apply(lambda x: str(x).replace('.0','').zfill(5))
df['jurisdiction_fips'] = df.jurisdiction_fips.apply(lambda x: str(x).replace('.0','').zfill(10))
df.state = df.state.str.upper()


# In[49]:


df['readme_check'] = 'FALSE'
df['magnitude'] = 1
df.loc[df.dataverse=='','magnitude'] = 0


# In[50]:


df[df.office=='TOWN MEETING MEMBERS'].jurisdiction_name.unique() #df.office.unique()


# In[51]:


df['mode'].unique()


# In[52]:


#local magnitude info from https://patch.com/connecticut/darien/darien-election-results-vote-totals-every-race


# In[53]:


df.loc[(df.office=='TOWN MEETING MEMBERS')&(df.district=='001'),'magnitude'] = 7
df.loc[(df.office=='TOWN MEETING MEMBERS')&(df.district=='002'),'magnitude'] = 8
df.loc[(df.office=='TOWN MEETING MEMBERS')&(df.district=='003'),'magnitude'] = 7
df.loc[(df.office=='TOWN MEETING MEMBERS')&(df.district=='004'),'magnitude'] = 7
df.loc[(df.office=='TOWN MEETING MEMBERS')&(df.district=='005'),'magnitude'] = 5
df.loc[(df.office=='TOWN MEETING MEMBERS')&(df.district=='006'),'magnitude'] = 5

df[df.office=='TOWN MEETING MEMBERS'][['office','district','magnitude']].drop_duplicates()


# In[54]:


df[df.office=='BOARD OF EDUCATION'][['office','jurisdiction_name','county_name','district','magnitude']] #.jurisdiction_name.unique()


# In[55]:


df.loc[(df.office=='BOARD OF EDUCATION')&(df.jurisdiction_name=='DARIEN'),'magnitude'] = 2



df['votes'] = df['votes'].replace({'':0})
df['votes'] = df['votes'].astype(int)


# In[62]:


df['candidate'] = df.candidate.replace({'JOHN (JACK) F HENNESSY':'JOHN F "JACK" HENNESSY'})
df['precinct'] = df['precinct'].str.upper()

# In[63]:


df = df[['precinct', 'district', 'office', 'writein',
       'party_detailed', 'party_simplified', 'candidate', 'dataverse', 'mode',
       'votes', 'special', 'jurisdiction_name', 'state', 'year', 'stage',
       'state_po', 'state_fips', 'state_cen', 'state_ic', 'date',
       'jurisdiction_fips', 'county_name', 'county_fips', 'readme_check',
       'magnitude']]

counties = ['FAIRFIELD','NEW HAVEN','TOLLAND','WINDHAM']
df.loc[df['county_name'].isin(counties),'readme_check'] = 'TRUE'

df.to_csv('2020-ct-precinct-general.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

