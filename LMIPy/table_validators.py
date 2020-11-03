import os
import json

from LMIPy import Table
from LMIPy.utils import flatten_list
import requests

def validate_table(table_id, table_type):
    print(f"Validating Table: {table_id}")
    print(f"Fetching table entity from API.")
    table = Table(table_id)

    with open('./LMIPy/table_schema.json') as f:
        schema = json.load(f)[table_type.upper()]

    types = schema['types']
    expected_columns = flatten_list([v for v in types.values()])

    print('\nValidating columns...')
    print('Columns valid!' if validate_column_types(table, expected_columns) else 'Columns invalid.')

    print('\nValidating types...')
    print('Types valid!' if validate_fields(table_id, types) else 'Types invalid.')


def validate_column_types(table, expected_columns):
    column_types = table.attributes.get('legend', {})

    data_columns_set = set(flatten_list([v for v in column_types.values() if v]))
    expected_columns_set = set(expected_columns)

    missing_columns = list(expected_columns_set-data_columns_set)
    extra_columns = list(data_columns_set-expected_columns_set)

    if missing_columns: print(f"Found missing columns: {', '.join(missing_columns)}")
    if extra_columns: print(f"Found extra columns: {', '.join(extra_columns)}")

    return False if any([missing_columns, extra_columns]) else True

def validate_fields(table_id, expected_types):
    url = f"https://api.resourcewatch.org/v1/fields/{table_id}"

    r = requests.get(url)
    fields = r.json().get('fields', {})

    data_types = {k: v['type'] for k,v in fields.items()}

    validated_columns = {col: col in expected_types[_type] for col, _type in data_types.items()}
    is_valid = all([v for v in validated_columns.values()])

    if not is_valid:
        for col,valid in validated_columns.items():
            expected_type = [_type for _type, col_list in expected_types.items() if col in col_list][0]
            found_type = data_types[v]
            if not valid:
                print(f"Field {col}:\nExpected <type {expected_type}>, found <type {found_type}>\n" )

    return True if is_valid else False


        



    # is_valid = all([len(v['found']) == 1 and v['expected'] == type_map[v['found'][0]] for v in report.values()])
    # if not is_valid: 
    #     for k,v in report.items():
    #         if len(v['found']) != 1:
    #             print(f"For {k}:\nExpected <type {v['expected']}>, found {', '.join(v['found'])}\n")


    # return True if is_valid else False