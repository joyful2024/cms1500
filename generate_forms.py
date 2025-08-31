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
        
        # Units (1-5)  
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
    
    # Referring physician (Box 17)
    if fake.random_int(1, 100) <= 40:  # 40% chance of referral
        ref_physician = f"Dr. {fake.first_name()} {fake.last_name()}, MD"
        ref_physician_npi = fake.bothify(text="##########")
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
    
    # PHASE 3: Extended diagnosis support (1-12 diagnoses for complex cases)
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
    
    # Weighted random selection
    random_val = fake.random_int(1, 10000) / 100  # 0.01 to 100.00
    cumulative = 0
    num_diagnoses = 1  # default
    for count, probability in diagnosis_probabilities:
        cumulative += probability
        if random_val <= cumulative:
            num_diagnoses = count
            break
    
    selected_diagnoses = fake.random_elements(common_icd10_codes, length=num_diagnoses, unique=True)
    
    # Create extended diagnosis code data (supporting up to 12 diagnoses)
    diagnosis_data = {}
    for i in range(1, 13):  # diagnosis1 through diagnosis12
        if i <= num_diagnoses:
            code, description = selected_diagnoses[i-1]
            diagnosis_data[f"diagnosis{i}"] = code
            diagnosis_data[f"diagnosis{i}_description"] = description
        else:
            diagnosis_data[f"diagnosis{i}"] = ""
            diagnosis_data[f"diagnosis{i}_description"] = ""
    
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
        
        # Treatment timeline
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
        
        # Hospitalization dates
        "hosp_mm_from": hosp_mm_from,
        "hosp_dd_from": hosp_dd_from,
        "hosp_yy_from": hosp_yy_from,
        "hosp_mm_end": hosp_mm_end,
        "hosp_dd_end": hosp_dd_end,
        "hosp_yy_end": hosp_yy_end,
        
        # Accident details
        "accident_place": accident_place,
        
        # Secondary insurance
        "other_ins_name": other_ins_name,
        "other_ins_policy": other_ins_policy,
        "other_ins_plan_name": other_ins_plan_name,
        
        # Authorization and reference
        "prior_auth": prior_auth,
        "original_ref": original_ref,
        "medicaid_resub": medicaid_resub,
        
        # Referring physician
        "ref_physician": ref_physician,
        "physician number 17a": ref_physician_npi,
        "physician number 17a1": ref_physician_qualifier,
        
        # Signatures
        "pt_signature": pt_signature,
        "pt_date": pt_signature_date,
        "physician_signature": physician_signature,
        "physician_date": physician_signature_date,
        
        # Service facility
        "fac_name": fac_name,
        "fac_street": fac_street,
        "fac_location": fac_location,
        
        # PHASE 2: Insurance & Provider Details
        "ins_street": ins_street,
        "ins_city": ins_city,
        "ins_state": ins_state,
        "ins_zip": ins_zip,
        "ins_phone": ins_phone,
        "ins_phone area": ins_phone_area,
        "insurance_id": insurance_id,
        "insurance_address2": insurance_address2,
        "insurance_city_state_zip": insurance_city_state_zip,
        "pin": pin,
        "pin1": pin1,
        "grp": grp,
        "grp1": grp1,
        "doc_location": doc_location,
        "NUCC USE": nucc_use,
        
        # PHASE 3: Enhanced Clinical Fields
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