#!/usr/bin/env python3
"""
JBMC Test Generator
A tool to automate the JBMC workflow and generate counter examples.
"""

import argparse
import os
import subprocess
import sys
import json_processor
import counterexample_generator


def compile_java(java_file):
    """Compile the Java file."""
    print(f"Compiling {java_file}...")
    result = subprocess.run(['javac', java_file],
                            capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error compiling {java_file}:")
        print(result.stderr)
        sys.exit(1)

    print(f"Successfully compiled {java_file}")
    return True


def run_jbmc(class_name):
    """Run JBMC on the given class and method."""
    output_file = "x.json"
    print(f"Running JBMC on {class_name}.test...")

    cmd = [
        'jbmc',
        f'{class_name}.test',
        '--drop-unused-functions',
        '--json-ui',
        '--unwind', '20'
    ]

    with open(output_file, 'w') as f:
        result = subprocess.run(
            cmd, stdout=f, stderr=subprocess.PIPE, text=True)

    # if result.returncode != 0 and "VERIFICATION FAILED" not in result.stderr:
    #     print(f"Error running JBMC:")
    #     print(result.stderr)
    #     sys.exit(1)

    print(f"JBMC analysis completed, output saved to {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description='JBMC Workflow Automation Tool')
    parser.add_argument('java_file', help='Input Java file to analyze')
    parser.add_argument('--output-dir', '-o', default='counter_examples',
                        help='Directory to store counter examples (default: counter_examples)')
    args = parser.parse_args()

    # Extract class name from the Java file
    class_name = os.path.splitext(os.path.basename(args.java_file))[0]

    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Step 1: Compile the Java file
    compile_java(args.java_file)

    # Step 2: Run JBMC
    json_file = run_jbmc(class_name)

    # Step 3: Process the JSON output
    temp_json = json_processor.process_json(json_file)

    # Step 4: Generate counter examples
    counterexample_generator.generate_counter_examples(
        temp_json, args.output_dir)

    print(f"Process completed. Counter examples saved in {args.output_dir}/")


if __name__ == "__main__":
    main()
