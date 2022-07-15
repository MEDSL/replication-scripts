import numpy as np
import pandas as pd
import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_statewide_file() -> DataFrame:
    file = 'raw/20gen_stwd_pct.xlsx'
    print(f'*Reading file {file}...')
    data = pd.DataFrame()
    parameters = [
        (0, [1, 2, 3, 4], range(20),
         '{name[0]} {name[1]}: {name[3]} ({name[2]})'),
        (1, [0, 1, 2, 4], range(8),
         '{name[0]} {name[1]} {name[2]}: {name[3]} (NONPARTISAN)')
        ]

    for (sheet_name, header, column_range, column_syntax) in parameters:
        sheet = pd.read_excel(file, sheet_name=sheet_name, header=header, skipfooter=11)
        sheet = sheet.iloc[:, column_range].copy()
        # Drop fully empty rows, which separate counties
        sheet = sheet.dropna(how='all')
        # Rename columns for the sake of convenience
        other_columns = [column_syntax.format(name=name) for name in sheet.columns[1:]]
        sheet.columns = ['Precinct'] + other_columns
        # Drop totals rows, as well as rows indicating continuation of county results
        sheet = sheet[~sheet['Precinct'].astype(str).str.upper()
                      .str.contains(r'\(CONTINUED\)|CO\. TOTAL')].reset_index(drop=True)

        # Get county names, which happen row wise
        county_list = list()
        for (_, row) in sheet.iterrows():
            if pd.isna(row[1]):
                county = row[0]
            else:
                county_list.append(county)
        # Now get the dataframe without county names
        sheet = sheet[~sheet.iloc[:, range(1, len(sheet.columns))].isna()
                      .all(axis=1)].reset_index(drop=True)
        # To then add the county list
        sheet['County'] = pd.Series(county_list)
        # And finally melt
        sheet = sheet.melt(id_vars=['County', 'Precinct'],
                           var_name='Office/Candidate/Party', value_name='Votes')
        sheet['Office/Candidate/Party'] = sheet['Office/Candidate/Party'].str.replace('\n', '')
        sheet = EC.split_column(sheet, 'Office/Candidate/Party',
                                r'REPRESENTATIVE DISTRICT (?P<District>\d+).*',
                                empty_value='STATEWIDE')
        sheet = EC.split_column(sheet, 'Office/Candidate/Party',
                                r'(?P<Office>.*): (?P<Candidate>.*) \((?P<Party>.*)\)')
        sheet = sheet.drop(labels='Office/Candidate/Party', axis=1)
        data = data.append(sheet)

    # For whatever reason, records for Ray J. Writz for US Senate were mistabulated off by one
    # in Custer County. We manually fix those
    precinct_votes = {
        'Battleground': 1,
        'Sunol': 1,
        'Clayton': 3,
        'Stanley': 6,
        'Absentee': 23,
        }

    for (precinct, votes) in precinct_votes.items():
        location = data[((data['Candidate'] == 'Ray J. Writz') & (data['County'] == 'CUSTER')
                         & (data['Precinct'] == precinct))].index[0]
        data.at[location, 'Votes'] = votes

    print(f'Read file {file}...')
    return data.reset_index(drop=True)


def load_legislative_file() -> DataFrame:
    file = 'raw/20gen_leg_pct.xlsx'
    print(f'*Reading file {file}...')
    sheet = pd.read_excel(file, header=None)
    # Drop fully empty rows, which separate districts
    sheet = sheet.dropna(how='all')
    # Drop totals rows
    sheet = sheet[~sheet.iloc[:, 0].astype(str).str.upper().str
                  .contains(r'COUNTY TOTAL|DISTRICT \d+ TOTAL')].reset_index(drop=True)
    # And remove the (Continued) labels
    sheet = sheet.replace({
        r' \(Continued\)': ''
        }, regex=True)

    # Load each district/county result
    frames = list()
    buffered_rows = list()

    def _update():
        frame = pd.DataFrame(buffered_rows).reset_index(drop=True).dropna(axis=1, how='all')
        # Forward fill office names
        frame.iloc[0, :] = frame.iloc[0, :].ffill()
        frames.append(frame)
        buffered_rows.clear()

    county = None
    for (_, row) in sheet.iterrows():
        if str(row[0]).startswith('Leg. Dist.'):
            if buffered_rows:
                _update()
                county = None

        if list(row[1:].unique()) == [np.nan]:
            # Reached a row indicating a county name
            if not county:
                county = row[0]
            else:
                # We have encountered a different county within the same "page".
                # Chop off dataframe and start a new one with the same header rows
                new_rows = [buffered_rows[0].copy(), buffered_rows[1].copy(),
                            buffered_rows[2].copy()]
                _update()
                county = row[0]
                buffered_rows.extend(new_rows)
        # Regardless, store row in growing buffer
        buffered_rows.append(row)

    _update()

    # For whatever reason, Leg. Dist 2 has an erroneous set of names for its first dataframe
    # We fix it by taking in the names of the second dataframe
    # Validated with https://sos.idaho.gov/elections-division/2020-results-legislative/
    frames[2].iloc[range(3), :] = frames[3].iloc[range(3), :].copy()
    frames[2] = frames[2].dropna(axis=1, how='all')

    data = pd.DataFrame()
    for (i, frame) in enumerate(frames):
        district = frame.at[0, 0]
        county = frame.at[3, 0]

        other_columns = list()
        for column in range(1, len(frame.columns)):
            value = frame.iloc[[0, 1, 2], column]
            new_value = f'{value[0].strip()}: {value[1].strip()} {value[2].strip()}'
            other_columns.append(new_value)

        new_frame = pd.DataFrame()
        new_frame = new_frame.append(frame.iloc[4:, :])
        new_frame.columns = ['Precinct'] + other_columns
        new_frame = new_frame.melt(id_vars=['Precinct'],
                                   var_name='Office/Candidate/Party', value_name='Votes')
        new_frame['County'] = county.upper()
        new_frame['District'] = district
        frames[i] = new_frame

    # Also for whatever reason, Leg. Dist 5 and 11 don't list party affiliations for
    # Renee Love and Jacob Lowder respectively. We manually add their party affiliations.
    # Validated with https://sos.idaho.gov/elections-division/2020-results-legislative/
    frames[8]['Office/Candidate/Party'] = (frames[8]['Office/Candidate/Party']
                                           .str.replace('Renee Love', 'D-Renee Love'))
    frames[9]['Office/Candidate/Party'] = (frames[9]['Office/Candidate/Party']
                                           .str.replace('Renee Love', 'D-Renee Love'))
    frames[10]['Office/Candidate/Party'] = (frames[10]['Office/Candidate/Party']
                                            .str.replace('Renee Love', 'D-Renee Love'))
    frames[32]['Office/Candidate/Party'] = (frames[32]['Office/Candidate/Party']
                                            .str.replace('Jacob Lowder', 'D-Jacob Lowder'))

    # Finally, Gail Bolin's party was misrepresented in Leg. Dist 1 was misrepresented.
    # We manually fix that.
    # Validated with https://sos.idaho.gov/elections-division/2020-results-legislative/
    frames[0]['Office/Candidate/Party'] = (frames[0]['Office/Candidate/Party']
                                           .str.replace('E-Gail Bolin', 'D-Gail Bolin'))
    frames[1]['Office/Candidate/Party'] = (frames[1]['Office/Candidate/Party']
                                           .str.replace('E-Gail Bolin', 'D-Gail Bolin'))

    # We can now split Office/Candidate/Party
    for frame in frames:
        frame = EC.split_column(frame, 'Office/Candidate/Party',
                                r'(?P<Office>.*): (?P<Party>[^-]*)-[ ]?(?P<Candidate>.*)')
        frame = frame.drop(labels='Office/Candidate/Party', axis=1)
        data = data.append(frame)

    print(f'Read file {file}...')
    return data.reset_index(drop=True)


def load_all_data() -> DataFrame:
    return load_statewide_file().append(load_legislative_file()).reset_index(drop=True)


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `state`...')
    # State is Idaho by definition
    data = EC.state.add_state_codes(data, state='Idaho')

    print('Parsed ID20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `precinct`...')
    # Data is pulled straight from `Precinct`.
    data['precinct'] = data['Precinct'].astype(str).str.strip().str.upper()

    print('Parsed ID20 `precinct`.')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `office`...')

    # Data is pulled from `Office`
    data['temp_office'] = data['Office']

    # A few statistic names were moved over to candidate. We will move them to office.
    data['temp_office'] = data['temp_office'].mask(
        data['temp_office'] == 'CONSTIUTIONAL VOTING STATISTICS',
        data['Candidate'])

    # Standardize names
    standard_names = {
        r'UNITED STATES PRESIDENT': 'US PRESIDENT',
        r'UNITED STATES SENATOR': 'US SENATE',
        r'REPRESENTATIVE.*': 'US HOUSE',
        r'ST SEN': 'STATE SENATE',
        r'ST REP A': 'STATE HOUSE SEAT A',
        r'ST REP B': 'STATE HOUSE SEAT B',
        r'CONSTIUTIONAL AMENDMENT HJR 4': 'CONSTITUTIONAL AMENDMENT HJR 4',  # Fix typo
        r'.*Number ElectionDay Registrants': 'REGISTERED VOTERS - ON ELECTION DAY',
        r'.*Total Number of Registered Voters at Cutoff':
            'REGISTERED VOTERS - BEFORE ELECTION DAY',
        r'.*Total Number ofRegistered Voters': 'REGISTERED VOTERS',
        r'.*Number ofBallots Cast': 'BALLOTS CAST',
        }

    data['temp_office'] = data['temp_office'].replace(standard_names, regex=True)

    # Drop unneeded statistics
    data = data[-data['temp_office'].str.contains('|'.join([
        '% of RegisteredVoters That Voted',
        ]))].reset_index(drop=True)

    # We will move seat information to district later
    print('Partially parsed ID20 `temp_office` (1/2).')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `party_detailed...`')

    data['party_detailed'] = data['Party']

    # First, move writein marks to proper place
    data['writein'] = EC.series_r_bool(data['party_detailed'] == 'W/I')

    # Standardize party names
    party_affiliation = {
        'DEM': 'DEMOCRAT',
        'CON': 'CONSTITUTION',
        'IND': 'INDEPENDENT',
        'LIB': 'LIBERTARIAN',
        'REP': 'REPUBLICAN',
        'W/I': 'INDEPENDENT',
        '^D$': 'DEMOCRAT',
        '^R$': 'REPUBLICAN',
        '^L$': 'LIBERTARIAN',
        '^C$': 'CONSTITUTION',
        '^I$': 'INDEPENDENT',
        }

    data['party_detailed'] = data['party_detailed'].replace(party_affiliation, regex=True)

    # Clear out party from statistics records
    data['party_detailed'] = data['party_detailed'].mask(
        data['temp_office'].str.contains('|'.join(['REGISTERED', 'BALLOTS'])),
        '')

    print('Parsed ID20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `party_simplified...`')
    # We can use the details from the recently parsed ID20 party_detailed for this.
    simplified_names = {
        r'CONSTITUTION': 'OTHER',
        r'INDEPENDENT': 'NONPARTISAN',
        }
    data['party_simplified'] = data['party_detailed'].replace(simplified_names, regex=True)

    print('Parsed ID20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `mode`...')
    # Absentee indications are shown in `precinct`
    data['mode'] = EC.iif(data['precinct'], lambda precinct: precinct.str.contains('ABSENTEE'),
                          'ABSENTEE', 'ELECTION DAY')

    print('Parsed ID20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    # A few entries in the raw dataset had empty cells, which could be decoded as either 0 or a
    # candidate not running in the district/precinct. The following were deduced to
    # be the US congressional districts each county was apart of (except ADA which is part of both)
    # With this, we can discard records of candidates that correspond to a district different
    # to the current county
    proper_congressional_districts = {
        # 'ADA': ,
        'ADAMS': 1,
        'BANNOCK': 2,
        'BEAR LAKE': 2,
        'BENEWAH': 1,
        'BINGHAM': 2,
        'BLAINE': 2,
        'BOISE': 1,
        'BONNER': 1,
        'BONNEVILLE': 2,
        'BOUNDARY': 1,
        'BUTTE': 2,
        'CAMAS': 2,
        'CANYON': 1,
        'CARIBOU': 2,
        'CASSIA': 2,
        'CLARK': 2,
        'CLEARWATER': 1,
        'CUSTER': 2,
        'ELMORE': 2,
        'FRANKLIN': 2,
        'FREMONT': 2,
        'GEM': 1,
        'GOODING': 2,
        'IDAHO': 1,
        'JEFFERSON': 2,
        'JEROME': 2,
        'KOOTENAI': 1,
        'LATAH': 1,
        'LEMHI': 2,
        'LEWIS': 1,
        'LINCOLN': 2,
        'MADISON': 2,
        'MINIDOKA': 2,
        'NEZ PERCE': 1,
        'ONEIDA': 2,
        'OWYHEE': 1,
        'PAYETTE': 1,
        'POWER': 2,
        'SHOSHONE': 1,
        'TETON': 2,
        'TWIN FALLS': 2,
        'VALLEY': 1,
        'WASHINGTON': 1,
        }

    data = data[(
        (data['temp_office'] != 'US HOUSE') |
        # For Ada, discard empty cells.
        ((data['County'] == 'ADA') & (~data['votes'].isna())) |
        # For Non-Ada, discard only candidates not running in district
        ((data['County'] != 'ADA') &
         (data['District'] == data['County'].replace(proper_congressional_districts).astype(str)))
        )].reset_index(drop=True)

    # For the remaining instances (including some apparitions for Us President, US Senate,
    # and State House), we can deduce they correspond to 0 votes that were not recorded.
    data['votes'] = data['votes'].fillna(0)

    # And convert to int
    data['votes'] = data['votes'].astype(int)

    print('Parsed ID20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `county_name`...')
    # Data is pulled straight from `County` and upper cased
    data['county_name'] = data['County'].str.upper()

    print('Parsed ID20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    data['county_fips'] = EC.county_fips.parse_fips_from_name(data)

    print('Parsed ID20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `jurisdiction_name`...')
    # `jurisdiction_name` is the same as `county_name` for Idaho, so use that
    data['jurisdiction_name'] = data['county_name']

    print('Parsed ID20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `jurisdiction_fips`...')
    # `jurisdiction_fips` is the same as `county_fips` for Idaho, so use that
    data['jurisdiction_fips'] = data['county_fips']

    print('Parsed ID20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['candidate'] = data['Candidate'].str.upper()

    # First, remove any extraneous whitespace/characters
    data['candidate'] = data['candidate'].str.strip().replace({
        r' ( )+': ' ',
        r' -': '-',
        r'\.': '',
        }, regex=True)

    # Standardize some candidates
    data['candidate'] = data['candidate'].replace({
        r'JACQUELYN \(JACKIE\) DAVIDSON': 'JACQUELYN "JACKIE" DAVIDSON',
        r'SHARON "SHARI" L WILLIAMS': 'SHARON L "SHARI" WILLIAMS'
        }, regex=True)

    # Clear out candidate from statistics records
    data['candidate'] = data['candidate'].mask(
        data['temp_office'].str.contains('|'.join(['REGISTERED', 'BALLOTS'])),
        '')

    print('Parsed ID20 `candidate`.')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `district`...')

    # Data is pulled from District
    data['district'] = data['District']

    # Remove 'Leg. Dist.'
    data['district'] = data['district'].str.replace('Leg. Dist. ', '')

    data['district'] = EC.district.fix_numerical_districts(data['district'])

    # Move Seat A and B to district from State House
    data['district'] = data['district'].mask(
        data['temp_office'].str.contains('SEAT A'),
        data['district'] + ', SEAT A')
    data['district'] = data['district'].mask(
        data['temp_office'].str.contains('SEAT B'),
        data['district'] + ', SEAT B')
    data['office'] = data['temp_office'].replace({
        ' SEAT.*': ''},
        regex=True)

    # Clear out district from statistics records
    data['district'] = data['district'].mask(data['office'].str.contains('|'.join([
        'REGISTERED', 'BALLOTS'
        ])), '')

    print('Parsed ID20 `office` (2/2).')
    print('Parsed ID20 `district`.')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `magnitude`...')

    # Magnitude is 1 except for statistics
    data['magnitude'] = EC.iif(data['office'], lambda series: series.isin({
        'BALLOTS CAST',
        'REGISTERED VOTERS - BEFORE ELECTION DAY',
        'REGISTERED VOTERS - ON ELECTION DAY',
        'REGISTERED VOTERS',
        }), 0, 1)

    print('Parsed ID20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['office'],
        state={
            'STATE SENATE',
            'STATE HOUSE SEAT A',
            'STATE HOUSE SEAT B',
            'CONSTITUTIONAL AMENDMENT HJR 4',
            },
        empty={
            'BALLOTS CAST',
            'REGISTERED VOTERS - BEFORE ELECTION DAY',
            'REGISTERED VOTERS - ON ELECTION DAY',
            'REGISTERED VOTERS',
            })

    print('Parsed ID20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed ID20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `stage`...')
    # Stage is consistently general for current data
    data['stage'] = 'GEN'

    print('Parsed ID20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `special`...')

    # # Special is consistently false for current data
    data['special'] = EC.r_bool(False)

    print('Parsed ID20 `special`.')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `writein`...')
    # Already parsed

    print('Parsed ID20 `writein`.')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `state_po`...')
    # Already parsed

    print('Parsed ID20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `state_fips`...')
    # Already parsed

    print('Parsed ID20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `state_cen`...')
    # Already parsed

    print('Parsed ID20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `state_ic`...')
    # Already parsed

    print('Parsed ID20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `date...`')

    # Idaho had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed ID20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing ID20 `readme_check...`')

    # A few vote totals are off: we manually mark them
    data['readme_check'] = EC.series_r_bool(
        # Power County seems to have miscounted votes for CONSTITUTIONAL AMENDMENT HJR 4: YES
        # Raw data reports 1967 votes,
        # Secretary of State reports 2017, according to
        # https://sos.idaho.gov/elections-division/2020-results-statistics/
        ((data['office'] == 'CONSTITUTIONAL AMENDMENT HJR 4') &
         (data['candidate'] == 'YES') &
         (data['county_name'] == 'POWER')))

    print('Parsed ID20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for Idaho.")
    raw_data = load_all_data()
    print("Parsed ID20 raw data for Idaho.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'District', 'Party', 'Candidate', 'Votes', 'County', 'Precinct',
                          'Office'},
        county_column='County', expected_counties=44
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
    # update readme to False for all observations
    data['readme_check'] = 'FALSE'

    data = EC.select_cleaned_dataset_columns(data, False)
    data = EC.sort_cleaned_dataset(data)

    # manual fix. There are duplicate precincts in raw data from BOISE county...
    # ... they are three separate rows with identical precinct names. Differentiate by adding 1/2/3 to end
    #... verified the order is correct. 
    data.loc[(data['precinct']=='90 ABSENTEE'),'precinct'] = ['90 ABSENTEE-1','90 ABSENTEE-2','90 ABSENTEE-3']*26

    EC.check_cleaned_dataset(data, expected_counties=44, expected_jurisdictions=44)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-id-precinct-general.csv')
