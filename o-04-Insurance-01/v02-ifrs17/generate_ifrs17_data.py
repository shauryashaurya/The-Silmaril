import os
import uuid
import random
import string
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from faker import Faker

fake = Faker()
os.makedirs('./data', exist_ok=True)


def rand_date(start_year=2018, end_year=2025):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return fake.date_between(start_date=start, end_date=end)


def gen_policy_id():
    return "POL" + ''.join(random.choices(string.digits, k=8))


def gen_group_id():
    return "GRP" + ''.join(random.choices(string.digits, k=5))


def gen_float(min_val, max_val, precision=2):
    return round(random.uniform(min_val, max_val), precision)


def generate_insurance_policy_master(n):
    rows = []
    for _ in range(n):
        start = rand_date()
        months = random.randint(6, 36)
        end = start + timedelta(days=30 * months)
        rows.append({
            "policy_id": gen_policy_id(),
            "policy_group_id": gen_group_id(),
            "start_date": start,
            "end_date": end,
            "line_of_business": random.choice(["Motor", "Property", "Life", "Health"]),
            "coverage_term_months": months,
            "underwriting_year": start.year,
            "currency": random.choice(["USD", "EUR", "GBP"]),
            "ifrs_model_type": random.choice(["GMM", "PAA"]),
            "status": random.choice(["Active", "Expired", "Cancelled"])
        })
    df = pd.DataFrame(rows)
    df.to_csv('./data/insurance_policy_master.csv', index=False)
    return df


def generate_premium_transactions(df, n):
    policies = df["policy_id"].tolist()
    rows = []
    for _ in range(n):
        policy_id = random.choice(policies)
        prem = gen_float(500, 10000)
        ceded = gen_float(0.1 * prem, 0.5 * prem)
        net = prem - ceded
        rows.append({
            "transaction_id": str(uuid.uuid4()),
            "policy_id": policy_id,
            "transaction_date": rand_date(),
            "premium_amount": prem,
            "ceded_premium_amount": ceded,
            "net_premium_amount": net,
            "commission_paid": gen_float(0.01 * prem, 0.1 * prem)
        })
    pd.DataFrame(rows).to_csv('./data/premium_transactions.csv', index=False)


def generate_claims_transactions(df, n):
    policies = df["policy_id"].tolist()
    rows = []
    for _ in range(n):
        policy_id = random.choice(policies)
        incurred = rand_date()
        paid = incurred + timedelta(days=random.randint(0, 180))
        gross = gen_float(100, 10000)
        recover = gen_float(0.2 * gross, 0.8 * gross)
        net = gross - recover
        rows.append({
            "claim_id": str(uuid.uuid4()),
            "policy_id": policy_id,
            "claim_incurred_date": incurred,
            "claim_paid_date": paid,
            "gross_claim_amount": gross,
            "recoverable_amount": recover,
            "net_claim_amount": net,
            "claim_status": random.choice(["Paid", "Outstanding", "Closed"])
        })
    pd.DataFrame(rows).to_csv('./data/claims_transactions.csv', index=False)


def generate_reinsurance_treaty_master(n):
    rows = []
    for _ in range(n):
        start = rand_date(2015, 2023)
        end = start + timedelta(days=random.randint(365, 5*365))
        rows.append({
            "treaty_id": "TREATY" + ''.join(random.choices(string.digits, k=6)),
            "treaty_type": random.choice(["Quota Share", "Surplus", "XoL", "Facultative"]),
            "coverage_start_date": start,
            "coverage_end_date": end,
            "ceding_company": fake.company(),
            "reinsurer_name": fake.company(),
            "limit_amount": gen_float(100000, 10000000),
            "retention_amount": gen_float(50000, 1000000),
            "quota_share_percent": gen_float(10, 90),
            "commission_percent": gen_float(5, 25),
            "profit_commission_flag": random.choice([True, False])
        })
    pd.DataFrame(rows).to_csv(
        './data/reinsurance_treaty_master.csv', index=False)


def generate_risk_adjustment_input(n):
    rows = []
    for _ in range(n):
        rows.append({
            "lob": random.choice(["Motor", "Property", "Life", "Health"]),
            "confidence_level": random.choice([0.75, 0.85, 0.9]),
            "std_dev": gen_float(1000, 10000),
            "risk_adjustment_method": random.choice(["VaR", "CoC"]),
            "cost_of_capital_rate": gen_float(0.02, 0.08)
        })
    pd.DataFrame(rows).to_csv('./data/risk_adjustment_input.csv', index=False)


# def generate_discount_curve(n):
#     rows = []
#     for _ in range(n):
#         for m in range(6, 121, 6):
#             rows.append({
#                 "curve_id": f"CURVE_{_}",
#                 "maturity_months": m,
#                 "discount_rate": gen_float(0.01, 0.07),
#                 "as_of_date": rand_date()
#             })
#     pd.DataFrame(rows).to_csv('./data/discount_curve.csv', index=False)

def generate_discount_curve(n):
    rows = []
    for curve_index in range(n):
        curve_id = f"CURVE_{curve_index}"
        as_of = rand_date()
        for m in range(6, 121, 6):
            rows.append({
                "curve_id": curve_id,
                "maturity_months": m,
                "discount_rate": gen_float(0.01, 0.07),
                "as_of_date": as_of
            })
    pd.DataFrame(rows).to_csv('./data/discount_curve.csv', index=False)


def generate_ifrs17_metrics_output(df, n):
    groups = df["policy_group_id"].unique().tolist()
    rows = []
    for _ in range(n):
        group = random.choice(groups)
        open_csm = gen_float(10000, 500000)
        accretion = gen_float(100, 5000)
        release = gen_float(500, 10000)
        close_csm = open_csm + accretion - release
        rows.append({
            "policy_group_id": group,
            "period": rand_date(),
            "csm_opening": open_csm,
            "csm_accretion": accretion,
            "csm_release": release,
            "csm_closing": close_csm,
            "risk_adjustment": gen_float(1000, 10000),
            "loss_component": gen_float(0, 2000),
            "coverage_units": random.randint(1, 100),
            "service_expense": gen_float(1000, 10000),
            "insurance_revenue": gen_float(5000, 30000),
            "reinsurance_asset_change": gen_float(-5000, 5000)
        })
    pd.DataFrame(rows).to_csv('./data/ifrs17_metrics_output.csv', index=False)


def generate_forecast_scenarios(n):
    rows = []
    for _ in range(n):
        rows.append({
            "scenario_id": f"SCEN_{uuid.uuid4().hex[:6]}",
            "description": fake.sentence(nb_words=5),
            "premium_growth_rate": gen_float(0.01, 0.15),
            "claim_frequency_shift": gen_float(-0.05, 0.2),
            "catastrophe_factor": gen_float(0.9, 2.5),
            "discount_curve_override": f"CURVE_{random.randint(1, 5)}",
            "lapse_rate": gen_float(0.01, 0.1),
            "run_date": rand_date()
        })
    pd.DataFrame(rows).to_csv('./data/forecast_scenarios.csv', index=False)


def generate_journal_entries(df, n):
    groups = df["policy_group_id"].unique().tolist()
    rows = []
    for _ in range(n):
        rows.append({
            "entry_id": str(uuid.uuid4()),
            "posting_date": rand_date(),
            "policy_group_id": random.choice(groups),
            "account_code": "AC" + ''.join(random.choices(string.digits, k=5)),
            "description": fake.sentence(nb_words=4),
            "amount": gen_float(-50000, 50000),
            "dr_cr_flag": random.choice(["DR", "CR"]),
            "source_metric": random.choice(["CSM", "RA", "Claim"]),
            "export_status": random.choice(["Ready", "Posted", "Rejected"])
        })
    pd.DataFrame(rows).to_csv('./data/journal_entries.csv', index=False)


def generate_all(volumes):
    df_policies = generate_insurance_policy_master(
        volumes['insurance_policy_master'])
    generate_premium_transactions(df_policies, volumes['premium_transactions'])
    generate_claims_transactions(df_policies, volumes['claims_transactions'])
    generate_reinsurance_treaty_master(volumes['reinsurance_treaty_master'])
    generate_risk_adjustment_input(volumes['risk_adjustment_input'])
    generate_discount_curve(volumes['discount_curve'])
    generate_ifrs17_metrics_output(
        df_policies, volumes['ifrs17_metrics_output'])
    generate_forecast_scenarios(volumes['forecast_scenarios'])
    generate_journal_entries(df_policies, volumes['journal_entries'])


if __name__ == '__main__':
    # generate_all({
    #     'insurance_policy_master': 1000,
    #     'premium_transactions': 5000,
    #     'claims_transactions': 3000,
    #     'reinsurance_treaty_master': 100,
    #     'risk_adjustment_input': 50,
    #     'discount_curve': 5,
    #     'ifrs17_metrics_output': 3000,
    #     'forecast_scenarios': 50,
    #     'journal_entries': 5000
    # })
    generate_all({
        'insurance_policy_master': 7000,
        'premium_transactions': 10000,
        'claims_transactions': 9000,
        'reinsurance_treaty_master': 500,
        'risk_adjustment_input': 90,
        'discount_curve': 15,
        'ifrs17_metrics_output': 7000,
        'forecast_scenarios': 100,
        'journal_entries': 15000
    })
