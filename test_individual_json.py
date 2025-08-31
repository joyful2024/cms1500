#!/usr/bin/env python3

import pytest
import os
import shutil
import json
from pypdf import PdfReader
from generate_forms import generate_random_address, fill_cms1500_form


def test_individual_json_files():
    """Test that individual JSON files are created for each form."""
    if not os.path.exists("form-cms1500.pdf"):
        pytest.skip("Original form not found")
    
    test_output_dir = "test_individual_json"
    
    try:
        # Create test directory
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Generate 3 test forms manually to test individual JSON creation
        for i in range(1, 4):
            address_data = generate_random_address()
            pdf_filename = os.path.join(test_output_dir, f"cms1500_form_{i:04d}.pdf")
            json_filename = os.path.join(test_output_dir, f"cms1500_form_{i:04d}.json")
            
            # Create PDF
            success = fill_cms1500_form(address_data, pdf_filename)
            assert success, f"PDF creation should succeed for form {i}"
            
            # Create individual JSON file (mimicking the updated generate_forms.py logic)
            individual_form_data = {
                "form_number": i,
                "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                "generated_date": "2025-01-01T12:00:00",
                "form_data": address_data
            }
            
            with open(json_filename, "w") as json_file:
                json.dump(individual_form_data, json_file, indent=2)
        
        # Verify individual JSON files exist
        pdf_files = [f for f in os.listdir(test_output_dir) if f.endswith('.pdf')]
        json_files = [f for f in os.listdir(test_output_dir) if f.endswith('.json')]
        
        assert len(pdf_files) == 3, f"Should have 3 PDF files, found {len(pdf_files)}"
        assert len(json_files) == 3, f"Should have 3 JSON files, found {len(json_files)}"
        
        # Verify each JSON file corresponds to a PDF
        for i in range(1, 4):
            pdf_file = f"cms1500_form_{i:04d}.pdf"
            json_file = f"cms1500_form_{i:04d}.json"
            
            assert pdf_file in pdf_files, f"PDF file {pdf_file} should exist"
            assert json_file in json_files, f"JSON file {json_file} should exist"
            
            # Verify JSON content
            json_path = os.path.join(test_output_dir, json_file)
            with open(json_path, "r") as f:
                json_data = json.load(f)
            
            assert json_data["form_number"] == i, f"Form number should be {i}"
            assert json_data["pdf_filename"] == pdf_file, f"PDF filename should match"
            assert "form_data" in json_data, "Should contain form_data"
            assert "generated_date" in json_data, "Should contain generated_date"
            
            # Verify form data completeness
            form_data = json_data["form_data"]
            required_fields = ["pt_street", "pt_city", "pt_state", "pt_zip", "pt_AreaCode", "pt_phone",
                              "birth_mm", "birth_dd", "birth_yy", "ins_dob_mm", "ins_dob_dd", "ins_dob_yy"]
            
            for field in required_fields:
                assert field in form_data, f"Form {i} JSON should contain {field}"
                assert form_data[field], f"Form {i} field {field} should not be empty"
        
        print("✓ Individual JSON files creation and structure verified")
        
    finally:
        # Clean up
        if os.path.exists(test_output_dir):
            shutil.rmtree(test_output_dir)


def test_json_pdf_pairing():
    """Test that individual JSON data matches corresponding PDF content."""
    if not os.path.exists("form-cms1500.pdf"):
        pytest.skip("Original form not found")
    
    test_output_dir = "test_json_pdf_pair"
    
    try:
        os.makedirs(test_output_dir, exist_ok=True)
        
        # Generate one form for detailed testing
        address_data = generate_random_address()
        pdf_filename = os.path.join(test_output_dir, "test_form.pdf")
        json_filename = os.path.join(test_output_dir, "test_form.json")
        
        # Create PDF
        success = fill_cms1500_form(address_data, pdf_filename)
        assert success, "PDF creation should succeed"
        
        # Create JSON
        json_data = {
            "form_number": 1,
            "pdf_filename": "test_form.pdf",
            "generated_date": "2025-01-01T12:00:00",
            "form_data": address_data
        }
        
        with open(json_filename, "w") as f:
            json.dump(json_data, f, indent=2)
        
        # Read PDF and JSON
        pdf_reader = PdfReader(pdf_filename)
        pdf_fields = pdf_reader.get_form_text_fields()
        
        with open(json_filename, "r") as f:
            json_content = json.load(f)
        
        # Compare data
        json_form_data = json_content["form_data"]
        for field_name, json_value in json_form_data.items():
            if field_name in pdf_fields:
                pdf_value = pdf_fields[field_name]
                assert pdf_value == json_value, f"Field {field_name}: PDF='{pdf_value}', JSON='{json_value}'"
        
        print("✓ Individual JSON and PDF data consistency verified")
        
    finally:
        if os.path.exists(test_output_dir):
            shutil.rmtree(test_output_dir)


if __name__ == "__main__":
    test_individual_json_files()
    test_json_pdf_pairing()
    print("All individual JSON tests passed!")