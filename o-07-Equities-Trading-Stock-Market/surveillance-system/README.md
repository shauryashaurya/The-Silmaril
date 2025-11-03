# Ontology #7.1: Stock Market / Equities Trading - **STOCK EXCHANGE SURVEILLANCE SYSTEM**                                                            
                                                              
                                                           
## Data Schemas                                                  
                                                  
### Order Schema                                                  
```                                                  
Order {                                                  
  order_id: UUID                                                  
  timestamp: nanosecond_precision_utc                                                  
  account_id: string                                                  
  trader_id: string                                                  
  firm_id: string                                                  
  instrument_id: string                                                  
  order_type: enum(market, limit, stop, stop_limit, iceberg, hidden)                                                  
  side: enum(buy, sell)                                                  
  quantity: decimal                                                  
  displayed_quantity: decimal                                                  
  price: decimal (nullable)                                                  
  stop_price: decimal (nullable)                                                  
  time_in_force: enum(day, gtc, ioc, fok, gtd)                                                  
  order_state: enum(new, partial_fill, filled, cancelled, rejected, expired)                                                  
  execution_instructions: set(post_only, reduce_only, self_trade_prevention)                                                  
  routing_instructions: string                                                  
  origination_channel: enum(api, gui, fix, proprietary)                                                  
  parent_order_id: UUID (nullable)                                                  
  related_order_ids: array[UUID]                                                  
  account_type: enum(retail, institutional, market_maker, proprietary)                                                  
  clearing_member: string                                                  
  mpid: string (market_participant_id)                                                  
  origin_ip: string                                                  
  session_id: string                                                  
  algorithmic_indicator: boolean                                                  
  algo_id: string (nullable)                                                  
  client_order_id: string                                                  
}                                                  
```                                                  
                                                  
### Trade Schema                                                  
```                                                  
Trade {                                                  
  trade_id: UUID                                                  
  timestamp: nanosecond_precision_utc                                                  
  instrument_id: string                                                  
  buy_order_id: UUID                                                  
  sell_order_id: UUID                                                  
  buy_account_id: string                                                  
  sell_account_id: string                                                  
  buy_firm_id: string                                                  
  sell_firm_id: string                                                  
  buy_trader_id: string                                                  
  sell_trader_id: string                                                  
  quantity: decimal                                                  
  price: decimal                                                  
  trade_value: decimal                                                  
  aggressor_side: enum(buy, sell)                                                  
  trade_type: enum(regular, cross, block, auction, dark)                                                  
  settlement_date: date                                                  
  clearing_member_buy: string                                                  
  clearing_member_sell: string                                                  
  buy_capacity: enum(principal, agency, riskless_principal, market_maker)                                                  
  sell_capacity: enum(principal, agency, riskless_principal, market_maker)                                                  
  reporting_party: string                                                  
  trade_conditions: set(opening, closing, late, out_of_sequence, derivative_priced)                                                  
  venue_id: string                                                  
}                                                  
```                                                  
                                                  
### Reference Data                                                  
```                                                  
Instrument {                                                  
  instrument_id: string                                                  
  symbol: string                                                  
  isin: string                                                  
  security_type: enum(equity, bond, derivative, etf)                                                  
  sector: string                                                  
  market_cap: decimal                                                  
  average_daily_volume: decimal                                                  
  circuit_breaker_thresholds: object                                                  
  tick_size: decimal                                                  
  lot_size: int                                                  
}                                                  
                                                  
Account {                                                  
  account_id: string                                                  
  firm_id: string                                                  
  account_type: enum(retail, institutional, market_maker, proprietary)                                                  
  beneficial_owners: array[string]                                                  
  related_accounts: array[string]                                                  
  credit_limit: decimal                                                  
  trading_permissions: set                                                  
}                                                  
```                                                  
                                                  
## CEP Rule Categories and Definitions                                                  
                                                  
### Category 1: Layering and Spoofing (10 rules)                                                  
                                                  
**Rule 1.1: Classic Layering**                                                  
- Detection: Multiple non-marketable limit orders on one side (typically 3+) followed by marketable order on opposite side within short timeframe (10-60 seconds), then cancellation of original orders                                                  
- Pattern: Account places 5 sell orders above market, then buys, then cancels sells                                                  
- Threshold: Order size ratio >3:1, execution within 60s, cancellation within 120s                                                  
- Why: Creates false liquidity impression to move price                                                  
                                                  
**Rule 1.2: Incremental Layering**                                                  
- Detection: Systematic placement of orders in small increments moving away from best bid/offer, creating illusion of depth                                                  
- Pattern: Orders placed at progressively worse prices (e.g., +0.01, +0.02, +0.03) within 5-second window                                                  
- Threshold: 5+ orders, uniform increment pattern, same account                                                  
- Why: Sophisticated variant avoiding detection by traditional rules                                                  
                                                  
**Rule 1.3: Flipping (Reverse Spoofing)**                                                  
- Detection: Large order placed, followed by multiple smaller orders on same side that execute, original order cancelled                                                  
- Pattern: 10,000 share buy order, then 500-share buys execute, original cancelled                                                  
- Threshold: Original order >5x subsequent orders, cancellation rate >80%                                                  
- Why: Uses own order to trigger HFT momentum algorithms                                                  
                                                  
**Rule 1.4: Quote Stuffing**                                                  
- Detection: Extremely high order-to-trade ratio with rapid entry/cancellation cycles                                                  
- Pattern: 1000+ orders per second from single account, <1% execution rate                                                  
- Threshold: Order rate >500/sec, cancellation within 50ms, execution <2%                                                  
- Why: Overloads order book, slows competitor systems, creates latency arbitrage                                                  
                                                  
**Rule 1.5: Iceberg Layering**                                                  
- Detection: Multiple iceberg orders with large hidden quantities combined with visible layering tactics                                                  
- Pattern: Visible 100-share orders backed by 10,000 hidden shares                                                  
- Threshold: Hidden quantity >10x visible, multiple price levels, correlated cancellations                                                  
- Why: Disguises true intent while creating false price pressure                                                  
                                                  
**Rule 1.6: Cross-Venue Layering**                                                  
- Detection: Layering orders on one venue while executing on another                                                  
- Pattern: Orders placed on Exchange A, executions on Exchange B, synchronous cancellations                                                  
- Threshold: Time correlation <500ms, multiple venues, same beneficial owner                                                  
- Why: Exploits inter-venue latency and NBBO calculation delays                                                  
                                                  
**Rule 1.7: Time-Based Spoofing**                                                  
- Detection: Orders placed at end of time period (auction, market close) then cancelled                                                  
- Pattern: Large orders 5 seconds before close, cancelled 1 second before close                                                  
- Threshold: Order size >2x average, timing pattern >60% of instances                                                  
- Why: Manipulates closing prices, settlement prices, or benchmark fixings                                                  
                                                  
**Rule 1.8: Momentum Ignition via Layering**                                                  
- Detection: Layering that triggers stop-losses or algorithmic breakout strategies                                                  
- Pattern: Orders push through technical resistance levels, cancelled after momentum established                                                  
- Threshold: Price movement >0.5%, volume spike >3x, immediate order cancellation                                                  
- Why: Intentionally creates false breakout signals                                                  
                                                  
**Rule 1.9: Ping Orders (Probing)**                                                  
- Detection: Systematic small orders across multiple price levels to discover hidden liquidity                                                  
- Pattern: 1-10 share orders at every price increment, rapid cancellations                                                  
- Threshold: Order size <0.1% typical, price levels >20, time window <5 seconds                                                  
- Why: Information gathering about dark pools and iceberg orders                                                  
                                                  
**Rule 1.10: Pinging with Cancellation Cascades**                                                  
- Detection: Ping orders that, when filled, trigger immediate cancellation of other orders                                                  
- Pattern: Small order executes, 50+ related orders cancel within 10ms                                                  
- Threshold: Cancel-to-fill ratio >50:1, latency <10ms, account correlation                                                  
- Why: Testing market depth while maintaining priority without commitment                                                  
                                                  
### Category 2: Wash Trading and Self-Matching (8 rules)                                                  
                                                  
**Rule 2.1: Same Account Wash Trading**                                                  
- Detection: Buy and sell orders from same account matching each other                                                  
- Pattern: Account A buys from Account A (via different sub-accounts or trading IDs)                                                  
- Threshold: Same beneficial owner, no economic benefit, pattern repetition >3                                                  
- Why: Creates false volume impression, tax loss harvesting fraud                                                  
                                                  
**Rule 2.2: Cross-Account Wash Trading**                                                  
- Detection: Systematic matching between related accounts with no price discovery                                                  
- Pattern: Account A always buys from Account B at predictable intervals                                                  
- Threshold: Match rate >60%, accounts share beneficial owner or IP address                                                  
- Why: Disguised wash trading through related entities                                                  
                                                  
**Rule 2.3: Marker Timing Wash Trading**                                                  
- Detection: Trades that occur at same price for extended periods between related parties                                                  
- Pattern: A-B trading at $50.00 for 100 consecutive trades while market moves                                                  
- Threshold: Price variance <0.01%, trade count >50, related parties                                                  
- Why: Clear indication of prearranged trading                                                  
                                                  
**Rule 2.4: High-Frequency Wash Pattern**                                                  
- Detection: Micro-burst wash trading within milliseconds                                                  
- Pattern: 100 wash trades in 1-second bursts, repeated hourly                                                  
- Threshold: Time pattern regularity >80%, no external participants                                                  
- Why: Automated wash trading to inflate volume metrics                                                  
                                                  
**Rule 2.5: Cross-Venue Wash Trading**                                                  
- Detection: Related accounts trading synchronously across multiple venues                                                  
- Pattern: Buy on Exchange A, sell on Exchange B, same parties, same time                                                  
- Threshold: Time correlation <100ms, beneficial owner match, no economic gain                                                  
- Why: Exploits cross-venue detection gaps                                                  
                                                  
**Rule 2.6: Pre-Arranged Trading**                                                  
- Detection: Perfect or near-perfect order matching suggesting coordination                                                  
- Pattern: Orders entered within milliseconds, quantities match exactly, repeated pattern                                                  
- Threshold: Order timing correlation >95%, quantity match 100%, frequency >10/day                                                  
- Why: Indicates collusion or prearranged agreements                                                  
                                                  
**Rule 2.7: Volume Inflation Before Corporate Events**                                                  
- Detection: Wash trading surge before capital raises, listings, or index additions                                                  
- Pattern: Volume increases 10x in week before event, wash trading characteristics                                                  
- Threshold: Volume anomaly >5σ, wash trading indicators present, event correlation                                                  
- Why: Manipulates liquidity metrics for corporate benefit                                                  
                                                  
**Rule 2.8: Parking via Wash Trades**                                                  
- Detection: Temporary position transfers between related accounts                                                  
- Pattern: Account A sells to Account B, reversed within 24 hours, no market activity between                                                  
- Threshold: Round-trip completion >90%, holding period <48hrs, related accounts                                                  
- Why: Regulatory position limit evasion or capital requirement manipulation                                                  
                                                  
### Category 3: Front Running and Information Leakage (9 rules)                                                  
                                                  
**Rule 3.1: Classic Front Running**                                                  
- Detection: Employee or firm trading ahead of customer order with material impact                                                  
- Pattern: Proprietary trade, then customer order same direction within 60 seconds, price movement                                                  
- Threshold: Proprietary order >100 shares, customer order >10,000 shares, profit >$1000                                                  
- Why: Breach of fiduciary duty, unlawful use of material non-public information                                                  
                                                  
**Rule 3.2: Shadow Trading**                                                  
- Detection: Consistent pattern of trading before related party's large orders                                                  
- Pattern: Account A trades, Account B (related) trades large order same direction within 5 minutes                                                  
- Threshold: Correlation >70%, profit consistent, relationship identifiable                                                  
- Why: Information leakage through family, friends, or business relationships                                                  
                                                  
**Rule 3.3: Time-Proximity Front Running**                                                  
- Detection: Trading immediately before algo order execution windows                                                  
- Pattern: Account enters position 1-10 seconds before known algo execution time                                                  
- Threshold: Timing precision >60%, algo order identification, consistent profit                                                  
- Why: Exploitation of predictable institutional trading patterns                                                  
                                                  
**Rule 3.4: Parent Order Front Running**                                                  
- Detection: Trading ahead of visible portions of iceberg or parent orders                                                  
- Pattern: Small orders accumulate before large iceberg refreshes                                                  
- Threshold: Position build >1000 shares, iceberg refresh follows within 30s, repetition >5                                                  
- Why: Exploiting visible order flow information                                                  
                                                  
**Rule 3.5: News-Based Front Running**                                                  
- Detection: Trading before news release with position unwound after release                                                  
- Pattern: Unusual buying 1-30 minutes before announcement, liquidation post-announcement                                                  
- Threshold: Volume >5x average, timing correlation >80%, information materiality                                                  
- Why: Material non-public information misuse                                                  
                                                  
**Rule 3.6: Block Trade Front Running**                                                  
- Detection: Trading ahead of known block trade negotiations                                                  
- Pattern: Accumulation while block trade being negotiated, execution before block prints                                                  
- Threshold: Party knowledge of block, position size >100 shares, temporal correlation                                                  
- Why: Misuse of block trading desk information                                                  
                                                  
**Rule 3.7: Derivative-Based Front Running**                                                  
- Detection: Trading underlying security ahead of large derivative orders                                                  
- Pattern: Equity purchase before large equity option order, delta correlation                                                  
- Threshold: Equity quantity correlates with option delta, timing <60s, consistent pattern                                                  
- Why: Exploiting derivative market color                                                  
                                                  
**Rule 3.8: Internalization Front Running**                                                  
- Detection: Firm trading ahead before internalizing customer order at worse price                                                  
- Pattern: Proprietary buy at $50.00, customer internalized at $50.05                                                  
- Threshold: Price difference >$0.02, consistent pattern, firm profits                                                  
- Why: Abusive internalization practices                                                  
                                                  
**Rule 3.9: Inter-Desk Front Running**                                                  
- Detection: One desk trading ahead of another desk's customer flow                                                  
- Pattern: Proprietary desk buys, customer flow from sales desk follows                                                  
- Threshold: Same firm, different desks, temporal correlation >70%, consistent profit                                                  
- Why: Information barriers failure within firm                                                  
                                                  
### Category 4: Marking the Close and Settlement Manipulation (7 rules)                                                  
                                                  
**Rule 4.1: Banging the Close**                                                  
- Detection: Aggressive buying or selling in final minutes to influence closing price                                                  
- Pattern: Large orders in last 5 minutes representing >20% of closing volume                                                  
- Threshold: Volume concentration >20%, price impact >0.3%, pattern frequency                                                  
- Why: Manipulates benchmarks, NAV calculations, portfolio valuations                                                  
                                                  
**Rule 4.2: Auction Imbalance Exploitation**                                                  
- Detection: Late order entry to influence closing auction imbalance signals                                                  
- Pattern: Orders entered in last 10 seconds of auction order entry period                                                  
- Threshold: Order size >5% of imbalance, timing >90% in last 10 seconds, repetition                                                  
- Why: Manipulates auction pricing mechanism                                                  
                                                  
**Rule 4.3: Settlement Price Manipulation**                                                  
- Detection: Trading in derivative underlying to influence settlement                                                  
- Pattern: Aggressive orders near settlement time, positions closed immediately after                                                  
- Threshold: Timing correlation >90%, position reversal within 1 hour, price impact                                                  
- Why: Manipulates derivative contract settlements                                                  
                                                  
**Rule 4.4: Marking for Month-End**                                                  
- Detection: Price manipulation on last trading day of month                                                  
- Pattern: Price elevation on month-end, return to normal next trading day                                                  
- Threshold: Price deviation >1%, volume spike >3x, monthly pattern                                                  
- Why: Portfolio valuation inflation, performance metric manipulation                                                  
                                                  
**Rule 4.5: Index Rebalancing Exploitation**                                                  
- Detection: Trading ahead of known index rebalancing with price impact                                                  
- Pattern: Accumulation before index add announcement, liquidation during rebalancing                                                  
- Threshold: Position size >100,000 shares, timing correlation with index events                                                  
- Why: Front running passive index fund flows                                                  
                                                  
**Rule 4.6: Benchmark Fixing**                                                  
- Detection: Coordinated trading at specific benchmark calculation times (VWAP, TWAP)                                                  
- Pattern: Volume surge at calculation snapshots, otherwise minimal activity                                                  
- Threshold: Snapshot volume >50% of period volume, price deviation, pattern regularity                                                  
- Why: Manipulates reference rates, benchmark indices                                                  
                                                  
**Rule 4.7: After-Hours Manipulation**                                                  
- Detection: Material trades in illiquid after-hours sessions to establish prices                                                  
- Pattern: Single trade moves price >2% in after-hours on low volume                                                  
- Threshold: Volume <100 shares, price impact >2%, timing near closing                                                  
- Why: Creates misleading pricing information for reporting                                                  
                                                  
### Category 5: Pump and Dump / Market Manipulation (6 rules)                                                  
                                                  
**Rule 5.1: Coordinated Pump Pattern**                                                  
- Detection: Multiple accounts simultaneously buying low-liquidity security                                                  
- Pattern: 10+ accounts buying within 5-minute window, social media correlation                                                  
- Threshold: Account coordination >80%, liquidity <$1M daily, price increase >10%                                                  
- Why: Artificial price inflation scheme                                                  
                                                  
**Rule 5.2: Dump Detection**                                                  
- Detection: Large liquidation after price run-up, especially by original accumulators                                                  
- Pattern: Accounts that bought during pump liquidate after >20% price increase                                                  
- Threshold: Liquidation >70% of accumulated position, price decline >15%, timeframe <24hrs                                                  
- Why: Completes pump-and-dump scheme                                                  
                                                  
**Rule 5.3: Churning**                                                  
- Detection: Excessive trading in customer account for commission generation                                                  
- Pattern: Account turnover >100x annually, minimal net position change                                                  
- Threshold: Commission-to-equity ratio >10%, turnover rate, customer complaint history                                                  
- Why: Broker misconduct, unauthorized trading                                                  
                                                  
**Rule 5.4: Painting the Tape**                                                  
- Detection: Trading between related accounts to create activity appearance                                                  
- Pattern: Back-and-forth trading at incrementally higher prices, low net position change                                                  
- Threshold: Related account trading >70%, price walk >5%, minimal outside participation                                                  
- Why: Creates false impression of demand                                                  
                                                  
**Rule 5.5: Capping/Pegging**                                                  
- Detection: Systematic order placement to prevent price from rising above threshold                                                  
- Pattern: Large sell orders appear whenever price approaches specific level                                                  
- Threshold: Price level defense >5 times, order cancellation when price retreats                                                  
- Why: Prevents options from going in-the-money or other threshold events                                                  
                                                  
**Rule 5.6: Cross-Product Manipulation**                                                  
- Detection: Trading one instrument to manipulate price of related instrument                                                  
- Pattern: Equity trades to influence option prices, cash-futures basis manipulation                                                  
- Threshold: Related instrument price correlation >0.9, timing <1 minute, reversal pattern                                                  
- Why: Exploits pricing relationships for profit                                                  
                                                  
### Category 6: Insider Trading Patterns (6 rules)                                                  
                                                  
**Rule 6.1: Pre-Announcement Trading**                                                  
- Detection: Unusual trading before material corporate announcements                                                  
- Pattern: Account trading >3σ above normal 1-5 days before announcement                                                  
- Threshold: Volume anomaly >5σ, timing correlation >75%, information materiality                                                  
- Why: Indicates possible insider information misuse                                                  
                                                  
**Rule 6.2: Family/Associate Trading Clusters**                                                  
- Detection: Trading by accounts related to corporate insiders before announcements                                                  
- Pattern: Spouse, relative, or known associate trades before material event                                                  
- Threshold: Relationship mapping, timing correlation, materiality of information                                                  
- Why: Information leakage through personal relationships                                                  
                                                  
**Rule 6.3: Tippee Chain Detection**                                                  
- Detection: Sequential trading pattern suggesting information cascade                                                  
- Pattern: Insider trades, associate trades, friend-of-friend trades in temporal sequence                                                  
- Threshold: Network analysis, temporal cascade <48 hours, consistent direction                                                  
- Why: Tracks information propagation through tipper-tippee chains                                                  
                                                  
**Rule 6.4: Options-Heavy Insider Pattern**                                                  
- Detection: Unusual options activity before announcements, especially OTM options                                                  
- Pattern: Out-of-money option buying, short-dated, before announcement                                                  
- Threshold: Volume >10x average, moneyness >5%, announcement within 30 days                                                  
- Why: High-leverage exploitation of material information                                                  
                                                  
**Rule 6.5: Blackout Period Trading**                                                  
- Detection: Insider trading during prohibited blackout windows                                                  
- Pattern: Corporate insider trades during earnings blackout period                                                  
- Threshold: Insider identification, blackout period violation, trade occurrence                                                  
- Why: Direct policy violation, regulatory concern                                                  
                                                  
**Rule 6.6: Reverse Merger/SPAC Insider Patterns**                                                  
- Detection: Trading before merger announcements in SPACs or reverse merger targets                                                  
- Pattern: Unusual volume in SPAC or target 1-14 days before announcement                                                  
- Threshold: Volume >5x average, price movement >15%, announcement timing                                                  
- Why: High-risk area for insider trading abuse                                                  
                                                  
### Category 7: Cross-Market and Cross-Asset Manipulation (5 rules)                                                  
                                                  
**Rule 7.1: Equity-Derivative Arbitrage Manipulation**                                                  
- Detection: Coordinated trading in equity and derivative to exploit pricing                                                  
- Pattern: Aggressive equity selling while holding large short derivative position                                                  
- Threshold: Position size correlation, timing synchronization, profit realization                                                  
- Why: Manipulates one market to profit in another                                                  
                                                  
**Rule 7.2: Cash-Futures Basis Manipulation**                                                  
- Detection: Trading cash instrument to influence futures settlement or vice versa                                                  
- Pattern: Large cash trades near futures expiration affecting basis                                                  
- Threshold: Position size >$10M, timing near expiration, basis anomaly >0.1%                                                  
- Why: Settlement price manipulation for derivative benefit                                                  
                                                  
**Rule 7.3: ETF Creation/Redemption Manipulation**                                                  
- Detection: Trading ETF underlying securities to influence NAV or arbitrage spread                                                  
- Pattern: Basket securities traded to widen tracking difference                                                  
- Threshold: Basket component correlation >0.8, timing near NAV calculation, profit                                                  
- Why: ETF arbitrage mechanism abuse                                                  
                                                  
**Rule 7.4: Cross-Border Manipulation**                                                  
- Detection: Trading ADR/ordinary shares to exploit settlement or time zone differences                                                  
- Pattern: ADR trading influences ordinary share price during closed market                                                  
- Threshold: Price deviation >0.5%, timing advantage exploitation, position reversal                                                  
- Why: Exploits market closure timing differences                                                  
                                                  
**Rule 7.5: Commodity-Equity Link Manipulation**                                                  
- Detection: Trading commodity to influence related equity or vice versa                                                  
- Pattern: Oil trading correlates with oil company equity trading                                                  
- Threshold: Cross-asset correlation >0.9, timing <5 minutes, related party                                                  
- Why: Cross-market manipulation for indirect benefit                                                  
                                                  
### Category 8: Operational and Credit Risk (4 rules)                                                  
                                                  
**Rule 8.1: Position Limit Breaches**                                                  
- Detection: Account exceeds regulatory or exchange position limits                                                  
- Pattern: Position accumulation across related accounts exceeds thresholds                                                  
- Threshold: Aggregated position >regulatory limit, beneficial owner consolidation                                                  
- Why: Regulatory compliance, systemic risk management                                                  
                                                  
**Rule 8.2: Credit Limit Breaches**                                                  
- Detection: Trading exceeds credit authorization                                                  
- Pattern: Account exposure exceeds approved credit limit                                                  
- Threshold: Exposure >credit limit, margin call trigger, firm risk exposure                                                  
- Why: Credit risk management, potential firm losses                                                  
                                                  
**Rule 8.3: Fat Finger Detection**                                                  
- Detection: Orders with likely erroneous size or price parameters                                                  
- Pattern: Order size >100x average for account, price >5% from market                                                  
- Threshold: Deviation >5σ from account history, price reasonability check                                                  
- Why: Operational risk mitigation, market disruption prevention                                                  
                                                  
**Rule 8.4: Algo Gone Wild**                                                  
- Detection: Algorithm behavior deviating from expected parameters                                                  
- Pattern: Order rate >1000/sec, price deviation >2%, repetitive pattern                                                  
- Threshold: Rate threshold, loss accumulation >$100K, kill switch activation                                                  
- Why: Technology risk management, market stability                                                  
                                                  
### Category 9: Trading Venue and Execution Abuse (5 rules)                                                  
                                                  
**Rule 9.1: Quote Fading**                                                  
- Detection: Orders systematically cancelled when approached by incoming order                                                  
- Pattern: Best bid/offer orders cancelled within 10ms of incoming marketable order                                                  
- Threshold: Cancellation rate >80%, latency <10ms, systematic pattern                                                  
- Why: False liquidity provision, unfair trading advantage                                                  
                                                  
**Rule 9.2: Order Book Layering on Multiple Venues**                                                  
- Detection: Coordinated order placement across venues to create false depth                                                  
- Pattern: Orders at same relative price levels on 3+ venues simultaneously                                                  
- Threshold: Venue count >3, price level correlation >0.95, cancellation synchronization                                                  
- Why: Cross-venue market manipulation                                                  
                                                  
**Rule 9.3: Dark Pool Information Leakage**                                                  
- Detection: Trading in lit market suggests knowledge of dark pool orders                                                  
- Pattern: Lit market orders systematically trade ahead of dark pool executions                                                  
- Threshold: Timing advantage >90%, dark pool order correlation, consistent profit                                                  
- Why: Information barrier breach between venues                                                  
                                                  
**Rule 9.4: Maker-Taker Abuse**                                                  
- Detection: Trading primarily for rebates rather than legitimate price discovery                                                  
- Pattern: Orders placed/cancelled to maximize rebates with minimal risk                                                  
- Threshold: Rebate revenue >trading P&L, order-to-trade ratio >100:1                                                  
- Why: Exchange incentive structure abuse                                                  
                                                  
**Rule 9.5: Post-Only Order Abuse**                                                  
- Detection: Systematic use of post-only orders to gain priority then cancel                                                  
- Pattern: Post-only orders to gain queue position, cancelled before execution                                                  
- Threshold: Cancellation rate >90%, queue position gaming, systematic pattern                                                  
- Why: Unfair priority advantage, liquidity provision failure                                                  
                                                  
## Technical Complexities                                                  
                                                  
### 1. Temporal Correlation and Causality                                                  
**Challenge**: Distinguishing causation from correlation across millions of events per second                                                  
- Requires sophisticated time-series analysis with nanosecond precision                                                  
- Must handle clock skew across distributed systems and venues                                                  
- Need to establish causal chains across related events with confidence scoring                                                  
- Complex when multiple rule triggers overlap temporally                                                  
                                                  
**Implementation**: Vector clocks, Lamport timestamps, causal consistency models                                                  
                                                  
### 2. Entity Resolution and Graph Analysis                                                  
**Challenge**: Identifying related accounts, beneficial owners, and hidden relationships                                                  
- Accounts may be related through: beneficial ownership, IP addresses, trading patterns, social graphs, corporate structures                                                  
- Dynamic relationships that change over time                                                  
- Privacy constraints limit information sharing across entities                                                  
- Graph database queries at scale with 1M TPS throughput                                                  
                                                  
**Implementation**: Real-time graph databases, entity resolution algorithms, probabilistic matching, network analysis                                                  
                                                  
### 3. Baseline Establishment and Anomaly Detection                                                  
**Challenge**: Defining "normal" for diverse trading patterns                                                  
- Each account, instrument, and market condition has different baseline                                                  
- Baselines shift with market conditions, volatility, news                                                  
- Cold start problem for new accounts or instruments                                                  
- Statistical significance vs practical significance tradeoffs                                                  
                                                  
**Implementation**: Adaptive sliding windows, multi-dimensional normal distributions, machine learning baselines, regime detection                                                  
                                                  
### 4. False Positive Management                                                  
**Challenge**: Reducing alert noise while maintaining detection sensitivity                                                  
- Rules generate alerts, alerts require investigation, investigators are limited resource                                                  
- Cost of false positives: investigation time, alert fatigue                                                  
- Cost of false negatives: regulatory penalties, market integrity damage                                                  
- Precision-recall optimization per rule type                                                  
                                                  
**Implementation**: Multi-stage filtering, risk scoring, case management workflows, machine learning classifiers                                                  
                                                  
### 5. Low-Latency Processing                                                  
**Challenge**: Sub-millisecond processing requirements for some patterns                                                  
- Quote stuffing detection requires <1ms response                                                  
- Must process 1M events/second with <10ms latency budget                                                  
- Stateful processing across distributed nodes                                                  
- Memory constraints for windowed aggregations                                                  
                                                  
**Implementation**: In-memory stream processing, partitioning strategies, optimized data structures, hardware acceleration                                                  
                                                  
### 6. State Management at Scale                                                  
**Challenge**: Maintaining trading state across millions of instruments and accounts                                                  
- Must track open orders, positions, execution history, account relationships                                                  
- State size: terabytes of in-memory data                                                  
- State consistency across distributed nodes                                                  
- Recovery and replay after failures                                                  
                                                  
**Implementation**: Distributed state stores, event sourcing, CQRS patterns, snapshotting strategies                                                  
                                                  
### 7. Cross-Venue Aggregation                                                  
**Challenge**: Correlating activity across fragmented markets                                                  
- Different data formats, timestamps, identifiers per venue                                                  
- Latency variations across venues (10-500ms)                                                  
- Missing or delayed data from some venues                                                  
- Regulatory requirements for consolidated audit trail                                                  
                                                  
**Implementation**: Normalization layers, clock synchronization, imputation strategies, multi-venue correlation algorithms                                                  
                                                  
### 8. Pattern Evolution and Adaptive Adversaries                                                  
**Challenge**: Manipulators adapt to detection rules                                                  
- Once a pattern is detected, manipulators modify tactics                                                  
- Need for continuous rule refinement and ML model retraining                                                  
- Behavioral fingerprinting vs rule-based detection tradeoffs                                                  
- Zero-day manipulation pattern detection                                                  
                                                  
**Implementation**: Ensemble methods, unsupervised learning, behavioral analytics, regular rule backtesting                                                  
                                                  
### 9. Explainability and Audit Trail                                                  
**Challenge**: Regulators require explainable alerts and decisions                                                  
- "Black box" ML models insufficient for regulatory proceedings                                                  
- Must reconstruct exact reasoning for any alert, years later                                                  
- Audit trail must survive system upgrades and migrations                                                  
- Chain of custody for evidence                                                  
                                                  
**Implementation**: Immutable audit logs, rule versioning, decision tree documentation, event replay capability                                                  
                                                  
### 10. Multi-Jurisdictional Compliance                                                  
**Challenge**: Different regulatory requirements across markets                                                  
- SEC, ESMA, MiFID II, ASIC have different definitions and thresholds                                                  
- Must support multiple rule variants simultaneously                                                  
- Configuration management complexity                                                  
- Harmonization vs localization tradeoffs                                                  
                                                  
**Implementation**: Configurable rule engines, jurisdiction-specific parameter sets, regulatory mapping layers                                                  
                                                  
### 11. Data Quality and Completeness                                                  
**Challenge**: Garbage in, garbage out for surveillance                                                  
- Missing trades, delayed updates, incorrect timestamps                                                  
- Reference data staleness (corporate actions, account changes)                                                  
- Handling data corrections and cancellations retroactively                                                  
- Incomplete beneficial ownership information                                                  
                                                  
**Implementation**: Data quality monitors, reconciliation processes, correction propagation, confidence scoring                                                  
                                                  
### 12. Performance Optimization                                                  
**Challenge**: Balancing detection depth with computational cost                                                  
- Some patterns require joins across billions of historical records                                                  
- Graph traversal for relationship detection is computationally expensive                                                  
- Trade-off between real-time detection and deep forensic analysis                                                  
- Resource allocation across rule priorities                                                  
                                                  
**Implementation**: Tiered processing architecture, sampling strategies, index optimization, query caching, approximate computing                                                  
                                                  
### 13. Rule Interaction and Precedence                                                  
**Challenge**: Rules may conflict or overlap                                                  
- Same behavior may trigger multiple rules                                                  
- Rules may have different severity levels                                                  
- Determining root cause when multiple manipulative behaviors co-occur                                                  
- Avoiding duplicate investigations                                                  
                                                  
**Implementation**: Rule dependency graphs, alert deduplication, composite pattern detection, root cause analysis                                                  
                                                  
### 14. Historical Analysis and Backtesting                                                  
**Challenge**: Validating rules against historical data                                                  
- Need to replay historical events to test new rules                                                  
- Must avoid lookahead bias in rule testing                                                  
- Computing infrastructure to process years of data                                                  
- Measuring rule effectiveness metrics                                                  
                                                  
**Implementation**: Time-travel query capabilities, replay infrastructure, A/B testing frameworks, performance metrics                                                  
                                                  
### 15. Privacy and Information Barriers                                                  
**Challenge**: Maintaining confidentiality while detecting manipulation                                                  
- Cannot share customer order information inappropriately                                                  
- Chinese walls between surveillance and trading desks                                                  
- GDPR and data protection requirements                                                  
- Secure multi-party computation for cross-firm patterns                                                  
                                                  
**Implementation**: Access controls, encryption, differential privacy, tokenization, need-to-know enforcement                                                  
                                                  
### Execution Architecture Considerations                                                  
                                                  
**Stream Processing Layer**: Apache Flink or custom CEP engine with:                                                  
- Horizontal scaling to 1000+ nodes                                                  
- Exactly-once processing semantics                                                  
- Millisecond-level windowing                                                  
- Complex pattern matching DSL                                                  
                                                  
**Storage Layer**: Hybrid approach:                                                  
- In-memory: Redis/Hazelcast for hot state                                                  
- Time-series: InfluxDB/TimescaleDB for historical metrics                                                    
- Graph: Neo4j for relationship analysis                                                  
- Data lake: Parquet on S3 for long-term retention                                                  
                                                  
**Rule Definition**: Domain-specific language allowing:                                                  
- Declarative pattern specification                                                  
- Temporal logic operators                                                  
- Statistical functions and anomaly detection                                                  
- Graph query integration                                                  
                                                  
**Alert Management**: Workflow system with:                                                  
- Risk-based prioritization                                                  
- Case assignment and tracking                                                  
- Evidence package generation                                                  
- Regulatory reporting integration                                                  
                                                  
The system must balance competing demands: regulatory compliance, operational efficiency, market integrity, and firm profitability. Success requires continuous evolution as market structure and manipulative tactics evolve.                                                  
                                               
	                                           
# Technical CEP Rule Definitions                                        
                                        
## Rule Definition Schema                                        
                                        
Each rule follows this structure:                                        
```                                        
RULE_ID: Unique identifier                                        
PATTERN: Event sequence pattern                                        
WINDOW: Temporal constraints                                        
CONDITIONS: Boolean expressions and thresholds                                        
CONTEXT: Required state and reference data                                        
AGGREGATIONS: Statistical computations                                        
ACTIONS: Alert generation and downstream processing                                        
```                                        
                                        
---                                        
                                        
## Category 1: Layering and Spoofing                                        
                                        
### Rule 1.1: Classic Layering                                        
                                        
```sql                                        
RULE_ID: LAYER_CLASSIC_001                                        
PRIORITY: CRITICAL                                        
                                        
PATTERN:                                        
  SEQ(                                        
    orders[side = S1, account_id = A1] AS layer_orders                                        
      WHERE count(*) >= 3                                        
      AND all(order_type = 'limit')                                        
      AND all(price - best_offer(instrument_id) > tick_size * 2),                                        
                                            
    trades[side = opposite(S1), account_id = A1] AS execution                                        
      WHERE quantity >= 100,                                        
                                            
    cancellations[order_id IN layer_orders.order_id] AS cancel_events                                        
      WHERE count(*) / layer_orders.count() >= 0.8                                        
  )                                        
                                        
WINDOW:                                        
  layer_orders: SLIDING(60 seconds)                                        
  execution: WITHIN(60 seconds) AFTER layer_orders                                        
  cancel_events: WITHIN(120 seconds) AFTER execution                                        
                                        
CONDITIONS:                                        
  - layer_orders.total_quantity / execution.quantity >= 3.0                                        
  - layer_orders.price_distance_avg >= tick_size * 2                                        
  - cancel_events.cancel_time_avg - execution.timestamp <= 120s                                        
  - execution.price_impact >= 0.001 (0.1%)                                        
                                        
CONTEXT:                                        
  - best_bid_offer: STREAM(market_data)                                         
      PARTITION BY instrument_id                                        
      KEEP LAST 1                                        
  - tick_size: REF_DATA(instruments)                                        
  - account_history: STATE(account_id)                                        
      KEEP 30 days                                        
                                        
AGGREGATIONS:                                        
  layer_depth = SUM(layer_orders.quantity)                                        
  layer_value = SUM(layer_orders.quantity * layer_orders.price)                                        
  execution_value = execution.quantity * execution.price                                        
  size_ratio = layer_depth / execution.quantity                                        
  price_impact = ABS(execution.price - pre_order_mid_price) / pre_order_mid_price                                        
  cancellation_speed = AVG(cancel_events.timestamp - execution.timestamp)                                        
                                        
OUTPUT:                                        
  alert_type: "LAYERING_CLASSIC"                                        
  severity: CASE                                        
    WHEN size_ratio > 10 AND price_impact > 0.005 THEN "HIGH"                                        
    WHEN size_ratio > 5 THEN "MEDIUM"                                        
    ELSE "LOW"                                        
  END                                        
  evidence: {                                        
    layer_orders: layer_orders[*],                                        
    execution: execution,                                        
    cancellations: cancel_events[*],                                        
    market_impact: price_impact,                                        
    metrics: {size_ratio, cancellation_speed, layer_depth}                                        
  }                                        
  related_accounts: GRAPH_QUERY(account_id, depth=2)                                        
```                                        
                                        
### Rule 1.2: Incremental Layering                                        
                                        
```sql                                        
RULE_ID: LAYER_INCREMENTAL_002                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  orders[account_id = A1, instrument_id = I1, side = S1] AS incremental_orders                                        
  WHERE                                         
    count(*) >= 5                                        
    AND order_type = 'limit'                                        
                                        
WINDOW:                                        
  SLIDING(5 seconds)                                        
                                        
CONDITIONS:                                        
  - price_increments_uniform(incremental_orders.price[], tolerance=0.0001)                                        
  - price_monotonic_increasing(incremental_orders.price[])                                         
      IF side = 'sell'                                        
  - price_monotonic_decreasing(incremental_orders.price[])                                         
      IF side = 'buy'                                        
  - time_between_orders_avg <= 1000ms                                        
  - orders_away_from_market(incremental_orders, min_distance=2*tick_size)                                        
                                        
CONTEXT:                                        
  best_market: STREAM(market_data)                                        
    PARTITION BY instrument_id                                        
    KEEP LAST 100ms                                        
                                        
AGGREGATIONS:                                        
  increment_size = AVG(incremental_orders.price[i+1] - incremental_orders.price[i])                                        
  increment_stddev = STDDEV(incremental_orders.price[i+1] - incremental_orders.price[i])                                        
  increment_coefficient_of_variation = increment_stddev / increment_size                                        
  total_displayed_depth = SUM(incremental_orders.displayed_quantity)                                        
  order_timing_variance = STDDEV(incremental_orders.timestamp[i+1] - incremental_orders.timestamp[i])                                        
                                        
FUNCTION price_increments_uniform(prices[], tolerance):                                        
  increments = [prices[i+1] - prices[i] for i in 0..len(prices)-2]                                        
  avg_increment = AVG(increments)                                        
  RETURN ALL(ABS(inc - avg_increment) <= tolerance for inc in increments)                                        
                                        
FUNCTION orders_away_from_market(orders, min_distance):                                        
  FOR each order IN orders:                                        
    IF order.side = 'buy':                                        
      distance = best_bid - order.price                                        
    ELSE:                                        
      distance = order.price - best_offer                                        
    IF distance < min_distance:                                        
      RETURN false                                        
  RETURN true                                        
                                        
OUTPUT:                                        
  alert_type: "LAYERING_INCREMENTAL"                                        
  severity: IF increment_coefficient_of_variation < 0.1 THEN "HIGH" ELSE "MEDIUM"                                        
  evidence: {                                        
    orders: incremental_orders[*],                                        
    increment_pattern: {increment_size, increment_stddev},                                        
    market_context: {best_bid, best_offer, spread}                                        
  }                                        
```                                        
                                        
### Rule 1.3: Flipping                                        
                                        
```sql                                        
RULE_ID: SPOOF_FLIP_003                                        
PRIORITY: CRITICAL                                        
                                        
PATTERN:                                        
  SEQ(                                        
    order[account_id = A1, instrument_id = I1, side = S1, quantity >= Q1] AS anchor_order                                        
      WHERE order_state = 'new',                                        
                                            
    trades[account_id = A1, instrument_id = I1, side = S1] AS subsequent_trades                                        
      WHERE count(*) >= 2                                        
      AND sum(quantity) < anchor_order.quantity * 0.3,                                        
                                            
    cancellation[order_id = anchor_order.order_id] AS anchor_cancel                                        
  )                                        
                                        
WINDOW:                                        
  subsequent_trades: WITHIN(30 seconds) AFTER anchor_order                                        
  anchor_cancel: WITHIN(60 seconds) AFTER anchor_order                                        
                                          
CONDITIONS:                                        
  - anchor_order.quantity >= 1000                                        
  - anchor_order.quantity / AVG(subsequent_trades.quantity) >= 5                                        
  - anchor_cancel.remaining_quantity / anchor_order.quantity >= 0.8                                        
  - TIME(anchor_cancel) - TIME(last(subsequent_trades)) <= 10 seconds                                        
  - price_movement_favorable(anchor_order, subsequent_trades)                                        
                                        
CONTEXT:                                        
  account_order_history: STATE(account_id, instrument_id)                                        
    WINDOW: 24 hours                                        
    METRICS: [avg_order_size, avg_execution_rate]                                        
                                        
AGGREGATIONS:                                        
  anchor_size = anchor_order.quantity                                        
  executed_size = SUM(subsequent_trades.quantity)                                        
  execution_rate = executed_size / anchor_size                                        
  size_ratio = anchor_size / AVG(subsequent_trades.quantity)                                        
  avg_execution_price = VWAP(subsequent_trades)                                        
  price_improvement = (avg_execution_price - anchor_order.price) *                                         
                      IF(side='buy', -1, 1)                                        
  time_to_cancel = anchor_cancel.timestamp - anchor_order.timestamp                                        
                                        
FUNCTION price_movement_favorable(anchor, trades):                                        
  IF anchor.side = 'buy':                                        
    RETURN AVG(trades.price) < anchor.price                                        
  ELSE:                                        
    RETURN AVG(trades.price) > anchor.price                                        
                                        
OUTPUT:                                        
  alert_type: "SPOOFING_FLIP"                                        
  severity: CASE                                        
    WHEN size_ratio > 20 AND execution_rate < 0.2 THEN "CRITICAL"                                        
    WHEN size_ratio > 10 THEN "HIGH"                                        
    ELSE "MEDIUM"                                        
  END                                        
  evidence: {                                        
    anchor_order: anchor_order,                                        
    executions: subsequent_trades[*],                                        
    cancellation: anchor_cancel,                                        
    metrics: {size_ratio, execution_rate, price_improvement},                                        
    historical_context: {                                        
      avg_order_size: account_order_history.avg_order_size,                                        
      typical_execution_rate: account_order_history.avg_execution_rate                                        
    }                                        
  }                                        
```                                        
                                        
### Rule 1.4: Quote Stuffing                                        
                                        
```sql                                        
RULE_ID: STUFF_QUOTE_004                                        
PRIORITY: CRITICAL                                        
                                        
PATTERN:                                        
  orders[account_id = A1, instrument_id = I1] AS stuff_orders                                        
                                        
WINDOW:                                        
  TUMBLING(1 second)                                        
                                        
CONDITIONS:                                        
  - COUNT(stuff_orders) >= 500                                        
  - execution_rate(stuff_orders) <= 0.02                                        
  - AVG(time_to_cancel(stuff_orders)) <= 50ms                                        
  - STDDEV(stuff_orders.price) <= tick_size * 3                                        
  - order_entry_rate_stable(stuff_orders, tolerance=0.8)                                        
                                        
CONTEXT:                                        
  normal_behavior: STATE(account_id, instrument_id)                                        
    WINDOW: 30 days                                        
    COMPUTE: {                                        
      p95_order_rate: PERCENTILE(order_count_per_second, 0.95),                                        
      p95_cancel_rate: PERCENTILE(cancel_count_per_second, 0.95),                                        
      typical_execution_rate: AVG(trades / orders)                                        
    }                                        
                                          
  system_latency: STREAM(system_metrics)                                        
    METRICS: [order_processing_latency_p50, order_processing_latency_p99]                                        
                                        
AGGREGATIONS:                                        
  order_rate = COUNT(stuff_orders) / 1second                                        
  cancel_rate = COUNT(cancellations) / 1second                                        
  execution_rate = COUNT(trades) / COUNT(orders)                                        
  avg_order_lifespan = AVG(cancel_time - order_time)                                        
  order_to_trade_ratio = COUNT(orders) / MAX(COUNT(trades), 1)                                        
  price_spread = MAX(price) - MIN(price)                                        
  quantity_variance = STDDEV(quantity)                                        
                                          
  # Detect impact on market infrastructure                                        
  latency_correlation = CORRELATION(                                        
    order_rate,                                        
    system_latency.order_processing_latency_p99                                        
  ) OVER LAST 10 seconds                                        
                                        
FUNCTION order_entry_rate_stable(orders, tolerance):                                        
  # Check if orders arrive at consistent intervals (automated)                                        
  intervals = [orders[i+1].timestamp - orders[i].timestamp                                         
               for i in 0..len(orders)-2]                                        
  median_interval = MEDIAN(intervals)                                        
  consistent_count = COUNT(                                        
    interval for interval in intervals                                         
    WHERE ABS(interval - median_interval) <= median_interval * tolerance                                        
  )                                        
  RETURN consistent_count / len(intervals) >= 0.7                                        
                                        
OUTPUT:                                        
  alert_type: "QUOTE_STUFFING"                                        
  severity: CASE                                        
    WHEN order_rate > 1000 AND latency_correlation > 0.5 THEN "CRITICAL"                                        
    WHEN order_rate > 500 THEN "HIGH"                                        
    ELSE "MEDIUM"                                        
  END                                        
  evidence: {                                        
    order_count: COUNT(stuff_orders),                                        
    order_rate: order_rate,                                        
    execution_rate: execution_rate,                                        
    avg_lifespan: avg_order_lifespan,                                        
    order_to_trade_ratio: order_to_trade_ratio,                                        
    system_impact: {                                        
      latency_correlation: latency_correlation,                                        
      latency_increase: system_latency.order_processing_latency_p99 - baseline_latency                                        
    },                                        
    sample_orders: SAMPLE(stuff_orders, 20)                                        
  }                                        
  immediate_action: IF severity = "CRITICAL" THEN "THROTTLE_ACCOUNT" ELSE "MONITOR"                                        
```                                        
                                        
### Rule 1.5: Iceberg Layering                                        
                                        
```sql                                        
RULE_ID: LAYER_ICEBERG_005                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  SEQ(                                        
    orders[account_id = A1, instrument_id = I1, side = S1] AS iceberg_orders                                        
      WHERE count(*) >= 3                                        
      AND all(order_type IN ('iceberg', 'hidden'))                                        
      AND all(hidden_quantity > displayed_quantity * 10),                                        
                                            
    orders[account_id = A1, instrument_id = I1, side = S1] AS visible_layer                                        
      WHERE count(*) >= 3                                        
      AND all(order_type = 'limit')                                        
      AND all(hidden_quantity IS NULL OR hidden_quantity = 0),                                        
                                            
    trades[account_id = A1, instrument_id = I1, side = opposite(S1)] AS execution,                                        
                                            
    cancellations[order_id IN (iceberg_orders.order_id + visible_layer.order_id)] AS cancels                                        
      WHERE count(*) / (iceberg_orders.count() + visible_layer.count()) >= 0.7                                        
  )                                        
                                        
WINDOW:                                        
  iceberg_orders: SLIDING(120 seconds)                                        
  visible_layer: OVERLAPS(iceberg_orders) WITHIN(120 seconds)                                        
  execution: WITHIN(30 seconds) AFTER visible_layer                                        
  cancels: WITHIN(180 seconds) AFTER execution                                        
                                        
CONDITIONS:                                        
  - iceberg_orders.total_hidden_quantity >= visible_layer.total_quantity * 5                                        
  - price_levels_coordinated(iceberg_orders, visible_layer)                                        
  - cancellation_synchronization(cancels, threshold=5000ms)                                        
  - execution.quantity * 10 <= iceberg_orders.total_hidden_quantity                                        
                                        
CONTEXT:                                        
  market_depth: STREAM(order_book)                                        
    PARTITION BY instrument_id                                        
    KEEP DEPTH 10                                        
                                        
AGGREGATIONS:                                        
  total_hidden_liquidity = SUM(iceberg_orders.hidden_quantity)                                        
  total_visible_liquidity = SUM(visible_layer.displayed_quantity) +                                         
                           SUM(iceberg_orders.displayed_quantity)                                        
  hidden_to_visible_ratio = total_hidden_liquidity / total_visible_liquidity                                        
                                          
  actual_depth = total_hidden_liquidity + total_visible_liquidity                                        
  apparent_depth = total_visible_liquidity                                        
  deception_ratio = actual_depth / apparent_depth                                        
                                          
  cancel_synchronization = STDDEV([c.timestamp for c in cancels])                                        
                                        
FUNCTION price_levels_coordinated(ice_orders, vis_orders):                                        
  # Check if visible orders create ladder above/below iceberg                                        
  ice_best_price = IF ice_orders[0].side = 'buy'                                         
    THEN MAX(ice_orders.price)                                         
    ELSE MIN(ice_orders.price)                                        
                                          
  vis_prices = SORT(vis_orders.price)                                        
                                          
  IF ice_orders[0].side = 'buy':                                        
    # Visible orders should be above iceberg buy orders                                        
    RETURN MIN(vis_prices) > ice_best_price                                        
  ELSE:                                        
    # Visible orders should be below iceberg sell orders                                          
    RETURN MAX(vis_prices) < ice_best_price                                        
                                        
FUNCTION cancellation_synchronization(cancels, threshold):                                        
  IF COUNT(cancels) <= 1:                                        
    RETURN false                                        
  cancel_times = [c.timestamp for c in cancels]                                        
  time_spread = MAX(cancel_times) - MIN(cancel_times)                                        
  RETURN time_spread <= threshold                                        
                                        
OUTPUT:                                        
  alert_type: "LAYERING_ICEBERG"                                        
  severity: CASE                                        
    WHEN deception_ratio > 20 THEN "HIGH"                                        
    WHEN deception_ratio > 10 THEN "MEDIUM"                                        
    ELSE "LOW"                                        
  END                                        
  evidence: {                                        
    iceberg_orders: iceberg_orders[*],                                        
    visible_layer: visible_layer[*],                                        
    execution: execution,                                        
    cancellations: cancels[*],                                        
    metrics: {                                        
      hidden_to_visible_ratio,                                        
      deception_ratio,                                        
      cancel_synchronization                                        
    },                                        
    market_depth_snapshot: market_depth.snapshot(execution.timestamp)                                        
  }                                        
```                                        
                                        
---                                        
                                        
## Category 2: Wash Trading and Self-Matching                                        
                                        
### Rule 2.1: Same Account Wash Trading                                        
                                        
```sql                                        
RULE_ID: WASH_SAME_ACCOUNT_001                                        
PRIORITY: CRITICAL                                        
                                        
PATTERN:                                        
  trades[instrument_id = I1] AS wash_trade                                        
  WHERE                                         
    beneficial_owner(buy_account_id) = beneficial_owner(sell_account_id)                                        
    OR parent_account(buy_account_id) = parent_account(sell_account_id)                                        
    OR session_correlation(buy_account_id, sell_account_id) > 0.9                                        
                                        
WINDOW:                                        
  CONTINUOUS                                        
                                        
CONDITIONS:                                        
  - wash_trade.buy_account_id != wash_trade.sell_account_id  # Different sub-accounts                                        
  - economic_benefit(wash_trade) < min_threshold  # No real benefit                                        
  - NOT exempt_market_making(wash_trade)  # Not legitimate MM activity                                        
  - pattern_repetition(account_pair, instrument_id) >= 3 OVER 24 hours                                        
                                        
CONTEXT:                                        
  account_relationships: REF_DATA(accounts)                                        
    GRAPH: [beneficial_owner, parent_account, linked_accounts]                                        
                                          
  session_data: STATE(sessions)                                        
    WINDOW: 24 hours                                        
    KEYS: [ip_address, device_fingerprint, login_pattern]                                        
                                          
  exempt_firms: REF_DATA(market_makers)                                        
    WHERE status = 'registered'                                        
                                        
AGGREGATIONS:                                        
  wash_count_24h = COUNT(*) OVER 24 hours                                        
    PARTITION BY beneficial_owner, instrument_id                                        
                                          
  wash_volume_24h = SUM(quantity * price) OVER 24 hours                                        
    PARTITION BY beneficial_owner, instrument_id                                        
                                          
  wash_percentage = wash_volume_24h / total_trading_volume_24h                                        
                                        
FUNCTION beneficial_owner(account_id):                                        
  RETURN LOOKUP(account_relationships, account_id).beneficial_owner_id                                        
                                        
FUNCTION parent_account(account_id):                                        
  RETURN LOOKUP(account_relationships, account_id).parent_account_id                                        
                                        
FUNCTION session_correlation(acc1, acc2):                                        
  sess1 = session_data[acc1]                                        
  sess2 = session_data[acc2]                                        
                                          
  ip_match = (sess1.ip_address = sess2.ip_address) ? 0.5 : 0                                        
  device_match = (sess1.device_fingerprint = sess2.device_fingerprint) ? 0.3 : 0                                        
  timing_match = timing_correlation(sess1.activity_times, sess2.activity_times) * 0.2                                        
                                          
  RETURN ip_match + device_match + timing_match                                        
                                        
FUNCTION economic_benefit(trade):                                        
  # Check if there's real economic change                                        
  fees = trade.buy_side_fees + trade.sell_side_fees                                        
  price_difference = ABS(trade.price - fair_market_value(trade.instrument_id, trade.timestamp))                                        
                                          
  # True economic benefit would exceed fees and price deviation                                        
  net_benefit = price_difference - fees                                        
                                          
  RETURN net_benefit                                        
                                        
FUNCTION exempt_market_making(trade):                                        
  buy_mm = trade.buy_firm_id IN exempt_firms                                        
  sell_mm = trade.sell_firm_id IN exempt_firms                                        
                                          
  # Both sides MM or one side with capacity = market_maker                                        
  RETURN (buy_mm AND sell_mm) OR                                         
         (trade.buy_capacity = 'market_maker' AND buy_mm) OR                                        
         (trade.sell_capacity = 'market_maker' AND sell_mm)                                        
                                        
FUNCTION pattern_repetition(account_pair, instrument):                                        
  RETURN COUNT(trades)                                         
    WHERE trades.beneficial_owner_match = true                                        
    AND trades.instrument_id = instrument                                        
    OVER LAST 24 hours                                        
                                        
OUTPUT:                                        
  alert_type: "WASH_TRADE_SAME_OWNER"                                        
  severity: CASE                                        
    WHEN wash_percentage > 0.2 THEN "CRITICAL"  # >20% of volume                                        
    WHEN wash_count_24h > 10 THEN "HIGH"                                        
    WHEN wash_count_24h > 3 THEN "MEDIUM"                                        
    ELSE "LOW"                                        
  END                                        
  evidence: {                                        
    trade: wash_trade,                                        
    relationship: {                                        
      buy_account: wash_trade.buy_account_id,                                        
      sell_account: wash_trade.sell_account_id,                                        
      beneficial_owner: beneficial_owner(wash_trade.buy_account_id),                                        
      relationship_type: relationship_type(wash_trade.buy_account_id, wash_trade.sell_account_id)                                        
    },                                        
    pattern: {                                        
      count_24h: wash_count_24h,                                        
      volume_24h: wash_volume_24h,                                        
      percentage_of_volume: wash_percentage                                        
    },                                        
    session_correlation: session_correlation(wash_trade.buy_account_id, wash_trade.sell_account_id)                                        
  }                                        
  regulatory_report: FORMAT_SAR(evidence)  # Suspicious Activity Report                                        
```                                        
                                        
### Rule 2.2: Cross-Account Wash Trading                                        
                                        
```sql                                        
RULE_ID: WASH_CROSS_ACCOUNT_002                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  trades[instrument_id = I1] AS potential_wash                                        
  HAVING                                        
    match_frequency(buy_account_id, sell_account_id, instrument_id) > 0.6                                        
    OVER SLIDING(7 days)                                        
                                        
WINDOW:                                        
  CONTINUOUS with LOOKBACK 30 days                                        
                                        
CONDITIONS:                                        
  - account_relationship_exists(buy_account_id, sell_account_id)                                        
  - price_discovery_absent(buy_account_id, sell_account_id, instrument_id)                                        
  - timing_pattern_systematic(buy_account_id, sell_account_id)                                        
  - volume_ratio_suspicious(buy_account_id, sell_account_id, instrument_id)                                        
                                        
CONTEXT:                                        
  account_graph: GRAPH_STATE(accounts)                                        
    RELATIONSHIPS: [                                        
      shared_beneficial_owner,                                        
      common_address,                                        
      common_ip_range,                                        
      common_bank_account,                                        
      corporate_affiliation,                                        
      family_relationship                                        
    ]                                        
    UPDATE: DAILY                                        
                                          
  trading_patterns: STATE(account_pairs)                                        
    WINDOW: 90 days                                        
    METRICS: [                                        
      total_trades_together,                                        
      total_trades_apart,                                        
      match_frequency,                                        
      price_variance,                                        
      time_pattern_score                                        
    ]                                        
                                        
AGGREGATIONS:                                        
  match_frequency_7d = COUNT(trades WHERE buy_account = A1 AND sell_account = A2) /                                        
                       COUNT(trades WHERE buy_account = A1 OR sell_account = A2)                                        
    OVER LAST 7 days                                        
                                          
  match_frequency_30d = COUNT(trades WHERE buy_account = A1 AND sell_account = A2) /                                        
                        COUNT(trades WHERE buy_account = A1 OR sell_account = A2)                                        
    OVER LAST 30 days                                        
                                          
  price_variance = STDDEV(price)                                         
    WHERE buy_account = A1 AND sell_account = A2                                        
    OVER LAST 30 days                                        
                                          
  market_price_variance = STDDEV(price)                                        
    WHERE instrument_id = I1                                        
    OVER LAST 30 days                                        
                                          
  time_of_day_pattern = ENTROPY(HOUR(timestamp))                                        
    WHERE buy_account = A1 AND sell_account = A2                                        
                                        
FUNCTION account_relationship_exists(acc1, acc2):                                        
  paths = GRAPH_QUERY(                                        
    START: acc1,                                        
    END: acc2,                                        
    MAX_DEPTH: 3,                                        
    GRAPH: account_graph                                        
  )                                        
  RETURN COUNT(paths) > 0                                        
                                        
FUNCTION price_discovery_absent(acc1, acc2, instrument):                                        
  # True price discovery would show variance similar to market                                        
  pair_variance = price_variance(acc1, acc2, instrument)                                        
  market_variance = market_price_variance(instrument)                                        
                                          
  # If pair trades at more consistent prices than market, suspicious                                        
  RETURN pair_variance < market_variance * 0.3                                        
                                        
FUNCTION timing_pattern_systematic(acc1, acc2):                                        
  trades_together = SELECT * FROM trades                                         
    WHERE buy_account = acc1 AND sell_account = acc2                                        
    OVER LAST 30 days                                        
                                          
  # Check for regular time intervals                                        
  intervals = [trades[i+1].timestamp - trades[i].timestamp                                         
               for i in 0..len(trades)-2]                                        
                                          
  # High consistency in timing suggests automation/coordination                                        
  interval_cv = STDDEV(intervals) / AVG(intervals)                                        
                                          
  # Check for specific time-of-day patterns                                        
  hour_distribution = HISTOGRAM(HOUR(t.timestamp) for t in trades_together)                                        
  hour_entropy = ENTROPY(hour_distribution)                                        
                                          
  # Low entropy = concentrated in specific hours = suspicious                                        
  # High interval consistency = suspicious                                        
  RETURN (interval_cv < 0.3) OR (hour_entropy < 2.0)                                        
                                        
FUNCTION volume_ratio_suspicious(acc1, acc2, instrument):                                        
  # What fraction of each account's trading in this instrument is with each other?                                        
  acc1_total = SUM(quantity) WHERE account = acc1 AND instrument = instrument                                        
  acc2_total = SUM(quantity) WHERE account = acc2 AND instrument = instrument                                        
  together_total = SUM(quantity)                                         
    WHERE buy_account = acc1 AND sell_account = acc2 AND instrument = instrument                                        
                                          
  acc1_ratio = together_total / acc1_total                                        
  acc2_ratio = together_total / acc2_total                                        
                                          
  # If >40% of their trading is with each other, suspicious                                        
  RETURN MAX(acc1_ratio, acc2_ratio) > 0.4                                        
                                        
OUTPUT:                                        
  alert_type: "WASH_TRADE_CROSS_ACCOUNT"                                        
  severity: CASE                                        
    WHEN match_frequency_7d > 0.8 AND account_relationship_exists THEN "CRITICAL"                                        
    WHEN match_frequency_30d > 0.7 THEN "HIGH"                                        
    WHEN match_frequency_30d > 0.6 THEN "MEDIUM"                                        
    ELSE "LOW"                                        
  END                                        
  evidence: {                                        
    trade: potential_wash,                                        
    account_pair: {                                        
      buy_account: potential_wash.buy_account_id,                                        
      sell_account: potential_wash.sell_account_id,                                        
      relationship: GRAPH_QUERY(buy_account_id, sell_account_id, max_depth=3),                                        
      relationship_strength: relationship_score(buy_account_id, sell_account_id)                                        
    },                                        
    pattern_analysis: {                                        
      match_frequency_7d,                                        
      match_frequency_30d,                                        
      price_variance_ratio: price_variance / market_price_variance,                                        
      timing_score: timing_pattern_systematic(buy_account_id, sell_account_id),                                        
      volume_concentration: volume_ratio_suspicious(buy_account_id, sell_account_id, instrument_id)                                        
    },                                        
    historical_trades: SELECT * FROM trades                                        
      WHERE buy_account = buy_account_id AND sell_account = sell_account_id                                        
      ORDER BY timestamp DESC                                        
      LIMIT 50                                        
  }                                        
```                                        
                                        
### Rule 2.3: Marker Timing Wash Trading                                        
                                        
```sql                                        
RULE_ID: WASH_MARKER_TIMING_003                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  SEQ(                                        
    trades[buy_account_id = A1, sell_account_id = A2, instrument_id = I1] AS wash_sequence                                        
    WHERE count(*) >= 50                                        
  )                                        
                                        
WINDOW:                                        
  SLIDING(4 hours)                                        
                                        
CONDITIONS:                                        
  - price_consistency(wash_sequence.price[], tolerance=0.0001) >= 0.95                                        
  - accounts_related(A1, A2)                                        
  - market_price_moved(I1, wash_sequence) >= 0.01  # Market moved 1%+                                        
  - external_participation_rate(wash_sequence) < 0.05  # <5% outside trades                                        
                                        
CONTEXT:                                        
  market_prices: STREAM(trades)                                        
    PARTITION BY instrument_id                                        
    WINDOW: SLIDING(4 hours)                                        
                                        
AGGREGATIONS:                                        
  wash_trade_count = COUNT(wash_sequence)                                        
  wash_trade_price = MODE(wash_sequence.price)  # Most common price                                        
  wash_price_stddev = STDDEV(wash_sequence.price)                                        
  wash_price_cv = wash_price_stddev / AVG(wash_sequence.price)                                        
                                          
  market_trade_count = COUNT(market_prices)                                        
  market_price_start = FIRST(market_prices.price)                                        
  market_price_end = LAST(market_prices.price)                                        
  market_price_stddev = STDDEV(market_prices.price)                                        
  market_price_cv = market_price_stddev / AVG(market_prices.price)                                        
                                          
  price_stability_ratio = wash_price_cv / MAX(market_price_cv, 0.0001)                                        
  market_movement = ABS(market_price_end - market_price_start) / market_price_start                                        
                                        
FUNCTION price_consistency(prices[], tolerance):                                        
  mode_price = MODE(prices)                                        
  consistent_count = COUNT(p for p in prices WHERE ABS(p - mode_price) <= tolerance)                                        
  RETURN consistent_count / LEN(prices)                                        
                                        
FUNCTION accounts_related(acc1, acc2):                                        
  RETURN LOOKUP(account_graph, acc1, acc2).relationship_exists                                        
                                        
FUNCTION market_price_moved(instrument, wash_seq):                                        
  start_price = LOOKUP(market_prices,                                         
    timestamp = MIN(wash_seq.timestamp) - 30 seconds,                                        
    aggregation = 'vwap'                                        
  )                                        
  end_price = LOOKUP(market_prices,                                        
    timestamp = MAX(wash_seq.timestamp) + 30 seconds,                                        
    aggregation = 'vwap'                                        
  )                                        
  RETURN ABS(end_price - start_price) / start_price                                        
                                        
FUNCTION external_participation_rate(wash_seq):                                        
  # Trades in same instrument NOT between A1 and A2                                        
  wash_times = [w.timestamp for w in wash_seq]                                        
  time_window = (MIN(wash_times), MAX(wash_times))                                        
                                          
  external_trades = SELECT COUNT(*) FROM trades                                        
    WHERE instrument_id = wash_seq[0].instrument_id                                        
    AND timestamp BETWEEN time_window                                        
    AND NOT (buy_account_id = A1 AND sell_account_id = A2)                                        
                                          
  total_trades = external_trades + COUNT(wash_seq)                                        
                                          
  RETURN external_trades / total_trades                                        
                                        
OUTPUT:                                        
  alert_type: "WASH_TRADE_MARKER_TIMING"                                        
  severity: CASE                                        
    WHEN price_stability_ratio < 0.1 AND market_movement > 0.02 THEN "CRITICAL"                                        
    WHEN price_stability_ratio < 0.2 THEN "HIGH"                                        
    ELSE "MEDIUM"                                        
  END                                        
  evidence: {                                        
    wash_trades: wash_sequence[*],                                        
    wash_statistics: {                                        
      count: wash_trade_count,                                        
      consistent_price: wash_trade_price,                                        
      price_cv: wash_price_cv                                        
    },                                        
    market_context: {                                        
      market_count: market_trade_count,                                        
      market_movement: market_movement,                                        
      market_cv: market_price_cv,                                        
      stability_ratio: price_stability_ratio                                        
    },                                        
    external_participation: external_participation_rate(wash_sequence),                                        
    account_relationship: GRAPH_QUERY(A1, A2, max_depth=2)                                        
  }                                        
  visualization: CHART_PRICE_TIME_SERIES(                                        
    instrument_id: I1,                                        
    window: wash_sequence.time_window,                                        
    highlight: wash_sequence.timestamps,                                        
    annotations: ["Market moving while wash trades at constant price"]                                        
  )                                        
```                                        
                                        
---                                        
                                        
## Category 3: Front Running                                        
                                        
### Rule 3.1: Classic Front Running                                        
                                        
```sql                                        
RULE_ID: FRONT_CLASSIC_001                                        
PRIORITY: CRITICAL                                        
                                        
PATTERN:                                        
  SEQ(                                        
    order[account_type = 'proprietary', firm_id = F1] AS prop_order                                        
      WHERE quantity >= 100,                                        
                                            
    order[account_type IN ('retail', 'institutional'),                                         
          firm_id = F1,                                        
          side = prop_order.side,                                        
          instrument_id = prop_order.instrument_id] AS customer_order                                        
      WHERE quantity >= prop_order.quantity * 10,                                        
                                            
    trades[order_id = prop_order.order_id] AS prop_execution                                        
  )                                        
                                        
WINDOW:                                        
  customer_order: WITHIN(60 seconds) AFTER prop_order                                        
  prop_execution: WITHIN(300 seconds) AFTER prop_order                                        
                                        
CONDITIONS:                                        
  - prop_order.timestamp < customer_order.timestamp                                        
  - prop_execution.timestamp < customer_order.fill_timestamp                                        
  - price_impact(customer_order) >= 0.001  # 0.1%                                        
  - prop_profit(prop_execution, customer_order) >= 1000                                        
  - NOT legitimate_principal_trading(prop_order, customer_order)                                        
                                        
CONTEXT:                                        
  firm_structure: REF_DATA(firms)                                        
    FIELDS: [customer_desks, proprietary_desks, information_barriers]                                        
                                          
  trader_assignments: REF_DATA(traders)                                        
    FIELDS: [desk_assignment, customer_access_level]                                        
                                          
  order_routing: STATE(orders)                                        
    FIELDS: [submission_path, handling_trader, visibility_scope]                                        
                                        
AGGREGATIONS:                                        
  prop_avg_fill_price = VWAP(prop_execution)                                        
  customer_avg_fill_price = VWAP(customer_order.fills)                                        
                                          
  price_impact = ABS(customer_avg_fill_price - pre_order_mid_price) / pre_order_mid_price                                        
                                          
  prop_profit = (customer_avg_fill_price - prop_avg_fill_price) *                                         
                prop_execution.total_quantity *                                        
                IF(prop_order.side = 'buy', 1, -1)                                        
                                          
  prop_profit_bps = (prop_profit / (prop_avg_fill_price * prop_execution.total_quantity)) * 10000                                        
                                        
FUNCTION price_impact(customer_order):                                        
  pre_order_mid = (best_bid + best_offer) / 2                                         
    AT TIME customer_order.timestamp - 1 second                                        
                                          
  post_execution_mid = (best_bid + best_offer) / 2                                        
    AT TIME customer_order.last_fill_timestamp                                        
                                          
  RETURN ABS(post_execution_mid - pre_order_mid) / pre_order_mid                                        
                                        
FUNCTION prop_profit(prop_exec, cust_order):                                        
  IF prop_exec.side = 'buy':                                        
    # Prop bought, then customer bought (pushing price up)                                        
    benefit = cust_order.avg_fill_price - prop_exec.avg_fill_price                                        
  ELSE:                                        
    # Prop sold, then customer sold (pushing price down)                                        
    benefit = prop_exec.avg_fill_price - cust_order.avg_fill_price                                        
                                          
  RETURN benefit * prop_exec.total_quantity                                        
                                        
FUNCTION legitimate_principal_trading(prop_ord, cust_ord):                                        
  # Check if this is legitimate principal trading (firm commitment)                                        
  # vs front running                                        
                                          
  # Legitimate if:                                        
  # 1. Firm committed to price before customer order                                        
  # 2. Customer got price improvement vs market                                        
  # 3. Documented as principal capacity                                        
                                          
  price_improvement = IF prop_ord.side = 'buy'                                        
    THEN cust_ord.avg_fill_price < prop_ord.price                                        
    ELSE cust_ord.avg_fill_price > prop_ord.price                                        
                                          
  documented_principal = cust_ord.capacity = 'principal' AND                                         
                        prop_ord.capacity = 'principal'                                        
                                          
  pre_committed = prop_ord.price_commitment_time < cust_ord.submission_time                                        
                                          
  RETURN price_improvement AND documented_principal AND pre_committed                                        
                                        
OUTPUT:                                        
  alert_type: "FRONT_RUNNING_CLASSIC"                                        
  severity: CASE                                        
    WHEN prop_profit > 10000 OR prop_profit_bps > 50 THEN "CRITICAL"                                        
    WHEN prop_profit > 5000 OR prop_profit_bps > 25 THEN "HIGH"                                        
    WHEN prop_profit > 1000 OR prop_profit_bps > 10 THEN "MEDIUM"                                        
    ELSE "LOW"                                        
  END                                        
  evidence: {                                        
    proprietary_order: {                                        
      order: prop_order,                                        
      execution: prop_execution,                                        
      avg_price: prop_avg_fill_price,                                        
      trader: LOOKUP(traders, prop_order.trader_id)                                        
    },                                        
    customer_order: {                                        
      order: customer_order,                                        
      avg_price: customer_avg_fill_price,                                        
      handling_trader: LOOKUP(traders, customer_order.handling_trader_id)                                        
    },                                        
    financial_impact: {                                        
      prop_profit_dollars: prop_profit,                                        
      prop_profit_bps: prop_profit_bps,                                        
      customer_price_impact_bps: price_impact * 10000                                        
    },                                        
    timing: {                                        
      prop_order_time: prop_order.timestamp,                                        
      customer_order_time: customer_order.timestamp,                                        
      time_delta_ms: customer_order.timestamp - prop_order.timestamp,                                        
      prop_execution_time: prop_execution.timestamp                                        
    },                                        
    information_barrier_check: {                                        
      barrier_exists: CHECK_BARRIER(prop_order.desk, customer_order.desk),                                        
      trader_access: CHECK_ACCESS(prop_order.trader_id, customer_order.order_id)                                        
    }                                        
  }                                        
  regulatory_report: true                                        
  immediate_escalation: IF severity IN ('CRITICAL', 'HIGH')                                        
```                                        
                                        
### Rule 3.2: Shadow Trading                                        
                                        
```sql                                        
RULE_ID: FRONT_SHADOW_002                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  trades[account_id = A1, instrument_id = I1] AS shadow_trade                                        
  FOLLOWED BY                                        
  trades[account_id = A2, instrument_id = I1] AS large_trade                                        
  WHERE                                        
    large_trade.quantity >= shadow_trade.quantity * 5                                        
    AND large_trade.side = shadow_trade.side                                        
                                        
WINDOW:                                        
  large_trade: WITHIN(5 minutes) AFTER shadow_trade                                        
                                        
CONDITIONS:                                        
  - accounts_potentially_related(A1, A2)                                        
  - pattern_consistency_30d(A1, A2, I1) >= 0.7                                        
  - shadow_profitability(shadow_trade, large_trade) >= 500                                        
  - large_trade_materiality(large_trade) >= 0.02  # 2% of ADV                                        
                                        
CONTEXT:                                        
  account_relationships: GRAPH_STATE(accounts)                                        
    RELATIONSHIPS: [                                        
      family_member,                                        
      business_associate,                                        
      common_address,                                        
      common_phone,                                        
      common_email_domain,                                        
      common_employer                                        
    ]                                        
    UPDATE_FREQUENCY: WEEKLY                                        
                                          
  historical_pattern: STATE(account_pairs, instrument)                                        
    WINDOW: 90 days                                        
    METRICS: [                                        
      shadow_count,                                        
      shadow_success_rate,                                        
      correlation_coefficient,                                        
      timing_consistency                                        
    ]                                        
                                          
  instrument_liquidity: REF_DATA(instruments)                                        
    FIELDS: [average_daily_volume, typical_trade_size]                                        
                                        
AGGREGATIONS:                                        
  # Historical pattern analysis                                        
  shadow_count_30d = COUNT(*) WHERE                                        
    account_id = A1 FOLLOWED BY account_id = A2                                        
    WITHIN 5 minutes                                        
    OVER LAST 30 days                                        
                                          
  pattern_consistency_30d = shadow_count_30d /                                         
    COUNT(trades WHERE account_id = A2) OVER LAST 30 days                                        
                                          
  correlation_score = CORRELATION(                                        
    [t1.timestamp for t1 in trades WHERE account_id = A1],                                        
    [t2.timestamp for t2 in trades WHERE account_id = A2]                                        
  ) OVER LAST 90 days                                        
                                          
  timing_precision = 1 / STDDEV(                                        
    [t2.timestamp - t1.timestamp                                         
     for (t1, t2) in paired_trades(A1, A2)]                                        
  ) OVER LAST 30 days                                        
                                          
  # Current trade analysis                                        
  price_movement = ABS(large_trade.price - shadow_trade.price) / shadow_trade.price                                        
                                          
  shadow_profit = (large_trade.avg_price - shadow_trade.price) *                                         
                  shadow_trade.quantity *                                        
                  IF(shadow_trade.side = 'buy', 1, -1)                                        
                                          
  large_trade_pct_adv = large_trade.quantity /                                         
                        instrument_liquidity.average_daily_volume                                        
                                        
FUNCTION accounts_potentially_related(acc1, acc2):                                        
  # Check multiple dimensions of potential relationship                                        
  direct_relationship = GRAPH_QUERY_EXISTS(                                        
    START: acc1,                                        
    END: acc2,                                        
    MAX_DEPTH: 2,                                        
    GRAPH: account_relationships                                        
  )                                        
                                          
  # Indirect relationship signals                                        
  trading_venue_overlap = JACCARD_SIMILARITY(                                        
    acc1.trading_venues_set,                                        
    acc2.trading_venues_set                                        
  )                                        
                                          
  time_zone_match = acc1.typical_trading_hours OVERLAPS acc2.typical_trading_hours                                        
                                          
  instrument_overlap = JACCARD_SIMILARITY(                                        
    acc1.traded_instruments_30d,                                        
    acc2.traded_instruments_30d                                        
  )                                        
                                          
  relationship_score = (                                        
    direct_relationship * 0.6 +                                        
    (trading_venue_overlap > 0.7) * 0.2 +                                        
    time_zone_match * 0.1 +                                        
    (instrument_overlap > 0.5) * 0.1                                        
  )                                        
                                          
  RETURN relationship_score > 0.3                                        
                                        
FUNCTION shadow_profitability(shadow, large):                                        
  # Calculate profit if shadow trade position closed at large trade price                                        
  IF shadow.side = 'buy':                                        
    profit = (large.price - shadow.price) * shadow.quantity                                        
  ELSE:                                        
    profit = (shadow.price - large.price) * shadow.quantity                                        
                                          
  RETURN profit                                        
                                        
FUNCTION large_trade_materiality(trade):                                        
  adv = LOOKUP(instrument_liquidity, trade.instrument_id).average_daily_volume                                        
  RETURN trade.quantity / adv                                        
                                        
OUTPUT:                                        
  alert_type: "FRONT_RUNNING_SHADOW"                                        
  severity: CASE                                        
    WHEN pattern_consistency_30d > 0.8 AND correlation_score > 0.7 THEN "CRITICAL"                                        
    WHEN pattern_consistency_30d > 0.7 THEN "HIGH"                                        
    WHEN shadow_count_30d > 5 THEN "MEDIUM"                                        
    ELSE "LOW"                                        
  END                                        
  evidence: {                                        
    shadow_trade: shadow_trade,                                        
    large_trade: large_trade,                                        
    accounts: {                                        
      shadow_account: A1,                                        
      large_account: A2,                                        
      relationship: GRAPH_QUERY(A1, A2, max_depth=3),                                        
      relationship_score: accounts_potentially_related(A1, A2),                                        
      relationship_type: classify_relationship(A1, A2)                                        
    },                                        
    pattern_analysis: {                                        
      shadow_count_30d,                                        
      shadow_count_90d: COUNT(shadow_trades OVER 90 days),                                        
      pattern_consistency: pattern_consistency_30d,                                        
      correlation_score,                                        
      timing_precision,                                        
      avg_time_gap: AVG(large_trade.time - shadow_trade.time) OVER 30 days                                        
    },                                        
    financial_metrics: {                                        
      shadow_profit,                                        
      price_movement_pct: price_movement * 100,                                        
      large_trade_pct_adv: large_trade_pct_adv * 100                                        
    },                                        
    timing: {                                        
      shadow_timestamp: shadow_trade.timestamp,                                        
      large_timestamp: large_trade.timestamp,                                        
      gap_ms: large_trade.timestamp - shadow_trade.timestamp                                        
    }                                        
  }                                        
  investigation_priority: CASE                                        
    WHEN relationship_score > 0.7 THEN "IMMEDIATE"                                        
    WHEN pattern_consistency_30d > 0.75 THEN "HIGH"                                        
    ELSE "NORMAL"                                        
  END                                        
```                                        
                                        
---                                        
                                        
## Category 4: Marking the Close                                        
                                        
### Rule 4.1: Banging the Close                                        
                                        
```sql                                        
RULE_ID: MANIP_BANGING_CLOSE_001                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  trades[instrument_id = I1, account_id = A1] AS closing_trades                                        
  WHERE                                        
    TIME_IN_WINDOW(timestamp, market_close - 5 minutes, market_close)                                        
                                        
WINDOW:                                        
  DAILY aligned with market_close                                        
                                        
CONDITIONS:                                        
  - closing_volume_concentration(closing_trades) >= 0.20  # >=20% of close volume                                        
  - closing_price_impact(closing_trades) >= 0.003  # >=0.3%                                        
  - pattern_repetition_monthly(A1, I1) >= 3  # Repeated behavior                                        
  - directional_consistency(closing_trades) >= 0.9  # Same direction                                        
  - NOT end_of_day_rebalancing(A1)  # Not legitimate index rebalancing                                        
                                        
CONTEXT:                                        
  market_schedule: REF_DATA(trading_calendar)                                        
    FIELDS: [market_open, market_close, auction_times]                                        
                                          
  closing_auction: STREAM(auction_data)                                        
    PARTITION BY instrument_id, date                                        
    FIELDS: [imbalance, indicative_price, auction_volume]                                        
                                          
  account_profile: REF_DATA(accounts)                                        
    FIELDS: [account_type, investment_strategy, index_tracking]                                        
                                          
  daily_volume: AGGREGATE(trades)                                        
    PARTITION BY instrument_id, date                                        
    COMPUTE: SUM(quantity) AS total_daily_volume                                        
                                        
AGGREGATIONS:                                        
  closing_window_volume = SUM(closing_trades.quantity)                                        
  total_closing_volume = SUM(all_trades.quantity)                                         
    WHERE TIME_IN_WINDOW(timestamp, market_close - 5 minutes, market_close)                                        
                                          
  closing_volume_concentration = closing_window_volume / total_closing_volume                                        
                                          
  pre_close_mid = (best_bid + best_offer) / 2                                        
    AT TIME market_close - 5 minutes - 1 second                                        
                                          
  actual_close_price = official_close_price(I1, date)                                        
                                          
  closing_price_impact = ABS(actual_close_price - pre_close_mid) / pre_close_mid                                        
                                          
  account_price_benefit = (actual_close_price - pre_close_mid) *                                         
    IF(PREDOMINANT_SIDE(closing_trades) = 'buy', 1, -1)                                        
                                          
  # Temporal distribution analysis                                        
  time_distribution = HISTOGRAM(                                        
    MINUTE_OF_HOUR(closing_trades.timestamp),                                        
    bins = [0, 1, 2, 3, 4, 5]  # Last 5 minutes                                        
  )                                        
                                          
  temporal_concentration = MAX(time_distribution) / SUM(time_distribution)                                        
                                        
FUNCTION closing_volume_concentration(trades):                                        
  account_volume = SUM(trades.quantity)                                        
  total_volume = SUM(all_trades.quantity) WHERE                                        
    TIME_IN_WINDOW(timestamp, market_close - 5 minutes, market_close) AND                                        
    instrument_id = trades[0].instrument_id                                        
                                          
  RETURN account_volume / total_volume                                        
                                        
FUNCTION closing_price_impact(trades):                                        
  pre_close_mid = GET_MID_PRICE(                                        
    instrument_id = trades[0].instrument_id,                                        
    timestamp = market_close - 5 minutes - 1 second                                        
  )                                        
                                          
  actual_close = GET_CLOSE_PRICE(                                        
    instrument_id = trades[0].instrument_id,                                        
    date = DATE(trades[0].timestamp)                                        
  )                                        
                                          
  RETURN ABS(actual_close - pre_close_mid) / pre_close_mid                                        
                                        
FUNCTION pattern_repetition_monthly(account, instrument):                                        
  # Count days in past 30 where similar pattern occurred                                        
  RETURN COUNT(DISTINCT date) WHERE                                        
    closing_volume_concentration(account, instrument, date) >= 0.15 AND                                        
    date BETWEEN CURRENT_DATE - 30 days AND CURRENT_DATE                                        
                                        
FUNCTION directional_consistency(trades):                                        
  buy_volume = SUM(quantity WHERE side = 'buy')                                        
  sell_volume = SUM(quantity WHERE side = 'sell')                                        
  total_volume = buy_volume + sell_volume                                        
                                          
  RETURN MAX(buy_volume, sell_volume) / total_volume                                        
                                        
FUNCTION end_of_day_rebalancing(account):                                        
  profile = LOOKUP(account_profile, account)                                        
                                          
  # Legitimate if:                                        
  # - Index fund with documented rebalancing                                        
  # - Consistent with investment mandate                                        
  # - Distributed across many securities (not focused)                                        
                                          
  is_index_fund = profile.investment_strategy = 'index_tracking'                                        
  rebalances_broadly = COUNT(DISTINCT instrument_id)                                         
    WHERE account_id = account                                         
    AND TIME_IN_WINDOW(timestamp, market_close - 5 minutes, market_close) > 10                                        
                                          
  RETURN is_index_fund AND rebalances_broadly                                        
                                        
OUTPUT:                                        
  alert_type: "MARKING_CLOSE"                                        
  severity: CASE                                        
    WHEN closing_volume_concentration > 0.3 AND closing_price_impact > 0.5 THEN "CRITICAL"                                        
    WHEN closing_volume_concentration > 0.25 OR closing_price_impact > 0.4 THEN "HIGH"                                        
    WHEN pattern_repetition_monthly >= 5 THEN "HIGH"                                        
    ELSE "MEDIUM"                                        
  END                                        
  evidence: {                                        
    trades: closing_trades[*],                                        
    volume_analysis: {                                        
      account_volume: closing_window_volume,                                        
      total_closing_volume,                                        
      concentration_pct: closing_volume_concentration * 100,                                        
      pct_of_daily_volume: (closing_window_volume / total_daily_volume) * 100                                        
    },                                        
    price_analysis: {                                        
      pre_close_mid,                                        
      actual_close_price,                                        
      price_impact_pct: closing_price_impact * 100,                                        
      price_impact_bps: closing_price_impact * 10000,                                        
      direction: IF(account_price_benefit > 0, "FAVORABLE", "UNFAVORABLE"),                                        
      account_benefit_estimate: account_price_benefit * SUM(account_positions)                                        
    },                                        
    temporal_analysis: {                                        
      time_distribution,                                        
      temporal_concentration,                                        
      last_minute_pct: time_distribution[4] / SUM(time_distribution) * 100                                        
    },                                        
    pattern_history: {                                        
      repetition_count_30d: pattern_repetition_monthly(A1, I1),                                        
      similar_dates: SELECT date, concentration, price_impact                                         
        FROM historical_close_patterns                                        
        WHERE account_id = A1 AND instrument_id = I1                                        
        ORDER BY date DESC                                        
        LIMIT 10                                        
    },                                        
    account_context: {                                        
      account_type: LOOKUP(account_profile, A1).account_type,                                        
      total_portfolio_value: GET_PORTFOLIO_VALUE(A1),                                        
      position_in_security: GET_POSITION(A1, I1)                                        
    }                                        
  }                                        
  related_alerts: FIND_RELATED_ALERTS(                                        
    account_id = A1,                                        
    alert_types = ['MARKING_CLOSE', 'SETTLEMENT_MANIP', 'BENCHMARK_FIX'],                                        
    lookback = 30 days                                        
  )                                        
```                                        
                                        
### Rule 4.2: Auction Imbalance Exploitation                                        
                                        
```sql                                        
RULE_ID: MANIP_AUCTION_IMBALANCE_001                                        
PRIORITY: HIGH                                        
                                        
PATTERN:                                        
  orders[instrument_id = I1, account_id = A1] AS late_orders                                        
  WHERE                                        
    TIME_IN_WINDOW(                                        
      timestamp,                                        
      auction_cutoff - 10 seconds,                                        
      auction_cutoff                                        
    )                                        
                                        
WINDOW:                                        
  PER_AUCTION (multiple per day: open, close, intraday)                                        
                                        
CONDITIONS:                                        
  - late_order_timing_score(late_orders) >= 0.9  # Concentrated in last 10s                                        
  - imbalance_influence(late_orders) >= 0.05  # >=5% of imbalance                                        
  - order_cancellation_post_auction(late_orders) >= 0.7  # 70%+ cancelled                                        
  - pattern_repetition_weekly(A1, I1) >= 3                                        
  - profit_from_auction_price(A1, I1) >= 1000                                        
                                        
CONTEXT:                                        
  auction_schedule: REF_DATA(auctions)                                        
    FIELDS: [auction_time, cutoff_time, auction_type]                                        
                                          
  auction_imbalance: STREAM(auction_data)                                        
    UPDATE: REAL_TIME during auction period                                        
    FIELDS: [                                        
      current_imbalance_quantity,                                        
      current_imbalance_side,                                        
      indicative_match_price,                                        
      paired_quantity,                                        
      imbalance_direction                                        
    ]                                        
                                          
  order_lifecycle: STATE(orders)                                        
    TRACK: [submission, modification, cancellation, execution]                                        
                                        
AGGREGATIONS:                                        
  # Timing analysis                                        
  late_order_timing_score = COUNT(orders WHERE                                         
    timestamp > auction_cutoff - 10 seconds                                        
  ) / COUNT(orders WHERE                                        
    timestamp > auction_cutoff - 60 seconds                                        
  )                                        
                                          
  avg_submission_second = AVG(                                        
    auction_cutoff - order.timestamp FOR order IN late_orders                                        
  )                                        
                                          
  # Imbalance impact                                        
  account_order_quantity = SUM(late_orders.quantity)                                        
                                          
  # Get imbalance BEFORE account's orders                                        
  pre_order_imbalance = GET_IMBALANCE(                                        
    instrument_id = I1,                                        
    timestamp = MIN(late_orders.timestamp) - 1 second                                        
  )                                        
                                          
  # Get imbalance AFTER account's orders                                        
  post_order_imbalance = GET_IMBALANCE(                                        
    instrument_id = I1,                                        
    timestamp = MAX(late_orders.timestamp) + 1 second                                        
  )                                        
                                          
  imbalance_influence = ABS(post_order_imbalance.quantity - pre_order_imbalance.quantity) /                                        
                       MAX(ABS(post_order_imbalance.quantity), 1)                                        
                                          
  # Post-auction behavior                                        
  cancelled_orders = COUNT(orders WHERE                                        
    order_id IN late_orders.order_id AND                                        
    order_state = 'cancelled' AND                                        
    cancel_time < auction_time + 60 seconds                                        
  )                                        
                                          
  order_cancellation_post_auction = cancelled_orders / COUNT(late_orders)                                        
                                          
  # Profitability                                        
  indicative_price_pre_orders = pre_order_imbalance.indicative_price                                        
  final_auction_price = GET_AUCTION_RESULT(I1, auction_time).price                                        
                                          
  account_contra_positions = GET_POSITIONS(A1, I1)                                        
    AT TIME auction_cutoff - 60 seconds                                        
                                          
  price_movement_benefit = (final_auction_price - indicative_price_pre_orders) *                                        
    account_contra_positions.quantity *                                        
    IF(account_contra_positions.side = 'long', 1, -1)                                        
                                        
FUNCTION late_order_timing_score(orders):                                        
  # Measure how concentrated orders are in the last 10 seconds                                        
  total_orders = COUNT(orders)                                        
  very_late_orders = COUNT(orders WHERE                                         
    auction_cutoff - timestamp <= 10                                        
  )                                        
                                          
  RETURN very_late_orders / total_orders                                        
                                        
FUNCTION imbalance_influence(orders):                                        
  pre_imbalance = GET_IMBALANCE_BEFORE(orders)                                        
  post_imbalance = GET_IMBALANCE_AFTER(orders)                                        
                                          
  # Calculate how much the imbalance changed                                        
  change = ABS(post_imbalance.quantity - pre_imbalance.quantity)                                        
                                          
  # Normalize by total imbalance size                                        
  RETURN change / MAX(ABS(post_imbalance.quantity), 1)                                        
                                        
FUNCTION order_cancellation_post_auction(orders):                                        
  cancelled = COUNT(orders WHERE                                         
    order_state = 'cancelled' AND                                        
    cancel_time BETWEEN auction_time AND auction_time + 60 seconds                                        
  )                                        
                                          
  RETURN cancelled / COUNT(orders)                                        
                                        
FUNCTION pattern_repetition_weekly(account, instrument):                                        
  RETURN COUNT(DISTINCT auction_id) WHERE                                        
    late_order_timing_score >= 0.8 AND                                        
    auction_time BETWEEN CURRENT_TIME - 7 days AND CURRENT_TIME                                        
                                        
FUNCTION profit_from_auction_price(account, instrument):                                        
  # Estimate profit from price movement caused by imbalance manipulation                                        
  RETURN price_movement_benefit  # Computed in aggregations                                        
                                        
OUTPUT:                                        
  alert_type: "AUCTION_IMBALANCE_MANIPULATION"                                        
  severity: CASE                                        
    WHEN imbalance_influence > 0.15 AND price_movement_benefit > 10000 THEN "CRITICAL"                                        
    WHEN imbalance_influence > 0.10 OR price_movement_benefit > 5000 THEN "HIGH"                                        
    WHEN pattern_repetition_weekly >= 5 THEN "HIGH"                                        
    ELSE "MEDIUM"                                        
  END                                        
  evidence: {                                        
    orders: late_orders[*],                                        
    timing_analysis: {                                        
      late_order_timing_score,                                        
      avg_submission_second,                                        
      latest_order_submission: MAX(auction_cutoff - order.timestamp),                                        
      order_clustering: HISTOGRAM(auction_cutoff - order.timestamp, bins=10)                                        
    },                                        
    imbalance_analysis: {                                        
      pre_order_imbalance: {                                        
        quantity: pre_order_imbalance.quantity,                                        
        side: pre_order_imbalance.side,                                        
        indicative_price: pre_order_imbalance.indicative_price                                        
      },                                        
      post_order_imbalance: {                                        
        quantity: post_order_imbalance.quantity,                                        
        side: post_order_imbalance.side,                                        
        indicative_price: post_order_imbalance.indicative_price                                        
      },                                        
      account_contribution: account_order_quantity,                                        
      imbalance_influence_pct: imbalance_influence * 100                                        
    },                                        
    auction_result: {                                        
      final_price: final_auction_price,                                        
      final_volume: GET_AUCTION_RESULT(I1, auction_time).volume,                                        
      price_vs_indicative: final_auction_price - indicative_price_pre_orders                                        
    },                                        
    post_auction_behavior: {                                        
      cancellation_rate: order_cancellation_post_auction * 100,                                        
      cancelled_within_60s: cancelled_orders,                                        
      avg_time_to_cancel: AVG(cancel_time - auction_time) FOR cancelled orders                                        
    },                                        
    profitability: {                                        
      estimated_benefit: price_movement_benefit,                                        
      contra_position_size: account_contra_positions.quantity,                                        
      price_impact_bps: (                                        
        (final_auction_price - indicative_price_pre_orders) /                                         
        indicative_price_pre_orders                                        
      ) * 10000                                        
    },                                        
    pattern_history: {                                        
      repetition_count_7d: pattern_repetition_weekly(A1, I1),                                        
      similar_auctions: SELECT * FROM historical_auction_patterns                                        
        WHERE account_id = A1 AND instrument_id = I1                                        
        ORDER BY auction_time DESC                                        
        LIMIT 10                                        
    }                                        
  }                                        
  visualization: CHART_AUCTION_TIMELINE(                                        
    instrument_id: I1,                                        
    auction_time: auction_time,                                        
    highlight_orders: late_orders,                                        
    imbalance_evolution: imbalance_timeline                                        
  )                                        
```                                        
                                        
---                                        
                                        
## Technical Implementation Patterns                                        
                                        
### Stream Processing Framework                                        
                                        
```sql                                        
-- Core CEP Engine Configuration                                        
                                        
DEFINE STREAM orders_stream (                                        
  order_id UUID PRIMARY KEY,                                        
  timestamp TIMESTAMP(9) EVENT_TIME,                                        
  WATERMARK FOR timestamp AS timestamp - INTERVAL '100' MILLISECOND                                        
) WITH (                                        
  'connector' = 'kafka',                                        
  'topic' = 'orders',                                        
  'properties.bootstrap.servers' = 'kafka:9092',                                        
  'scan.startup.mode' = 'latest-offset',                                        
  'format' = 'avro-confluent'                                        
);                                        
                                        
DEFINE STREAM trades_stream (                                        
  trade_id UUID PRIMARY KEY,                                        
  timestamp TIMESTAMP(9) EVENT_TIME,                                        
  WATERMARK FOR timestamp AS timestamp - INTERVAL '50' MILLISECOND                                        
) WITH (                                        
  'connector' = 'kafka',                                        
  'topic' = 'trades',                                        
  'format' = 'avro-confluent'                                        
);                                        
                                        
-- State Store Configuration                                        
DEFINE STATE_STORE account_state (                                        
  account_id STRING PRIMARY KEY,                                        
  metrics MAP<STRING, DOUBLE>,                                        
  last_update TIMESTAMP                                        
) WITH (                                        
  'backend' = 'rocksdb',                                        
  'checkpoint.interval' = '30s',                                        
  'state.ttl' = '30d'                                        
);                                        
                                        
-- Pattern Matching Configuration                                        
SET 'table.exec.mini-batch.enabled' = 'true';                                        
SET 'table.exec.mini-batch.allow-latency' = '1s';                                        
SET 'table.exec.mini-batch.size' = '5000';                                        
SET 'table.optimizer.agg-phase-strategy' = 'TWO_PHASE';                                        
```                                        
                                        
### Partitioning Strategy                                        
                                        
```sql                                        
-- Partition by account for stateful rules                                        
PARTITION BY account_id                                        
  -- Enables co-location of account's orders, trades, state                                        
                                          
-- Partition by instrument for market-wide patterns                                        
PARTITION BY instrument_id                                        
  -- Enables co-location of all activity in a security                                        
                                        
-- Composite partitioning for cross-entity rules                                        
PARTITION BY HASH(account_id, instrument_id) MOD parallelism                                        
  -- Distributes load while maintaining related events together                                        
```                                        
                                        
### Window Semantics                                        
                                        
```sql                                        
-- Sliding Window (for continuous patterns)                                        
OVER (                                        
  PARTITION BY account_id, instrument_id                                        
  ORDER BY timestamp                                        
  RANGE BETWEEN INTERVAL '60' SECOND PRECEDING AND CURRENT ROW                                        
)                                        
                                        
-- Tumbling Window (for discrete period analysis)                                        
TUMBLE(timestamp, INTERVAL '1' SECOND)                                        
                                        
-- Session Window (for burst detection)                                        
SESSION(timestamp, INTERVAL '5' SECOND)                                        
                                        
-- Hop Window (for overlapping analysis)                                        
HOP(timestamp, INTERVAL '10' SECOND, INTERVAL '60' SECOND)                                        
  -- 60s window, sliding every 10s                                        
```                                        
                                        
### Performance Optimizations                                        
                                        
```sql                                        
-- Materialized view for frequently accessed reference data                                        
CREATE MATERIALIZED VIEW instrument_metrics AS                                        
SELECT                                        
  instrument_id,                                        
  AVG(volume) as avg_volume,                                        
  STDDEV(price) as price_volatility,                                        
  COUNT(*) as trade_count                                        
FROM trades_stream                                        
GROUP BY                                         
  instrument_id,                                        
  TUMBLE(timestamp, INTERVAL '1' DAY);                                        
                                        
-- Pre-aggregation for baseline computation                                        
CREATE TABLE account_baselines WITH (                                        
  'connector' = 'jdbc',                                        
  'url' = 'jdbc:postgresql://postgres:5432/surveillance',                                        
  'table-name' = 'account_baselines'                                        
) AS                                        
SELECT                                        
  account_id,                                        
  instrument_id,                                        
  PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY order_size) as p95_size,                                        
  AVG(orders_per_minute) as avg_rate                                        
FROM account_activity                                        
GROUP BY account_id, instrument_id;                                        
                                        
-- Index strategy for graph queries                                        
CREATE INDEX ON accounts USING GIN(related_accounts);                                        
CREATE INDEX ON accounts(beneficial_owner_id, account_id);                                        
CREATE INDEX ON trades(timestamp DESC, instrument_id, account_id);                                        
```                                        
                                        
                                      
                    
                    
# CEP Rule Definitions                    
                    
## Category 1: Layering and Spoofing (continued)                    
                    
### Rule 1.6: Cross-Venue Layering                    
                    
```sql                    
RULE_ID: LAYER_CROSS_VENUE_006                    
                    
PATTERN:                    
  orders[account_id = A1, venue_id = V1, side = S1] AS venue1_orders                    
    WHERE count(*) >= 3,                    
  trades[account_id = A1, venue_id = V2, side = opposite(S1)] AS venue2_trades,                    
  cancellations[order_id IN venue1_orders.order_id] AS cancels                    
    WHERE count(*) / venue1_orders.count() >= 0.8                    
                    
WINDOW: venue2_trades WITHIN 500ms AFTER venue1_orders                    
                    
CONDITIONS:                    
  V1 != V2                    
  AND beneficial_owner(A1) SAME ACROSS venues                    
  AND time_correlation(venue1_orders, venue2_trades) < 500ms                    
  AND venue1_orders.total_quantity / venue2_trades.quantity >= 3                    
                    
AGGREGATIONS:                    
  cross_venue_latency = AVG(venue2_trades.timestamp - venue1_orders.timestamp)                    
  cancel_sync = STDDEV(cancels.timestamp)                    
                    
OUTPUT: alert_type='CROSS_VENUE_LAYER', severity=HIGH                    
```                    
                    
### Rule 1.7: Time-Based Spoofing                    
                    
```sql                    
RULE_ID: SPOOF_TIME_BASED_007                    
                    
PATTERN:                    
  orders[account_id = A1, instrument_id = I1] AS spoof_orders                    
    WHERE timestamp BETWEEN period_end - 10s AND period_end - 1s,                    
  cancellations[order_id IN spoof_orders.order_id]                    
    WHERE timestamp < period_end                    
                    
WINDOW: PER_PERIOD [close, auction, settlement]                    
                    
CONDITIONS:                    
  spoof_orders.quantity >= 2 * recent_avg_size(A1, I1)                    
  AND cancellation_rate >= 0.8                    
  AND timing_pattern_frequency(A1, period_type) >= 0.6 OVER 30 days                    
                    
AGGREGATIONS:                    
  avg_cancel_lead_time = AVG(period_end - cancel.timestamp)                    
  size_vs_normal = spoof_orders.avg_quantity / baseline_avg_size                    
                    
OUTPUT: alert_type='TIME_BASED_SPOOF', severity=CRITICAL                    
```                    
                    
### Rule 1.8: Momentum Ignition                    
                    
```sql                    
RULE_ID: LAYER_MOMENTUM_008                    
                    
PATTERN:                    
  SEQ(                    
    orders[account_id = A1, side = S1] AS layer,                    
    price_move[instrument_id = I1, direction = S1, magnitude >= 0.005],                    
    trades[account_id != A1, side = S1] AS momentum WHERE count(*) >= 10,                    
    cancellations[order_id IN layer.order_id] WHERE count(*) >= 0.7 * layer.count()                    
  )                    
                    
WINDOW: momentum WITHIN 30s AFTER price_move                    
                    
CONDITIONS:                    
  price_move THROUGH technical_level(I1)                    
  AND momentum.total_volume >= layer.total_quantity * 2                    
  AND stop_loss_triggers(I1) > 0                    
                    
AGGREGATIONS:                    
  breakout_magnitude = price_move.magnitude                    
  follower_volume = SUM(momentum.quantity)                    
  cancel_speed = AVG(cancellation.timestamp - price_move.timestamp)                    
                    
OUTPUT: alert_type='MOMENTUM_IGNITION', severity=CRITICAL                    
```                    
                    
### Rule 1.9: Ping Orders                    
                    
```sql                    
RULE_ID: PROBE_PING_009                    
                    
PATTERN:                    
  orders[account_id = A1, instrument_id = I1] AS pings                    
    WHERE count(*) >= 20                    
                    
WINDOW: SLIDING 5s                    
                    
CONDITIONS:                    
  AVG(pings.quantity) <= 10                    
  AND COUNT(DISTINCT pings.price) >= 20                    
  AND pings.price SPAN >= 20 * tick_size                    
  AND execution_rate(pings) < 0.05                    
  AND AVG(time_to_cancel) <= 100ms                    
                    
AGGREGATIONS:                    
  price_levels_probed = COUNT(DISTINCT price)                    
  avg_order_size = AVG(quantity)                    
  cancel_rate = COUNT(cancelled) / COUNT(*)                    
                    
OUTPUT: alert_type='PING_PROBING', severity=MEDIUM                    
```                    
                    
### Rule 1.10: Cancellation Cascades                    
                    
```sql                    
RULE_ID: CASCADE_CANCEL_010                    
                    
PATTERN:                    
  SEQ(                    
    trade[account_id = A1, quantity <= 100] AS trigger,                    
    cancellations[account_id = A1] AS cascade WHERE count() >= 50                    
  )                    
                    
WINDOW: cascade WITHIN 10ms AFTER trigger                    
                    
CONDITIONS:                    
  cascade.timestamp - trigger.timestamp < 10ms                    
  AND cascade.total_quantity >= trigger.quantity * 50                    
  AND ALL(cancellations.order_state = 'open')                    
                    
AGGREGATIONS:                    
  cancel_count = COUNT(cascade)                    
  cancel_latency_p99 = PERCENTILE(cascade.timestamp - trigger.timestamp, 0.99)                    
  cancel_to_fill_ratio = cascade.count() / 1                    
                    
OUTPUT: alert_type='CANCEL_CASCADE', severity=HIGH                    
```                    
                    
## Category 2: Wash Trading (continued)                    
                    
### Rule 2.4: HF Wash Pattern                    
                    
```sql                    
RULE_ID: WASH_HF_004                    
                    
PATTERN:                    
  trades[buy_account = A1, sell_account = A2] AS wash_burst                    
    WHERE count(*) >= 100                    
                    
WINDOW: TUMBLING 1s, REPEAT hourly                    
                    
CONDITIONS:                    
  beneficial_owner(A1) = beneficial_owner(A2)                    
  AND time_pattern_regular(wash_burst) > 0.8                    
  AND external_participation(I1, time_window) < 0.05                    
                    
AGGREGATIONS:                    
  burst_count = COUNT(wash_burst)                    
  burst_frequency = COUNT(DISTINCT hour) OVER 24h                    
  time_regularity = 1 / STDDEV(inter_burst_interval)                    
                    
OUTPUT: alert_type='HF_WASH_PATTERN', severity=HIGH                    
```                    
                    
### Rule 2.5: Cross-Venue Wash                    
                    
```sql                    
RULE_ID: WASH_CROSS_VENUE_005                    
                    
PATTERN:                    
  trades[account = A1, venue = V1, side = 'buy'] AS buy_leg,                    
  trades[account = A2, venue = V2, side = 'sell'] AS sell_leg                    
                    
WINDOW: sell_leg WITHIN 100ms OF buy_leg                    
                    
CONDITIONS:                    
  beneficial_owner(A1) = beneficial_owner(A2)                    
  AND V1 != V2                    
  AND ABS(buy_leg.price - sell_leg.price) <= tick_size                    
  AND time_correlation >= 0.95 OVER 10 trades                    
                    
AGGREGATIONS:                    
  venue_pair_frequency = COUNT(*) OVER 24h                    
  time_sync = CORRELATION(buy_leg.timestamp, sell_leg.timestamp)                    
                    
OUTPUT: alert_type='CROSS_VENUE_WASH', severity=CRITICAL                    
```                    
                    
### Rule 2.6: Pre-Arranged Trading                    
                    
```sql                    
RULE_ID: PREARRANGED_006                    
                    
PATTERN:                    
  SEQ(                    
    order[account = A1, side = S1] AS order1,                    
    order[account = A2, side = opposite(S1)] AS order2                    
  )                    
                    
WINDOW: order2 WITHIN 5ms AFTER order1                    
                    
CONDITIONS:                    
  order1.quantity = order2.quantity                    
  AND order1.price = order2.price                    
  AND timing_precision(A1, A2) >= 0.95 OVER 20 trades                    
  AND order_time_gap < 5ms                    
                    
AGGREGATIONS:                    
  match_precision = COUNT(exact_matches) / COUNT(orders)                    
  avg_time_gap = AVG(order2.timestamp - order1.timestamp)                    
  quantity_match_rate = COUNT(quantity_exact_match) / COUNT(*)                    
                    
OUTPUT: alert_type='PREARRANGED', severity=CRITICAL                    
```                    
                    
### Rule 2.7: Volume Inflation Pre-Event                    
                    
```sql                    
RULE_ID: WASH_EVENT_INFLATION_007                    
                    
PATTERN:                    
  trades[beneficial_owner = B1] AS wash_trades                    
                    
WINDOW: event_date - 7d TO event_date                    
                    
CONDITIONS:                    
  event_type IN ('IPO', 'secondary_offering', 'index_add')                    
  AND volume_increase >= 10 * baseline_volume                    
  AND wash_characteristics(wash_trades) > 0.7                    
  AND price_variance < market_variance * 0.3                    
                    
AGGREGATIONS:                    
  volume_ratio = current_volume / baseline_volume                    
  wash_score = COMPOSITE(price_variance, match_frequency, timing_pattern)                    
                    
OUTPUT: alert_type='PRE_EVENT_INFLATION', severity=CRITICAL                    
```                    
                    
### Rule 2.8: Position Parking                    
                    
```sql                    
RULE_ID: PARKING_008                    
                    
PATTERN:                    
  SEQ(                    
    trade[buy_account = A1, sell_account = A2] AS initial,                    
    trade[buy_account = A2, sell_account = A1] AS reversal                    
  )                    
                    
WINDOW: reversal WITHIN 48h AFTER initial                    
                    
CONDITIONS:                    
  accounts_related(A1, A2)                    
  AND initial.quantity = reversal.quantity                    
  AND ABS(initial.price - reversal.price) <= 0.01 * initial.price                    
  AND no_external_trades(A2, I1) BETWEEN initial AND reversal                    
  AND round_trip_rate(A1, A2) >= 0.9 OVER 30d                    
                    
AGGREGATIONS:                    
  holding_period = reversal.timestamp - initial.timestamp                    
  price_difference = ABS(reversal.price - initial.price)                    
  round_trip_frequency = COUNT(*) OVER 30d                    
                    
OUTPUT: alert_type='POSITION_PARKING', severity=HIGH                    
```                    
                    
## Category 3: Front Running (continued)                    
                    
### Rule 3.3: Time-Proximity Front Running                    
                    
```sql                    
RULE_ID: FRONT_TIME_PROX_003                    
                    
PATTERN:                    
  SEQ(                    
    order[account = A1] AS front_order,                    
    order[account = A2, algo_indicator = true] AS algo_order                    
  )                    
                    
WINDOW: algo_order WITHIN 10s AFTER front_order AT algo_execution_time                    
                    
CONDITIONS:                    
  front_order.side = algo_order.side                    
  AND front_order.timestamp - algo_execution_time < 10s                    
  AND timing_precision(A1, algo_execution_time) >= 0.6 OVER 20 instances                    
  AND profit(front_order, algo_order.avg_fill) >= 500                    
                    
AGGREGATIONS:                    
  timing_precision = 1 / STDDEV(front_order.time - expected_algo_time)                    
  occurrence_count = COUNT(*) OVER 30d                    
  avg_profit = AVG(profit) OVER 30d                    
                    
OUTPUT: alert_type='TIME_PROXIMITY_FRONT', severity=HIGH                    
```                    
                    
### Rule 3.4: Parent Order Front Running                    
                    
```sql                    
RULE_ID: FRONT_PARENT_004                    
                    
PATTERN:                    
  SEQ(                    
    order[account = A1, quantity < 1000] AS accumulation WHERE count(*) >= 5,                    
    order[type = 'iceberg', refresh_event = true] AS iceberg_refresh                    
  )                    
                    
WINDOW: accumulation WITHIN 30s BEFORE iceberg_refresh                    
                    
CONDITIONS:                    
  accumulation.side = iceberg_refresh.side                    
  AND accumulation.total_quantity >= 1000                    
  AND pattern_repetition(A1, iceberg_parent_id) >= 5 OVER 30d                    
  AND position_reversal_post_execution(A1) >= 0.8                    
                    
AGGREGATIONS:                    
  accumulation_size = SUM(accumulation.quantity)                    
  timing_correlation = CORRELATION(accumulation.end_time, refresh.time)                    
                    
OUTPUT: alert_type='PARENT_ORDER_FRONT', severity=HIGH                    
```                    
                    
### Rule 3.5: News-Based Front Running                    
                    
```sql                    
RULE_ID: FRONT_NEWS_005                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument = I1] AS pre_news_trades,                    
    news_event[instrument = I1, materiality >= 'high'] AS news,                    
    trades[account = A1, side = opposite(pre_news_trades.side)] AS unwind                    
  )                    
                    
WINDOW:                     
  pre_news_trades: 1m TO 30m BEFORE news                    
  unwind: WITHIN 10m AFTER news                    
                    
CONDITIONS:                    
  pre_news_trades.volume >= 5 * baseline_volume(A1, I1)                    
  AND price_move(news) >= 0.02                    
  AND directional_accuracy(pre_news_trades, news) = 1.0                    
  AND unwind.quantity >= 0.7 * pre_news_trades.quantity                    
                    
AGGREGATIONS:                    
  pre_news_volume_ratio = pre_news_trades.volume / baseline_volume                    
  profit_estimate = (news.price_impact) * pre_news_trades.quantity                    
  pattern_frequency = COUNT(*) OVER 90d                    
                    
OUTPUT: alert_type='NEWS_FRONT_RUNNING', severity=CRITICAL                    
```                    
                    
### Rule 3.6: Block Trade Front Running                    
                    
```sql                    
RULE_ID: FRONT_BLOCK_006                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, quantity < 1000] AS front_trades,                    
    trade[type = 'block', quantity >= 10000] AS block                    
  )                    
                    
WINDOW: front_trades WITHIN 60s BEFORE block                    
                    
CONDITIONS:                    
  front_trades.side = block.side                    
  AND knowledge_inference(A1, block_negotiation) > 0.7                    
  AND front_trades.timestamp < block.print_timestamp                    
  AND profit(front_trades, block.price) >= 1000                    
                    
AGGREGATIONS:                    
  front_volume = SUM(front_trades.quantity)                    
  profit = (block.price - front_trades.avg_price) * front_volume * direction                    
  timing_gap = block.timestamp - MAX(front_trades.timestamp)                    
                    
OUTPUT: alert_type='BLOCK_FRONT_RUN', severity=CRITICAL                    
```                    
                    
### Rule 3.7: Derivative Front Running                    
                    
```sql                    
RULE_ID: FRONT_DERIVATIVE_007                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument = underlying(I1)] AS equity_trades,                    
    order[account = A2, instrument = I1, type = 'option'] AS option_order                    
  )                    
                    
WINDOW: equity_trades WITHIN 60s BEFORE option_order                    
                    
CONDITIONS:                    
  related_accounts(A1, A2) OR same_firm(A1, A2)                    
  AND equity_trades.quantity * delta(option_order) >= option_order.quantity * 0.8                    
  AND equity_trades.side = hedge_direction(option_order)                    
  AND pattern_frequency >= 5 OVER 30d                    
                    
AGGREGATIONS:                    
  delta_hedge_ratio = equity_trades.quantity / (option_order.quantity * delta)                    
  timing_consistency = 1 / STDDEV(equity_time - option_time) OVER 30d                    
                    
OUTPUT: alert_type='DERIVATIVE_FRONT_RUN', severity=HIGH                    
```                    
                    
### Rule 3.8: Internalization Front Running                    
                    
```sql                    
RULE_ID: FRONT_INTERNALIZATION_008                    
                    
PATTERN:                    
  SEQ(                    
    trade[account_type = 'proprietary', firm = F1] AS prop_trade,                    
    trade[account_type = 'customer', firm = F1, execution_type = 'internalized'] AS customer_trade                    
  )                    
                    
WINDOW: customer_trade WITHIN 5s AFTER prop_trade                    
                    
CONDITIONS:                    
  prop_trade.side = customer_trade.side                    
  AND prop_trade.price BETTER_THAN customer_trade.price BY >= 0.02                    
  AND customer_trade.venue = 'internal'                    
  AND pattern_frequency(F1) >= 3 OVER 7d                    
                    
AGGREGATIONS:                    
  price_differential = customer_trade.price - prop_trade.price                    
  firm_profit = price_differential * prop_trade.quantity                    
  internalization_rate = COUNT(internalized) / COUNT(customer_orders)                    
                    
OUTPUT: alert_type='INTERNALIZATION_FRONT', severity=CRITICAL                    
```                    
                    
### Rule 3.9: Inter-Desk Front Running                    
                    
```sql                    
RULE_ID: FRONT_INTER_DESK_009                    
                    
PATTERN:                    
  SEQ(                    
    order[desk = 'proprietary', firm = F1] AS prop_order,                    
    order[desk = 'customer', firm = F1] AS customer_order                    
  )                    
                    
WINDOW: customer_order WITHIN 30s AFTER prop_order                    
                    
CONDITIONS:                    
  prop_order.side = customer_order.side                    
  AND prop_order.instrument = customer_order.instrument                    
  AND information_barrier_breach(prop_desk, customer_desk)                    
  AND prop_order.quantity >= 100                    
  AND customer_order.quantity >= 1000                    
                    
AGGREGATIONS:                    
  desk_correlation = COUNT(*) OVER 30d / total_customer_orders                    
  avg_time_gap = AVG(customer_order.time - prop_order.time)                    
  profit = (customer_avg_fill - prop_avg_fill) * prop_quantity * direction                    
                    
OUTPUT: alert_type='INTER_DESK_FRONT', severity=CRITICAL                    
```                    
                    
## Category 4: Marking the Close (continued)                    
                    
### Rule 4.3: Settlement Price Manipulation                    
                    
```sql                    
RULE_ID: SETTLEMENT_MANIP_003                    
                    
PATTERN:                    
  trades[account = A1, instrument = underlying(derivative)] AS manip_trades                    
                    
WINDOW: settlement_time - 5m TO settlement_time                    
                    
CONDITIONS:                    
  derivative_position(A1) LARGE                    
  AND manip_trades.volume >= 0.15 * total_settlement_volume                    
  AND price_impact >= 0.003                    
  AND position_reversal WITHIN 1h POST settlement                    
                    
AGGREGATIONS:                    
  volume_concentration = manip_trades.volume / total_volume                    
  settlement_price_impact = ABS(settlement_price - pre_manip_mid) / pre_manip_mid                    
  derivative_pnl_benefit = derivative_position * settlement_price_impact                    
                    
OUTPUT: alert_type='SETTLEMENT_MANIP', severity=CRITICAL                    
```                    
                    
### Rule 4.4: Month-End Marking                    
                    
```sql                    
RULE_ID: MONTH_END_MARKING_004                    
                    
PATTERN:                    
  trades[account = A1, instrument = I1, date = month_end] AS marking_trades                    
                    
WINDOW: DAILY ON month_end                    
                    
CONDITIONS:                    
  marking_trades.volume >= 0.2 * daily_volume                    
  AND closing_price_deviation >= 0.01                    
  AND next_day_price_reversion >= 0.008                    
  AND pattern_frequency >= 3 OVER 6 months                    
  AND position_holding(A1, I1) LARGE                    
                    
AGGREGATIONS:                    
  month_end_deviation = (month_end_close - month_end_open) / month_end_open                    
  next_day_reversion = (next_day_close - month_end_close) / month_end_close                    
  marking_frequency = COUNT(month_ends) OVER 12 months                    
                    
OUTPUT: alert_type='MONTH_END_MARKING', severity=HIGH                    
```                    
                    
### Rule 4.5: Index Rebalancing Exploitation                    
                    
```sql                    
RULE_ID: INDEX_REBAL_EXPLOIT_005                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument = I1] AS accumulation,                    
    announcement[type = 'index_add', instrument = I1] AS announce,                    
    trades[account = A1, instrument = I1] AS liquidation                    
  )                    
                    
WINDOW:                    
  accumulation: 7d BEFORE announce                    
  liquidation: DURING rebalancing_period                    
                    
CONDITIONS:                    
  accumulation.side = 'buy'                    
  AND liquidation.side = 'sell'                    
  AND accumulation.quantity >= 100000                    
  AND liquidation.quantity >= 0.7 * accumulation.quantity                    
  AND timing_correlation_with_index_flows >= 0.8                    
                    
AGGREGATIONS:                    
  accumulation_size = SUM(accumulation.quantity)                    
  profit = (liquidation.avg_price - accumulation.avg_price) * liquidation.quantity                    
  rebalancing_timing_score = CORRELATION(liquidation.times, index_flow_times)                    
                    
OUTPUT: alert_type='INDEX_REBAL_EXPLOIT', severity=MEDIUM                    
```                    
                    
### Rule 4.6: Benchmark Fixing                    
                    
```sql                    
RULE_ID: BENCHMARK_FIX_006                    
                    
PATTERN:                    
  trades[account = A1, instrument = I1] AS fixing_trades                    
                    
WINDOW: snapshot_times +/- 30s                    
                    
CONDITIONS:                    
  fixing_trades.volume >= 0.5 * snapshot_volume                    
  AND price_at_snapshot DEVIATES >= 0.005 FROM pre_window_mid                    
  AND volume_concentration_at_snapshots >= 0.6                    
  AND pattern_at_fixing_times >= 5 OVER 30d                    
                    
AGGREGATIONS:                    
  snapshot_volume_share = fixing_trades.volume / total_snapshot_volume                    
  price_deviation_at_fix = ABS(snapshot_price - reference_price) / reference_price                    
  fixing_frequency = COUNT(fixing_days) OVER 30d                    
                    
OUTPUT: alert_type='BENCHMARK_FIXING', severity=HIGH                    
```                    
                    
### Rule 4.7: After-Hours Manipulation                    
                    
```sql                    
RULE_ID: AFTER_HOURS_MANIP_007                    
                    
PATTERN:                    
  trades[account = A1, instrument = I1, session = 'post_market'] AS ah_trades                    
                    
WINDOW: DAILY post_market_session                    
                    
CONDITIONS:                    
  ah_trades.volume <= 1000                    
  AND price_impact >= 0.02                    
  AND next_day_opening_reversion >= 0.015                    
  AND pattern_frequency >= 3 OVER 30d                    
                    
AGGREGATIONS:                    
  ah_volume = SUM(ah_trades.quantity)                    
  price_impact = ABS(ah_close - regular_close) / regular_close                    
  reversion = ABS(next_open - ah_close) / ah_close                    
                    
OUTPUT: alert_type='AFTER_HOURS_MANIP', severity=MEDIUM                    
```                    
                    
## Category 5: Pump and Dump                    
                    
### Rule 5.1: Coordinated Pump                    
                    
```sql                    
RULE_ID: PUMP_COORDINATED_001                    
                    
PATTERN:                    
  trades[instrument = I1, side = 'buy'] AS pump_trades                    
    WHERE COUNT(DISTINCT account_id) >= 10                    
                    
WINDOW: SLIDING 5m                    
                    
CONDITIONS:                    
  I1.market_cap <= 100M                    
  AND I1.daily_volume <= 1M                    
  AND pump_trades.time_clustering >= 0.8                    
  AND price_increase >= 0.10                    
  AND social_media_correlation(I1) >= 0.7                    
                    
AGGREGATIONS:                    
  account_count = COUNT(DISTINCT account_id)                    
  time_clustering = 1 / STDDEV(timestamp)                    
  price_increase = (current_price - start_price) / start_price                    
  coordinated_volume = SUM(pump_trades.quantity)                    
                    
OUTPUT: alert_type='COORDINATED_PUMP', severity=CRITICAL                    
```                    
                    
### Rule 5.2: Dump Detection                    
                    
```sql                    
RULE_ID: DUMP_002                    
                    
PATTERN:                    
  SEQ(                    
    price_increase[instrument = I1, magnitude >= 0.20] AS pump,                    
    trades[account IN pump_accumulators, side = 'sell'] AS dump                    
  )                    
                    
WINDOW: dump WITHIN 24h AFTER pump                    
                    
CONDITIONS:                    
  dump.quantity >= 0.7 * accumulated_during_pump                    
  AND price_decline >= 0.15                    
  AND dump.accounts = original_accumulators                    
                    
AGGREGATIONS:                    
  liquidation_rate = dump.quantity / accumulated_quantity                    
  price_decline = (pump_peak_price - current_price) / pump_peak_price                    
  dumper_overlap = JACCARD(pump_accounts, dump_accounts)                    
                    
OUTPUT: alert_type='PUMP_DUMP_COMPLETE', severity=CRITICAL                    
```                    
                    
### Rule 5.3: Churning                    
                    
```sql                    
RULE_ID: CHURNING_003                    
                    
PATTERN:                    
  trades[account = A1, managed_by = broker] AS churning_trades                    
                    
WINDOW: ROLLING 12 months                    
                    
CONDITIONS:                    
  account_turnover >= 100                    
  AND net_position_change <= 0.2 * total_traded_value                    
  AND commission_to_equity_ratio >= 0.10                    
  AND customer_initiated_rate < 0.2                    
                    
AGGREGATIONS:                    
  turnover_ratio = total_traded_value / account_equity                    
  net_position_delta = ABS(end_position - start_position) / total_traded_value                    
  commission_ratio = total_commissions / account_equity                    
                    
OUTPUT: alert_type='CHURNING', severity=HIGH                    
```                    
                    
### Rule 5.4: Painting the Tape                    
                    
```sql                    
RULE_ID: PAINTING_TAPE_004                    
                    
PATTERN:                    
  trades[buy_account IN related_set, sell_account IN related_set] AS tape_trades                    
                    
WINDOW: SLIDING 1h                    
                    
CONDITIONS:                    
  accounts_related(buy_accounts, sell_accounts)                    
  AND price_walking_pattern >= 0.8                    
  AND net_position_change < 0.1 * gross_volume                    
  AND external_participation < 0.2                    
                    
AGGREGATIONS:                    
  price_walk_score = REGRESSION_R2(price vs sequence_number)                    
  net_change = ABS(SUM(buys) - SUM(sells))                    
  circularity = COUNT(round_trips) / COUNT(trades)                    
                    
OUTPUT: alert_type='PAINTING_TAPE', severity=HIGH                    
```                    
                    
### Rule 5.5: Capping/Pegging                    
                    
```sql                    
RULE_ID: CAPPING_PEGGING_005                    
                    
PATTERN:                    
  orders[account = A1, instrument = I1, side = S1] AS capping_orders                    
                    
WINDOW: SLIDING 1h                    
                    
CONDITIONS:                    
  price_level_defense_count(price_threshold) >= 5                    
  AND cancel_on_retreat_rate >= 0.8                    
  AND option_interest(I1, strike_near_threshold) LARGE                    
  AND price_prevented_from_crossing >= 5 instances                    
                    
AGGREGATIONS:                    
  defense_count = COUNT(orders placed when price approaches threshold)                    
  cancel_on_retreat = COUNT(cancelled when price retreats) / defense_count                    
  threshold_proximity = STDDEV(order.price - threshold)                    
                    
OUTPUT: alert_type='CAPPING_PEGGING', severity=HIGH                    
```                    
                    
### Rule 5.6: Cross-Product Manipulation                    
                    
```sql                    
RULE_ID: CROSS_PRODUCT_MANIP_006                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument = I1] AS primary_trades,                    
    price_move[instrument = related(I1), correlation >= 0.9] AS related_move                    
  )                    
                    
WINDOW: related_move WITHIN 1m AFTER primary_trades                    
                    
CONDITIONS:                    
  position(A1, related_instrument) LARGE                    
  AND primary_trades.volume >= 0.1 * I1.daily_volume                    
  AND related_price_impact >= 0.005                    
  AND instruments_linked(I1, related_instrument)                    
                    
AGGREGATIONS:                    
  correlation_strength = CORRELATION(I1.price, related.price) OVER 30d                    
  related_position_benefit = related_position * related_price_impact                    
  manipulation_ratio = primary_cost / related_benefit                    
                    
OUTPUT: alert_type='CROSS_PRODUCT_MANIP', severity=HIGH                    
```                    
                    
## Category 6: Insider Trading                    
                    
### Rule 6.1: Pre-Announcement Trading                    
                    
```sql                    
RULE_ID: INSIDER_PRE_ANNOUNCE_001                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument = I1] AS pre_trades,                    
    announcement[instrument = I1, materiality >= 'high'] AS announce                    
  )                    
                    
WINDOW: pre_trades: 1d TO 5d BEFORE announce                    
                    
CONDITIONS:                    
  pre_trades.volume >= 5 * STDDEV(volume) + AVG(volume)                    
  AND price_move_post_announce >= 0.05                    
  AND direction_match(pre_trades.side, announce.direction) = 1.0                    
  AND NOT public_information_available                    
                    
AGGREGATIONS:                    
  volume_z_score = (pre_trades.volume - avg_volume) / stddev_volume                    
  profit_estimate = pre_trades.quantity * price_move_post_announce                    
  timing_suspicion = 1 / (announce.time - last_trade.time)                    
                    
OUTPUT: alert_type='PRE_ANNOUNCEMENT_TRADING', severity=CRITICAL                    
```                    
                    
### Rule 6.2: Family/Associate Trading                    
                    
```sql                    
RULE_ID: INSIDER_FAMILY_002                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = insider_account] AS insider_trade,                    
    trades[account = related_account] AS associate_trade,                    
    announcement AS announce                    
  )                    
                    
WINDOW:                    
  associate_trade WITHIN 48h AFTER insider_trade                    
  announce WITHIN 30d AFTER trades                    
                    
CONDITIONS:                    
  relationship(insider_account, related_account) IN (family, associate)                    
  AND insider_account.person IN company_insiders(I1)                    
  AND direction_match = 1.0                    
  AND combined_profit >= 5000                    
                    
AGGREGATIONS:                    
  relationship_strength = GRAPH_WEIGHT(insider_account, related_account)                    
  combined_volume = SUM(insider_trade.qty + associate_trade.qty)                    
  profit = combined_volume * price_move_post_announce                    
                    
OUTPUT: alert_type='INSIDER_TIPPEE', severity=CRITICAL                    
```                    
                    
### Rule 6.3: Tippee Chain                    
                    
```sql                    
RULE_ID: INSIDER_CHAIN_003                    
                    
PATTERN:                    
  SEQUENCE(                    
    trade[account = A1, role = 'insider'],                    
    trade[account = A2, related_to = A1],                    
    trade[account = A3, related_to = A2],                    
    announcement                    
  ) WHERE time_cascade <= 48h                    
                    
CONDITIONS:                    
  ALL_MATCH(side) = 1.0                    
  AND graph_path_exists(A1, A2, A3)                    
  AND cascade_timing < 48h                    
  AND announcement WITHIN 30d                    
                    
AGGREGATIONS:                    
  chain_length = COUNT(distinct_accounts_in_sequence)                    
  cascade_time = MAX(timestamp) - MIN(timestamp)                    
  network_profit = SUM(all_accounts.quantity * price_move)                    
                    
OUTPUT: alert_type='TIPPEE_CHAIN', severity=CRITICAL                    
```                    
                    
### Rule 6.4: Options-Heavy Insider                    
                    
```sql                    
RULE_ID: INSIDER_OPTIONS_004                    
                    
PATTERN:                    
  SEQ(                    
    orders[account = A1, instrument.type = 'option', moneyness < 0.05] AS option_orders,                    
    announcement[underlying = option_orders.underlying] AS announce                    
  )                    
                    
WINDOW: announce WITHIN 30d AFTER option_orders                    
                    
CONDITIONS:                    
  option_orders.volume >= 10 * baseline_volume(A1, options)                    
  AND option_orders.days_to_expiry <= 45                    
  AND options.out_of_money_distance >= 0.05                    
  AND price_move_post_announce BRINGS options IN_THE_MONEY                    
                    
AGGREGATIONS:                    
  option_volume_ratio = option_orders.volume / baseline_volume                    
  leverage_factor = option_orders.notional / option_orders.premium                    
  pnl_estimate = (intrinsic_value_post - premium_paid) * contracts                    
                    
OUTPUT: alert_type='INSIDER_OPTIONS', severity=CRITICAL                    
```                    
                    
### Rule 6.5: Blackout Trading                    
                    
```sql                    
RULE_ID: BLACKOUT_VIOLATION_005                    
                    
PATTERN:                    
  trades[account = A1, instrument = I1] AS blackout_trades                    
                    
WINDOW: DURING blackout_period                    
                    
CONDITIONS:                    
  account_person(A1) IN company_insiders(I1)                    
  AND current_date BETWEEN earnings_date - 15d AND earnings_date + 2d                    
  AND NOT pre_approved_10b5_1_plan(A1)                    
                    
AGGREGATIONS:                    
  blackout_violation_count = COUNT(blackout_trades)                    
  trade_value = SUM(quantity * price)                    
                    
OUTPUT: alert_type='BLACKOUT_VIOLATION', severity=CRITICAL                    
```                    
                    
### Rule 6.6: SPAC/Merger Insider                    
                    
```sql                    
RULE_ID: INSIDER_SPAC_006                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument.type IN ('SPAC', 'pre_merger')] AS pre_trades,                    
    announcement[type = 'merger', instrument = I1] AS merge_announce                    
  )                    
                    
WINDOW: pre_trades: 1d TO 14d BEFORE merge_announce                    
                    
CONDITIONS:                    
  pre_trades.volume >= 5 * baseline_volume                    
  AND price_jump_post_announce >= 0.15                    
  AND insider_connection(A1, merge_parties) > 0                    
                    
AGGREGATIONS:                    
  volume_anomaly = pre_trades.volume / baseline_volume                    
  price_jump = (post_announce_price - pre_trade_price) / pre_trade_price                    
  profit = pre_trades.quantity * price_jump * pre_trade_price                    
                    
OUTPUT: alert_type='SPAC_INSIDER_TRADING', severity=CRITICAL                    
```                    
                    
## Category 7: Cross-Market Manipulation                    
                    
### Rule 7.1: Equity-Derivative Arbitrage Manipulation                    
                    
```sql                    
RULE_ID: CROSS_EQUITY_DERIV_001                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument = equity] AS eq_trades,                    
    price_move[instrument = derivative(equity)] AS deriv_move                    
  )                    
                    
WINDOW: deriv_move WITHIN 60s AFTER eq_trades                    
                    
CONDITIONS:                    
  position(A1, derivative) >= 10000 * delta                    
  AND eq_trades.volume >= 0.05 * equity.daily_volume                    
  AND deriv_price_impact >= 0.003                    
  AND correlation(eq_price, deriv_price) >= 0.95                    
                    
AGGREGATIONS:                    
  deriv_position_pnl = position * deriv_price_impact                    
  eq_manipulation_cost = eq_trades.value * transaction_cost                    
  net_benefit = deriv_position_pnl - eq_manipulation_cost                    
                    
OUTPUT: alert_type='EQUITY_DERIV_MANIP', severity=HIGH                    
```                    
                    
### Rule 7.2: Cash-Futures Basis Manipulation                    
                    
```sql                    
RULE_ID: CROSS_CASH_FUTURES_002                    
                    
PATTERN:                    
  trades[account = A1, instrument IN basket_components] AS cash_trades                    
                    
WINDOW: futures_expiry - 1h TO futures_expiry                    
                    
CONDITIONS:                    
  futures_position(A1) LARGE                    
  AND cash_trades.impact_on_index >= 0.001                    
  AND basis_deviation >= 2 * historical_stddev                    
  AND reversal WITHIN 1h POST expiry                    
                    
AGGREGATIONS:                    
  basket_impact = WEIGHTED_SUM(cash_trades.impact, index_weights)                    
  basis_distortion = current_basis - fair_basis                    
  futures_pnl = futures_position * basis_distortion                    
                    
OUTPUT: alert_type='BASIS_MANIPULATION', severity=CRITICAL                    
```                    
                    
### Rule 7.3: ETF Arbitrage Manipulation                    
                    
```sql                    
RULE_ID: CROSS_ETF_ARB_003                    
                    
PATTERN:                    
  trades[account = A1, instrument IN etf_basket] AS basket_trades                    
                    
WINDOW: nav_calculation - 15m TO nav_calculation                    
                    
CONDITIONS:                    
  basket_trades.impact_on_nav >= 0.002                    
  AND etf_position(A1) >= 50000 shares                    
  AND tracking_difference widening >= 0.003                    
  AND basket_trades.systematic_pattern >= 0.7 OVER 10d                    
                    
AGGREGATIONS:                    
  nav_impact = SUM(basket_trades.impact * basket_weights)                    
  etf_arb_profit = etf_position * nav_impact                    
  pattern_consistency = COUNT(similar_days) / 10                    
                    
OUTPUT: alert_type='ETF_MANIP', severity=HIGH                    
```                    
                    
### Rule 7.4: Cross-Border Manipulation                    
                    
```sql                    
RULE_ID: CROSS_BORDER_004                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, venue = 'US', instrument = ADR] AS adr_trades,                    
    price_move[venue = 'HOME', instrument = ordinary_shares] AS home_move                    
  )                    
                    
WINDOW: home_market CLOSED during adr_trades                    
                    
CONDITIONS:                    
  adr_trades.volume >= 0.1 * adr.daily_volume                    
  AND home_price_impact_at_open >= 0.005                    
  AND position_reversal WITHIN 2h POST home_open                    
                    
AGGREGATIONS:                    
  adr_impact = (adr_close - adr_open) / adr_open                    
  home_impact = (home_open - prev_close) / prev_close                    
  cross_border_profit = home_position * home_impact                    
                    
OUTPUT: alert_type='CROSS_BORDER_MANIP', severity=HIGH                    
```                    
                    
### Rule 7.5: Commodity-Equity Link Manipulation                    
                    
```sql                    
RULE_ID: CROSS_COMMODITY_EQUITY_005                    
                    
PATTERN:                    
  SEQ(                    
    trades[account = A1, instrument.type = 'commodity'] AS commodity_trades,                    
    price_move[instrument = related_equity] AS equity_move                    
  )                    
                    
WINDOW: equity_move WITHIN 5m AFTER commodity_trades                    
                    
CONDITIONS:                    
  correlation(commodity, equity) >= 0.85                    
  AND position(A1, equity) LARGE                    
  AND commodity_trades.volume >= 0.05 * commodity.daily_volume                    
  AND equity_price_impact >= 0.003                    
                    
AGGREGATIONS:                    
  commodity_equity_correlation = CORRELATION OVER 30d                    
  equity_position_benefit = equity_position * equity_price_impact                    
  commodity_cost = commodity_trades.value * transaction_cost                    
                    
OUTPUT: alert_type='COMMODITY_EQUITY_MANIP', severity=MEDIUM                    
```                    
                    
## Category 8: Operational Risk                    
                    
### Rule 8.1: Position Limit Breach                    
                    
```sql                    
RULE_ID: RISK_POSITION_LIMIT_001                    
                    
PATTERN:                    
  positions[beneficial_owner = B1, instrument = I1] AS aggregated_position                    
                    
WINDOW: CONTINUOUS                    
                    
CONDITIONS:                    
  aggregated_position.net_quantity > regulatory_limit(I1, position_type)                    
  OR aggregated_position.net_quantity > exchange_limit(I1)                    
                    
AGGREGATIONS:                    
  total_position = SUM(positions.quantity) ACROSS related_accounts                    
  limit_breach_magnitude = total_position / limit - 1.0                    
  breach_duration = current_time - first_breach_time                    
                    
OUTPUT: alert_type='POSITION_LIMIT_BREACH', severity=CRITICAL, immediate_action='BLOCK_TRADING'                    
```                    
                    
### Rule 8.2: Credit Limit Breach                    
                    
```sql                    
RULE_ID: RISK_CREDIT_LIMIT_002                    
                    
PATTERN:                    
  exposure[account = A1] AS current_exposure                    
                    
WINDOW: CONTINUOUS real-time                    
                    
CONDITIONS:                    
  current_exposure.total > credit_limit(A1)                    
  OR current_exposure.margin_utilization > 1.0                    
                    
AGGREGATIONS:                    
  total_exposure = positions.value + open_orders.value                    
  margin_required = CALCULATE_MARGIN(positions, volatility)                    
  available_credit = credit_limit - total_exposure                    
                    
OUTPUT: alert_type='CREDIT_BREACH', severity=CRITICAL, immediate_action='MARGIN_CALL'                    
```                    
                    
### Rule 8.3: Fat Finger Detection                    
                    
```sql                    
RULE_ID: RISK_FAT_FINGER_003                    
                    
PATTERN:                    
  order[account = A1, instrument = I1] AS suspect_order                    
                    
WINDOW: IMMEDIATE on_order_entry                    
                    
CONDITIONS:                    
  (order.quantity > 100 * percentile_95(A1, I1, quantity) OVER 30d)                    
  OR (ABS(order.price - mid_price) / mid_price > 0.05)                    
  OR (order.value > 10 * percentile_95(A1, value) OVER 30d)                    
                    
AGGREGATIONS:                    
  quantity_z_score = (order.quantity - avg_quantity) / stddev_quantity                    
  price_deviation = ABS(order.price - mid_price) / mid_price                    
  value_ratio = order.value / typical_order_value                    
                    
OUTPUT: alert_type='FAT_FINGER', severity=HIGH, immediate_action='REQUIRE_CONFIRMATION'                    
```                    
                    
### Rule 8.4: Algo Gone Wild                    
                    
```sql                    
RULE_ID: RISK_ALGO_WILD_004                    
                    
PATTERN:                    
  orders[account = A1, algo_id = ALGO1] AS algo_orders                    
                    
WINDOW: SLIDING 1s                    
                    
CONDITIONS:                    
  COUNT(algo_orders) >= 1000 per_second                    
  OR cumulative_loss(algo_orders) >= 100000                    
  OR price_deviation(algo_orders) >= 0.02                    
                    
AGGREGATIONS:                    
  order_rate = COUNT(*) per_second                    
  cumulative_pnl = SUM(realized_pnl + unrealized_pnl)                    
  volatility_contribution = STDDEV(algo_orders.price) / market_stddev                    
                    
OUTPUT: alert_type='ALGO_MALFUNCTION', severity=CRITICAL, immediate_action='KILL_ALGO'                    
```                    
                    
## Category 9: Execution Abuse                    
                    
### Rule 9.1: Quote Fading                    
                    
```sql                    
RULE_ID: EXEC_QUOTE_FADE_001                    
                    
PATTERN:                    
  SEQ(                    
    order[account = A1, at_best = true] AS best_quote,                    
    marketable_order[account != A1, aggressing = best_quote.level] AS incoming,                    
    cancellation[order_id = best_quote.order_id] AS fade                    
  )                    
                    
WINDOW: fade WITHIN 10ms AFTER incoming                    
                    
CONDITIONS:                    
  fade.timestamp - incoming.timestamp <= 10ms                    
  AND fade_rate(A1) >= 0.8 OVER 1000 instances                    
  AND NOT legitimate_market_making(A1)                    
                    
AGGREGATIONS:                    
  fade_rate = COUNT(faded) / COUNT(at_best_quotes)                    
  avg_fade_latency = AVG(cancellation.time - incoming.time)                    
  false_liquidity_ratio = faded_volume / (provided_volume + faded_volume)                    
                    
OUTPUT: alert_type='QUOTE_FADING', severity=HIGH                    
```                    
                    
### Rule 9.2: Multi-Venue Layering                    
                    
```sql                    
RULE_ID: EXEC_MULTI_VENUE_LAYER_002                    
                    
PATTERN:                    
  orders[account = A1, side = S1] AS multi_venue_orders                    
    WHERE COUNT(DISTINCT venue_id) >= 3                    
                    
WINDOW: SLIDING 60s                    
                    
CONDITIONS:                    
  ALL(price_relative_to_nbbo) SAME_LEVEL                    
  AND cancellation_synchronization <= 5000ms                    
  AND executes_on_different_venue(A1) = true                    
                    
AGGREGATIONS:                    
  venue_count = COUNT(DISTINCT venue_id)                    
  cancel_synchronization = MAX(cancel_time) - MIN(cancel_time)                    
  cross_venue_coordination = CORRELATION(cancel_times ACROSS venues)                    
                    
OUTPUT: alert_type='MULTI_VENUE_LAYER', severity=HIGH                    
```                    
                    
### Rule 9.3: Dark Pool Leakage                    
                    
```sql                    
RULE_ID: EXEC_DARK_LEAK_003                    
                    
PATTERN:                    
  SEQ(                    
    order[venue.type = 'dark_pool'] AS dark_order,                    
    trades[venue.type = 'lit', account = A1] AS lit_trades                    
  )                    
                    
WINDOW: lit_trades WITHIN 100ms BEFORE dark_execution                    
                    
CONDITIONS:                    
  lit_trades.side = opposite(dark_order.side)                    
  AND timing_advantage(A1, dark_order) >= 0.9 OVER 20 instances                    
  AND consistent_profit(A1) >= 5000 OVER 30d                    
                    
AGGREGATIONS:                    
  timing_precision = 1 / STDDEV(lit_trade.time - dark_execution.time)                    
  success_rate = COUNT(profitable_trades) / COUNT(attempts)                    
  avg_profit_per_instance = SUM(profit) / COUNT(instances)                    
                    
OUTPUT: alert_type='DARK_POOL_LEAKAGE', severity=CRITICAL                    
```                    
                    
### Rule 9.4: Maker-Taker Abuse                    
                    
```sql                    
RULE_ID: EXEC_MAKER_TAKER_004                    
                    
PATTERN:                    
  orders[account = A1] AS rebate_orders                    
                    
WINDOW: DAILY                    
                    
CONDITIONS:                    
  rebate_revenue(A1) > trading_pnl(A1)                    
  AND order_to_trade_ratio >= 100:1                    
  AND avg_time_to_cancel <= 500ms                    
  AND NOT providing_meaningful_liquidity(A1)                    
                    
AGGREGATIONS:                    
  rebate_revenue = COUNT(maker_fills) * rebate_per_share                    
  trading_pnl = SUM(trade_pnl)                    
  rebate_ratio = rebate_revenue / (rebate_revenue + ABS(trading_pnl))                    
  order_to_trade = COUNT(orders) / COUNT(trades)                    
                    
OUTPUT: alert_type='MAKER_TAKER_ABUSE', severity=MEDIUM                    
```                    
                    
### Rule 9.5: Post-Only Abuse                    
                    
```sql                    
RULE_ID: EXEC_POST_ONLY_005                    
                    
PATTERN:                    
  orders[account = A1, execution_instruction = 'post_only'] AS post_orders                    
                    
WINDOW: SLIDING 1h                    
                    
CONDITIONS:                    
  cancel_before_match_rate >= 0.9                    
  AND queue_position_gaming_score >= 0.8                    
  AND NOT legitimate_liquidity_provision(A1)                    
                    
AGGREGATIONS:                    
  cancel_rate = COUNT(cancelled_before_match) / COUNT(post_orders)                    
  avg_queue_time = AVG(cancel_time - post_time)                    
  gaming_score = CORRELATION(queue_position, cancel_probability)                    
                    
OUTPUT: alert_type='POST_ONLY_ABUSE', severity=MEDIUM                    
```                    
                    
## Supporting Functions and Context                    
                    
```sql                    
-- Common Functions Library                    
                    
FUNCTION beneficial_owner(account_id):                    
  RETURN LOOKUP(account_graph, account_id).beneficial_owner                    
                    
FUNCTION accounts_related(acc1, acc2):                    
  RETURN GRAPH_PATH_EXISTS(acc1, acc2, max_depth=3)                    
                    
FUNCTION opposite(side):                    
  RETURN IF side = 'buy' THEN 'sell' ELSE 'buy'                    
                    
FUNCTION timing_correlation(events1, events2):                    
  RETURN CORRELATION(events1.timestamp, events2.timestamp)                    
                    
FUNCTION price_discovery_absent(acc1, acc2, instrument):                    
  pair_var = STDDEV(price WHERE acc1 trades with acc2)                    
  market_var = STDDEV(price WHERE instrument = instrument)                    
  RETURN pair_var < market_var * 0.3                    
                    
FUNCTION technical_level(instrument):                    
  RETURN [resistance_levels, support_levels, moving_averages] FROM technical_analysis                    
                    
FUNCTION baseline_volume(account, instrument):                    
  RETURN AVG(volume) OVER 30 days WHERE account AND instrument                    
                    
FUNCTION information_barrier_breach(desk1, desk2):                    
  RETURN NOT EXISTS(barrier BETWEEN desk1 AND desk2)                    
                    
-- State Stores                    
                    
STATE account_baselines:                    
  KEY: (account_id, instrument_id)                    
  VALUES: (avg_size, avg_rate, p95_size, typical_times)                    
  TTL: 90 days                    
                    
STATE relationship_graph:                    
  NODES: accounts                    
  EDGES: [beneficial_owner, family, corporate, ip_address, trading_pattern]                    
  UPDATE: streaming + batch_daily                    
                    
STATE market_metrics:                    
  KEY: (instrument_id, timestamp)                    
  VALUES: (mid_price, spread, volume, volatility)                    
  TTL: 30 days                    
  RESOLUTION: 100ms                    
                    
-- Reference Data                    
                    
REF_DATA instruments:                    
  FIELDS: [symbol, isin, tick_size, lot_size, sector, avg_daily_volume]                    
  UPDATE: daily                    
                    
REF_DATA regulatory_limits:                    
  FIELDS: [instrument, position_type, limit_quantity]                    
  UPDATE: on_change                    
                    
REF_DATA corporate_events:                    
  FIELDS: [instrument, event_type, event_date, materiality]                    
  UPDATE: real_time                    
                    
REF_DATA account_relationships:                    
  GRAPH: true                    
  UPDATE: daily + real_time_triggers                    
```                    
                                        
                                                  
                                                  
                                                  
                                                  
