#!/usr/bin/env python3

from pypdf import PdfReader, PdfWriter
import sys

def fill_cms1500_form():
    """Fill the CMS-1500 form with patient address information."""
    
    # Read the original form
    reader = PdfReader("form-cms1500.pdf")
    writer = PdfWriter()
    
    # Get the first page (CMS-1500 is typically single page)
    page = reader.pages[0]
    
    # Check if the form has fillable fields
    if "/AcroForm" in reader.trailer["/Root"]:
        print("Form has fillable fields")
        
        # Get form fields
        fields = reader.get_form_text_fields()
        if fields:
            print("Available fields:")
            for field_name in fields.keys():
                print(f"  - {field_name}")
        else:
            print("No text fields found")
            
        # Fill patient address fields using the actual field names found in the form
        address_fields = {
            "pt_street": "1247 Maple Street",
            "pt_city": "Springfield", 
            "pt_state": "IL",
            "pt_zip": "62701",
            "pt_AreaCode": "555",
            "pt_phone": "123-4567"
        }
        
        # Fill the form
        writer.clone_reader_document_root(reader)
        
        # Update all fields at once
        field_updates = {}
        for field_name, value in address_fields.items():
            if field_name in fields:
                field_updates[field_name] = value
                print(f"Filled field '{field_name}' with '{value}'")
        
        if field_updates:
            writer.update_page_form_field_values(writer.pages[0], field_updates)
    else:
        print("This PDF does not contain fillable form fields")
        writer.add_page(page)
    
    # Save the filled form
    with open("filled-cms1500.pdf", "wb") as output_file:
        writer.write(output_file)
    
    print("\nFilled form saved as 'filled-cms1500.pdf'")
    print("\nPatient Address Information:")
    print("1247 Maple Street")
    print("Springfield, IL 62701")
    print("(555) 123-4567")

if __name__ == "__main__":
    fill_cms1500_form()