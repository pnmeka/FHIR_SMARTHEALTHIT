# FHIR_SMARTHEALTHIT
shows basic use of fhir api structure
Step1: Got to https://launch.smarthealthit.org
Choose patient portal launch. Choose R4 as FHIR version. Choose a random patient from drop down menu. Select. Then launch app. This will take you to mock patient login page. Click login and click approve to go to get the numbers.


step2: 
Open FHIR_API.py file above and paste the links from the above login page. 
a) URL under FHIR_Server. That will be your base server. It is usually of this format: https://launch.smarthealthit.org/v/r4/fhir
b) In patient_id: Go to the 4th tab called ID token and copy the FHIR_User of this format Patient/d00b766a-f5fa-4730-a64d-e8574994f460
c) paste this in the file FHIR_API: in patient ID.
d) save the file

step3: 

          pip install -r requirments.txt
          python3 FHIR_API.py

This should pull all data, store it in a json file and read the json file to populate with patient demographics, enounters, encounter specific observations etc and print them in terrminal.
