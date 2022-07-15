import pandas as pd

import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_file(file: str) -> DataFrame:
    data_dict = pd.read_excel(f'raw2/{file}', sheet_name=None, header=[0, 5], skipfooter=3)
    file_data = pd.DataFrame()

    for (county_name, county_data) in data_dict.items():
        if county_name == 'County Results':
            # Ignore county aggregate
            continue
        race = file[:-4].upper()
        if race.startswith('FOR '):
            race = race[4:]

        county_data.columns = [column[1] for column in county_data.columns]
        county_data['County'] = county_name
        county_data['Office'] = race
        county_data = county_data[~(
            (county_data['Precinct'].str.contains('Countywide'))
            & (county_data['TOTALS'] == 0)
            )]
        countywide = county_data[county_data['Precinct'].str.contains('Countywide')].copy()
        if not countywide.empty:
            county_data = countywide
        county_data = county_data.drop(labels='TOTALS', axis=1)
        county_data = county_data.melt(id_vars=['County', 'Precinct', 'Office'],
                                       var_name='Candidate', value_name='Votes')
        county_data['Candidate'] = county_data['Candidate'].str.strip()
        file_data = file_data.append(county_data)

    return file_data


def load_all_data(prepare_pickle=True) -> DataFrame:
    if prepare_pickle:
        data = pd.DataFrame()

        for file in EC.simple_walk(raw_folder='raw2'):
            if file == 'For President and Vice President of the United States.xls':
                # We ignore these, as they are aggregates of the district totals.
                continue

            print(f'*Reading file raw2/{file}...')
            file_data = load_file(file)
            data = data.append(file_data)
            print(f'Read file raw2/{file}...')
        data.reset_index(drop=True).to_pickle('raw_NE20.pkl')

    data = pd.read_pickle('raw_NE20.pkl')
    return data


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `state`...')
    # State is Nebraska by definition
    # This has to be performed first to allow to search county and jurisdiction fips later
    data = EC.state.add_state_codes(data, state='Nebraska')

    print('Parsed NE20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `precinct`...')
    # Data is pulled straight from `Precinct`.
    data['precinct'] = data['Precinct'].str.strip().str.upper()

    # We standardize COUNTYWIDE exactly to COUNTY FLOATING
    data['precinct'] = data['precinct'].replace({
        r'^COUNTYWIDE$': 'COUNTY FLOATING',
        }, regex=True)

    print('Parsed NE20 `precinct`.')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `office`...')

    # Data is pulled from `Office`
    data['temp_office'] = data['Office'].str.upper()

    # Standardize names
    standard_names = {
        r'.*PRESIDENT AND VICE PRESIDENT OF THE UNITED STATES': 'US PRESIDENT',
        r'.*REPRESENTATIVE IN CONGRESS - 2 YEAR TERM': 'US HOUSE',
        r'.*UNITED STATES SENATOR.*': 'US SENATE',
        r'MEMBER OF THE LEGISLATURE': 'STATE SENATE',
        r'AT LARGE FOR ': ' ',
        r'MEMBER OF THE BOARD OF REGENTS ': 'BOARD OF REGENTS - ',
        r'PROPOSED AMENDMENT NO\.': 'PROPOSED AMENDMENT',
        }

    data['temp_office'] = data['temp_office'].replace(standard_names, regex=True)

    offices_with_location = '(' + '|'.join([
        'PUBLIC POWER DISTRICT',
        'PUBLIC POWER AND IRRIGATION DISTRICT',
        'FOR BOARD OF DIRECTORS',
        # For 'MIDDLE REPUBLICAN NATURAL RESOURCES DISTRICT  BOARD OF DIRECTORS - AT LARGE'
        ' BOARD OF DIRECTORS',
        'FOR BOARD OF GOVERNORS',
        # For 'WESTERN COMMUNITY COLLEGE  BOARD OF GOVERNORS - AT LARGE'
        ' BOARD OF GOVERNORS',
        ]) + ')'

    data = EC.adapt_column(
        data,
        'temp_office',
        rf'(?P<location>.*) (?P<office_with_location>{offices_with_location}) (?P<rest>.*)',
        '{office_with_location} - {location} {rest}')

    data['temp_office'] = data['temp_office'].replace({
        'FOR BOARD ': 'BOARD ',
        r'DOUGLAS-SARPY LEARNING COMMUNITY COORDINATING COUNCIL':
            'BOARD MEMBER - DOUGLAS-SARPY LEARNING COMMUNITY COORDINATING COUNCIL',
        r'EDUCATIONAL SERVICE UNIT NO\.': 'BOARD OF EDUCATION - UNIT',
        r'MEMBER OF THE STATE BOARD OF EDUCATION': 'STATE BOARD OF EDUCATION',
        r'^PUBLIC POWER DISTRICT': 'BOARD OF DIRECTORS - PUBLIC POWER DISTRICT',
        r'^PUBLIC POWER AND IRRIGATION DISTRICT':
            'BOARD OF DIRECTORS - PUBLIC POWER AND IRRIGATION DISTRICT',
        r'^LOUP BASIN RECLAMATION DISTRICT':
            'BOARD OF DIRECTORS - LOUP BASIN RECLAMATION DISTRICT',
        r'^METROPOLITAN UTILITIES DISTRICT OF OMAHA':
            'BOARD OF DIRECTORS - METROPOLITAN UTILITIES DISTRICT OF OMAHA',
        r'^TWIN LOUPS RECLAMATION DISTRICT':
            'BOARD OF DIRECTORS - TWIN LOUPS RECLAMATION DISTRICT',
        }, regex=True).str.strip()

    # Make it easier to parse district later on
    data['temp_office'] = data['temp_office'].replace({
        '- AT LARGE$': '- DISTRICT AT LARGE',
        # For 'NORRIS PUBLIC POWER DISTRICT - 6 YEAR TERM - PP1912'
        r'- PP1912': '- SUBDIVISION 012',
        # For 'BOARD OF DIRECTORS - METROPOLITAN UTILITIES DISTRICT OF OMAHA - 6 YEAR TERM - UDMUD',
        r'METROPOLITAN UTILITIES DISTRICT OF OMAHA - 6 YEAR TERM - UDMUD':
            'METROPOLITAN UTILITIES DISTRICT OF OMAHA - 6 YEAR TERM - SUBDIVISION ',
        # For 'SHALL JUDGE DIRK V. BLOCK BE RETAINED IN OFFICE - STATEWIDE' and the like
        r'- STATEWIDE': '- DISTRICT STATEWIDE',
        # For 'SHALL JUDGE MATTHEW R. KAHLER BE RETAINED IN OFFICE - DOUGLAS'
        r'- DOUGLAS$': '- DISTRICT DOUGLAS',
        # For 'SHALL JUDGE LAWRENCE D. GENDLER BE RETAINED IN OFFICE - SARPY',
        r'- SARPY$': '- DISTRICT SARPY',
        }, regex=True)

    data = EC.adapt_column(
        data,
        'temp_office',
        r'(?P<office1>.* TERM -) (?P<office2>.*) SUBDIVISION',
        '{office1} SUBDIVISION {office2}'
        )

    data['temp_office'] = data['temp_office'].replace({
        r'BOARD OF DIRECTORS - PUBLIC POWER AND IRRIGATION DISTRICT':
            'PUBLIC POWER AND IRRIGATION DISTRICT BOARD OF DIRECTORS',
        r'BOARD OF DIRECTORS - PUBLIC POWER DISTRICT':
            'PUBLIC POWER DISTRICT BOARD OF DIRECTORS',
        r'BOARD MEMBER - DOUGLAS-SARPY LEARNING COMMUNITY COORDINATING COUNCIL':
            'LEARNING COMMUNITY COORDINATING COUNCIL BOARD MEMBER - DOUGLAS-SARPY',
        r'BOARD OF DIRECTORS - LOUP BASIN RECLAMATION DISTRICT':
            'RECLAMATION DISTRICT BOARD OF DIRECTORS - LOUP BASIN',
        r'BOARD OF DIRECTORS - METROPOLITAN UTILITIES DISTRICT OF OMAHA':
            'METROPOLITAN UTILITIES DISTRICT BOARD OF DIRECTORS - OMAHA',
        r'BOARD OF DIRECTORS - TWIN LOUPS RECLAMATION DISTRICT':
            'RECLAMATION DISTRICT BOARD OF DIRECTORS - TWIN LOUPS',
        }, regex=True)

    data = EC.adapt_column(
        data,
        'temp_office',
        r'(?P<office1>BOARD OF DIRECTORS - .*) NATURAL RESOURCES DISTRICT(?P<office2>.*)',
        'NATURAL RESOURCES DISTRICT {office1}{office2}'
        )

    # Offices still contain term information, which is used to distinguish special elections
    # We will get rid of those later.
    print('Partially parsed NE20 `office` (1/2).')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `party_detailed...`')
    # Nebraska does not provide party information, for most of the races are nonpartisan.

    data['party_detailed'] = 'NONPARTISAN'

    # Except for a few races. Party affiliation is deduced from the
    # Secretary of State general election canvass at
    # https://sos.nebraska.gov/sites/sos.nebraska.gov/files/doc/elections/2020/2020-General-Canvass-Book.pdf

    party_affiliation = {
        # US PRESIDENT
        'Joseph R. Biden and Kamala D. Harris': 'DEMOCRAT',
        'Donald J. Trump and Michael R. Pence': 'REPUBLICAN',
        'Jo Jorgensen and Jeremy Cohen': 'LIBERTARIAN',

        # US SENATE
        'Gene Siadek': 'LIBERTARIAN',
        'Ben Sasse': 'REPUBLICAN',
        'Chris Janicek': 'DEMOCRAT',

        # US HOUSE
        'Kate Bolz': 'DEMOCRAT',
        'Jeff Fortenberry': 'REPUBLICAN',
        'Dennis B. Grace': 'LIBERTARIAN',
        'Donald Bacon': 'REPUBLICAN',
        'Kara Eastman': 'DEMOCRAT',
        'Tyler Schaeffer': 'LIBERTARIAN',
        'Adrian Smith': 'REPUBLICAN',
        'Mark Elworth Jr.': 'DEMOCRAT',
        'Dustin C. Hobbs': 'LIBERTARIAN',

        # Public Service Commissioner
        'Tim Davis': 'REPUBLICAN',
        'Crystal Rhoades': 'DEMOCRAT',
        }

    data['party_detailed'] = data['party_detailed'].mask(
        data['Candidate'].isin(party_affiliation),
        data['Candidate'].replace(party_affiliation),
        )

    print('Parsed NE20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `party_simplified...`')
    # We can use the details from the recently parsed NE20 party_detailed for this.
    data['party_simplified'] = data['party_detailed']

    print('Parsed NE20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `mode`...')
    # All vote totals are TOTAL
    data['mode'] = 'TOTAL'

    print('Parsed NE20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    print('Parsed NE20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `county_name`...')
    # Data is pulled straight from `County` and upper cased
    data['county_name'] = data['County'].str.upper()

    print('Parsed NE20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    data['county_fips'] = EC.county_fips.parse_fips_from_name(data)

    print('Parsed NE20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `jurisdiction_name`...')
    # `jurisdiction_name` is the same as `county_name` for Nebraska, so use that
    data['jurisdiction_name'] = data['county_name']

    print('Parsed NE20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `jurisdiction_fips`...')
    # `jurisdiction_fips` is the same as `county_fips` for Nebraska, so use that
    data['jurisdiction_fips'] = data['county_fips']

    print('Parsed NE20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['candidate'] = data['Candidate'].str.upper()

    # Recover judicial retention race candidates first
    data['judicial_candidate'] = data['temp_office'].str.extract(
        r'SHALL JUDGE (.*) BE RETAINED IN OFFICE',
        expand=False)

    data['candidate'] = data['candidate'].mask(
        ~data['judicial_candidate'].isna(),
        data['judicial_candidate'] + ' - ' + data['candidate']
        )

    # With that information, we can cleanup retention offices
    # Source:
    # https://sos.nebraska.gov/sites/sos.nebraska.gov/files/doc/elections/2020/FINAL-Judges-List-9-11-2020.pdf
    raw_retention_offices = {
        # Supreme Court
        r'LINDSEY MILLER-LERMAN': 'RETENTION SUPREME COURT',
        r'JEFFREY J\. FUNKE': 'RETENTION SUPREME COURT',

        # Court of Appeals
        r'MICHAEL W\. PIRTLE': 'RETENTION COURT OF APPEALS',
        r'DAVID K\. ARTERBURN': 'RETENTION COURT OF APPEALS',

        # Nebraska Workers' Compensation Court
        r'THOMAS E\. STINE': "RETENTION WORKERS' COMPENSATION COURT",
        r'DIRK V\. BLOCK': "RETENTION WORKERS' COMPENSATION COURT",

        # District Court
        r'JULIE D\. SMITH': 'RETENTION DISTRICT COURT',
        r'RICK SCHREINER': 'RETENTION DISTRICT COURT',
        r'STEFANIE A\. MARTINEZ': 'RETENTION DISTRICT COURT',
        r'MICHAEL A\. SMITH': 'RETENTION DISTRICT COURT',
        r'GEORGE A\. THOMPSON': 'RETENTION DISTRICT COURT',
        r'ANDREW R\. JACOBSEN': 'RETENTION DISTRICT COURT',
        r'KEVIN R\. MCMANAMAN': 'RETENTION DISTRICT COURT',
        r'DARLA S\. IDEUS': 'RETENTION DISTRICT COURT',
        r'TIMOTHY P\. BURNS': 'RETENTION DISTRICT COURT',
        r'MARLON A\. POLK': 'RETENTION DISTRICT COURT',
        r'J\. MICHAEL COFFEY': 'RETENTION DISTRICT COURT',
        r'DUANE C\. DOUGHERTY': 'RETENTION DISTRICT COURT',
        r'GARY B\. RANDALL': 'RETENTION DISTRICT COURT',
        r'GEOFFREY C\. HALL': 'RETENTION DISTRICT COURT',
        r'MARK D\. KOZISEK': 'RETENTION DISTRICT COURT',
        r'JOHN H\. MARSH': 'RETENTION DISTRICT COURT',
        r'TERRI S\. HARDER': 'RETENTION DISTRICT COURT',
        r'RICHARD A\. BIRCH': 'RETENTION DISTRICT COURT',
        r"TRAVIS P\. O'GORMAN": 'RETENTION DISTRICT COURT',
        r'ANDREA D\. MILLER': 'RETENTION DISTRICT COURT',

        # Separate Juvenile Court
        r'MATTHEW R\. KAHLER': 'RETENTION SEPARATE JUVENILE COURT',
        r'LAWRENCE D\. GENDLER': 'RETENTION SEPARATE JUVENILE COURT',

        # County Court
        r'CURTIS L\. MASCHMAN': 'RETENTION COUNTY COURT',
        r'TRICIA A\. FREEMAN': 'RETENTION COUNTY COURT',
        r'TODD J\. HUTTON': 'RETENTION COUNTY COURT',
        r'RODNEY D\. REUTER': 'RETENTION COUNTY COURT',
        r'DARRYL R\. LOWE': 'RETENTION COUNTY COURT',
        r'STEPHANIE STEIGLEDER SHEARER': 'RETENTION COUNTY COURT',
        r'CRAIG Q\. MCDERMOTT': 'RETENTION COUNTY COURT',
        r'SHERYL L\. LOHAUS': 'RETENTION COUNTY COURT',
        r'MARCELA A\. KEIM': 'RETENTION COUNTY COURT',
        r'MARCENA M\. HENDRIX': 'RETENTION COUNTY COURT',
        r'JOHN E\. HUBER': 'RETENTION COUNTY COURT',
        r'KENNETH J\. VAMPOLA': 'RETENTION COUNTY COURT',
        r'KALE B\. BURDICK': 'RETENTION COUNTY COURT',
        r'ALFRED E\. COREY III': 'RETENTION COUNTY COURT',
        r'ARTHUR S\. WETZEL': 'RETENTION COUNTY COURT',
        r'MICHAEL P\. BURNS': 'RETENTION COUNTY COURT',
        r'EDWARD D\. STEENBURG': 'RETENTION COUNTY COURT',
        r'KENT D\. TURNBULL': 'RETENTION COUNTY COURT',
        r'KRISTEN MICKEY': 'RETENTION COUNTY COURT',
        r'JAMES M\. WORDEN': 'RETENTION COUNTY COURT',
        }

    retention_offices = {
        r'SHALL JUDGE ' + key + ' BE RETAINED IN OFFICE': value
        for (key, value) in raw_retention_offices.items()
        }

    data['temp_office'] = data['temp_office'].replace(retention_offices, regex=True)

    # First, remove any extraneous whitespace/characters
    data['candidate'] = data['candidate'].str.strip().replace({
        r' ( )+': ' ',
        r'\.': '',
        }, regex=True)

    # For presidential candidates, we just record the president's name
    data['candidate'] = data['candidate'].replace({
        'JOSEPH R BIDEN AND KAMALA D HARRIS': 'JOSEPH R BIDEN',
        'JO JORGENSEN AND JEREMY COHEN': 'JO JORGENSEN',
        'DONALD J TRUMP AND MICHAEL R PENCE': 'DONALD J TRUMP',
        })

    print('Parsed NE20 `candidate`.')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `district`...')

    district_markers = '(' + '|'.join([
        'DISTRICT',
        'CONGRESSIONAL DISTRICT',
        'SUBDISTRICT',
        'SUBDIVISION',
        ]) + ')'

    data = EC.split_column(
        data,
        'temp_office',
        rf'(?P<temp_office>.*) - {district_markers} (?P<district>.*)',
        maintaining_columns=['temp_office'],
        empty_value='')

    data['district'] = EC.district.mark_statewide_districts(
        data['district'], data['temp_office'], [
            'US SENATE',
            'PROPOSED AMENDMENT 1',
            'PROPOSED AMENDMENT 2',
            'INITIATIVE MEASURE 428',
            'INITIATIVE MEASURE 429',
            'INITIATIVE MEASURE 430',
            'INITIATIVE MEASURE 431',
        ])

    data['district'] = EC.district.fix_numerical_districts(data['district'])

    data = EC.split_column(
        data,
        'temp_office',
        r'(?P<temp_office>BOARD OF EDUCATION)(?P<discard> - )(?P<unit>UNIT.*)',
        maintaining_columns=['temp_office'],
        )

    data['district'] = data['district'].mask(
        ~data['unit'].isna(),
        data['unit'] + ', ' + data['district']
        )

    print('Parsed NE20 `district`.')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `magnitude`...')

    data['magnitude'] = 1
    # Magnitude is consistently 1 except for a few at large offices. We handle those now.
    # Source
    # https://sos.nebraska.gov/sites/sos.nebraska.gov/files/doc/elections/2020/2020-General-Canvass-Book.pdf
    offices_with_magnitude = {
        'PUBLIC POWER DISTRICT BOARD OF DIRECTORS - BURT COUNTY - 6 YEAR TERM': 2,
        'PUBLIC POWER DISTRICT BOARD OF DIRECTORS - CHIMNEY ROCK - 6 YEAR TERM': 2,
        'PUBLIC POWER DISTRICT BOARD OF DIRECTORS - CUSTER - 6 YEAR TERM': 2,
        'PUBLIC POWER DISTRICT BOARD OF DIRECTORS - LOUP VALLEYS RURAL - 6 YEAR TERM': 3,
        }

    data['magnitude'] = data['magnitude'].mask(
        data['temp_office'].isin(offices_with_magnitude),
        data['temp_office'].replace(offices_with_magnitude, regex=True)
        )

    print('Parsed NE20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['temp_office'],
        state={
            'BOARD OF REGENTS - UNIVERSITY OF NEBRASKA',
            'PROPOSED AMENDMENT 1',
            'PROPOSED AMENDMENT 2',
            'INITIATIVE MEASURE 428',
            'INITIATIVE MEASURE 429',
            'INITIATIVE MEASURE 430',
            'INITIATIVE MEASURE 431',
            'PUBLIC SERVICE COMMISSIONER',
            'RETENTION SUPREME COURT',
            'RETENTION COURT OF APPEALS',
            'RETENTION DISTRICT COURT',
            'STATE BOARD OF EDUCATION',
            'STATE SENATE',
            })

    print('Parsed NE20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed NE20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `stage`...')
    # Stage is consistently general for current data
    data['stage'] = 'GEN'

    print('Parsed NE20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `special`...')

    # Only a few elections are special
    special_offices = {
        'NATURAL RESOURCES DISTRICT BOARD OF DIRECTORS - CENTRAL PLATTE - 2 YEAR TERM',
        'NATURAL RESOURCES DISTRICT BOARD OF DIRECTORS - LOWER BIG BLUE - 2 YEAR TERM',
        'NATURAL RESOURCES DISTRICT BOARD OF DIRECTORS - NEMAHA - 2 YEAR TERM',
        'PUBLIC POWER DISTRICT BOARD OF DIRECTORS - ELKHORN RURAL - 2 YEAR TERM',
        'PUBLIC POWER DISTRICT BOARD OF DIRECTORS - TWIN VALLEYS',  # 2 YEAR TERM
        }

    data['special'] = EC.series_r_bool(data['temp_office'].isin(special_offices))

    data['office'] = data['temp_office'].replace({
        ' - 2 YEAR TERM': '',
        ' - 4 YEAR TERM': '',
        ' - 6 YEAR TERM': '',
        }, regex=True)

    print('Parsed NE20 `office` (2/2).')
    print('Parsed NE20 `special`.')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `writein`...')
    # The Nebraska data does not indicate writeins
    data['writein'] = EC.r_bool(False)

    print('Parsed NE20 `writein`.')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `state_po`...')
    # Already parsed

    print('Parsed NE20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `state_fips`...')
    # Already parsed

    print('Parsed NE20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `state_cen`...')
    # Already parsed

    print('Parsed NE20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `state_ic`...')
    # Already parsed

    print('Parsed NE20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `date...`')

    # Nebraska had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed NE20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing NE20 `readme_check...`')

    # No particular remarks about data completeness
    data['readme_check'] = EC.r_bool(False)

    print('Parsed NE20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for Nebraska.")
    raw_data = load_all_data(prepare_pickle=True)
    print("Parsed NE20 raw data for Nebraska.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'County', 'Precinct', 'Office', 'Candidate', 'Votes'},
        county_column='County', expected_counties=93
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

    # raw data contains duplicate precincts within counties...
    # However, the duplicates are always 0 votes. Dropping near duplicates with 0 votes removes...
    # all near duplicates in the state.
    data = data[~((data.drop(columns = 'votes').duplicated(keep = False))&(data['votes']==0))].copy()

    data = EC.sort_cleaned_dataset(data)
    EC.check_cleaned_dataset(data, expected_counties=93, expected_jurisdictions=93)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-ne-precinct-general.csv')
