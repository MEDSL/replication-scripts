import os
import re

import pandas as pd
import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_file(file: str) -> DataFrame:
    data_dict = pd.read_excel(file, sheet_name=None, skiprows=5, skipfooter=1)
    data_dict.pop('Document map')
    data = pd.DataFrame()
    for (name, sheet) in data_dict.items():
        sheet = sheet.dropna(how='all')
        if sheet.empty:
            # Ignore empty sheets
            continue
        office = sheet.iloc[0][0]
        sheet = sheet.dropna(how='all', axis=1).reset_index(drop=True)
        sheet = sheet.drop(labels='Unnamed: 2', axis=1)
        header = sheet.iloc[2] + ' (' + sheet.iloc[1].fillna('') + ')'
        header[0] = 'County'
        header[1] = 'Precinct'
        header = header.str.replace('\n', '-')
        sheet['Unnamed: 0'] = sheet['Unnamed: 0'].ffill().str.strip()
        sheet = sheet[sheet['Unnamed: 1'] != 'County Totals:']
        # Lame way of dropping header
        new_sheet = sheet[sheet['Unnamed: 0'] != office].reset_index(drop=True)
        new_sheet.columns = header
        new_sheet = new_sheet.melt(id_vars=['Precinct', 'County'],
                                   var_name='Candidate', value_name='Votes')
        new_sheet['Office'] = office
        new_sheet = EC.split_column(new_sheet, 'Candidate',
                                    r'(?P<Candidate>.*) \((?P<Party>.*)\)')
        new_sheet = EC.split_column(new_sheet, 'Office',
                                    r'(?P<Office>.*) DISTRICT (?P<District>\d+)',
                                    maintaining_columns=['Office'],
                                    empty_value='')
        data = data.append(new_sheet)
    return data


def load_all_data(prepare_pickle=True) -> DataFrame:
    if prepare_pickle:
        data = pd.DataFrame()

        for (_, _, files) in os.walk(os.getcwd()+'/raw'):
            for file in files:
                if '~' in file:
                    continue
                print(f'*Reading file raw/{file}...')
                file_data = load_file(f'raw/{file}')
                data = data.append(file_data)
                print(f'Read file raw/{file}...')
        data = data.reset_index(drop=True)
        data.to_pickle('raw_WI20.pkl')

    data = pd.read_pickle('raw_WI20.pkl')
    return data


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `state`...')
    # State is Wisconsin by definition
    data = EC.state.add_state_codes(data, state='Wisconsin')

    print('Parsed WI20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `precinct`...')
    # Data is pulled straight from `Precinct`.
    data['precinct'] = data['Precinct'].astype(str).str.strip().str.upper()
    print('Parsed WI20 `precinct`.')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `office`...')

    # Data is pulled from `Office`
    data['office'] = data['Office'].str.upper()

    # Standardize names
    standard_names = {
        r'PRESIDENT.*': 'US PRESIDENT',
        r'REPRESENTATIVE IN CONGRESS': 'US HOUSE',
        r'REPRESENTATIVE TO THE ASSEMBLY': 'STATE HOUSE',
        r'STATE SENATOR': 'STATE SENATE',
        }

    data['office'] = data['office'].replace(standard_names, regex=True)

    print('Parsed WI20 `office`.')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `party_detailed...`')

    # Data is pulled from `Party`
    data['party_detailed'] = data['Party']

    # Standardize
    data['party_detailed'] = data['party_detailed'].replace({
        r'DEM': 'DEMOCRAT',
        r'REP': 'REPUBLICAN',
        r'CON': 'CONSTITUTION',
        r'IND': 'INDEPENDENT',
        }, regex=True)

    # For writeins, replace INDEPENDENT with '' and leave everything else as is
    data['party_detailed'] = data['party_detailed'].mask(
        ((data['Candidate'].str.upper().str.contains(r'\(WRITE-IN\)'))
         & (data['party_detailed'] == 'INDEPENDENT')), '')

    # The following candidates have incorrectly listed parties
    candidate_to_party = {
        r'JO JORGENSEN.*': 'LIBERTARIAN',
        r'BRIAN CARROLL.*': 'AMERICAN SOLIDARITY',
        # Unofficial
        r'HOWIE HAWKINS.*': 'GREEN',
        r'GLORIA LA RIVA.*': 'PARTY FOR SOCIALISM AND LIBERATION',
        }

    data['party_detailed'] = data['party_detailed'].mask(
        data['Candidate'].str.upper().str.contains('|'.join(candidate_to_party.keys())),
        data['Candidate'].str.upper().replace(candidate_to_party, regex=True))

    print('Parsed WI20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `party_simplified...`')
    # We can use the details from the recently parsed WI20 party_detailed for this.
    data['party_simplified'] = data['party_detailed'].replace({
        'CONSTITUTION': 'OTHER',
        'AMERICAN SOLIDARITY': 'OTHER',
        'GREEN': 'OTHER',
        'PARTY FOR SOCIALISM AND LIBERATION': 'OTHER',
        'INDEPENDENT': 'NONPARTISAN',
        })

    print('Parsed WI20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `mode`...')
    # All vote totals are TOTAL
    data['mode'] = 'TOTAL'

    print('Parsed WI20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    print('Parsed WI20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `county_name`...')
    # Data is pulled straight from `County` and upper cased
    data['county_name'] = data['County'].str.upper()

    print('Parsed WI20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    data['county_fips'] = EC.county_fips.parse_fips_from_name(data)

    print('Parsed WI20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `jurisdiction_name`...')
    # `jurisdiction_name` is in `precinct`

    def get_jurisdiction_name(precinct):
        precinct = precinct.upper().split(' WARD')[0]
        if re.match('CITY OF', precinct):
            return precinct.split('CITY OF ')[1].strip() + ' CITY'
        if re.match('TOWN OF', precinct):
            return precinct.split('TOWN OF ')[1].strip() + ' TOWN'
        if re.match('VILLAGE OF', precinct):
            return precinct.split('VILLAGE OF ')[1].strip() + ' VILLAGE'
        raise ValueError(precinct)

    data['jurisdiction_name'] = data['precinct'].apply(get_jurisdiction_name)

    # We then adapt some names from the raw data so they match jurisdiction-fips-codes.csv names
    data['jurisdiction_name'] = data['jurisdiction_name'].replace({
        'GRAND VIEW TOWN': 'GRANDVIEW TOWN',
        'MT. STERLING VILLAGE': 'MOUNT STERLING VILLAGE',
        'LAVALLE VILLAGE': 'LA VALLE VILLAGE',
        'LAND O-LAKES TOWN': "LAND O'LAKES TOWN",
        'FONTANA VILLAGE': 'FONTANA-ON-GENEVA LAKE VILLAGE',
        'SAINT LAWRENCE TOWN': 'ST. LAWRENCE TOWN',
        })

    print('Parsed WI20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `jurisdiction_fips`...')
    # Use recently obtained `jurisdiction_name` field and list of jurisdiction fips codes
    # We need to do this manually because multiple towns in different counties have the same name,
    # and some places are not in the current jurisdiction-fips-codes.csv files

    additional_places = {
        # FIPS codes obtained from
        # https://doa.wi.gov/DIR/Changes_in_WI_Munis_2000.xlsx

        # KENOSHA, SALEM TOWN, 5505971125
        # to KENOSHA, SALEM LAKES VILLAGE, 5505971163
        # https://www.kenoshanews.com/news/after-years-town-of-salem-is-no-more/article_2e3e7322-a92f-575f-aad8-71dce7834439.html
        'SALEM LAKES VILLAGE': 5505971163,

        # RACINE, RAYMOND TOWN, 5510166375
        # to RACINE, RAYMOND VILLAGE, 5510166350
        # https://www.tmj4.com/news/local-news/town-of-raymond-has-become-village-of-raymond
        'RAYMOND VILLAGE': 5510166350,

        # RACINE, YORKVILLE TOWN, 5510189575
        # to RACINE, YORKVILLE VILLAGE, 5510189550
        # https://journaltimes.com/news/local/after-incorporation-yorkville-to-elect-new-village-board/article_7870454d-499f-572e-bb19-f42094aeedb1.html
        'YORKVILLE VILLAGE': 5510189550,

        # VERNON TOWN, 5513382575
        # to VERNON VILLAGE, ?
        # New fips is unknown, so we temporarily use the old one
        'VERNON VILLAGE': 5513382575,

        # WAUKESHA TOWN, 5513384275
        # to WAUKESHA VILLAGE, ?
        # New fips is unknown, so we temporarily use the old one
        'WAUKESHA VILLAGE': 5513384275,
        }

    fips_file = pd.read_csv('../../help-files/jurisdiction-fips-codes.csv')
    fips_file['state'] = fips_file['state'].str.upper()

    # Some counties have been renamed/changed FIPS codes since the last updated version of
    # jurisdiction-fips-codes.csv. Add records

    for (place, fips) in additional_places.items():
        fips_file = fips_file.append({
            'state': 'WISCONSIN',
            'jurisdiction_name': place,
            'jurisdiction_fips': fips,
            }, ignore_index=True)

    fips_file['county_fips'] = fips_file['jurisdiction_fips'].apply(lambda fips: int(str(fips)[:5]))
    data = data.merge(fips_file, on=['state', 'county_fips', 'jurisdiction_name'], how="left")

    print('Parsed WI20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['temp_candidate'] = data['Candidate'].str.upper()

    # First, remove any extraneous whitespace/characters
    data['temp_candidate'] = data['temp_candidate'].str.strip().replace({
        r' ( )+': ' ',
        r'\.': '',
        r',': '',
        }, regex=True)

    # Remove vicepresident name
    data['temp_candidate'] = data['temp_candidate'].replace({
        r'JOSEPH R BIDEN.*': 'JOSEPH R BIDEN',
        r'DONALD J TRUMP.*': 'DONALD J TRUMP',
        r'DON BLANKENSHIP.*': 'DON BLANKENSHIP',
        r'JO JORGENSEN.*': 'JO JORGENSEN',
        r'BRIAN CARROLL.*': 'BRIAN CARROLL',
        r'JADE SIMMONS.*': 'JADE SIMMONS (WRITE-IN)',
        r'HOWIE HAWKINS.*': 'HOWIE HAWKINS (WRITE-IN)',
        r'GLORIA LA RIVA.*': 'GLORIA LA RIVA (WRITE-IN)',
        r'KANYE WEST.*': 'KANYE WEST (WRITE-IN)',
        r'MARK CHARLES.*': 'MARK CHARLES (WRITE-IN)'
        }, regex=True)

    # Standardize a few names
    data['temp_candidate'] = data['temp_candidate'].replace({
        r'SCATTERING': 'WRITEIN'
        }, regex=True)

    # We will remove write in marks later
    print('Partially parsed WI20 `candidate` (1/2).')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `district`...')

    # Data is pulled from District and uppercased
    data['district'] = data['District'].str.upper()

    data['district'] = EC.district.mark_statewide_districts(
        data['district'], data['office'], [
            'US PRESIDENT',
            'US SENATE',
            ])

    data['district'] = EC.district.fix_numerical_districts(data['district'])

    print('Parsed WI20 `district`.')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `magnitude`...')

    # Magnitude is 1 everywhere
    data['magnitude'] = 1

    print('Parsed WI20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['office'],
        state={
            'STATE HOUSE',
            'STATE SENATE',
            })

    print('Parsed WI20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed WI20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `stage`...')
    # Election is consistently general
    data['stage'] = 'GEN'

    print('Parsed WI20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `special`...')

    # The Wisconsin data does not have special elections
    data['special'] = EC.r_bool(False)

    print('Parsed WI20 `special`.')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `writein`...')
    # The Wisconsin data indicates writein in `candidate`
    data['writein'] = EC.series_r_bool(data['temp_candidate'].str.contains(
        r'\(write-in\)|WRITEIN'))
    data['candidate'] = data['temp_candidate'].replace({
        r' \(WRITE-IN\)': ''
        }, regex=True)

    print('Parsed WI20 `writein`.')
    print('Parsed WI20 `candidate` (2/2).')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `state_po`...')
    # Already parsed

    print('Parsed WI20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `state_fips`...')
    # Already parsed

    print('Parsed WI20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `state_cen`...')
    # Already parsed

    print('Parsed WI20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `state_ic`...')
    # Already parsed

    print('Parsed WI20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `date...`')

    # Wisconsin had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed WI20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing WI20 `readme_check...`')

    # Mark jurisdictions with outdated fips code
    data['readme_check'] = EC.series_r_bool(data['jurisdiction_name'].isin({
        'VERNON VILLAGE',
        'WAUKESHA VILLAGE',
        }))

    print('Parsed WI20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for Wisconsin.")
    raw_data = load_all_data(prepare_pickle=True)
    print("Parsed WI20 raw data for Wisconsin.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'County', 'Precinct', 'Office', 'Candidate', 'Party', 'Votes',
                          'District'},
        county_column='County', expected_counties=72
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
    EC.check_cleaned_dataset(data, expected_counties=72)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-wi-precinct-general.csv')
