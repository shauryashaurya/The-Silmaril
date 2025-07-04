import os
import re
import json
import logging
import ast
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter

# Configuration
data_location = os.getenv('DATA_LOCATION', './data')

# Utility Functions


def normalize_id(value: Any) -> str:
    """Normalize numeric IDs to string form, preventing FK mismatches."""
    try:
        # return str(int(float(value)))
        if type(value) == 'str':
            return value
        else:
            return str(value)
    except (ValueError, TypeError):
        logging.warning(f"Failed to normalize ID: {value}")
        return str(value)


def parse_id_list(value: Any) -> List[str]:
    """Parse comma-, list-, or bracket-formatted ID lists into normalized strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [normalize_id(v) for v in value]
    s = str(value)
    if s.startswith('[') and s.endswith(']'):
        try:
            lst = ast.literal_eval(s)
            return [normalize_id(v) for v in lst]
        except Exception:
            pass
    return [normalize_id(p.strip()) for p in s.split(',') if p.strip()]

# Entity Dataclasses


@dataclass
class PolicyHolder:
    id: str
    name: str
    dateOfBirth: str
    address: str
    phoneNumber: str
    policies: List['Policy'] = field(default_factory=list)
    claims: List['Claim'] = field(default_factory=list)
    totalClaimAmount: Optional[float] = None
    riskScore: Optional[float] = None
    classifications: List[str] = field(default_factory=list)
    status: Optional[str] = None
    eligibleForDiscount: Optional[str] = None


@dataclass
class Insurer:
    id: str
    insurerName: str
    headquartersLocation: str
    industryRating: float
    policies: List['Policy'] = field(default_factory=list)


@dataclass
class Agent:
    id: str
    name: str
    agencyName: str
    agentLicense: str
    policies: List['Policy'] = field(default_factory=list)
    commissionAmount: Optional[float] = None


@dataclass
class Underwriter:
    id: str
    name: str
    licenseID: str
    experienceYears: int
    policies: List['Policy'] = field(default_factory=list)


@dataclass
class Policy:
    id: str
    policyNumber: str
    policyType: str
    startDate: str
    endDate: str
    premiumAmount: float
    status: str
    policyHolderId: str
    insurerId: str
    underwriterId: str
    coverageIds: List[str]
    agentId: str
    policyHolder: Optional[PolicyHolder] = None
    insurer: Optional[Insurer] = None
    underwriter: Optional[Underwriter] = None
    agent: Optional[Agent] = None
    coverages: List['Coverage'] = field(default_factory=list)
    claims: List['Claim'] = field(default_factory=list)
    classifications: List[str] = field(default_factory=list)


@dataclass
class Coverage:
    id: str
    coverageName: str
    coverageLimit: float
    deductible: float
    policy: Optional[Policy] = None


@dataclass
class Claim:
    id: str
    claimNumber: str
    claimDate: str
    claimType: str
    amountClaimed: float
    amountSettled: Optional[float]
    status: str
    policyId: str
    policyHolderId: str
    insurerId: str
    policy: Optional[Policy] = None
    claimHolder: Optional[PolicyHolder] = None
    classifications: List[str] = field(default_factory=list)


class DataLoader:
    """Phase 1: Data Ingestion and Diagnostics"""

    def __init__(self, data_location: str = data_location):
        self.data_location = data_location
        self.raw_dfs: Dict[str, pd.DataFrame] = {}

    def load_all_data(self) -> None:
        logging.info("[DataLoader] Loading all data sources...")
        self._load_dataframes()
        self._run_diagnostics()

    def _load_dataframes(self) -> None:
        logging.info("[DataLoader] Vectorized loading of CSVs...")
        file_map = {
            'policyholders': 'policyholders.csv',
            'policies': 'policies.csv',
            'agents': 'agents.csv',
            'insurers': 'insurers.csv',
            'underwriters': 'underwriters.csv',
            'coverages': 'coverages.csv',
            'claims': 'claims.csv'
        }
        for key, fname in file_map.items():
            path = os.path.join(self.data_location, fname)
            df = pd.read_csv(path)
            df.rename(columns={
                'policyHolderID': 'policyHolderId',
                'insurerID': 'insurerId',
                'underwriterID': 'underwriterId',
                'agentID': 'agentId',
                'coverageIDs': 'coverageIds',
                'policyID': 'policyId'
            }, inplace=True)
            # Normalize IDs
            for col in df.columns:
                if col.lower().endswith('id'):
                    df[col] = df[col].apply(normalize_id)
            # Cast numerics
            for num_col in ['premiumAmount', 'coverageLimit', 'deductible', 'amountClaimed', 'amountSettled', 'industryRating']:
                if num_col in df:
                    df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
            if 'experienceYears' in df:
                df['experienceYears'] = pd.to_numeric(
                    df['experienceYears'], errors='coerce', downcast='integer')
            if 'coverageIds' in df:
                df['coverageIds'] = df['coverageIds'].apply(parse_id_list)
            self.raw_dfs[key] = df

    def _run_diagnostics(self) -> None:
        logging.info("[DataLoader] Running diagnostics...")
        ph_ids = set(self.raw_dfs['policyholders']['id'])
        ins_ids = set(self.raw_dfs['insurers']['id'])
        uw_ids = set(self.raw_dfs['underwriters']['id'])
        ag_ids = set(self.raw_dfs['agents']['id'])
        pol_ids = set(self.raw_dfs['policies']['id'])

        # Policies FK checks
        for _, row in self.raw_dfs['policies'].iterrows():
            if row['policyHolderId'] not in ph_ids:
                logging.error(
                    f"Policy {row['id']} references missing PolicyHolder {row['policyHolderId']}")
            if row['insurerId'] not in ins_ids:
                logging.error(
                    f"Policy {row['id']} references missing Insurer {row['insurerId']}")
            if row['underwriterId'] not in uw_ids:
                logging.error(
                    f"Policy {row['id']} references missing Underwriter {row['underwriterId']}")
            if row['agentId'] not in ag_ids:
                logging.error(
                    f"Policy {row['id']} references missing Agent {row['agentId']}")

        # Claims FK checks
        for _, row in self.raw_dfs['claims'].iterrows():
            if row['policyId'] not in pol_ids:
                logging.error(
                    f"Claim {row['id']} references missing Policy {row['policyId']}")
            if row['policyHolderId'] not in ph_ids:
                logging.error(
                    f"Claim {row['id']} references missing PolicyHolder {row['policyHolderId']}")
            if row['insurerId'] not in ins_ids:
                logging.error(
                    f"Claim {row['id']} references missing Insurer {row['insurerId']}")

        # Orphans
        holders_with_policies = set(self.raw_dfs['policies']['policyHolderId'])
        for ph in ph_ids - holders_with_policies:
            logging.warning(f"PolicyHolder {ph} has no associated policies")


class Reasoner:
    """Phases 2-4: Processing, Analytics & Output"""

    def __init__(self, loader: DataLoader):
        self.loader = loader
        self.entities: Dict[str, List[Any]] = {}
        self.stats: Dict[str, Any] = {}
        self.insights: Dict[str, Any] = {}
        self.performance: Dict[str, Any] = {}
        self.recommendations: List[str] = []

    def _serialize(self, obj: Any) -> Any:
        """Recursively convert dataclass objects and nested structures to JSON-serializable form."""
        # primitives
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        # lists
        if isinstance(obj, list):
            return [self._serialize(item) for item in obj]
        # dataclass-like objects
        if hasattr(obj, '__dict__'):
            data = {}
            for key, val in vars(obj).items():
                # if it’s a back-reference list, just emit IDs
                if isinstance(val, list) and val and hasattr(val[0], 'id'):
                    data[key] = [item.id for item in val]
                # if it’s a single object, emit its ID
                elif hasattr(val, 'id'):
                    data[key] = val.id
                else:
                    data[key] = self._serialize(val)
            return data
        # fallback
        return str(obj)

    # Phase 2: Entity load & relationships

    def _create_entities_from_dataframes(self) -> None:
        logging.info("[Reasoner] Instantiating entities...")
        mapping = {
            'policyholders': PolicyHolder,
            'policies': Policy,
            'agents': Agent,
            'insurers': Insurer,
            'underwriters': Underwriter,
            'coverages': Coverage,
            'claims': Claim
        }
        for key, cls in mapping.items():
            df = self.loader.raw_dfs.get(key)
            if df is None:
                continue
            self.entities[key] = [cls(**dict(zip(df.columns, row)))
                                  for row in df.itertuples(index=False, name=None)]

    def _build_relationship_mappings(self) -> None:
        logging.info("[Reasoner] Building relationships...")
        # Link policies to holders, insurers, underwriters, agents
        for p in self.entities.get('policies', []):
            ph = next(
                (x for x in self.entities['policyholders'] if x.id == p.policyHolderId), None)
            if ph:
                ph.policies.append(p)
                p.policyHolder = ph
            ins = next(
                (x for x in self.entities['insurers'] if x.id == p.insurerId), None)
            if ins:
                ins.policies.append(p)
                p.insurer = ins
            uw = next(
                (x for x in self.entities['underwriters'] if x.id == p.underwriterId), None)
            if uw:
                uw.policies.append(p)
                p.underwriter = uw
            ag = next(
                (x for x in self.entities['agents'] if x.id == p.agentId), None)
            if ag:
                ag.policies.append(p)
                p.agent = ag

        # Link coverages to policies
        for c in self.entities.get('coverages', []):
            for p in self.entities.get('policies', []):
                if c.id in p.coverageIds:
                    p.coverages.append(c)
                    c.policy = p
                    break

        # Link claims
        for cl in self.entities.get('claims', []):
            pol = next(
                (x for x in self.entities['policies'] if x.id == cl.policyId), None)
            if pol:
                pol.claims.append(cl)
                cl.policy = pol
            ph = next(
                (x for x in self.entities['policyholders'] if x.id == cl.policyHolderId), None)
            if ph:
                ph.claims.append(cl)
                cl.claimHolder = ph

    def _compute_inverse_properties(self) -> None:
        logging.info("[Reasoner] Ensuring inverse links...")
        # Already set in build; verify completeness
        # No-op

    def _calculate_derived_properties(self) -> None:
        logging.info("[Reasoner] Placeholder for domain-specific derives")

    def _validate_cardinality_constraints(self) -> None:
        logging.info("[Reasoner] Enforcing cardinalities...")
        for cl in self.entities.get('claims', []):
            if cl.claimHolder is None:
                logging.error(f"Claim {cl.id} lacks a filing PolicyHolder")
        for p in self.entities.get('policies', []):
            if p.policyHolder is None:
                logging.error(f"Policy {p.id} lacks a PolicyHolder")
        for c in self.entities.get('coverages', []):
            if c.policy is None:
                logging.error(f"Coverage {c.id} not attached to any Policy")

    def apply_reasoning_rules(self) -> None:
        logging.info("[Reasoner] Applying rules...")
        for name in sorted(dir(self)):
            if name.startswith('_rule_'):
                getattr(self, name)()

    # ===== N3 Rules Implementation =====
    def _rule_01_policy_status_classification(self):
        today = datetime.utcnow().date()
        for p in self.entities.get('policies', []):
            try:
                start = datetime.strptime(p.startDate, '%Y-%m-%d').date()
                end = datetime.strptime(p.endDate, '%Y-%m-%d').date()
            except:
                continue
            if start <= today <= end:
                p.classifications.append('ActivePolicy')
                p.status = 'ACTIVE'
            elif today > end:
                p.classifications.append('ExpiredPolicy')
                p.status = 'EXPIRED'

    def _rule_02_high_risk_policy_holder(self):
        for ph in self.entities.get('policyholders', []):
            if len({cl.id for cl in ph.claims}) >= 3:
                ph.classifications.append('HighRiskPolicyHolder')

    def _rule_03_total_claim_amount(self):
        for ph in self.entities.get('policyholders', []):
            ph.totalClaimAmount = sum(cl.amountClaimed for cl in ph.claims)

    def _rule_04_risk_score_calculation(self):
        for ph in self.entities.get('policyholders', []):
            total_c = ph.totalClaimAmount or 0
            total_p = sum(p.premiumAmount for p in ph.policies)
            ph.riskScore = (total_c/total_p*100) if total_p else 0

    def _rule_05_claim_auto_approval(self):
        for cl in self.entities.get('claims', []):
            if cl.amountClaimed < 5000 and cl.claimType.lower() == 'auto':
                cl.classifications.append('ApprovedClaim')
                cl.status = 'AUTO_APPROVED'

    def _rule_06_large_claim_review(self):
        for cl in self.entities.get('claims', []):
            if cl.amountClaimed >= 50000:
                cl.classifications.append('PendingClaim')
                cl.status = 'REQUIRES_SENIOR_REVIEW'

    def _rule_07_agent_commission(self):
        for ag in self.entities.get('agents', []):
            ag.commissionAmount = round(
                sum(p.premiumAmount*0.05 for p in ag.policies), 2)

    def _rule_08_coverage_limit_validation(self):
        for cl in self.entities.get('claims', []):
            if cl.policy:
                for cov in cl.policy.coverages:
                    if cl.amountClaimed > cov.coverageLimit:
                        cl.classifications.append('ExceedsCoverageLimit')
                        cl.status = 'EXCEEDS_COVERAGE_LIMIT'
                        break

    def _rule_09_policy_renewal_eligibility(self):
        today = datetime.utcnow().date()
        for p in self.entities.get('policies', []):
            ph = p.policyHolder
            if ph and ph.riskScore is not None:
                end = datetime.strptime(p.endDate, '%Y-%m-%d').date()
                days_left = (end-today).days
                if ph.riskScore < 150 and 0 <= days_left <= 30:
                    p.classifications.append('EligibleForRenewal')
                    p.status = 'ELIGIBLE_FOR_RENEWAL'

    def _rule_10_underwriter_assignment(self):
        candidates = [u for u in self.entities.get(
            'underwriters', []) if u.experienceYears > 5]
        for p in self.entities.get('policies', []):
            if p.premiumAmount > 10000 and candidates:
                best = max(candidates, key=lambda u: u.experienceYears)
                p.underwriter = best
                p.underwriterId = best.id
                best.policies.append(p)

    def _rule_11_claim_settlement_amount(self):
        for cl in self.entities.get('claims', []):
            if cl.policy:
                for cov in cl.policy.coverages:
                    amt = cl.amountClaimed - cov.deductible
                    if amt > 0:
                        cl.amountSettled = round(amt, 2)
                        break

    def _rule_12_policy_type_inference(self):
        for p in self.entities.get('policies', []):
            for cov in p.coverages:
                name = cov.coverageName.upper()
                if 'AUTO' in name:
                    p.policyType = 'AUTOMOBILE'
                    break
                if 'HOME' in name:
                    p.policyType = 'HOMEOWNERS'
                    break

    def _rule_13_high_value_customer(self):
        for ph in self.entities.get('policyholders', []):
            total_p = sum(p.premiumAmount for p in ph.policies)
            if total_p > 50000:
                ph.classifications.append('HighValueCustomer')

    def _rule_14_claim_fraud_detection(self):
        for ph in self.entities.get('policyholders', []):
            claims = sorted(ph.claims, key=lambda c: datetime.strptime(
                c.claimDate, '%Y-%m-%d'))
            for i in range(len(claims)-1):
                c1, c2 = claims[i], claims[i+1]
                diff = (datetime.strptime(c2.claimDate, '%Y-%m-%d') -
                        datetime.strptime(c1.claimDate, '%Y-%m-%d')).days
                if diff <= 7 and c1.amountClaimed > 10000 and c2.amountClaimed > 10000:
                    ph.status = 'POTENTIAL_FRAUD_REVIEW'
                    break

    def _rule_15_policy_discount(self):
        for ph in self.entities.get('policyholders', []):
            if len(ph.policies) >= 3:
                ph.eligibleForDiscount = 'MULTI_POLICY_DISCOUNT'

    # Phase 3: Analytics & Intelligence
    def generate_comprehensive_statistics(self) -> None:
        logging.info("Generating comprehensive statistics...")
        ph_list = self.entities.get('policyholders', [])
        pol_list = self.entities.get('policies', [])
        cov_list = self.entities.get('coverages', [])
        cl_list = self.entities.get('claims', [])

        # Basic counts
        self.stats['num_policyholders'] = len(ph_list)
        self.stats['num_policies'] = len(pol_list)
        self.stats['num_coverages'] = len(cov_list)
        self.stats['num_claims'] = len(cl_list)

        # Distributions
        self.stats['policy_status_distribution'] = dict(
            Counter(p.status for p in pol_list if p.status))
        self.stats['claim_status_distribution'] = dict(
            Counter(c.status for c in cl_list if c.status))

        # Averages
        self.stats['avg_policies_per_holder'] = (
            self.stats['num_policies'] / self.stats['num_policyholders']
            if self.stats['num_policyholders'] else 0
        )
        self.stats['avg_coverages_per_policy'] = (
            sum(len(p.coverages) for p in pol_list) / len(pol_list)
            if pol_list else 0
        )
        self.stats['avg_claims_per_policy'] = (
            sum(len(p.claims) for p in pol_list) / len(pol_list)
            if pol_list else 0
        )

        # Risk score metrics
        risk_scores = [
            ph.riskScore for ph in ph_list if ph.riskScore is not None]
        self.stats['avg_risk_score'] = (
            sum(risk_scores) / len(risk_scores)
            if risk_scores else 0
        )
        top_risk = sorted(
            ph_list, key=lambda x: x.riskScore or 0, reverse=True)[:5]
        self.stats['top_5_highest_risk_holders'] = [
            (ph.id, ph.riskScore) for ph in top_risk]

    def _generate_business_insights(self) -> None:
        logging.info("Generating business insights...")
        # Top 3 agents by commission (requires commission computed)
        agent_commissions = {a.id: sum(premium.premiumAmount for premium in a.policies) * 0.05
                             for a in self.entities.get('agents', [])}
        top_agents = sorted(agent_commissions.items(),
                            key=lambda x: x[1], reverse=True)[:3]
        self.insights['top_agents'] = [
            {'agent_id': aid, 'commission': comm} for aid, comm in top_agents]

        # Underwriter workload imbalance
        workloads = {u.id: len(u.policies)
                     for u in self.entities.get('underwriters', [])}
        if workloads:
            max_load = max(workloads.values())
            min_load = min(workloads.values())
            avg_load = sum(workloads.values()) / len(workloads)
            self.insights['underwriter_workload'] = {
                'max': max_load,
                'min': min_load,
                'avg': avg_load
            }

        # High claim frequency holders
        avg_claims_per_holder = (
            sum(len(ph.claims) for ph in self.entities.get('policyholders', [])) /
            len(self.entities.get('policyholders', []))
            if self.entities.get('policyholders', []) else 0
        )
        frequent_claimers = [ph.id for ph in self.entities.get('policyholders', [])
                             if len(ph.claims) > avg_claims_per_holder]
        self.insights['frequent_claimers'] = frequent_claimers

        # Policy type distribution
        types = [p.policyType for p in self.entities.get(
            'policies', []) if p.policyType]
        self.insights['policy_type_distribution'] = dict(Counter(types))

        # Insurer claim ratio
        insurer_claims = {}
        for ins in self.entities.get('insurers', []):
            claims_count = sum(len(p.claims) for p in ins.policies)
            insurer_claims[ins.id] = claims_count / \
                len(ins.policies) if ins.policies else 0
        self.insights['insurer_claim_ratios'] = insurer_claims

    def _calculate_performance_metrics(self) -> None:
        logging.info("Calculating performance metrics...")
        # (unchanged implementation)
        rules = [m for m in dir(self) if m.startswith('_rule_')]
        self.performance['rule_count'] = len(rules)
        self.performance['entity_counts'] = {
            k: len(v) for k, v in self.entities.items()}
        self.performance['dataframe_shapes'] = {
            k: df.shape for k, df in self.loader.raw_dfs.items()}
        ph_count = self.performance['entity_counts'].get('policyholders', 0)
        pol_count = self.performance['entity_counts'].get('policies', 0)
        total_coverages = sum(len(p.coverages)
                              for p in self.entities.get('policies', []))
        total_claims = sum(len(p.claims)
                           for p in self.entities.get('policies', []))
        self.performance['avg_coverages_per_policy'] = (
            total_coverages / pol_count) if pol_count else 0
        self.performance['avg_claims_per_policy'] = (
            total_claims / pol_count) if pol_count else 0
        self.performance['avg_policies_per_holder'] = (
            pol_count / ph_count) if ph_count else 0

    def _generate_strategic_recommendations(self) -> None:
        logging.info("Generating strategic recommendations...")
        # (unchanged implementation)
        if any(len(ph.policies) >= 3 for ph in self.entities.get('policyholders', [])):
            self.recommendations.append(
                "Promote multi-policy discount programs to increase retention."
            )
        high_risk = sum(
            1 for ph in self.entities.get('policyholders', [])
            if 'HighRiskPolicyHolder' in getattr(ph, 'classifications', [])
        )
        total_ph = self.performance['entity_counts'].get(
            'policyholders', len(self.entities.get('policyholders', [])))
        if total_ph and (high_risk / total_ph) > 0.2:
            self.recommendations.append(
                "Implement risk mitigation strategies for high-risk policyholders."
            )
        exceed_count = sum(
            1 for cl in self.entities.get('claims', [])
            if 'ExceedsCoverageLimit' in getattr(cl, 'classifications', [])
        )
        if exceed_count > 0:
            self.recommendations.append(
                "Review and adjust coverage limits to minimize uncovered claim amounts."
            )
        workloads = {uw.id: len(uw.policies)
                     for uw in self.entities.get('underwriters', [])}
        if workloads:
            max_load = max(workloads.values())
            avg_load = sum(workloads.values()) / len(workloads)
            self.performance['underwriter_max_load'] = max_load
            self.performance['underwriter_avg_load'] = avg_load
            if max_load > (avg_load * 1.5):
                self.recommendations.append(
                    "Balance underwriter workloads to prevent bottlenecks and burnout."
                )

    # Phase 4: Output Generation
    def export_json_report(self, filepath: str) -> None:
        """Export full reasoning results and stats to JSON file."""
        logging.info(f"Exporting JSON report to {filepath}...")
        # serialize each entity list
        serial_entities = {
            kind: [self._serialize(ent) for ent in lst]
            for kind, lst in self.entities.items()
        }
        report = {
            'entities':       serial_entities,
            'statistics':     self.stats,
            'insights':       self.insights,
            'performance':    self.performance,
            'recommendations': self.recommendations
        }
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

    def generate_markdown_report(self) -> str:
        logging.info("Generating Markdown report...")
        lines = [
            "# Reasoning Pipeline Report",
            "## Summary Statistics",
            *[f"- **{k}**: {v}" for k, v in self.stats.items()],
            "## Insights",
            *[f"- {k}: {v}" for k, v in self.insights.items()],
            "## Recommendations",
            *[f"- {r}" for r in self.recommendations]
        ]
        return "\n".join(lines)

    def load_and_run(self) -> None:
        """High-level entry: execute all phases end-to-end and export reports."""
        # Phase 1: Data Ingestion
        self.loader.load_all_data()
        # Phase 2: Ontological Processing
        self._create_entities_from_dataframes()
        self._build_relationship_mappings()
        self._compute_inverse_properties()
        self._calculate_derived_properties()
        self._validate_cardinality_constraints()
        self.apply_reasoning_rules()
        # Phase 3: Analytics & Intelligence
        self.generate_comprehensive_statistics()
        self._generate_business_insights()
        self._calculate_performance_metrics()
        self._generate_strategic_recommendations()
        # Phase 4: Output Generation
        json_path = os.path.join('.', 'report.json')
        markdown_path = os.path.join('.', 'report.md')
        # Export JSON report
        self.export_json_report(json_path)
        # Generate and write Markdown report
        md_content = self.generate_markdown_report()
        with open(markdown_path, 'w') as md_file:
            md_file.write(md_content)
        logging.info(f"JSON report written to {json_path}")
        logging.info(f"Markdown report written to {markdown_path}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loader = DataLoader()
    reasoner = Reasoner(loader)
    reasoner.load_and_run()
