# Ontology #7: Stock Market / Equities Trading 
  
## Ontology Structure                                    
                                         
                                          
```mermaid                                          
classDiagram    
    class Investor {    
        %% Data Properties    
        investorName : string    
        investorType : string  %% e.g. "Retail", "Institutional"    
        %% Object Properties    
        places *--1 Order : one-to-many    
        portfolioBelongsTo 1--* Portfolio: one-to-many    
        cashAccountBelongsTo o--* CashAccount : many-to-one    
        %% Rules    
        %% RULE: An Investor may place Orders and hold Positions in a Portfolio.    
    }    
    
    class Broker {    
        %% Data Properties    
        brokerName : string    
        brokerLicenseID : string    
        %% Object Properties    
        feeStructure o--1 CommissionPlan : one-to-one    
        orderExecutedBy 1--* Order: one-to-many    
        %% Rules    
        %% RULE: If a Broker is associated with an Order, it means the broker executed/submitted that Order on behalf of an Investor.    
    }    
    
    class CommissionPlan {    
        %% Data Properties    
        planID : string    
        commissionRate : float    
        planName : string    
        %% Object Properties    
        %% Rules    
         %% RULE: commissionRate should be > 0 and typically < 0.05 (5%) in normal scenarios.    
    }    
    
    class Exchange {    
        %% Data Properties    
        exchangeName : string    
        country : string    
        %% Object Properties    
        orderTradedOn 1--* Order : one-to-many    
        %% Rules    
        %% RULE: Orders that are "tradedOn" this Exchange have trades executed under that exchange's rules (not deeply enforced here).    
    }    
    
    class FinancialInstrument {    
        %% Data Properties    
        symbol : string    
        description : string    
        tickSize : float    
        instrumentType : string  %% e.g. "Equity", "ETF"    
        %% Object Properties    
        orderInvolves *--1 Order: one-to-many    
        positionReferences *--1 Position : one-to-many    
        %% Rules    
        %% RULE: price increments for trades must be multiples of tickSize in a strict system (we approximate in code).    
    }    
    
    class Order {    
        %% Data Properties    
        orderID : string    
        orderType : string  %% e.g. "Market", "Limit", "Stop"    
        side : string  %% "Buy", "Sell"    
        quantity : int    
        limitPrice : float  %% null or not required for MarketOrder    
        timeInForce : string  %% e.g. "DAY", "GTC"    
        status : string  %% "Open", "PartiallyFilled", "Filled", "Cancelled"    
        creationDateTime : dateTime    
        %% Object Properties    
        placedBy 1--1 Investor : one-to-one    
        executedBy o--1 Broker : one-to-one    
        tradedOn o--1 Exchange : one-to-one    
        involvesInstrument 1--1 FinancialInstrument : one-to-one    
        tradeRelatedTo *--1 Trade: One-to-many    
    
        %% Rules    
        %% RULE 1: If orderType = "Limit", then limitPrice must not be null.    
        %% RULE 2: If orderType = "Market", limitPrice must be null.    
        %% RULE 3: If status = "Filled", sum of trade quantities for this order = quantity.    
        %% RULE 4: If status = "PartiallyFilled", sum of trade quantities < quantity and > 0.    
        %% RULE 5: If status = "Open" or "Cancelled", sum of trade quantities = 0 or < quantity.    
    }    
    
    class Trade {    
        %% Data Properties    
        tradeID : string    
        price : float    
        quantity : int    
        tradeDateTime : dateTime    
        %% Object Properties    
        relatedOrder 1--1 Order : one-to-one    
        %% Rules    
        %% RULE: must reference exactly one Order that it partially or fully fills.    
    }    
    
    class Portfolio {    
        %% Data Properties    
        portfolioID : string    
        portfolioName : string    
        %% Object Properties    
        belongsTo 1--1 Investor : one-to-one    
        hasPosition *--o Position : many-to-many    
        %% Rules    
        %% RULE: belongs to exactly one Investor.    
    }    
    
    class Position {    
        %% Data Properties    
        averageCost : float    
        currentQuantity : int    
        %% Object Properties    
        referencesInstrument 1--1 FinancialInstrument : one-to-one    
        portfolioHas o--* Portfolio: Many-to-one    
        %% Rules    
        %% RULE: negative quantity indicates short position, if the system allows short selling.    
    }    
    
    class CashAccount {    
        %% Data Properties    
        accountID : string    
        balance : float    
        %% Object Properties    
        belongsTo o--1 Investor : one-to-one    
        %% Rules    
        %% RULE: belongsTo -> Investor or Broker. If belongsToBroker, might be margin or settlement account.    
    }    
    
    
    %% Relationships    
    Investor "1..1" --> "1..*" Order : Association (placedBy)    
    Order "0..1" -- "1..1" Broker : Association (executedBy)    
    Order "0..1" -- "1..1" Exchange : Association (tradedOn)    
    Order "1..1" -- "1..1" FinancialInstrument : Association (involvesInstrument)    
    Trade "1..1" -- "1..1" Order : Association (relatedOrder)    
    Portfolio "1..1" -- "1..1" Investor : Association (belongsTo)    
    Portfolio "0..*" -- "1..*" Position : Association (hasPosition)    
    Position "1..1" -- "1..1" FinancialInstrument : Association (referencesInstrument)    
    CashAccount "0..1" --o "1..1" Investor : Association (belongsTo)    
    Broker "0..1" -- "1..1" CommissionPlan : Association (feeStructure)       
```                             
                                        
---              
              
```pseudocode            
Class: Investor    
   - investorName: string    
   - investorType: string   // e.g. "Retail", "Institutional"    
   // RULE: An Investor may place Orders and hold Positions in a Portfolio.    
    
Class: Broker    
   - brokerName: string    
   - brokerLicenseID: string    
   - feeStructure -> CommissionPlan (0..1)    
   // RULE: If a Broker is associated with an Order, it means the broker executed/submitted that Order on behalf of an Investor.    
    
Class: CommissionPlan (optional)    
   - planID: string    
   - commissionRate: float    
   - planName: string    
   // RULE: commissionRate should be > 0 and typically < 0.05 (5%) in normal scenarios.    
    
Class: Exchange    
   - exchangeName: string    
   - country: string    
   // RULE: Orders that are "tradedOn" this Exchange have trades executed under that exchange's rules (not deeply enforced here).    
    
Class: FinancialInstrument    
   - symbol: string    
   - description: string    
   - tickSize: float    
   - instrumentType: string // e.g. "Equity", "ETF"    
   // RULE: price increments for trades must be multiples of tickSize in a strict system (we approximate in code).    
    
Class: Order    
   - orderID: string    
   - orderType: string   // e.g. "Market", "Limit", "Stop"    
   - side: string        // "Buy", "Sell"    
   - quantity: int    
   - limitPrice: float   // null or not required for MarketOrder    
   - timeInForce: string // e.g. "DAY", "GTC"    
   - status: string      // "Open", "PartiallyFilled", "Filled", "Cancelled"    
   - creationDateTime: dateTime    
   // RULE 1: If orderType = "Limit", then limitPrice must not be null.    
   // RULE 2: If orderType = "Market", limitPrice must be null.    
   // RULE 3: If status = "Filled", sum of trade quantities for this order = quantity.    
   // RULE 4: If status = "PartiallyFilled", sum of trade quantities < quantity and > 0.    
   // RULE 5: If status = "Open" or "Cancelled", sum of trade quantities = 0 or < quantity.    
    
   // RELATIONSHIPS:    
   - placedBy -> Investor (1..1)    
   - executedBy -> Broker (0..1)  // optional if self-directed    
   - tradedOn -> Exchange (0..1)    
   - involvesInstrument -> FinancialInstrument (1..1)    
    
Class: Trade    
   - tradeID: string    
   - price: float    
   - quantity: int    
   - tradeDateTime: dateTime    
   // RULE: must reference exactly one Order that it partially or fully fills.    
    
   // RELATIONSHIP:    
   - relatedOrder -> Order (1..1)    
    
Class: Portfolio    
   - portfolioID: string    
   - portfolioName: string    
   // RULE: belongs to exactly one Investor.     
   - belongsTo -> Investor (1..1)    
   - hasPosition -> Position (0..*)    
    
Class: Position    
   - averageCost: float    
   - currentQuantity: int    
   // RULE: negative quantity indicates short position, if the system allows short selling.    
    
   // RELATIONSHIP:    
   - referencesInstrument -> FinancialInstrument (1..1)    
    
Class: CashAccount (optional)    
   - accountID: string    
   - balance: float    
   // RULE: belongsTo -> Investor or Broker. If belongsToBroker, might be margin or settlement account.    
    
   // RELATIONSHIP:    
   - belongsTo -> Investor (0..1)    
    
    
```             
              
*(We could add many more details—like quantity, material unit-of-measure, labor hours, etc. We are still in early stages, for this exercise, this may be enough.)*              
  
  