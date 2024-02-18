
#https://launch.smarthealthit.org/
# Example FHIR server base URL and patient ID


import requests
import json
from datetime import datetime
from epic_fhir_fn import *


# Example FHIR server base URL and patient ID
fhir_base_url = 'https://launch.smarthealthit.org/v/r4/fhir'  # This URL FHIR server URL
patient_id = 'Patient/cd09f5d4-55f7-4a24-a25d-a5b65c7a8805'  # Replace this with the actual patient ID

file_path = 'fhir_collected_data.json'

# Additional headers, such as authentication tokens, might be required depending on the server setup
headers = {
    'Accept': 'application/fhir+json',
    #'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6InBhdGllbnQvKi4qIHVzZXIvKi4qIGxhdW5jaC9wYXRpZW50IGxhdW5jaC9lbmNvdW50ZXIgb3BlbmlkIGZoaXJVc2VyIHByb2ZpbGUgb2ZmbGluZV9hY2Nlc3Mgb25saW5lX2FjY2VzcyBzbWFydC9vcmNoZXN0cmF0ZV9sYXVuY2ggIiwiY29kZV9jaGFsbGVuZ2VfbWV0aG9kIjoiUzI1NiIsImNvZGVfY2hhbGxlbmdlIjoiTF81Y3QzNkVqTzd2c19ncUI3NmxrTEcteDMyUFhONFBSMGY5SndMLVI4dyIsImNvbnRleHQiOnsibmVlZF9wYXRpZW50X2Jhbm5lciI6dHJ1ZSwic21hcnRfc3R5bGVfdXJsIjoiaHR0cHM6Ly9sYXVuY2guc21hcnRoZWFsdGhpdC5vcmcvc21hcnQtc3R5bGUuanNvbiIsInBhdGllbnQiOiJiOWM3ODYwOS1iY2EzLTQwMDQtYTVlZC0yNDZlNWYzZmYyMjkiLCJlbmNvdW50ZXIiOiI1OWIzN2FiMS1iODZhLTQyMjgtODZkYi1kY2Y1OTUxYTIzY2QifSwiY2xpZW50X2lkIjoid2hhdGV2ZXIiLCJmaGlyVXNlciI6IlBhdGllbnQvYjljNzg2MDktYmNhMy00MDA0LWE1ZWQtMjQ2ZTVmM2ZmMjI5IiwiaWF0IjoxNzA3ODE4ODczLCJleHAiOjE3MDc4MjI0NzN9.1LuSzrQxHtr78IHPOWhFI43egbt0-qfdOU1NQTPLv00',  # Uncomment and replace if auth is needed
}

           
# Fetch patient details
patient_request_url = f'{fhir_base_url}/{patient_id}'

# Get patient details
patient_response = requests.get(patient_request_url, headers=headers)
if patient_response.status_code == 200:
    patient_data = patient_response.json()
    #print_dict_simple(patient_data)
    
    print("\nPatient Details from FHIR API directly:")

    if 'name' in patient_data and len(patient_data['name']) > 0:
        name = patient_data['name'][0]  # Assuming you want the first (or "official") name
        given_name = " ".join(name.get('given', [""]))
        family_name = name.get('family', "")
        prefix = " ".join(name.get('prefix', [""]))
        full_name = f"{prefix} {given_name} {family_name}".strip()
    else:
        full_name = ""
    print(f"Name: {full_name}")

    # Gender
    gender = patient_data.get('gender', "")
    print(f"Gender: {gender}")
    
    #tel
    telecom = patient_data.get('telecom', [])
    phone_number = ""
    for contact in telecom:
        if contact.get('system') == 'phone' and contact.get('use') == 'home':
            phone_number = contact.get('value', '')
            break  # Assumes you only need the first home phone number
    print(f"Phone: {phone_number}")

    # BirthDate
    birthDate = patient_data.get('birthDate', "")
    print(f"BirthDate: {birthDate}")

    # Marital Status
    marital_status = patient_data.get('maritalStatus', {}).get('text', "")
    print(f"Marital Status: {marital_status}")

    # Language
    language = patient_data.get('communication', [{}])[0].get('language', {}).get('text', "")
    print(f"Language: {language}")

    # Identifier - Handling multiple identifiers
    identifiers = patient_data.get('identifier', [])
    identifier_str = ", ".join([f"{identifier.get('type', {}).get('text', '')}:{identifier.get('value', '')}" for identifier in identifiers])
    #print(f"Identifiers: {identifier_str if identifier_str else ''}")

    # For simplicity, showing the handling for one type of identifier. Extend similarly for others as needed.
    medical_record_number = ""
    social_security_number = ""
    drivers_license = ""
    passport_number = ""
    for identifier in identifiers:
        if identifier.get('type', {}).get('text', '') == 'Medical Record Number':
            medical_record_number = identifier.get('value', '')
        elif identifier.get('type', {}).get('text', '') == 'Social Security Number':
            social_security_number = identifier.get('value', '')
        elif identifier.get('type', {}).get('text', '') == "Driver's License":
            drivers_license = identifier.get('value', '')
        elif identifier.get('type', {}).get('text', '') == 'Passport Number':
            passport_number = identifier.get('value', '')

    print(f"Medical Record Number: {medical_record_number}")
    print(f"Social Security Number: {social_security_number}")
    print(f"Driver's License: {drivers_license}")
    print(f"Passport Number: {passport_number}")

  
    address = patient_data['address'][0]
    address_parts = []
    if 'extension' in address:
        for ext in address['extension']:
            if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/geolocation':
                for geo in ext.get('extension', []):
                    if geo.get('url') == 'latitude':
                        latitude = geo.get('valueDecimal', '')
                    elif geo.get('url') == 'longitude':
                        longitude = geo.get('valueDecimal', '')
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    
    if address.get('line'):
        address_parts.append(address['line'][0])
        address_parts.append(address['city'])
        address_parts.append(address['state'])
        address_parts.append(address['postalCode'])
        address_parts.append(address['country'])

        print(f"Address: {', '.join(address_parts)}")
    else:
        print(f"Failed to retrieve patient details. Status code:{patient_response.status_code}")


    
    
    
# List of FHIR resource types you're interested in
resource_types_of_interest = [ "Procedure", "Observation", "Encounter", "Immunization", "MedicationRequest", "Procedure", "CarePlan", "DiagnosticReport", "Condition"
    # resources with good hit rate: "Observation", "Encounter", "Immunization", "MedicationRequest", "Procedure", "CarePlan", "DiagnosticReport", "Condition",
    #not useful: "Invoice", "CatalogEntry", "EventDefinition", "DocumentManifest", "MessageDefinition", "Goal", "MedicinalProductPackaged", "Endpoint", "EnrollmentRequest", "Consent", "CapabilityStatement", "Measure", "Medication", "ResearchSubject", "Subscription", "DocumentReference", "GraphDefinition", "Parameters", "CoverageEligibilityResponse", "MeasureReport", "PractitionerRole", "SubstanceReferenceInformation", "RelatedPerson", "ServiceRequest", "SupplyRequest", "Practitioner", "PractitionerRole", "VerificationResult", "SubstanceProtein", "BodyStructure", "Slot", "Contract", "Person", "RiskAssessment", "EpisodeOfCare", "OperationOutcome",  "List", "ConceptMap", "OperationDefinition", "ValueSet", "Account", "Group", "PaymentNotice", "ResearchDefinition", "MedicinalProductManufactured", "Organization", "CareTeam", "ImplementationGuide", "ImagingStudy", "FamilyMemberHistory", "ChargeItem", "ResearchElementDefinition", "ObservationDefinition", "Substance", "SubstanceSpecification", "SearchParameter", "ActivityDefinition", "Communication", "InsurancePlan", "Linkage", "SubstanceSourceMaterial", "ImmunizationEvaluation", "DeviceUseStatement", "RequestGroup", "DeviceRequest", "MessageHeader", "ImmunizationRecommendation", "Provenance", "Task", "Questionnaire", "ExplanationOfBenefit", "MedicinalProductPharmaceutical", "ResearchStudy", "Specimen", "AllergyIntolerance",  "StructureDefinition", "ChargeItemDefinition", "EpisodeOfCare", "OperationOutcome", "List", "ConceptMap", "OperationDefinition", "ValueSet", "EffectEvidenceSynthesis", "BiologicallyDerivedProduct", "Device", "VisionPrescription", "Media", "MedicinalProductContraindication", "EvidenceVariable", "MolecularSequence", "MedicinalProduct", "DeviceMetric", "CodeSystem", "Flag", "SubstanceNucleicAcid", "RiskEvidenceSynthesis", "AppointmentResponse", "StructureMap", "AdverseEvent", "GuidanceResponse", "MedicationAdministration", "EnrollmentResponse", "Binary", "Library", "MedicinalProductInteraction", "MedicationStatement", "CommunicationRequest", "TestScript", "Basic", "SubstancePolymer", "TestReport", "ClaimResponse", "MedicationDispense", "OrganizationAffiliation", "HealthcareService", "MedicinalProductIndication", "NutritionOrder", "TerminologyCapabilities", "Evidence", "AuditEvent",  "PaymentReconciliation",  "SpecimenDefinition", "Composition", "DetectedIssue", "Bundle", "CompartmentDefinition", "MedicationKnowledge", "MedicinalProductIngredient", "Patient", "Coverage", "QuestionnaireResponse", "CoverageEligibilityRequest", "NamingSystem", "MedicinalProductUndesirableEffect", "ExampleScenario", "Schedule", "SupplyDelivery", "ClinicalImpression", "DeviceDefinition", "PlanDefinition", "MedicinalProductAuthorization", "Claim", "Location"
]


# Iterate through the selected resource types and fetch their data
collected_data = {}
fetch_patient_demographics(fhir_base_url, patient_id, headers, collected_data)
for resource_type in resource_types_of_interest:
    fetch_and_store_resource_data(resource_type, fhir_base_url, patient_id, headers, collected_data)

# Save the collected data to a JSON file 
with open(file_path, 'w') as file:
    json.dump(collected_data, file, indent=4)
     # Adjust this to the correct path
print(f"FHIR data saved to {file_path}")

#patient demographics
print("\nDemographics from stored records: \n")
patient_info(file_path)

#print medication 
print("\nMedication:\n")
print_medication_information(file_path)  

#print past medical history 
print("\nPast Medical history:\n")
summarize_conditions(file_path) 

#print communication history 
print("\nCommunication history:\n")
communication_data(file_path)

#print Encounter history 
print("\nEncounter history:\n")
encounter_processor = EncounterProcessor(file_path)
encounter_processor.load_data()
encounter_processor.process_encounters()

 
