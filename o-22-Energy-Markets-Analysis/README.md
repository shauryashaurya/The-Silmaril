# Ontology #22 - Energy Markets Analysis                                           
                                 
Here we are focussed on building ontologies to analyse the markets from a EPCC Transmission and Distribution business unit as well as Oil and Gas buisiness unit's perspective. We want to enable the respective teams to explore scenarios and build strategies for investments.
---

## 1. EnergyMarketForecast Ontology

### **Competency & Usage**
- **Focus**: Captures details for **Transmission & Distribution (T&D)** and **Oil & Gas (O&G)** markets, including basic region info, specialized profiles, and multi-year forecasts.  
- **Core Entities**:  
  1. **Region**: Basic geographic grouping (city/state/country) or operational territory.  
  2. **Market**: Represents a T&D or O&G market within a region, with overarching attributes like risk rating.  
  3. **TransmissionDistributionProfile**: Specialized data for T&D infrastructure (line miles, substation counts, reliability metrics).  
  4. **OilGasProfile**: Specialized data for O&G (reserves, pipeline miles, refining capacity).  
  5. **Forecast**: Multi-year financial projections, CAPEX, OPEX, profit margin, etc.

### **Scenarios**
1. **T&D Reliability Improvement**  
   - Evaluate how upgrades to transmission lines (in `TransmissionDistributionProfile`) might improve system reliability and lower SAIDI.  
   - Compare `Forecast` data to see if additional CAPEX has a favorable ROI.
2. **O&G Production Expansion**  
   - Assess new pipeline expansions (`OilGasProfile.pipeline_miles`) or increased production capacity.  
   - Observe resulting changes in forecasted revenue or risk ratings for the next 5 years.
3. **Cross-Region Investment Comparison**  
   - Filter by `region_id` to see which areas have the highest growth potential, balancing risk vs. potential profit.

### **Pseudocode**

```pseudocode
Ontology EnergyMarketForecast {

  Entity Region {
    Attributes:
      - region_id: String
      - name: String
      - country: String
      - sub_region: String
      - population: Long
      - major_metropolitan_areas: List<String>
      - energy_regulatory_body: String
      - data_source_references: List<String>
      // (latitude, longitude optional or omitted)
  }

  Entity Market {
    Attributes:
      - market_id: String
      - name: String
      - sector: Enum {TRANSMISSION_DISTRIBUTION, OIL_GAS, RENEWABLES, OTHER}
      - region_id: FK(Region)
      - currency_code: String
      - five_year_growth_projection: Float
      - risk_rating: Float
      - data_source_references: List<String>
  }

  Entity TransmissionDistributionProfile {
    Attributes:
      - td_profile_id: String
      - market_id: FK(Market)
      - total_line_miles: Float
      - substation_count: Integer
      - avg_system_voltage_kv: Float
      - planned_upgrades_count: Integer
      - projected_load_growth_pct: Float
      - reliability_metric_sadi: Float
      - distribution_automation_index: Float
  }

  Entity OilGasProfile {
    Attributes:
      - og_profile_id: String
      - market_id: FK(Market)
      - total_proven_reserves_barrels: Float
      - total_gas_reserves_bcfe: Float
      - pipeline_miles: Float
      - production_capacity_barrels_per_day: Float
      - active_well_count: Integer
      - refining_capacity_barrels_per_day: Float
  }

  Entity Forecast {
    Attributes:
      - forecast_id: String
      - market_id: FK(Market)
      - year: Integer
      - revenue_usd_million: Float
      - capex_usd_million: Float
      - opex_usd_million: Float
      - demand_index: Float
      - supply_index: Float
      - profit_margin_pct: Float
      - confidence_score: Float
      - data_source_references: List<String>
  }

  Relationship Region HAS Market
  Relationship Market HAS TransmissionDistributionProfile
  Relationship Market HAS OilGasProfile
  Relationship Market HAS Forecast
}
```

### **Mermaid Diagram**

Below is an ER (Entity-Relationship) style diagram. **All strings** are in **double quotes**, and we use standard Mermaid notations:

```mermaid
erDiagram
  %% A Region can have multiple Markets
  Region ||--o{ Market : HAS
  %% A Market can have multiple TransmissionDistributionProfiles
  Market ||--o{ TransmissionDistributionProfile : HAS
  %% A Market can have multiple OilGasProfiles
  Market ||--o{ OilGasProfile : HAS
  %% A Market can have multiple Forecasts
  Market ||--o{ Forecast : HAS

  Region {
    string region_id
    string name
    string country
    string sub_region
    long population
    string[] major_metropolitan_areas
    string energy_regulatory_body
    string[] data_source_references
  }

  Market {
    string market_id
    string name
    string sector
    string region_id
    %% Foreign Key to Region
    string currency_code
    float five_year_growth_projection
    float risk_rating
    string[] data_source_references
  }

  TransmissionDistributionProfile {
    string td_profile_id
    string market_id
    %% Foreign Key to Market
    float total_line_miles
    int substation_count
    float avg_system_voltage_kv
    int planned_upgrades_count
    float projected_load_growth_pct
    float reliability_metric_sadi
    float distribution_automation_index
  }

  OilGasProfile {
    string og_profile_id
    string market_id
    %% Foreign Key to Market
    float total_proven_reserves_barrels
    float total_gas_reserves_bcfe
    float pipeline_miles
    float production_capacity_barrels_per_day
    int active_well_count
    float refining_capacity_barrels_per_day
  }

  Forecast {
    string forecast_id
    string market_id
    %% Foreign Key to Market
    int year
    float revenue_usd_million
    float capex_usd_million
    float opex_usd_million
    float demand_index
    float supply_index
    float profit_margin_pct
    float confidence_score
    string[] data_source_references
  }
```

---

## 2. EconomicAndStrategicIndicators Ontology (Extended)

### **Competency & Usage**
- **Focus**: Provides **macro-level** (GDP, inflation, interest rates) and **micro-level** (workforce, average salaries) context for each region, plus **market news** and **strategic/policy** insights.  
- **Core Entities**:  
  1. **RegionEconomics**: Captures annual GDP, unemployment, household income, etc.  
  2. **WorkforceStats**: Tracks total employees, skill availability, training programs.  
  3. **EconomicPerformanceIndicator**: Extended macro data—inflation rate, interest rate, government debt.  
  4. **MarketNews**: Aggregates news headlines and sentiment for each region.  
  5. **StrategicIndicator** (optional extension): Could measure regulatory stability, competition index.

### **Scenarios**
1. **Macro-Driven Demand Forecast**  
   - Combine *inflation_rate_pct* with OPEX or CAPEX forecasts to see if rising inflation impacts project viability.  
   - Evaluate how unemployment or consumer confidence might affect local energy demand.
2. **Workforce Planning**  
   - Regions with high skill_availability_index can handle large T&D or O&G expansions.  
   - Evaluate impact of new training programs on *industry_skilled_labor_pct* over multiple years.
3. **Sentiment & Regulatory Risk**  
   - *MarketNews* sentiment can act as an early warning for shifting public or political attitudes.  
   - High competition or low policy stability can deter large CAPEX expansions.

### **Pseudocode**

```pseudocode
Ontology EconomicAndStrategicIndicators {

  // Basic region-level economic data
  Entity RegionEconomics {
    Attributes:
      - region_econ_id: String
      - region_id: FK(Region)  // or a direct link if "Region" is external
      - year: Integer
      - gdp_usd_billion: Float
      - unemployment_rate_pct: Float
      - avg_household_income_usd: Float
      - population_growth_rate_pct: Float
      - business_growth_index: Float
      - data_source_references: List<String>
  }

  Entity WorkforceStats {
    Attributes:
      - workforce_id: String
      - region_id: FK(Region)
      - year: Integer
      - total_employees: Long
      - industry_skilled_labor_pct: Float
      - avg_salary_usd: Float
      - skill_availability_index: Float
      - training_programs_count: Integer
      - data_source_references: List<String>
  }

  // Extended macro-level indicators
  Entity EconomicPerformanceIndicator {
    Attributes:
      - epi_id: String
      - region_id: FK(Region)
      - year: Integer
      - inflation_rate_pct: Float
      - interest_rate_pct: Float
      - govt_debt_gdp_ratio: Float
      - govt_budget_balance_usd_billion: Float
      - consumer_confidence_index: Float
      - data_source_references: List<String>
  }

  // News & sentiment data
  Entity MarketNews {
    Attributes:
      - news_id: String
      - region_id: FK(Region)
      - date_published: Date
      - headline: String
      - sentiment_score: Float
      - source: String
      - relevant_keywords: List<String>
  }

  // Optional: broader strategic indicators
  Entity StrategicIndicator {
    Attributes:
      - strategic_id: String
      - region_id: FK(Region)
      - market_id: FK(Market)
      - year: Integer
      - regulatory_index: Float
      - infrastructure_quality_index: Float
      - competition_index: Float
      - foreign_investment_usd_million: Float
      - policy_stability_score: Float
      - data_source_references: List<String>
  }

  Relationship RegionEconomics -> Region
  Relationship WorkforceStats -> Region
  Relationship EconomicPerformanceIndicator -> Region
  Relationship MarketNews -> Region
  Relationship StrategicIndicator -> Region
  Relationship StrategicIndicator -> Market
}
```

### **Mermaid Diagram**

```mermaid
erDiagram
  %% RegionEconomics BELONGS_TO Region
  RegionEconomics }o--|| Region : BELONGS_TO
  %% WorkforceStats BELONGS_TO Region
  WorkforceStats }o--|| Region : BELONGS_TO
  %% EconomicPerformanceIndicator BELONGS_TO Region
  EconomicPerformanceIndicator }o--|| Region : BELONGS_TO
  %% MarketNews BELONGS_TO Region
  MarketNews }o--|| Region : BELONGS_TO
  %% StrategicIndicator BELONGS_TO Region
  StrategicIndicator }o--|| Region : BELONGS_TO
  %% StrategicIndicator AFFECTS Market
  StrategicIndicator }o--|| Market : AFFECTS

  RegionEconomics {
    string region_econ_id
    string region_id
    int year
    float gdp_usd_billion
    float unemployment_rate_pct
    float avg_household_income_usd
    float population_growth_rate_pct
    float business_growth_index
    string[] data_source_references
  }

  WorkforceStats {
    string workforce_id
    string region_id
    int year
    long total_employees
    float industry_skilled_labor_pct
    float avg_salary_usd
    float skill_availability_index
    int training_programs_count
    string[] data_source_references
  }

  EconomicPerformanceIndicator {
    string epi_id
    string region_id
    int year
    float inflation_rate_pct
    float interest_rate_pct
    float govt_debt_gdp_ratio
    float govt_budget_balance_usd_billion
    float consumer_confidence_index
    string[] data_source_references
  }

  MarketNews {
    string news_id
    string region_id
    date date_published
    string headline
    float sentiment_score
    string source
    string[] relevant_keywords
  }

  StrategicIndicator {
    string strategic_id
    string region_id
    string market_id
    int year
    float regulatory_index
    float infrastructure_quality_index
    float competition_index
    float foreign_investment_usd_million
    float policy_stability_score
    string[] data_source_references
  }
```

---

## **Putting It All Together**

- The **EnergyMarketForecast** ontology covers **sector-specific** data (T&D, O&G, Forecasts) and ties everything to **Region**.  
- The **EconomicAndStrategicIndicators** ontology (with extended macro data) adds **economic performance**, **workforce** stats, **market news**, and optional **strategic** insights.  
- **Cross-Ontology Link**: The **Region** entity typically belongs to **EnergyMarketForecast**, while the extended ontology references that same `region_id`. If a *StrategicIndicator* or *MarketNews* references a specific Market, it can link to the *Market* entity from the first ontology.  

By merging these two ontologies, you gain **comprehensive coverage** of financial, operational, macroeconomic, and strategic/regulatory insights—enabling **rich scenario modeling** and **multi-year forecasts** for T&D and O&G investments.