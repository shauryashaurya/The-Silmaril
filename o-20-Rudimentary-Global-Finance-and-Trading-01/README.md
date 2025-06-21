# Ontology #20 Global Finance & Trading Domain                                
                   
## Domain           
           
Models a finance system with StockExchanges, ListedCompanies, Stocks, Traders, Transactions, Indices, Derivatives, MarketAlerts, etc.           
           
## Sample Competency Questions           
* “Which stocks belong to which index, and which transactions are in which trading account?”           
* “Which derivative references which underlying stock, and does it belong to a certain regulatory authority?”           
* “Which fund invests in which stocks, and which simulation references a specific derivative?”           
* “Which derivatives are close to expiration, referencing which underlying stock that belongs to which index?”  
* “Which traders hold multiple accounts across different brokerages with conflicting compliance policies?”  
* “Which market alerts referencing which risk model triggered the greatest shift in fund NAV?”  
* “Which portfolio invests in derivatives and is impacted by a negative scenario simulation?”  
* “Which listing companies are recognizedBy a certain regulatory authority but are also supervised by a second authority?”  
* “Which financesim scenario includes which stock exchanges, producing changes in sharePrice > X percent?”  
* “Which fund invests in conflicting underlying assets that violate some compliance policy?”

**Palantir Foundry Context**:
- Each entity (StockExchange, ListedCompany, Trader, Fund, Portfolio) is an object type in Foundry.  
- Code-workbooks or transforms unify transactions, derivative data, risk models, compliance policy references.  
- Real-time or daily updates can recalc share prices or fund NAV.  
- Branch merges handle new or changed properties (like adding “shortSellingAllowed = true” to certain accounts).                    
				           
           
---                      
                      
## **Scenario-based competency questions** for Ontology #20: Global Finance & Trading Domain                      
                      
1. **Derivative Chain Reaction**                        
   - “If a main `Stock` price collapses, which **Derivative** referencing it triggers margin calls for certain `TradingAccount` or `Portfolio`?”                      
                      
2. **Short Selling Ban**                        
   - “If `RegulatoryAuthority` imposes a short selling ban, do we forcibly freeze certain `Transaction` referencing `quantity < 0` or advanced trades?”                      
                      
3. **Fund Merge**                        
   - “What if two `Fund` objects unify—do we unify all `RiskModel` references or partial references for each fund’s `Portfolio` assets?”                      
                      
4. **Index Rebalancing**                        
   - “If a major `MarketIndex` changes membership to remove a certain `Stock`, do we see forced selling in multiple `Portfolio.investsIn` references?”                      
                      
5. **Trader License Revoked**                        
   - “Which `Trader` with license revoked can no longer hold `TradingAccount`? Do we forcibly reassign the account or freeze it?”                      
                      
6. **CompliancePolicy Overhaul**                        
   - “If a new `CompliancePolicy` raises strict rules, do we see multiple `Brokerage` objects failing references or do we run a partial scenario to enforce compliance?”                      
                      
7. **Simulation Crash**                        
   - “Which `FinanceSimulation` scenario includes certain `StockExchange` or `Derivative` that, if set to 0 price, triggers mass `MarketAlert` with severity=High?”                      
                      
8. **Cross-Exchange Delisting**                        
   - “If a certain `ListedCompany` is delisted from one `StockExchange` but not supervisedBy another, do we forcibly unify or treat them as partial listings with minimal liquidity?”                      
                      
9. **Cyber Attack**                        
   - “Which `ExchangeEvent` sets triggers_Alert to produce a new risk model reference if we simulate a large scale hacking scenario?”                      
                      
---                  
---                           
                           
## Ontology Structure: Core Classes / Entities (Domain Ontology)                           
                           
Below is a conceptual structure, with a **pseudocode** approach.                    
                   
                           
                           
                                                                         
```mermaid                                                                         
                  
                    
```                                                            
                                                                       
---                                             
                                           

```plaintext
Class: GlobalFinanceSystem
  - systemID: string
  - regionCoverage: string
  - foundationYear: int              
  - mainCurrency: string             

Class: StockExchange
  - exchangeID: string
  - exchangeName: string
  - country: string
  - exchangeVolume: float            

Class: ListedCompany
  - companyID: string
  - companyName: string
  - sector: string

Class: Stock
  - stockID: string
  - tickerSymbol: string
  - sharePrice: float

Class: Trader
  - traderID: string
  - traderName: string
  - licenseID: string
  - yearsActive: int                 

Class: Brokerage
  - brokerageID: string
  - brokerageName: string

Class: TradingAccount
  - accountID: string
  - balance: float

Class: Transaction
  - transactionID: string
  - transactionDate: dateTime
  - transactionType: string
  - quantity: int

Class: MarketIndex
  - indexID: string
  - indexName: string
  - currentValue: float

Class: Derivative
  - derivativeID: string
  - derivativeType: string
  - underlyingAsset: string
  - expirationDate: dateTime         

Class: RegulatoryAuthority
  - authorityID: string
  - authorityName: string

Class: MarketAlert
  - alertID: string
  - alertDescription: string
  - severity: string

Class: RiskModel
  - modelID: string
  - modelName: string

Class: Fund
  - fundID: string
  - fundName: string
  - fundType: string
  - fundNAV: float                   

Class: Portfolio
  - portfolioID: string
  - portfolioValue: float

Class: ExchangeEvent
  - eventID: string
  - eventType: string
  - eventTime: dateTime

Class: CompliancePolicy
  - policyID: string
  - policyScope: string

Class: FinanceSimulation
  - simID: string
  - scenarioDesc: string

// relationships:
// 1) includesExchange (GlobalFinanceSystem → StockExchange, 1..*)
// 2) listsCompany (StockExchange → ListedCompany, 0..*)
// 3) hasStock (ListedCompany → Stock, 1..*)
// 4) tradesAt (Trader → StockExchange, 0..*)
// 5) usesBrokerage (Trader → Brokerage, 0..1)
// 6) holdsAccount (Trader → TradingAccount, 1..*)
// 7) recordsTransaction (TradingAccount → Transaction, 0..*)
// 8) belongsToIndex (Stock -> MarketIndex, 0..*)
// 9) referencesUnderlying (Derivative -> Stock, 0..1)
// 10) supervisedBy (StockExchange -> RegulatoryAuthority, 0..1)
// 11) triggersAlert (ExchangeEvent -> MarketAlert, 0..*)
// 12) appliesModel (RiskModel -> Fund, 0..*)
// 13) investsIn (Portfolio -> Stock, 0..*)
// 14) subjectToPolicy (Brokerage -> CompliancePolicy, 0..*)
// 15) runsSimulation (FinanceSimulation -> StockExchange, 0..*)
// 16) impactedBy (FinanceSimulation -> Derivative, 0..*)
// 17) referencingFund (FinanceSimulation -> Fund, 0..1)

Relationship: recognizedBy (Stock → RegulatoryAuthority, 0..*)
  // e.g., a particular regulatory body recognized a certain stock listing

Relationship: investsDerivative (Portfolio → Derivative, 0..*)  
  // portfolio invests in derivative instruments as well

Relationship: referencesRisk (MarketAlert → RiskModel, 0..1)  
  // an alert might reference a risk model that triggered it

Relationship: calculatesNAV (Fund → MarketIndex, 0..*)
  // a fund might reference an index as a benchmark for NAV calculations

Relationship: influencesAccount (CompliancePolicy → TradingAccount, 0..*)
  // certain compliance policies can impose restrictions or checks on trading accounts
```
                          
