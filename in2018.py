###############################################################################
# Clean the monstrous precinct data from Indiana's 2018 elections
#
# written by sbaltz based on code by cstewartiii at mit
#   october and november 2022
###############################################################################
import pandas as pd
import numpy as np
import copy
import os


###############################################################################
# Global variables
###############################################################################
#Set the following switch separately in each stage to print in just that stage
STAGEWISE_VERBOSE = False

COUNTY_FIPS_FNAME = '../../help-files/county-fips-codes.csv'

CANON_COUNTIES = set(i.upper() for i in \
        ["Adams", "Allen", "Bartholomew", "Benton", "Blackford", "Boone", 
         "Brown", "Carroll", "Cass", "Clark", "Clay", "Clinton", "Crawford", 
         "Daviess", "Dearborn", "Decatur", "DeKalb", "Delaware", "Dubois", 
         "Elkhart", "Fayette", "Floyd", "Fountain", "Franklin", "Fulton", 
         "Gibson", "Grant", "Greene", "Hamilton", "Hancock", "Harrison", 
         "Hendricks", "Henry", "Howard", "Huntington", "Jackson", "Jasper", 
         "Jay", "Jefferson", "Jennings", "Johnson", "Knox", "Kosciusko", 
         "LaGrange", "Lake", "LaPorte", "Lawrence", "Madison", "Marion", 
         "Marshall", "Martin", "Miami", "Monroe", "Montgomery", "Morgan", 
         "Newton", "Noble", "Ohio", "Orange", "Owen", "Parke", "Perry", "Pike",
         "Porter", "Posey", "Pulaski", "Putnam", "Randolph", "Ripley", "Rush", 
         "St Joseph", "Scott", "Shelby", "Spencer", "Starke", "Steuben", 
         "Sullivan", "Switzerland", "Tippecanoe", "Tipton", "Union", 
         "Vanderburgh", "Vermillion", "Vigo", "Wabash", "Warren", "Warrick", 
         "Washington", "Wayne", "Wells", "White", "Whitley"])


###############################################################################
# Quality of life functions
###############################################################################
def QuietPrint(theString):
    """Defines verbosity-aware printing""" 
    global STAGEWISE_VERBOSE
    print(theString) if STAGEWISE_VERBOSE else None

def CountyToFile(county):
    """Turns a standardized county name into a file name"""
    fname = county.lower()
    fname = fname.replace(' ','_')
    return(fname)

def DropExtremeSpaces(df, varname):
    """Remove a space if it is the first or last character of a series val"""
    df.loc[df[varname].str.endswith(' '), varname] = df[varname].str[:-1]
    df.loc[df[varname].str.startswith(' '), varname] = df[varname].str[1:]
    return(df)        


###############################################################################
# Data cleaning functions
###############################################################################
def CleanOffice(df):
    """Standardize the office column of a dataframe"""
    #Uppercase and clean punctuation
    df.office = df.office.str.upper()
    df.office.replace({'\.': '',
                       'U S': 'US',
                       '\-': ''}, regex=True, inplace=True)
    df.office.replace({'  ': ' '}, regex=True, inplace=True)
    #Custom standardization for the office names that appear in these raw data
    df.office.replace({"BALLOTS CAST ": "BALLOTS CAST",
                       "WRITE IN": "WRITE-IN",
                       "STATE SENATE ": "STATE SENATE",
                       "STATE SENATOR": "STATE SENATE",
                       "STATE REPRESENTATIVE": "STATE HOUSE"}, inplace=True)
    return(df)

def CleanCounty(df):
    """Standardize the county column of a dataframe"""
    #Uppercase and clean punctuation
    df.county = df.county.str.upper()
    df.county.replace({'\.': ''}, regex=True, inplace=True)
    return(df)

def CleanCandidate(df):
    """Standardize the county column of a dataframe"""
    #Uppercase and clean punctuation
    df.candidate = df.candidate.str.upper()
    df.candidate.replace({'\.': '',
                          '\,': ''
                      }, regex=True, inplace=True)
    df.loc[df.candidate.isna(), "candidate"] = ""
    df = DropExtremeSpaces(df, 'candidate')
    return(df)

def PrepData(df):
    """Apply the initial data cleaning steps"""
    #Clean base columns
    df = CleanOffice(df)
    df = CleanCounty(df)
    df = CleanCandidate(df)
    #Drop index column if it has been included
    if 'id' in df.columns:
        df = df.drop('id', axis=1)
    return(df)

def MeltModesIfNeeded(df):
    """Melt modes into a long-format dataframe"""
    colnames = set(df.columns)
    baseCols = {'candidate', 'office', 'district', 'party', 'county', \
                'precinct', 'votes'}
    #List all of the ways that a county can depart from the base case columns
    # (rather than listing all subsets, so we don't waste time)
    value_var_sets = [
                {'election_day', 'absentee', 'provisional'},
                {'election_day', 'absentee', 'early_voting'},
                {'election_day', 'absentee', 'early_voting', 'provisional'},
                {'election_day', 'early_voting'},
                {'election_day', 'absentee'}
                ]
    for valueVars in value_var_sets:
        tryCols = baseCols.union(valueVars)
        if colnames == tryCols:
            df = pd.melt(df,
                         value_vars=valueVars,
                         id_vars=[_ for _ in colnames if _ not in valueVars]
                        )
            df.drop('votes', axis=1, inplace=True)
            df = df.rename(columns = {'variable': 'mode',
                                      'value': 'votes' 
                                       })
            break
    return(df)


###############################################################################
# Data loading, joining, and basic quality of life setup
###############################################################################
STAGEWISE_VERBOSE = False
#Initialize a statewide dataframe
ind = pd.DataFrame({'county':             pd.Series(dtype='str'),
                    'precinct':           pd.Series(dtype='str'),
                    'office':             pd.Series(dtype='str'),
                    'district':           pd.Series(dtype='str'),
                    'party':              pd.Series(dtype='str'),
                    'candidate':          pd.Series(dtype='str'),
                    'votes':              pd.Series(dtype='str'),
                    'mode':               pd.Series(dtype='str')
                    })
CANON_ORDER = list(ind.columns)
files = os.listdir('raw')

#Load in, clean, and merge every file
for fname in files:
    ct = pd.read_csv('raw/'+fname, encoding='utf-8')
    #If necessary, extract and apply the county name
    if 'county' not in ct.columns:
        sLoc = fname.find('general__')+len('general__')
        eLoc = fname.find('__precinct')
        ctName = fname[sLoc:eLoc]
        ct['county'] = ctName
    ct = PrepData(ct)
    ct = MeltModesIfNeeded(ct)
    if 'mode' not in ct.columns:
        ct['mode'] = ''
    if set(CANON_ORDER) == set(ct.columns):
        ct = ct[CANON_ORDER]
        ind = pd.concat([ind, ct],
                        join = 'outer',
                        axis = 0,
                        sort = False)
        QuietPrint(f"*Joined {fname}")
    else:
        QuietPrint(f"*Could not join {fname} with columns {ct.columns}")

#Some county names are misspelled (!!!)
ind.loc[ind.county == 'STUEBEN', 'county'] = 'STEUBEN'
ind.loc[ind.county == 'VERMILION', 'county'] = 'VERMILLION'
ind.loc[ind.county == 'WAHINGTON', 'county'] = 'WASHINGTON'

QuietPrint(f"\nLIST OF COUNTIES:\n*{np.sort(ind.county.unique())}")


###############################################################################
# Variable types, and nonsense row elimination
###############################################################################
STAGEWISE_VERBOSE = False
#Drop or overwrite nonsensical vote values
# Note: if no votes are recorded, the dataset has nothing to say about that row
ind = ind.loc[~ind.votes.isna()]
ind.loc[ind.votes == '10 \'', 'votes'] = '10'
ind.loc[ind.votes == 'o', 'votes'] = '0'
ind.loc[ind.votes == '/46', 'votes'] = '46'
ind.votes.replace({',': ''}, regex=True, inplace=True)

#Set the variable types. We can only do so now rather than on reading because
# we needed to first correct values (like the broken vote totals) that cannot 
# be read as the appropriate type
data_types = {'county': str,
              'precinct': str,
              'office': str,
              'district': str,
              'party': str,
              'candidate': str,
              'votes': int,
              'mode': str
             }
ind = ind.astype(data_types)

#Districts need to go from floats to ints
ind.district = ind.district.str.split('.').str[0]
ind.loc[ind.district == 'nan', 'district'] = ''


###############################################################################
# District
###############################################################################
STAGEWISE_VERBOSE = False
#Sorry Pandas
ind.district = np.where(ind.district != '', ind.district.str.zfill(3), '')
QuietPrint(f"\nDISTRICT VALUES:\n*{ind.district.unique()}")


###############################################################################
# Party
###############################################################################
STAGEWISE_VERBOSE = False
#Party detailed
ind["party_detailed"] = ind.party.str.upper()
ind.party_detailed.replace({'\(': '',
                            '\)': '',
                            '\.': '',
                            ' ': ''
                           }, regex=True, inplace=True)
ind.replace({'party_detailed': {'R': 'REPUBLICAN',
                                'REP': 'REPUBLICAN',
                                'REPUBLICANPARTY': 'REPUBLICAN',
                                'D': 'DEMOCRAT',
                                'DEM': 'DEMOCRAT',
                                'DEMOCRATICPARTY': 'DEMOCRAT',
                                'L': 'LIBERTARIAN',
                                'LIB': 'LIBERTARIAN',
                                'LIBERTARIANPARTY': 'LIBERTARIAN',
                                'IND': 'INDEPENDENT',
                                'WRITE-IN': '',
                                'NAN': ''
                           }}, inplace=True)

#What do the remaining party labels mean? We can print a few candidates with
# each one and check their party label to infer the meaning of the label
QuietPrint(f"\nALL PARTY LABELS: \n*{ind.party_detailed.unique()}\n")
for label in ['I', 'LBT', 'W', '']:
    QuietPrint(f"*{label} candidates:\n"+
           f"**{ind.candidate[ind.party_detailed == label].unique()}\n")
#Replace accordingly
ind.replace({'party_detailed': {'I': 'INDEPENDENT',
                                'LBT': 'LIBERTARIAN',
                                "W": ''
                               }}, inplace=True)
QuietPrint(f"\nALL PARTY LABELS: \n*{ind.party_detailed.unique()}\n")

#All provided party labels belong to the party simplified canon, except one,
# which we will fix at the end
ind["party_simplified"] = ind.party_detailed

#Remove the original party variable
ind = ind.drop('party', axis=1)


###############################################################################
# Write-in
###############################################################################
STAGEWISE_VERBOSE = False
ind['writein'] = 'FALSE'
#We will fill in true values when we clean the variables that store this info


###############################################################################
# Office
###############################################################################
STAGEWISE_VERBOSE = False
QuietPrint(f"\nALL PRE-FIX OFFICES: \n*{np.sort(ind.office.unique())}\n")

#Correct typos/formatting irregularities
ind.office.replace({'COUNTY COUNCIL DISTRICT I':'COUNTY COUNCIL DISTRICT 1',
    'COURT OF APPEALS DIST 2ALTICE': 'COURT OF APPEALS ALTICE DIST2'
                   }, inplace=True)

#We do not typically remove all geographic information from local offices, but
# when it is a literal district number it probably is best to just sort that
# into the district column
offices_with_dists = {'COUNTY COMMISSIONER DIST ': [1],
                      'COUNTY COMMISSIONER DISTRICT ': [2,3],
                      'COUNTY COMMISSIONER #': [2],
                      'APPEALS COURT JUDGE DIST ': [1,2,3,4],
                      'COUNTY COUNCIL #': [1,2,3,4],
                      'COUNTY COUNCIL DISTRICT ': [1,2,3,4],
                      'COUNTY COUNCIL DST ': [1,2,3,4],
                      'CRT OF APPEALS JUDICIAL RETENTION D': [2],
                      'COURT OF APPEALS ALTICE DIST': [2],
                      'GREENWOOD SCHOOL DIST #': [2],
                      'KOUTS TOWN COUNCIL DST ': [2,4],
                      'NEW PRAIRIE UNITED SB DIST ': [2],
                      'TOWN OF OGDEN DUNES DIST ': [5],
                      'SCHOOL BOARD DISTRICT ': [4]
                      }
office_replacements = {'COUNTY COMMISSIONER DIST ': 'COUNTY COMMISSIONER',
    'COUNTY COMMISSIONER DISTRICT ': 'COUNTY COMMISSIONER',
    'APPEALS COURT JUDGE DIST ': 'APPEALS COURT JUDGE',
    'COUNTY COUNCIL #': 'COUNTY COUNCIL',
    'COUNTY COUNCIL DISTRICT ': 'COUNTY COUNCIL',
    'COUNTY COUNCIL DST ': 'COUNTY COUNCIL',
    'CRT OF APPEALS JUDICIAL RETENTION D': 'CRT OF APPEALS JUDICIAL RETENTION',
    'COURT OF APPEALS ALTICE DIST': 'COURT OF APPEALS ALTICE',
    'GREENWOOD SCHOOL DIST #': 'GREENWOOD SCHOOL',
    'KOUTS TOWN COUNCIL DST ': 'KOUTS TOWN COUNCIL',
    'NEW PRAIRIE UNITED SB DIST ': 'NEW PRAIRIE UNITED SB',
    'TOWN OF OGDEN DUNES DIST ': 'TOWN OF OGDEN DUNES',
    'COUNTY COMMISSIONER #': 'COUNTY COMMISSIONER',
    'SCHOOL BOARD DISTRICT ': 'SCHOOL BOARD',
                      }
for officeBase in offices_with_dists.keys():
    for num in offices_with_dists[officeBase]:
        officeName = officeBase + str(num)
        distVal = str(num).zfill(3)
        #Add the district to the district column in the relevant rows
        ind.loc[ind.office == officeName, 'district'] = distVal
        #Overwrite the office name without the district
        ind.office.replace({
            officeName: office_replacements[officeBase],
        }, inplace=True)
#Clean up all remaining typos and non-standard values
ind.office.replace({'STATE REP DIST': 'STATE HOUSE',
                    'USHOUSE': 'US HOUSE',
                    'UNITED STATES HOUSE': 'US HOUSE',
                    'UNITED STATES SENATOR': 'US SENATE',
                    'SECT OF STATE': 'SECRETARY OF STATE'}, inplace=True)
#Treasurer is non-standardized but it's the same office
QuietPrint(ind.candidate[ind.office == "STATE TREASURER"].unique())
QuietPrint(ind.candidate[ind.office == "TREASURER"].unique())
QuietPrint(ind.candidate[ind.office == "TREASURER OF STATE"].unique())
ind.office.replace({'TREASURER OF STATE': 'STATE TREASURER',
                    'TREASURER': 'STATE TREASURER',
                    'AUDITOR OF STATE': 'STATE AUDITOR'
                   }, inplace=True)

#Handle meta-information.

#What does it mean for "office" to have the value WRITE-IN?
# It would seem to be storing aggregate information about the number of
# write-in votes cast total by mode in the precinct, for some reason in the
# office variable rather than the candidate variable. We do not need to keep
# that information in the office variable because it is now in the writein var
ind.loc[ind.office == 'WRITE-IN', 'writein'] = 'TRUE'
ind.loc[ind.office == 'WRITE-IN', 'office'] = ''

ind.office.replace({'BALLOTS CAST TOTAL': 'BALLOTS CAST'
                   },inplace=True)

#Office should be STRAIGHT TICKET not STRAIGHT PARTY
ind.office.replace({'STRAIGHT PARTY': 'STRAIGHT TICKET'},inplace=True)

#Drop any NaN artifacts
ind.office.replace({'nan': ''},inplace=True)

#Standardize some state-level offices
# AUDITOR == AUDITOR OF STATE
QuietPrint(f"\n AUDITOR and AUDITOR OF STATE cands match (up to nonsense):\n*"+
           f"**{ind.candidate[ind.office == 'AUDITOR'].unique()}\n"+
           f"**{ind.candidate[ind.office == 'STATE AUDITOR'].unique()}\n")
ind.office.replace({'AUDITOR': 'STATE AUDITOR'
                   },inplace=True)
ind.office.replace({'COUNTY RECORDER ': 'COUNTY RECORDER'
                   },inplace=True)

QuietPrint(f"\nALL POST-FIX OFFICES: \n*{np.sort(ind.office.unique())}\n")


###############################################################################
# Candidate
###############################################################################
STAGEWISE_VERBOSE = False
QuietPrint(np.sort(ind.candidate.unique()))

#Clean anything parenthetical that is not a nickname. First, drop OCR artifacts 
# from candidates who were write-ins represented with a (W) in the cand name
ind.candidate.replace({
    ' \(VII\)': '',
    ' \(VS1\)': '',
    ' \(UV\)': '',
    ' \(1N\)': '',
    ' \(V\)\/\)': '',
    '\(I\) ': '',
    ' \(N\)': '',
    ' \(VV\)': '',
    ' \(V': '',
    ' \(W\)': '',
    ' \{V': '',
    ' ON\)': ''
    },regex=True, inplace=True)
#Standardize the candidates in question
ind.candidate.replace({
                    'GEORGE WM WOLFE': 'GEORGE WILLIAM WOLFE',
                    'JAMES L JOHNSON': 'JAMES L JOHNSON JR'
    },inplace = True)
#Now we can log that these candidates were write-ins
ind.loc[ind.candidate.isin(['GEORGE WILLIAM WOLFE',
                          'CHRISTOPHER FISCHER',
                          'JAMES L JOHNSON JR',
                          'JEREMY HEATH']), 'writein'] = 'TRUE'
QuietPrint(f"WRITEIN CANDIDATES:\n"+\
           f"*{ind.candidate[ind.writein=='TRUE'].unique()}")
'''
Replace parens in nicknames with strings, and move nicknames to 
immediately before surname per QA engine enforced convention. A tempting idea
is to grab anything inside parentheses and move it to immediately before the 
last space. But with such messy data the actually professional approach is 
probably to just suck it up and do some typing.
'''
ind.candidate.replace({'\(': '"',
                       '\)': '"'
                      }, regex=True, inplace=True)
ind.candidate.replace({
    '\"CINDY" CYNTHIA REINERT': 'CYNTHIA "CINDY" REINERT',
    'ANTHONY J ""TONY"" COOK': 'ANTHONY J "TONY" COOK',
    'CLYDE A CHIP PERFECT JR': 'CLYDE A "CHIP" PERFECT JR',
    'ROBERT "BOB" D EMERY': 'ROBERT D "BOB" EMERY',
    'SHERIAN "SHERRY" J MORRIS': 'SHERIAN J "SHERRY" MORRIS'
    }, inplace = True)
ind.candidate.replace({'\&QUOT;': '"'}, regex=True, inplace=True)

#Double check that all similar-looking candidates really are the same people
cand_pairs = [
	("AMY SWAN","AMY SWAIN"),
	("RYAN DVORAK","RYAN M DVORAK"),
	("DAVID ABBOTT","DAVID H ABBOTT"),
	("SUSAN BROOKS","SUSAN W BROOKS"),
	("DAVID WOLKINS","DAVID A WOLKINS"),
	("LACK CAMPBELL","ZACK CAMPBELL"),
	("LARRY BUCSHON","LARRY D BUCSHON"),
	("LARY K KLEEMAN","LARRY K KLEEMAN"),
	("MATTHEW LEHMAN","MATTHEW S LEHMAN"),
	("CHRISTINA ZACNY","CHRISTINA L ZACNY"),
	("PETER VISCLOSKY","PETER J VISCLOSKY"),
	("DONALD RAINWATER","DONALD G RAINWATER II"),
	("THOMASINA MARSILI","E THOMASINA MARSILI"),
	("MANDY GAUGER CREECH","RANDY GAUGER CREECH")
]
for cands in cand_pairs:
    QuietPrint(f"Offices for {cands[0]} vs {cands[1]}:\n" +
            str(ind[ind.candidate == cands[0]].office.unique()) + \
            str(ind[ind.candidate == cands[1]].office.unique())
         )

#Standardization
ind.candidate.replace({
    'BALLOTS': 'BALLOTS CAST',
    'BEN SCHMALTZ': 'BEN SMALTZ',
    'BRIAN BOSMA': 'BRIAN C BOSMA',
    'CAST VOLES:': 'CAST VOTES',#lol
    '"CAST VOTES"': 'CAST VOTES',
    "CAST VOTES'": 'CAST VOTES',
    'CAST VOTES-': 'CAST VOTES',
    'CAST VOTES:': 'CAST VOTES',
    'DEE MOORE': 'DEE M MOORE',
    'DEMOCRAT': 'DEMOCRATIC',
    'DEMOCRATIC PARTY': 'DEMOCRATIC',
    'DENNIS KRUSE': 'DENNIS K KRUSE',
    'DONALD LEHE': 'DONALD J LEHE',
    'DONNA SCHAJBLEY': 'DONNA SCHAIBLEY',
    'GARY SNYDER': 'GARY L SNYDER',
    'JAMES BUCK': 'JAMES R BUCK',
    'JIM RANKS': 'JIM BANKS',
    'JOHN AGUILERA': 'JOHN C AGUILERA',
    'JOSBLYN WHITTICKER': 'JOSELYN WHITTICKER',
    'JOSELYN VVHITTICKER': 'JOSELYN WHITTICKER',
    'JOSELYN WHITTICKFR': 'JOSELYN WHITTICKER',
    'JOSELYN WIIITTICKER': 'JOSELYN WHITTICKER',
    'KAREN ENGLEHAN': 'KAREN ENGLEMAN',
    'KEVIN MAHAN': 'KEVIN A MAHAN',
    'KIMBERLY ANN FIDLER': 'KIMBERLY ANNE FIDLER',
    'LARRY D SUCSHON': 'LARRY D BUCSHON',
    'LIBERTARIAN PARTY': 'LIBERTARIAN',
    'LUCY BRENTON': 'LUCY M BRENTON',
    'LUCY NC BRENTON': 'LUCY M BRENTON',
    'MAURICE FULLER': 'MAURICE OAKEL FULLER',
    'MEL WALL': 'MEL HALL',
    'NAOMI BECHTOLD': 'NAOMI S BECHTOLD',
    'OVER': 'OVERVOTES',
    'OVER VOTES': 'OVERVOTES',
    'PHILIP L BOOTS': 'PHILIP L "PHIL" BOOTS',
    'REGISTERED': 'REGISTERED VOTERS',
    'REGISTRATION': 'REGISTERED VOTERS', #registered voter nums in VANDERBURG
    'REPUBLICAN PARTY': 'REPUBLICAN',
    'MARK RUTHERFORD': 'MARK W RUTHERFORD',
    'TOBY BECK': 'TOBI BECK',
    'TOM FERKINHOGG': 'TOM FERKINHOFF',
    'TREY HOLLINGSWORM': 'TREY HOLLINGSWORTH', #lol
    'UNDER': 'UNDERVOTES',
    'UNDER VOTES': 'UNDERVOTES',
    'WENDY MCNAMARA': 'WENDY "MAC" MCNAMARA',
    'WILLIAM TANGOS': 'WILLIAM TANOOS',
    'WITHAM TANOOS': 'WILLIAM TANOOS',
    'WRITE IN': 'WRITEIN',
    'WRITE-1N': 'WRITEIN',
    'WRITE-IN': 'WRITEIN',
    'WRITE-IN VOTES': 'WRITEIN',
    'WRITE-INS': 'WRITEIN',
    'WRITE~IN': 'WRITEIN',
    '_': '', #Only used for meta-information in one precinct in GIBSON county
    'AMY SWAN': 'AMY SWAIN',
    'RYAN DVORAK': 'RYAN M DVORAK',
    'DAVID ABBOTT': 'DAVID H ABBOTT',
    'SUSAN BROOKS': 'SUSAN W BROOKS',
    'DAVID WOLKINS': 'DAVID A WOLKINS',
    'LACK CAMPBELL': 'ZACK CAMPBELL',
    'LARRY BUCSHON': 'LARRY D BUCSHON',
    'LARY K KLEEMAN': 'LARRY K KLEEMAN',
    'MATTHEW LEHMAN': 'MATTHEW S LEHMAN',
    'CHRISTINA ZACNY': 'CHRISTINA L ZACNY',
    'PETER VISCLOSKY': 'PETER J VISCLOSKY',
    'DONALD RAINWATER': 'DONALD G RAINWATER II',
    'THOMASINA MARSILI': 'E THOMASINA MARSILI',
    'MANDY GAUGER CREECH': 'RANDY GAUGER CREECH'
    }, inplace = True)

#Straight tickets: when the office is 'STRAIGHT TICKET', the candidate name
# needs to match party_simplified
ind.loc[(ind.candidate == '') & (ind.office == 'STRAIGHT TICKET'),
        'candidate'] = \
         ind.loc[(ind.candidate == '') & (ind.office == 'STRAIGHT TICKET'),
         'party_simplified']

#The raw data from Tippecanoe county has 4 rows with positive vote totals but 
# no candidate name. Drop them
ind = ind[~((ind.county == 'TIPPECANOE') & \
            (ind.candidate == '') & \
            (ind.party_simplified == 'DEMOCRAT')
          )]

#Now that names are standardized, we find that some candidates have missing 
# party labels. Let's apply all of those. First check actually ambiguous ones
ambiguous = ['THOMAS HEDDE', 'CORINNE WESTERFIELD', 'DALE ARNETT', \
             'MIKE WILBER']
for cand in ambiguous:
    QuietPrint(f"{cand} offices:\n"+\
               f"{ind[ind.candidate == cand].office.unique()}")
'''
These are all one person, so some people are just mislabeled. Next we also
need to know that this is not coming from us but that these double-labels
are issues in the original data. List the counties, then check the raw data
manually. Sadly the problems do originate with the raw data
'''
for cand in ambiguous:
    QuietPrint(f"{cand} counties:\n"+\
               f"{ind[ind.candidate == cand].county.unique()}")

#Now we can overwrite/fill out the contradictory/missing party labels
cand_to_party = {
	'ADAM WERNER': 'LIBERTARIAN',
	'CHRISTINA FIVECOATE': 'DEMOCRAT',
	'CLYDE A "CHIP" PERFECT JR': 'REPUBLICAN',
	'CONNIE LAWSON': 'REPUBLICAN',
	'CORDELLE FEUSTON': 'DEMOCRAT',
	'CORINNE WESTERFIELD': 'DEMOCRAT',
	'COURTNEY TRITCH': 'DEMOCRAT',
	'DALE ARNETT': 'LIBERTARIAN',
	'DANIEL J "DAN" LEONARD': 'REPUBLICAN',
	'DEE THORNTON': 'DEMOCRAT',
	'DEMOCRATIC': 'DEMOCRAT',
	'DENNIS K KRUSE': 'REPUBLICAN',
	'DONALD J LEHE': 'REPUBLICAN',
	'EDIE HARDCASTLE': 'DEMOCRAT',
	'ETHAN MANNING': 'REPUBLICAN',
	'GREG PENCE': 'REPUBLICAN',
	'HEATH R VANNATTER': 'REPUBLICAN',
	'JAMES R BUCK': 'REPUBLICAN',
	'JEANNINE LEE LAKE': 'DEMOCRAT',
	'JEFF RAATZ': 'REPUBLICAN',
	'JEROME "JAKE" HOOG': 'DEMOCRAT',
	'JIM BAIRD': 'REPUBLICAN',
	'JIM BANKS': 'REPUBLICAN',
	'JIM HARPER': 'DEMOCRAT',
	'JIM TOMES': 'REPUBLICAN',
	'JOE DONNELLY': 'DEMOCRAT',
	'JOHN "JD" PRESCOTT': 'REPUBLICAN',
	'JOHN C AGUILERA': 'DEMOCRAT',
	'JOHN SCHICK': 'LIBERTARIAN',
	'JORGE FERNANDEZ': 'DEMOCRAT',
	'JOSELYN WHITTICKER': 'DEMOCRAT',
	'KELLY MITCHELL': 'REPUBLICAN',
	'KEVIN A MAHAN': 'REPUBLICAN',
	'LARRY D BUCSHON': 'REPUBLICAN',
	'LIBERTARIAN': 'LIBERTARIAN',
	'LUCY M BRENTON': 'LIBERTARIAN',
	'LYNN JOHNSON': 'DEMOCRAT',
	'MARK MESSMER': 'REPUBLICAN',
	'MARK W RUTHERFORD': 'LIBERTARIAN',
	'MATT HOSTETTLER': 'REPUBLICAN',
	'MATTHEW S LEHMAN': 'REPUBLICAN',
	'MAURICE OAKEL FULLER': 'DEMOCRAT',
	'MIKE BRAUN': 'REPUBLICAN',
	'MIKE WILBER': 'DEMOCRAT',
	'PATRICK BAUER': 'DEMOCRAT',
	'RANDY FRYE': 'REPUBLICAN',
	'REPUBLICAN': 'REPUBLICAN',
	'RYAN M DVORAK': 'DEMOCRAT',
	'SHON BYRUM': 'DEMOCRAT',
	'SUSAN W BROOKS': 'REPUBLICAN',
	'TERA KLUTZ': 'REPUBLICAN',
	'TERRY DORAN': 'DEMOCRAT',
	'THOMAS "TOM" HEDDE': 'DEMOCRAT',
	'THOMAS E "TOM" SAUNDERS': 'REPUBLICAN',
	'THOMAS HEDDE': 'DEMOCRAT',
	'TOBI BECK': 'DEMOCRAT',
	'TOM FERKINHOFF': 'LIBERTARIAN',
	'TRACY ROBERTS': 'DEMOCRAT',
	'TRAVIS HOLDMAN': 'REPUBLICAN',
	'WILLIAM TANOOS': 'DEMOCRAT'
        }
for cand in cand_to_party.keys():
    party = cand_to_party[cand]
    ind.loc[ind.candidate == cand, 'party_simplified'] = party
    ind.loc[ind.candidate == cand, 'party_detailed'] = party

#TOM FERKINHOFF was on the ballot, and it's hard to imagine they were on the
# ballot in some places but was reported as a writein somewhere else
ind.loc[ind.candidate == 'TOM FERKINHOFF', 'writein'] = 'FALSE'

#WRITEIN candidates should always have a WRITEIN value of true
ind.loc[ind.candidate == 'WRITEIN', 'writein'] = 'TRUE'

QuietPrint(np.sort(ind.candidate.unique()))


###############################################################################
# Mode
###############################################################################
STAGEWISE_VERBOSE = False
QuietPrint(np.sort(ind["mode"].unique()))

ind["mode"].replace({'election_day': 'ELECTION DAY',
                     'early_voting': 'EARLY',
                     'absentee': 'ABSENTEE',
                     'provisional': 'PROVISIONAL'
                    }, inplace=True)

QuietPrint(np.sort(ind["mode"].unique()))


###############################################################################
# Generate all remaining standard MEDSL variables
###############################################################################
STAGEWISE_VERBOSE = False

ind['dataverse'] = ''
ind.loc[ind.office == 'US SENATE', 'dataverse'] = 'SENATE'
ind.loc[ind.office == 'US HOUSE', 'dataverse'] = 'HOUSE'
ind.loc[ind.office.isin([
        'BALLOTS CAST',
        'REGISTERED VOTERS'
        ]), 'dataverse'] = ''
ind.loc[ind.dataverse == '', 'dataverse'] = 'STATE'
QuietPrint(np.sort(ind.dataverse.unique()))

ind = ind.rename(columns = {"county": "county_name"})

ind["year"] = 2018
ind["stage"] = "GEN"
ind["state"] = "INDIANA"
ind["special"] = "FALSE"
ind["state_po"] = "IN"
ind["state_fips"] = "18"
ind["state_cen"] = "32"
ind["state_ic"] = "22"
ind["date"] = "2018-11-06"
ind["readme_check"] = "TRUE" #Always read the readme

#Magnitude is not necessarily known for local races, and likely many school
# board races have magnitude greater than 1. Just apply magnitude at the
# state or federal level
ind['magnitude'] = None
ind.loc[ind.office.isin([
                         'US SENATE',
                         'US HOUSE',
                         'STATE HOUSE',
                         'STATE SENATE',
                         'SECRETARY OF STATE',
                         'STATE AUDITOR',
                         'STATE TREASURER'
                         ]), 'magnitude'] = 1

#Merge in local-level fips codes, create jurisdiction variable with county
# names and fips
county_fips = pd.read_csv(COUNTY_FIPS_FNAME)
county_fips.state = county_fips.state.str.upper()
county_fips.replace({'ST. JOSEPH': 'ST JOSEPH'}, inplace=True)
ind = pd.merge(ind, county_fips, on=['state','county_name'],how='left')
ind.county_fips = ind['county_fips'].apply(str).str.pad(
                                     5, side='left', fillchar='0')
ind['jurisdiction_fips'] = ind['county_fips']
ind['jurisdiction_name'] = ind['county_name']


###############################################################################
# Duplicate handling
###############################################################################
STAGEWISE_VERBOSE = False

'''
At this point the duplicated checker reports 48 duplicated rows and 11 further
near-duplicated rows, so we address those here
First, Mike Bowling in Clark county precinct Bethlehem 1: 
    this is in the raw data. Here are the extra votes:
'''
QuietPrint(f"MILE BOWLING VOTE TOTAL: "+\
           f"{sum(ind.votes[ind.candidate == 'MIKE BOWLING'])}")

#Dropping them gets us only 2 off from his real vote total: 
#https://ballotpedia.org/Mike_Bowling
ind = ind.drop([84527])

#Now there is a series of overvote rows with no votes in them. These can be 
#dropped losslessly
ind = ind.drop([94503, 94508, 94605, 94610, 94707, 94712, 94809, 94814, 94911,\
                94916])

#DAN FORESTAL has vote totals equalling 11,844 extra votes. 
# These duplicated rows are in the original data. 
QuietPrint(f"DAN FORESTAL VOTE TOTAL: "+\
           f"{sum(ind.votes[ind.candidate == 'DAN FORESTAL'])}")

#His vote total in our data is much larger than the real total ... even after
#dropping the exactly duplicated rows: https://ballotpedia.org/Dan_Forestal
ind = ind.drop([150949, 150950, 150951, 150952, 150953, 150954, 150955, \
                150956, 150957, 150958, 150959, 150960, 150961, 150962, \
                150963, 150964, 150965, 150966, 150967, 150968, 150969, \
                150970, 150971, 150972, 150973, 150974, 150975, 150976, \
                150977, 150978, 150979, 150980, 150981, 150982, 150983
                ])

'''
JOHN L BARTLETT has one duplicated row with 763 extra votes. It is present in
the original dataset. His vote total in our data exceed his real vote total
by about 700 votes. Dropping.
'''
QuietPrint(f"JOHN L BARTLETT VOTE TOTAL: "+\
           f"{sum(ind.votes[ind.candidate == 'JOHN L BARTLETT'])}")
ind = ind.drop([150944])

ind_no_votes = ind.drop('votes', axis=1)
ind_no_votes[ind_no_votes.duplicated()].to_csv('near_duplicates.csv')
'''
Of the 11 near-duplicates, I don't see how we can resolve 10 of them. These are
votes in Johnson sounty, in some NEEDHAM precincts, for county council. They 
are all undervotes, and all present in the original data, but the vote totals
 are non-zero and unequal. There is presumably no canonical statement about 
the real number of undervotes in these county council races, because all we
have for Indiana at the county level are ENR maps. So, we retain them and 
inform the people in the readme.
What we can look into is MAURICE OAKEL FULLER's near-duplicate in TIPPECANOE.
This near-duplicate is present in the original data.
'''
QuietPrint(f"MAURICE OAKEL FULLER VOTE TOTAL: "+\
           f"{sum(ind.votes[ind.candidate == 'MAURICE OAKEL FULLER'])}")
#Fuller's vote total is very substantially too large. We therefore don't know
# which one to drop, if we were to drop one. Another one bites the readme


###############################################################################
# Final glossing
###############################################################################
STAGEWISE_VERBOSE = True

#Some global rules are safest to implement now
ind.party_simplified.replace({'INDEPENDENT': 'OTHER'}, inplace=True)

#Drop county-level aggregate vote rows
QuietPrint(f"Aggregate rows found in counties "+\
           f"{ind[ind.precinct.str.contains(' IN')].county_name.unique()}")
preDropLen = len(ind)
ind = ind[~(ind.precinct.isin(['HAMILTON IN',
                               'KOSCIUSKO IN',
                               'LAKE IN',
                               'VIGO IN',
                               'TIPPECANOE IN',
                               'TOTAL',
                               'Total',
                               'Totals'
                               ])
         )]
'''
#"Total" sometimes used when mode not provided. Can only drop case by case :(
ind = ind[~((ind.county_name == 'RIPLEY') & (ind.precinct == 'Total'))]
ind = ind[~((ind.county_name == 'STEUBEN') & (ind.precinct == 'Total'))]
ind = ind[~((ind.county_name == 'VERMILLION') & (ind.precinct == 'Total'))]
'''
postDropLen = len(ind)
QuietPrint(f"Dropped {preDropLen - postDropLen} aggregate rows")


###############################################################################
# Output the full statewide dataset
###############################################################################
ind.to_csv("2018-in-precinct-general.csv",
           index=False,
           encoding='utf-8')


