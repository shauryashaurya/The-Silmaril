# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `claims.csv`  
**Header:**  
```csv  
id,claimNumber,claimDate,totalBilled,totalPaid,status,payerID,encounterID  
```  
**Example Data:**  
```csv  
claim_0,CL-53327,2023-07-26,9593.69,0.0,Submitted,payer_0,enc_32  
```  
---  
  
## File: `claim_line_items.csv`  
**Header:**  
```csv  
id,claimID,lineCode,billedAmount,allowedAmount  
```  
**Example Data:**  
```csv  
cli_0,claim_6,J0885,672.19,338.0  
```  
---  
  
## File: `diagnoses.csv`  
**Header:**  
```csv  
id,encounterID,diagnosisCode,codeSystem,diagnosisDesc  
```  
**Example Data:**  
```csv  
diag_0,enc_13,Z33.1,ICD-10,Race nor police mind.  
```  
---  
  
## File: `encounters.csv`  
**Header:**  
```csv  
id,encounterID,startDateTime,endDateTime,reasonForVisit,encounterType,patientID,providerID,facilityID  
```  
**Example Data:**  
```csv  
enc_0,ENC-99397,2023-03-25T09:42:55,2023-03-25T09:42:55,Protect support debate perhaps word listen.,Outpatient,pat_46,prov_14,fac_0  
```  
---  
  
## File: `facilities.csv`  
**Header:**  
```csv  
id,facilityName,facilityType,location  
```  
**Example Data:**  
```csv  
fac_0,Williams-Phillips Hospital,Hospital,Sarahmouth  
```  
---  
  
## File: `lab_results.csv`  
**Header:**  
```csv  
id,labTestID,resultValue,units,referenceRange,resultDateTime  
```  
**Example Data:**  
```csv  
lr_0,lt_73,13.06,mg/dL,Normal range depends,2023-07-24T04:35:57  
```  
---  
  
## File: `lab_tests.csv`  
**Header:**  
```csv  
id,encounterID,testID,testName,testCode,specimenType,testDateTime  
```  
**Example Data:**  
```csv  
lt_0,enc_97,LT-6058,LabTest leader,4548-4,Blood,2024-03-27T03:51:36  
```  
---  
  
## File: `medications.csv`  
**Header:**  
```csv  
id,brandName,genericName,rxNormCode,strength  
```  
**Example Data:**  
```csv  
med_0,Draw,against,860975,399mg  
```  
---  
  
## File: `medication_orders.csv`  
**Header:**  
```csv  
id,encounterID,orderID,startDate,endDate,dosage,frequency,medicationID  
```  
**Example Data:**  
```csv  
mo_0,enc_9,MO-8361,2023-05-11,2023-05-30,3 tablets,BID,med_45  
```  
---  
  
## File: `patients.csv`  
**Header:**  
```csv  
id,firstName,lastName,birthDate,gender,address,phoneNumber  
```  
**Example Data:**  
```csv  
pat_0,Andrew,Moore,2008-06-09,Male,"6857 Koch Overpass, West Amandamouth, PR 78131",001-919-317-8156x237  
```  
---  
  
## File: `patient_coverage.csv`  
**Header:**  
```csv  
id,patientID,payerID,coverageStart,coverageEnd  
```  
**Example Data:**  
```csv  
cov_0,pat_26,payer_3,2022-04-21,2025-02-19  
```  
---  
  
## File: `payers.csv`  
**Header:**  
```csv  
id,payerName,payerType,contactInfo  
```  
**Example Data:**  
```csv  
payer_0,Hall and Sons Insurance,Medicaid,918-521-7309x501  
```  
---  
  
## File: `procedures.csv`  
**Header:**  
```csv  
id,encounterID,procedureCode,codeSystem,procedureDesc,procedureDate  
```  
**Example Data:**  
```csv  
proc_0,enc_84,G0101,HCPCS,envisioneer world-class e-business,2024-01-15T01:21:14  
```  
---  
  
## File: `providers.csv`  
**Header:**  
```csv  
id,providerName,licenseNumber,specialty  
```  
**Example Data:**  
```csv  
prov_0,Patrick Ryan,LIC-1561,General  
```  
---  
  
