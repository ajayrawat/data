import pandas
from pandas import DataFrame
from pathlib import Path

def dataframe_output(data: DataFrame, root: Path, name: str):
    '''
    This function performs the following steps:
    1. Sorts the dataset by date and country / region
    2. Merges the data with country / region metadata
    3. Outputs dataset as CSV and JSON to output/<name>.csv and output/<name>.json
    4. Outputs dataset as CSV and JSON to output/<name>_latest.csv and output/<name>_latest.json
    '''
    pivot_columns = ['CountryCode', 'CountryName']
    if 'Region' in data.columns: pivot_columns = ['Region'] + pivot_columns

    # Core columns are those that appear in all datasets
    core_columns = ['Date'] + pivot_columns + ['Confirmed', 'Deaths']

    # Merge with metadata from appropriate helper dataset
    # Data from https://developers.google.com/public-data/docs/canonical/countries_csv and Wikipedia
    meta_name = '%s_regions.csv' % name if 'Region' in data.columns else 'country_coordinates.csv'
    metadata = pandas.read_csv(root / 'input' / meta_name, dtype=str)
    data = data.merge(metadata)[core_columns + [col for col in metadata.columns if col not in core_columns]]

    # Make sure the dataset is properly sorted
    data = data.sort_values(['Date', pivot_columns[0]])

    # Make sure the core columns have the right data type
    data['Date'] = data['Date'].astype(str)
    number_converter = lambda x: None if pandas.isna(x) else int(x)
    data['Confirmed'] = data['Confirmed'].astype(float).astype('Int64')
    data['Deaths'] = data['Deaths'].astype(float).astype('Int64')
    for pivot_column in pivot_columns:
        data[pivot_column] = data[pivot_column].astype(str)

    # Output time-series dataset as-is
    data.to_csv(root / 'output' / ('%s.csv' % name), index=False)
    dataframe_to_json(data, root / 'output' / ('%s.json' % name), orient='records')

    # Output a subset to the _latest version of the dataset
    latest = pandas.DataFrame(columns=list(data.columns))
    for pivot_column in sorted(data[pivot_columns[0]].unique()):
        latest = pandas.concat([latest, data[data[pivot_columns[0]] == pivot_column].iloc[-1:]])

    latest.to_csv(root / 'output' / ('%s_latest.csv' % name), index=False)
    dataframe_to_json(latest, root / 'output' / ('%s_latest.json' % name), orient='records')


def dataframe_to_json(data: DataFrame, path: Path, **kwargs):
    with open(path, 'w', encoding='UTF-8') as file:
        data.to_json(file, force_ascii=False, **kwargs)