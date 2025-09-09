# CMS-1500 Form Field Analysis for ML Training

## Currently Filled Fields (26/239)
✅ **Patient Demographics (Box 2, 3, 5)**
- pt_street, pt_city, pt_state, pt_zip, pt_AreaCode, pt_phone
- birth_mm, birth_dd, birth_yy

✅ **Insurance Type (Box 1)**
- Insurance checkboxes handled via button fields

✅ **Insurance Holder Demographics (Box 11)**  
- ins_dob_mm, ins_dob_dd, ins_dob_yy

✅ **Diagnosis Codes (Box 21)**
- diagnosis1-4, diag1-4 (diagnosis pointers)

✅ **Service Lines (Box 24)**
- cpt1-5, mod2 (partial modifiers)

## Critical Missing Fields for ML Training

### **HIGH PRIORITY - Core Billing Data**

1. **Patient Information**
   - `pt_name` - Patient full name (Box 2)
   - `pt_account` - Patient account number
   - `pt_signature` - Patient signature field
   - `pt_date` - Patient signature date

2. **Insurance Information (Box 11)**
   - `ins_name` - Insured person name
   - `ins_policy` - Policy/ID number  
   - `ins_plan_name` - Insurance plan name
   - `insurance_name` - Primary insurance company name
   - `insurance_address` - Insurance company address
   - `insurance_city_state_zip` - Insurance company location
   - `insurance_id` - Insurance company ID

3. **Provider Information (Box 17, 33)**
   - `ref_physician` - Referring physician name
   - `doc_name` - Rendering provider name
   - `doc_street` - Provider address
   - `doc_location` - Provider location
   - `doc_phone`, `doc_phone area` - Provider phone
   - `id_physician` - Provider NPI
   - `physician_signature` - Provider signature
   - `physician_date` - Provider signature date

4. **Service Line Details (Box 24)**
   - Service dates: `sv1_mm_from`, `sv1_dd_from`, `sv1_yy_from` (etc. for lines 1-6)
   - Service dates to: `sv1_mm_end`, `sv1_dd_end`, `sv1_yy_end` 
   - Place of service: `place1-6`
   - Emergency indicator: `emg1-6`
   - Charges: `ch1-6` (individual line charges)
   - Units: Currently missing
   - Modifier fields: `mod1`, `mod3-6` and sub-modifiers `mod1a-1c`, etc.

5. **Financial Data**
   - `t_charge` - Total charges
   - `amt_paid` - Amount paid
   - `charge` - Balance due

6. **Tax ID & Billing**
   - `tax_id` - Provider tax ID number
   - `grp` - Group practice number
   - `pin` - Provider PIN

### **MEDIUM PRIORITY - Enhanced Training Data**

7. **Condition/Treatment Timeline**
   - `cur_ill_mm/dd/yy` - Current illness onset date
   - `sim_ill_mm/dd/yy` - Similar illness date
   - `work_mm/dd/yy_from/end` - Unable to work dates
   - `hosp_mm/dd/yy_from/end` - Hospitalization dates

8. **Secondary Insurance (Box 9)**
   - `other_ins_name` - Other insured name
   - `other_ins_policy` - Other insurance policy
   - `other_ins_plan_name` - Other insurance plan

9. **Accident/Injury Details**
   - `accident_place` - Place of accident (state)

10. **Authorization & References**
    - `prior_auth` - Prior authorization number
    - `original_ref` - Original reference number
    - `medicaid_resub` - Medicaid resubmission code

### **LOW PRIORITY - Specialized Fields**

11. **EPSDT/Family Planning**
    - `epsdt1-6` - EPSDT/Family planning indicators

12. **Local Use Fields**
    - `local1-6`, `local1a-6a` - Carrier-specific fields

13. **Facility Information (Box 32)**
    - `fac_name` - Service facility name
    - `fac_location` - Service facility location
    - `fac_street` - Service facility address

## Recommendations for ML Training Enhancement

### Phase 1: Core Fields (Immediate)
Add generation for patient names, insurance details, provider information, complete service line data, and financial amounts.

### Phase 2: Clinical Context (Next)  
Add illness dates, hospitalization periods, accident details, and secondary insurance.

### Phase 3: Advanced Features (Future)
Add authorization numbers, facility details, and specialized program indicators.

This would increase field coverage from 26/239 (11%) to approximately 120+ fields (50%+), providing much richer training data for EHR and claims processing ML models.