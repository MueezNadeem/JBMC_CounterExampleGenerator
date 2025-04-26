#!/usr/bin/env python3
"""
Module to process the JSON output from JBMC
"""

import json
import os


def process_json(json_file):
    """Process the JSON file output from JBMC."""
    print(f"Processing {json_file}...")

    # Read and parse the JSON file
    try:
        with open(json_file, 'r', encoding='utf-16') as file:
            data = json.load(file)
    except UnicodeError:
        # Try with different encodings if utf-16 fails
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

    # Extract failure results
    result_dicts = [item for item in data if "result" in item]
    arr = []

    for each in result_dicts:
        for x in each['result']:
            if x['status'] == 'FAILURE':
                a = [item for item in x['trace']
                     if "assignmentType" in item and item.get('lhs', '').startswith('arg')]
                arr.append(a)

    print(f"Found {len(arr)} failing test cases")

    # Save intermediate results
    temp_json = 'temp.json'
    with open(temp_json, 'w') as f:
        json.dump(arr, f)

    # Process further to extract relevant information
    results = []
    for block in arr:
        for item in block:
            lhs = item.get('lhs', '')
            value = item.get('value', {})
            data_value = value.get('data')
            binary_value = value.get('binary')
            type_value = value.get('type')

            if lhs.startswith('arg') and (data_value == "null" or binary_value is not None):
                results.append({
                    'lhs': lhs,
                    'data': data_value,
                    'type': type_value
                })

    # Print summary of results
    print(f"Extracted {len(results)} relevant arguments")
    for result in results:
        print(
            f"lhs: {result['lhs']}, data: {result['data']}, type: {result['type']}")

    return temp_json
