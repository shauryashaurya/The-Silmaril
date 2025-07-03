# CSV Data Schema  
  
This file summarizes the headers and a sample data row of all CSV files found in the `data` folder.  
  
---  
  
## File: `brokers.csv`  
**Header:**  
```csv  
id,brokerName,brokerLicenseID,commissionPlanID  
```  
**Example Data:**  
```csv  
broker_0,"Austin, Smith and Walton Brokerage",BR-1818,plan_4  
```  
---  
  
## File: `cash_accounts.csv`  
**Header:**  
```csv  
id,accountID,balance,belongsToInvestorID  
```  
**Example Data:**  
```csv  
cash_0,CASH-0,77420.25,inv_23  
```  
---  
  
## File: `commission_plans.csv`  
**Header:**  
```csv  
id,planName,commissionRate  
```  
**Example Data:**  
```csv  
plan_0,engineer cross-media experiences,0.0186  
```  
---  
  
## File: `exchanges.csv`  
**Header:**  
```csv  
id,exchangeName,country  
```  
**Example Data:**  
```csv  
exch_0,"Baker, Rodriguez and Reyes Exchange",Germany  
```  
---  
  
## File: `instruments.csv`  
**Header:**  
```csv  
id,symbol,description,tickSize,instrumentType  
```  
**Example Data:**  
```csv  
instr_0,VHE37,Integrated fresh-thinking hierarchy,0.01,Equity  
```  
---  
  
## File: `investors.csv`  
**Header:**  
```csv  
id,investorName,investorType  
```  
**Example Data:**  
```csv  
inv_0,Christopher Sanchez,Retail  
```  
---  
  
## File: `orders.csv`  
**Header:**  
```csv  
id,orderID,orderType,side,quantity,limitPrice,timeInForce,status,creationDateTime,investorID,brokerID,exchangeID,instrumentID  
```  
**Example Data:**  
```csv  
ord_0,ORD-619957,Limit,Buy,721,87.16,GTC,PartiallyFilled,2024-04-06T01:25:56,inv_12,,exch_3,instr_64  
```  
---  
  
## File: `portfolios.csv`  
**Header:**  
```csv  
id,portfolioID,portfolioName,investorID  
```  
**Example Data:**  
```csv  
port_0,PORT-0,Kaitlin Duke's Portfolio,inv_11  
```  
---  
  
## File: `positions.csv`  
**Header:**  
```csv  
id,portfolioID,instrumentID,averageCost,currentQuantity  
```  
**Example Data:**  
```csv  
pos_0,port_27,instr_7,167.82,477  
```  
---  
  
