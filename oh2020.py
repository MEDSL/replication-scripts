import pandas as pd
import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_nonlocal_file() -> DataFrame:
    file = 'raw/statewideresultsbyprecinct.xlsx'
    print(f'*Reading file {file}...')
    data = pd.read_excel(file, sheet_name="Master", header=[0, 1], skiprows=[2, 3])
    # Remove WRITEIN from this file as they contain nothing
    data = data[[column for column in data.columns if '(WI)' not in column[1]]]

    STR = ('November 3, 2020 General Election Official Canvass\nAll Member of the State Board of '
           'Education, Justice of the Supreme Court and Judge of the Court of Appeals races are '
           'non-partisan.\n*Write-in candidates will be displayed with a (WI) designation and not '
           'party affiliation.\n*Precinct-level data is not available for write-in candidates. To '
           'view results for write-in candidates, download the Summary-level spreadsheet.')
    variables = [(STR, 'County Name'), (STR, 'Precinct Name'), (STR, 'Precinct Code'),
                 (STR, 'Region Name'), (STR, 'Media Market'), (STR, 'Registered Voters'),
                 (STR, 'Ballots Counted'), (STR, 'Official Voter Turnout')]
    data = pd.melt(data, id_vars=variables)
    data = data.rename(columns={
        (STR, 'County Name'): 'County',
        (STR, 'Precinct Name'): 'Precinct',
        (STR, 'Precinct Code'): 'Precinct Code',
        (STR, 'Region Name'): 'Region Name',
        (STR, 'Media Market'): 'Media Market',
        (STR, 'Registered Voters'): 'Registered Voters',
        (STR, 'Ballots Counted'): 'Ballots Counted',
        (STR, 'Official Voter Turnout'): 'Official Voter Turnout',
        'variable_0': 'Office',
        'variable_1': 'Candidate/Party',
        'value': 'Votes',
        })

    # Discard trivial 0 votes (and non-trivial ones).
    # Ohio lists 0 votes for candidates that did not run in a particular district, which if left
    # untreated, yields millions of records records; which is too much
    # We will remove offices that indicate county name where they do not correspond to the
    # actual county.

    data = data[((data['Office'] == 'President and Vice-President\n') |
                 # (data['Office'].str.contains('County')) |
                 (data['Votes'] > 0))].reset_index(drop=True)

    # Fix Registered Voters and Ballots Counted so they are proper records.
    data = data[['County', 'Precinct', 'Registered Voters', 'Ballots Counted',
                 'Office', 'Candidate/Party', 'Votes']]

    data1 = data[['County', 'Precinct', 'Office', 'Candidate/Party', 'Votes']]
    data2 = data[['County', 'Precinct', 'Registered Voters',
                  'Ballots Counted']].drop_duplicates()
    data2 = pd.melt(data2, id_vars=['County', 'Precinct'],
                    var_name='Office', value_name='Votes')
    data2['Candidate/Party'] = ''
    data2 = data2[['County', 'Precinct', 'Office', 'Candidate/Party', 'Votes']]

    data = data1.append(data2)
    print(f'Read file {file}.')

    return data


def load_local_file() -> DataFrame:
    file = 'raw/CountyRaceResultsByPrecinct.xlsx'
    print(f'*Reading file {file}...')

    # This line alone took 4 minutes in my machine. You better have a good reason to run this.
    data = pd.read_excel(file, sheet_name="Master", header=[0, 1], skiprows=[2, 3])
    STR = ('November 3, 2020 General Election Official Canvass\nAll Judge of the Court of Common '
           'Pleas and Judge of the County Court races are non-partisan.\n*Write-in candidates will '
           'be displayed with a (WI) designation and not party affiliation.\n*Precinct-level data '
           'is not available for write-in candidates. To view results for write-in candidates, '
           'download the Summary-level spreadsheet.')
    variables = [(STR, 'County Name'), (STR, 'Precinct Name'), (STR, 'Precinct Code'),
                 (STR, 'Region Name'), (STR, 'Media Market'), (STR, 'Registered Voters'),
                 (STR, 'Ballots Counted'), (STR, 'Official Voter Turnout')]

    # Remove WRITEIN from this file as they contain nothing
    data = data[[column for column in data.columns if '(WI)' not in column[1]]]
    data = pd.melt(data, id_vars=variables)
    data = data.rename(columns={
        (STR, 'County Name'): 'County',
        (STR, 'Precinct Name'): 'Precinct',
        (STR, 'Precinct Code'): 'Precinct Code',
        (STR, 'Region Name'): 'Region Name',
        (STR, 'Media Market'): 'Media Market',
        (STR, 'Registered Voters'): 'Registered Voters',
        (STR, 'Ballots Counted'): 'Ballots Counted',
        (STR, 'Official Voter Turnout'): 'Official Voter Turnout',
        'variable_0': 'Office',
        'variable_1': 'Candidate/Party',
        'value': 'Votes',
        })

    data = data[['County', 'Precinct', 'Office', 'Candidate/Party', 'Votes']]
    # We will remove offices that indicate county name where they do not correspond to the
    # actual county.
    data['office_county'] = data['Office'].str.extract('(.* )([A-Za-z]+)( County.*)')[1]
    data = data[((data['office_county'].isna()) |
                 (data['office_county'] == data['County']))].reset_index(drop=True)

    data = data.drop(labels='office_county', axis=1)
    data = EC.adapt_column(data, 'Office',
                           '(?P<name1>.*) - (?P<County>.*) County\n?(?P<name2>.+)',
                           '{name1}: {name2}')
    data = EC.adapt_column(data, 'Office',
                           '(?P<name1>.*) - (?P<County>.*) County\n',
                           '{name1}')
    print(f'Read file {file}.')
    return data


def load_nonlocal_writein_file() -> DataFrame:
    # We use the county file to recover aggregate writein results
    file = 'raw/statewideresultsbycounty.xlsx'
    print(f'*Reading file {file}...')
    data = pd.read_excel(file, sheet_name="Master", header=[0, 1], skiprows=[2, 3])
    # Remove WRITEIN from this file as they contain nothing
    data = data[[column for column in data.columns if '(WI)' in column[1] or 'Nov' in column[0]]]

    STR = ('November 3, 2020 General Election Official Canvass\nAll Member of the State Board of '
           'Education, Justice of the Supreme Court and Judge of the Court of Appeals races are '
           'non-partisan.\n*Write-in candidates will be displayed with a (WI) designation and not '
           'party affiliation.')
    variables = [(STR, 'County Name'), (STR, 'Region Name'), (STR, 'Media Market'),
                 (STR, 'Registered Voters'), (STR, 'Ballots Counted'),
                 (STR, 'Official Voter Turnout')]

    data = pd.melt(data, id_vars=variables)
    data = data.rename(columns={
        (STR, 'County Name'): 'County',
        (STR, 'Precinct Name'): 'Precinct',
        (STR, 'Precinct Code'): 'Precinct Code',
        (STR, 'Region Name'): 'Region Name',
        (STR, 'Media Market'): 'Media Market',
        (STR, 'Registered Voters'): 'Registered Voters',
        (STR, 'Ballots Counted'): 'Ballots Counted',
        (STR, 'Official Voter Turnout'): 'Official Voter Turnout',
        'variable_0': 'Office',
        'variable_1': 'Candidate',
        'value': 'Votes',
        })

    data = data[['County', 'Office', 'Votes']]
    data = data.groupby(['County', 'Office']).sum().reset_index()
    data['Candidate/Party'] = 'WRITEIN (NP)'
    data['Precinct'] = 'COUNTY FLOATING'
    print(f'Read file {file}.')

    return data


def load_local_writein_file() -> DataFrame:
    # We use the county file to recover aggregate writein results
    file = 'raw/countyracebycounty.xlsx'
    print(f'*Reading file {file}...')
    data = pd.read_excel(file, sheet_name="Master", header=[0, 1], skiprows=[2, 3])
    # Remove WRITEIN from this file as they contain nothing
    data = data[[column for column in data.columns if '(WI)' in column[1] or 'Nov' in column[0]]]
    STR = ('November 3, 2020 General Election Official Canvass\nAll Judge of the Court of Common '
           'Pleas and Judge of the County Court races are non-partisan.\n*Write-in candidates will '
           'be displayed with a (WI) designation and not party affiliation.')
    variables = [(STR, 'County Name'), (STR, 'Region Name'), (STR, 'Media Market'),
                 (STR, 'Registered Voters'), (STR, 'Ballots Counted'),
                 (STR, 'Official Voter Turnout')]

    data = pd.melt(data, id_vars=variables)
    data = data.rename(columns={
        (STR, 'County Name'): 'County',
        (STR, 'Precinct Name'): 'Precinct',
        (STR, 'Precinct Code'): 'Precinct Code',
        (STR, 'Region Name'): 'Region Name',
        (STR, 'Media Market'): 'Media Market',
        (STR, 'Registered Voters'): 'Registered Voters',
        (STR, 'Ballots Counted'): 'Ballots Counted',
        (STR, 'Official Voter Turnout'): 'Official Voter Turnout',
        'variable_0': 'Office',
        'variable_1': 'Candidate',
        'value': 'Votes',
        })

    data = data[['County', 'Office', 'Votes']]
    data = data.groupby(['County', 'Office']).sum().reset_index()
    data['Candidate/Party'] = 'WRITEIN (NP)'
    data['Precinct'] = 'COUNTY FLOATING'
    # We will remove offices that indicate county name where they do not correspond to the
    # actual county.
    data['office_county'] = data['Office'].str.extract('(.* )([A-Za-z]+)( County.*)')[1]
    data = data[((data['office_county'].isna()) |
                 (data['office_county'] == data['County']))].reset_index(drop=True)

    data = data.drop(labels='office_county', axis=1)
    data = EC.adapt_column(data, 'Office',
                           '(?P<name1>.*) - (?P<County>.*) County\n?(?P<name2>.+)',
                           '{name1}: {name2}')
    data = EC.adapt_column(data, 'Office',
                           '(?P<name1>.*) - (?P<County>.*) County\n',
                           '{name1}')
    data = data[['County', 'Precinct', 'Office', 'Candidate/Party', 'Votes']]

    print(f'Read file {file}.')

    return data


def load_all_data(prepare_pickle=True) -> DataFrame:
    if prepare_pickle:
        # WARNING! SLOW!!!!
        data = pd.DataFrame()
        for func in [load_nonlocal_file,
                     load_nonlocal_writein_file,
                     load_local_file,
                     load_local_writein_file]:
            file_data = func()
            data = data.append(file_data).reset_index(drop=True)
        data.to_pickle('raw_OH20.pkl')

    data = pd.read_pickle('raw_OH20.pkl')
    return data


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `state`...')
    # State is Ohio by definition
    # This has to be performed first to allow to search county and jurisdiction fips later
    data = EC.state.add_state_codes(data, state='Ohio')

    print('Parsed OH20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `precinct`...')
    # Data is pulled straight from `Precinct`.
    data['precinct'] = data['Precinct'].str.strip().str.upper()
    print('Parsed OH20 `precinct`.')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `office`...')

    # Data is pulled from `Office`
    data['temp_office'] = data['Office'].str.upper().astype(str).str.replace('\n', '')

    # Standardize names
    standard_names = {
        r'PRESIDENT.*': 'US PRESIDENT',
        r'REPRESENTATIVE TO CONGRESS': 'US HOUSE',
        r'STATE SENATOR': 'STATE SENATE',
        r'STATE REPRESENTATIVE': 'STATE HOUSE',
        r'SHERIFF': 'COUNTY SHERIFF',
        r'CORONER': 'COUNTY CORONER',
        r'COUNTY COUNCIL DISTRICT': 'COUNTY COUNCIL - DISTRICT',  # Helps with regex later
        }

    data['temp_office'] = data['temp_office'].replace(standard_names, regex=True)

    # For a lot of of offices there is a term commencing/ending date. It used to be separated by a
    # newline, but that was removed earlier. Add a colon+space to separate for now
    data['temp_office'] = data['temp_office'].replace({
        '(?<!: )TERM COMMENCING': ': TERM COMMENCING',
        '(?<!: )UNEXPIRED TERM ENDING': ': UNEXPIRED TERM ENDING',
        }, regex=True)

    print('Parsed OH20 `temp_office`.')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `party_detailed...`')
    # Data is pulled from `Candidate/Party`, upper-cased, and standardizing party names
    data['party_detailed'] = data['Candidate/Party']

    # Standardize names
    standard_names = {
        '(D)': 'DEMOCRAT',
        '(R)': 'REPUBLICAN',
        '(L)': 'LIBERTARIAN',
        '(NP)': 'NONPARTISAN'
        }

    def build_party(candidateparty: str) -> str:
        for (abbreviation, party) in standard_names.items():
            if abbreviation in candidateparty:
                return party
        return 'NONPARTISAN'

    data['party_detailed'] = data['party_detailed'].apply(build_party)

    # Make writeins be empty
    data['party_detailed'] = data['party_detailed'].mask(
        data['Candidate/Party'] == 'WRITEIN (NP)', '')

    print('Parsed OH20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `party_simplified...`')
    # We can use the details from the recently parsed OH20 party_detailed for this.
    data['party_simplified'] = data['party_detailed']

    print('Parsed OH20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `mode`...')
    # All vote totals are TOTAL
    data['mode'] = 'TOTAL'

    print('Parsed OH20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    print('Parsed OH20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `county_name`...')
    # Data is pulled straight from `County` and upper cased
    data['county_name'] = data['County'].str.upper()

    print('Parsed OH20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    fips = pd.read_csv(r"..\..\help-files\county-fips-codes.csv")
    fips['state'] = fips['state'].str.upper()
    data = data.join(fips.set_index(['state', 'county_name']), on=['state', 'county_name'],
                     how="left")
    data['county_fips'] = data['county_fips'].astype(int, errors='raise')  # Force int

    print('Parsed OH20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `jurisdiction_name`...')
    # `jurisdiction_name` is the same as `county_name` for Ohio, so use that
    data['jurisdiction_name'] = data['county_name']

    print('Parsed OH20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `jurisdiction_fips`...')
    # `jurisdiction_fips` is the same as `county_fips` for Ohio, so use that
    data['jurisdiction_fips'] = data['county_fips']

    print('Parsed OH20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['candidate'] = data['Candidate/Party'].str.upper()

    # First, remove any extraneous whitespace/characters
    data['candidate'] = data['candidate'].str.strip().replace({
        r' ( )+': ' ',
        r'\.': '',
        }, regex=True)

    # Now, trim party affiliation from the end
    data['candidate'] = data['candidate'].replace({
        r' \(D\)': '',
        r' \(R\)': '',
        r' \(L\)': '',
        r' \(NP\)': '',
        }, regex=True)

    # For presidential candidates, we just record the president's name
    data['candidate'] = data['candidate'].replace({
        'JOSEPH R BIDEN AND KAMALA D HARRIS': 'JOSEPH R BIDEN',
        'JO JORGENSEN AND SPIKE COHEN': 'JO JORGENSEN',
        'HOWIE HAWKINS AND ANGELA WALKER': 'HOWIE HAWKINS',
        'DONALD J TRUMP AND MICHAEL R PENCE': 'DONALD J TRUMP',
        })

    print('Parsed OH20 `candidate`...')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `district`...')

    # Extract district information from `temp_office`
    regex = '(?P<temp_office1>.*) - DISTRICT (?P<district>[0-9]+)(?P<temp_office2>.*)'

    data = EC.split_column(data, 'temp_office',
                           regex,
                           maintaining_columns=['temp_office'], empty_value='')
    data = EC.merge_columns(data, 'temp_office_merged', '{temp_office1}{temp_office2}')
    # At this point we are done modifying office
    data['office'] = EC.left_merge_series([data['temp_office'], data['temp_office_merged']], {''})

    data['district'] = EC.district.mark_statewide_districts(
        data['district'], data['office'], [
            'PRESIDENT',
            'JUSTICE OF THE SUPREME COURT',
        ])

    data['district'] = EC.district.fix_numerical_districts(data['district'])

    print('Parsed OH20 `office` (3/3).')
    print('Parsed OH20 `district`.')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `magnitude`...')

    # Magnitude is 1 except for statistics
    data['magnitude'] = EC.iif(data['office'], lambda series: series.isin({
        'BALLOTS COUNTED',
        'REGISTERED VOTERS',
        }), 0, 1)

    print('Parsed OH20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['office'],
        state={
            'JUSTICE OF THE SUPREME COURT',
            'JUDGE OF THE COURT OF APPEALS',
            'MEMBER OF THE STATE BOARD OF EDUCATION',
            'STATE HOUSE',
            'STATE SENATE',
            'CLERK OF THE COURT OF COMMON PLEAS',
            },
        empty={
            'REGISTERED VOTERS',
            'BALLOTS COUNTED',
            })
    # Manually do this case because there are so many
    data['dataverse'] = data['dataverse'].mask(
        data['office'].str.contains('JUDGE OF THE COURT OF COMMON PLEAS'),
        'STATE')
    print('Parsed OH20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed OH20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `stage`...')
    # Stage is consistently general for current data
    data['stage'] = 'GEN'

    print('Parsed OH20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `special`...')

    # Unexpired elections are special. Those are the only special elections.
    data['special'] = EC.series_r_bool(data['office'].str.contains('UNEXPIRED'))

    print('Parsed OH20 `special`.')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `writein`...')
    # The Ohio data indicates this in the candidate field
    data['writein'] = EC.series_r_bool(data['candidate'] == 'WRITEIN')

    print('Parsed OH20 `writein`.')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `state_po`...')
    # Already parsed

    print('Parsed OH20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `state_fips`...')
    # Already parsed

    print('Parsed OH20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `state_cen`...')
    # Already parsed

    print('Parsed OH20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `state_ic`...')
    # Already parsed

    print('Parsed OH20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `date...`')

    # Ohio had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed OH20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing OH20 `readme_check...`')

    data['readme_check'] = EC.series_r_bool(
        # Remarks about vote drops
        (data['office'] != 'US PRESIDENT') |
        # Writeins are county aggregates
        (data['candidate'] == 'WRITEIN')
        )

    print('Parsed OH20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for Ohio.")
    raw_data = load_all_data(prepare_pickle=True)
    print("Parsed OH20 raw data for Ohio.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'County', 'Precinct', 'Office', 'Candidate/Party', 'Votes'},
        county_column='County', expected_counties=88
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

    data = EC.select_cleaned_dataset_columns(data, False)
    data = EC.sort_cleaned_dataset(data)
    EC.check_cleaned_dataset(data, expected_counties=88, expected_jurisdictions=88)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-oh-precinct-general.csv')
