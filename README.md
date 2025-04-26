# JBMC Workflow Tool

A tool to automate the JBMC workflow and generate counter examples from Java code.

## Installation

### Option 1: Direct Use

```bash
# Clone the repository
git clone https://github.com/MueezNadeem/JBMC_CounterExampleGenerator.git
cd JBMC_CounterExampleGenerator

# Make the main script executable
chmod +x jbmc_workflow.py
```

### Option 2: Install as Package

```bash
# Clone the repository
git clone https://github.com/MueezNadeem/JBMC_CounterExampleGenerator.git
cd JBMC_CounterExampleGenerator

# Install the package
pip install -e .
```

## Prerequisites

- Java Development Kit (JDK)
- JBMC (Java Bounded Model Checker)
- Python 3.6+

## Usage

```bash
# Option 1: Using the script directly
./jbmc_workflow.py Input.java

# Option 2: Using the installed package
jbmc-workflow Input.java

# Specify output directory
jbmc-workflow Input.java --output-dir my_counter_examples
```

## Workflow

1. Compiles the Java file
2. Runs JBMC with specified parameters
3. Processes the JSON output from JBMC
4. Generates counter example Java files

## Output

The tool generates counter example Java files in the specified output directory (default: `counter_examples/`).
