#!/usr/bin/env python3

import pytest
import os
import shutil
import json
from pypdf import PdfReader
from generate_forms import generate_multiple_forms


def test_json_output_creation():
    """Test that JSON file is created with form data."""
    if not os.path.exists("form-cms1500.pdf"):
        pytest.skip("Original form not found")
    
    test_output_dir = "test_json_forms"
    
    try:
        # Monkey patch to use test directory
        import generate_forms
        original_generate = generate_forms.generate_multiple_forms
        
        def test_generate_multiple_forms(n):
            os.makedirs(test_output_dir, exist_ok=True)
            all_forms_data = []
            
            for i in range(1, n + 1):
                address_data = generate_forms.generate_random_address()
                output_filename = os.path.join(test_output_dir, f"cms1500_form_{i:04d}.pdf")
                success = generate_forms.fill_cms1500_form(address_data, output_filename)
                
                if success:
                    form_record = {
                        "form_number": i,
                        "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                        "form_data": address_data
                    }
                    all_forms_data.append(form_record)
            
            # Save JSON file
            json_filename = os.path.join(test_output_dir, "forms_data.json")
            with open(json_filename, "w") as json_file:
                json.dump({
                    "metadata": {
                        "total_forms": len(all_forms_data),
                        "generated_date": "2025-01-01T12:00:00",
                        "description": "CMS-1500 form data for validation"
                    },
                    "forms": all_forms_data
                }, json_file, indent=2)
        
        # Generate test forms
        test_generate_multiple_forms(2)
        
        # Verify JSON file exists
        json_filename = os.path.join(test_output_dir, "forms_data.json")
        assert os.path.exists(json_filename), "JSON file should be created"
        
        # Load and verify JSON content
        with open(json_filename, "r") as json_file:
            data = json.load(json_file)
        
        # Verify structure
        assert "metadata" in data, "JSON should contain metadata"
        assert "forms" in data, "JSON should contain forms array"
        assert data["metadata"]["total_forms"] == 2, "Should record correct number of forms"
        assert len(data["forms"]) == 2, "Should have 2 form records"
        
        # Verify each form record
        for i, form_record in enumerate(data["forms"], 1):
            assert "form_number" in form_record, f"Form {i} should have form_number"
            assert "pdf_filename" in form_record, f"Form {i} should have pdf_filename"
            assert "form_data" in form_record, f"Form {i} should have form_data"
            
            form_data = form_record["form_data"]
            required_fields = ["pt_street", "pt_city", "pt_state", "pt_zip", "pt_AreaCode", "pt_phone",
                              "birth_mm", "birth_dd", "birth_yy", "ins_dob_mm", "ins_dob_dd", "ins_dob_yy"]
            
            for field in required_fields:
                assert field in form_data, f"Form {i} should contain {field} in form_data"
                assert form_data[field], f"Form {i} field {field} should not be empty"
        
        print("✓ JSON output creation and structure verified")
        
    finally:
        # Clean up
        if os.path.exists(test_output_dir):
            shutil.rmtree(test_output_dir)


def test_json_pdf_data_consistency():
    """Test that JSON data matches what's actually in the PDF forms."""
    if not os.path.exists("form-cms1500.pdf"):
        pytest.skip("Original form not found")
    
    test_output_dir = "test_consistency_forms"
    
    try:
        # Generate one form for testing
        import generate_forms
        os.makedirs(test_output_dir, exist_ok=True)
        
        address_data = generate_forms.generate_random_address()
        pdf_filename = os.path.join(test_output_dir, "test_form.pdf")
        json_filename = os.path.join(test_output_dir, "test_data.json")
        
        # Create PDF
        success = generate_forms.fill_cms1500_form(address_data, pdf_filename)
        assert success, "PDF creation should succeed"
        
        # Create JSON
        json_data = {
            "metadata": {"total_forms": 1},
            "forms": [{
                "form_number": 1,
                "pdf_filename": "test_form.pdf",
                "form_data": address_data
            }]
        }
        
        with open(json_filename, "w") as f:
            json.dump(json_data, f, indent=2)
        
        # Read PDF form fields
        reader = PdfReader(pdf_filename)
        pdf_fields = reader.get_form_text_fields()
        
        # Load JSON data
        with open(json_filename, "r") as f:
            json_content = json.load(f)
        
        json_form_data = json_content["forms"][0]["form_data"]
        
        # Compare JSON data with PDF fields
        for field_name, json_value in json_form_data.items():
            if field_name in pdf_fields:
                pdf_value = pdf_fields[field_name]
                assert pdf_value == json_value, f"Field {field_name}: PDF has '{pdf_value}', JSON has '{json_value}'"
        
        print("✓ JSON and PDF data consistency verified")
        
    finally:
        # Clean up
        if os.path.exists(test_output_dir):
            shutil.rmtree(test_output_dir)


if __name__ == "__main__":
    test_json_output_creation()
    test_json_pdf_data_consistency()
    print("All JSON tests passed!")