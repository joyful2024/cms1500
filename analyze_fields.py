#!/usr/bin/env python3

from pypdf import PdfReader
import sys

def analyze_form_fields(pdf_path):
    """Analyze all form fields in a CMS-1500 PDF."""
    reader = PdfReader(pdf_path)
    
    if "/AcroForm" not in reader.trailer["/Root"]:
        print("No form fields found in PDF")
        return
    
    fields = reader.get_form_text_fields()
    
    print(f"=== ANALYZING {pdf_path} ===")
    print(f"Total fields: {len(fields)}")
    print("\n=== ALL FORM FIELDS ===")
    
    filled_fields = []
    empty_fields = []
    
    for field_name in sorted(fields.keys()):
        value = fields[field_name]
        if value and value.strip():
            filled_fields.append((field_name, value))
        else:
            empty_fields.append(field_name)
    
    print(f"\n=== FILLED FIELDS ({len(filled_fields)}) ===")
    for field_name, value in filled_fields:
        print(f"{field_name}: \"{value}\"")
    
    print(f"\n=== EMPTY FIELDS ({len(empty_fields)}) ===")
    for field_name in empty_fields:
        print(f"{field_name}: (empty)")
    
    return fields, filled_fields, empty_fields

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_fields.py <pdf_path>")
        sys.exit(1)
    
    analyze_form_fields(sys.argv[1])