# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a CMS-1500 healthcare billing form generator that creates realistic synthetic data for ML training in EHR and medical claim processing systems. It generates both filled PDF forms and structured JSON data using PyPDF and Faker libraries.

## Common Development Commands

### Environment Setup
```bash
# Install dependencies (preferred method)
uv sync

# Alternative installation
pip install -e .
```

### Form Generation
```bash
# Generate a single form
uv run python generate_forms.py 1

# Generate multiple forms (e.g., 10)
uv run python generate_forms.py 10

# Simple form filling (basic functionality)
uv run python fill_form.py
```

### Testing
```bash
# Run all tests
uv run pytest test_generate_forms.py -v

# Run specific test files
uv run pytest test_fill_form.py -v
uv run pytest test_json_output.py -v
uv run pytest test_individual_json.py -v

# Quick test run
python test_generate_forms.py
python test_fill_form.py
```

### Analysis and Utilities
```bash
# Analyze field coverage in CMS-1500 form
uv run python analyze_fields.py

# Run basic main script
python main.py
```

## Code Architecture

### Core Components

- **`generate_forms.py`**: Main form generation engine with 3-phase implementation
  - Phase 1: Service line enhancements and emergency indicators
  - Phase 2: Insurance & provider details expansion  
  - Phase 3: Extended clinical fields (1-12 diagnoses, intelligent lab detection)
  
- **`fill_form.py`**: Basic form filling functionality for PDF manipulation

- **Template Files**:
  - `form-cms1500.pdf`: Blank fillable CMS-1500 form template
  - `filled-cms1500.pdf`: Output example

### Data Generation Logic

- **Medical Coding**: ICD-10-CM diagnosis codes, CPT/HCPCS procedure codes, healthcare modifiers
- **Demographics**: Uses Faker for realistic patient/provider information
- **Insurance**: Supports 14+ plan types (Medicare, Medicaid, BCBS, HMO, PPO, etc.)
- **Probability Distributions**: Weighted diagnosis scenarios (25% single, 30% dual, 15% complex 4+)

### Output Structure
```
generated_forms/
├── cms1500_form_XXXX.pdf    # Filled PDF forms
├── cms1500_form_XXXX.json   # Individual form data
├── forms_data.json          # Consolidated dataset
└── *.png                    # Visual examples (photocopy/fax quality)
```

### Dependencies

- **pypdf** (>=6.0.0): PDF form manipulation and field extraction
- **faker** (>=28.0.0): Synthetic healthcare data generation  
- **pytest** (>=8.0.0): Testing framework (test dependency)

### Key Features

- **Field Coverage**: 103+ populated fields out of 239 total CMS-1500 fields
- **Healthcare Compliance**: Proper ICD-10/CPT code relationships and medical modifiers
- **Batch Processing**: Command-line interface for multiple form generation
- **ML Training Ready**: JSON export with structured data for model training

## Development Notes

- Python 3.12+ required (configured in pyproject.toml)
- Uses `uv` for dependency management (preferred over pip)
- All synthetic data generation - no real patient information
- Form field analysis available via `analyze_fields.py`
- Comprehensive test suite covers data validation, healthcare coding compliance, and field population logic