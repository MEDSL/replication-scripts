import pandas as pd
import csv

file = '2018-nh-precinct-autoadapted.csv'
df = pd.read_csv(file)

def fixBool(x):
    if x == True:
        return 'TRUE'
    else:
        return 'FALSE'
    
df['special'] = df['special'].apply(fixBool)
df['writein'] = df['writein'].apply(fixBool)

df.fillna('', inplace=True) 
df

def fixJurisdiction(x):
    if any(s in x for s in ['CAMBRIDGE', 'DIXVILLE', 'KILKENNY', 'MILLSFIELD', 'ODELL', 'SUCCESS']):
        return x + ' TOW'
    if x=='LACONIA WD':
        return 'LACONIA'
    if x=='HALES LOCATION':
        return "HALE'S LOCATION"
    if x=='HARTS LOCATION':
        return "HART'S LOCATION"
    if x=='WENTWORTHS LOCATION':
        return 'WENTWORTH LOCATION'
    if x=='LOW BURBANKS GRANT':
        return 'LOW AND BURBANKS GRANT'
    if x=='THOMPSON MESERVES PURCHASE':
        return 'THOMPSON AND MESERVES PURCHASE'
    if x=="GREEN'S GRANT":
        return "GREENS GRANT"
    return x
df['jurisdiction_name'] = df['jurisdiction_name'].apply(fixJurisdiction)
df.loc[(df['jurisdiction_name']=='ATKINSON')&(df['county_name']=='COOS'),
    'jurisdiction_name'] = 'ATKINSON AND GILMANTON ACADEMY GRANT'
df.loc[(df['jurisdiction_name']=='WENTWORTH')&(df['county_name']=='COOS'),
    'jurisdiction_name'] = 'WENTWORTH LOCATION'

def merge_fips_codes(df):
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
df = merge_fips_codes(df)

df['date'] = '2018-11-06'
df['readme_check'] = 'FALSE'
df['state_ic'] = df['state_ic'].astype(str).str.zfill(2)
df['state_fips'] = df['state_fips'].astype(str)
df['state_cen'] = df['state_cen'].astype(str)
df['year'] = df['year'].astype(str)
df['county_fips'] = df['county_fips'].astype(str)
df['jurisdiction_fips'] = df['jurisdiction_fips'].astype(str)

def fixDistrict(x):
    if x != 'STATEWIDE':
        dist_num = ''.join([str(n) for n in list(x) if n.isdigit()]).zfill(3)
        if dist_num == '000':
            return ''
        return dist_num
    return 'STATEWIDE'
df['district'] = df['district'].apply(fixDistrict)

def fixQuotes(x):
    if x=='""':
        return ''
    return x
df['party_detailed'] = df['party_detailed'].apply(fixQuotes)

def getMagnitude(county, district, office):
    if office=='STATE HOUSE':
        if county=='BELKNAP':
            if any(s==district for s in ['002', '003']):
                return 4
            if any(s==district for s in ['004', '005', '006']):
                return 2
        if county=='CARROLL':
            if any(s==district for s in ['002', '005']):
                return 3
            if any(s==district for s in ['003', '004', '006']):
                return 2
        if county=='CHESHIRE':
            if any(s==district for s in ['001']):
                return 4
            if any(s==district for s in ['009', '011', '012', '016']):
                return 2
        if county=='COOS':
            if any(s==district for s in ['001']):
                return 2
            if any(s==district for s in ['003']):
                return 3
        if county=='GRAFTON':
            if any(s==district for s in ['001', '009']):
                return 2
            if any(s==district for s in ['008']):
                return 3
            if any(s==district for s in ['012', '013']):
                return 4
        if county=='HILLSBOROUGH':
            if any(s==district for s in ['001', '004', '005', '008', '009', '010', '011', 
                                         '012', '013', '014', '015', '016', '017', '018',
                                         '019', '020', '024', '025', '027', '027', '038', 
                                         '042', '044', '045']):
                return 2
            if any(s==district for s in ['002', '028', '029', '030', '031', '032', '033',
                                         '034', '035', '036', '043']):
                return 3
            if any(s==district for s in ['023']):
                return 4
            if any(s==district for s in ['006']):
                return 5
            if any(s==district for s in ['007']):
                return 6
            if any(s==district for s in ['021']):
                return 8
            if any(s==district for s in ['037']):
                return 11
        if county=='MERRIMACK':
            if any(s==district for s in ['002', '003', '005', '006', '009', '021', '027']):
                return 2
            if any(s==district for s in ['010', '020', '023']):
                return 3
            if any(s==district for s in ['024']):
                return 4
        if county=='ROCKINGHAM':
            if any(s==district for s in ['009', '019', '024']):
                return 2
            if any(s==district for s in ['002', '003', '017', '020']):
                return 3
            if any(s==district for s in ['007', '013', '014', '018', '021']):
                return 4
            if any(s==district for s in ['004']):
                return 5
            if any(s==district for s in ['005']):
                return 7
            if any(s==district for s in ['008']):
                return 9
            if any(s==district for s in ['006']):
                return 10
        if county=='STRAFFORD':
            if any(s==district for s in ['001', '002', '003', '004']):
                return 2
            if any(s==district for s in ['017', '018']):
                return 3
            if any(s==district for s in ['006']):
                return 5
        if county=='SULLIVAN':
            if any(s==district for s in ['001', '006']):
                return 2
    if office=='COUNTY COMMISSIONER':
        if county=='STRAFFORD':
            return 3
    return 1
df['magnitude'] = df.apply(lambda x: getMagnitude(x['county_name'], x['district'], x['office']), axis=1)

def cleanCandidate(x):
    if x=='[WRITE-IN]':
        return 'WRITEIN'
    x = x.replace('.', '')
    x = x.replace(',', '')
    if x=='AHERN JR':
        return 'HENRY D AHERN JR'
    if x=='ARNOLD':
        return 'PAMELA J ARNOLD'
    if x=='BABSON':
        return 'DAVID L BABSON JR'
    if x=='BAILEY':
        return 'RICHARD BRADFORD BAILEY'
    if x=='MONAHAN':
        return 'KELLEY JEAN MONAHAN'
    if x=='BAKER':
        return 'KATE BAKER'
    if x=='BARRETTE':
        return 'JEFF BARRETTE'
    if x=='BARRY':
        return 'DICK BARRY'
    if x=='BERGERON':
        return 'PAUL G BERGERON'
    if x=='BERNIER':
        return 'LEO R BERNIER'
    if x=='BERUBE':
        return 'CATHERINE A BERUBE'
    if x=='BOURDON':
        return 'JOSHUA BOURDON'
    if x=='BRACK':
        return 'CHARLENE A BRACK'
    if x=='BRADSTREET':
        return 'JANE BRADSTREET'
    if x=='BRADY':
        return 'THOMAS M BRADY'
    if x=='BROWN':
        return 'BRUCE G BROWN'
    if x=='BRYK':
        return 'WILLIAM BRYK'
    if x=='CARTWRIGHT':
        return 'JOE CARTWRIGHT'
    if x=='CLARK':
        return 'TERRY M CLARK'
    if x=='JACOBS':
        return 'EMILY JACOBS'
    if x=='CONLON':
        return 'MICHAEL CONLON'
    if x=='CONWAY':
        return 'PATRICIA M CONWAY'
    if x=='COSTELLO':
        return 'JOSEPH L COSTELLO'
    if x=='COYLE':
        return 'KEVIN COYLE'
    if x=='CRAGIN':
        return 'SUSAN CRAGIN'
    if x=='DAVIDSON':
        return 'BOB DAVIDSON'
    if x=='DAVIS':
        return 'ROBIN DAVIS'
    if x=='DAY':
        return 'AARON DAY'
    if x=='DEVOY II':
        return 'DAVID D DEVOY II'
    if x=='DUBOIS':
        return 'DAVID G DUBOIS'
    if x=='DUTILE':
        return 'DOUGLAS R DUTILE'
    if x=='ENGLUND':
        return 'ROBERT J ENGLUND'
    if x=='FREDETTE':
        return 'DAVID G FREDETTE'
    if x=='GAGNON':
        return 'RAYMOND GAGNON'
    if x=='GIBSON':
        return 'JANET GIBSON'
    if x=='GLASSMAN':
        return 'ALAN GLASSMAN'
    if x=='GRAVES':
        return 'R GRAVES'
    if x=='HALVORSEN':
        return 'PAUL A HALVORSEN'
    if x=='HARDY':
        return 'JAMES HARDY'
    if x=='HATHAWAY':
        return 'MARC HATHAWAY'
    if x=='HEBERT':
        return 'GEORGE HEBERT'
    if x=='HILL':
        return 'KEN HILL'
    if x=='HILLIARD':
        return 'SCOTT E HILLIARD'
    if x=='HOGAN':
        return 'DENNIS HOGAN'
    if x=='HORNICK':
        return 'MARCIE HORNICK'
    if x=='KAROUTAS':
        return 'PERIKLIS KAROUTAS'
    if x=='KIDDER':
        return 'DAVID KIDDER'
    if x=='LAPLANTE':
        return 'JEREMY LAPLANTE'
    if x=='LAUER':
        return 'LINDA LAUER'
    if x=='LAVENDER':
        return 'MEG LAVENDER'
    if x=='LESTER':
        return 'DARLENE LESTER'
    if x=='LEVASSEUR':
        return 'JOSEPH KELLY LEVASSEUR'
    if x=='LIVERNOIS':
        return 'ANDREW B LIVERNOIS'
    if x=='MAGLARAS':
        return 'GEORGE MAGLARAS'
    if x=='MASSAHOS':
        return 'CHUCK MASSAHOS'
    if x=='MAYBERRY':
        return 'MATT MAYBERRY'
    if x=='MCCARTHY':
        return 'TERRY MCCARTHY'
    if x=='MCCORMICK':
        return 'DAN MCCORMICK'
    if x=='MCGRATH':
        return 'JUDY MCGRATH'
    if x=='MCLAUGHLIN':
        return 'D CHRIS MCLAUGHLIN'
    if x=='MIRSKI':
        return 'PAUL MIRSKI'
    if x=='MORIN':
        return 'DON MORIN JR'
    if x=='MORRIS':
        return 'MARCIA MORRIS'
    if x=='MOYER':
        return 'MICHAEL A MOYER'
    if x=='MUZZEY':
        return 'MICHAEL G MUZZEY'
    if x=="O'HEARNE":
        return "TIMOTHY O'HEARNE"
    if x=="O'ROURKE-ANDRUZZI":
        return "MICHAELA O'ROURKE-ANDRUZZI"
    if x=='PAPPAS':
        return 'CHRIS PAPPAS'
    if x=='PETERSON':
        return 'TERRI L PETERSON'
    if x=='PIPER':
        return 'WENDY PIPER'
    if x=='POUTRE':
        return 'GRIFFIN POUTRE'
    if x=='PRIESTLEY':
        return 'SCOTT PRIESTLEY'
    if x=='REARDON':
        return 'TARA REARDON'
    if x=='RICHARDI':
        return 'DOMENIC M RICHARDI'
    if x=='RIDEOUT':
        return 'LEON H RIDEOUT'
    if x=='RIVERA':
        return 'ELI RIVERA'
    if x=='RODRIGUEZ':
        return 'RICARDO RODRIGUEZ'
    if x=='ROLLO':
        return 'DEANNA S ROLLO'
    if x=='ROPP':
        return 'ELIZABETH ROPP'
    if x=='ROTH':
        return 'BETH ROTH'
    if x=='ROWE':
        return 'ROBERT ROWE'
    if x=='SAMSON':
        return 'RICHARD J SAMSON'
    if x=='SANDERSON':
        return 'MICHAEL SANDERSON'
    if x=='SAPIENZA':
        return 'EDWARD J SAPIENZA'
    if x=='SCOTT':
        return 'DAVID SCOTT'
    if x=='SIMONDS':
        return 'JOHN P SIMONDS'
    if x=='SIROIS':
        return 'NANCY SIROIS'
    if x=='SOUCY':
        return 'CAROL J SOUCY'
    if x=='SPAULDING':
        return 'PETER J SPAULDING'
    if x=='SPRATT':
        return 'STEVE SPRATT'
    if x=='STACEY':
        return 'CATHY STACEY'
    if x=='STIEGLER':
        return 'JEFF STIEGLER'
    if x=='SUBJECK':
        return 'HEATHER A SUBJECK'
    if x=='SWEENEY':
        return 'CYNTHIA PAGE SWEENEY'
    if x=='TAPPAN':
        return 'BILL TAPPAN'
    if x=='TAYLOR':
        return 'HUNTER TAYLOR'
    if x=='TILTON':
        return 'ANNA Z TILTON'
    if x=='TOMBARELLO':
        return 'THOMAS TOMBARELLO'
    if x=='TWEEDIE':
        return 'RAY TWEEDIE'
    if x=='VALERINO':
        return 'BRIAN L VALERINO'
    if x=='VELARDI':
        return 'THOMAS P VELARDI'
    if x=='WATSON':
        return 'ROBERT J WATSON'
    if x=='WEISS':
        return 'BERT WEISS'
    if x=='WHALEN':
        return 'DONALD WHALEN'
    if x=='WOZMAK':
        return 'JACK WOZMAK'
    if x=='DUVAL':
        return 'JEROME DUVAL'
    if x=='LACHANCE':
        return 'DIANA M LACHANCE'
    return x
df['candidate'] = df['candidate'].apply(cleanCandidate)

def unmatchedCands(name, district):
    if name=='KATHY DESJARDIN' and district=='036':
        return 'GILBERT DESJARDINS'
    if name=='LISA NASH':
        return 'DAVID NASH'
    return name
df['candidate'] = df.apply(lambda x: unmatchedCands(x['candidate'], x['district']), axis=1)

# Fixing misisng candidate
df.loc[df['candidate'] == 'JANET WALL', 'party_detailed'] = 'DEMOCRAT'
df.loc[df['candidate'] == 'JANET WALL', 'party_simplified'] = 'DEMOCRAT'

df.loc[df['candidate'] == 'CHRIS PAPPAS', 'party_detailed'] = 'DEMOCRAT'
df.loc[df['candidate'] == 'CHRIS PAPPAS', 'party_simplified'] = 'DEMOCRAT'

df.loc[df['candidate'] == 'DAVID NASH', 'party_detailed'] = 'REPUBLICAN'
df.loc[df['candidate'] == 'DAVID NASH', 'party_simplified'] = 'REPUBLICAN'

df.loc[df['candidate'] == 'DICK BARRY', 'party_detailed'] = 'REPUBLICAN'
df.loc[df['candidate'] == 'DICK BARRY', 'party_simplified'] = 'REPUBLICAN'

df.loc[df['candidate'] == 'DONALD WHALEN', 'party_detailed'] = 'REPUBLICAN'
df.loc[df['candidate'] == 'DONALD WHALEN', 'party_simplified'] = 'REPUBLICAN'

df.loc[df['candidate'] == 'KIMBERLY RICE', 'party_detailed'] = 'REPUBLICAN'
df.loc[df['candidate'] == 'KIMBERLY RICE', 'party_simplified'] = 'REPUBLICAN'

# fixing holdout candidates
df.loc[((df['candidate']=='NELSON')&(df['office']=='SHERIFF')&(df['county_name']=='CHESHIRE')),
    'candidate'] = 'EARL NELSON'
df.loc[((df['candidate']=='KELLY')&(df['office']=='TREASURER')&(df['county_name']=='CHESHIRE')),
    'candidate'] = 'KENNETH KELLY'
df.loc[((df['candidate']=='COLLINS')&(df['office']=='TREASURER')&(df['county_name']=='COOS')),
    'candidate'] = 'SUZANNE COLLINS'
df.loc[((df['candidate']=='MACAIONE  JR')&(df['office']=='SHERIFF')&(df['county_name']=='STRAFFORD')),
    'candidate'] = 'ANTHONY MACAIONE JR'

df.loc[((df['candidate']=='RICE')&(df['office']=='STATE HOUSE')&
    (df['county_name']=='HILLSBOROUGH')&(df['district']=='037')),'candidate'] = 'KIMBERLY RICE'
df.loc[((df['candidate']=='RICE')&(df['office']=='STATE HOUSE')&
    (df['county_name']=='ROCKINGHAM')&(df['district']=='020')),'candidate'] = 'DENIS RICE'


df = df[~((df['candidate']=='WRITEIN')&(df['votes']==0))].drop_duplicates().copy()

# fix issue where someone previously changed Wentworth to wrong county
df.loc[(df['precinct']=='WENTWORTH')&(df['jurisdiction_name'] == 'WENTWORTH LOCATION'),'county_name'] = 'GRAFTON'
df.loc[(df['precinct']=='WENTWORTH')&(df['jurisdiction_name'] == 'WENTWORTH LOCATION'),'county_fips'] = '33009'
df.loc[(df['precinct']=='WENTWORTH')&(df['jurisdiction_name'] == 'WENTWORTH LOCATION'),'jurisdiction_fips'] = '3300980500'
df.loc[(df['precinct']=='WENTWORTH')&(df['jurisdiction_name'] == 'WENTWORTH LOCATION'),'jurisdiction_name'] = 'WENTWORTH'

column_names = ['precinct', 'office', 'party_detailed', 'party_simplified', 'mode', 'votes', 
                'county_name', 'county_fips', 'jurisdiction_name', 'jurisdiction_fips', 'candidate', 
                'district', 'dataverse', 'year', 'stage', 'state', 'special', 'writein', 'state_po', 
                'state_fips', 'state_cen', 'state_ic', 'date', 'readme_check', 'magnitude']
df = df.reindex(columns=column_names)


df.to_csv('2018-nh-precinct-general-updated.csv', index=False, quoting=csv.QUOTE_NONNUMERIC)

