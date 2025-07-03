# CSV Data Schema

This file summarizes the headers of all CSV files found in the `data` folder.

---

## File: `brokers.csv`
**Header:**
```csv
id,brokerName,brokerLicenseID,commissionPlanID
```
---

## File: `cash_accounts.csv`
**Header:**
```csv
id,accountID,balance,belongsToInvestorID
```
---

## File: `commission_plans.csv`
**Header:**
```csv
id,planName,commissionRate
```
---

## File: `exchanges.csv`
**Header:**
```csv
id,exchangeName,country
```
---

## File: `instruments.csv`
**Header:**
```csv
id,symbol,description,tickSize,instrumentType
```
---

## File: `investors.csv`
**Header:**
```csv
id,investorName,investorType
```
---

## File: `orders.csv`
**Header:**
```csv
id,orderID,orderType,side,quantity,limitPrice,timeInForce,status,creationDateTime,investorID,brokerID,exchangeID,instrumentID
```
---

## File: `portfolios.csv`
**Header:**
```csv
id,portfolioID,portfolioName,investorID
```
---

## File: `positions.csv`
**Header:**
```csv
id,portfolioID,instrumentID,averageCost,currentQuantity
```
---

