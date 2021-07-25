import os
import json

from LMIPy import Table
from LMIPy.utils import flatten_list
import requests

def validate_tables(path, verbose=False):
    with open(path) as f:
        tables = json.load(f)

    checks_list = []
    for table_type, table_id in tables.items():
        validation = validate_table(table_id, table_type, verbose)
        if verbose: print(f"\n{table_type} {table_id} {'passed!' if all(validation) else 'failed'}.")
        checks_list += [{
            "id": table_id,
            "type": table_type,
            "valid": validation,
        }]

    print("\n\nValidation complete.\n")
    if all(flatten_list([el['valid'] for el in checks_list])):
        print('All passed!')
    else:
        _ = [print(f"\n{el['type']} {el['id']} failed.") for el in checks_list if not all(el['valid'])]



def validate_table(table_id, table_type, verbose=False):
    print(f"Validating Table: {table_type} ({table_id})")
    if verbose: print(f"Fetching table entity from API.")
    table = Table(table_id)

    with open('./LMIPy/table_schema.json') as f:
        schema = json.load(f)[table_type.upper()]

    types = schema['types']

    validation_tests = {
        'fields exist': validate_fields_exist,
        'field types': validate_field_types
    }

    checks_list = []
    for k,v in validation_tests.items():
        if verbose: print(f'\nValidating {k}.')
        validation = v(table, types, verbose)
        if verbose: print('Passed!' if validation else 'Failed.')
        checks_list += [validation]

    return checks_list


def validate_fields_exist(table, types, verbose):
    expected_columns = flatten_list([v for v in types.values()])
    column_types = table.attributes.get('legend', {})

    data_columns_set = set(flatten_list([v for v in column_types.values() if v]))
    expected_columns_set = set(expected_columns)

    missing_columns = list(expected_columns_set-data_columns_set)
    extra_columns = list(data_columns_set-expected_columns_set)

    if verbose and missing_columns: print(f"Found missing columns: {', '.join(missing_columns)}")
    if verbose and extra_columns: print(f"Found extra columns: {', '.join(extra_columns)}")

    return False if any([missing_columns, extra_columns]) else True

def validate_field_types(table, expected_types, verbose):
    table_id = table.id
    url = f"https://api.resourcewatch.org/v1/fields/{table_id}"

    r = requests.get(url)
    fields = r.json().get('fields', {})

    data_types = {k: v['type'] for k,v in fields.items()}

    validated_columns = {col: col in expected_types.get(_type, []) for col, _type in data_types.items()}
    is_valid = all([v for v in validated_columns.values()])

    if not is_valid:
        for col,valid in validated_columns.items():
            expected_type = [_type for _type, col_list in expected_types.items() if col in col_list]
            found_type = data_types[col]
            if verbose and not valid:
                print(f"Field {col}:\nExpected <type {expected_type[0] if len(expected_type) else None}>, found <type {found_type}>\n" )

    return True if is_valid else False


        



    # is_valid = all([len(v['found']) == 1 and v['expected'] == type_map[v['found'][0]] for v in report.values()])
    # if not is_valid: 
    #     for k,v in report.items():
    #         if len(v['found']) != 1:
    #             print(f"For {k}:\nExpected <type {v['expected']}>, found {', '.join(v['found'])}\n")


    # return True if is_valid else False