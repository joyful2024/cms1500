#!/usr/bin/env python3

import pytest
import os
from pypdf import PdfReader
from fill_form import fill_cms1500_form


def test_form_filling():
    """Test that the CMS-1500 form is filled with patient address correctly."""
    
    # Ensure original form exists
    assert os.path.exists("form-cms1500.pdf"), "Original form file not found"
    
    # Fill the form
    fill_cms1500_form()
    
    # Verify filled form was created
    assert os.path.exists("filled-cms1500.pdf"), "Filled form was not created"
    
    # Read the filled form and verify fields
    reader = PdfReader("filled-cms1500.pdf")
    fields = reader.get_form_text_fields()
    
    # Expected values
    expected_values = {
        "pt_street": "1247 Maple Street",
        "pt_city": "Springfield", 
        "pt_state": "IL",
        "pt_zip": "62701",
        "pt_AreaCode": "555",
        "pt_phone": "123-4567"
    }
    
    # Verify each field is filled correctly
    for field_name, expected_value in expected_values.items():
        assert field_name in fields, f"Field {field_name} not found in form"
        actual_value = fields[field_name]
        assert actual_value == expected_value, f"Field {field_name}: expected '{expected_value}', got '{actual_value}'"
    
    print("✓ All patient address fields verified successfully")


def test_original_form_has_required_fields():
    """Test that the original form contains the expected fillable fields."""
    
    reader = PdfReader("form-cms1500.pdf")
    fields = reader.get_form_text_fields()
    
    required_fields = ["pt_street", "pt_city", "pt_state", "pt_zip", "pt_AreaCode", "pt_phone"]
    
    for field in required_fields:
        assert field in fields, f"Required field {field} not found in original form"
    
    print("✓ All required fields found in original form")


if __name__ == "__main__":
    test_original_form_has_required_fields()
    test_form_filling()
    print("All tests passed!")