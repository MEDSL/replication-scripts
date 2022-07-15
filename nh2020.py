import os
import re

import numpy as np
import pandas as pd
import electioncleaner as EC

DataFrame = pd.core.frame.DataFrame
Series = pd.core.series.Series


def load_file_federal_1(file: str) -> DataFrame:
    data_dict = pd.read_excel(file, sheet_name=None, header=[1, 3])

    # Preparse
    # We keep the header of the first sheet, which includes full names of candidates
    # which we will use for the other sheets
    first_sheet_name = [x for x in data_dict.keys() if x.upper().startswith('SUM')][0]
    first_sheet_header = data_dict[first_sheet_name].columns

    # First sheet includes summary statistics, which we drop
    valid_rows = list()
    valid = False
    for (_, row) in data_dict[first_sheet_name].iterrows():
        if not pd.isna(row[0]) and row[0].endswith('County'):
            valid = True
        if valid:
            valid_rows.append(row)
    data_dict[first_sheet_name] = pd.DataFrame(valid_rows[1:]).reset_index(drop=True)
    data_dict[first_sheet_name].columns = pd.MultiIndex.from_tuples(
        [('', valid_rows[0][0])] + [cell for cell in first_sheet_header[1:]])

    # Last sheet includes results from two counties, which we split
    last_sheet_name = [x for x in data_dict.keys() if x.upper().startswith('STRA')][0]
    first_county_rows = list()
    second_county_rows = list()
    in_second_county = False
    for (_, row) in data_dict[last_sheet_name].iterrows():
        if pd.isna(row[0]):
            continue
        if row[0].endswith('County'):
            in_second_county = True
        if in_second_county:
            second_county_rows.append(row)
        else:
            first_county_rows.append(row)

    first_county = data_dict[last_sheet_name].columns[0][1]
    second_county = second_county_rows[0][0]
    data_dict[first_county] = pd.DataFrame(first_county_rows)
    data_dict[second_county] = pd.DataFrame(second_county_rows[1:]).reset_index(drop=True)
    data_dict[second_county].columns = pd.MultiIndex.from_tuples(
        [('', second_county)] + [cell for cell in data_dict[second_county].columns[1:]])
    data_dict.pop(last_sheet_name)

    for (sheet_name, county_data) in data_dict.items():
        # Drop empty/quasi-empty columns
        for column in county_data.columns.copy():
            values = set(county_data[column].fillna(''))
            if values in [{''}, {'', ' '}]:
                county_data = county_data.drop(column, axis=1)
        # Drop empty/quasi-empty rows
        for (index, row) in county_data.copy().iterrows():
            values = set(row.fillna(''))
            if values in [{''}, {'', ' '},
                          {'*correction received', ''},
                          {'*corrections received', ''}]:
                county_data = county_data.drop(index)

        county_data = county_data.drop(county_data.tail(1).index)  # Drop TOTALS
        data_dict[sheet_name] = county_data

    first_sheet_header = first_sheet_header[:len(data_dict[first_sheet_name].columns)]
    for (sheet_name, county_data) in data_dict.items():
        # Use full names for candidates for the sheets
        county_data.columns = pd.MultiIndex.from_tuples(
            [county_data.columns[0]] + [cell for cell in first_sheet_header[1:]])
        data_dict[sheet_name] = county_data

    # Now we are ready to merge
    file_data = pd.DataFrame()

    for (sheet_name, county_data) in data_dict.items():
        office = county_data.columns[1][0]
        county = county_data.columns[0][1][:-7].strip()
        county_data.columns = ['Precinct'] + [cell[1] for cell in county_data.columns[1:]]
        county_data = county_data.melt(id_vars=['Precinct'],
                                       var_name='Candidate', value_name='Votes')
        county_data['County'] = county
        county_data['Office'] = office.strip()
        county_data['District'] = ''
        county_data['Candidate'] = county_data['Candidate'].str.strip()
        county_data['Votes'] = county_data['Votes'].fillna(0).astype(str).replace({'-': 0})
        county_data['Votes'] = county_data['Votes'].astype(float).astype(int)
        # Do float then int because int('3964.0') yields a value error

        county_data = EC.split_column(county_data, 'Candidate',
                                      r'(?P<Candidate>[^,]*) (?P<Party>[^ ]+)',
                                      maintaining_columns=['Candidate'],
                                      empty_value='NONPARTISAN',)
        county_data = EC.split_column(county_data, 'Candidate',
                                      r'(?P<Candidate>.*), (?P<Party>[^ ]+)',
                                      maintaining_columns=['Candidate', 'Party'],
                                      empty_value='NONPARTISAN',)
        file_data = file_data.append(county_data)
    file_data = file_data.reset_index(drop=True).sort_values('County')
    return file_data


def load_files_federal_1() -> DataFrame:
    files = [
        'governor-2020.xls',
        'president-2020.xls',
        'us-senator-2020.xls',
        ]

    data = pd.DataFrame()
    for file in files:
        print(f'*Reading file raw/{file}...')
        file_data = load_file_federal_1(f'raw/{file}')
        data = data.append(file_data)
        print(f'Read file raw/{file}...')

    data = data.reset_index(drop=True)
    data['Precinct'] = data['Precinct'].replace({
        r'\*': '',
        r'At\. & Gil\. Academy Grant': 'Atkinson and Gilmanton Academy Grant',
        r'Atk\. & Gilm\. Ac\. Gt\.': 'Atkinson and Gilmanton Academy Grant',
        r"Low & Burbank's Gt\.": "Low and Burbank's Grant",
        r"Low & Burbank's Grant": "Low and Burbank's Grant",
        r"Second College Gt\.": "Second College Grant",
        r"Thompson & Mes's Pur\.": "Thompson and Meserve's Purchase",
        r"Thompson & Meserve's Pur\.": "Thompson and Meserve's Purchase",
        r"Wentworth's Loc\.": "Wentworth's Location",
        }, regex=True).str.strip()
    data['Stage'] = 'GEN'
    return data


def load_file_federal_2(file: str) -> DataFrame:
    data_dict = pd.read_excel(file, sheet_name=None, header=[1, 2], skipfooter=3)
    for (sheet_name, county_data) in data_dict.items():
        # Drop empty/quasi-empty columns
        for column in county_data.columns.copy():
            values = set(county_data[column].fillna(''))
            if values in [{''}, {'', ' '}]:
                county_data = county_data.drop(column, axis=1)
        data_dict[sheet_name] = county_data

    # Now we are ready to merge
    file_data = pd.DataFrame()

    for (sheet_name, county_data) in data_dict.items():
        raw_office = county_data.columns[1][0]
        match = re.match(r'(?P<office>[^-]+)( -)? District (No\. )?(?P<district>\d+)', raw_office)
        office, district = match['office'], match['district']
        county_data.columns = ['Precinct'] + [cell[1] for cell in county_data.columns[1:]]
        county_data = county_data.melt(id_vars=['Precinct'],
                                       var_name='Candidate', value_name='Votes')
        county_data['Office'] = office
        county_data['District'] = district
        county_data['Candidate'] = county_data['Candidate'].str.strip()
        county_data['Votes'] = county_data['Votes'].fillna(0).astype(str).str.strip()
        county_data['Votes'] = county_data['Votes'].replace({'-': 0}).astype(float).astype(int)
        # Do float then int because int('3964.0') yields a value error

        county_data = EC.split_column(county_data, 'Candidate',
                                      r'(?P<Candidate>[^,]*) (?P<Party>[^ ]+)',
                                      maintaining_columns=['Candidate'],
                                      empty_value='NONPARTISAN',)
        county_data = EC.split_column(county_data, 'Candidate',
                                      r'(?P<Candidate>.*), (?P<Party>[^ ]+)',
                                      maintaining_columns=['Candidate', 'Party'],
                                      empty_value='NONPARTISAN',)
        file_data = file_data.append(county_data)
    file_data = file_data.reset_index(drop=True)

    return file_data


def load_files_federal_2() -> DataFrame:
    files = [
        'congressional-district-1-2020.xlsx',
        'congressional-district-2-2020.xlsx',
        'executive-council-district-1-5-2020.xls',
        ]

    data = pd.DataFrame()
    for file in files:
        print(f'*Reading file raw/{file}...')
        file_data = load_file_federal_2(f'raw/{file}')
        data = data.append(file_data)
        print(f'Read file raw/{file}...')

    data['Precinct'] = data['Precinct'].replace({
        r'\*': '',
        r'At\. & Gil Ac\. Gt': 'Atkinson and Gilmanton Academy Grant',
        r'Atkinson & Gilmanton Academy Gt': 'Atkinson and Gilmanton Academy Grant',
        r"Low & Burbank's Grant": "Low and Burbank's Grant",
        r'- Ward': 'Ward',
        r"Martins' Location": "Martin's Location",
        r"Thomp. and Mes's Pur.": "Thompson and Meserve's Purchase",
        r"Thompson & Meserve's Purchase": "Thompson and Meserve's Purchase",
        }, regex=True).str.strip()

    data = data.reset_index(drop=True)
    data['Stage'] = 'GEN'
    return data


def load_file_state_senate(file: str) -> DataFrame:
    data_dict = pd.read_excel(file, sheet_name=None, header=None)
    # Preparse, as a few sheets include multiple races in the same sheet
    dfs = dict()

    for (sheet, sheet_data) in data_dict.items():
        rows = list()
        race = ''
        for (_, row) in sheet_data.iterrows():
            new_row = list()
            for value in row:
                if pd.isna(value):
                    new_row.append('')
                else:
                    new_row.append(str(value).strip())

            if new_row[1] == 'State of New Hampshire':
                continue
            if new_row[2] == '':
                # Header column
                race = new_row[1]
                rows = list()
                continue
            if set(new_row) in [{''}, {'', ' '}]:
                # Ignore empty rows
                continue
            if new_row[0].upper() == 'TOTALS':
                # Save dataframe
                df = pd.DataFrame(rows[1:])
                df.columns = rows[0]
                df = df.dropna(axis=1, how='all')
                dfs[race] = df
                continue
            rows.append(row)

    # Now we are ready to merge
    file_data = pd.DataFrame()
    for (sheet_name, race_data) in dfs.items():
        match = re.match(r'(?P<office>[^-]+)( -)? District (No\. )?(?P<district>\d+)', sheet_name)
        office, district = match['office'], match['district']
        race_data.columns = ['Precinct'] + [cell for cell in race_data.columns[1:]]
        race_data = race_data.melt(id_vars=['Precinct'],
                                   var_name='Candidate', value_name='Votes')
        race_data['Office'] = office
        race_data['District'] = district
        race_data['Candidate'] = race_data['Candidate'].str.strip()
        race_data['Precinct'] = race_data['Precinct'].str.strip()
        race_data['Votes'] = race_data['Votes'].fillna(0).astype(str).str.strip()
        race_data['Votes'] = race_data['Votes'].replace({'--': 0}).astype(float).astype(int)
        # Do float then int because int('3964.0') yields a value error
        race_data = EC.split_column(race_data, 'Candidate',
                                    r'(?P<Candidate>.*), (?P<Party>[^ ]+)',
                                    maintaining_columns=['Candidate'],
                                    empty_value='NONPARTISAN',)
        file_data = file_data.append(race_data)
    file_data = file_data.reset_index(drop=True)

    return file_data


def load_files_state_senate() -> DataFrame:
    files = [
        'state-senate-district-1-11-2020.xls',
        'state-senate-district-12-24-2020.xls',
        ]

    data = pd.DataFrame()
    for file in files:
        print(f'*Reading file raw/{file}...')
        file_data = load_file_state_senate(f'raw/{file}')
        data = data.append(file_data)
        print(f'Read file raw/{file}...')

    data = data.reset_index(drop=True)
    data['Stage'] = 'GEN'

    # A few races had recounts, which were not appropriate labeled. Manually convert them based on
    # Precinct and Vote totals

    recount_candidates = {
        # STATE SENATE DISTRICT 11
        ('Amherst', 3532): ('Gary L. Daniels', 'r'),
        ('Merrimack', 8193): ('Gary L. Daniels', 'r'),
        ('Milford', 4581): ('Gary L. Daniels', 'r'),
        ('Wilton', 1187): ('Gary L. Daniels', 'r'),
        ('Amherst', 4409): ('Shannon E. Chandley', 'd'),
        ('Merrimack', 7588): ('Shannon E. Chandley', 'd'),
        ('Milford', 4155): ('Shannon E. Chandley', 'd'),
        ('Wilton', 1182): ('Shannon E. Chandley', 'd'),

        # STATE SENATE DISTRICT 12
        ('Brookline', 1765): ('Kevin Avard', 'r'),
        ('Greenville', 556): ('Kevin Avard', 'r'),
        ('Hollis', 2772): ('Kevin Avard', 'r'),
        ('Mason', 556): ('Kevin Avard', 'r'),
        ('Nashua Ward 1', 2673):  ('Kevin Avard', 'r'),
        ('Nashua Ward 2', 2127):  ('Kevin Avard', 'r'),
        ('Nashua Ward 5', 2770): ('Kevin Avard', 'r'),
        ('New Ipswich', 2130): ('Kevin Avard', 'r'),
        ('Rindge', 2185): ('Kevin Avard', 'r'),
        ('Brookline', 1799): ('Melanie Levesque', 'd'),
        ('Greenville', 464): ('Melanie Levesque', 'd'),
        ('Hollis', 2897): ('Melanie Levesque', 'd'),
        ('Mason', 367): ('Melanie Levesque', 'd'),
        ('Nashua Ward 1', 3103):  ('Melanie Levesque', 'd'),
        ('Nashua Ward 2', 2727):  ('Melanie Levesque', 'd'),
        ('Nashua Ward 5', 3118): ('Melanie Levesque', 'd'),
        ('New Ipswich', 923): ('Melanie Levesque', 'd'),
        ('Rindge', 1331): ('Melanie Levesque', 'd'),
        }

    for (key, value) in recount_candidates.items():
        precinct, votes = key
        candidate, party = value

        row = data.index[((data['Precinct'] == precinct) & (data['Candidate'] == 'Recount')
                          & (data['Votes'] == votes))][0]
        data.iat[row, 1] = candidate
        data.iat[row, 5] = party
        data.iat[row, 6] = 'GEN RECOUNT'

    data['Precinct'] = data['Precinct'].replace({
        r'\*': '',
        r'Atkinson and Gilmanton Ac. Gt.': 'Atkinson and Gilmanton Academy Grant',
        r"Low & Burbank's Grant": "Low and Burbank's Grant",
        r"Thompson & Meserve's Pur.": "Thompson and Meserve's Purchase"
        }, regex=True).str.strip()

    return data


def load_file_state_house(file: str) -> DataFrame:
    county = re.search(r'house-(?P<county>.*)-2020.xls', file)['county']
    raw_data = pd.read_excel(file, sheet_name=0, header=None)
    dfs = dict()
    rows = list()
    race = ''

    # Carroll dropped a comma
    if county == 'carroll':
        raw_data.iat[9, 1] = 'Richardson, r'
    # And Coos did not name a district for whatever reason
    elif county == 'coos':
        raw_data.iat[31, 0] = 'District No. 3'
    # And Hillsborough misplaced a few rows:
    elif county == 'hillsborough':
        raw_data.iat[79, 6] = 'Scatter'
        raw_data.iat[80, 6] = 16
        # And these are extraneous rows
        raw_data.iat[223, 8] = np.nan
        raw_data.iat[224, 8] = np.nan
        # And dropped a comma
        raw_data.iat[175, 2] = 'Hennessey, d'
    # And Merrimack did not name a district
    elif county == 'merrimack':
        raw_data.iat[114, 0] = 'District No. 24'
        # And had a space cell
        raw_data.iat[112, 7] = np.nan
    # And Rockingham misplaced a few rows, so we manually fix them before anything
    elif county == 'rockingham':
        raw_data.iat[45, 0] = ''
        raw_data.iat[46, 0] = 'District No. 6'
        raw_data.iat[47, 0] = 'Derry'
        # And fix empty cell
        raw_data.iat[130, 0] = 'District No. 21'
    # And Sullivan has a space cell
    elif county == 'sullivan':
        raw_data.iat[12, 4] = np.nan
    # And Strafford misnamed a district and had an extra value
    elif county == 'strafford':
        raw_data.iat[58, 0] = 'District No. 15 (1)'
        raw_data.iat[122, 4] = ''

    def _save_dataframe(rows, race):
        df = pd.DataFrame(rows[1:])
        df.columns = [str(x).strip() for x in rows[0]]
        if '' in df.columns:
            df = df.drop(labels='', axis=1)
        df = df.dropna(axis=1, how='all')
        fixed_races = [race[:-2] for race in dfs.keys()]
        race += f'#{fixed_races.count(race)}'
        dfs[race] = df
        rows.clear()

    # Preparse
    for (i, row) in raw_data.iterrows():
        new_row = list()
        for value in row:
            if pd.isna(value):
                new_row.append('')
            else:
                new_row.append(str(value).strip())

        if i < 2:
            # Skip title rows
            continue
        if set(new_row) == {''}:
            # Ignore empty rows...
            # Unless we have buffered rows already (which happen if races dont include a totals row)
            if not rows:
                continue
            _save_dataframe(rows, race)
            continue
        if new_row[0].startswith('District') or new_row[0].startswith('Distict'):
            if rows:
                _save_dataframe(rows, race)
            # Header column
            # Magnitude
            match = re.search(r'\((?P<magnitude>\d+)\)', new_row[0])
            if match:
                magnitude = match['magnitude']
                if magnitude != '1':
                    race = f'STATE HOUSE (VOTE FOR {magnitude})'
                else:
                    race = 'STATE HOUSE'
            else:
                race = 'STATE HOUSE'

            # District
            match = re.search(r'Distr?ict No\.?( *)(?P<district>\d+).*', new_row[0])
            district = match['district']
            if 'F' in new_row[0]:
                district += 'F'
            race += f' - District {district}'
            row[0] = race

            rows = list()
            rows.append(row)
            continue
        if new_row[0].upper() == 'TOTALS':
            _save_dataframe(rows, race)
            continue
        rows.append(row)

    # A few districts straddle rows, so we merge them based on the longest name
    new_dfs = dict()
    for name in sorted(dfs.keys()):
        for other_name in new_dfs.keys():
            if other_name[-12:-2] == name[-12:-2]:
                new_dfs[other_name] = pd.concat([
                    new_dfs[other_name].reset_index(drop=True),
                    dfs[name].drop(dfs[name].columns[0], axis=1).reset_index(drop=True),
                    ], axis=1)
                break
        else:
            new_dfs[name] = dfs[name]

    # Now we are ready to merge
    file_data = pd.DataFrame()

    for (sheet_name, race_data) in new_dfs.items():
        match = re.match(r'(?P<office>.+) - District (?P<district>\d+F?)', sheet_name[:-2])
        office, district = match['office'], match['district']
        race_data.columns = ['Precinct'] + [cell for cell in race_data.columns[1:]]
        race_data = race_data.melt(id_vars=['Precinct'],
                                   var_name='Candidate', value_name='Votes')
        race_data['County'] = county.capitalize()
        race_data['Office'] = office
        race_data['District'] = district
        race_data['Candidate'] = race_data['Candidate'].str.strip()
        race_data['Precinct'] = race_data['Precinct'].str.strip()
        race_data['Votes'] = race_data['Votes'].fillna(0).astype(str).str.strip()
        race_data['Votes'] = race_data['Votes'].replace({
            '.*-.*': 0,
            '^$': 0,
            }, regex=True).astype(float).astype(int)
        # Do float then int because int('3964.0') yields a value error
        race_data = EC.split_column(race_data, 'Candidate',
                                    r'(?P<Candidate>.*), ?(?P<Party>[^ ]+)',
                                    maintaining_columns=['Candidate'],
                                    empty_value='NONPARTISAN',)
        file_data = file_data.append(race_data)
    file_data = file_data.reset_index(drop=True).sort_values('District')
    return file_data


def load_files_state_house() -> DataFrame:
    files = [
        'house-belknap-2020.xls',
        'house-carroll-2020.xls',
        'house-cheshire-2020.xls',
        'house-coos-2020.xls',
        'house-grafton-2020.xls',
        'house-hillsborough-2020.xls',
        'house-merrimack-2020.xls',
        'house-rockingham-2020.xls',
        'house-strafford-2020.xls',
        'house-sullivan-2020.xls',
        ]

    data = pd.DataFrame()
    for file in files:
        print(f'*Reading file raw/{file}...')
        file_data = load_file_state_house(f'raw/{file}')
        data = data.append(file_data)
        print(f'Read file raw/{file}...')

    data = data.reset_index(drop=True)
    data['Stage'] = 'GEN'

    # A few races had recounts, which were not appropriate labeled. Manually convert them based on
    # Precinct and Vote totals
    # These ones were listed as columns

    recount_candidates = {
        # GRAFTON
        ('17F', 'Hughes', 'r'): {
            'Alexandria': 572,
            'Ashland': 649,
            'Bridgewater': 477,
            'Bristol': 1005,
            'Enfield': 939,
            'Grafton': 406,
            },
        ('17F', 'Adjutant', 'd'): {
            'Alexandria': 450,
            'Ashland': 524,
            'Bridgewater': 358,
            'Bristol': 767,
            'Enfield': 1695,
            'Grafton': 334,
            },
        # Hillsborough
        ('4', 'Kofalt', 'r'): {
            'Francestown': 521,
            'Greenville': 520,
            'Lyndeborough': 537,
            'Wilton': 1098,
            },
        ('4', 'Post', 'r'): {
            'Francestown': 531,
            'Greenville': 493,
            'Lyndeborough': 576,
            'Wilton': 1048,
            },
        ('4', 'Bernet', 'd'): {
            'Francestown': 531,
            'Greenville': 432,
            'Lyndeborough': 476,
            'Wilton': 1187,
            },
        ('4', 'Williams', 'd'): {
            'Francestown': 496,
            'Greenville': 409,
            'Lyndeborough': 427,
            'Wilton': 1151,
            },
        # MERRIMACK
        ('17', 'D. Soucy', 'r'): {
            'Concord Ward 8': 1016,
            },
        ('17', 'Wazir', 'd'): {
            'Concord Ward 8': 1209,
            },
        ('20', 'Seaworth', 'r'): {
            'Chichester': 939,
            'Pembroke': 2107,
            },
        ('20', 'White', 'r'): {
            'Chichester': 851,
            'Pembroke': 1805,
            },
        ('20', 'Gagyi', 'r'): {
            'Chichester': 786,
            'Pembroke': 1689,
            },
        ('20', 'Hanson, Jr.', 'd'): {
            'Chichester': 615,
            'Pembroke': 1824,
            },
        ('20', 'Schuett', 'd'): {
            'Chichester': 704,
            'Pembroke': 2031,
            },
        ('20', 'Doherty', 'd'): {
            'Chichester': 669,
            'Pembroke': 1967,
            },
        }

    for (key, value) in recount_candidates.items():
        district, candidate, party, = key
        for (precinct, votes) in value.items():
            row = data.index[((data['Precinct'] == precinct) & (data['Candidate'] == 'Recount') &
                              (data['District'] == district) & (data['Votes'] == votes))][0]
            data.iat[row, 1] = candidate
            data.iat[row, 6] = party
            data.iat[row, 7] = 'GEN RECOUNT'

    # These ones were rows
    recount_candidates_2 = {
        # DISTRICT 15
        ('Hillsborough', 'McNair', 'r'): {
            'Manchester Ward 8': 2437,
            },
        ('Hillsborough', 'Warden', 'r'): {
            'Manchester Ward 8': 2612,
            },
        ('Hillsborough', 'Connors', 'd'): {
            'Manchester Ward 8': 2454,
            },
        ('Hillsborough', 'Katsiantonis', 'd'): {
            'Manchester Ward 8': 1721,
            },
        # DISTRICT 16
        ('Hillsborough', 'Kliskey', 'r'): {
            'Manchester Ward 9': 1785,
            },
        ('Hillsborough', 'Stefanik', 'r'): {
            'Manchester Ward 9': 1720,
            },
        ('Hillsborough', 'Query', 'd'): {
            'Manchester Ward 9': 1820,
            },
        ('Hillsborough', 'Shaw', 'd'): {
            'Manchester Ward 9': 2336
            },
        # DISTRICT 19
        ('Hillsborough', 'Marston', 'r'): {
            'Manchester Ward 12': 2019,
            },
        ('Hillsborough', 'Whitlock', 'r'): {
            'Manchester Ward 12': 1881,
            },
        ('Hillsborough', 'Snow', 'd'): {
            'Manchester Ward 12': 2419,
            },
        ('Hillsborough', 'Zackeroff', 'd'): {
            'Manchester Ward 12': 2009,
            },
        # DISTRICT 34
        ('Hillsborough', 'Hall', 'r'): {
            'Nashua Ward 7': 1787,
            },
        ('Hillsborough', 'Hogan', 'r'): {
            'Nashua Ward 7': 1537,
            },
        ('Hillsborough', 'Casey', 'r'): {
            'Nashua Ward 7': 1526,
            },
        ('Hillsborough', 'Sofikitis', 'd'): {
            'Nashua Ward 7': 2029,
            },
        ('Hillsborough', 'Stevens', 'd'): {
            'Nashua Ward 7': 2041,
            },
        ('Hillsborough', 'Moran, Jr.', 'd'): {
            'Nashua Ward 7': 1805,
            },
        # DISTRICT 7
        ('Rockingham', 'Soti', 'r'): {
            'Windham': 4777,
            },
        ('Rockingham', 'Griffin', 'r'): {
            'Windham': 5591,
            },
        ('Rockingham', 'Lynn', 'r'): {
            'Windham': 5089,
            },
        ('Rockingham', 'McMahon', 'r'): {
            'Windham': 5554,
            },
        ('Rockingham', 'St.Laurent', 'd'): {
            'Windham': 4357,
            },
        ('Rockingham', 'Azibert', 'd'): {
            'Windham': 2808,
            },
        ('Rockingham', 'Roman', 'd'): {
            'Windham': 3443,
            },
        ('Rockingham', 'Singureanu', 'd'): {
            'Windham': 2782,
            },
        # DISTRICT 7
        ('Strafford', 'deBree', 'r'): {
            'Rochester Ward 1': 1405,
            },
        ('Strafford', 'Fontneau', 'd'): {
            'Rochester Ward 1': 1409,
            }
        }

    for (key, value) in recount_candidates_2.items():
        county, candidate, party, = key
        for (precinct, votes) in value.items():
            row = data.index[((data['Precinct'] == 'Recount') & (data['Candidate'] == candidate) &
                              (data['Party'] == party) &
                              (data['County'] == county) & (data['Votes'] == votes))][0]
            data.iat[row, 0] = precinct
            data.iat[row, 7] = 'GEN RECOUNT'

    # There were a few precinct rows that correspond to recounts that also lists scatters. Those
    # were not recounted, so they are not included in the final data
    data = data[~((data['Precinct'] == 'Recount') &
                  (data['Votes'] == 0))]

    # State House candidates did not include name
    # .......sigh
    replacements = {
        # Belknap
        ("Belknap", "1", "Joseph, Jr.", "d"): 'Robert Joseph Jr.',
        ("Belknap", "1", "Ploszaj", "r"): 'Tom Ploszaj',
        ("Belknap", "2", "Taylor", "d"): 'Natalie Taylor',
        ("Belknap", "2", "Mackie", "r"): 'Jonathan Mackie',
        ("Belknap", "2", "Silber", "r"): 'Norman Silber',
        ("Belknap", "2", "Carita", "d"): 'Shelley Carita',
        ("Belknap", "2", "Aldrich", "r"): 'Glen Aldrich',
        ("Belknap", "2", "McCue", "d"): 'Dara McCue',
        ("Belknap", "2", "Hanley", "d"): 'Diane Hanley',
        ("Belknap", "2", "Bean", "r"): 'Harry Bean',
        ("Belknap", "3", "Hough", "r"): 'Gregg Hough',
        ("Belknap", "3", "Cardona", "d"): 'Carlos Cardona',
        ("Belknap", "3", "Johnson", "r"): 'Dawn Johnson',
        ("Belknap", "3", "Ober", "d"): 'Gail Ober',
        ("Belknap", "3", "Bordes", "r"): 'Mike Bordes',
        ("Belknap", "3", "Huot", "d"): 'David Huot',
        ("Belknap", "3", "Hayward", "d"): 'Marcia Hayward',
        ("Belknap", "3", "Littlefield", "r"): 'Richard Littlefield',
        ("Belknap", "4", "Harvey-Bolia", "r"): 'Juliet Harvey-Bolia',
        ("Belknap", "4", "R. Burke (w-in)", "NONPARTISAN"): 'Rich Burke (w-in)',
        ("Belknap", "4", "Lang, Sr.", "r"): 'Timothy Lang Sr.',
        ("Belknap", "4", "Alden", "d"): 'Jane Alden',
        ("Belknap", "5", "Hammond", "d"): 'Duane Hammond',
        ("Belknap", "5", "Copithorne", "d"): 'Stephen Copithorne',
        ("Belknap", "5", "Varney", "r"): 'Peter Varney',
        ("Belknap", "5", "Terry", "r"): 'Paul Terry',
        ("Belknap", "6", "Sylvia", "r"): 'Michael Sylvia',
        ("Belknap", "6", "Trottier", "r"): 'Douglas Trottier',
        ("Belknap", "6", "Condode-metraky", "d"): 'George Condodemetraky',
        ("Belknap", "6", "House", "d"): 'Don House',
        ("Belknap", "7", "Comtois", "r"): 'Barbara Comtois',
        ("Belknap", "7", "Westlake", "d"): 'Jane Westlake',
        ("Belknap", "8F", "Larson", "d"): 'Ruth Larson',
        ("Belknap", "8F", "Howard, Jr.", "r"): 'Raymond Howard Jr',
        ("Belknap", "9F", "St. Clair", "d"): 'Charlie St. Clair',
        ("Belknap", "9F", "O'Hara", "r"): "Travis O'Hara",

        # Carroll
        ("Carroll", "1", "Gilmore", "r"): 'Ray Gilmore',
        ("Carroll", "1", "Burroughs", "d"): 'Anita Burroughs',
        ("Carroll", "2", "McCarthy", "r"): 'Frank McCarthy',
        ("Carroll", "2", "Umberger", "r"): 'Karen Umberger',
        ("Carroll", "2", "Richardson", "r"): 'Wendy Richardson',
        ("Carroll", "2", "Woodcock", "d"): 'Stephen Woodcock',
        ("Carroll", "2", "Buco", "d"): 'Tom Buco',
        ("Carroll", "2", "Leonard", "d"): 'Ellin Leonard',
        ("Carroll", "3", "McConkey", "r"): 'Mark McConkey',
        ("Carroll", "3", "Ticehurst", "d"): 'Susan Ticehurst',
        ("Carroll", "3", "Nordlund", "r"): 'Nicole Nordlund',
        ("Carroll", "3", "Knirk", "d"): 'Jerry Knirk',
        ("Carroll", "4", "Cordelli", "r"): 'Glenn Cordelli',
        ("Carroll", "4", "Nesbitt", "d"): 'Caroline Nesbitt',
        ("Carroll", "4", "Merrill", "d"): 'Chip Merrill',
        ("Carroll", "4", "Crawford", "r"): 'Karel Crawford',
        ("Carroll", "5", "Ackerman", "d"): 'Donna Ackerman',
        ("Carroll", "5", "Pustell", "d"): 'Patricia Pustell',
        ("Carroll", "5", "Nelson", "r"): 'Bill Nelson',
        ("Carroll", "5", "Smith", "r"): 'Jonathan Smith',
        ("Carroll", "5", "Avellani", "r"): 'Lino Avellani',
        ("Carroll", "5", "Ogren", "d"): 'Knute Ogren',
        ("Carroll", "6", "Deshaies", "r"): 'Brodie Deshaies',
        ("Carroll", "6", "MacDonald", "r"): 'John MacDonald',
        ("Carroll", "6", "Duran", "d"): 'Carrie Duran',
        ("Carroll", "6", "Wall", "d"): 'John Wall',
        ("Carroll", "7F", "Tregenza", "r"): 'Norman Tregenza',
        ("Carroll", "7F", "McAleer", "d"): 'Chris McAleer',
        ("Carroll", "8F", "Klotz", "d"): 'Eve Klotz',
        ("Carroll", "8F", "Marsh", "r"): 'William Marsh',

        # Cheshire
        ("Cheshire", "1", "Day", "r"): 'Kate Day',
        ("Cheshire", "1", "Benik", "r"): 'Peter Benik',
        ("Cheshire", "1", "Aldrich", "r"): 'Whitney Aldrich',
        ("Cheshire", "1", "Weber", "d"): 'Lucy McVitty Weber',
        ("Cheshire", "1", "Harvey", "d"): 'Cathryn A Harvey',
        ("Cheshire", "1", "Berch", "d"): 'Paul Berch',
        ("Cheshire", "1", "Abbott", "d"): 'Michael Abbott',
        ("Cheshire", "1", "Merkt", "r"): 'Richard Merkt',
        ("Cheshire", "10", "Thackston", "r"): 'Dick Thackston',
        ("Cheshire", "10", "Parshall", "d"): 'Lucius Parshall',
        ("Cheshire", "11", "Hunt", "r"): 'John Hunt',
        ("Cheshire", "11", "Qualey", "r"): 'Jim Qualey',
        ("Cheshire", "11", "Andersen", "d"): 'Gene Andersen',
        ("Cheshire", "11", "Martin", "d"): 'Patricia Martin',
        ("Cheshire", "12", "Gomarlo", "d"): 'Jennie Gomarlo',
        ("Cheshire", "12", "Faulkner", "d"): 'Barrett Faulkner',
        ("Cheshire", "12", "Malone", "r"): 'Stephen K Malone',
        ("Cheshire", "12", "Karasinski", "r"): 'Sly Karasinski',
        ("Cheshire", "13", "Quevedo", "d"): 'Natalie Quevedo',
        ("Cheshire", "13", "Kilanski", "r"): 'Ben Kilanski',
        ("Cheshire", "14F", "Santonastaso", "r"): 'Matthew Santonastaso',
        ("Cheshire", "14F", "Maneval", "d"): 'Andrew Maneval',
        ("Cheshire", "15F", "Tatro", "d"): 'Bruce Tatro',
        ("Cheshire", "15F", "Rhodes", "r"): 'Jennifer Rhodes',
        ("Cheshire", "16F", "Roach", "r"): 'Matt Roach',
        ("Cheshire", "16F", "Toll", "d"): 'Amanda Toll',
        ("Cheshire", "16F", "Schapiro", "d"): 'Joe Schapiro',
        ("Cheshire", "16F", "Sickels", "r"): 'Jerry Sickels',
        ("Cheshire", "2", "Nalevanko", "r"): 'Richard Nalevanko',
        ("Cheshire", "2", "Mann", "d"): 'John Mann',
        ("Cheshire", "3", "D'Arcy", "r"): "Robert D'Arcy",
        ("Cheshire", "3", "Eaton", "d"): 'Daniel Eaton',
        ("Cheshire", "4", "Welkowitz", "d"): 'Lawrence Welkowitz',
        ("Cheshire", "5", "Huston", "r"): 'Marilyn Huston',
        ("Cheshire", "5", "Bordenet", "d"): 'John Bordenet',
        ("Cheshire", "6", "Fox", "d"): 'Dru Fox',
        ("Cheshire", "6", "LaBrie", "r"): 'Kyle LaBrie',
        ("Cheshire", "7", "Call", "r"): 'Robert Call',
        ("Cheshire", "7", "Von Plinsky", "d"): 'Sparky Von Plinsky',
        ("Cheshire", "8", "Fenton", "d"): 'Donovan Fenton',
        ("Cheshire", "9", "Ley", "d"): 'Douglas Ley',
        ("Cheshire", "9", "Ames", "d"): 'Richard Ames',
        ("Cheshire", "9", "Plante", "r"): 'Leo Plante',
        ("Cheshire", "9", "Mattson", "r"): 'Rita Mattson',

        # Coos
        ("Coos", "1", "Dostie", "r"): 'Donald Dostie',
        ("Coos", "1", "Christianson", "d"): 'Bernice Christianson',
        ("Coos", "1", "Thompson", "r"): 'Dennis Thompson',
        ("Coos", "1", "Baker", "d"): 'Bob Baker',
        ("Coos", "2", "Roberge", "d"): 'Christopher Roberge',
        ("Coos", "2", "Davis", "r"): 'Arnold Davis',
        ("Coos", "3", "Kelley", "d"): 'Earnon Kelley',
        ("Coos", "3", "Noel", "d"): 'Henry Noel',
        ("Coos", "3", "Laflamme", "d"): 'Larry Laflamme',
        ("Coos", "3", "Evans", "r"): 'Mark Evans',
        ("Coos", "3", "Theberge", "r"): 'Robert Theberge',
        ("Coos", "3", "Light", "r"): 'Stuart Light',
        ("Coos", "4", "Merrick", "d"): 'Evalyn Merrick',
        ("Coos", "4", "Craig", "r"): 'Kevin Craig',
        ("Coos", "5", "Tucker", "d"): 'Edith Tucker',
        ("Coos", "5", "Greer", "r"): 'John Greer',
        ("Coos", "6", "Hatch", "d"): 'William Hatch',
        ("Coos", "7F", "Merner", "r"): 'Troy Merner',
        ("Coos", "7F", "Stocks", "d"): 'Gregor Stocks',

        # Grafton
        ("Grafton", "1", "Beaulier", "r"): 'Calvin Beaulier',
        ("Grafton", "1", "Sherrard", "d"): 'Sally Sherrard',
        ("Grafton", "1", "DePalma IV", "r"): 'Joseph DePalma IV',
        ("Grafton", "1", "Massimilla", "d"): 'Linda Massimilla',
        ("Grafton", "10", "Dontonville", "d"): 'Roger Dontonville',
        ("Grafton", "11", "Josephson", "d"): 'Timothy Josephson',
        ("Grafton", "11", "Folsom", "r"): 'Beth Folsom',
        ("Grafton", "12", "Hakken-Phillips", "d"): 'Mary Hakken-Phillips',
        ("Grafton", "12", "Muirhead", "d"): 'Russell Muirhead',
        ("Grafton", "12", "Murpy", "d"): 'James M Murphy',  # Misspelled
        ("Grafton", "12", "Nordgren", "d"): 'Sharon Nordgren',
        ("Grafton", "13", "Balog", "r"): 'Michael Balog',
        ("Grafton", "13", "Flanders", "r"): 'Joshua Flanders',
        ("Grafton", "13", "Sykes", "d"): 'George Sykes',
        ("Grafton", "13", "Abel", "d"): 'Richard Abel',
        ("Grafton", "13", "Almy", "d"): 'Susan Almy',
        ("Grafton", "13", "Stavis", "d"): 'Laurel Stavis',
        ("Grafton", "14F", "Simon", "r"): 'Matthew Simon',
        ("Grafton", "14F", "French", "d"): 'Elaine French',
        ("Grafton", "15F", "Rajsteter", "d"): 'Ed Rajsteter',
        ("Grafton", "15F", "Binford", "r"): 'David W Binford',
        ("Grafton", "16F", "Diggs", "d"): 'Francesca Diggs',
        ("Grafton", "16F", "Greeson", "r"): 'Jeffrey Greeson',
        ("Grafton", "17F", "Adjutant", "d"): 'Joshua Adjutant',
        ("Grafton", "17F", "Hughes", "r"): 'Kendall Hughes',
        ("Grafton", "2", "Peraino", "r"): 'Robert Peraino',
        ("Grafton", "2", "Egan", "d"): 'Timothy Egan',
        ("Grafton", "3", "Chapmon", "r"): 'Wes Chapmon',
        ("Grafton", "3", "Ruprecht", "d"): 'Denny Ruprecht',
        ("Grafton", "4", "Ladd", "r"): 'Roderick Ladd',
        ("Grafton", "4", "LoCascio", "d"): 'Don Locascio',
        ("Grafton", "5", "Stringham", "d"): 'Jerry Stringham',
        ("Grafton", "5", "Ham", "r"): 'Bonnie Ham',
        ("Grafton", "6", "Maes", "d"): 'Kevin Maes',
        ("Grafton", "6", "Sanborn", "r"): 'Gail Sanborn',
        ("Grafton", "7", "Alliegro", "r"): 'Mark Alliegro',
        ("Grafton", "7", "Osborne", "d"): 'Richard Osborne',
        ("Grafton", "8", "Kirk", "r"): 'George Kirk',
        ("Grafton", "8", "McLaughlin", "r"): 'Mike McLaughlin',
        ("Grafton", "8", "Benedetto", "r"): 'Steven Benedetto',
        ("Grafton", "8", "Smith", "d"): 'Suzanne Smith',
        ("Grafton", "8", "Weston", "d"): 'Joyce Weston',
        ("Grafton", "8", "Fellows", "d"): 'Sallie Fellows',
        ("Grafton", "9", "Berezhny", "r"): 'Lex Berezhny',
        ("Grafton", "9", "Gordon", "r"): 'Ned Gordon',
        ("Grafton", "9", "Fluehr-Lobban", "d"): 'Carolyn Fluehr-Lobban',
        ("Grafton", "9", "Mulholland", "d"): 'Catherine Mulholland',

        # Hillsborough
        ("Hillsborough", "1", "Porter", "d"): 'Marjorie Porter',
        ("Hillsborough", "1", "Valera", "r"): 'John Valera',
        ("Hillsborough", "1", "Fedolfi", "r"): 'Jim Fedolfi',
        ("Hillsborough", "1", "White", "d"): 'Susanne White',
        ("Hillsborough", "10", "Long", "d"): 'Patrick Long',
        ("Hillsborough", "10", "Jeudy", "d"): 'Jean Jeudy',
        ("Hillsborough", "10", "Beene", "r"): 'Holly Beene',
        ("Hillsborough", "11", "Hodgdon", "r"): 'Jason Hodgdon',
        ("Hillsborough", "11", "Hagala", "r"): 'Richard Hagala',
        ("Hillsborough", "11", "Knight", "d"): 'Nicole Klein-Knight',
        ("Hillsborough", "11", "Bouchard", "d"): 'Donald Bouchard',
        ("Hillsborough", "11", "Daniel", "l"): 'Robert Daniel',
        ("Hillsborough", "12", "Poisson", "r"): 'Sharon Poisson',
        ("Hillsborough", "12", "Amanda Bouldin", "d"): 'Amanda Bouldin',
        ("Hillsborough", "12", "Andrew Bouldin", "d"): 'Andrew Bouldin',
        ("Hillsborough", "12", "Spencer", "r"): 'Constance Spencer',
        ("Hillsborough", "13", "Gagne", "r"): 'Larry Gagne',
        ("Hillsborough", "13", "Infantine", "r"): 'William Infantine',
        ("Hillsborough", "13", "Hamilton", "d"): 'Christy Hamilton',
        ("Hillsborough", "13", "Dion", "d"): 'Darryl Dion',
        ("Hillsborough", "14", "Heath", "d"): 'Mary Heath',
        ("Hillsborough", "14", "Freitas", "d"): 'Mary Freitas',
        ("Hillsborough", "14", "Focht", "r"): 'Steve Focht',
        ("Hillsborough", "14", "Cole", "r"): 'Brian Cole',
        ("Hillsborough", "15", "Katsiantonis", "d"): 'Thomas Katsiantonis',
        ("Hillsborough", "15", "Warden", "r"): 'Mark Warden',
        ("Hillsborough", "15", "McNair", "r"): 'Macy McNair',
        ("Hillsborough", "15", "Connors", "d"): 'Erika Connors',
        ("Hillsborough", "16", "Shaw", "d"): 'Barbara Shaw',
        ("Hillsborough", "16", "Kliskey", "r"): 'Robert Kliskey',
        ("Hillsborough", "16", "Stefanik", "r"): 'Steven Stefanik',
        ("Hillsborough", "16", "Query", "d"): 'Joshua Query',
        ("Hillsborough", "17", "Hamer", "d"): 'Heidi Hamer',
        ("Hillsborough", "17", "Smith", "d"): 'Timothy Smith',
        ("Hillsborough", "17", "Simmons", "r"): 'Tammy Simmons',
        ("Hillsborough", "17", "Garthwaite", "r"): 'Dan Garthwaite',
        ("Hillsborough", "18", "Cornell", "d"): 'Patricia Cornell',
        ("Hillsborough", "18", "Chicoine", "r"): 'Brian Chicoine',
        ("Hillsborough", "18", "Griffith", "d"): 'Willis Griffith',
        ("Hillsborough", "18", "LeClear-Ping", "r"): 'Brittany LeClear-Ping',
        ("Hillsborough", "19", "Zackeroff", "d"): 'William Zackeroff',
        ("Hillsborough", "19", "Marston", "r"): 'Dick Marston',
        ("Hillsborough", "19", "Whitlock", "r"): 'Matt Whitlock',
        ("Hillsborough", "19", "Snow", "d"): 'Kendall Snow',
        ("Hillsborough", "2", "Cushman", "r"): 'Lean Cushman',
        ("Hillsborough", "2", "Hopper", "r"): 'Gary Hopper',
        ("Hillsborough", "2", "Girard", "d"): 'Robert Girard',
        ("Hillsborough", "2", "Erf", "r"): 'Keith Erf',
        ("Hillsborough", "2", "Paveglio", "d"): 'Jennifer Paveglio',
        ("Hillsborough", "2", "Cisto", "d"): 'Rachel Cisto',
        ("Hillsborough", "20", "Fordey", "d"): 'Nikki Fordey',
        ("Hillsborough", "20", "Lascelles", "r"): 'Richard Lascelles',
        ("Hillsborough", "20", "Boehm", "r"): 'Ralph Boehm',
        ("Hillsborough", "21", "Notter", "r"): 'Jeanine Notter',
        ("Hillsborough", "21", "Tausch", "r"): 'Lindsay Tausch',
        ("Hillsborough", "21", "Balcom", "r"): 'Jack Balcom',
        ("Hillsborough", "21", "Blasek", "r"): 'Melissa Blasek',
        ("Hillsborough", "21", "Healey", "r"): 'Bob Healy',
        ("Hillsborough", "21", "Hinch", "r"): 'Dick Hinch',
        ("Hillsborough", "21", "Mayville", "r"): 'Mary Mayville',
        ("Hillsborough", "21", "Mooney", "r"): 'Maureen Mooney',
        ("Hillsborough", "21", "Sylvester", "d"): 'Joseph Sylvester',
        ("Hillsborough", "21", "Thomas", "d"): 'Wendy Thomas',
        ("Hillsborough", "21", "M. Murphy", "d"): 'Mackenzie Murphy',
        ("Hillsborough", "21", "N. Murphy", "d"): 'Nancy Murphy',
        ("Hillsborough", "21", "Parente", "d"): 'Cynthia Parente',
        ("Hillsborough", "21", "Rung", "d"): 'Rosemarie Rung',
        ("Hillsborough", "21", "B. Stack", "d"): 'Bryce Stack',
        ("Hillsborough", "21", "K. Stack", "d"): 'Kathryn Stack',
        ("Hillsborough", "22", "Hansen", "r"): 'Peter Hansen',
        ("Hillsborough", "22", "Pray", "r"): 'Danielle Pray',
        ("Hillsborough", "22", "Labranche", "d"): 'Tony Labranche',
        ("Hillsborough", "22", "Coughlin", "r"): 'Pamela Coughlin',
        ("Hillsborough", "22", "Murray", "d"): 'Megan Murray',
        ("Hillsborough", "22", "Veilleux", "d"): 'Daniel Veilleux',
        ("Hillsborough", "23", "Sheehan", "r"): 'Vanessa Sheehan',
        ("Hillsborough", "23", "Petrigno", "d"): 'Peter Petrigno',
        ("Hillsborough", "23", "Perez", "d"): 'Maria Perez',
        ("Hillsborough", "23", "Thornton", "r"): 'Michael Thornton',
        ("Hillsborough", "23", "Lloyd", "d"): 'Alexander Lloyd',
        ("Hillsborough", "23", "Salmon", "d"): 'Herb Salmon',
        ("Hillsborough", "23", "King", "r"): 'Bill King',
        ("Hillsborough", "23", "Tourangeau", "r"): 'Steve Tourangeau',
        ("Hillsborough", "24", "Vann", "d"): 'Ivy Vann',
        ("Hillsborough", "24", "Pilcher", "r"): 'David Pilcher',
        ("Hillsborough", "24", "Leishman", "d"): 'Peter Leishman',
        ("Hillsborough", "24", "Maidment", "r"): 'Christopher Maidment',
        ("Hillsborough", "25", "Kelley", "r"): 'Diane Kelley',
        ("Hillsborough", "25", "Somero", "r"): 'Paul Somero',
        ("Hillsborough", "25", "Lynch", "d"): 'Laura Lynch',
        ("Hillsborough", "25", "Crooker", "d"): 'Elizabeth Crooker',
        ("Hillsborough", "26", "Pauer", "r"): 'Diane Pauer',
        ("Hillsborough", "26", "Wheeler", "d"): 'Chris Wheeler',
        ("Hillsborough", "26", "Rater", "d"): 'Brian Rater',
        ("Hillsborough", "26", "Lewicke", "r"): 'John Lewicke',
        ("Hillsborough", "27", "Werner", "r"): 'David Werner',
        ("Hillsborough", "27", "Harris", "d"): 'Tom Harris',
        ("Hillsborough", "27", "McGhee", "d"): 'Kat McGhee',
        ("Hillsborough", "27", "Homola", "r"): 'Susan Homola',
        ("Hillsborough", "28", "Lanzara", "r"): 'Tom Lanzara',
        ("Hillsborough", "28", "Russell", "r"): 'Rosemary Russell',
        ("Hillsborough", "28", "Ferreira", "r"): 'Elizabeth Ferreira',
        ("Hillsborough", "28", "Cohen", "d"): 'Bruce Cohen',
        ("Hillsborough", "28", "Schmidt", "d"): 'Jan Schmidt',
        ("Hillsborough", "28", "Bordy", "d"): 'William Bordy',
        ("Hillsborough", "29", "Mercer", "r"): 'Brian Mercer',
        ("Hillsborough", "29", "R. Newman", "d"): 'Ray Newman',
        ("Hillsborough", "29", "McCarthy", "r"): 'Michael McCarthy',
        ("Hillsborough", "29", "S. Newman", "d"): 'Sue Newman',
        ("Hillsborough", "29", "Bergeron", "d"): 'Paul Bergeron',
        ("Hillsborough", "29", "Smith", "r"): 'Julie Smith',
        ("Hillsborough", "3", "Pickering", "d"): 'Dan Pickering',
        ("Hillsborough", "3", "Bedard", "r"): 'David Bedard',
        ("Hillsborough", "30", "Schoneman", "r"): 'David Schoneman',
        ("Hillsborough", "30", "Dutzy", "d"): 'Sherry Dutzy',
        ("Hillsborough", "30", "Hohensee", "r"): 'Doris Hohensee',
        ("Hillsborough", "30", "Vail", "d"): 'Suzanne Vail',
        ("Hillsborough", "30", "Klee", "d"): 'Patricia Klee',
        ("Hillsborough", "30", "Coffman", "r"): 'Howard Coffman',
        ("Hillsborough", "31", "Terrell", "r"): 'Ryan Terrell',
        ("Hillsborough", "31", "Baumeister", "r"): 'Joost Baumeister',
        ("Hillsborough", "31", "Espitia", "d"): 'Manny Espitia',
        ("Hillsborough", "31", "Laughton", "d"): 'Stacie-Marie Laughton',
        ("Hillsborough", "31", "Cote", "d"): 'David Cote',
        ("Hillsborough", "31", "Van Twuyver", "r"): 'Elizabeth van Twuyver',
        ("Hillsborough", "32", "Toomey", "d"): 'Dan Toomey',
        ("Hillsborough", "32", "Nutting-Wong", "d"): 'Allison Nutting-Wong',
        ("Hillsborough", "32", "Pedersen", "d"): 'Michael Pedersen',
        ("Hillsborough", "32", "Johnson", "r"): 'Paula Johnson',
        ("Hillsborough", "32", "Lothrop", "r"): 'Di Lothrop',
        ("Hillsborough", "32", "Cole", "r"): 'Joseph Cole',
        ("Hillsborough", "33", "Booras", "d"): 'Efstathia Booras',
        ("Hillsborough", "33", "King", "d"): 'Mark King',
        ("Hillsborough", "33", "Decatur", "r"): 'Ed Decatur',
        ("Hillsborough", "33", "T. Scully", "r"): 'Teresa Scully',
        ("Hillsborough", "33", "K. Scully", "r"): 'Kevin Scully',
        ("Hillsborough", "33", "Nutter-Upham", "d"): 'Fran Nutter-Upham',
        ("Hillsborough", "34", "Stevens", "d"): 'Deb Stevens',
        ("Hillsborough", "34", "Hogan", "r"): 'Edith Hogan',
        ("Hillsborough", "34", "Moran, Jr.", "d"): 'Melbourne Moran Jr.',
        ("Hillsborough", "34", "Casey", "r"): 'Jacqueline Casey',
        ("Hillsborough", "34", "Hall", "r"): 'Charlie Hall',
        ("Hillsborough", "34", "Sofikitis", "d"): 'Catherine Sofikitis',
        ("Hillsborough", "35", "Hutsteiner", "r"): 'Paul Hutsteiner',
        ("Hillsborough", "35", "Cleaver", "d"): 'Skip Cleaver',
        ("Hillsborough", "35", "Silva", "r"): 'Peter Silva',
        ("Hillsborough", "35", "Mangipudi", "d"): 'Latha Mangipudi',
        ("Hillsborough", "35", "Telerski", "d"): 'Laura Telerski',
        ("Hillsborough", "35", "DiPaolo", "r"): 'Anthony DiPaolo',
        ("Hillsborough", "36", "Harriott-Gathright", "d"): 'Linda Harriott-Gathright',
        ("Hillsborough", "36", "O'Brien, Sr.", "d"): "Michael O'Brien Sr.",
        ("Hillsborough", "36", "Jack", "d"): 'Martin Jack',
        ("Hillsborough", "36", "Gouveia", "r"): 'Tyler Gouveia',
        ("Hillsborough", "36", "Ohm", "r"): 'Bill Ohm',
        ("Hillsborough", "36", "O'Brien", "r"): "William O'Brien",
        ("Hillsborough", "37", "T. Lekas", "r"): 'Tony Lekas',
        ("Hillsborough", "37", "Nunez", "r"): 'Hershel Nunez',
        ("Hillsborough", "37", "L. Ober", "r"): 'Lynne Ober',
        ("Hillsborough", "37", "R. Ober", "r"): 'Russell Ober',
        ("Hillsborough", "37", "Prout", "r"): 'Andrew Prout',
        ("Hillsborough", "37", "Renzullo", "r"): 'Andrew Renzulio',
        ("Hillsborough", "37", "Rice", "r"): 'Kimberly Rice',
        ("Hillsborough", "37", "Smith", "r"): 'Denise Smith',
        ("Hillsborough", "37", "Ulery", "r"): 'Jordan Ulery',
        ("Hillsborough", "37", "Greene", "r"): 'Bob Greene',
        ("Hillsborough", "37", "A. Lekas", "r"): 'Alicia Lekas',
        ("Hillsborough", "37", "Gagnon", "d"): 'Brett Gagnon',
        ("Hillsborough", "37", "Hennessey", "d"): 'David Hennessey',
        ("Hillsborough", "37", "Jauregui", "d"): 'Beatriz Jauregui',
        ("Hillsborough", "37", "Katsos", "d"): 'Steven Katsos',
        ("Hillsborough", "37", "Lynde", "d"): 'Harold Lynde',
        ("Hillsborough", "37", "Paliy", "d"): 'Lana Paliy',
        ("Hillsborough", "37", "Sherman", "d"): 'Robert Sherman',
        ("Hillsborough", "37", "Urrutia", "d"): 'Alejandro Urrutia',
        ("Hillsborough", "37", "Wyatt", "d"): 'Timothy Wyatt',
        ("Hillsborough", "37", "Blue", "d"): 'Barbara Blue',
        ("Hillsborough", "37", "Brucker", "d"): 'Nancy Brucker',
        ("Hillsborough", "38F", "Hyland", "d"): 'Stephanie Hyland',
        ("Hillsborough", "38F", "Bosman", "d"): 'James Bosman',
        ("Hillsborough", "38F", "Colcombe", "r"): 'Riche Colcombe',
        ("Hillsborough", "38F", "Creighton", "r"): 'Jim Creighton',
        ("Hillsborough", "39F", "Burt", "r"): 'John Burt',
        ("Hillsborough", "39F", "Evans", "d"): 'Gary Evans',
        ("Hillsborough", "4", "Williams", "d"): 'Kermit Williams',
        ("Hillsborough", "4", "Bernet", "d"): 'Jennifer Bernet',
        ("Hillsborough", "4", "Post", "r"): 'Lisa Post',
        ("Hillsborough", "4", "Kofalt", "r"): 'Jim Kofalt',
        ("Hillsborough", "40F", "Ammon", "r"): 'Keith Ammon',
        ("Hillsborough", "40F", "Ming", "d"): 'Ben Ming',
        ("Hillsborough", "41F", "Sanborn", "r"): 'Laurie Sanborn',
        ("Hillsborough", "41F", "Nash", "d"): 'Lisa Nash',
        ("Hillsborough", "42F", "Wilhelm", "d"): 'Matt Wilhelm',
        ("Hillsborough", "42F", "Senneville", "r"): 'Julie Senneville',
        ("Hillsborough", "42F", "Harris", "r"): 'Phillip Harris',
        ("Hillsborough", "42F", "Chretien", "d"): 'Jacqueline Chretien',
        ("Hillsborough", "43F", "Baroody", "d"): 'Benjamin Baroody',
        ("Hillsborough", "43F", "Herbert", "d"): 'Christopher Herbert',
        ("Hillsborough", "43F", "Lachance", "r"): 'Joseph Lachance',
        ("Hillsborough", "43F", "Bradley", "d"): 'Amy L Bradley',
        ("Hillsborough", "43F", "Freeman", "r"): 'Lisa Freeman',
        ("Hillsborough", "43F", "McConville", "r"): 'Kirk McConville',
        ("Hillsborough", "44F", "Berry", "r"): 'Ross Berry',
        ("Hillsborough", "44F", "Moulton", "d"): 'Candace Moulton',
        ("Hillsborough", "44F", "McLean", "r"): 'Mark McLean',
        ("Hillsborough", "44F", "Curran", "d"): 'Robert Curran',
        ("Hillsborough", "45F", "Van Houten", "d"): 'Connie Van Houten',
        ("Hillsborough", "45F", "Beaulieu", "d"): 'Jane Beaulieu',
        ("Hillsborough", "45F", "Gonzalez", "r"): 'Carlos Gonzalez',
        ("Hillsborough", "45F", "Higgins", "r"): 'Amanda Higgins',
        ("Hillsborough", "5", "Foster", "r"): 'William Foster',
        ("Hillsborough", "5", "Mombourquette", "d"): 'Donna Mombourquette',
        ("Hillsborough", "5", "Woodbury", "d"): 'David Woodbury',
        ("Hillsborough", "5", "Griffin", "r"): 'Gerald Griffin',
        ("Hillsborough", "6", "McCune", "d"): 'Robin McCune',
        ("Hillsborough", "6", "Griffin", "r"): 'Barbara Griffin',
        ("Hillsborough", "6", "Gunski", "r"): 'Michael Gunski',
        ("Hillsborough", "6", "Plette", "r"): 'Fred Plett',  # Misspelled
        ("Hillsborough", "6", "Rouillard", "r"): 'Claire Rouillard',
        ("Hillsborough", "6", "Bruno", "d"): 'Richard Bruno',
        ("Hillsborough", "6", "Craig", "d"): 'Jim Craig',
        ("Hillsborough", "6", "Lanza", "d"): 'Judi Lanza',
        ("Hillsborough", "6", "Renfrew-Hebert", "d"): 'Melanie Renfrew-Hebert',
        ("Hillsborough", "6", "Alexander", "r"): 'Joe Alexander Jr',
        ("Hillsborough", "7", "Graham", "r"): 'John Graham',
        ("Hillsborough", "7", "Paradis", "r"): 'Emma Paradis',
        ("Hillsborough", "7", "Kenda", "r"): 'Stephen Kenda',
        ("Hillsborough", "7", "Danielson", "r"): 'David Danielson',
        ("Hillsborough", "7", "Gorski", "r"): 'Ted Gorski',
        ("Hillsborough", "7", "Gould", "r"): 'Linda Gould',
        ("Hillsborough", "7", "Kelsey", "r"): 'Niki Kelsey',
        ("Hillsborough", "7", "Rombeau", "d"): 'Cattherine Rombeau',
        ("Hillsborough", "7", "Schmitt", "d"): 'Cheri Schmitt',
        ("Hillsborough", "7", "Dong", "d"): 'Daniel Dong',
        ("Hillsborough", "7", "Mullen", "d"): 'Sue Mullen',
        ("Hillsborough", "7", "Potvin", "d"): 'Shana Potvin',
        ("Hillsborough", "8", "DiIulio", "r"): 'Paul DiIulio',
        ("Hillsborough", "8", "Goldner", "r"): 'Dan Goldner',
        ("Hillsborough", "8", "Goley", "d"): 'Jeffrey Goley',
        ("Hillsborough", "8", "Langley", "d"): 'Diane Langley',
        ("Hillsborough", "9", "Chase", "r"): 'Tyler Chase',
        ("Hillsborough", "9", "Whitfield", "r"): 'Doug Whitfield',
        ("Hillsborough", "9", "DiSilvestro", "d"): 'Linda DiSilvestro',
        ("Hillsborough", "9", "Piedra", "d"): 'Iz Piedra',

        # Merrimack
        ("Merrimack", "1", "Wells", "d"): 'Ken Wells',
        ("Merrimack", "1", "Andrus", "r"): 'Louise Andrus',
        ("Merrimack", "10", "Luneau", "d"): 'David Luneau',
        ("Merrimack", "10", "Wallner", "d"): 'Mary Jane Wallner',
        ("Merrimack", "10", "Myler", "d"): 'Mel Myler',
        ("Merrimack", "10", "Dellas", "r"): 'Alexandros Dellas',
        ("Merrimack", "10", "French VI", "r"): 'John French VI',
        ("Merrimack", "10", "Ean", "r"): 'Pamela Ean',
        ("Merrimack", "11", "Newell", "r"): 'David Newell',
        ("Merrimack", "11", "Shurtleff", "d"): 'Stephen Shurtleff',
        ("Merrimack", "12", "Myers", "r"): 'Patrice Myers',
        ("Merrimack", "12", "Lane", "d"): 'Connie Lane',
        ("Merrimack", "13", "Bahuma", "r"): 'Samuel Bahuma',
        ("Merrimack", "13", "Richards", "d"): 'Beth Richards',
        ("Merrimack", "14", "Davey", "r"): 'Donna Davey',
        ("Merrimack", "14", "MacKay", "d"): 'Jim MacKay',
        ("Merrimack", "15", "McCartney", "r"): 'Michelle McCartney',
        ("Merrimack", "15", "Gallager", "d"): 'Eric Gallager',
        ("Merrimack", "16", "Bertrand", "r"): 'Robert G Bertrand',
        ("Merrimack", "16", "T. Soucy", "d"): 'Timothy Soucy',
        ("Merrimack", "17", "Wazir", "d"): 'Safiya Wazir',
        ("Merrimack", "17", "D. Soucy", "r"): 'Dennis Soucy',
        ("Merrimack", "18", "Bongambe", "r"): 'Claude Bongambe',  # Withdrew but appeared on ballot
        ("Merrimack", "18", "Schultz", "d"): 'Kris Schultz',
        ("Merrimack", "19", "Cate", "r"): 'Jonathan Cate',
        ("Merrimack", "19", "Bartlett", "d"): 'Christy Bartlett',
        ("Merrimack", "2", "Smith", "d"): 'Terry Smith',
        ("Merrimack", "2", "Testerman", "r"): 'Dave Testerman',
        ("Merrimack", "2", "Burns", "d"): 'Scott Burns',
        ("Merrimack", "2", "Mason", "r"): 'James Mason',
        ("Merrimack", "20", "Doherty", "d"): 'David Doherty',
        ("Merrimack", "20", "Schuett", "d"): 'Dianne Schuett',
        ("Merrimack", "20", "Hanson, Jr.", "d"): 'Clinton Hanson Jr.',
        ("Merrimack", "20", "White", "r"): 'Nick White',
        ("Merrimack", "20", "Gagyi", "r"): 'Peter Gagyi',
        ("Merrimack", "20", "Seaworth", "r"): 'Brian Seaworth',
        ("Merrimack", "21", "Klose", "r"): 'John Klose',
        ("Merrimack", "21", "Frambach", "d"): 'Mary Frambach',
        ("Merrimack", "21", "Curley", "d"): 'Hugh Curley',
        ("Merrimack", "21", "Allard", "r"): 'James Allard',
        ("Merrimack", "22", "Pitaro", "r"): 'Matthew Pitaro',
        ("Merrimack", "22", "Coolidge", "d"): 'David A Coolidge',
        ("Merrimack", "23", "Fox", "d"): 'Samantha Fox',
        ("Merrimack", "23", "Woods", "d"): 'Gary Woods',
        ("Merrimack", "23", "Walz", "d"): 'Mary Beth Walz',
        ("Merrimack", "23", "Martin", "r"): 'John Martin',
        ("Merrimack", "23", "Plante", "r"): 'Raymond Plante',
        ("Merrimack", "23", "Markova", "r"): 'Mariya Markova',
        ("Merrimack", "24", "Gurung", "d"): 'Madalasa Gurung',
        ("Merrimack", "24", "Kozlowski", "d"): 'Harry Kozlowski',
        ("Merrimack", "24", "Martins", "d"): 'Kathleen Martins',
        ("Merrimack", "24", "Walsh", "r"): 'Thomas Walsh',
        ("Merrimack", "24", "Yakubovich", "r"): 'Michael Yakubovich',
        ("Merrimack", "24", "Boyd", "r"): 'Stephen Boyd',
        ("Merrimack", "24", "Leavitt", "r"): 'John Leavitt',
        ("Merrimack", "25F", "Wells", "r"): 'Natalie Wells',
        ("Merrimack", "25F", "Minton", "d"): 'Faith Minton',
        ("Merrimack", "26F", "Carey", "d"): 'Lorrie Carey',
        ("Merrimack", "26F", "Pearl", "r"): 'Howard Pearl',
        ("Merrimack", "27F", "Visconti", "r"): 'Mike Visconti',
        ("Merrimack", "27F", "Stevens", "r"): 'Japhet Stevens',
        ("Merrimack", "27F", "Ellison", "d"): 'Art Ellison',
        ("Merrimack", "27F", "McWilliams", "d"): 'Rebecca McWilliams',
        ("Merrimack", "28F", "Rogers", "d"): 'Katherine Rogers',
        ("Merrimack", "28F", "Georgevits", "r"): 'Andrew Georgevits',
        ("Merrimack", "29F", "Cahill-Yeaton", "d"): 'Miriam Cahill-Yeaton',
        ("Merrimack", "29F", "McGuire", "r"): 'Carol McGuire',
        ("Merrimack", "3", "Cross", "r"): 'Kenna Cross',
        ("Merrimack", "3", "Hill", "r"): 'Gregory Hill',
        ("Merrimack", "3", "Fulweiler", "d"): 'Joyce Fulweiler',
        ("Merrimack", "3", "Duncan", "d"): 'Sheena Duncan',
        ("Merrimack", "4", "Prieto", "r"): 'Victor Prieto',
        ("Merrimack", "4", "Schamberg", "d"): 'Tom Schamberg',
        ("Merrimack", "5", "Richard", "r"): 'Roger Richard',
        ("Merrimack", "5", "Wolf", "r"): 'Dan Wolf',
        ("Merrimack", "5", "Ebel", "d"): 'Karen Ebel',
        ("Merrimack", "5", "Zurheide", "d"): 'Karen Zurheide',
        ("Merrimack", "6", "Caplan", "d"): 'Tony Caplan',
        ("Merrimack", "6", "Pimentel", "d"): 'Rod Pimentel',
        ("Merrimack", "6", "Parker", "r"): 'James Parker',
        ("Merrimack", "6", "Dunne", "r"): 'Thomas Dunne Jr.',
        ("Merrimack", "7", "Carson", "d"): 'Clyde Carson',
        ("Merrimack", "7", "Kennedy", "r"): 'Margaret Kennedy',
        ("Merrimack", "8", "Alicea", "d"): 'Caroletta Alicea',
        ("Merrimack", "8", "Forsythe", "r"): 'Robert Forsythe',
        ("Merrimack", "8", "Rick Devoid (w-in)", "NONPARTISAN"): 'Rick Devoid (w-in)',
        ("Merrimack", "9", "Cambrils", "r"): 'Jose Cambrils',
        ("Merrimack", "9", "Moffett", "r"): 'Michael Moffett',
        ("Merrimack", "9", "Bergevin", "d"): 'Leslie Bergevin',
        ("Merrimack", "9", "Friedrich", "d"): 'Lois Friedrich',

        # Rockingham
        ("Rockingham", "1", "Tudor", "r"): 'Paul Tudor',
        ("Rockingham", "1", "Chase", "d"): 'Tom Chase',
        ("Rockingham", "10", "Acton", "r"): 'Dennis Acton',
        ("Rockingham", "10", "Douglas", "d"): 'Ellen Marie Douglas',
        ("Rockingham", "11", "Litchfield", "r"): 'Melissa Litchfield',
        ("Rockingham", "11", "McConnell", "d"): 'Liz McConnell',
        ("Rockingham", "12", "Wallace", "r"): 'Scott Wallace',
        ("Rockingham", "12", "West", "d"): 'Diana West',
        ("Rockingham", "13", "Collins", "d"): 'Mindy Funke Collins',
        ("Rockingham", "13", "LaValley", "d"): 'Jim LaValley',
        ("Rockingham", "13", "Tidd", "d"): 'Trisha Tidd',
        ("Rockingham", "13", "Warnock", "d"): 'Laurie Warnock',
        ("Rockingham", "13", "Guthrie", "r"): 'Joe Guthrie',
        ("Rockingham", "13", "Welch", "r"): 'David Welch',
        ("Rockingham", "13", "Green", "r"): 'Dennis Green',
        ("Rockingham", "13", "Weyler", "r"): 'Ken Weyler',
        ("Rockingham", "14", "Harb", "r"): 'Robert Harb',
        ("Rockingham", "14", "Major", "r"): 'Norman Major',
        ("Rockingham", "14", "Torosian", "r"): 'Peter Torosian',
        ("Rockingham", "14", "Hamblen", "d"): 'George Hamblen',
        ("Rockingham", "14", "Bishop", "d"): 'Nancy Bishop',
        ("Rockingham", "14", "Delfino", "d"): 'Kate Delfino',
        ("Rockingham", "14", "Galloway", "d"): 'Kay Galloway',
        ("Rockingham", "14", "DeSimone", "r"): 'Debra DeSimone',
        ("Rockingham", "15", "Bartlett", "d"): 'Robert Bartlett',
        ("Rockingham", "15", "Melvin, Sr.", "r"): 'Charles Melvin Sr.',
        ("Rockingham", "16", "Oldak", "d"): 'Peter Oldak',
        ("Rockingham", "16", "Bernardy", "r"): 'J D Bernardy',
        ("Rockingham", "17", "Scanlon", "r"): 'Carolyn Scanlon',
        ("Rockingham", "17", "DiLorenzo", "d"): 'Charlotte DiLorenzo',
        ("Rockingham", "17", "Read", "d"): 'Ellen Read',
        ("Rockingham", "17", "Cahill", "d"): 'Michael Cahill',
        ("Rockingham", "18", "Stone", "r"): 'Greg Stone',
        ("Rockingham", "18", "Smith", "r"): 'William A Smith',
        ("Rockingham", "18", "Duncan", "r"): 'Edward Duncan',
        ("Rockingham", "18", "Wikstrom", "r"): 'Carl Wikstrom',
        ("Rockingham", "18", "Gilman", "d"): 'Julie Gilman',
        ("Rockingham", "18", "Paige", "d"): 'Mark Paige',
        ("Rockingham", "18", "Bunker", "d"): 'Lisa Bunker',
        ("Rockingham", "18", "Grossman", "d"): 'Gaby Grossman',
        ("Rockingham", "19", "Abrami", "r"): 'Patrick Abrami',
        ("Rockingham", "19", "Jeffrey", "r"): 'Amy Jeffrey',
        ("Rockingham", "19", "Altschiller", "d"): 'Debra Altschiller',
        ("Rockingham", "19", "Scrafford", "d"): 'Jennifer Scrafford',
        ("Rockingham", "2", "Boisvert", "d"): 'Richard Boisvert',
        ("Rockingham", "2", "Rosenfield", "d"): 'Avis Rosenfield',
        ("Rockingham", "2", "Bershtein", "r"): 'Alan Bershtein',
        ("Rockingham", "2", "Verville", "r"): 'Kevin Verville',
        ("Rockingham", "2", "Spillane", "r"): 'James Spillane',
        ("Rockingham", "2", "Messier", "d"): 'Jocelyn Messier',
        ("Rockingham", "20", "O'Keefe", "d"): "Patricia O'Keefe",
        ("Rockingham", "20", "Flynn", "d"): 'Louis Flynn',
        ("Rockingham", "20", "Marrow", "d"): 'Greg Marrow',
        ("Rockingham", "20", "Baxter", "r"): 'Tim Baxter',
        ("Rockingham", "20", "Khan", "r"): 'Aboul Khan',
        ("Rockingham", "20", "Harley", "r"): 'Tina Harley',
        ("Rockingham", "21", "Sheffert", "r"): 'Ken Sheffert',
        ("Rockingham", "21", "Emerick", "r"): 'Tracy Emerick',
        ("Rockingham", "21", "Hagen", "r"): 'David Hagen',
        ("Rockingham", "21", "Hurst", "r"): 'Sharleene Hurst',
        ("Rockingham", "21", "Edgar", "d"): 'Michael Edgar',
        ("Rockingham", "21", "Harake", "d"): 'Katherine Harake',
        ("Rockingham", "21", "Cushing", "d"): 'Robert Cushing',
        ("Rockingham", "21", "Loughman", "d"): 'Tom Loughman',
        ("Rockingham", "22", "Schultz", "r"): 'Kirsten Larsen Schultz',
        ("Rockingham", "22", "Maggiore", "d"): 'Jim Maggiore',
        ("Rockingham", "23", "Malloy", "d"): 'Dennis Malloy',
        ("Rockingham", "23", "Boynton", "r"): 'Jenni Boynton',
        ("Rockingham", "24", "Tucker", "r"): 'Julie Tucker',
        ("Rockingham", "24", "Meyer", "r"): 'Joanne Meyer',
        ("Rockingham", "24", "Grote", "d"): 'Jaci Grote',
        ("Rockingham", "24", "Murray", "d"): 'Kate Murray',
        ("Rockingham", "25", "Pantelakos", "d"): 'Laura Pantelakos',
        ("Rockingham", "26", "McBeath", "d"): 'Rebecca McBeath',
        ("Rockingham", "26", "Knox", "r"): 'Alexandria Knox',
        ("Rockingham", "27", "Somssich", "d"): 'Peter Somssich',
        ("Rockingham", "28", "Taylor-Hollandbeck", "r"): 'Cytnhia Taylor-Hollandbeck',
        ("Rockingham", "28", "Ward", "d"): 'Gerry Ward',
        ("Rockingham", "29", "Meuse", "d"): 'David Meuse',
        ("Rockingham", "3", "Kolifrath", "d"): 'Diane Kolifrath',
        ("Rockingham", "3", "Dodge", "r"): 'Dustin Dodge',
        ("Rockingham", "3", "Pratt", "r"): 'Kevin Pratt',
        ("Rockingham", "3", "Ayer", "r"): 'Paul Ayer',
        ("Rockingham", "3", "DiTommaso", "d"): 'Michael DiTommaso',
        ("Rockingham", "3", "Garnham", "d"): 'Dennis Garnham',
        ("Rockingham", "30F", "Cali-Pitts", "d"): 'Jacqueline Cali-Pitts',
        ("Rockingham", "30F", "Lukacz", "r"): 'Tom Lukacz',
        ("Rockingham", "31F", "Marsh", "r"): 'Henry Mash',
        ("Rockingham", "31F", "Hamblet", "d"): 'Joan Hamblet',
        ("Rockingham", "32F", "Roy", "r"): 'Terry Roy',
        ("Rockingham", "32F", "Rafter", "d"): 'Hal Rafter',
        ("Rockingham", "33F", "Yokela", "r"): 'Josh Yokela',
        ("Rockingham", "33F", "Turer", "d"): 'Eric Turer',
        ("Rockingham", "34F", "Pearson", "r"): 'Mark Pearson',
        ("Rockingham", "34F", "DeMio", "d"): 'Lisa DeMio',
        ("Rockingham", "35F", "Moore", "d"): 'Robert Moore',
        ("Rockingham", "35F", "Hobson", "r"): 'Deborah Hobson',
        ("Rockingham", "36F", "Simpson", "d"): 'Alexis Simpson',
        ("Rockingham", "36F", "Gray", "r"): 'Daniel Gray',
        ("Rockingham", "37F", "Abramson", "r"): 'Max Abramson',
        ("Rockingham", "37F", "Andrews-Ahearn", "d"): 'E Elaine Andrews-Ahearn',
        ("Rockingham", "4", "Van Zandt", "d"): 'Jane Van Zandt',
        ("Rockingham", "4", "Norman", "d"): 'Russell Norman',
        ("Rockingham", "4", "Krohn", "d"): 'Matthew Krohn',
        ("Rockingham", "4", "Geiger", "d"): 'Ben Geiger',
        ("Rockingham", "4", "True", "r"): 'Chris True',
        ("Rockingham", "4", "Piemonte", "r"): 'Tony Piemonte',
        ("Rockingham", "4", "Osborne", "r"): 'Jason Osborne',
        ("Rockingham", "4", "D'Angelo", "d"): "Michael D'Angelo",
        ("Rockingham", "4", "Edwards", "r"): 'Jess Edwards',
        ("Rockingham", "4", "Ford", "r"): 'Oliver Ford',
        ("Rockingham", "5", "Thomas", "r"): 'Doug Thomas',
        ("Rockingham", "5", "Baldasaro", "r"): 'Alfred Baldasaro',
        ("Rockingham", "5", "Dolan", "r"): 'Tom Dolan',
        ("Rockingham", "5", "Lundgren", "r"): 'David Lundgren',
        ("Rockingham", "5", "MacDonald", "r"): 'Wayne MacDonald',
        ("Rockingham", "5", "McKinney", "r"): 'Betsy McKinney',
        ("Rockingham", "5", "Packard", "r"): 'Sherman Packard',
        ("Rockingham", "5", "Warner", "d"): 'Anne Warner',
        ("Rockingham", "5", "Combes", "d"): 'Ted Combes',
        ("Rockingham", "5", "Leathurby", "d"): 'Mack Leathurby',
        ("Rockingham", "5", "Piette", "d"): 'Luisa Piette',
        ("Rockingham", "5", "P. Skudlarek", "d"): 'Paul Skudlarek',
        ("Rockingham", "5", "R. Skudlarek", "d"): 'Robin Skudlarek',
        ("Rockingham", "5", "Smith", "d"): 'Martha Smith',
        ("Rockingham", "6", "Tripp", "r"): 'Richard Tripp',
        ("Rockingham", "6", "Copp", "r"): 'Anne Copp',
        ("Rockingham", "6", "Katakiores", "r"): 'Phyllis Katsakiores',  # Misspelled
        ("Rockingham", "6", "Kimball", "r"): 'Mary Ann Kimball',
        ("Rockingham", "6", "Layon", "r"): 'Erica Layon',
        ("Rockingham", "6", "Love", "r"): 'David Love',
        ("Rockingham", "6", "Milz", "r"): 'David Milz',
        ("Rockingham", "6", "O'Brien", "r"): "Katherine Prudhomme O'Brien",
        ("Rockingham", "6", "Pearson", "r"): 'Stephen Pearson',
        ("Rockingham", "6", "Potucek", "r"): 'John Potucek',
        ("Rockingham", "6", "Wood", "d"): 'Thomas Wood',
        ("Rockingham", "6", "Dattner-Levy", "d"): 'Amy Dattner-Levy',
        ("Rockingham", "6", "Doolittle", "d"): 'Paul Doolittle',
        ("Rockingham", "6", "Eisner", "d"): 'Mary Eisner',
        ("Rockingham", "6", "Ingram", "d"): 'Owen Ingram',
        ("Rockingham", "6", "Sawyer-Moge", "d"): 'Michelle Sawyer-Moge',
        ("Rockingham", "6", "Spencer", "d"): 'Erin Spencer',
        ("Rockingham", "6", "Till", "d"): 'Mary Till',
        ("Rockingham", "6", "Vargas", "d"): 'Beatrice Vargas',
        ("Rockingham", "6", "West", "d"): 'Johnathan West',
        ("Rockingham", "6", "Willis", "und"): 'Brenda Willis',
        ("Rockingham", "7", "Griffin", "r"): 'Mary Griffin',
        ("Rockingham", "7", "Soti", "r"): 'Julius Soti',
        ("Rockingham", "7", "Lynn", "r"): 'Robert J Lynn',
        ("Rockingham", "7", "McMahon", "r"): 'Charles McMahon',
        ("Rockingham", "7", "St.Laurent", "d"): 'Kristi St Laurent',
        ("Rockingham", "7", "Roman", "d"): 'Valerie Roman',
        ("Rockingham", "7", "Singureanu", "d"): 'Ioana Singureanu',
        ("Rockingham", "7", "Azibert", "d"): 'Henri Azibert',
        ("Rockingham", "8", "Sytek", "r"): 'John Sytek',
        ("Rockingham", "8", "Vandecasteele", "r"): 'Susan Vandecasteele',
        ("Rockingham", "8", "Abbas", "r"): 'Daryl Abbas',
        ("Rockingham", "8", "Doucette", "r"): 'Fred Doucette',
        ("Rockingham", "8", "Elliott", "r"): 'Robert Elliott',
        ("Rockingham", "8", "Gay", "r"): 'Betty Gay',
        ("Rockingham", "8", "Janigian", "r"): 'John Janigian',
        ("Rockingham", "8", "McBride, Jr.", "r"): 'Everett McBride Jr.',
        ("Rockingham", "8", "Sweeney", "r"): 'Joe Sweeney',
        ("Rockingham", "8", "Thibault", "d"): 'Maureen Thibault',
        ("Rockingham", "8", "Wright", "d"): 'Bonnie Wright',
        ("Rockingham", "8", "Davis", "d"): 'Gregory Davis',
        ("Rockingham", "8", "Dillingham", "d"): 'Sara Dillingham',
        ("Rockingham", "8", "Iannalfo", "d"): 'Cam Iannalfo',
        ("Rockingham", "8", "Karibian", "d"): 'Claire Karibian',
        ("Rockingham", "8", "Lewis", "d"): 'Sean Lewis',
        ("Rockingham", "8", "Loranger", "d"): 'Donna Loranger',
        ("Rockingham", "8", "Muollo", "d"): 'Jacqueline Muollo',
        ("Rockingham", "9", "Belanger", "r"): 'Cody Belanger',
        ("Rockingham", "9", "Vose", "r"): 'Michael Vose',
        ("Rockingham", "9", "Tillman", "d"): 'Gregory Tillman',
        ("Rockingham", "9", "Vallone", "d"): 'Mark Vallone',

        # Strafford
        ("Strafford", "1", "Bailey", "r"): 'Glenn Bailey',
        ("Strafford", "1", "Hayward", "r"): 'Peter Hayward',
        ("Strafford", "1", "Brown", "d"): 'Larry Brown',
        ("Strafford", "10", "Ankarberg", "r"): 'Aidan Ankarberg',
        ("Strafford", "11", "Clement", "r"): 'Jonathan Clement',
        ("Strafford", "11", "Grassie", "d"): 'Chuck Grassie',
        ("Strafford", "12", "Kittredge", "r"): 'Mac Kittredge',
        ("Strafford", "12", "DeVito", "d"): 'Anni DeVito',
        ("Strafford", "13", "Childs", "r"): 'Debra Childs',
        ("Strafford", "13", "Conley", "d"): 'Casey Conley',
        ("Strafford", "14", "Cooper", "r"): 'Mary Ann Cooper',
        ("Strafford", "14", "Fargo", "d"): 'Kristina Fargo',
        ("Strafford", "15", "Blouin", "r"): 'Tyler Blouin',
        ("Strafford", "15", "Oxaal", "d"): 'Ariel Oxaal',
        ("Strafford", "16", "Morgan", "r"): 'Steve Morgan',
        ("Strafford", "16", "Frost", "d"): 'Sherry Frost',
        ("Strafford", "17", "Vincent", "d"): 'Kenneth Vincent',
        ("Strafford", "17", "Treleaven", "d"): 'Susan Treleaven',
        ("Strafford", "17", "Bixby", "d"): 'Peter Bixby',
        ("Strafford", "17", "Castaldo", "r"): 'Michael Castaldo',
        ("Strafford", "17", "Hastings", "r"): 'Edwina Hastings',
        ("Strafford", "17", "Allie", "r"): 'Simon Allie',
        ("Strafford", "18", "Rich", "d"): 'Cecilia Rich',
        ("Strafford", "18", "Cannon", "d"): 'Gerri Cannon',
        ("Strafford", "18", "McMahon", "r"): 'Steven Douglas McMahon',
        ("Strafford", "18", "Spencer", "r"): 'Matthew Spencer',
        ("Strafford", "18", "Carnes", "r"): 'Jodi Lavoie-Carnes',
        ("Strafford", "18", "Chase", "d"): 'Wendy Chase',
        ("Strafford", "19F", "Schmidt", "d"): 'Peter Schmidt',
        ("Strafford", "19F", "Burr", "r"): 'William Burr',
        ("Strafford", "2", "Horgan", "r"): 'James Horgan',
        ("Strafford", "2", "Pitre", "r"): 'Joseph Pitre',
        ("Strafford", "2", "Krasner", "d"): 'Emmanuel Krasner',
        ("Strafford", "20F", "Wyrsch", "r"): 'Steven Wyrsch',
        ("Strafford", "20F", "Southworth", "d"): 'Tom Southworth',
        ("Strafford", "21F", "Munck", "r"): 'Philip Munck',
        ("Strafford", "21F", "Sandler", "d"): 'Catt Sandler',
        ("Strafford", "22F", "Kaczynski, Jr.", "r"): 'Thomas Kaczynski Jr.',
        ("Strafford", "22F", "Higgins", "d"): 'Peg Higgins',
        ("Strafford", "23F", "Keans", "d"): 'Sandra Keans',
        ("Strafford", "23F", "Groen", "r"): 'Fenton Groen',
        ("Strafford", "24F", "Delemus", "r"): 'Susan DeLemus',
        ("Strafford", "24F", "Minihan", "d"): 'Jeremiah Minihan',
        ("Strafford", "25F", "Gourgue", "d"): 'Amanda Gourgue',
        ("Strafford", "25F", "Hannon", "r"): 'Joe Hannon',
        ("Strafford", "3", "Howard", "d"): 'Heath Howard',
        ("Strafford", "3", "Wuelper", "r"): 'Kurt Wuelper',
        ("Strafford", "3", "Allard", "d"): 'Jeff Allard',
        ("Strafford", "3", "Harrington", "r"): 'Michael Harrington',
        ("Strafford", "4", "Turcotte", "r"): 'Len Turcotte',
        ("Strafford", "4", "Wilson", "r"): 'Jenny Wilson',
        ("Strafford", "4", "Levesque", "d"): 'Cassandra Levesque',
        ("Strafford", "4", "Towne", "d"): 'Matthew Towne',
        ("Strafford", "5", "Bugbee", "r"): 'Scott Bugbee',
        ("Strafford", "5", "Salloway", "d"): 'Jeffrey Salloway',
        ("Strafford", "6", "Spang", "d"): 'Judith Spang',
        ("Strafford", "6", "Lamoureux", "r"): 'Cheryl Lamoureux',
        ("Strafford", "6", "McDermott", "r"): 'Bonnie McDermott',
        ("Strafford", "6", "Zetterstrom", "r"): 'Cliff Zetterstrom',
        ("Strafford", "6", "Ziegra", "r"): 'James Ziegra',
        ("Strafford", "6", "Racic", "r"): 'Mark Racic',
        ("Strafford", "6", "Kenney", "d"): 'Cam Kenney',
        ("Strafford", "6", "Smith", "d"): 'Marjorie Smith',
        ("Strafford", "6", "Wall", "d"): 'Janet Wall',
        ("Strafford", "6", "Horrigan", "d"): 'Timothy Horrigan',
        ("Strafford", "7", "deBree", "r"): 'Harrison deBree',
        ("Strafford", "7", "Fontneau", "d"): 'Timothy Fontneau',
        ("Strafford", "8", "Barkin", "r"): 'Kalmen Barkin',
        ("Strafford", "8", "Ellis", "d"): 'Donna Ellis',
        ("Strafford", "9", "Ransom", "d"): 'Tom Ransom',
        ("Strafford", "9", "Newton", "r"): 'Clifford Newton',

        # Sullivan
        ("Sullivan", "1", "V. Drye", "r"): 'Virginia Drye',
        ("Sullivan", "1", "Sullivan", "d"): 'Brian Sullivan',
        ("Sullivan", "1", "Oxenham", "d"): 'Lee Walker Oxenham',
        ("Sullivan", "1", "McIntire", "r"): 'Tany McIntire',
        ("Sullivan", "10F", "Cloutier", "d"): 'John Cloutier',
        ("Sullivan", "10F", "Stone", "r"): 'Jonathan Stone',
        ("Sullivan", "11F", "Henry", "d"): 'Mary Henry',
        ("Sullivan", "11F", "S. Smith", "r"): 'Steven Smith',
        ("Sullivan", "2", "Bettencourt", "r"): 'Don Bettencourt',
        ("Sullivan", "2", "Gottling", "d"): 'Sue Gottling',
        ("Sullivan", "3", "O'Hearne", "d"): "Andrew O'Hearne",
        ("Sullivan", "3", "Lozito", "r"): 'Patrick Lozito',
        ("Sullivan", "4", "Merchant", "d"): 'Gary Merchant',
        ("Sullivan", "4", "LaCasse, Sr.", "r"): 'Paul LaCasse Sr',
        ("Sullivan", "5", "Draper", "d"): 'Liza Draper',
        ("Sullivan", "5", "Stapleton", "r"): 'Walter Stapleton',
        ("Sullivan", "6", "Callum", "r"): 'John Callum',
        ("Sullivan", "6", "Franklin", "d"): 'Peter Franklin',
        ("Sullivan", "6", "Rollins", "r"): 'Skip Rollins',
        ("Sullivan", "6", "Flint", "d"): 'Larry Flint',
        ("Sullivan", "7", "Aron", "r"): 'Judy Aron',
        ("Sullivan", "7", "Istel", "d"): 'Claudia Istel',
        ("Sullivan", "8", "Spilsbury", "r"): 'Walter Spilsbury',
        ("Sullivan", "8", "Streeter", "d"): 'John Streeter',
        ("Sullivan", "9F", "Menard", "l"): 'Tobin Menard',
        ("Sullivan", "9F", "Tanner", "d"): 'Linda Tanner',
        ("Sullivan", "9F", "M. Drye", "r"): 'Margaret Drye',
        }

    data = data.reset_index(drop=True)
    for (key, candidate) in replacements.items():
        county, district, short_candidate, party = key
        rows = data.index[((data['County'] == county) & (data['District'] == district)
                          & (data['Candidate'] == short_candidate) & (data['Party'] == party))]
        for row in rows:
            data.iat[row, 1] = candidate

    # Fix typo in candidates
    data['Candidate'] = data['Candidate'].str.replace('Scattter', 'Scatter')

    # Finally, standardize some precincts
    data['Precinct'] = data['Precinct'].replace({
        r'\*': '',
        r'Atkinson & Gilmanton Ac Gt': 'Atkinson and Gilmanton Academy Grant',
        r'Wd': 'Ward',
        r"Low and Burbank's Gt.": "Low and Burbank's Grant",
        r"Thomp and Mes's Pur": "Thompson and Meserve's Purchase"
        }, regex=True).str.strip()

    data = data.sort_values(['County', 'District', 'Precinct', 'Stage']).reset_index(drop=True)
    return data


def load_file_county(file: str) -> DataFrame:
    county = re.search('county-(?P<county>.*)-2020', file)['county'].capitalize()
    raw_data = pd.read_excel(file, sheet_name=0, header=None)

    # We manually fix a few nan's for county commissioner. For other offices they will just be
    # fillna'd with 0. We do this manually because most of the nan's for county commissioner
    # correspond to situation where the race did not happen in a precinct, as they are based
    # on district
    if county == 'Belknap':
        raw_data.iat[52, 5] = 0
        # We also fix a nan cell that should indicate Reg. of Probate
        raw_data.iat[23, 4] = 'Reg. of Probate'
    elif county == 'Carroll':
        raw_data.iat[37, 9] = 0
    elif county == 'Coos':
        raw_data.iat[91, 3] = 0

    dfs = dict()
    rows = list()

    def _save_dataframe(rows):
        df = pd.DataFrame(rows)
        if '' in df.columns:
            df = df.drop(labels='', axis=1)
        df = df.dropna(axis=1, how='all').reset_index(drop=True)
        df = df.ffill(axis=0)
        for (i, row) in df.iterrows():
            row = row.replace({'': np.nan, '2020-11-03 00:00:00': np.nan})
            if pd.isna(row[0]) and ',' not in str(row[1]):
                row = row.ffill()
            df.iloc[i] = row
        # Merge two first rows if header has 3 rows
        if pd.isna(df.iloc[2][0]):
            df.iloc[1] = (df.iloc[0].fillna('') + ' ' + df.iloc[1]).str.strip()
            df = df.drop(0)
        race = f's{len(dfs)}'
        dfs[race] = df
        rows.clear()

    # Preparse
    for (i, row) in raw_data.iterrows():
        new_row = list()
        for value in row:
            if pd.isna(value):
                new_row.append('')
            else:
                new_row.append(str(value).strip())

        if i < 2:
            # Skip title rows
            continue
        if set(new_row) == {''}:
            # Ignore empty rows...
            # Unless we have buffered rows already (which happen if races dont include a totals row)
            if not rows:
                continue
            _save_dataframe(rows)
            continue
        if new_row[0].upper() == 'TOTALS':
            _save_dataframe(rows)
            continue
        rows.append(new_row)

    new_file = file.replace("raw/", "raw/new-")
    if new_file.endswith('xls'):
        new_file += 'x'

    with pd.ExcelWriter(new_file) as writer:
        for (sheet_name, df) in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)

    # Now we are ready to merge
    data_dict = pd.read_excel(new_file, sheet_name=None, header=[0, 1])
    # Remove temp file
    os.remove(new_file)
    file_data = pd.DataFrame()
    for sheet in data_dict.values():
        for column in sheet.columns.copy():
            if set(sheet[column].fillna('')) in [{''}, {'NO ELECTION', ''}]:
                sheet = sheet.drop(labels=column, axis=1)

        sheet.columns = ['Precinct'] + [cell for cell in sheet.columns[1:]]
        sheet = sheet.melt(id_vars=['Precinct'], var_name='Office_Candidate', value_name='Votes')
        sheet['Office'] = [x[0] for x in sheet['Office_Candidate']]
        sheet['Candidate'] = [x[1] for x in sheet['Office_Candidate']]
        sheet = EC.split_column(sheet, 'Candidate',
                                r'(?P<Candidate>.*), (?P<Party>[^ ]+)',
                                maintaining_columns=['Candidate'],
                                empty_value='NONPARTISAN',)
        sheet = EC.split_column(sheet, 'Office',
                                r'(?P<Office>.*) Dist(rict|\.)?( No\.)? (?P<District>.*)',
                                maintaining_columns=['Office'],
                                empty_value='')
        sheet['County'] = county
        sheet['Stage'] = 'GEN'
        sheet = sheet[['Precinct', 'Votes', 'Office', 'Candidate', 'Party', 'District', 'County',
                       'Stage']]
        file_data = file_data.append(sheet)

    file_data = file_data.reset_index(drop=True).sort_values(['Office', 'District'])
    return file_data


def load_files_county() -> DataFrame:
    files = [
        'county-belknap-2020.xls',
        'county-carroll-2020.xls',
        'county-cheshire-2020.xls',
        'county-coos-2020.xls',
        'county-grafton-2020.xlsx',
        'county-hillsborough-2020.xls',
        'county-merrimack-2020.xls',
        'county-rockingham-2020.xls',
        'county-strafford-2020.xls',
        'county-sullivan-2020.xls',
        ]

    data = pd.DataFrame()
    for file in files:
        print(f'*Reading file raw/{file}...')
        file_data = load_file_county(f'raw/{file}')
        data = data.append(file_data)
        print(f'Read file raw/{file}...')

    # Standardize office for the sake of additional clearing
    data['Office'] = data['Office'].replace({
        r'Reg\. of Deeds': 'Register of Deeds',
        r'Reg\. of Probate': 'Register of Probate',
        r'COUNTY COMMISSIONERS': 'County Commissioners',
        }, regex=True)

    # Drop nans that correspond to county commissioners (race did not occur in precinct)
    data = data[~((data['Office'] == 'County Commissioners') &
                  (data['Votes'].isna()))]
    # And fill the remaining with 0s (race did happen, value was not recorded)
    data = data.fillna(0)
    data['Votes'] = data['Votes'].astype(int)

    # County offices did not provide full names
    # .......sigh
    replacements = {
        # Most names are obtained from
        # https://www.wmur.com/article/new-hampshire-county-race-results-2020/34541028 and
        # https://sos.nh.gov/media/e55ioibt/general-election-winners.pdf
        # Except links immediately preceding a line
        ("Belknap", "Attorney", "", "Livernois", "r/d"): 'Andrew Livernois',
        ("Belknap", "County Commissioners", "1", "Spanos", "r"): 'Peter John Spanos',
        ("Belknap", "County Commissioners", "1", "Brunette", "d"): 'Peter R Brunette',
        ("Belknap", "County Commissioners", "2", "Waring", "r"): 'Glen A Waring',
        ("Belknap", "Register of Deeds", "", "McGrath", "r"): 'Judy McGrath',
        ("Belknap", "Register of Deeds", "", "Davis", "d"): 'Johnna Davis',
        ("Belknap", "Register of Probate", "", "Glassman", "r"): 'Alan Glassman',
        ("Belknap", "Register of Probate", "", "Thomas", "d"): 'Lynn Thomas',
        ("Belknap", "Sheriff", "", "Wright", "r"): 'Bill Wright',
        ("Belknap", "Sheriff", "", "Robinson", "d"): 'Richard Robinson',
        ("Belknap", "Treasurer", "", "Muzzey", "r/d"): 'Michael G Muzzey',
        ("Carroll", "Attorney", "", "O'Rourke-Andruzzi", "d/r"): "Michaela O'Rourke Andruzzi",
        ("Carroll", "County Commissioners", "2", "Tessari", "r"): 'Kimberly J Tessari',
        ("Carroll", "County Commissioners", "2", "Pustell", "d"): 'Bob Pustell',
        ("Carroll", "County Commissioners", "3", "Plache", "r"): 'Matthew Plache',
        ("Carroll", "County Commissioners", "3", "Albee", "d"): 'Chip Albee',
        ("Carroll", "Register of Deeds", "", "Scott", "r/d"): 'Lisa Scott',
        ("Carroll", "Register of Probate", "", "Lavender", "r"): 'Meg Lavender',
        ("Carroll", "Sheriff", "", "Richardi", "r/d"): 'Domenic M Richardi',
        ("Carroll", "Treasurer", "", "Costello", "r/d"): 'Joseph L Costello',
        ("Cheshire", "Attorney", "", "McLaughlin", "d"): 'D Chris McLaughlin',
        ("Cheshire", "County Commissioners", "1", "DiBernardo", "r"): 'Skipper DiBernardo',
        ("Cheshire", "County Commissioners", "1", "Wozmak", "d"): 'Jack Wozmak',
        ("Cheshire", "County Commissioners", "2", "Clark", "d"): 'Terry M Clark',
        ("Cheshire", "Register of Deeds", "", "Tilton", "d"): 'Anna Z Tilton',
        ("Cheshire", "Register of Probate", "", "LaPlante", "d"): 'Jeremy LaPlante',
        ("Cheshire", "Sheriff", "", "DiMezzo", "r"): 'Aria DiMezzo',
        ("Cheshire", "Sheriff", "", "Rivera", "d"): 'Eli Rivera',
        ("Cheshire", "Sheriff", "", "Earl Nelson (w-in)", "NONPARTISAN"): 'Earl Nelson (w-in)',
        ("Cheshire", "Treasurer", "", "Cartwright", "r"): 'Joseph H Cartwright',
        ("Cheshire", "Treasurer", "", "Weed", "d"): 'Charles Weed',
        ("Coos", "Attorney", "", "McCormick", "d"): 'John G McCormick',
        ("Coos", "County Commissioners", "1", "Grenier", "d"): 'Paul R Grenier',
        ("Coos", "County Commissioners", "3", "Gorman", "r"): 'Ray Gorman',
        ("Coos", "Register of Deeds", "", "Rideout", "r"): 'Leon H Rideout',
        ("Coos", "Register of Deeds", "", "Kelley", "d"): 'Kathleen U Kelley',
        ("Coos", "Register of Probate", "", "Peterson", "r"): 'Terri L Peterson',
        ("Coos", "Sheriff", "", "Valerino", "r/d"): 'Brian L Valerino',
        ("Coos", "Treasurer", "", "Collins", "r"): 'Suzanne L Collins',
        ("Grafton", "Attorney", "", "Hornick", "d/r"): 'Marcie Hornick',
        ("Grafton", "County Commissioners", "1", "Piper", "d"): 'Wendy Piper',
        ("Grafton", "County Commissioners", "2", "Dutile", "r"): 'Douglas R Dutile',
        ("Grafton", "County Commissioners", "2", "Lauer", "d"): 'Linda D Lauer',
        ("Grafton", "County Commissioners", "3", "Ahern, Jr.", "r"): 'Omer C Ahern Jr.',
        ("Grafton", "County Commissioners", "3", "Morris", "d"): 'Marcia Morris',
        ("Grafton", "Register of Deeds", "", "Monahan", "d/r"): 'Kelly Jean Monahan',
        ("Grafton", "Register of Probate", "", "Mirski w-in", "NONPARTISAN"):
            'Paul M Mirski (w-in)',
        ("Grafton", "Register of Probate", "", "Teszler w-in", "NONPARTISAN"):
            'Teszler (w-in)',  # Could not find their name :(
        ("Grafton", "Register of Probate", "", "Townsend w-in", "NONPARTISAN"):
            'Townsend (w-in)',  # Could not find their name :(
        # https://www.townofthornton.org/sites/g/files/vyhlif5081/f/pages/
        # unofficial_results_november_general_election.pdf
        ("Grafton", "Register of Probate", "", "Tyrell w-in", "NONPARTISAN"):
            'Jim Tyrell (w-in)',
        ("Grafton", "Sheriff", "", "Stiegler", "d/r"): 'Jeff Stiegler',
        ("Grafton", "Treasurer", "", "Hill", "d"): 'Karen Liot Hill',
        ("Hillsborough", "Attorney", "", "Coughlin", "r"): 'John J Coughlin',
        ("Hillsborough", "Attorney", "", "Conlon", "d"): 'Michael Conlon',
        ("Hillsborough", "Attorney", "", "Sarwark", "l"): 'Nicholas Sarwark',
        ("Hillsborough", "County Commissioners", "1", "Pappas", "r"): 'Toni Pappas',
        ("Hillsborough", "County Commissioners", "1", "Hopwood", "d"): 'Jon Claude Hopwood',
        ("Hillsborough", "County Commissioners", "2", "Soucy", "r"): 'Michael Soucy',
        ("Hillsborough", "County Commissioners", "2", "Hansberry", "d"): 'Daniel Hansberry',
        ("Hillsborough", "County Commissioners", "3", "Rowe", "r"): 'Robert H Rowe',
        ("Hillsborough", "County Commissioners", "3", "Ketteridge", "d"): 'Suzanne Ketteridge',
        ("Hillsborough", "Register of Deeds", "", "Flanagan", "r"): 'Jack Flanagan',
        ("Hillsborough", "Register of Deeds", "", "Crowell", "d"): 'Mary Ann Crowell',
        ("Hillsborough", "Register of Probate", "", "Moreau", "r"): 'Elizabeth Ann Moreau',
        ("Hillsborough", "Register of Probate", "", "Ropp", "d"): 'Elizabeth Ropp',
        ("Hillsborough", "Sheriff", "", "Connelly", "r"): 'Christopher Connelly',
        ("Hillsborough", "Sheriff", "", "Barry", "d"): 'Bill Barry',
        ("Hillsborough", "Treasurer", "", "Fredette", "r"): 'David G Fredette',
        ("Hillsborough", "Treasurer", "", "Bryk", "d"): 'William Bryk',
        ("Hillsborough", "Treasurer", "", "Manzo", "l"): 'Richard Manzo',
        ("Merrimack", "Attorney", "", "Halvorsen", "r"): 'Paul Halvorsen',
        ("Merrimack", "Attorney", "", "Davis", "d"): 'Robin Davis',
        ("Merrimack", "County Commissioners", "1", "Reardon", "d"): 'Tara Reardon',
        ("Merrimack", "County Commissioners", "2", "Trachy", "r"): 'Stuart D Trachy',
        ("Merrimack", "County Commissioners", "2", "Ratzki", "d"): 'Mario Ratzki',
        ("Merrimack", "Register of Deeds", "", "Cragin", "d/r"): 'Susan Cragin',
        ("Merrimack", "Register of Probate", "", "Maltzie", "r"): 'Scott Maltzie',
        ("Merrimack", "Register of Probate", "", "Bradstreet", "d"): 'Jane Bradstreet',
        ("Merrimack", "Sheriff", "", "Crawford", "r"): 'Dennis Crawford',
        ("Merrimack", "Sheriff", "", "Croft", "d"): 'David A Croft',
        ("Merrimack", "Treasurer", "", "Heath", "r"): 'Mary Heath',
        ("Merrimack", "Treasurer", "", "Donnelly", "d"): 'Kathleen G Donnelly',
        ("Rockingham", "Attorney", "", "Conway", "r"): 'Patricia Conway',
        ("Rockingham", "Attorney", "", "Briden", "d"): 'Steven Briden',
        ("Rockingham", "County Commissioners", "1", "St. James", "r"): 'Kevin St James',
        ("Rockingham", "County Commissioners", "1", "Coyle", "d"): 'Kate Coyle',
        ("Rockingham", "County Commissioners", "3", "Chirichiello", "r"): 'Brian K Chirichiello',
        ("Rockingham", "County Commissioners", "3", "D'Angelo", "d"): "Stephen D'Angelo",
        ("Rockingham", "Register of Deeds", "", "Stacey", "r"): 'Cathy Stacey',
        ("Rockingham", "Register of Deeds", "", "McCord", "d"): 'Michael McCord',
        ("Rockingham", "Register of Probate", "", "Tweedie", "r"): 'Ray Tweedie',
        ("Rockingham", "Register of Probate", "", "Davidson", "d"): 'Bob Davidson',
        ("Rockingham", "Sheriff", "", "Massahos", "r"): 'Chuck Massahos',
        ("Rockingham", "Sheriff", "", "Rivard", "d"): 'Patrick William Rivard',
        ("Rockingham", "Treasurer", "", "Priestley", "r"): 'Scott Priestley',
        ("Rockingham", "Treasurer", "", "Quinn", "d"): 'Ty Quinn',
        ("Strafford", "Attorney", "", "Velardi", "d/r"): 'Thomas P Velardi',
        ("Strafford", "County Commissioners", "", "Rollo", "d/r"): 'Deanna Rollo',
        ("Strafford", "County Commissioners", "", "Maglaras", "d/r"): 'George Maglaras',
        ("Strafford", "County Commissioners", "", "Watson", "d/r"): 'Robert J Watson',
        ("Strafford", "Register of Deeds", "", "Berube", "d/r"): 'Catherine A Berube',
        ("Strafford", "Register of Probate", "", "Bay", "d"): 'Luz Bay',
        ("Strafford", "Sheriff", "", "Callaghan", "r"): 'Paul Callaghan',
        ("Strafford", "Sheriff", "", "Brave", "d"): 'Mark Brave',
        ("Strafford", "Treasurer", "", "Arnold", "d/r"): 'Pamela J Arnold',
        ("Sullivan", "Attorney", "", "Hathaway", "r/d"): 'Marc Hathaway',
        ("Sullivan", "County Commissioners", "1", "Osgood", "r"): 'Joe Osgood',
        ("Sullivan", "County Commissioners", "1", "Gagnon", "d"): 'Raymond Gagnon',
        ("Sullivan", "County Commissioners", "2", "Nelson", "r"): 'Ben Nelson',
        ("Sullivan", "County Commissioners", "2", "Irwin", "d"): "Virginia O'Brien Irwin",
        ("Sullivan", "Register of Deeds", "", "Gibson", "r/d"): 'Janet A Gibson',
        ("Sullivan", "Register of Probate", "", "Ward", "r"): 'Rodd Ward',
        ("Sullivan", "Register of Probate", "", "Eames", "d"): 'Kathleen Eames',
        ("Sullivan", "Sheriff", "", "Simonds", "r/d"): 'John P Simonds',
        ("Sullivan", "Treasurer", "", "Sanderson", "r"): 'Michael Sanderson',
    }

    data = data.reset_index(drop=True)
    for (key, candidate) in replacements.items():
        county, office, district, short_candidate, party = key
        rows = data.index[((data['County'] == county) & (data['Office'] == office)
                           & (data['District'] == district)
                           & (data['Candidate'] == short_candidate) & (data['Party'] == party))]
        for row in rows:
            data.iat[row, 3] = candidate

    # Finally, standardize some precincts
    data['Precinct'] = data['Precinct'].replace({
        r'\*': '',
        r'Atk. & Gilm. Ac. Gt.': 'Atkinson and Gilmanton Academy Grant',
        r"Low & Burbank's Gt.": "Low and Burbank's Grant",
        r"Second College Gt.": "Second College Grant",
        r"Thompson & Mes's Pur.": "Thompson and Meserve's Purchase",
        r"Wentworth's Loc.": "Wentworth's Location",
        }, regex=True).str.strip()

    data = data.reset_index(drop=True)
    return data


def load_all_data(prepare_pickle=True) -> DataFrame:
    if prepare_pickle:
        federal_1_data = load_files_federal_1()
        federal_2_data = load_files_federal_2()
        state_senate_data = load_files_state_senate()
        state_house_data = load_files_state_house()
        county_data = load_files_county()

        # federal_2_data lacks county information, so we obtain that from type1_data
        federal_2_data = federal_2_data.join(
            federal_1_data[['Precinct', 'County']].drop_duplicates().set_index(['Precinct']),
            on=['Precinct'])

        # state_senate_data lacks county information, so we obtain that from type1_data
        state_senate_data = state_senate_data.join(
            federal_1_data[['Precinct', 'County']].drop_duplicates().set_index(['Precinct']),
            on=['Precinct'])

        data = pd.DataFrame().append([federal_1_data, federal_2_data, state_senate_data,
                                      state_house_data, county_data])
        data = data.reset_index(drop=True)
        data.to_pickle('raw_NH20.pkl')

    data = pd.read_pickle('raw_NH20.pkl')
    return data


def make_state(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `state`...')
    # State is New Hampshire by definition
    data = EC.state.add_state_codes(data, state='New Hampshire')

    print('Parsed NH20 `state`.')
    return data


def make_precinct(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `precinct`...')
    # Data is pulled straight from `Precinct`.
    data['precinct'] = data['Precinct'].astype(str).str.strip().str.upper()
    print('Parsed NH20 `precinct`.')
    return data


def make_office(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `office`...')

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
        r'PRESIDENT.*': 'US PRESIDENT',
        r'UNITED STATES SENATOR.*': 'US SENATE',
        r'CONGRESSIONAL': 'US HOUSE',
        r'GOVERNOR AND LT GOVERNOR': 'GOVERNOR AND LIEUTENANT GOVERNOR',
        r'ATTORNEY': 'COUNTY ATTORNEY',
        r'COUNTY COMMISSIONERS': 'COUNTY COMMISIONER',
        r'REGISTER OF DEEDS': 'COUNTY REGISTER OF DEEDS',
        r'REGISTER OF PROBATE': 'COUNTY REGISTER OF PROBATE',
        r'SHERIFF': 'COUNTY SHERIFF',
        r'TREASURE': 'COUNTY TREASURE'
        }

    data['temp_office'] = data['temp_office'].replace(standard_names, regex=True)

    # We will remove magnitude later
    print('Partially parsed NH20 `office` (1/2).')
    return data


def make_party_detailed(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `party_detailed...`')

    # Data is pulled from `Party`
    data['party_detailed'] = data['Party']

    # Standardize
    data['party_detailed'] = data['party_detailed'].replace({
        '^d$': 'DEMOCRAT',
        '^r$': 'REPUBLICAN',
        'l(ib)?': 'LIBERTARIAN',
        'r/d': 'REPUBLICAN-DEMOCRAT',
        'd/r': 'DEMOCRAT-REPUBLICAN',
        'und': 'INDEPENDENT',

        'NONPARTISAN': '',  # Only candidates that show NONPARTISAN are writeins
        }, regex=True)

    # Writein candidates don't have party
    print('Parsed NH20 `party_detailed`.')
    return data


def make_party_simplified(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `party_simplified...`')
    # We can use the details from the recently parsed NH20 party_detailed for this.
    data['party_simplified'] = data['party_detailed'].replace({
        'REPUBLICAN-DEMOCRAT': 'OTHER',
        'DEMOCRAT-REPUBLICAN': 'OTHER',
        'INDEPENDENT': 'NONPARTISAN',
        })

    print('Parsed NH20 `party_simplified`.')
    return data


def make_mode(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `mode`...')
    # All vote totals are TOTAL
    data['mode'] = 'TOTAL'

    print('Parsed NH20 `mode`.')
    return data


def make_votes(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `votes...`')
    # Data is pulled straight from `Votes`
    data['votes'] = pd.to_numeric(data['Votes'], errors='raise')

    print('Parsed NH20 `votes`.')
    return data


def make_county_name(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `county_name`...')
    # Data is pulled straight from `County` and upper cased
    data['county_name'] = data['County'].str.upper()

    print('Parsed NH20 `county_name`.')
    return data


def make_county_fips(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `county_fips`...')
    # Use recently obtained `county_name` field and list of county fips codes
    data['county_fips'] = EC.county_fips.parse_fips_from_name(data)

    print('Parsed NH20 `county_fips`.')
    return data


def make_jurisdiction_name(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `jurisdiction_name`...')
    # `jurisdiction_name` is given in precinct. We strip out ward information however
    data['jurisdiction_name'] = data['precinct'].replace({
        ' WARD.*': '',
        }, regex=True)

    print('Parsed NH20 `jurisdiction_name`.')
    return data


def make_jurisdiction_fips(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `jurisdiction_fips`...')
    # Use recently obtained `jurisdiction_name` field and list of jurisdiction fips codes
    # Of note is Coos County uses slightly different names in jurisdiction-fips-csv, so we
    # must manually consider their equivalent names in data.

    coos_fips = {
        "BEAN'S GRANT": 3300704100,
        "BEAN'S PURCHASE": 3300704260,
        "CAMBRIDGE": 3300708420,
        "CHANDLER'S PURCHASE": 3300711220,
        "CRAWFORD'S PURCHASE": 3300716100,
        "CUTT'S GRANT": 3300716660,
        "DIX'S GRANT": 3300718340,
        "DIXVILLE": 3300718420,
        "ERVING'S LOCATION": 3300725180,
        "GREEN'S GRANT": 3300731780,
        "HADLEY'S PURCHASE": 3300732420,
        "KILKENNY": 3300739940,
        "LOW AND BURBANK'S GRANT": 3300743620,
        "MARTIN'S LOCATION": 3300746020,
        "MILLSFIELD": 3300748260,
        "ODELL": 3300757860,
        "PINKHAM'S GRANT": 3300761620,
        "SARGENT'S PURCHASE": 3300767860,
        "SUCCESS": 3300774500,
        "THOMPSON AND MESERVE'S PURCHASE": 3300776580,
        "WENTWORTH'S LOCATION": 3300780740,
        }

    data['jurisdiction_fips'] = EC.jurisdiction_fips.parse_fips_from_name(
        data, additional=coos_fips)

    print('Parsed NH20 `jurisdiction_fips`.')
    return data


def make_candidate(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `candidate...`')
    # Data is pulled from Candidate and uppercased
    data['temp_candidate'] = data['Candidate'].str.upper()

    # First, remove any extraneous whitespace/characters
    data['temp_candidate'] = data['temp_candidate'].str.strip().replace({
        r' ( )+': ' ',
        r'\.': '',
        }, regex=True)

    # For presidential candidates, we just record the president's name
    data['temp_candidate'] = data['temp_candidate'].replace({
        'BIDEN.*': 'JOSEPH R BIDEN',
        'JORGENSEN.*': 'JO JORGENSEN',
        'TRUMP.*': 'DONALD J TRUMP',
        }, regex=True)

    # Standardize a few names
    data['temp_candidate'] = data['temp_candidate'].replace({
        r'SCATTER': 'WRITEIN'
        }, regex=True)

    # We now have sufficient information to drop writeins with 0 votes
    data = data[~(
        (data['party_detailed'] == '')
        & (data['temp_candidate'] != 'WRITEIN')
        & (data['votes'] == 0)
        )].reset_index(drop=True)

    # We will remove write in marks later
    print('Partially parsed NH20 `candidate` (1/2).')
    return data


def make_district(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `district`...')

    # Data is pulled from Candidate and uppercased
    data['district'] = data['District'].str.upper()

    data['district'] = EC.district.mark_statewide_districts(
        data['district'], data['temp_office'], [
            'US PRESIDENT',
            'US SENATE',
            'GOVERNOR',
            ])

    data['district'] = EC.district.fix_numerical_districts(data['district'])

    # Zero-pad floterial districts 1F, ..., 9F
    data['district'] = data['district'].mask((data['district'].str.len() == 2) &
                                             (data['district'].str.endswith('F')),
                                             '0' + data['district'])
    print('Parsed NH20 `district`.')
    return data


def make_magnitude(data: DataFrame) -> DataFrame:
    print('*Parsing MT20 `magnitude`...')

    # Magnitude is consistently 1, except for STATE HOUSE (VOTE FOR .*)
    data = EC.split_column(data, 'temp_office',
                           r'(?P<temp_office>.*) \(VOTE FOR (?P<magnitude>\d+)\)',
                           maintaining_columns=['temp_office'],
                           empty_value='1')
    data['magnitude'] = pd.to_numeric(data['magnitude'])
    data['office'] = data['temp_office']

    print('Parsed MT20 `office` (2/2).')
    print('Parsed MT20 `magnitude`.')
    return data


def make_dataverse(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `dataverse`...')

    data['dataverse'] = EC.dataverse.parse_dataverse_from_office(
        data['office'],
        state={
            'EXECUTIVE COUNCIL',
            'GOVERNOR',
            'STATE HOUSE',
            'STATE SENATE',
            })

    print('Parsed NH20 `dataverse`.')
    return data


def make_year(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `year`...')
    # Year is 2020 by definition
    data['year'] = 2020

    print('Parsed NH20 `year`.')
    return data


def make_stage(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `stage`...')
    # Data is pulled from Stage
    data['stage'] = data['Stage']

    print('Parsed NH20 `stage`.')
    return data


def make_special(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `special`...')

    # The New Hampshire data does not have special elections
    data['special'] = EC.r_bool(False)

    print('Parsed NH20 `special`.')
    return data


def make_writein(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `writein`...')
    # The New Hampshire data indicates writein by empty party detailed
    data['writein'] = EC.series_r_bool(data['party_detailed'] == '')
    data['candidate'] = data['temp_candidate'].replace({
        r' \(W-IN\)': ''
        }, regex=True)

    print('Parsed NH20 `writein`.')
    print('Parsed NH20 `candidate` (2/2).')
    return data


def make_state_po(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `state_po`...')
    # Already parsed

    print('Parsed NH20 `state_po`.')
    return data


def make_state_fips(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `state_fips`...')
    # Already parsed

    print('Parsed NH20 `state_fips`.')
    return data


def make_state_cen(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `state_cen`...')
    # Already parsed

    print('Parsed NH20 `state_cen`.')
    return data


def make_state_ic(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `state_ic`...')
    # Already parsed

    print('Parsed NH20 `state_ic`.')
    return data


def make_date(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `date...`')

    # New Hampshire had one date for all elections
    data['date'] = '2020-11-03'

    print('*Parsed NH20 `date`.')
    return data


def make_readme_check(data: DataFrame) -> DataFrame:
    print('*Parsing NH20 `readme_check...`')

    # Notes:
    # 1. A few districts are floterial districts, which are marked with an F.
    # 2. State house members need to have their districts concatenated with county
    # 3. A few races have mistabulated their totals
    # 4. No full names were found for some writein candidates for Register of Probate in Grafton
    # 5. State House and State Senate District 11 Recounts do not indicate writeins
    data['readme_check'] = EC.series_r_bool(
        # 1.
        (data['district'].str.contains('F')) |
        # 2.
        (data['office'] == 'STATE HOUSE') |
        # 3.
        ((data['office'] == 'COUNTY REGISTER OF PROBATE') & (data['county_name'] == 'GRAFTON')) |
        # Already handled state house district 18 in Strafford County in 2
        # 4.
        # Already handled Teszler and Townsend in 3
        # 5.
        # Already handled State House recounts
        ((data['office'] == 'STATE SENATE') & (data['district'] == '011'))
        )

    print('Parsed NH20 `readme_check`.')
    return data


if __name__ == '__main__':
    print("Parsing raw data for New Hampshire.")
    raw_data = load_all_data(prepare_pickle=True)
    print("Parsed NH20 raw data for New Hampshire.")

    EC.check_original_dataset(
        raw_data,
        expected_columns={'County', 'Precinct', 'Office', 'Candidate', 'Party', 'Votes', 'Stage',
                          'District'},
        county_column='County', expected_counties=10
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
    EC.check_cleaned_dataset(data, expected_counties=10, expected_jurisdictions=247+12)
    EC.inspect_cleaned_dataset(data)
    EC.save_cleaned_dataset(data, '2020-nh-precinct-general.csv')
