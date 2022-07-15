import os

import pandas as pd
import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_file(file: str) -> DataFrame:
    data_dict = pd.read_excel(file, sheet_name=None, header=6, skipfooter=1)
    file_data = pd.DataFrame()

    for (county_name, county_data) in data_dict.items():
        race = county_data.columns[0]
        county_data = county_data.drop(labels=race, axis=1)
        county_data = county_data.melt(id_vars=['Precinct'],
                                       var_name='Candidate', value_name='Votes')
        county_data['County'] = file[4:-13]
        county_data['Office'] = race
        county_data['Candidate'] = county_data['Candidate'].str.strip()
        county_data = EC.split_column(county_data, 'Candidate',
                                      r'(?P<Candidate>.*)\n(?P<Party>.*)',
                                      maintaining_columns=['Candidate'],
                                      empty_value='NONPARTISAN',)

        file_data = file_data.append(county_data)

    return file_data


def load_all_data(prepare_pickle=True) -> DataFrame:
    if prepare_pickle:
        data = pd.DataFrame()

        for (_, _, files) in os.walk(os.getcwd()+'/raw'):
            for file in files:
                if '~' in file:
                    continue
                if not file.endswith('Results.xlsx'):
                    continue
                print(f'*Reading file raw/{file}...')
                file_data = load_file(f'raw/{file}')
                data = data.append(file_data)
                print(f'Read file raw/{file}...')
        data = data.reset_index(drop=True)
        data.to_pickle('raw_MT20.pkl')

    data = pd.read_pickle('raw_MT20.pkl')
    return data


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `state`...')
    # State is Montana by definition
    data = EC.state.add_state_codes(data, state='Montana')

    print('Parsed MT20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `precinct`...')
    # Data is pulled straight from `Precinct`.
    data['precinct'] = data['Precinct'].astype(str).str.strip().str.upper()
    print('Parsed MT20 `precinct`.')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `office`...')

    # Data is pulled from `Office`
    data['temp_office'] = data['Office'].str.upper()

    # First, remove any extraneous whitespace/characters
    data['temp_office'] = data['temp_office'].str.strip().replace({
        r' ( )+': ' ',
        r' -': '-',
        r'\.': '',
        r'/ ': '/',
        r'&': 'AND',
        }, regex=True)

    # Standardize names
    standard_names = {
        r'PRESIDENT': 'US PRESIDENT',
        r'UNITED STATES SENATOR.*': 'US SENATE',
        r'UNITED STATES REPRESENTATIVE': 'US HOUSE',
        r'GOVERNOR AND LT GOVERNOR': 'GOVERNOR AND LIEUTENANT GOVERNOR',
        r'STATE REPRESENTATIVE': 'STATE HOUSE',
        r'STATE SENATOR': 'STATE SENATE',
        r'.*\nCHIEF': 'COUNTY CHIEF',
        r'.*\nCLERK': 'COUNTY CLERK',
        r'^CLERK OF THE DISTRICT COURT': 'COUNTY CLERK OF THE DISTRICT COURT',
        r'.*\nCOMMUNITY COUNCIL': 'COUNTY COMMUNITY COUNCIL',
        r'.*\nCORONER': 'COUNTY CORONER',
        r'.*\nJUSTICE OF THE PEACE': 'COUNTY JUSTICE OF THE PEACE',
        r'.*\nPUBLIC ADMINISTRATOR': 'COUNTY PUBLIC ADMINISTRATOR',
        r'.*\nSHERIFF': 'SHERIFF',
        r'.*\nCOUNTY': 'COUNTY',
        r'\nFLATHEAD COUNTY': 'COUNTY',
        r'^COMMISSIONER': 'COUNTY COMMISSIONER',
        r'AREA SUPERVISOR': 'COUNTY AREA SUPERVISOR',
        r'UNEXPIRED TWO YEAR TERM': '2 YEAR TERM UNEXPIRED TERM',
        r'DEPT': 'DEPARTMENT',
        }

    data['temp_office'] = data['temp_office'].replace(standard_names, regex=True)

    # More standardization
    standard_districts = {
        r'DIST #[ ]?': 'DISTRICT ',
        r'\nDISTRICT ': ' DISTRICT ',
        r'DISTRICT #[ ]?': 'DISTRICT ',
        r'DISTRICT NO ': 'DISTRICT ',
        r'DIST ': 'DISTRICT ',
        }

    data['temp_office'] = data['temp_office'].replace(standard_districts, regex=True)

    # Remove County labels
    data['temp_office'] = data['temp_office'].replace({
        '.* COUNTY\n': ''
        }, regex=True)

    # Temporarily fix names to make it easier to parse district
    data['temp_office'] = data['temp_office'].replace({
        'COUNTY COMMISSIONER DISTRICT 2 UNEXPIRED 2 YEAR TERM':
            'COUNTY COMMISSIONER 2 YEAR TERM UNEXPIRED TERM DISTRICT 2',
        'COUNTY COMMISSIONER WEST END DISTRICT': 'COUNTY COMMISSIONER DISTRICT WEST-END',
        'COUNTY COMMISSIONER WESTERN DISTRICT': 'COUNTY COMMISSIONER DISTRICT WESTERN',
        'DISTRICT COURT JUDGE DISTRICT 4, DEPARTMENT 4 UNEXPIRED TERM':
            'DISTRICT COURT JUDGE UNEXPIRED TERM DISTRICT 4, DEPARTMENT 4'
        })

    # We will standardize retention elections, and remove unexpired/district information later
    print('Partially parsed MT20 `office` (1/3).')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `party_detailed...`')

    # Data is pulled from `Party`
    data['party_detailed'] = data['Party'].str.upper()

    # Standardize
    data['party_detailed'] = data['party_detailed'].replace({
        'NON-PARTISAN': 'NONPARTISAN',
        }, regex=True)

    print('Parsed MT20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `party_simplified...`')
    # We can use the details from the recently parsed MT20 party_detailed for this.
    data['party_simplified'] = data['party_detailed'].replace("INDEPENDENT","OTHER")

    print('Parsed MT20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `mode`...')
    # All vote totals are TOTAL
    data['mode'] = 'TOTAL'

    print('Parsed MT20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    print('Parsed MT20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `county_name`...')
    # Data is pulled straight from `County` and upper cased
    data['county_name'] = data['County'].str.upper()

    # Standardize names
    data['county_name'] = data['county_name'].replace({
        r'LEWIS & CLARK': 'LEWIS AND CLARK',
        }, regex=True)

    print('Parsed MT20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    data['county_fips'] = EC.county_fips.parse_fips_from_name(data)

    print('Parsed MT20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `jurisdiction_name`...')
    # `jurisdiction_name` is the same as `county_name` for Montana, so use that
    data['jurisdiction_name'] = data['county_name']

    print('Parsed MT20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `jurisdiction_fips`...')
    # `jurisdiction_fips` is the same as `county_fips` for Montana, so use that
    data['jurisdiction_fips'] = data['county_fips']

    print('Parsed MT20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['candidate'] = data['Candidate'].str.upper()

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

    # Standardize a few names
    data['candidate'] = data['candidate'].replace({
        r'DARIN \(DA\) MICHELS': 'DARIN "D A" MICHELS',
        r'EDITH \(EDIE\) MCCLAFFERTY': 'EDITH "EDIE" MCCLAFFERTY',
        r'JAMES L LARSON \(JIM\)': 'JAMES L "JIM" LARSON',
        r'JOHN \(JACK\) KAMBICH': 'JOHN "JACK" KAMBICH',
        r'VALERIE J \(MIDDLEMAS\) HORNSVELD': 'VALERIE J "MIDDLEMAS" HORNSVELD',
        r'AGAINST.*': 'NO',
        r'FOR.*': 'YES',
        }, regex=True)

    retention_candidates = {
        r'SHALL JUDGE GREGORY R TODD.*': 'GREGORY R TODD',
        r'SHALL JUDGE HOWARD F RECHT.*': 'HOWARD F RECHT',
        r'SHALL JUDGE JAMES A MANLEY.*': 'JAMES A MANLEY',
        r'SHALL JUDGE JEROME MCCARTHY.*': 'JEROME MCCARTHY',
        r'SHALL JUDGE JENNIFER B LINT.*': 'JENNIFER B LINT',
        r'SHALL JUDGE JIM SHEA.*': 'JIM SHEA',
        r'SHALL JUDGE JOHN W PARKER.*': 'JOHN W PARKER',
        r'SHALL JUDGE KATHERINE M BIDEGARAY.*': 'KATHERINE M BIDEGARAY',
        r'SHALL JUDGE KATHY SEELEY.*': 'KATHY SEELEY',
        r'SHALL JUDGE KAYDEE N SNIPES RUIZ.*': 'KAYDEE N SNIPES RUIZ',
        r'SHALL JUDGE RIENNE H MCELYEA.*': 'RIENNE H MCELYEA',
        r'SHALL JUDGE ROD SOUZA.*': 'ROD SOUZA',
        r'SHALL JUDGE SHANE A VANNATTA.*': 'SHANE A VANNATTA',
        r'SHALL JUSTICE OF THE PEACE JAMES F \(JIMM\) KILMER.*': 'JAMES F "JIMM" KILMER',
        r'SHALL JUSTICE OF THE PEACE JOHN G LESOFSKI.*': 'JOHN G LESOFSKI',
        r'SHALL JUSTICE OF THE PEACE STEVE ANDERSEN.*': 'STEVE ANDERSEN',
        }

    data['candidate'] = data['candidate'].mask(
        data['temp_office'].str.contains('|'.join(retention_candidates.keys())),
        data['temp_office'].replace(retention_candidates, regex=True) + ' - ' + data['candidate'],
        )

    print('Parsed MT20 `candidate`.')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `district`...')

    data['district'] = ''

    # Split district information
    data = EC.split_column(data, 'temp_office',
                           r'(?P<temp_office>.*) DISTRICT (?!COURT)(?P<district>[^ ]*)',
                           maintaining_columns=['temp_office', 'district'],
                           empty_value='')
    data = EC.split_column(data, 'temp_office',
                           r'(?P<temp_office>.*) (?P<district>DISTRICT \d+, DEPARTMENT \d+)',
                           maintaining_columns=['temp_office', 'district'],
                           empty_value='')
    # Fix back temporary fix
    data['district'] = data['district'].replace({'WEST-END': 'WEST END'}, regex=True)
    # 'US HOUSE' has one at-large district
    data['district'] = data['district'].mask(data['temp_office'] == 'US HOUSE', '000')

    data['district'] = EC.district.mark_statewide_districts(
        data['district'], data['temp_office'], [
            'PRESIDENT',
            'US SENATE',
            'GOVERNOR AND LIEUTENANT GOVERNOR',
            'SECRETARY OF STATE',
            'ATTORNEY GENERAL',
            'STATE AUDITOR',
            'STATE SUPERINTENDENT OF PUBLIC INSTRUCTION',
            'SUPREME COURT JUSTICE #5',
            'CONSTITUTIONAL AMENDMENT C-46',
            'CONSTITUTIONAL AMENDMENT C-47',
            'CONSTITUTIONAL INITIATIVE CI-118',
            'INITIATIVE NO 190',
            ])

    retention_districts = {
        r'SHALL JUDGE GREGORY R TODD.*': 'DISTRICT 13, DEPARTMENT 4',
        r'SHALL JUDGE HOWARD F RECHT.*': 'DISTRICT 21, DEPARTMENT 1',
        r'SHALL JUDGE JAMES A MANLEY.*': 'DISTRICT 20, DEPARTMENT 1',
        r'SHALL JUDGE JENNIFER B LINT.*': 'DISTRICT 21, DEPARTMENT 2',
        r'SHALL JUDGE JEROME MCCARTHY.*': '',
        r'SHALL JUDGE JIM SHEA.*': 'STATEWIDE',
        r'SHALL JUDGE JOHN W PARKER.*': 'DISTRICT 8, DEPARTMENT 4',
        r'SHALL JUDGE KATHERINE M BIDEGARAY.*': 'DISTRICT 7, DEPARTMENT 2',
        r'SHALL JUDGE KATHY SEELEY.*': 'DISTRICT 1, DEPARTMENT 3',
        r'SHALL JUDGE KAYDEE N SNIPES RUIZ.*': 'DISTRICT 12, DEPARTMENT 1',
        r'SHALL JUDGE RIENNE H MCELYEA.*': 'DISTRICT 18, DEPARTMENT 2',
        r'SHALL JUDGE ROD SOUZA.*': 'DISTRICT 13, DEPARTMENT 5',
        r'SHALL JUDGE SHANE A VANNATTA.*': 'DISTRICT 4, DEPARTMENT 5',
        r'SHALL JUSTICE OF THE PEACE JAMES F \(JIMM\) KILMER.*': '',
        r'SHALL JUSTICE OF THE PEACE JOHN G LESOFSKI.*': '',
        r'SHALL JUSTICE OF THE PEACE STEVE ANDERSEN.*': '',
        }

    data['district'] = data['district'].mask(
        data['temp_office'].str.contains('|'.join(retention_districts.keys())),
        data['temp_office'].replace(retention_districts, regex=True),
        )

    retention_offices = {
        r'SHALL JUDGE GREGORY R TODD.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE HOWARD F RECHT.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE JAMES A MANLEY.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE JENNIFER B LINT.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE JEROME MCCARTHY.*': 'COUNTY CITY COURT JUDGE',
        r'SHALL JUDGE JIM SHEA.*': 'SUPREME COURT JUSTICE',
        r'SHALL JUDGE JOHN W PARKER.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE KATHERINE M BIDEGARAY.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE KATHY SEELEY.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE KAYDEE N SNIPES RUIZ.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE RIENNE H MCELYEA.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE ROD SOUZA.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUDGE SHANE A VANNATTA.*': 'DISTRICT COURT JUDGE',
        r'SHALL JUSTICE OF THE PEACE JAMES F \(JIMM\) KILMER.*':
            'COUNTY JUSTICE OF THE PEACE',
        r'SHALL JUSTICE OF THE PEACE JOHN G LESOFSKI.*': 'COUNTY JUSTICE OF THE PEACE',
        r'SHALL JUSTICE OF THE PEACE STEVE ANDERSEN.*': 'COUNTY JUSTICE OF THE PEACE',
        }

    data['temp_office'] = data['temp_office'].mask(
        data['temp_office'].str.contains('|'.join(retention_offices.keys())),
        'RETENTION ' + data['temp_office'].replace(retention_offices, regex=True),
        )

    data['district'] = EC.district.fix_numerical_districts(data['district'])

    print('Parsed MT20 `district`.')
    print('Parsing MT20 `office` (2/3)...')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `magnitude`...')

    # Magnitude is consistently 1
    data['magnitude'] = 1

    print('Parsed MT20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['temp_office'],
        state={
            'ATTORNEY GENERAL',
            'CONSTITUTIONAL AMENDMENT C-46',
            'CONSTITUTIONAL AMENDMENT C-47',
            'CONSTITUTIONAL INITIATIVE CI-118',
            'GOVERNOR AND LIEUTENANT GOVERNOR',
            'INITIATIVE NO 190',
            'LEGISLATIVE REFERENDUM NO. 130',
            'RETENTION DISTRICT COURT JUDGE',
            'RETENTION SUPREME COURT',
            'SECRETARY OF STATE',
            'STATE AUDITOR',
            'STATE SUPERINTENDENT OF PUBLIC INSTRUCTION',
            'STATE SENATE',
            'STATE HOUSE',
            'SUPREME COURT JUSTICE #5',
            'DISTRICT COURT JUDGE'
            })

    print('Parsed MT20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed MT20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `stage`...')
    # Stage is consistently general for current data
    data['stage'] = 'GEN'

    print('Parsed MT20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `special`...')

    # Deal with unexpired term marks now
    data['special'] = EC.series_r_bool(data['temp_office'].str.contains('UNEXPIRED TERM'))
    data['temp_office'] = data['temp_office'].replace({
        r' UNEXPIRED TERM': '',
        }, regex=True)

    data['office'] = data['temp_office']

    print('Parsed MT20 `special`.')
    print('Parsed MT20 `office` (3/3).')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `writein`...')
    # The Montana data does not indicate writeins
    data['writein'] = EC.r_bool(False)

    print('Parsed MT20 `writein`.')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `state_po`...')
    # Already parsed

    print('Parsed MT20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `state_fips`...')
    # Already parsed

    print('Parsed MT20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `state_cen`...')
    # Already parsed

    print('Parsed MT20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `state_ic`...')
    # Already parsed

    print('Parsed MT20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `date...`')

    # Montana had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed MT20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `readme_check...`')

    # No particular remarks about data completeness
    data['readme_check'] = EC.r_bool(False)

    print('Parsed MT20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for Montana.")
    raw_data = load_all_data(prepare_pickle=True)
    print("Parsed MT20 raw data for Montana.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'County', 'Precinct', 'Office', 'Candidate', 'Party', 'Votes'},
        county_column='County', expected_counties=56
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

    print('Parsed MT20 data.')
    data = EC.select_cleaned_dataset_columns(data, False)
    data = EC.sort_cleaned_dataset(data)
    EC.check_cleaned_dataset(data, expected_counties=56, expected_jurisdictions=56)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-mt-precinct-general.csv')
