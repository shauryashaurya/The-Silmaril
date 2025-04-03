import random
import uuid
import os
from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

fake = Faker()
Faker.seed(42)
random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------------------
NUM_REGIONS = 1001
NUM_MARKETS = 5001
FORECASTS_PER_MARKET = 21
ECO_INDICATORS_PER_REGION = 10
NEWS_RECORDS_PER_REGION = 11

TD_RATIO = 0.6
START_ECON_YEAR = 2018
END_ECON_YEAR = 2024

# -------------------------------------------------------------------------
# STATIC NEWS HEADLINES & SOURCES
# -------------------------------------------------------------------------
NEWS_HEADLINES = [
    "Global crude prices surge amid pipeline outage",
    "New offshore wind project secures government funding",
    "Major utility announces $2B transmission line expansion",
    "Regulatory body greenlights interstate natural gas pipeline",
    "Refinery maintenance shutdown sparks local fuel shortage",
    "Solar capacity reaches record high in southwestern states",
    "Union strike halts construction of new oil sands project",
    "Energy giant acquires smaller competitor in $5.3B deal",
    "Hurricane disrupts Gulf Coast production and shipping routes",
    "Lawmakers propose incentives for grid modernization",
    "Natural gas demand spikes as winter temperatures drop",
    "Nuclear reactor retrofit aims to extend plant lifespan",
    "Research group forecasts sharp rise in LNG exports",
    "EV charging infrastructure gains traction in urban areas",
    "Oil major invests $600M in carbon capture technology",
    "Regulators mull stricter methane emission standards",
    "Utility raises rates to fund resilience improvements",
    "Floating wind farm pilot project breaks ground",
    "Arctic drilling ban prompts re-evaluation of leases",
    "Merger talks collapse over environmental permit delays",
    "Coal-fired plant announces phased shutdown plans",
    "Pipeline company eyes new export terminal in Asia",
    "Offshore drilling rig faces regulatory compliance audit",
    "European Union sets new targets for renewable energy adoption",
    "Solar farm expansions face local community opposition",
    "Battery storage facility doubles capacity in pilot program",
    "Gas flaring controversy triggers investor backlash",
    "Wind turbine manufacturers report supply chain disruptions",
    "LNG infrastructure projected to meet record global demand",
    "Refinery capacity utilization nears 90% after upgrades",
    "Major oil producer commits to net-zero by 2050 target",
    "T&D reliability metrics improve amid grid digitization",
    "New legislation offers tax credits for hydrogen projects",
    "EIA reports record natural gas inventories",
    "Tech startup unveils AI-driven pipeline leak detection system",
    "Floating solar array installed in local reservoir",
    "Energy trade summit focuses on transnational grid integration",
    "Public outcry over fracking expansions triggers lawsuits",
    "Distribution network modernization slashes outage durations",
    "Gas pipeline expansions stall amid environmental reviews",
    "Uranium spot prices jump on renewed nuclear interest",
    "Grid operator warns of potential summer brownouts",
    "Major offshore wind developer secures $1.8B in financing",
    "Utility invests $300M in advanced metering infrastructure",
    "Global energy demand rebounds faster than expected",
    "Biofuel producers explore algae-based alternatives",
    "Power sector grapples with cybersecurity threats",
    "Oil & gas workforce shortage prompts recruitment drive",
    "Renewable penetration tops 30% in European power mix",
    "Decommissioning costs rise for aging offshore platforms",
    "Microgrid solutions gain traction in rural communities",
    "Pipeline expansion project stalls amid protester blockade",
    "Gas utility invests in RNG to meet decarbonization goals",
    "Grid-scale battery pilot slashes peak load by 15%",
    "Power purchase agreements surge for wind and solar",
    "Emissions trading scheme faces political hurdles",
    "Major storm highlights grid vulnerabilities in coastal states",
    "Power line relocation plan meets fierce local resistance",
    "Oil futures dip on weaker-than-expected global demand",
    "Geothermal pilot project seeks to tap volcanic reservoir",
    "Refinery invests in advanced hydrocracking technology",
    "Industry watchdog fines pipeline operator for safety lapse",
    "Nationwide EV adoption spurs distribution grid upgrades",
    "Operators adopt drone inspections for remote well sites",
    "Funding allocated to research next-generation nuclear reactors",
    "Local authorities approve new carbon capture hub",
    "Green hydrogen partnership announced by major utilities",
    "Commodity traders brace for volatility in gas markets",
    "Offshore safety standards tighten after wellhead incident",
    "Long-duration energy storage sees first commercial deployment",
    "Load dispatch center rolls out advanced SCADA for real-time grid balancing",
    "Utility invests in major substation expansions to meet rising EV demand",
    "Smart grid technology pilot reduces distribution losses by 12%",
    "State regulators call for enhanced T&D reliability reporting",
    "New HVDC line to connect remote wind farms to major load centers",
    "Distribution automation pilot shows 20% reduction in outage durations",
    "Digital twin approach tested for substation asset management",
    "High-voltage line upgrade completed to improve cross-border electricity trade",
    "Smart meters rollout surpasses 1 million installations in metropolitan area",
    "Regulators propose penalties for repeated distribution reliability failures",
    "Rural electrification project uses microgrids to boost service reliability",
    "Distribution system planning prioritizes DER integration and load forecasting",
    "Utility forms consortium to standardize distribution SCADA interoperability",
    "Fiber-optic networks piggyback on T&D corridors to expand broadband access",
    "Underground cable replacement program aims to reduce storm-related outages",
    "Utility unveils advanced fault location technology for distribution lines",
    "Major city upgrades 80 substations for real-time demand response",
    "Drone-based line inspections detect 200 potential hazards in pilot study",
    "Grid modernization strategies pivot to multi-directional power flows",
    "Community battery storage demonstration ties into local distribution feeder",
    "Distribution operator invests in next-gen protection relay systems",
    "Long-range weather forecasting integrated into T&D planning",
    "Advanced sensor deployment reveals hidden hotspots on aging lines",
    "Demand response programs yield 150 MW peak load reduction",
    "State utility commission approves rate increase for T&D upgrades",
    "Energy management system overhaul reduces blackouts in coastal region",
    "Distribution grid congestion triggers dynamic tariff adjustments",
    "Urban undergrounding project aims to enhance public safety and aesthetics",
    "Utility invests $50M in overhead line reconductoring to increase capacity",
    "Cybersecurity vulnerabilities found in legacy substation control systems",
    "Wide-area monitoring system pilot improves early detection of faults",
    "Distribution transformers replaced with eco-friendly biodegradable fluid",
    "Voltage optimization pilot saves customers $3.2M in annual energy costs",
    "Line recloser automation helps isolate faults in under 60 seconds",
    "Substation consolidation plan sparks local controversy over land use",
    "Regulator mandates T&D reliability index targets be met by 2030",
    "Urban load growth forces re-evaluation of distribution capacity expansions",
    "Grid-edge analytics reduce distribution losses by pinpointing theft hotspots",
    "Next-generation DMS platform to unify SCADA and outage management systems",
    "Cold snap challenges distribution networks as electric heating demand soars",
    "High-impedance fault detection system tested in suburban feeders",
    "Utility invests in climate-resilient poles and cross-arms",
    "Energy storage aggregator coordinates with T&D operators to flatten peaks",
    "Transformer monitoring sensors cut emergency replacement costs by 40%",
    "Distribution system resilience plan addresses wildfire risk in dry regions",
    "Streetlight conversion to LED integrated with smart grid control",
    "Advanced meter data analytics reveal significant load shifting opportunities",
    "Distribution corridor expansions to support data center growth",
    "Regulators weigh benefits of performance-based T&D incentives",
    "Utility implements cost-reflective tariffs for distributed generation backfeed"
]


NEWS_SOURCES = [
    "Reuters",
    "Bloomberg",
    "Wall Street Journal",
    "Financial Times",
    "Energy Voice",
    "Oil & Gas Journal",
    "Platts",
    "S&P Global",
    "Rigzone",
    "Utility Dive",
    "E&E News"
]

# -------------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------------


def random_string_id(prefix=""):
    return prefix + str(uuid.uuid4())[:8]


def random_float(min_val, max_val):
    return round(random.uniform(min_val, max_val), 2)


def random_int(min_val, max_val):
    return random.randint(min_val, max_val)


def random_risk_rating():
    return round(random.uniform(1, 10), 2)


def random_sentiment():
    # If you still want a sentiment, keep it random or partial random
    return round(random.uniform(-1, 1), 2)


def random_date_in_past_decade():
    """Return a random date within the past ~10 years."""
    # Choose a random days offset up to ~3650 days (10 years)
    days_offset = random_int(0, 3650)
    return datetime.now() - timedelta(days=days_offset)

# ------------------------------------------------------------------------------
# 1. GENERATE REGIONS (Skipping lat/long for now)
# ------------------------------------------------------------------------------


def generate_regions(num_regions):
    regions_data = []
    for _ in range(num_regions):
        region_id = random_string_id("R-")
        city_name = fake.city()
        country_name = fake.country()
        sub_region = fake.state()
        population = random_int(100000, 20_000_000)
        major_areas = [fake.city() for __ in range(random_int(1, 3))]
        regulator = f"RegBody_{fake.word()}"
        references = [f"Source_{fake.word()}"]

        regions_data.append({
            "region_id": region_id,
            "name": city_name,
            "country": country_name,
            "sub_region": sub_region,
            "population": population,
            "major_metropolitan_areas": major_areas,
            "energy_regulatory_body": regulator,
            "data_source_references": references
        })

    return pd.DataFrame(regions_data)

# ------------------------------------------------------------------------------
# 2. GENERATE MARKETS
# ------------------------------------------------------------------------------


def generate_markets(regions_df, num_markets, td_ratio=0.6):
    region_ids = regions_df["region_id"].tolist()
    markets_data = []
    for _ in range(num_markets):
        market_id = random_string_id("M-")
        region_id = random.choice(region_ids)
        sector = "TRANSMISSION_DISTRIBUTION" if random.random() < td_ratio else "OIL_GAS"
        name = f"{sector[:3]}_{fake.company()[:10]}"
        currency = random.choice(["USD", "EUR", "GBP", "CAD", "AUD"])
        growth_projection = random_float(0.5, 10.0)
        risk = random_risk_rating()
        references = [f"Source_{fake.word()}"]

        markets_data.append({
            "market_id": market_id,
            "name": name,
            "sector": sector,
            "region_id": region_id,
            "currency_code": currency,
            "five_year_growth_projection": growth_projection,
            "risk_rating": risk,
            "data_source_references": references
        })

    return pd.DataFrame(markets_data)

# ------------------------------------------------------------------------------
# 3. T&D / O&G PROFILES
# ------------------------------------------------------------------------------


def generate_td_profiles(markets_df):
    td_markets = markets_df[markets_df["sector"]
                            == "TRANSMISSION_DISTRIBUTION"]
    td_data = []
    for _, row in td_markets.iterrows():
        td_profile_id = random_string_id("TD-")
        total_line_miles = random_float(100, 100000)
        substation_count = random_int(1, 5000)
        avg_voltage = random_float(33, 500)
        planned_upgrades = random_int(0, 50)
        load_growth = random_float(0.5, 5.0)
        reliability_metric = random_float(0.5, 5.0)
        automation_index = random_float(0, 10)

        td_data.append({
            "td_profile_id": td_profile_id,
            "market_id": row["market_id"],
            "total_line_miles": total_line_miles,
            "substation_count": substation_count,
            "avg_system_voltage_kv": avg_voltage,
            "planned_upgrades_count": planned_upgrades,
            "projected_load_growth_pct": load_growth,
            "reliability_metric_sadi": reliability_metric,
            "distribution_automation_index": automation_index
        })
    return pd.DataFrame(td_data)


def generate_og_profiles(markets_df):
    og_markets = markets_df[markets_df["sector"] == "OIL_GAS"]
    og_data = []
    for _, row in og_markets.iterrows():
        og_profile_id = random_string_id("OG-")
        proven_reserves = random_float(10, 10000)
        gas_reserves = random_float(10, 5000)
        pipeline_miles = random_float(50, 50000)
        production_capacity = random_float(1000, 5000000)
        well_count = random_int(10, 2000)
        refining_capacity = random_float(1000, 2000000)

        og_data.append({
            "og_profile_id": og_profile_id,
            "market_id": row["market_id"],
            "total_proven_reserves_barrels": proven_reserves,
            "total_gas_reserves_bcfe": gas_reserves,
            "pipeline_miles": pipeline_miles,
            "production_capacity_barrels_per_day": production_capacity,
            "active_well_count": well_count,
            "refining_capacity_barrels_per_day": refining_capacity
        })
    return pd.DataFrame(og_data)

# ------------------------------------------------------------------------------
# 4. FORECASTS
# ------------------------------------------------------------------------------


def generate_forecasts(markets_df, forecasts_per_market=10):
    all_forecasts = []
    for _, mrow in markets_df.iterrows():
        market_id = mrow["market_id"]
        start_year = random_int(2023, 2025)
        for i in range(forecasts_per_market):
            forecast_id = random_string_id("F-")
            year = start_year + i
            revenue = random_float(50, 5000)
            capex = random_float(10, revenue * 0.8)
            opex = random_float(5, revenue * 0.5)
            demand_idx = random_float(0, 10)
            supply_idx = random_float(0, 10)
            margin_pct = 0.0
            if revenue > 0:
                margin_pct = round(
                    ((revenue - opex - capex) / revenue) * 100, 2)

            confidence_score = random_float(0.5, 1.0)
            refs = [f"ForecastData_{fake.word()}"]

            all_forecasts.append({
                "forecast_id": forecast_id,
                "market_id": market_id,
                "year": year,
                "revenue_usd_million": revenue,
                "capex_usd_million": capex,
                "opex_usd_million": opex,
                "demand_index": demand_idx,
                "supply_index": supply_idx,
                "profit_margin_pct": margin_pct,
                "confidence_score": confidence_score,
                "data_source_references": refs
            })
    return pd.DataFrame(all_forecasts)

# ------------------------------------------------------------------------------
# 5. ECONOMIC & WORKFORCE DATA
# ------------------------------------------------------------------------------


def generate_region_economics(regions_df, start_year=2018, end_year=2023):
    econ_records = []
    years = list(range(start_year, end_year + 1))
    for _, row in regions_df.iterrows():
        region_id = row["region_id"]
        for year in years:
            rec_id = random_string_id("RE-")
            gdp = random_float(10, 2000)  # billions
            unemp = random_float(0, 25)
            income = random_float(10000, 120000)
            pop_growth = random_float(0, 4)
            biz_index = random_float(0, 10)
            refs = [f"EconData_{fake.word()}"]

            econ_records.append({
                "region_econ_id": rec_id,
                "region_id": region_id,
                "year": year,
                "gdp_usd_billion": gdp,
                "unemployment_rate_pct": unemp,
                "avg_household_income_usd": income,
                "population_growth_rate_pct": pop_growth,
                "business_growth_index": biz_index,
                "data_source_references": refs
            })
    return pd.DataFrame(econ_records)


def generate_workforce_stats(regions_df, start_year=2018, end_year=2023):
    wf_records = []
    years = list(range(start_year, end_year + 1))
    for _, row in regions_df.iterrows():
        region_id = row["region_id"]
        for year in years:
            wf_id = random_string_id("WF-")
            total_emp = random_int(5000, 2_000_000)
            skilled_pct = random_float(5, 40) / 100.0
            avg_salary = random_float(20000, 150000)
            skill_index = random_float(0, 10)
            training_count = random_int(0, 100)
            refs = [f"WF_{fake.word()}"]

            wf_records.append({
                "workforce_id": wf_id,
                "region_id": region_id,
                "year": year,
                "total_employees": total_emp,
                "industry_skilled_labor_pct": skilled_pct,
                "avg_salary_usd": avg_salary,
                "skill_availability_index": skill_index,
                "training_programs_count": training_count,
                "data_source_references": refs
            })
    return pd.DataFrame(wf_records)

# ------------------------------------------------------------------------------
# 6. REPLACEMENT NEWS GENERATOR (Static Headlines)
# ------------------------------------------------------------------------------


def generate_market_news(regions_df, records_per_region=10):
    news_data = []
    for _, row in regions_df.iterrows():
        region_id = row["region_id"]
        for _ in range(records_per_region):
            news_id = random_string_id("N-")
            # Randomly pick from static headlines and sources
            headline = random.choice(NEWS_HEADLINES)
            source = random.choice(NEWS_SOURCES)
            date_published = fake.date_between(
                start_date='-10y', end_date='today')
            sentiment = random_sentiment()
            keywords = [fake.word() for __ in range(random_int(1, 4))]

            news_data.append({
                "news_id": news_id,
                "region_id": region_id,
                "date_published": date_published,
                "headline": headline,
                "sentiment_score": sentiment,
                "source": source,
                "relevant_keywords": keywords
            })
    return pd.DataFrame(news_data)

# ------------------------------------------------------------------------------
# 7. EXTENDED MACRO ENTITIES
# ------------------------------------------------------------------------------


def generate_economic_performance_indicator(regions_df, records_per_region=3):
    epi_data = []
    for _, row in regions_df.iterrows():
        region_id = row["region_id"]
        for _ in range(records_per_region):
            epi_id = random_string_id("EPI-")
            year = random_int(2018, 2026)
            inflation = random_float(0.0, 15.0)
            interest = random_float(0.0, 10.0)
            debt_ratio = random_float(10, 200)
            budget_balance = random_float(-100, 300)
            consumer_conf = random_float(50, 120)
            refs = [f"EPI_{fake.word()}"]

            epi_data.append({
                "epi_id": epi_id,
                "region_id": region_id,
                "year": year,
                "inflation_rate_pct": inflation,
                "interest_rate_pct": interest,
                "govt_debt_gdp_ratio": debt_ratio,
                "govt_budget_balance_usd_billion": budget_balance,
                "consumer_confidence_index": consumer_conf,
                "data_source_references": refs
            })
    return pd.DataFrame(epi_data)

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------


def main():
    print("Generating synthetic Regions (without lat/long)...")

    # 1. REGIONS
    regions_df = generate_regions(NUM_REGIONS)

    print("\nGenerating synthetic data for Markets, Profiles, Forecasts, etc...\n")
    # 2. MARKETS
    markets_df = generate_markets(regions_df, NUM_MARKETS, TD_RATIO)

    # 3. T&D / O&G Profiles
    td_profiles_df = generate_td_profiles(markets_df)
    og_profiles_df = generate_og_profiles(markets_df)

    # 4. FORECASTS
    forecasts_df = generate_forecasts(markets_df, FORECASTS_PER_MARKET)

    # 5. Region Economics & Workforce
    region_econ_df = generate_region_economics(
        regions_df, START_ECON_YEAR, END_ECON_YEAR)
    workforce_df = generate_workforce_stats(
        regions_df, START_ECON_YEAR, END_ECON_YEAR)

    # 6. Extended Macro & News Data
    epi_df = generate_economic_performance_indicator(
        regions_df, ECO_INDICATORS_PER_REGION)
    news_df = generate_market_news(regions_df, NEWS_RECORDS_PER_REGION)

    # Summaries
    print(f"Regions: {len(regions_df)}")
    print(f"Markets: {len(markets_df)}")
    print(f"T&D Profiles: {len(td_profiles_df)}")
    print(f"O&G Profiles: {len(og_profiles_df)}")
    print(f"Forecasts: {len(forecasts_df)}")
    print(f"Region Economics: {len(region_econ_df)}")
    print(f"Workforce Stats: {len(workforce_df)}")
    print(f"Economic Performance Indicators: {len(epi_df)}")
    print(f"Market News: {len(news_df)}")

    total_records = sum([
        len(regions_df),
        len(markets_df),
        len(td_profiles_df),
        len(og_profiles_df),
        len(forecasts_df),
        len(region_econ_df),
        len(workforce_df),
        len(epi_df),
        len(news_df)
    ])
    print(f"Total records generated: {total_records}\n")

    # OPTIONAL: PERSIST CSVs LOCALLY
    os.makedirs("./data", exist_ok=True)
    regions_df.to_csv("./data/regions.csv", index=False)
    markets_df.to_csv("./data/markets.csv", index=False)
    td_profiles_df.to_csv("./data/td_profiles.csv", index=False)
    og_profiles_df.to_csv("./data/og_profiles.csv", index=False)
    forecasts_df.to_csv("./data/forecasts.csv", index=False)
    region_econ_df.to_csv("./data/region_econ.csv", index=False)
    workforce_df.to_csv("./data/workforce_stats.csv", index=False)
    epi_df.to_csv("./data/economic_performance_indicators.csv", index=False)
    news_df.to_csv("./data/market_news.csv", index=False)

    print("CSV files have been saved in the './data' folder.")


if __name__ == "__main__":
    main()
