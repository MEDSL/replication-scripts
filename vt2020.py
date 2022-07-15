import pandas as pd
import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_file(file: str) -> DataFrame:
    data = pd.read_excel(file)
    # We do not need Total votes
    data = data.drop('Total Votes', axis=1)
    data = data.melt(id_vars=['Town', 'Rep District'],
                     var_name='Candidate', value_name='Votes')
    name = file[4:-51]
    # Drop Write-In if votes == 0
    data = data[
        ~((data['Candidate'].str.upper().str.contains('\(WRITE-IN\)')) &
          (data['Votes'] == 0))
        ].reset_index(drop=True)
    data['File'] = name
    return data


def load_file2(file: str) -> DataFrame:
    all_sheets = pd.read_excel(file, sheet_name=None)
    data = pd.DataFrame()

    for sheet in all_sheets.values():
        # Remove vote totals
        sheet = sheet.drop(columns=sheet.columns[-2:], axis=1)

        # Remove vote types
        sheet = sheet.drop(sheet.tail(4).index)

        title = sheet.columns[0]
        sheet.columns = ['Candidate', 'Party']
        office, magnitude = title.split(' || ')
        sheet['Magnitude'] = magnitude[16:]

        # Make file field that matches other format
        file2 = 'StateWide' if file == 'raw2/state.xlsx' else file[5:-5].capitalize()
        if office.startswith('STATE SENATOR'):
            office = office[15:]
        elif office.startswith('STATE REPRESENTATIVE'):
            office = office[22:]
        elif file2 == 'County':
            if office == 'ADDISON':
                office = 'ADDISON_HIGH BAILIFF'
            else:
                office = office + '_' + office

        sheet['File'] = file2 + '_' + office

        data = data.append(sheet)

    return data


def load_files() -> DataFrame:
    data = pd.DataFrame()
    for file in EC.simple_walk():
        print(f'*Reading file raw/{file}...')
        file_data = load_file(f'raw/{file}')
        data = data.append(file_data)
        print(f'Read file raw/{file}...')
    data = data.reset_index(drop=True)
    return data


def load_files2() -> DataFrame:
    data = pd.DataFrame()
    for file in EC.simple_walk(raw_folder='raw2'):
        print(f'*Reading file raw2/{file}...')
        file_data = load_file2(f'raw2/{file}')
        data = data.append(file_data)
        print(f'Read file raw2/{file}...')
    # Standardize for the sake of being able to merge
    data['Candidate'] = data['Candidate'].replace({
        'AMOS COLBY  \(Write-in\)': 'AMOS COLBY(Write-In)',
        }, regex=True)
    data = data.reset_index(drop=True)
    return data


def load_all_data(prepare_pickle=True) -> DataFrame:
    if prepare_pickle:
        data1 = load_files()
        data2 = load_files2()
        data = data1.merge(data2, how='outer', on=['Candidate', 'File'])
        data['Party'] = data['Party'].fillna('')  # Only such cases are writeins
        data.to_pickle('raw_VT20.pkl')

    data = pd.read_pickle('raw_VT20.pkl')
    return data


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `state`...')
    # State is Vermont by definition
    data = EC.state.add_state_codes(data, state='Vermont')

    print('Parsed VT20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `precinct`...')
    # Data is pulled straight from `Town`.
    data['temp_precinct'] = data['Town'].astype(str).str.strip().str.upper()

    # Still need to add - FLOAT were appropriate
    print('Partially parsed VT20 `precinct` (1/2).')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `office`...')

    # Data is pulled from `File`
    data['office'] = data['File']

    # Standardize names
    standard_names = {
        r'County.*': 'COUNTY HIGH BAILIFF',  # All such elections are High Bailiff
        r'Federal_REPRESENTATIVE.*': 'US HOUSE',
        r'Federal_US PRESIDENT.*': 'US PRESIDENT',
        r'House_.*': 'STATE HOUSE',
        r'Senate_.*': 'STATE SENATE',
        r'StateWide_': '',  # Rest of name is already standardized
        }

    data['office'] = data['office'].replace(standard_names, regex=True)

    print('Parsed VT20 `office`.')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `party_detailed...`')

    data['party_detailed'] = data['Party'].replace({
        'DEMOCRATIC': 'DEMOCRAT',
        'DEM/REP': 'DEMOCRAT-REPUBLICAN',
        'REP/DEM': 'REPUBLICAN-DEMOCRAT',
        'PROG/DEM': 'PROGRESSIVE-DEMOCRAT',
        'DEM/PROG': 'DEMOCRAT-PROGRESSIVE',
        }, regex=True)

    print('Parsed VT20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `party_simplified...`')

    same = {
        'DEMOCRAT',
        'REPUBLICAN',
        'LIBERTARIAN',
        ''
        }

    data['party_simplified'] = data['party_detailed'].where(
        data['party_detailed'].isin(same),
        'OTHER'
        )

    print('Parsed VT20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `mode`...')
    # Mode is consistently 'TOTAL'
    data['mode'] = 'TOTAL'

    print('Parsed VT20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    print('Parsed VT20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `county_name`...')
    # Data is pulled from `File`. We use the County elections to figure out which town
    # belongs to each county. WE cannot use Rep District as a few Rep District contain
    # 2 or more counties. We also take advantage of the fact each town name is unique

    county = data[data['File'].str.contains('County')][['Town', 'File']].drop_duplicates()
    county = EC.split_column(county, 'File', '.*_(?P<County>.*)_.*')
    county_map = county[['Town', 'County']].set_index('Town').to_dict()['County']

    data['county_name'] = data['Town'].replace(county_map)

    print('Parsed VT20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    data['county_fips'] = EC.county_fips.parse_fips_from_name(data)

    print('Parsed VT20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `jurisdiction_name`...')
    # `jurisdiction_name` is the same as `precinct` for Vermont, so use that
    data['jurisdiction_name'] = data['temp_precinct']

    print('Parsed VT20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `jurisdiction_fips`...')
    additional = {
        # From fips file.
        "SAINT JOHNSBURY": 5000562200,
        "SAINT GEORGE": 5000762050,

        # https://en.wikipedia.org/wiki/St._Albans_(city),_Vermont
        "SAINT ALBANS CITY": 5001161675,
        # https://en.wikipedia.org/wiki/St._Albans_(town),_Vermont
        "SAINT ALBANS TOWN": 5001161750,

        # https://en.wikipedia.org/wiki/Newport_(city),_Vermont
        "NEWPORT CITY": 5001948850,
        # https://en.wikipedia.org/wiki/Newport_(town),_Vermont
        "NEWPORT TOWN": 5001948925,

        # https://en.wikipedia.org/wiki/Rutland_(city),_Vermont
        "RUTLAND CITY": 5002161225,
        # https://en.wikipedia.org/wiki/Rutland_(town),_Vermont
        "RUTLAND TOWN": 5002161300,

        # https://en.wikipedia.org/wiki/Barre_(city),_Vermont
        "BARRE CITY": 5002303175,
        # https://en.wikipedia.org/wiki/Barre_(town),_Vermont
        "BARRE TOWN": 5002303250,
        }

    # Use recently obtained `jurisdiction_name` field and list of county fips codes
    data['jurisdiction_fips'] = EC.jurisdiction_fips.parse_fips_from_name(data,
                                                                          additional=additional)

    print('Parsed VT20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['temp_candidate'] = data['Candidate'].str.upper().str.strip()

    # First, remove any extraneous whitespace/characters
    data['temp_candidate'] = data['temp_candidate'].str.strip().replace({
        r' ( )+': ' ',
        r' - ': ' AND ',
        r'\.': '',
        r',': '',
        r'&': 'AND',
        }, regex=True)

    # Standardize some candidates
    data['temp_candidate'] = data['temp_candidate'].replace({
        r'SPOILED BALLOTS': 'OVERVOTES',
        r'SPOILED VOTES': 'OVERVOTES',
        r'BLANK VOTES': 'UNDERVOTES',
        r'BLANK/FICTIOUS': 'SCATTER',
        r'OVAL FILLED/BLANK': 'SCATTER',
        r'BLANK/FICTITIOUS': 'SCATTER',

        r'TOTAL WRITE-INS?': 'WRITEIN',
        r'CHRIS O;GRADY': "CHRIS O'GRADY",
        r'LAURA CHA\[PMAN': 'LAURA CHAPMAN',
        r'\[AUL MEACHAM': 'PAUL MEACHAM',
        r'SMITTY \?\?\?': 'SMITTY',
        r'\"ELISCA STEPHANIC\"': 'ELISCA STEPHANIC',
        r'PETER JR MARTIN': 'PETER J R MARTIN',
        r'WOODMAN \"WOODY\" H PAGE': 'WOODMAN H "WOODY" PAGE',
        }, regex=True)

    # Replace / with AND. We do this now so that it doesn't conflict with BLANK/FICTIOUS etc
    data['temp_candidate'] = data['temp_candidate'].str.strip().replace({
        r'/ ?': ' AND ',
        }, regex=True)

    # For non writein US President, remove the Vicepresident
    data['temp_candidate'] = data['temp_candidate'].mask(
        (data['office']=='US PRESIDENT') & (~data['temp_candidate'].str.contains('WRITE-IN')),
        data['temp_candidate'].replace({
            ' AND.*': '',
            }, regex=True)
        )

    # We will remove Writein later
    print('Partially parsed VT20 `candidate` (1/2).')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `district`...')

    # Data is pulled from District
    data['district'] = data['Rep District']


# removing this, as overwriting the district field for statewide offices leads to quasi duplicate rows because there are 
# multiple rows per township in the raw data that are differentiated by the district field.
    # Except statewide/federal races, whose district must be STATEWIDE
    statewide = {
        'US PRESIDENT',
        'ATTORNEY GENERAL',
        'AUDITOR OF ACCOUNTS',
        'GOVERNOR',
        'LIEUTENANT GOVERNOR',
        'SECRETARY OF STATE',
        'STATE TREASURER',
        }

    data['district'] = data['district'].mask(
        data['office'].isin(statewide),
        'STATEWIDE',
        )

    data['district'] = data['district'].mask(data['office'].str.contains('COUNTY'), "")
    data['district'] = data['district'].mask(data['office']=='US HOUSE', "000")


    print('Parsed VT20 `district`.')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `magnitude`...')

    data['magnitude'] = data['Magnitude'].replace({
        'ONE': 1,
        'TWO': 2,
        'THREE': 3,
        'SIX': 6,
        })

    # We still have a few NaNs, we get rid of the trivial 1s
    trivial_magnitude_one = {
        'US PRESIDENT',
        'US HOUSE',
        'ATTORNEY GENERAL',
        'AUDITOR OF ACCOUNTS',
        'GOVERNOR',
        'LIEUTENANT GOVERNOR',
        'SECRETARY OF STATE',
        'STATE TREASURER',
        'COUNTY HIGH BAILIFF'
        }

    data['magnitude'] = data['magnitude'].mask(
        data['office'].isin(trivial_magnitude_one),
        1
        )


    # For State House, each office, district either has magnitude one number or NaN
    # We replace the NaNs with the proper number, taking advantage n < NaN for all numbers n
    house = data[data['office']=='STATE HOUSE'][['magnitude', 'district']]
    house = house.drop_duplicates().sort_values(['district', 'magnitude'])
    house['magnitude'] = house['magnitude'].ffill()
    house = house.drop_duplicates()
    house_dict = house.set_index('district').to_dict()['magnitude']

    data['magnitude'] = data['magnitude'].mask(
        data['office'] == 'STATE HOUSE',
        data['district'].replace(house_dict)
        )

    # State Senate is the same. However, we also need the name of the town (precinct) as for a
    # few districts, it is the case that different towns elect different number of state senators
    senate = data[data['office']=='STATE SENATE'][['magnitude', 'district', 'temp_precinct']]
    senate = senate.drop_duplicates().sort_values(['district', 'temp_precinct', 'magnitude'])
    senate['magnitude'] = senate['magnitude'].ffill()
    senate = senate.drop_duplicates()
    senate_dict = senate.set_index(['district', 'temp_precinct']).to_dict()['magnitude']
    senate_dict = {(key[0] + '_' + key[1]): value for key, value in senate_dict.items()}
    data['District_precinct'] = data['district'] + '_' + data['temp_precinct']

    data['magnitude'] = data['magnitude'].mask(
        data['office'] == 'STATE SENATE',
        data['District_precinct'].replace(senate_dict)
        )

    data['magnitude'] = data['magnitude'].astype(int)

    # Now that we no longer need precinct, we can update the floating precincts
    # These happen as a few towns physically located in one county vote for state senator in a
    # neighboring county
    # We use the districts to match, as they are unique
    # floating = {
    #     # Addison
    #     # Huntington is in Chittenden and votes for Addison senator
    #     'WAS-CHI_HUNTINGTON',

    #     # Bennington
    #     # Wilmington is in Windham and votes for Bennington senator
    #     'WDH-6_WILMINGTON',

    #     # Caledonia
    #     # Several towns are in Orange and vote for Caledonia senator
    #     'ORA-2_BRADFORD',
    #     'ORA-2_FAIRLEE',
    #     'ORA-2_WEST FAIRLEE',
    #     'ORA-CAL_NEWBURY',
    #     'ORA-CAL_TOPSHAM',
    #     'ORA-1_ORANGE',

    #     # Chittenden
    #     # -

    #     # Essex-Orleans
    #     # Wolcott is in Lamoille and votes for Essex-Orleans senator
    #     'LAM-2_WOLCOTT',
    #     'FRA-7_MONTGOMERY',
    #     'FRA-5_RICHFORD',

    #     # Franklin
    #     # Alburgh is in Grand Isle and votes for Franklin senator
    #     'GI-CHI_ALBURGH',

    #     # Grand Isle
    #     # Colchester is in Chittenden and votes for Grand Isle senator
    #     'CHI-9-1_COLCHESTER',
    #     'CHI-9-2_COLCHESTER',

    #     # Lamoille
    #     # -

    #     # Orange
    #     # -

    #     # Rutland
    #     # -

    #     # Washington
    #     # -

    #     # Windham
    #     # -

    #     # Windsor
    #     # Londonderry is in Windham and votes for Windsor senator
    #     'WDH-BEN-WDR_LONDONDERRY',
    #     }

    # data['precinct'] = data['temp_precinct'].mask(
    #     (data['office'] == 'STATE SENATE') & (data['District_precinct'].isin(floating)),
    #     data['temp_precinct'] + ' - FLOAT'
    #     )

    print('Parsed VT20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['office'],
        state={
            'STATE HOUSE',
            'STATE SENATE',
            'ATTORNEY GENERAL',
            'AUDITOR OF ACCOUNTS',
            'GOVERNOR',
            'LIEUTENANT GOVERNOR',
            'SECRETARY OF STATE',
            'STATE TREASURER'
            },)

    print('Parsed VT20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed VT20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `stage`...')
    # Stage is consistently general for current data
    data['stage'] = 'GEN'

    print('Parsed VT20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `special`...')

    # # Special is consistently false for current data
    data['special'] = EC.r_bool(False)

    print('Parsed VT20 `special`.')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `writein`...')
    # We parse this from Candidate
    data['writein'] = EC.series_r_bool(data['temp_candidate'].str.contains('WRITE-?IN'))
    data['candidate'] = data['temp_candidate'].replace({
        '\(WRITE-IN\)': ''
        }, regex=True).str.strip()

    print('Parsed VT20 `candidate` (2/2).')
    print('Parsed VT20 `writein`.')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `state_po`...')
    # Already parsed

    print('Parsed VT20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `state_fips`...')
    # Already parsed

    print('Parsed VT20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `state_cen`...')
    # Already parsed

    print('Parsed VT20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `state_ic`...')
    # Already parsed

    print('Parsed VT20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `date...`')

    # Vermont had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed VT20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing VT20 `readme_check...`')

    # # Floating precincts
    # data['readme_check'] = EC.series_r_bool(
    #     data['precinct'].str.contains(' - FLOAT')
    #     )
    data['readme_check'] = 'FALSE'

    print('Parsed VT20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for Vermont.")
    raw_data = load_all_data(prepare_pickle=True)
    print("Parsed VT20 raw data for Vermont.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'Town', 'Rep District', 'Candidate', 'Votes', 'File', 'Magnitude',
                          'Party'},
        )

    data = raw_data.copy()
    # Parse needed details for standard form
    data = make_state(data)
    data = make_precinct(data)
    data = make_office(data)
    data = make_party_detailed(data)
    data = make_party_simplified(data)
    data = make_mode(data)
    data = make_votes(data)
    data = make_county_name(data)
    data = make_county_fips(data)
    data = make_jurisdiction_name(data)
    data = make_jurisdiction_fips(data)
    data = make_candidate(data)
    data = make_district(data)
    data = make_magnitude(data)
    data = make_dataverse(data)
    data = make_year(data)
    data = make_stage(data)
    data = make_special(data)
    data = make_writein(data)
    data = make_state_po(data)
    data = make_state_fips(data)
    data = make_state_cen(data)
    data = make_state_ic(data)
    data = make_date(data)
    data = make_readme_check(data)

    # making new precinct field
    data['precinct'] = data['temp_precinct'] + '_' + data['Rep District']

    data = EC.select_cleaned_dataset_columns(data, False)
    data = EC.sort_cleaned_dataset(data)
    EC.check_cleaned_dataset(data, expected_counties=14, expected_jurisdictions=246)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-vt-precinct-general.csv')
