# Ontology subclass axioms used by all toy reasoners.
SUBCLASS = {
    "Terrier": "Dog",
    "Dog": "Mammal",
    "Film": "CreativeWork",
    "Song": "CreativeWork",
}

# Ontology property-domain axioms used to infer class membership.
PROPERTY_DOMAIN = {
    "song_by": "Song",
}

# Base assertions span animal, film, and music domains.
BASE = {
    ("type", "Fido", "Terrier"),
    ("age", "Fido", 12),
    ("type", "Amelie", "Film"),
    ("song_by", "I Choose You", "Sara Bareilles"),
}

# Ontology disjointness axiom used for consistency checking.
DISJOINT = {
    ("Mammal", "Reptile"),
}


# Render one fact using ontology-style terms used in the paper.
def fact_text(fact):
    if fact[0] == "type":
        return f"{fact[1]} rdf:type {fact[2]}"
    if fact[0] == "song_by":
        return f"{fact[1]} song_by {fact[2]}"
    if fact[0] == "age":
        return f"{fact[1]} age {fact[2]}"
    if len(fact) == 2:
        return f"{fact[0]}({fact[1]})"
    return str(fact)


# Print one reasoning trace line when tracing is enabled.
def emit_trace(enabled, reasoner, message):
    if enabled:
        print(f"TRACE {reasoner}: {message}")


# Derive ontology facts by repeated forward rule application to a fixpoint.
def forward(facts, trace=False):
    facts = set(facts)
    emit_trace(trace, "forward", "start from asserted facts")
    changed = True
    while changed:
        changed = False
        for fact in list(facts):
            if fact[0] in PROPERTY_DOMAIN:
                cls = PROPERTY_DOMAIN[fact[0]]
                new = ("type", fact[1], cls)
                if new not in facts:
                    emit_trace(trace, "forward", f"domain axiom: {fact[0]} rdfs:domain {cls}")
                    emit_trace(trace, "forward", f"infer class assertion: {fact_text(new)}")
                    facts.add(new)
                    changed = True
            if fact[0] == "type" and fact[2] in SUBCLASS:
                parent = SUBCLASS[fact[2]]
                new = ("type", fact[1], parent)
                if new not in facts:
                    emit_trace(trace, "forward", f"subclass axiom: {fact[2]} rdfs:subClassOf {parent}")
                    emit_trace(trace, "forward", f"infer class assertion: {fact_text(new)}")
                    facts.add(new)
                    changed = True
        for fact in list(facts):
            if fact[0] == "age" and fact[2] > 10:
                dog = ("type", fact[1], "Dog")
                new = ("health_check", fact[1])
                if dog in facts and new not in facts:
                    emit_trace(trace, "forward", "rule: Dog(x) and age(x) > 10 -> health_check(x)")
                    emit_trace(trace, "forward", f"infer rule conclusion: {fact_text(new)}")
                    facts.add(new)
                    changed = True
    emit_trace(trace, "forward", f"fixpoint reached with {len(facts)} facts")
    return facts


# Prove one ontology goal by searching backward for supporting assertions and axioms.
def backward(goal, facts, seen=None, trace=False, depth=0):
    facts = set(facts)
    seen = set() if seen is None else set(seen)
    prefix = "  " * depth
    emit_trace(trace, "backward", f"{prefix}goal: {fact_text(goal)}")
    if goal in facts:
        emit_trace(trace, "backward", f"{prefix}found asserted fact")
        return True, [goal]
    if goal in seen:
        emit_trace(trace, "backward", f"{prefix}stop repeated goal")
        return False, []
    seen.add(goal)
    if goal[0] == "type":
        entity, target = goal[1], goal[2]
        for predicate, cls in PROPERTY_DOMAIN.items():
            if cls == target:
                matches = [f for f in facts if f[0] == predicate and f[1] == entity]
                if matches:
                    emit_trace(trace, "backward", f"{prefix}use domain axiom: {predicate} rdfs:domain {cls}")
                    emit_trace(trace, "backward", f"{prefix}support: {fact_text(matches[0])}")
                    return True, [matches[0], goal]
        for child, parent in SUBCLASS.items():
            if parent == target:
                subgoal = ("type", entity, child)
                emit_trace(trace, "backward", f"{prefix}use subclass axiom: {child} rdfs:subClassOf {parent}")
                ok, proof = backward(subgoal, facts, seen, trace, depth + 1)
                if ok:
                    emit_trace(trace, "backward", f"{prefix}entailed: {fact_text(goal)}")
                    return True, proof + [goal]
    if goal[0] == "health_check":
        entity = goal[1]
        subgoal = ("type", entity, "Dog")
        emit_trace(trace, "backward", f"{prefix}use rule: Dog(x) and age(x) > 10 -> health_check(x)")
        ok, proof = backward(subgoal, facts, seen, trace, depth + 1)
        ages = [f for f in facts if f[0] == "age" and f[1] == entity and f[2] > 10]
        if ok and ages:
            emit_trace(trace, "backward", f"{prefix}support: {fact_text(ages[0])}")
            return True, proof + [ages[0], goal]
    emit_trace(trace, "backward", f"{prefix}goal not proved")
    return False, []


# Keep RETE-style partial matches for the Fido health-check rule.
class TinyRete:
    # Create alpha memories and the terminal output memory.
    def __init__(self, trace=False):
        self.dogs = set()
        self.old = set()
        self.output = set()
        self.trace = trace

    # Add one fact, update alpha memories, and join matching partial bindings.
    def add(self, fact):
        emit_trace(self.trace, "rete", f"assert fact: {fact_text(fact)}")
        if fact[0] == "type" and fact[2] == "Dog":
            self.dogs.add(fact[1])
            emit_trace(self.trace, "rete", f"alpha memory Dog(x): bind x={fact[1]}")
        if fact[0] == "age" and fact[2] > 10:
            self.old.add(fact[1])
            emit_trace(self.trace, "rete", f"alpha memory age(x)>10: bind x={fact[1]}")
        entity = fact[1]
        if entity in self.dogs and entity in self.old:
            new = ("health_check", entity)
            if new not in self.output:
                emit_trace(self.trace, "rete", f"beta join on x={entity}")
                emit_trace(self.trace, "rete", f"fire rule conclusion: {fact_text(new)}")
                self.output.add(new)


# Track ontology assertions and justifications so unsupported conclusions can be retracted.
class TinyTMS:
    # Create the fact store and justification store for the toy truth-maintenance system.
    def __init__(self, trace=False):
        self.facts = set()
        self.supports = {}
        self.trace = trace

    # Add one asserted ontology fact.
    def add(self, fact):
        self.facts.add(fact)
        emit_trace(self.trace, "tms", f"assert base fact: {fact_text(fact)}")

    # Add one derived fact with the facts that justify it.
    def derive(self, fact, support):
        support = tuple(support)
        if all(item in self.facts for item in support):
            self.facts.add(fact)
            self.supports.setdefault(fact, []).append(support)
            text = ", ".join(fact_text(item) for item in support)
            emit_trace(self.trace, "tms", f"derive {fact_text(fact)} because [{text}]")

    # Retract one fact and cascade through conclusions that lose every justification.
    def remove(self, fact):
        self.facts.discard(fact)
        emit_trace(self.trace, "tms", f"retract fact: {fact_text(fact)}")
        changed = True
        while changed:
            changed = False
            for derived, alternatives in self.supports.items():
                if derived not in self.facts:
                    continue
                valid = any(all(item in self.facts for item in support) for support in alternatives)
                if not valid:
                    self.facts.remove(derived)
                    emit_trace(self.trace, "tms", f"retract unsupported conclusion: {fact_text(derived)}")
                    changed = True


# Classify individuals with ontology axioms and report disjoint-class inconsistencies.
def description_logic(facts, trace=False):
    types = {}
    for fact in facts:
        if fact[0] == "type":
            types.setdefault(fact[1], set()).add(fact[2])
            emit_trace(trace, "description_logic", f"class assertion: {fact_text(fact)}")
        if fact[0] in PROPERTY_DOMAIN:
            cls = PROPERTY_DOMAIN[fact[0]]
            types.setdefault(fact[1], set()).add(cls)
            emit_trace(trace, "description_logic", f"domain axiom: {fact[0]} rdfs:domain {cls}")
            emit_trace(trace, "description_logic", f"classify {fact[1]} as {cls}")
    changed = True
    while changed:
        changed = False
        for entity, classes in list(types.items()):
            for child in list(classes):
                if child in SUBCLASS:
                    parent = SUBCLASS[child]
                    if parent not in classes:
                        classes.add(parent)
                        emit_trace(trace, "description_logic", f"subsumption: {child} rdfs:subClassOf {parent}")
                        emit_trace(trace, "description_logic", f"classify {entity} as {parent}")
                        changed = True
    clashes = []
    for left, right in DISJOINT:
        emit_trace(trace, "description_logic", f"disjointness axiom: {left} disjointWith {right}")
    for entity, classes in types.items():
        for left, right in DISJOINT:
            if left in classes and right in classes:
                clash = (entity, left, right)
                clashes.append(clash)
                emit_trace(trace, "description_logic", f"inconsistency: {entity} is both {left} and {right}")
    return types, clashes


# Evaluate negation only after the positive ontology stratum reaches a fixpoint.
def stratified_negation(facts, trace=False):
    lower = forward(facts)
    result = set(lower)
    emit_trace(trace, "stratified_negation", "stratum 0 complete: positive facts are fixed")
    dogs = {f[1] for f in lower if f[0] == "type" and f[2] == "Dog"}
    dangerous = {f[1] for f in lower if f[0] == "dangerous"}
    for entity in dogs:
        emit_trace(trace, "stratified_negation", f"evaluate not dangerous({entity}) in completed lower stratum")
        if entity not in dangerous:
            new = ("may_enter", entity)
            result.add(new)
            emit_trace(trace, "stratified_negation", f"infer rule conclusion: {fact_text(new)}")
        else:
            emit_trace(trace, "stratified_negation", f"block permission because dangerous({entity}) is present")
    return result


# Return the logical complement of one ground literal.
def complement(literal):
    return literal[1:] if literal.startswith("~") else "~" + literal


# Resolve two ground clauses on each complementary literal pair.
def resolve(left, right):
    out = set()
    for literal in left:
        other = complement(literal)
        if other in right:
            out.add(frozenset((left - {literal}) | (right - {other})))
    return out


# Render one resolution clause for a compact proof trace.
def clause_text(clause):
    return " OR ".join(sorted(clause)) if clause else "EMPTY"


# Prove a ground ontology claim by adding its negation and deriving the empty clause.
def resolution_proves(goal, trace=False):
    clauses = {
        frozenset({"Terrier(Fido)"}),
        frozenset({"~Terrier(Fido)", "Dog(Fido)"}),
        frozenset({"~Dog(Fido)", "Mammal(Fido)"}),
        frozenset({"Film(Amelie)"}),
        frozenset({"~Film(Amelie)", "CreativeWork(Amelie)"}),
        frozenset({"SongBy(IChooseYou,SaraBareilles)"}),
        frozenset({"~SongBy(IChooseYou,SaraBareilles)", "Song(IChooseYou)"}),
        frozenset({"~Song(IChooseYou)", "CreativeWork(IChooseYou)"}),
        frozenset({complement(goal)}),
    }
    emit_trace(trace, "resolution", f"query claim: {goal}")
    emit_trace(trace, "resolution", f"add negated claim: {complement(goal)}")
    while True:
        current = list(clauses)
        new = set()
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                for clause in resolve(current[i], current[j]):
                    if clause not in clauses and clause not in new:
                        emit_trace(
                            trace,
                            "resolution",
                            f"resolve [{clause_text(current[i])}] with [{clause_text(current[j])}] -> [{clause_text(clause)}]",
                        )
                    if not clause:
                        emit_trace(trace, "resolution", "empty clause derived: claim is entailed")
                        return True
                    new.add(clause)
        new -= clauses
        if not new:
            emit_trace(trace, "resolution", "no empty clause: claim is not proved")
            return False
        clauses |= new


# Evaluate one arithmetic theory atom for a concrete Fido meal count.
def theory_holds(atom, meals):
    if atom == "at_least_2":
        return meals >= 2
    if atom == "at_most_4":
        return meals <= 4
    if atom == "cost_at_most_9":
        return meals * 3 <= 9
    if atom == "exactly_4":
        return meals == 4
    return False


# Evaluate one Boolean clause under a partial assignment.
def clause_value(clause, assignment):
    undecided = False
    for literal in clause:
        name = literal[1:] if literal.startswith("~") else literal
        if name not in assignment:
            undecided = True
            continue
        value = assignment[name]
        if literal.startswith("~"):
            value = not value
        if value:
            return True
    return None if undecided else False


# Find a concrete meal count that satisfies the current theory assignment.
def theory_model(assignment):
    for meals in range(0, 6):
        if all(theory_holds(atom, meals) == truth for atom, truth in assignment.items()):
            return meals
    return None


# Search Boolean assignments and use the arithmetic theory check to prune them.
def dpll_t(clauses, atoms, assignment=None, trace=False, depth=0):
    assignment = {} if assignment is None else dict(assignment)
    prefix = "  " * depth
    meals = theory_model(assignment)
    if meals is None:
        emit_trace(trace, "smt", f"{prefix}theory conflict for assignment {assignment}")
        return None
    values = [clause_value(clause, assignment) for clause in clauses]
    if False in values:
        emit_trace(trace, "smt", f"{prefix}Boolean clause conflict")
        return None
    if all(value is True for value in values):
        emit_trace(trace, "smt", f"{prefix}model found: meals={meals}")
        return {"meals": meals}
    for atom in atoms:
        if atom not in assignment:
            for truth in (True, False):
                assignment[atom] = truth
                emit_trace(trace, "smt", f"{prefix}try theory atom {atom}={truth}")
                model = dpll_t(clauses, atoms, assignment, trace, depth + 1)
                if model is not None:
                    return model
            return None
    return None


# Solve the toy Satisfiability Modulo Theories constraints for Fido's meals.
def smt_meals(require_four=False, trace=False):
    atoms = ["at_least_2", "at_most_4", "cost_at_most_9", "exactly_4"]
    clauses = [["at_least_2"], ["at_most_4"], ["cost_at_most_9"]]
    emit_trace(trace, "smt", "constraint: meals >= 2")
    emit_trace(trace, "smt", "constraint: meals <= 4")
    emit_trace(trace, "smt", "constraint: meals * 3 <= 9")
    if require_four:
        clauses.append(["exactly_4"])
        emit_trace(trace, "smt", "constraint: meals == 4")
    return dpll_t(clauses, atoms, trace=trace)


# Compose toy reasoners as tools in the paper's propose-check-repair loop.
def propose_check_repair(proposal, facts=None, trace=False):
    facts = BASE if facts is None else set(facts)
    emit_trace(trace, "loop", f"propose: {fact_text(proposal)}")
    if proposal[0] == "type":
        emit_trace(trace, "loop", "check with backward ontology reasoning")
        ok, proof = backward(proposal, facts, trace=trace)
        status = "accept" if ok else "repair"
        emit_trace(trace, "loop", f"decision: {status}")
        return {"status": status, "evidence": proof}
    if proposal[0] == "health_check":
        emit_trace(trace, "loop", "check with forward rule materialization")
        ok = proposal in forward(facts, trace=trace)
        status = "accept" if ok else "repair"
        emit_trace(trace, "loop", f"decision: {status}")
        return {"status": status, "evidence": []}
    if proposal[0] == "may_enter":
        emit_trace(trace, "loop", "check with stratified negation")
        ok = proposal in stratified_negation(facts, trace=trace)
        status = "accept" if ok else "repair"
        emit_trace(trace, "loop", f"decision: {status}")
        return {"status": status, "evidence": []}
    if proposal[0] == "meals":
        emit_trace(trace, "loop", "check with SMT constraints")
        model = smt_meals(trace=trace)
        ok = model is not None and proposal[2] == model["meals"]
        status = "accept" if ok else "repair"
        emit_trace(trace, "loop", f"decision: {status}")
        return {"status": status, "evidence": model}
    emit_trace(trace, "loop", "no matching formal checker")
    emit_trace(trace, "loop", "decision: repair")
    return {"status": "repair", "evidence": []}
