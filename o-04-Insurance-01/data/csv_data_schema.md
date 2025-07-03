# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `agents.csv`  
**Header:**  
```csv  
id,name,agencyName,agentLicense  
```  
**Example Data:**  
```csv  
agent_0,Karen Gomez,Spencer-Garcia Agency,AG-6313  
```  
---  
  
## File: `claims.csv`  
**Header:**  
```csv  
id,claimNumber,claimDate,claimType,amountClaimed,amountSettled,status,policyID,policyHolderID,insurerID  
```  
**Example Data:**  
```csv  
claim_0,CL-40997,2023-08-12,Liability,7773.44,4198.12,Pending Review,policy_880,holder_337,insurer_2  
```  
---  
  
## File: `coverages.csv`  
**Header:**  
```csv  
id,coverageName,coverageLimit,deductible  
```  
**Example Data:**  
```csv  
coverage_0,Personal Injury Protection,20779.0,171.0  
```  
---  
  
## File: `insurers.csv`  
**Header:**  
```csv  
id,insurerName,headquartersLocation,industryRating  
```  
**Example Data:**  
```csv  
insurer_0,Schneider-Hicks Insurance,Port Ronaldton,4.6  
```  
---  
  
## File: `policies.csv`  
**Header:**  
```csv  
id,policyNumber,policyType,startDate,endDate,premiumAmount,status,policyHolderID,insurerID,underwriterID,coverageIDs,agentID  
```  
**Example Data:**  
```csv  
policy_0,PN-5216-0,Auto,2022-06-21,2023-11-23,278.33,Active,holder_194,insurer_5,underwriter_10,"['coverage_8', 'coverage_10']",agent_14  
```  
---  
  
## File: `policyholders.csv`  
**Header:**  
```csv  
id,name,dateOfBirth,address,phoneNumber  
```  
**Example Data:**  
```csv  
holder_0,Richard Gonzales,2001-10-09,"4805 Porter Lodge Apt. 121, Thomasberg, CT 16719",(585)238-6800  
```  
---  
  
## File: `underwriters.csv`  
**Header:**  
```csv  
id,name,licenseID,experienceYears  
```  
**Example Data:**  
```csv  
underwriter_0,Michael Wyatt,UW-2150,20  
```  
---  
  
