#!/usr/bin/env python3

import argparse
import os
import json
from pypdf import PdfReader, PdfWriter
from faker import Faker
import sys
from pdf2image import convert_from_path

fake = Faker()

def generate_valid_npi():
    """Generate a valid 10-digit National Provider Identifier (NPI) with proper check digit."""
    # Generate first 9 digits
    prefix = "80840"  # Standard NPI prefix for individual providers
    sequence = fake.bothify(text="####")
    first_nine = prefix + sequence
    
    # Calculate check digit using Luhn algorithm
    check_digit = calculate_npi_check_digit(first_nine)
    return first_nine + str(check_digit)

def calculate_npi_check_digit(first_nine_digits):
    """Calculate NPI check digit using Luhn algorithm."""
    # Add prefix constant
    digits = "80840" + first_nine_digits
    
    # Apply Luhn algorithm
    total = 0
    for i, digit in enumerate(digits):
        n = int(digit)
        if i % 2 == 1:  # Every other digit starting from right
            n *= 2
            if n > 9:
                n -= 9
        total += n
    
    check_digit = (10 - (total % 10)) % 10
    return check_digit

def generate_realistic_insurance_id(insurance_type):
    """Generate realistic insurance ID numbers based on insurance type."""
    if insurance_type == "Medicare":
        # Medicare format: 1-3 letters + 2-9 digits + 0-2 letters
        return fake.bothify(text="#??######?")
    elif insurance_type == "Medicaid":
        # Medicaid varies by state, often numeric
        return fake.bothify(text="##########")
    elif insurance_type == "Blue Cross Blue Shield":
        # BCBS format: 3 letters + 9 digits
        return fake.bothify(text="???#########")
    elif insurance_type == "Aetna":
        # Aetna format: 1-2 letters + 8-9 digits
        return fake.bothify(text="??########")
    elif insurance_type == "Cigna":
        # Cigna format: typically numeric
        return fake.bothify(text="##########")
    elif insurance_type == "UnitedHealth":
        # UnitedHealth format: letters + numbers
        return fake.bothify(text="??########")
    else:
        # Generic insurance ID format
        return fake.bothify(text="??########")

def validate_patient_name(name):
    """Ensure patient name follows insurance card format standards."""
    # Remove extra spaces and ensure proper capitalization
    parts = [part.strip().title() for part in name.split() if part.strip()]
    if len(parts) < 2:
        # Ensure at least first and last name
        parts.append(fake.last_name())
    # Limit to 3 parts max (First Middle Last)
    return " ".join(parts[:3])

def get_compatible_cpt_codes(diagnosis_codes):
    """Return CPT codes that are medically appropriate for the given diagnosis codes."""
    # Mapping of diagnosis types to appropriate CPT codes
    diagnosis_cpt_mapping = {
        # Diabetes diagnoses
        'diabetes': {
            'codes': ['E11.9', 'E11.40', 'E11.65'],
            'cpts': [('99213', 'Office visit'), ('99214', 'Office visit complex'), ('80053', 'Metabolic panel'), ('85025', 'CBC')]
        },
        # Hypertension
        'hypertension': {
            'codes': ['I10', 'I12.9'],
            'cpts': [('99213', 'Office visit'), ('93000', 'ECG'), ('80053', 'Metabolic panel')]
        },
        # Respiratory
        'respiratory': {
            'codes': ['J44.1', 'J45.9', 'J06.9'],
            'cpts': [('99213', 'Office visit'), ('94010', 'Spirometry'), ('71020', 'Chest X-ray')]
        },
        # Routine care
        'preventive': {
            'codes': ['Z00.00'],
            'cpts': [('99396', 'Preventive medicine'), ('85025', 'CBC'), ('80053', 'Metabolic panel'), ('90471', 'Immunization')]
        },
        # Infections
        'infection': {
            'codes': ['A49.9', 'B34.9'],
            'cpts': [('99213', 'Office visit'), ('85025', 'CBC'), ('36415', 'Venipuncture')]
        },
        # Injury
        'injury': {
            'codes': ['S72.001A', 'T14.90XA'],
            'cpts': [('99283', 'ER visit'), ('73060', 'X-ray'), ('12001', 'Wound repair')]
        },
        # General symptoms
        'symptoms': {
            'codes': ['R50.9', 'R06.02', 'R51'],
            'cpts': [('99213', 'Office visit'), ('99214', 'Office visit complex'), ('85025', 'CBC')]
        }
    }
    
    # Find which category the diagnoses belong to
    compatible_cpts = set()
    for diag_code in diagnosis_codes:
        for category, data in diagnosis_cpt_mapping.items():
            if any(diag_code.startswith(code.split('.')[0]) for code in data['codes']):
                compatible_cpts.update([cpt[0] for cpt in data['cpts']])
    
    # If no specific match, return general office visit codes
    if not compatible_cpts:
        compatible_cpts = {'99213', '99214', '99203', '85025'}
    
    return list(compatible_cpts)

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
    
    # Generate patient sex (Field 3 - Patient Sex) - ensure only one is selected
    patient_sex_options = ["M", "F"]  # M=Male, F=Female
    selected_patient_sex = fake.random_element(patient_sex_options)
    # Validate: never allow both M and F to be selected simultaneously
    
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
    
    # Generate patient identity information with validation
    patient_full_name = validate_patient_name(fake.name())
    patient_account_number = fake.bothify(text="####-###-####")  # Medical record number format
    
    # Generate insurance details with realistic ID format
    insured_name = patient_full_name if fake.random_int(1, 100) <= 70 else validate_patient_name(fake.name())  # 70% self, 30% other
    insurance_policy_id = generate_realistic_insurance_id(selected_insurance_name)
    
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
    
    # Generate provider information with valid NPI
    provider_name = f"Dr. {fake.first_name()} {fake.last_name()}, MD"
    provider_address = fake.address().replace('\n', ', ')
    provider_npi = generate_valid_npi()  # Valid 10-digit NPI with check digit
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
    
    # Generate diagnoses first to ensure CPT code compatibility
    # PHASE 1: Generate diagnoses first to ensure CPT code compatibility
    
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
    
    # Extended diagnosis support (1-12 diagnoses for complex cases)
    # Most claims have 1-4 diagnoses, but complex cases can have up to 12
    diagnosis_probabilities = [
        (1, 25),  # 1 diagnosis: 25%
        (2, 30),  # 2 diagnoses: 30% 
        (3, 20),  # 3 diagnoses: 20%
        (4, 15),  # 4 diagnoses: 15%
        (5, 5),   # 5 diagnoses: 5%
        (6, 3),   # 6 diagnoses: 3%
        (7, 1),   # 7+ diagnoses: 2% total (complex cases)
        (8, 0.5),
        (9, 0.3),
        (10, 0.1),
        (11, 0.05),
        (12, 0.05)
    ]
    
    # Weighted random selection for number of diagnoses
    random_val = fake.random_int(1, 10000) / 100  # 0.01 to 100.00
    cumulative = 0
    num_diagnoses = 1  # default
    for count, probability in diagnosis_probabilities:
        cumulative += probability
        if random_val <= cumulative:
            num_diagnoses = count
            break
    
    selected_diagnoses = fake.random_elements(common_icd10_codes, length=num_diagnoses, unique=True)
    
    # Extract just the diagnosis codes for CPT compatibility checking
    diagnosis_codes = [code for code, description in selected_diagnoses]
    compatible_cpt_codes = get_compatible_cpt_codes(diagnosis_codes)
    
    # Generate 1-6 service lines (most claims have 1-3 services)
    num_service_lines = fake.random_int(1, 6)
    
    # Select procedures from compatible CPT codes based on diagnoses
    if len(compatible_cpt_codes) >= num_service_lines:
        selected_cpt_codes = fake.random_elements(compatible_cpt_codes, length=num_service_lines, unique=True)
    else:
        # If not enough compatible codes, add comprehensive general codes
        general_codes = ['99213', '99214', '99203', '99204', '85025', '80053', '36415', 
                        '90471', '93000', '94010', '71020', '73030', '12001', '11042']
        all_available = list(set(compatible_cpt_codes + general_codes))
        
        # Ensure we have enough codes, limit service lines if necessary
        if len(all_available) < num_service_lines:
            num_service_lines = len(all_available)
        
        selected_cpt_codes = fake.random_elements(all_available, length=num_service_lines, unique=True)
    
    # Convert to the format expected by the rest of the code
    selected_procedures = [(code, f"Medical service for {code}") for code in selected_cpt_codes]
    
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
    
    # Type of service codes for medical billing
    type_of_service_codes = [
        "1",   # Medical care
        "2",   # Surgery
        "3",   # Consultation
        "4",   # Diagnostic X-ray
        "5",   # Diagnostic laboratory
        "6",   # Radiation therapy
        "7",   # Anesthesia
        "8",   # Assistant at surgery
        "9",   # Other medical items or services
        "0",   # Whole blood only
        "A",   # Used DME
        "E",   # Ambulance
        "F",   # Oxygen and other gases
        "P",   # Lenses, prisms, etc.
        "V",   # Pneumococcal/influenza virus vaccine
        "S",   # Surgical dressings
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
        
        # Primary modifier (20% chance of having a modifier)
        if fake.random_int(1, 100) <= 20:
            modifier = fake.random_element([m for m in common_modifiers if m != ""])
            service_line_data[f"mod{i}"] = modifier
        else:
            service_line_data[f"mod{i}"] = ""
        
        # Additional modifier positions (10% chance each for mod1a, mod1b, mod1c)
        for mod_pos in ['a', 'b', 'c']:
            if fake.random_int(1, 100) <= 10:  # 10% chance for additional modifiers
                additional_modifier = fake.random_element([m for m in common_modifiers if m != ""])
                service_line_data[f"mod{i}{mod_pos}"] = additional_modifier
            else:
                service_line_data[f"mod{i}{mod_pos}"] = ""
        
        # Service dates (within last 30 days) - ensure MM/DD/YY format consistency
        service_date = fake.date_between(start_date='-30d', end_date='today')
        # Always use 2-digit year format for CMS-1500 compatibility
        service_dates[f"sv{i}_mm_from"] = f"{service_date.month:02d}"
        service_dates[f"sv{i}_dd_from"] = f"{service_date.day:02d}"
        service_dates[f"sv{i}_yy_from"] = f"{service_date.year % 100:02d}"
        
        # For most services, from and to dates are the same (validate date range)
        # Ensure end date is not before start date
        service_dates[f"sv{i}_mm_end"] = f"{service_date.month:02d}"
        service_dates[f"sv{i}_dd_end"] = f"{service_date.day:02d}"
        service_dates[f"sv{i}_yy_end"] = f"{service_date.year % 100:02d}"
        
        # Place of service
        place_code = fake.random_element(place_of_service_codes)
        service_line_data[f"place{i}"] = place_code
        
        # Type of service - match to procedure type
        if code.startswith('99'):  # E&M codes
            type_code = "1"  # Medical care
        elif code.startswith(('10', '11', '12', '20', '21')):  # Surgery codes  
            type_code = "2"  # Surgery
        elif code.startswith(('70', '71', '72', '73', '74', '75', '76', '77')):  # Radiology
            type_code = "4"  # Diagnostic X-ray
        elif code.startswith(('80', '81', '82', '83', '84', '85', '86', '87', '88', '89')):  # Lab
            type_code = "5"  # Diagnostic laboratory
        elif code.startswith('36415'):  # Venipuncture
            type_code = "5"  # Diagnostic laboratory
        elif code.startswith('90471'):  # Immunization
            type_code = "V"  # Vaccine
        elif code.startswith('93000'):  # ECG
            type_code = "4"  # Diagnostic
        elif code.startswith('94010'):  # Spirometry
            type_code = "4"  # Diagnostic
        else:
            type_code = fake.random_element(type_of_service_codes[:3])  # Default to medical/surgery/consultation
        
        service_line_data[f"type{i}"] = type_code
        
        # Emergency indicator (8% chance - increased from 5% for better ML training)
        emergency_procedures = ['99281', '99282', '99283', '99284', '99285']  # ER visit codes
        if any(code.startswith(emergency) for emergency in emergency_procedures):
            service_line_data[f"emg{i}"] = "Y"  # Emergency procedures always marked
        elif fake.random_int(1, 100) <= 8:
            service_line_data[f"emg{i}"] = "Y"
        else:
            service_line_data[f"emg{i}"] = ""
        
        # Charges ($50-$500)
        charge = fake.random_int(50, 500)
        service_charges[f"ch{i}"] = f"{charge}.00"
        total_charges += charge
        
        # Units (1-10) - realistic for medical services
        # Different service types have different typical unit counts
        if code.startswith('90471'):  # Immunization - typically 1 unit
            units = 1
        elif code.startswith(('80', '81', '82', '83', '84', '85', '86', '87', '88')):  # Lab tests - 1-2 units
            units = fake.random_int(1, 2)
        elif code.startswith('99'):  # E&M codes - always 1 unit
            units = 1
        else:  # Other procedures - 1-5 units
            units = fake.random_int(1, 5)
        service_units[f"units{i}"] = str(units)
        
        # Days (for services that span multiple days - 15% chance)
        if fake.random_int(1, 100) <= 15:
            days = fake.random_int(1, 30)  # 1-30 days
            service_line_data[f"day{i}"] = str(days)
        else:
            service_line_data[f"day{i}"] = ""
    
    # Fill remaining service lines with empty values
    for i in range(num_service_lines + 1, 7):
        service_line_data[f"cpt{i}"] = ""
        service_line_data[f"mod{i}"] = ""
        service_line_data[f"mod{i}a"] = ""
        service_line_data[f"mod{i}b"] = ""
        service_line_data[f"mod{i}c"] = ""
        service_dates[f"sv{i}_mm_from"] = ""
        service_dates[f"sv{i}_dd_from"] = ""
        service_dates[f"sv{i}_yy_from"] = ""
        service_dates[f"sv{i}_mm_end"] = ""
        service_dates[f"sv{i}_dd_end"] = ""
        service_dates[f"sv{i}_yy_end"] = ""
        service_line_data[f"place{i}"] = ""
        service_line_data[f"type{i}"] = ""
        service_line_data[f"emg{i}"] = ""
        service_line_data[f"day{i}"] = ""
        service_charges[f"ch{i}"] = ""
        service_units[f"units{i}"] = ""
    
    # Generate financial totals
    amount_paid = fake.random_int(0, int(total_charges * 0.8))  # 0-80% of total charges paid
    balance_due = total_charges - amount_paid
    
    # Generate treatment timeline dates (Box 14, 15, 16)
    # Current illness onset date (Box 14) - 30-365 days ago
    if fake.random_int(1, 100) <= 60:  # 60% chance of having illness onset date
        illness_onset_date = fake.date_between(start_date='-365d', end_date='-30d')
        cur_ill_mm = f"{illness_onset_date.month:02d}"
        cur_ill_dd = f"{illness_onset_date.day:02d}"
        cur_ill_yy = f"{illness_onset_date.year % 100:02d}"
    else:
        cur_ill_mm = cur_ill_dd = cur_ill_yy = ""
    
    # Similar illness date (Box 15) - only if different from current illness
    if fake.random_int(1, 100) <= 20:  # 20% chance of having similar illness date
        similar_illness_date = fake.date_between(start_date='-2y', end_date='-6m')
        sim_ill_mm = f"{similar_illness_date.month:02d}"
        sim_ill_dd = f"{similar_illness_date.day:02d}"
        sim_ill_yy = f"{similar_illness_date.year % 100:02d}"
    else:
        sim_ill_mm = sim_ill_dd = sim_ill_yy = ""
    
    # Unable to work dates (Box 16) - only for work-related conditions
    if fake.random_int(1, 100) <= 25:  # 25% chance of work disability
        work_start_date = fake.date_between(start_date='-90d', end_date='-7d')
        work_end_date = fake.date_between(start_date=work_start_date, end_date='today')
        work_mm_from = f"{work_start_date.month:02d}"
        work_dd_from = f"{work_start_date.day:02d}"
        work_yy_from = f"{work_start_date.year % 100:02d}"
        work_mm_end = f"{work_end_date.month:02d}"
        work_dd_end = f"{work_end_date.day:02d}"
        work_yy_end = f"{work_end_date.year % 100:02d}"
    else:
        work_mm_from = work_dd_from = work_yy_from = ""
        work_mm_end = work_dd_end = work_yy_end = ""
    
    # Hospitalization dates (Box 18) - for serious conditions
    if fake.random_int(1, 100) <= 15:  # 15% chance of hospitalization
        hosp_admit_date = fake.date_between(start_date='-30d', end_date='-3d')
        hosp_discharge_date = fake.date_between(start_date=hosp_admit_date, end_date='today')
        hosp_mm_from = f"{hosp_admit_date.month:02d}"
        hosp_dd_from = f"{hosp_admit_date.day:02d}"
        hosp_yy_from = f"{hosp_admit_date.year % 100:02d}"
        hosp_mm_end = f"{hosp_discharge_date.month:02d}"
        hosp_dd_end = f"{hosp_discharge_date.day:02d}"
        hosp_yy_end = f"{hosp_discharge_date.year % 100:02d}"
    else:
        hosp_mm_from = hosp_dd_from = hosp_yy_from = ""
        hosp_mm_end = hosp_dd_end = hosp_yy_end = ""
    
    # Accident place (Box 10b, 10c) - state where accident occurred
    if auto_accident_related == "YES" or other_accident_related == "YES":
        # Use realistic US state abbreviations
        us_states = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]
        accident_place = fake.random_element(us_states)
    else:
        accident_place = ""
    
    # Secondary insurance (Box 9) - 30% chance of having secondary coverage
    if fake.random_int(1, 100) <= 30:
        other_ins_name = fake.name()
        other_ins_policy = fake.bothify(text="??########")
        other_ins_plan_name = fake.random_element([
            "Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth",
            "Humana", "Anthem", "Kaiser Permanente"
        ])
    else:
        other_ins_name = other_ins_policy = other_ins_plan_name = ""
    
    # Authorization and reference numbers (Box 19, 23)
    if fake.random_int(1, 100) <= 25:  # 25% chance of prior authorization
        prior_auth = fake.bothify(text="PA########")
    else:
        prior_auth = ""
    
    if fake.random_int(1, 100) <= 15:  # 15% chance of original reference
        original_ref = fake.bothify(text="REF#######")
    else:
        original_ref = ""
    
    if fake.random_int(1, 100) <= 10:  # 10% chance of Medicaid resubmission
        medicaid_resub = fake.bothify(text="###")
    else:
        medicaid_resub = ""
    
    # Referring physician (Box 17) with valid NPI
    if fake.random_int(1, 100) <= 40:  # 40% chance of referral
        ref_physician = f"Dr. {fake.first_name()} {fake.last_name()}, MD"
        ref_physician_npi = generate_valid_npi()  # Valid NPI with check digit
        ref_physician_qualifier = "1B"  # NPI qualifier
    else:
        ref_physician = ""
        ref_physician_npi = ""
        ref_physician_qualifier = ""
    
    # Signature fields
    pt_signature = "Patient Signature on File" if fake.random_int(1, 100) <= 85 else ""
    pt_signature_date = fake.date_between(start_date='-30d', end_date='today').strftime('%m/%d/%y') if pt_signature else ""
    
    physician_signature = f"{provider_name}"
    physician_signature_date = fake.date_between(start_date='-7d', end_date='today').strftime('%m/%d/%y')
    
    # Service facility (Box 32) - for services not performed at billing location
    if fake.random_int(1, 100) <= 35:  # 35% chance of different service facility
        facility_names = [
            "City General Hospital",
            "Regional Medical Center", 
            "Outpatient Surgery Center",
            "Diagnostic Imaging Center",
            "Physical Therapy Clinic",
            "Urgent Care Center",
            "Community Health Center"
        ]
        fac_name = fake.random_element(facility_names)
        fac_street = fake.address().replace('\n', ', ')
        fac_location = f"{fake.city()}, {fake.state_abbr()} {fake.zipcode()}"
    else:
        fac_name = fac_street = fac_location = ""
    
    # PHASE 2: Insurance & Provider Detail Fields
    
    # Insured's address (Box 7) - 85% chance of having insured address
    if fake.random_int(1, 100) <= 85:
        ins_street = fake.street_address()
        ins_city = fake.city()
        ins_state = fake.state_abbr()
        ins_zip = fake.zipcode()
        ins_phone_area = str(fake.random_int(100, 999))
        ins_phone = fake.bothify(text="###-####")
    else:
        ins_street = ins_city = ins_state = ins_zip = ""
        ins_phone_area = ins_phone = ""
    
    # Additional insurance identifiers (Box 11d, various insurance fields)
    insurance_id = fake.bothify(text="##########") if fake.random_int(1, 100) <= 70 else ""
    insurance_address2 = f"Suite {fake.random_int(100, 999)}" if fake.random_int(1, 100) <= 30 else ""
    insurance_city_state_zip = f"{fake.city()}, {fake.state_abbr()} {fake.zipcode()}" if fake.random_int(1, 100) <= 60 else ""
    
    # Provider identification numbers (Box 25, 33)
    # PIN (Provider Identification Number) - legacy identifier
    pin = fake.bothify(text="##########") if fake.random_int(1, 100) <= 40 else ""
    pin1 = fake.bothify(text="##########") if fake.random_int(1, 100) <= 35 else ""
    
    # Group practice identifiers
    grp = fake.bothify(text="GRP######") if fake.random_int(1, 100) <= 50 else ""
    grp1 = fake.bothify(text="######") if fake.random_int(1, 100) <= 45 else ""
    
    # Provider location identifier
    doc_location = f"{fake.city()}, {fake.state_abbr()}" if fake.random_int(1, 100) <= 55 else ""
    
    # Supplemental claim information (various boxes)
    suppl_fields = {}
    for suffix in ["", "a", "b", "c", "d", "e"]:
        field_name = f"Suppl{suffix}" if suffix else "Suppl"
        if fake.random_int(1, 100) <= 15:  # 15% chance for supplemental info
            suppl_fields[field_name] = fake.bothify(text="SUP###")
        else:
            suppl_fields[field_name] = ""
    
    # NUCC (National Uniform Claim Committee) usage field
    nucc_use = fake.bothify(text="NUCC###") if fake.random_int(1, 100) <= 20 else ""
    
    # Local use codes (Box 24K - local use area)
    local_use_fields = {}
    for i in range(1, 7):  # local1 through local6
        for suffix in ["", "a"]:  # local1, local1a, etc.
            field_name = f"local{i}{suffix}"
            if fake.random_int(1, 100) <= 25:  # 25% chance of local use codes
                local_codes = ["LOC", "MED", "REG", "SPEC", "PROV", "FAC"]
                local_use_fields[field_name] = fake.random_element(local_codes) + fake.bothify(text="###")
            else:
                local_use_fields[field_name] = ""
    
    # EPSDT (Early and Periodic Screening, Diagnostic and Treatment) fields
    epsdt_fields = {}
    for i in range(1, 7):  # epsdt1 through epsdt6
        field_name = f"epsdt{i}"
        if fake.random_int(1, 100) <= 20:  # 20% chance - EPSDT is for pediatric Medicaid
            epsdt_values = ["Y", "N", "P"]  # Yes, No, Pending
            epsdt_fields[field_name] = fake.random_element(epsdt_values)
        else:
            epsdt_fields[field_name] = ""
    
    # Plan codes (treatment/service plan codes)
    plan_fields = {}
    for i in range(1, 7):  # plan1 through plan6
        field_name = f"plan{i}"
        if fake.random_int(1, 100) <= 30:  # 30% chance of plan codes
            plan_types = ["PREV", "THER", "DIAG", "SURG", "EMRG", "ROUT"]
            plan_fields[field_name] = fake.random_element(plan_types) + fake.bothify(text="##")
        else:
            plan_fields[field_name] = ""
    
    # PHASE 3: Enhanced Clinical Timeline & Insurance Fields
    
    # Insurance plan details (Box 11c)
    ins_plan_name = ""
    ins_signature = ""
    if fake.random_int(1, 100) <= 75:  # 75% chance of having plan name
        plan_names = [
            "HMO Basic", "PPO Premium", "EPO Standard", "POS Select",
            "Medicare Supplement Plan F", "Medicare Advantage", "Medigap Plan G",
            "Employee Health Plan", "Family Coverage", "Individual Plan",
            "High Deductible Health Plan", "Bronze Plan", "Silver Plan", "Gold Plan"
        ]
        ins_plan_name = fake.random_element(plan_names)
    
    # Insured signature field (Box 12) - 70% chance of signature on file
    if fake.random_int(1, 100) <= 70:
        ins_signature = "Signature on File"
    
    # Enhanced laboratory services logic based on CPT codes
    # Override the basic lab field with intelligent detection
    lab_related_cpts = ['80053', '80061', '85025', '85027', '36415', '81002', '82962']
    has_lab_services = False
    for i in range(1, num_service_lines + 1):
        cpt_code = service_line_data.get(f"cpt{i}", "")
        if any(cpt_code.startswith(lab_code) for lab_code in lab_related_cpts):
            has_lab_services = True
            break
    
    # Set lab field based on actual services (overrides random assignment from earlier)
    if has_lab_services:
        lab = "YES"  # Override previous random assignment
    # Keep existing random assignment if no lab CPT codes detected
    
    # Diagnosis generation moved above - no duplicate code needed here
    
    # Create extended diagnosis code data (supporting up to 12 diagnoses) - Box 21
    diagnosis_data = {}
    for i in range(1, 13):  # diagnosis1 through diagnosis12
        if i <= num_diagnoses:
            code, description = selected_diagnoses[i-1]
            # New box-based naming
            diagnosis_data[f"box_21_diagnosis_{i}_code"] = code
            diagnosis_data[f"box_21_diagnosis_{i}_description"] = description
            # Legacy naming for backward compatibility
            diagnosis_data[f"diagnosis{i}"] = code
            diagnosis_data[f"diagnosis{i}_description"] = description
        else:
            # New box-based naming
            diagnosis_data[f"box_21_diagnosis_{i}_code"] = ""
            diagnosis_data[f"box_21_diagnosis_{i}_description"] = ""
            # Legacy naming for backward compatibility
            diagnosis_data[f"diagnosis{i}"] = ""
            diagnosis_data[f"diagnosis{i}_description"] = ""
    
    # For service lines, randomly reference the diagnosis codes - Box 24e
    # diag1-diag6 should contain pointers (A, B, C, D) to the diagnosis codes
    diagnosis_pointers = ['A', 'B', 'C', 'D', 'E', 'F']
    service_line_diagnoses = {}
    for i in range(1, 7):  # diag1 through diag6
        if i <= num_diagnoses:
            # Reference one of the available diagnoses, limited by diagnosis_pointers length
            max_pointer_index = min(num_diagnoses - 1, len(diagnosis_pointers) - 1)
            pointer_index = fake.random_int(0, max_pointer_index)
            # New box-based naming
            service_line_diagnoses[f"box_24e_diagnosis_pointer_{i}"] = diagnosis_pointers[pointer_index]
            # Legacy naming for backward compatibility
            service_line_diagnoses[f"diag{i}"] = diagnosis_pointers[pointer_index]
        else:
            # New box-based naming
            service_line_diagnoses[f"box_24e_diagnosis_pointer_{i}"] = ""
            # Legacy naming for backward compatibility
            service_line_diagnoses[f"diag{i}"] = ""
    
    return {
        # Box 1: Type of Insurance
        "box_1_insurance_type_index": selected_insurance_type,
        "box_1_insurance_type_name": selected_insurance_name,
        
        # Box 1a: Insured's ID Number
        "box_1a_insured_id_number": insurance_policy_id,
        
        # Box 2: Patient's Name
        "box_2_patient_name": patient_full_name,
        
        # Box 3: Patient's Birth Date & Sex
        "box_3_patient_birth_month": patient_birth_mm,
        "box_3_patient_birth_day": patient_birth_dd,
        "box_3_patient_birth_year": patient_birth_yy,
        "box_3_patient_sex": selected_patient_sex,
        
        # Box 4: Insured's Name
        "box_4_insured_name": insured_name,
        
        # Box 5: Patient's Address
        "box_5_patient_street": street_address,
        "box_5_patient_city": city,
        "box_5_patient_state": state,
        "box_5_patient_zip": zip_code,
        "box_5_patient_area_code": area_code,
        "box_5_patient_phone": phone_number,
        
        # Box 6: Patient Relationship to Insured
        "box_6_patient_relationship_to_insured": selected_relationship,
        
        # Box 7: Insured's Address
        "box_7_insured_street": ins_street,
        "box_7_insured_city": ins_city,
        "box_7_insured_state": ins_state,
        "box_7_insured_zip": ins_zip,
        "box_7_insured_phone_area": ins_phone_area,
        "box_7_insured_phone": ins_phone,
        
        # Box 8: Reserved for NUCC Use
        "box_8_reserved_for_nucc_use": nucc_use,
        
        # Box 9: Other Insured's Name
        "box_9_other_insured_name": other_ins_name,
        
        # Box 9a: Other Insured's Policy or Group Number
        "box_9a_other_insured_policy_number": other_ins_policy,
        
        # Box 9d: Insurance Plan Name or Program Name
        "box_9d_other_insurance_plan_name": other_ins_plan_name,
        
        # Box 10: Is Condition Related to...
        "box_10a_employment_related": employment_related,
        "box_10b_auto_accident_related": auto_accident_related,
        "box_10c_other_accident_related": other_accident_related,
        "box_10d_accident_place": accident_place,
        
        # Box 11: Insured's Policy Group or FECA Number
        "box_11_insured_group_number": grp,
        
        # Box 11a: Insured's Date of Birth & Sex
        "box_11a_insured_birth_month": ins_birth_mm,
        "box_11a_insured_birth_day": ins_birth_dd,
        "box_11a_insured_birth_year": ins_birth_yy,
        "box_11a_insured_sex": selected_insured_sex,
        
        # Box 11c: Insurance Plan Name or Program Name
        "box_11c_insurance_plan_name": ins_plan_name,
        
        # Box 11d: Is There Another Health Benefit Plan?
        "box_11d_other_health_benefit_plan": other_benefit_plan,
        
        # Box 12: Patient's or Authorized Person's Signature
        "box_12_patient_signature": pt_signature,
        "box_12_patient_signature_date": pt_signature_date,
        
        # Box 13: Insured's or Authorized Person's Signature
        "box_13_insured_signature": ins_signature,
        
        # Box 14: Date of Current Illness, Injury, or Pregnancy
        "box_14_current_illness_month": cur_ill_mm,
        "box_14_current_illness_day": cur_ill_dd,
        "box_14_current_illness_year": cur_ill_yy,
        
        # Box 15: Other Date
        "box_15_other_date_month": sim_ill_mm,
        "box_15_other_date_day": sim_ill_dd,
        "box_15_other_date_year": sim_ill_yy,
        
        # Box 16: Dates Patient Unable to Work
        "box_16_work_unable_from_month": work_mm_from,
        "box_16_work_unable_from_day": work_dd_from,
        "box_16_work_unable_from_year": work_yy_from,
        "box_16_work_unable_to_month": work_mm_end,
        "box_16_work_unable_to_day": work_dd_end,
        "box_16_work_unable_to_year": work_yy_end,
        
        # Box 17: Name of Referring Provider
        "box_17_referring_provider_name": ref_physician,
        "box_17a_referring_provider_npi": ref_physician_npi,
        "box_17b_referring_provider_qualifier": ref_physician_qualifier,
        
        # Box 18: Hospitalization Dates Related to Current Services
        "box_18_hospitalization_from_month": hosp_mm_from,
        "box_18_hospitalization_from_day": hosp_dd_from,
        "box_18_hospitalization_from_year": hosp_yy_from,
        "box_18_hospitalization_to_month": hosp_mm_end,
        "box_18_hospitalization_to_day": hosp_dd_end,
        "box_18_hospitalization_to_year": hosp_yy_end,
        
        # Box 20: Outside Lab? $ Charges
        "box_20_outside_lab": outside_lab,
        
        # Box 21: Diagnosis or Nature of Illness or Injury
        # Box 22: Resubmission Code/Original Reference Number
        "box_22_medicaid_resubmission": medicaid_resub,
        "box_22_original_reference_number": original_ref,
        
        # Box 23: Prior Authorization Number
        "box_23_prior_authorization": prior_auth,
        
        # Box 25: Federal Tax ID Number
        "box_25_federal_tax_id": provider_tax_id,
        "box_25_tax_id_type": tax_id_type,
        
        # Box 26: Patient's Account Number
        "box_26_patient_account_number": patient_account_number,
        
        # Box 27: Accept Assignment?
        "box_27_accept_assignment": accept_assignment,
        
        # Box 28: Total Charge
        "box_28_total_charge": f"{total_charges}.00",
        
        # Box 29: Amount Paid
        "box_29_amount_paid": f"{amount_paid}.00",
        
        # Box 30: Reserved for NUCC Use
        "box_30_balance_due": f"{balance_due}.00",
        
        # Box 31: Signature of Physician or Supplier
        "box_31_physician_signature": physician_signature,
        "box_31_physician_signature_date": physician_signature_date,
        
        # Box 32: Service Facility Location Information
        "box_32_service_facility_name": fac_name,
        "box_32_service_facility_street": fac_street,
        "box_32_service_facility_location": fac_location,
        
        # Box 33: Billing Provider Info & Phone Number
        "box_33_billing_provider_name": provider_name,
        "box_33_billing_provider_address": provider_address,
        "box_33_billing_provider_phone": provider_phone_formatted,
        "box_33_billing_provider_phone_area": provider_area_code,
        "box_33a_billing_provider_npi": provider_npi,
        
        # Additional insurance details
        "insurance_company_name": insurance_company_name,
        "insurance_company_address": insurance_company_address,
        "insurance_id": insurance_id,
        "insurance_address2": insurance_address2,
        "insurance_city_state_zip": insurance_city_state_zip,
        "pin": pin,
        "pin1": pin1,
        "grp1": grp1,
        "doc_location": doc_location,
        
        # Metadata fields for processing
        "num_diagnoses": num_diagnoses,
        "num_service_lines": num_service_lines,
        
        # Legacy field mappings for backward compatibility
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
        "pt_name": patient_full_name,
        "pt_account": patient_account_number,
        "ins_name": insured_name,
        "ins_policy": insurance_policy_id,
        "doc_name": provider_name,
        "doc_street": provider_address,
        "doc_phone": provider_phone_formatted,
        "doc_phone area": provider_area_code,
        "id_physician": provider_npi,
        "tax_id": provider_tax_id,
        "t_charge": f"{total_charges}.00",
        "amt_paid": f"{amount_paid}.00",
        "charge": f"{balance_due}.00",
        "cur_ill_mm": cur_ill_mm,
        "cur_ill_dd": cur_ill_dd,
        "cur_ill_yy": cur_ill_yy,
        "sim_ill_mm": sim_ill_mm,
        "sim_ill_dd": sim_ill_dd,
        "sim_ill_yy": sim_ill_yy,
        "work_mm_from": work_mm_from,
        "work_dd_from": work_dd_from,
        "work_yy_from": work_yy_from,
        "work_mm_end": work_mm_end,
        "work_dd_end": work_dd_end,
        "work_yy_end": work_yy_end,
        "hosp_mm_from": hosp_mm_from,
        "hosp_dd_from": hosp_dd_from,
        "hosp_yy_from": hosp_yy_from,
        "hosp_mm_end": hosp_mm_end,
        "hosp_dd_end": hosp_dd_end,
        "hosp_yy_end": hosp_yy_end,
        "accident_place": accident_place,
        "other_ins_name": other_ins_name,
        "other_ins_policy": other_ins_policy,
        "other_ins_plan_name": other_ins_plan_name,
        "prior_auth": prior_auth,
        "original_ref": original_ref,
        "medicaid_resub": medicaid_resub,
        "ref_physician": ref_physician,
        "physician number 17a": ref_physician_npi,
        "physician number 17a1": ref_physician_qualifier,
        "pt_signature": pt_signature,
        "pt_date": pt_signature_date,
        "physician_signature": physician_signature,
        "physician_date": physician_signature_date,
        "fac_name": fac_name,
        "fac_street": fac_street,
        "fac_location": fac_location,
        "ins_street": ins_street,
        "ins_city": ins_city,
        "ins_state": ins_state,
        "ins_zip": ins_zip,
        "ins_phone": ins_phone,
        "ins_phone area": ins_phone_area,
        "NUCC USE": nucc_use,
        "ins_plan_name": ins_plan_name,
        "ins_signature": ins_signature,
        
        **diagnosis_data,
        **service_line_diagnoses,
        **service_line_data,
        **service_dates,
        **service_charges,
        **service_units,
        **suppl_fields,
        **local_use_fields,
        **epsdt_fields,
        **plan_fields
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
        
        # Handle all checkbox fields with proper PDF name objects
        checkbox_updates = {}
        
        # Import PDF objects
        from pypdf.generic import NameObject
        
        # Insurance type (Field 1) - Radio button group handling
        if 'insurance_type_index' in address_data:
            insurance_type_index = address_data['insurance_type_index']
            # Correct export values based on PDF analysis
            insurance_mapping = {
                0: NameObject("/Medicare"),     # Medicare
                1: NameObject("/Medicaid"),     # Medicaid  
                2: NameObject("/Tricare"),      # Tricare
                3: NameObject("/Champva"),      # Champva
                4: NameObject("/Group"),        # Group Health Plan
                5: NameObject("/Feca"),         # FECA
                6: NameObject("/Other")         # Other
            }
            if insurance_type_index in insurance_mapping:
                # For radio button groups, set the field value to the selected export value
                checkbox_updates["insurance_type"] = insurance_mapping[insurance_type_index]
        
        # Sex field - convert M/F to PDF name objects (Radio button group)
        if 'sex' in address_data:
            sex_value = address_data['sex']
            if sex_value == 'M':
                checkbox_updates['sex'] = NameObject("/M")
            elif sex_value == 'F':
                checkbox_updates['sex'] = NameObject("/F")
        
        # Other checkbox fields with proper mappings (using actual export values from PDF analysis)
        checkbox_field_mappings = {
            'rel_to_ins': {'S': '/S', 'M': '/M', 'C': '/C', 'O': '/O'},
            'employment': {'YES': '/YES', 'NO': '/NO'},
            'pt_auto_accident': {'YES': '/YES', 'NO': '/NO'},
            'other_accident': {'YES': '/YES', 'NO': '/NO'},
            'ins_sex': {'MALE': '/MALE', 'FEMALE': '/FEMALE'},
            'ins_benefit_plan': {'YES': '/YES', 'NO': '/NO'},
            'lab': {'YES': '/YES', 'NO': '/NO'},
            'ssn': {'SSN': '/SSN', 'EIN': '/EIN'},
            'assignment': {'YES': '/YES', 'NO': '/NO'}
        }
        
        for field_name, value_mapping in checkbox_field_mappings.items():
            if field_name in address_data:
                raw_value = address_data[field_name]
                if raw_value in value_mapping:
                    checkbox_updates[field_name] = NameObject(value_mapping[raw_value])
        
        # Apply all checkbox updates
        if checkbox_updates:
            try:
                writer.update_page_form_field_values(writer.pages[0], checkbox_updates)
                print(f"Set {len(checkbox_updates)} checkbox fields")
            except Exception as e:
                print(f"Warning: Could not set some checkbox fields: {e}")
        
        # Always flatten the form to ensure checkboxes and field values are visually apparent
        # PyPDF 6.0.0 requires a different flattening approach
        try:
            # Check if we have form fields to work with
            form_fields = None
            if "/AcroForm" in reader.trailer["/Root"]:
                form_fields = reader.get_form_text_fields()
                print(f"Found {len(form_fields)} form fields")
            
            # For PyPDF 6.0.0, the most reliable approach is to write the PDF with fields
            # and then read it back to flatten it properly
            import tempfile
            flattened = False
            
            # Method 1: Use a temporary file approach for proper flattening
            try:
                # Save to temporary file first
                temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
                os.close(temp_fd)
                
                with open(temp_path, "wb") as temp_file:
                    writer.write(temp_file)
                
                # Read it back and flatten
                temp_reader = PdfReader(temp_path)
                flattened_writer = PdfWriter()
                
                for page in temp_reader.pages:
                    flattened_writer.add_page(page)
                
                # Now try flattening
                if hasattr(flattened_writer, '_flatten'):
                    flattened_writer._flatten()
                    writer = flattened_writer  # Use the flattened version
                    print("Form fields flattened using temp file method")
                    flattened = True
                
                # Clean up temp file
                os.unlink(temp_path)
                
            except Exception as e:
                print(f"Temp file flattening failed: {e}")
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            # Method 2: Try the direct _flatten method as fallback
            if hasattr(writer, '_flatten') and not flattened:
                try:
                    writer._flatten()
                    print("Form fields flattened using _flatten method")
                    flattened = True
                except Exception as e:
                    print(f"_flatten method failed: {e}")
            
            if not flattened:
                print("Warning: No flattening method succeeded - checkboxes may not be visually apparent in PDF")
                
        except Exception as e:
            print(f"Warning: Could not flatten form fields: {e} - checkboxes may not be visually apparent")
    else:
        print("Warning: PDF does not contain fillable form fields")
        writer.add_page(page)
    
    # Save the flattened form (PDF will now show checkboxes properly but won't be editable)
    with open(output_filename, "wb") as output_file:
        writer.write(output_file)
    
    return True

def create_core_subset_data(form_data):
    """Extract core CMS-1500 fields for a simplified JSON file."""
    
    core_fields = {
        # Box 1: Type of Insurance
        "box_1_insurance_type": form_data.get("box_1_insurance_type_name", ""),
        
        # Box 1a: Insured's ID Number  
        "box_1a_insured_id": form_data.get("box_1a_insured_id_number", ""),
        
        # Box 2: Patient's Name
        "box_2_patient_name": form_data.get("box_2_patient_name", ""),
        
        # Box 3: Patient's Birth Date & Sex
        "box_3_patient_dob": f"{form_data.get('box_3_patient_birth_month', '')}/{form_data.get('box_3_patient_birth_day', '')}/{form_data.get('box_3_patient_birth_year', '')}",
        "box_3_patient_sex": form_data.get("box_3_patient_sex", ""),
        
        # Box 4: Insured's Name
        "box_4_insured_name": form_data.get("box_4_insured_name", ""),
        
        # Box 5: Patient's Address (combined)
        "box_5_patient_address": f"{form_data.get('box_5_patient_street', '')}, {form_data.get('box_5_patient_city', '')}, {form_data.get('box_5_patient_state', '')} {form_data.get('box_5_patient_zip', '')}",
        "box_5_patient_phone": f"({form_data.get('box_5_patient_area_code', '')}) {form_data.get('box_5_patient_phone', '')}",
        
        # Box 6: Patient Relationship to Insured
        "box_6_relationship": form_data.get("box_6_patient_relationship_to_insured", ""),
        
        # Box 21: Primary Diagnosis (first 4 only for core subset)
        "box_21_primary_diagnosis": form_data.get("box_21_diagnosis_1_code", ""),
        "box_21_secondary_diagnosis": form_data.get("box_21_diagnosis_2_code", ""),
        "box_21_tertiary_diagnosis": form_data.get("box_21_diagnosis_3_code", ""),
        "box_21_quaternary_diagnosis": form_data.get("box_21_diagnosis_4_code", ""),
        
        # Box 24: Service Line 1 (primary service only for core subset)
        "box_24_primary_service_date": f"{form_data.get('sv1_mm_from', '')}/{form_data.get('sv1_dd_from', '')}/{form_data.get('sv1_yy_from', '')}",
        "box_24_primary_cpt_code": form_data.get("cpt1", ""),
        "box_24_primary_charge": form_data.get("ch1", ""),
        
        # Box 25: Provider Tax ID
        "box_25_provider_tax_id": form_data.get("box_25_federal_tax_id", ""),
        
        # Box 26: Patient Account Number
        "box_26_account_number": form_data.get("box_26_patient_account_number", ""),
        
        # Box 28: Total Charge
        "box_28_total_charge": form_data.get("box_28_total_charge", ""),
        
        # Box 33: Billing Provider
        "box_33_billing_provider": form_data.get("box_33_billing_provider_name", ""),
        "box_33_provider_npi": form_data.get("box_33a_billing_provider_npi", ""),
        
        # Summary fields for quick reference
        "summary": {
            "patient_name": form_data.get("box_2_patient_name", ""),
            "insurance_type": form_data.get("box_1_insurance_type_name", ""),
            "total_diagnoses": form_data.get("num_diagnoses", 0),
            "total_services": form_data.get("num_service_lines", 0),
            "total_amount": form_data.get("box_28_total_charge", "")
        }
    }
    
    return core_fields

def generate_multiple_forms(n):
    """Generate N CMS-1500 forms with random addresses."""
    
    if not os.path.exists("form-cms1500.pdf"):
        print("Error: form-cms1500.pdf not found in current directory!")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = "output_forms"
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
            # Convert PDF to PNG
            png_filename = os.path.join(output_dir, f"cms1500_form_{i:04d}.png")
            png_success = convert_pdf_to_png(output_filename, png_filename)
            
            # Create individual JSON file for this form (complete data)
            individual_json_filename = os.path.join(output_dir, f"cms1500_form_{i:04d}.json")
            individual_form_data = {
                "form_number": i,
                "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                "png_filename": f"cms1500_form_{i:04d}.png" if png_success else None,
                "generated_date": fake.iso8601(),
                "form_data": address_data
            }
            
            with open(individual_json_filename, "w") as json_file:
                json.dump(individual_form_data, json_file, indent=2)
            
            # Create core subset JSON file for this form (simplified data)
            core_json_filename = os.path.join(output_dir, f"cms1500_form_{i:04d}_core.json")
            core_form_data = {
                "form_number": i,
                "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                "png_filename": f"cms1500_form_{i:04d}.png" if png_success else None,
                "generated_date": fake.iso8601(),
                "core_data": create_core_subset_data(address_data)
            }
            
            with open(core_json_filename, "w") as json_file:
                json.dump(core_form_data, json_file, indent=2)
            
            # Add form metadata for combined file
            form_record = {
                "form_number": i,
                "pdf_filename": f"cms1500_form_{i:04d}.pdf",
                "png_filename": f"cms1500_form_{i:04d}.png" if png_success else None,
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
    print(f"Individual JSON files created for each form:")
    print(f"  - Full data: cms1500_form_XXXX.json (complete field data)")
    print(f"  - Core subset: cms1500_form_XXXX_core.json (essential fields only)")
    print(f"Combined form data saved to '{json_filename}' for validation.")

def convert_pdf_to_png(pdf_path, output_path):
    """Convert the first page of a PDF to PNG format."""
    try:
        # Convert first page of PDF to image
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        if images:
            # Save the first (and only) page as PNG
            images[0].save(output_path, 'PNG')
            return True
    except Exception as e:
        print(f"Error converting {pdf_path} to PNG: {e}")
        return False
    return False

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