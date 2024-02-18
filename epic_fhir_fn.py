#functions to extract from FHIR
import requests
import json
from datetime import datetime

#printing a key: text format
def print_dict_simple(d, indent=0):
    for key, value in d.items():
        if isinstance(value, dict):  # If the value is another dictionary, print its key and recurse
            print(' ' * indent + f"{key}:")
            print_dict_simple(value, indent + 2)
        else:  # If the value is not a dictionary, print the key-value pair
            print(' ' * indent + f"{key}: {value}")
            
#going through several variables in dict

# Fetch patient demographics only once
def fetch_patient_demographics(fhir_base_url, patient_id, headers, collected_data):
    patient_request_url = f'{fhir_base_url}/{patient_id}'
    response = requests.get(patient_request_url, headers=headers)
    if response.status_code == 200:
        print("Patient demographics:\n")
        collected_data['Patient'] = response.json()
    else:
        print(f"Failed to retrieve patient demographics. Status code: {response.status_code}")


def fetch_and_store_resource_data(resource_type, fhir_base_url, patient_id, headers, collected_data):
    """
    Fetches data for a specified resource type and stores in database.
    """
    resource_request_url = f'{fhir_base_url}/{resource_type}?patient={patient_id}'
    response = requests.get(resource_request_url, headers=headers)
    

    if response.status_code == 200:
        print(f"Recent {resource_type}:\n")
        resource_data = response.json()
        print(resource_data)
        
        # If the resource type already exists in collected_data, append new entries
        if resource_type in collected_data:  
            for entry in resource_data.get('entry', []):
                collected_data[resource_type].append(entry.get('resource', {}))
                
        else:
        # Else, create a new key for the resource type
            collected_data[resource_type] = [entry.get('resource', {}) for entry in resource_data.get('entry', [])]
    else:
        print(f"Failed to retrieve {resource_type}. Status code: {response.status_code}")      
 
#print demographic function
def patient_info(file_path):
    """
    Opens a JSON file containing FHIR patient data, extracts, and prints patient information.
    """
    try:
        with open(file_path, 'r') as file:
            fhir_data = json.load(file)
        
        # Name
        if 'Patient' in fhir_data:
            patient_data = fhir_data['Patient']
           
        if 'name' in patient_data and len(patient_data['name']) > 0:
            name = patient_data['name'][0] 
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
        
        # Phone
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

        # Identifiers
        medical_record_number = ""
        social_security_number = ""
        drivers_license = ""
        passport_number = ""
        identifiers = patient_data.get('identifier', [])
        for identifier in identifiers:
            identifier_type = identifier.get('type', {}).get('text', '')
            identifier_value = identifier.get('value', '')
            if identifier_type == 'Medical Record Number':
                medical_record_number = identifier_value
            elif identifier_type == 'Social Security Number':
                social_security_number = identifier_value
            elif identifier_type == "Driver's License":
                drivers_license = identifier_value
            elif identifier_type == 'Passport Number':
                passport_number = identifier_value
        
        print(f"Medical Record Number: {medical_record_number}")
        print(f"Social Security Number: {social_security_number}")
        print(f"Driver's License: {drivers_license}")
        print(f"Passport Number: {passport_number}")

        # Address and Geolocation
        if 'address' in patient_data and len(patient_data['address']) > 0:
            address = patient_data['address'][0]
            latitude = longitude = None
            if 'extension' in address:
                for ext in address['extension']:
                    if ext.get('url') == 'http://hl7.org/fhir/StructureDefinition/geolocation':
                        for geo in ext.get('extension', []):
                            if geo.get('url') == 'latitude':
                                latitude = geo.get('valueDecimal', '')
                            elif geo.get('url') == 'longitude':
                                longitude = geo.get('valueDecimal', '')
                print(f"Latitude: {latitude}, Longitude: {longitude}")
            
            address_parts = [part for part in [
                address.get('line', [''])[0] if address.get('line') else "",
                address.get('city', ""),
                address.get('state', ""),
                address.get('postalCode', ""),
                address.get('country', "")
            ] if part]  # Filter out empty parts

            print(f"Address: {', '.join(address_parts)}")
    
    except Exception as e:
        print(f"An error occurred: {e}")


#function to print medications
def print_medication_information(file_path):
    """
    Opens a JSON file containing FHIR data, extracts medication information, 
    and prints each medication with its start date and status.
    """
    try:
        # Open and load the JSON data
        with open(file_path, 'r') as file:
            fhir_data = json.load(file)
        
        # Assuming 'MedicationRequest' is the key under which medication data is stored
        if 'MedicationRequest' in fhir_data:
            medication_data = fhir_data['MedicationRequest']
            for entry in medication_data:
                medication_request = entry  # Assuming each entry is the medication request itself
                
                # Extract and print relevant information
                medication_name = medication_request.get('medicationCodeableConcept', {}).get('text', 'Unknown')
                status = medication_request.get('status', 'No status available')
                # Assuming 'authoredOn' is the field for start date; adjust if your data uses a different field
                start_date = medication_request.get('authoredOn', 'No start date available')
                if start_date:
                    start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z").date()
                
                print(f"{medication_name} Currently Taking: {status} Began: {start_date}")
        else:
            print("MedicationRequest data not found in the provided JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")

#function to print conditions:


def summarize_conditions(file_path):
    """
    Opens a JSON file containing FHIR data, extracts conditions information, 
    and prints a summary for each condition with its onset date, recorded date,
    clinical status, resolve date, and verification status.

    """
    try:
        # Open and load the JSON data
        with open(file_path, 'r') as file:
            fhir_data = json.load(file)
        
        # Check if 'Condition' key exists and process data
        if 'Condition' in fhir_data:
            condition_data = fhir_data['Condition']

            print("Condition/Onset/Recorded/Clinical Status/Resolve Date/Verification")
            for condition in condition_data:
                # Extract condition details
                clinical_status = condition.get('clinicalStatus', {}).get('coding', [{}])[0].get('display', "Unknown")
                verification_status = condition.get('verificationStatus', {}).get('coding', [{}])[0].get('display', "Unknown")
                condition_code = condition.get('code', {}).get('coding', [{}])[0].get('display', "Unknown")
                onset_date = condition.get('onsetDateTime', "")
                abatement_date = condition.get('abatementDateTime', "")
                recorded_date = condition.get('recordedDate', "")
                
                # Format dates
                onset_date = datetime.strptime(onset_date, "%Y-%m-%dT%H:%M:%S%z").date() if onset_date else "Unknown"
                abatement_date = datetime.strptime(abatement_date, "%Y-%m-%dT%H:%M:%S%z").date() if abatement_date else "Unknown"
                recorded_date = datetime.strptime(recorded_date, "%Y-%m-%dT%H:%M:%S%z").date() if recorded_date else "Unknown"

                print(f"{condition_code}/ {onset_date}/ {recorded_date}/ {clinical_status}/ {abatement_date}/ {verification_status}")
        else:
            print("Condition data not found in the provided JSON file.")
    except Exception as e:
        print(f"An error occurred: {e}")

#print communications from FHIR data

def communication_data(file_path):
    """
    Opens a JSON file containing FHIR data, extracts communications.

    """
    try:
        # Open and load the JSON data
        with open(file_path, 'r') as file:
            fhir_data = json.load(file)
        
        # Check if 'Condition' key exists and process data
        if 'Communication' in fhir_data:
            communication_data = fhir_data['Communication']
            
            # If there are multiple communications, you may need to iterate through them
            for entry in communication_data.get('entry', []):
                # Extract the resource for each communication
                communication = entry.get('resource', {})

                # Now, you can print details for each communication
                status = communication.get('status', 'Unknown')
                print(f"Status: {status}")

                # Assuming sender is directly accessible and not a reference
                sender = communication.get('sender', {}).get('display', 'Unknown sender')
                print(f"Sender: {sender}")

                # Recipients can be multiple, so we iterate through them
                recipients = communication.get('recipient', [])
                recipient_names = ', '.join([recipient.get('display', 'Unknown recipient') for recipient in recipients])
                print(f"Recipients: {recipient_names}")

                # Print the sent date/time
                sent = communication.get('sent', 'Unknown date/time')
                print(f"Sent: {sent}")

                # Assuming there's at least one payload and it's a simple string content
                payload = communication.get('payload', [{}])[0]
                content = payload.get('contentString', 'No content')
                print(f"Content: {content}")

        else:
            print(f"Failed to retrieve communications as None.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        
#encounter processor:
class EncounterProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        

    def load_data(self):
        """Loads the JSON data from the specified file."""
        with open(self.file_path, 'r') as file:
            self.fhir_data = json.load(file)
        self.map_resources_to_encounters()
        
        
    def map_resources_to_encounters(self):
        """Maps Observations and Procedures to their respective encounters."""
        self.encounter_observations = {}
        self.encounter_procedures = {}
        self.encounter_diagnostics = {}
        
        # Map Observations
        if 'Observation' in self.fhir_data:
            for obs in self.fhir_data['Observation']:
                encounter_ref = obs.get('encounter', {}).get('reference', '')
                if encounter_ref:
                    if encounter_ref not in self.encounter_observations:
                        self.encounter_observations[encounter_ref] = []
                    self.encounter_observations[encounter_ref].append(obs)
        
        # Map Procedures
        if 'Procedure' in self.fhir_data:
            for proc in self.fhir_data['Procedure']:
                encounter_ref = proc.get('encounter', {}).get('reference', '')
                if encounter_ref:
                    if encounter_ref not in self.encounter_procedures:
                        self.encounter_procedures[encounter_ref] = []
                    self.encounter_procedures[encounter_ref].append(proc)

        if 'DiagnosticReport' in self.fhir_data:
            for report in self.fhir_data['DiagnosticReport']:
                encounter_ref = report.get('encounter', {}).get('reference', '')
                if encounter_ref not in self.encounter_diagnostics:
                    self.encounter_diagnostics[encounter_ref] = []
                self.encounter_diagnostics[encounter_ref].append(report)
        
       

    def process_encounters(self):
        """Processes and prints details for each Encounter entry."""
        if 'Encounter' not in self.fhir_data:
            print("Encounter data not found.")
            return
        
        for encounter in self.fhir_data['Encounter']:
            encounter_id = encounter.get('id', 'Unknown')
            print(f"Encounter ID: {encounter_id}")
            self.print_encounter_details(encounter)
            self.print_encounter_observations(encounter_id)
            self.print_encounter_procedures(encounter_id)
            self.print_encounter_diagnostics(encounter['id'])

    def print_encounter_details(self, encounter):
        """Prints the details of a single Encounter."""
        encounter_class = encounter.get('class', {}).get('code', 'Unknown')
        encounter_type = encounter.get('type', [{}])[0].get('text', 'Unknown')
        provider_reference = encounter.get('serviceProvider', {}).get('reference', 'Unknown provider')
        
        period_start = encounter.get('period', {}).get('start', 'Unknown start date')
        period_end = encounter.get('period', {}).get('end', 'Unknown end date')
        # Format dates for readability
        period_start = self.format_date(period_start)
        period_end = self.format_date(period_end)

        reason_code_display = encounter.get('type', [{}])[0].get('coding', [{}])[0].get('display', 'Unknown reason')

        print(f"Site: {encounter_class} {encounter_type} by provider {provider_reference}")
        print(f"Date: {period_start}, End: {period_end}")
        
    def print_encounter_observations(self, encounter_id):
        """Prints observations related to a single Encounter."""
        encounter_ref = f"Encounter/{encounter_id}"
        if encounter_ref in self.encounter_observations:
            print("Observations:")
            for obs in self.encounter_observations[encounter_ref]:
                obs_details = obs.get('code', {}).get('text', 'Unknown Observation')
                value_quantity = obs.get('valueQuantity', {})
                value = value_quantity.get('value', 'No value')
                unit = value_quantity.get('unit', 'No unit')
                print(f"  - {obs_details}: {value} {unit}")
        else:
            print("  No observations found for this encounter.")

    def print_encounter_procedures(self, encounter_id):
        """Prints procedures related to a single Encounter."""
        encounter_ref = f"Encounter/{encounter_id}"
        if encounter_ref in self.encounter_procedures:
            print("Procedures:")
            for proc in self.encounter_procedures[encounter_ref]:
                proc_details = proc.get('code', {}).get('text', 'Unknown Procedure')
                print(f"  - {proc_details}")
        else:
            print("  No procedures found for this encounter.")
            
    def print_encounter_diagnostics(self, encounter_id):
        """Prints diagnostics related to a single Encounter."""
        encounter_ref = f"Encounter/{encounter_id}"
        if encounter_ref in self.encounter_diagnostics:
            print("Diagnostics:")
            for report in self.encounter_diagnostics[encounter_ref]:
                for result_ref in report.get('result', []):
                    print(f"  - {result_ref.get('display', 'Unknown diagnostic')}")
                   
                    # Here you could add more detailed processing for each result
                    # For example, fetching detailed Observation data if available
        else:
            pass

    @staticmethod
    def format_date(date_str):
        """Formats the date string for readability if not 'Unknown start date' or 'Unknown end date'."""
        if date_str.startswith('Unknown'):
            return date_str
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")


