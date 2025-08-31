#!/usr/bin/env python3

import argparse
import os
import json
from pypdf import PdfReader, PdfWriter
from faker import Faker
import sys

fake = Faker()

def generate_random_address():
    """Generate a random address and birthday data using Faker."""
    street_address = fake.street_address()
    city = fake.city()
    state = fake.state_abbr()
    zip_code = fake.zipcode()
    phone = fake.phone_number()
    
    # Format phone number to extract area code and number
    phone_digits = ''.join(filter(str.isdigit, phone))
    if len(phone_digits) >= 10:
        area_code = phone_digits[:3]
        phone_number = f"{phone_digits[3:6]}-{phone_digits[6:10]}"
    else:
        area_code = "555"
        phone_number = f"{fake.random_int(100, 999)}-{fake.random_int(1000, 9999)}"
    
    # Generate patient birthday (18-80 years old)
    patient_birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
    patient_birth_mm = f"{patient_birth_date.month:02d}"
    patient_birth_dd = f"{patient_birth_date.day:02d}"
    patient_birth_yy = f"{patient_birth_date.year % 100:02d}"  # Last 2 digits of year
    
    # Generate insurance holder birthday (could be same as patient or different)
    ins_birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80)
    ins_birth_mm = f"{ins_birth_date.month:02d}"
    ins_birth_dd = f"{ins_birth_date.day:02d}"
    ins_birth_yy = f"{ins_birth_date.year % 100:02d}"  # Last 2 digits of year
    
    # Generate random insurance type (Field 1 - 7 options)
    insurance_types = [
        "Medicare",
        "Medicaid", 
        "Tricare/Champus",
        "Champva",
        "Group Health Plan",
        "FECA BLK LUNG",
        "Other"
    ]
    selected_insurance_type = fake.random_int(0, 6)
    selected_insurance_name = insurance_types[selected_insurance_type]
    
    # Generate random sex (Field 3 - Patient Sex)
    patient_sex_options = ["M", "F"]  # M=Male, F=Female
    selected_patient_sex = fake.random_element(patient_sex_options)
    
    # Generate random relationship to insured (Field 6)
    relationship_options = ["S", "M", "C", "O"]  # S=Self, M=Spouse, C=Child, O=Other
    selected_relationship = fake.random_element(relationship_options)
    
    # Generate random employment related (Field 10a)
    employment_related = fake.random_element(["YES", "NO"])
    
    # Generate random auto accident related (Field 10b)
    auto_accident_related = fake.random_element(["YES", "NO"])
    
    # Generate random other accident related (Field 10c)
    other_accident_related = fake.random_element(["YES", "NO"])
    
    # Generate random insured sex (Field 11b)
    insured_sex_options = ["MALE", "FEMALE"]
    selected_insured_sex = fake.random_element(insured_sex_options)
    
    # Generate random other health benefit plan (Field 11c)
    other_benefit_plan = fake.random_element(["YES", "NO"])
    
    # Generate random outside lab (Field 20)
    outside_lab = fake.random_element(["YES", "NO"])
    
    # Generate random tax ID type (Field 25)
    tax_id_type = fake.random_element(["SSN", "EIN"])
    
    # Generate random accept assignment (Field 27)
    accept_assignment = fake.random_element(["YES", "NO"])
    
    # Generate patient identity information
    patient_full_name = fake.name()
    patient_account_number = fake.bothify(text="####-###-####")  # Medical record number format
    
    # Generate insurance details
    insured_name = patient_full_name if fake.random_int(1, 100) <= 70 else fake.name()  # 70% self, 30% other
    insurance_policy_id = fake.bothify(text="??########")  # Insurance policy format
    
    # Common insurance company names
    insurance_companies = [
        ("Blue Cross Blue Shield", "123 Insurance Way, Hartford, CT 06103"),
        ("Aetna", "151 Farmington Ave, Hartford, CT 06156"), 
        ("Cigna", "900 Cottage Grove Rd, Bloomfield, CT 06002"),
        ("UnitedHealth", "9900 Bren Rd E, Minnetonka, MN 55343"),
        ("Humana", "500 W Main St, Louisville, KY 40202"),
        ("Anthem", "220 Virginia Ave, Indianapolis, IN 46204"),
        ("Kaiser Permanente", "1 Kaiser Plaza, Oakland, CA 94612"),
        ("Medicare", "7500 Security Blvd, Baltimore, MD 21244"),
        ("Medicaid", "Centers for Medicare & Medicaid Services, Baltimore, MD 21244")
    ]
    
    # Select insurance company based on insurance type
    if selected_insurance_name == "Medicare":
        insurance_company_info = insurance_companies[7]
    elif selected_insurance_name == "Medicaid":
        insurance_company_info = insurance_companies[8]
    else:
        insurance_company_info = fake.random_element(insurance_companies[:7])
    
    insurance_company_name = insurance_company_info[0]
    insurance_company_address = insurance_company_info[1]
    
    # Generate provider information
    provider_name = f"Dr. {fake.first_name()} {fake.last_name()}, MD"
    provider_address = fake.address().replace('\n', ', ')
    provider_npi = fake.bothify(text="##########")  # 10-digit NPI
    provider_tax_id = fake.bothify(text="##-#######")  # EIN format
    provider_phone = fake.phone_number()
    
    # Format provider phone for area code extraction
    provider_phone_digits = ''.join(filter(str.isdigit, provider_phone))
    if len(provider_phone_digits) >= 10:
        provider_area_code = provider_phone_digits[:3]
        provider_phone_formatted = f"{provider_phone_digits[3:6]}-{provider_phone_digits[6:10]}"
    else:
        provider_area_code = "555"
        provider_phone_formatted = f"{fake.random_int(100, 999)}-{fake.random_int(1000, 9999)}"
    
    # Generate CPT/HCPCS codes and modifiers for service lines (Box 24d)
    # Common CPT codes by category
    common_cpt_codes = [
        # Evaluation & Management
        ("99213", "Office visit, established patient, moderate complexity"),
        ("99214", "Office visit, established patient, high complexity"),
        ("99203", "Office visit, new patient, moderate complexity"),
        ("99204", "Office visit, new patient, high complexity"),
        ("99282", "Emergency department visit, moderate complexity"),
        ("99283", "Emergency department visit, high complexity"),
        
        # Preventive Medicine
        ("99395", "Periodic comprehensive preventive medicine, 18-39 years"),
        ("99396", "Periodic comprehensive preventive medicine, 40-64 years"),
        ("99397", "Periodic comprehensive preventive medicine, 65+ years"),
        
        # Laboratory
        ("80053", "Comprehensive metabolic panel"),
        ("85025", "Complete blood count with differential"),
        ("36415", "Routine venipuncture for collection of specimen"),
        ("80061", "Lipid panel"),
        ("85027", "Complete blood count, automated"),
        
        # Radiology
        ("73030", "Radiologic examination, shoulder, 2 views"),
        ("71020", "Radiologic examination, chest, 2 views"),
        ("73060", "Radiologic examination, knee, 2 views"),
        ("72148", "MRI lumbar spine without contrast"),
        
        # Surgery/Procedures
        ("12001", "Simple repair of superficial wounds of scalp, neck"),
        ("11042", "Debridement, subcutaneous tissue"),
        ("20610", "Arthrocentesis, major joint"),
        
        # Medicine
        ("90471", "Immunization administration"),
        ("93000", "Electrocardiogram, routine ECG with interpretation"),
        ("94010", "Spirometry"),
    ]
    
    # Common modifiers
    common_modifiers = [
        "25",  # Significant, separately identifiable E&M service
        "59",  # Distinct procedural service
        "RT",  # Right side
        "LT",  # Left side
        "50",  # Bilateral procedure
        "26",  # Professional component
        "TC",  # Technical component
        ""     # No modifier (empty)
    ]
    
    # Generate 1-6 service lines (most claims have 1-3 services)
    num_service_lines = fake.random_int(1, 6)
    selected_procedures = fake.random_elements(common_cpt_codes, length=num_service_lines, unique=True)
    
    # Common place of service codes
    place_of_service_codes = [
        "11",  # Office
        "12",  # Home
        "21",  # Inpatient Hospital
        "22",  # Outpatient Hospital
        "23",  # Emergency Room
        "24",  # Ambulatory Surgical Center
        "25",  # Birthing Center
        "26",  # Military Treatment Facility
        "31",  # Skilled Nursing Facility
        "32",  # Nursing Facility
        "33",  # Custodial Care Facility
        "34",  # Hospice
        "41",  # Ambulance - Land
        "49",  # Independent Clinic
        "50",  # Federally Qualified Health Center
        "51",  # Inpatient Psychiatric Facility
        "52",  # Psychiatric Facility - Partial Hospitalization
        "53",  # Community Mental Health Center
        "54",  # Intermediate Care Facility/Mentally Retarded
        "55",  # Residential Substance Abuse Treatment Facility
        "56",  # Psychiatric Residential Treatment Center
        "57",  # Non-residential Substance Abuse Treatment Facility
        "58",  # Non-residential Opioid Treatment Facility
        "60",  # Mass Immunization Center
        "61",  # Comprehensive Inpatient Rehabilitation Facility
        "62",  # Comprehensive Outpatient Rehabilitation Facility
        "65",  # End-Stage Renal Disease Treatment Facility
        "71",  # Public Health Clinic
        "72",  # Rural Health Clinic
        "81",  # Independent Laboratory
        "99"   # Other Place of Service
    ]
    
    # Create service line data
    service_line_data = {}
    service_dates = {}
    service_charges = {}
    service_units = {}
    total_charges = 0
    
    for i, (code, description) in enumerate(selected_procedures, 1):
        # CPT/HCPCS code
        service_line_data[f"cpt{i}"] = code
        service_line_data[f"cpt{i}_description"] = description
        
        # Modifiers (20% chance of having a modifier)
        if fake.random_int(1, 100) <= 20:
            modifier = fake.random_element([m for m in common_modifiers if m != ""])
            service_line_data[f"mod{i}"] = modifier
        else:
            service_line_data[f"mod{i}"] = ""
        
        # Service dates (within last 30 days)
        service_date = fake.date_between(start_date='-30d', end_date='today')
        service_dates[f"sv{i}_mm_from"] = f"{service_date.month:02d}"
        service_dates[f"sv{i}_dd_from"] = f"{service_date.day:02d}"
        service_dates[f"sv{i}_yy_from"] = f"{service_date.year % 100:02d}"
        
        # For most services, from and to dates are the same
        service_dates[f"sv{i}_mm_end"] = f"{service_date.month:02d}"
        service_dates[f"sv{i}_dd_end"] = f"{service_date.day:02d}"
        service_dates[f"sv{i}_yy_end"] = f"{service_date.year % 100:02d}"
        
        # Place of service
        place_code = fake.random_element(place_of_service_codes)
        service_line_data[f"place{i}"] = place_code
        
        # Emergency indicator (5% chance)
        if fake.random_int(1, 100) <= 5:
            service_line_data[f"emg{i}"] = "Y"
        else:
            service_line_data[f"emg{i}"] = ""
        
        # Charges ($50-$500)
        charge = fake.random_int(50, 500)
        service_charges[f"ch{i}"] = f"{charge}.00"
        total_charges += charge
        
        # Units (1-5)  
        units = fake.random_int(1, 5)
        service_units[f"units{i}"] = str(units)
    
    # Fill remaining service lines with empty values
    for i in range(num_service_lines + 1, 7):
        service_line_data[f"cpt{i}"] = ""
        service_line_data[f"mod{i}"] = ""
        service_dates[f"sv{i}_mm_from"] = ""
        service_dates[f"sv{i}_dd_from"] = ""
        service_dates[f"sv{i}_yy_from"] = ""
        service_dates[f"sv{i}_mm_end"] = ""
        service_dates[f"sv{i}_dd_end"] = ""
        service_dates[f"sv{i}_yy_end"] = ""
        service_line_data[f"place{i}"] = ""
        service_line_data[f"emg{i}"] = ""
        service_charges[f"ch{i}"] = ""
        service_units[f"units{i}"] = ""
    
    # Generate financial totals
    amount_paid = fake.random_int(0, int(total_charges * 0.8))  # 0-80% of total charges paid
    balance_due = total_charges - amount_paid
    
    # Generate random ICD-10-CM diagnosis codes (Field 21)
    # Common ICD-10-CM codes for realistic healthcare scenarios
    common_icd10_codes = [
        # Diabetes
        ("E11.9", "Type 2 diabetes mellitus without complications"),
        ("E11.40", "Type 2 diabetes mellitus with diabetic neuropathy, unspecified"),
        ("E11.65", "Type 2 diabetes mellitus with hyperglycemia"),
        
        # Hypertension
        ("I10", "Essential hypertension"),
        ("I12.9", "Hypertensive chronic kidney disease with stage 1 through stage 4 chronic kidney disease, or unspecified chronic kidney disease"),
        
        # Respiratory
        ("J44.1", "Chronic obstructive pulmonary disease with acute exacerbation"),
        ("J45.9", "Asthma, unspecified"),
        ("J06.9", "Acute upper respiratory infection, unspecified"),
        
        # Musculoskeletal
        ("M25.511", "Pain in right shoulder"),
        ("M54.5", "Low back pain"),
        ("M79.3", "Panniculitis, unspecified"),
        
        # Cardiovascular
        ("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris"),
        ("I48.91", "Unspecified atrial fibrillation"),
        
        # Mental Health
        ("F32.9", "Major depressive disorder, single episode, unspecified"),
        ("F41.9", "Anxiety disorder, unspecified"),
        
        # Infections
        ("A49.9", "Bacterial infection, unspecified"),
        ("B34.9", "Viral infection, unspecified"),
        
        # General symptoms
        ("R50.9", "Fever, unspecified"),
        ("R06.02", "Shortness of breath"),
        ("R51", "Headache"),
        
        # Injury
        ("S72.001A", "Fracture of unspecified part of neck of right femur, initial encounter for closed fracture"),
        ("T14.90XA", "Injury, unspecified, initial encounter"),
        
        # Routine care
        ("Z00.00", "Encounter for general adult medical examination without abnormal findings"),
        ("Z51.11", "Encounter for antineoplastic chemotherapy")
    ]
    
    # Select 1-4 random diagnosis codes (most claims have 1-3 diagnoses)
    num_diagnoses = fake.random_int(1, 4)
    selected_diagnoses = fake.random_elements(common_icd10_codes, length=num_diagnoses, unique=True)
    
    # Create diagnosis code data
    diagnosis_data = {}
    for i, (code, description) in enumerate(selected_diagnoses, 1):
        diagnosis_data[f"diagnosis{i}"] = code
        diagnosis_data[f"diagnosis{i}_description"] = description
    
    # For service lines, randomly reference the diagnosis codes
    # diag1-diag6 should contain pointers (A, B, C, D) to the diagnosis codes
    diagnosis_pointers = ['A', 'B', 'C', 'D', 'E', 'F']
    service_line_diagnoses = {}
    for i in range(1, 7):  # diag1 through diag6
        if i <= num_diagnoses:
            # Reference one of the available diagnoses
            pointer_index = fake.random_int(0, num_diagnoses - 1)
            service_line_diagnoses[f"diag{i}"] = diagnosis_pointers[pointer_index]
        else:
            service_line_diagnoses[f"diag{i}"] = ""
    
    return {
        "pt_street": street_address,
        "pt_city": city,
        "pt_state": state,
        "pt_zip": zip_code,
        "pt_AreaCode": area_code,
        "pt_phone": phone_number,
        "birth_mm": patient_birth_mm,
        "birth_dd": patient_birth_dd,
        "birth_yy": patient_birth_yy,
        "ins_dob_mm": ins_birth_mm,
        "ins_dob_dd": ins_birth_dd,
        "ins_dob_yy": ins_birth_yy,
        "insurance_type_index": selected_insurance_type,
        "insurance_type_name": selected_insurance_name,
        "sex": selected_patient_sex,
        "rel_to_ins": selected_relationship,
        "employment": employment_related,
        "pt_auto_accident": auto_accident_related,
        "other_accident": other_accident_related,
        "ins_sex": selected_insured_sex,
        "ins_benefit_plan": other_benefit_plan,
        "lab": outside_lab,
        "ssn": tax_id_type,
        "assignment": accept_assignment,
        "num_diagnoses": num_diagnoses,
        "num_service_lines": num_service_lines,
        
        # Patient identity
        "pt_name": patient_full_name,
        "pt_account": patient_account_number,
        
        # Insurance details
        "ins_name": insured_name,
        "ins_policy": insurance_policy_id,
        "insurance_name": insurance_company_name,
        "insurance_address": insurance_company_address,
        
        # Provider information
        "doc_name": provider_name,
        "doc_street": provider_address,
        "doc_phone": provider_phone_formatted,
        "doc_phone area": provider_area_code,
        "id_physician": provider_npi,
        "tax_id": provider_tax_id,
        
        # Financial totals
        "t_charge": f"{total_charges}.00",
        "amt_paid": f"{amount_paid}.00",
        "charge": f"{balance_due}.00",
        
        **diagnosis_data,
        **service_line_diagnoses,
        **service_line_data,
        **service_dates,
        **service_charges,
        **service_units
    }

def fill_cms1500_form(address_data, output_filename):
    """Fill the CMS-1500 form with the provided address data."""
    
    if not os.path.exists("form-cms1500.pdf"):
        print("Error: form-cms1500.pdf not found!")
        return False
    
    # Read the original form
    reader = PdfReader("form-cms1500.pdf")
    writer = PdfWriter()
    
    # Get the first page
    page = reader.pages[0]
    
    # Check if the form has fillable fields
    if "/AcroForm" in reader.trailer["/Root"]:
        fields = reader.get_form_text_fields()
        
        # Fill the form
        writer.clone_reader_document_root(reader)
        
        # Update text fields
        field_updates = {}
        checkbox_fields = ['insurance_type_index', 'insurance_type_name', 'sex', 'rel_to_ins', 
                          'employment', 'pt_auto_accident', 'other_accident', 'ins_sex', 
                          'ins_benefit_plan', 'lab', 'ssn', 'assignment']
        
        # Skip metadata fields (descriptions and counts)
        metadata_fields = ['num_diagnoses', 'num_service_lines'] + [f'diagnosis{i}_description' for i in range(1, 13)] + [f'cpt{i}_description' for i in range(1, 7)]
        skip_fields = checkbox_fields + metadata_fields
        
        for field_name, value in address_data.items():
            # Skip checkbox fields and metadata - handle them separately
            if field_name in skip_fields:
                continue
            if field_name in fields:
                field_updates[field_name] = value
        
        if field_updates:
            writer.update_page_form_field_values(writer.pages[0], field_updates)
        
        # Handle all checkbox fields
        checkbox_updates = {}
        
        # Insurance type (Field 1)
        if 'insurance_type_index' in address_data:
            insurance_type_index = address_data['insurance_type_index']
            checkbox_values = ["Medicare", "Medicaid", "Tricare", "Champva", "Group", "Feca", "Other"]
            if insurance_type_index < len(checkbox_values):
                checkbox_updates["insurance_type"] = checkbox_values[insurance_type_index]
        
        # All other checkboxes - direct mapping
        direct_checkbox_fields = ['sex', 'rel_to_ins', 'employment', 'pt_auto_accident', 
                                 'other_accident', 'ins_sex', 'ins_benefit_plan', 'lab', 
                                 'ssn', 'assignment']
        
        for field_name in direct_checkbox_fields:
            if field_name in address_data:
                checkbox_updates[field_name] = address_data[field_name]
        
        # Apply all checkbox updates
        if checkbox_updates:
            try:
                writer.update_page_form_field_values(writer.pages[0], checkbox_updates)
                print(f"Set {len(checkbox_updates)} checkbox fields")
            except Exception as e:
                print(f"Warning: Could not set some checkbox fields: {e}")
    else:
        print("Warning: PDF does not contain fillable form fields")
        writer.add_page(page)
    
    # Save the filled form
    with open(output_filename, "wb") as output_file:
        writer.write(output_file)
    
    return True

def generate_multiple_forms(n):
    """Generate N CMS-1500 forms with random addresses."""
    
    if not os.path.exists("form-cms1500.pdf"):
        print("Error: form-cms1500.pdf not found in current directory!")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = "generated_forms"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating {n} CMS-1500 forms with random addresses...")
    
    # Store all form data for JSON export
    all_forms_data = []
    
    for i in range(1, n + 1):
        # Generate random address
        address_data = generate_random_address()
        
        # Create output filename
        output_filename = os.path.join(output_dir, f"cms1500_form_{i:04d}.pdf")
        
        # Fill the form
        success = fill_cms1500_form(address_data, output_filename)
        
        if success:
            # Create individual JSON file for this form
            individual_json_filename = os.path.join(output_dir, f"cms1500_form_{i:04d}.json")
            individual_form_data = {
                "form_number": i,
                "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                "generated_date": fake.iso8601(),
                "form_data": address_data
            }
            
            with open(individual_json_filename, "w") as json_file:
                json.dump(individual_form_data, json_file, indent=2)
            
            # Add form metadata for combined file
            form_record = {
                "form_number": i,
                "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                "json_filename": f"cms1500_form_{i:04d}.json",
                "form_data": address_data
            }
            all_forms_data.append(form_record)
            
            patient_birth = f"{address_data['birth_mm']}/{address_data['birth_dd']}/{address_data['birth_yy']}"
            insurance_type = address_data['insurance_type_name']
            patient_sex = "Male" if address_data['sex'] == 'M' else "Female"
            relationship = {"S": "Self", "M": "Spouse", "C": "Child", "O": "Other"}.get(address_data['rel_to_ins'], address_data['rel_to_ins'])
            
            # Show primary diagnosis codes
            num_diagnoses = address_data['num_diagnoses']
            diagnosis_codes = []
            for j in range(1, num_diagnoses + 1):
                if f'diagnosis{j}' in address_data:
                    diagnosis_codes.append(address_data[f'diagnosis{j}'])
            diagnosis_str = ", ".join(diagnosis_codes) if diagnosis_codes else "None"
            
            # Show primary CPT codes
            num_service_lines = address_data['num_service_lines']
            cpt_codes = []
            for j in range(1, num_service_lines + 1):
                if f'cpt{j}' in address_data:
                    cpt_code = address_data[f'cpt{j}']
                    modifier = address_data.get(f'mod{j}', '')
                    if modifier:
                        cpt_codes.append(f"{cpt_code}-{modifier}")
                    else:
                        cpt_codes.append(cpt_code)
            cpt_str = ", ".join(cpt_codes) if cpt_codes else "None"
            
            print(f"Generated form {i:04d}: {address_data['pt_street']}, {address_data['pt_city']}, {address_data['pt_state']} {address_data['pt_zip']} | DOB: {patient_birth} | {patient_sex} | {insurance_type} | Relationship: {relationship} | Diagnoses: {diagnosis_str} | CPT: {cpt_str}")
        else:
            print(f"Failed to generate form {i:04d}")
    
    # Save all form data to JSON file
    json_filename = os.path.join(output_dir, "forms_data.json")
    with open(json_filename, "w") as json_file:
        json.dump({
            "metadata": {
                "total_forms": len(all_forms_data),
                "generated_date": fake.iso8601(),
                "description": "CMS-1500 form data for validation"
            },
            "forms": all_forms_data
        }, json_file, indent=2)
    
    print(f"\nCompleted! Generated {n} forms in '{output_dir}' directory.")
    print(f"Individual JSON files created for each form (cms1500_form_XXXX.json)")
    print(f"Combined form data saved to '{json_filename}' for validation.")

def main():
    parser = argparse.ArgumentParser(description="Generate N CMS-1500 forms with random addresses")
    parser.add_argument("n", type=int, help="Number of forms to generate")
    
    args = parser.parse_args()
    
    if args.n <= 0:
        print("Error: N must be a positive integer")
        sys.exit(1)
    
    generate_multiple_forms(args.n)

if __name__ == "__main__":
    main()