# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `claims.csv`
**Header:**
```csv
id,claimNumber,claimDate,totalBilled,totalPaid,status,payerID,encounterID
```
---

## File: `claim_line_items.csv`
**Header:**
```csv
id,claimID,lineCode,billedAmount,allowedAmount
```
---

## File: `diagnoses.csv`
**Header:**
```csv
id,encounterID,diagnosisCode,codeSystem,diagnosisDesc
```
---

## File: `encounters.csv`
**Header:**
```csv
id,encounterID,startDateTime,endDateTime,reasonForVisit,encounterType,patientID,providerID,facilityID
```
---

## File: `facilities.csv`
**Header:**
```csv
id,facilityName,facilityType,location
```
---

## File: `lab_results.csv`
**Header:**
```csv
id,labTestID,resultValue,units,referenceRange,resultDateTime
```
---

## File: `lab_tests.csv`
**Header:**
```csv
id,encounterID,testID,testName,testCode,specimenType,testDateTime
```
---

## File: `medications.csv`
**Header:**
```csv
id,brandName,genericName,rxNormCode,strength
```
---

## File: `medication_orders.csv`
**Header:**
```csv
id,encounterID,orderID,startDate,endDate,dosage,frequency,medicationID
```
---

## File: `patients.csv`
**Header:**
```csv
id,firstName,lastName,birthDate,gender,address,phoneNumber
```
---

## File: `patient_coverage.csv`
**Header:**
```csv
id,patientID,payerID,coverageStart,coverageEnd
```
---

## File: `payers.csv`
**Header:**
```csv
id,payerName,payerType,contactInfo
```
---

## File: `procedures.csv`
**Header:**
```csv
id,encounterID,procedureCode,codeSystem,procedureDesc,procedureDate
```
---

## File: `providers.csv`
**Header:**
```csv
id,providerName,licenseNumber,specialty
```
---

