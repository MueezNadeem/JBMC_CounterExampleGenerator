#!/usr/bin/env python3
"""
Module to generate Java counter examples from JBMC results
"""

import itertools
from collections import defaultdict
import json
import re
import os


def extract_function_info(test_case):
    """Extract function information from the test case."""
    for entry in test_case:
        if "sourceLocation" in entry and "function" in entry["sourceLocation"]:
            function_str = entry["sourceLocation"]["function"]
            return function_str
    return None


def extract_args_info(test_case):
    """Extract all values for each argument from the test case."""
    args = defaultdict(list)
    for entry in test_case:
        if "lhs" in entry and entry["lhs"].startswith("arg"):
            arg_name = entry["lhs"]
            if "value" in entry:
                value_data = entry["value"]
                if value_data.get("data") == "null" or "binary" in value_data:
                    args[arg_name].append({
                        "type": value_data.get("type", "unknown"),
                        "value": value_data.get("data", "unknown"),
                        "binary": value_data.get("binary", None)
                    })
    return args

    args = {}
    for entry in test_case:
        if "lhs" in entry and entry["lhs"].startswith("arg"):
            arg_name = entry["lhs"]
            if "value" in entry:
                value_data = entry["value"]
                if value_data.get("data") == "null" or "binary" in value_data:
                    args[arg_name] = {
                        "type": value_data.get("type", "unknown"),
                        "value": value_data.get("data", "unknown"),
                        "binary": value_data.get("binary", None)
                    }
    return args


def map_type_to_java(type_str):
    """Map C/C++ type representation to Java type."""
    if "java::array" in type_str:
        array_match = re.search(r'struct java::array\[(.*?)\]', type_str)
        if array_match:
            element_type = array_match.group(1)
            java_element_type = map_primitive_type(element_type)
            return f"{java_element_type}[]"
        return "Object[]"

    if "java.lang.String" in type_str:
        return "String"

    if "struct " in type_str:
        struct_match = re.search(r'struct (\w+)\$(\w+)', type_str)
        if struct_match:
            return f"{struct_match.group(1)}.{struct_match.group(2)}"

        class_match = re.search(r'struct (\w+)', type_str)
        if class_match:
            return class_match.group(1)

    return map_primitive_type(type_str)


def map_primitive_type(type_str):
    """Map primitive type names."""
    type_mapping = {
        "int": "int",
        "float": "float",
        "double": "double",
        "char": "char",
        "boolean": "boolean",
        "void": "void",
        "byte": "byte",
        "short": "short",
        "long": "long"
    }

    for java_type, mapped_type in type_mapping.items():
        if java_type in type_str:
            return mapped_type

    return "Object"


def generate_java_code(test_case, index):
    """Generate Java code based on the test case data."""
    function_info = extract_function_info(test_case)
    if not function_info:
        return "// Could not find function information in the JSON data."

    match = re.search(r'java::(\w+)\.(\w+):\((.*?)\)(\w+)', function_info)
    if not match:
        return "// Could not parse function information."

    class_name = match.group(1)
    method_name = match.group(2)
    param_str = match.group(3)

    args_info = extract_args_info(test_case)

    java_code = f"class CounterExample{index} {{\n"
    java_code += f"    public static void main(String[] args) {{\n"

    arg_values = []
    for arg_name, arg_info in args_info.items():
        type_str = arg_info["type"]
        java_type = map_type_to_java(type_str)

        java_type = java_type.replace("*", "").replace("const ", "").strip()

        if arg_info["value"] == "null":
            java_code += f"        {java_type} {arg_name} = null;\n"
        elif "binary" in arg_info:
            value = arg_info["value"]
            java_code += f"        {java_type} {arg_name} = {value};\n"

        arg_values.append(arg_name)

    arg_list = ", ".join(arg_values)
    java_code += f"        {class_name}.{method_name}({arg_list});\n"
    java_code += "    }\n"
    java_code += "}\n"

    return java_code


def generate_counter_examples(json_file, output_dir):
    """Generate counter examples from the processed JSON file."""
    print(f"Generating counter examples from {json_file}...")

    with open(json_file, 'r') as f:
        json_data = json.load(f)

    counter_examples = []
    for i, test_case in enumerate(json_data):
        function_info = extract_function_info(test_case)
        args_info = extract_args_info(test_case)

        for j, combination in enumerate(generate_arg_combinations(args_info)):
            index = f"{i}_{j}"
            java_code = generate_java_code_from_combination(
                function_info, combination, index)
            file_name = f"CounterExample{index}.java"
            output_path = os.path.join(output_dir, file_name)

            print(f"Generating {file_name}...")

            with open(output_path, 'w') as f:
                f.write(java_code)

            counter_examples.append(output_path)

    print(f"Generated {len(counter_examples)} counter example Java files.")
    return counter_examples

    print(f"Generating counter examples from {json_file}...")

    with open(json_file, 'r') as f:
        json_data = json.load(f)

    counter_examples = []
    for i, test_case in enumerate(json_data):
        java_code = generate_java_code(test_case, i)
        file_name = f"CounterExample{i}.java"
        output_path = os.path.join(output_dir, file_name)

        print(f"Generating {file_name}...")

        with open(output_path, 'w') as f:
            f.write(java_code)

        counter_examples.append(output_path)

    print(f"Generated {len(counter_examples)} counter example Java files.")
    return counter_examples


def generate_arg_combinations(args_info):
    """Generate all unique combinations of argument values."""
    keys = list(args_info.keys())
    values_lists = [args_info[key] for key in keys]

    seen = set()
    for combination in itertools.product(*values_lists):
        # Create a hashable representation of the combination
        combo_key = tuple((key, val['value'])
                          for key, val in zip(keys, combination))
        if combo_key not in seen:
            seen.add(combo_key)
            yield dict(zip(keys, combination))

    keys = list(args_info.keys())
    values_lists = [args_info[key] for key in keys]
    for combination in itertools.product(*values_lists):
        yield dict(zip(keys, combination))


def generate_java_code_from_combination(function_info, args_info, index):
    """Generate Java code based on a single combination of argument values."""
    if not function_info:
        return "// Could not find function information in the JSON data."

    match = re.search(r'java::(\w+)\.(\w+):\((.*?)\)(\w+)', function_info)
    if not match:
        return "// Could not parse function information."

    class_name = match.group(1)
    method_name = match.group(2)

    java_code = f"class CounterExample{index} {{\n"
    java_code += f"    public static void main(String[] args) {{\n"

    arg_values = []
    for arg_name, arg_info in args_info.items():
        java_type = map_type_to_java(arg_info["type"])
        java_type = java_type.replace("*", "").replace("const ", "").strip()

        if arg_info["value"] == "null":
            java_code += f"        {java_type} {arg_name} = null;\n"
        elif "binary" in arg_info:
            value = arg_info["value"]
            java_code += f"        {java_type} {arg_name} = {value};\n"
        else:
            java_code += f"        {java_type} {arg_name} = {arg_info['value']};\n"

        arg_values.append(arg_name)

    arg_list = ", ".join(arg_values)
    java_code += f"        {class_name}.{method_name}({arg_list});\n"
    java_code += "    }\n"
    java_code += "}\n"

    return java_code
