#!/usr/bin/env python3

import pytest
import os
import shutil
import json
from pypdf import PdfReader
from generate_forms import generate_random_address, fill_cms1500_form, generate_multiple_forms


def test_generate_random_address():
    """Test that random address generation creates valid data."""
    address = generate_random_address()
    
    # Check that all required fields are present
    required_fields = ["pt_street", "pt_city", "pt_state", "pt_zip", "pt_AreaCode", "pt_phone",
                      "birth_mm", "birth_dd", "birth_yy", "ins_dob_mm", "ins_dob_dd", "ins_dob_yy",
                      "insurance_type_index", "insurance_type_name", "sex", "rel_to_ins", 
                      "employment", "pt_auto_accident", "other_accident", "ins_sex", 
                      "ins_benefit_plan", "lab", "ssn", "assignment", "num_service_lines"]
    for field in required_fields:
        assert field in address, f"Missing field: {field}"
        assert address[field] is not None, f"None value for field: {field}"
    
    # Check data types and formats
    assert isinstance(address["pt_street"], str)
    assert isinstance(address["pt_city"], str)
    assert len(address["pt_state"]) == 2  # State abbreviation
    assert len(address["pt_AreaCode"]) == 3  # Area code
    assert "-" in address["pt_phone"]  # Phone format xxx-xxxx
    
    # Check birthday formats (MM, DD, YY as 2-digit strings)
    assert len(address["birth_mm"]) == 2 and address["birth_mm"].isdigit()
    assert len(address["birth_dd"]) == 2 and address["birth_dd"].isdigit()
    assert len(address["birth_yy"]) == 2 and address["birth_yy"].isdigit()
    assert len(address["ins_dob_mm"]) == 2 and address["ins_dob_mm"].isdigit()
    assert len(address["ins_dob_dd"]) == 2 and address["ins_dob_dd"].isdigit()
    assert len(address["ins_dob_yy"]) == 2 and address["ins_dob_yy"].isdigit()
    
    # Check valid date ranges
    assert 1 <= int(address["birth_mm"]) <= 12
    assert 1 <= int(address["birth_dd"]) <= 31
    assert 1 <= int(address["ins_dob_mm"]) <= 12
    assert 1 <= int(address["ins_dob_dd"]) <= 31
    
    # Check insurance type fields
    assert isinstance(address["insurance_type_index"], int)
    assert 0 <= address["insurance_type_index"] <= 6
    assert isinstance(address["insurance_type_name"], str)
    assert address["insurance_type_name"] in [
        "Medicare", "Medicaid", "Tricare/Champus", "Champva", 
        "Group Health Plan", "FECA BLK LUNG", "Other"
    ]
    
    # Check checkbox field values
    assert address["sex"] in ["M", "F"]
    assert address["rel_to_ins"] in ["S", "M", "C", "O"]
    assert address["employment"] in ["YES", "NO"]
    assert address["pt_auto_accident"] in ["YES", "NO"]
    assert address["other_accident"] in ["YES", "NO"]
    assert address["ins_sex"] in ["MALE", "FEMALE"]
    assert address["ins_benefit_plan"] in ["YES", "NO"]
    assert address["lab"] in ["YES", "NO"]
    assert address["ssn"] in ["SSN", "EIN"]
    assert address["assignment"] in ["YES", "NO"]
    
    # Check diagnosis fields
    assert isinstance(address["num_diagnoses"], int)
    assert 1 <= address["num_diagnoses"] <= 4
    
    # Check that diagnosis codes are present
    for i in range(1, address["num_diagnoses"] + 1):
        diag_field = f"diagnosis{i}"
        desc_field = f"diagnosis{i}_description"
        assert diag_field in address, f"Missing diagnosis field: {diag_field}"
        assert desc_field in address, f"Missing diagnosis description field: {desc_field}"
        assert isinstance(address[diag_field], str), f"Diagnosis code should be string: {diag_field}"
        assert len(address[diag_field]) >= 3, f"Diagnosis code too short: {address[diag_field]}"
    
    # Check service line diagnosis pointers
    for i in range(1, 7):
        diag_pointer_field = f"diag{i}"
        assert diag_pointer_field in address, f"Missing diagnosis pointer field: {diag_pointer_field}"
        if address[diag_pointer_field]:  # If not empty
            assert address[diag_pointer_field] in ["A", "B", "C", "D", "E", "F"], f"Invalid diagnosis pointer: {address[diag_pointer_field]}"
    
    # Check CPT/HCPCS service line fields
    assert isinstance(address["num_service_lines"], int)
    assert 1 <= address["num_service_lines"] <= 6
    
    # Check that CPT codes are present
    for i in range(1, address["num_service_lines"] + 1):
        cpt_field = f"cpt{i}"
        desc_field = f"cpt{i}_description"
        mod_field = f"mod{i}"
        charge_field = f"ch{i}"  # Updated field name
        units_field = f"units{i}"
        place_field = f"place{i}"
        type_field = f"type{i}"
        emg_field = f"emg{i}"
        day_field = f"day{i}"
        
        assert cpt_field in address, f"Missing CPT field: {cpt_field}"
        assert desc_field in address, f"Missing CPT description field: {desc_field}"
        assert mod_field in address, f"Missing modifier field: {mod_field}"
        assert charge_field in address, f"Missing charge field: {charge_field}"
        assert units_field in address, f"Missing units field: {units_field}"
        assert place_field in address, f"Missing place of service field: {place_field}"
        assert type_field in address, f"Missing type of service field: {type_field}"
        assert emg_field in address, f"Missing emergency field: {emg_field}"
        assert day_field in address, f"Missing days field: {day_field}"
        
        # Check additional modifier positions
        for mod_pos in ['a', 'b', 'c']:
            mod_ext_field = f"mod{i}{mod_pos}"
            assert mod_ext_field in address, f"Missing extended modifier field: {mod_ext_field}"
        
        assert isinstance(address[cpt_field], str), f"CPT code should be string: {cpt_field}"
        assert len(address[cpt_field]) == 5, f"CPT code should be 5 characters: {address[cpt_field]}"
        assert address[cpt_field].isdigit(), f"CPT code should be numeric: {address[cpt_field]}"
        
        # Modifier can be empty or 2 characters
        if address[mod_field]:
            assert len(address[mod_field]) <= 2, f"Modifier too long: {address[mod_field]}"
        
        # Place of service should be 2-digit string
        assert isinstance(address[place_field], str), f"Place of service should be string: {place_field}"
        assert len(address[place_field]) == 2, f"Place of service should be 2 digits: {address[place_field]}"
        assert address[place_field].isdigit(), f"Place of service should be numeric: {address[place_field]}"
        
        # Type of service should be valid code
        assert isinstance(address[type_field], str), f"Type of service should be string: {type_field}"
        assert address[type_field] in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "V", "A"], f"Invalid type of service: {address[type_field]}"
        
        # Emergency field should be empty or Y
        assert address[emg_field] in ["", "Y"], f"Invalid emergency indicator: {address[emg_field]}"
        
        # Days field should be empty or numeric
        if address[day_field]:
            assert address[day_field].isdigit(), f"Days should be numeric: {address[day_field]}"
        
        # Charges should be in format "XXX.00"
        assert "." in address[charge_field], f"Charge should have decimal: {address[charge_field]}"
        charge_parts = address[charge_field].split(".")
        assert len(charge_parts) == 2, f"Invalid charge format: {address[charge_field]}"
        assert charge_parts[0].isdigit(), f"Charge amount should be numeric: {address[charge_field]}"
        assert charge_parts[1] == "00", f"Charge should end with .00: {address[charge_field]}"
        
        # Units should be numeric string
        assert address[units_field].isdigit(), f"Units should be numeric: {address[units_field]}"
        assert 1 <= int(address[units_field]) <= 5, f"Units should be 1-5: {address[units_field]}"
        
        # Service dates (from and end dates)
        for date_type in ["from", "end"]:
            for date_part in ["mm", "dd", "yy"]:
                date_field = f"sv{i}_{date_part}_{date_type}"
                assert date_field in address, f"Missing service date field: {date_field}"
                if address[date_field]:  # If not empty
                    assert len(address[date_field]) == 2, f"Service date part should be 2 digits: {address[date_field]}"
                    assert address[date_field].isdigit(), f"Service date part should be numeric: {address[date_field]}"
    
    # Check that remaining service lines are empty
    for i in range(address["num_service_lines"] + 1, 7):
        cpt_field = f"cpt{i}"
        assert cpt_field in address, f"Missing empty CPT field: {cpt_field}"
        assert address[cpt_field] == "", f"CPT field should be empty: {cpt_field}"
    
    print("✓ Random address generation with all checkboxes, diagnosis codes, and CPT/HCPCS codes working correctly")


def test_fill_single_form():
    """Test filling a single form with random address."""
    if not os.path.exists("form-cms1500.pdf"):
        pytest.skip("Original form not found")
    
    address = generate_random_address()
    output_filename = "test_single_form.pdf"
    
    try:
        success = fill_cms1500_form(address, output_filename)
        assert success, "Form filling should succeed"
        assert os.path.exists(output_filename), "Output file should be created"
        
        # Verify the form was filled correctly
        reader = PdfReader(output_filename)
        fields = reader.get_form_text_fields()
        
        for field_name, expected_value in address.items():
            if field_name in fields:
                actual_value = fields[field_name]
                assert actual_value == expected_value, f"Field {field_name}: expected '{expected_value}', got '{actual_value}'"
        
        print("✓ Single form filling working correctly")
        
    finally:
        # Clean up
        if os.path.exists(output_filename):
            os.remove(output_filename)


def test_generate_multiple_forms():
    """Test generating multiple forms."""
    if not os.path.exists("form-cms1500.pdf"):
        pytest.skip("Original form not found")
    
    test_output_dir = "test_generated_forms"
    
    try:
        # Temporarily patch the output directory
        import generate_forms
        original_output_dir = "generated_forms"
        
        # Monkey patch for testing
        def patched_generate_multiple_forms(n):
            os.makedirs(test_output_dir, exist_ok=True)
            for i in range(1, n + 1):
                address_data = generate_random_address()
                output_filename = os.path.join(test_output_dir, f"cms1500_form_{i:04d}.pdf")
                fill_cms1500_form(address_data, output_filename)
        
        # Generate 2 test forms
        patched_generate_multiple_forms(2)
        
        # Verify forms were created
        assert os.path.exists(test_output_dir), "Output directory should be created"
        forms = [f for f in os.listdir(test_output_dir) if f.endswith('.pdf')]
        assert len(forms) == 2, f"Should have 2 forms, found {len(forms)}"
        
        # Verify each form is valid
        for form_file in forms:
            form_path = os.path.join(test_output_dir, form_file)
            assert os.path.getsize(form_path) > 0, f"Form {form_file} should not be empty"
            
            # Basic PDF validation
            reader = PdfReader(form_path)
            assert len(reader.pages) > 0, f"Form {form_file} should have pages"
        
        print("✓ Multiple form generation working correctly")
        
    finally:
        # Clean up
        if os.path.exists(test_output_dir):
            shutil.rmtree(test_output_dir)


if __name__ == "__main__":
    test_generate_random_address()
    test_fill_single_form()
    test_generate_multiple_forms()
    print("All tests passed!")