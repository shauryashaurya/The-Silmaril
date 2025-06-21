# Ontology #23 - Construction Spend from Census data.                                           
                                 
[The constuction spend data at the US Census website](https://www.census.gov/construction/c30/data/index.html)
---

## 1. Possible Ontology

### **Mermaid Diagram**

Studing the site, this is a possible ontology we can explore:

```mermaid
graph LR
  A[Construction Spending Data] --> B[Temporal Dimension]
  A --> C[Sector Classification]
  A --> D[Geographic Dimension]
  A --> E[Economic Indicators]
  A --> F[Labor Market Attributes]
  A --> G[Risk Factors]
  A --> H[Revenue & Industry Impact]
  A --> I[Sustainability Metrics]

  B --> B1[Monthly]
  B --> B2[Quarterly]
  B --> B3[Annual]

  C --> C1[Private Construction]
  C1 --> C11[Residential]
  C1 --> C12[Nonresidential]
  C --> C2[Public Construction]
  C2 --> C21[Federal]
  C2 --> C22[State & Local]

  D --> D1[National]
  D --> D2[Regional]
  D --> D3[State-level]
  D --> D4[Urban vs Rural]

  E --> E1[GDP Growth]
  E --> E2[Unemployment]
  E --> E3[Interest Rates]
  E --> E4[Inflation]

  F --> F1[Employment Levels]
  F --> F2[Wage Growth]
  F --> F3[Productivity]

  G --> G1[Volatility]
  G --> G2[Policy Changes]
  G --> G3[Supply Chain Disruptions]

  H --> H1[Material Suppliers]
  H --> H2[Equipment Manufacturers]
  H --> H3[Real Estate Firms]
  H --> H4[ESG Companies]

  I --> I1[Green Certifications]
  I --> I2[Renewable Energy]
  I --> I3[CO2 Reductions]

```

---

