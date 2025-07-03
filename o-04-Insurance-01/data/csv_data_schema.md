# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `agents.csv`
**Header:**
```csv
id,name,agencyName,agentLicense
```
---

## File: `claims.csv`
**Header:**
```csv
id,claimNumber,claimDate,claimType,amountClaimed,amountSettled,status,policyID,policyHolderID,insurerID
```
---

## File: `coverages.csv`
**Header:**
```csv
id,coverageName,coverageLimit,deductible
```
---

## File: `insurers.csv`
**Header:**
```csv
id,insurerName,headquartersLocation,industryRating
```
---

## File: `policies.csv`
**Header:**
```csv
id,policyNumber,policyType,startDate,endDate,premiumAmount,status,policyHolderID,insurerID,underwriterID,coverageIDs,agentID
```
---

## File: `policyholders.csv`
**Header:**
```csv
id,name,dateOfBirth,address,phoneNumber
```
---

## File: `underwriters.csv`
**Header:**
```csv
id,name,licenseID,experienceYears
```
---

