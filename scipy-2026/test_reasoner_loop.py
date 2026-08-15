from reasoner_loop import BASE
from reasoner_loop import TinyRete
from reasoner_loop import TinyTMS
from reasoner_loop import backward
from reasoner_loop import description_logic
from reasoner_loop import forward
from reasoner_loop import propose_check_repair
from reasoner_loop import resolution_proves
from reasoner_loop import smt_meals
from reasoner_loop import stratified_negation


# Print a visible section heading before each reasoner trace.
def heading(name):
    print()
    print("TEST", name)


# Check forward materialization across animal, film, and music ontology classes.
def test_forward():
    heading("forward chaining")
    facts = forward(BASE, trace=True)
    assert ("type", "Fido", "Dog") in facts
    assert ("type", "Fido", "Mammal") in facts
    assert ("health_check", "Fido") in facts
    assert ("type", "Amelie", "CreativeWork") in facts
    assert ("type", "I Choose You", "Song") in facts
    assert ("type", "I Choose You", "CreativeWork") in facts


# Check backward proof search across animal, film, and music ontology classes.
def test_backward():
    heading("backward chaining")
    ok, proof = backward(("type", "Fido", "Mammal"), BASE, trace=True)
    assert ok
    assert proof == [
        ("type", "Fido", "Terrier"),
        ("type", "Fido", "Dog"),
        ("type", "Fido", "Mammal"),
    ]
    ok, proof = backward(("type", "Amelie", "CreativeWork"), BASE, trace=True)
    assert ok
    assert proof == [
        ("type", "Amelie", "Film"),
        ("type", "Amelie", "CreativeWork"),
    ]
    ok, proof = backward(("type", "I Choose You", "CreativeWork"), BASE, trace=True)
    assert ok
    assert proof == [
        ("song_by", "I Choose You", "Sara Bareilles"),
        ("type", "I Choose You", "Song"),
        ("type", "I Choose You", "CreativeWork"),
    ]


# Check RETE alpha memories and beta join for the health-check rule.
def test_rete():
    heading("RETE")
    rete = TinyRete(trace=True)
    rete.add(("type", "Fido", "Dog"))
    assert not rete.output
    rete.add(("age", "Fido", 12))
    assert ("health_check", "Fido") in rete.output


# Check truth maintenance retracts ontology conclusions that lose their justification.
def test_truth_maintenance():
    heading("truth maintenance")
    terrier = ("type", "Fido", "Terrier")
    dog = ("type", "Fido", "Dog")
    mammal = ("type", "Fido", "Mammal")
    tms = TinyTMS(trace=True)
    tms.add(terrier)
    tms.derive(dog, [terrier])
    tms.derive(mammal, [dog])
    assert mammal in tms.facts
    tms.remove(terrier)
    assert dog not in tms.facts
    assert mammal not in tms.facts


# Check description-logic classification and disjoint-class inconsistency detection.
def test_description_logic():
    heading("description logic")
    types, clashes = description_logic(BASE, trace=True)
    assert types["Fido"] == {"Terrier", "Dog", "Mammal"}
    assert types["Amelie"] == {"Film", "CreativeWork"}
    assert types["I Choose You"] == {"Song", "CreativeWork"}
    assert not clashes
    print("TRACE description_logic: add conflicting class assertion Fido rdf:type Reptile")
    _, clashes = description_logic(BASE | {("type", "Fido", "Reptile")}, trace=True)
    assert clashes == [("Fido", "Mammal", "Reptile")]


# Check stratified negation evaluates absence only after positive facts are fixed.
def test_stratified_negation():
    heading("stratified negation")
    facts = stratified_negation(BASE, trace=True)
    assert ("may_enter", "Fido") in facts
    print("TRACE stratified_negation: add lower-stratum fact dangerous(Fido)")
    facts = stratified_negation(BASE | {("dangerous", "Fido")}, trace=True)
    assert ("may_enter", "Fido") not in facts


# Check resolution proves selected ontology entailments by refutation.
def test_resolution():
    heading("resolution")
    assert resolution_proves("Mammal(Fido)", trace=True)
    assert resolution_proves("CreativeWork(Amelie)", trace=True)
    assert resolution_proves("CreativeWork(IChooseYou)", trace=True)
    assert not resolution_proves("Reptile(Fido)", trace=True)


# Check the toy SMT solver finds or rejects a model for Fido's meal constraints.
def test_smt():
    heading("satisfiability modulo theories")
    model = smt_meals(trace=True)
    assert model is not None
    assert model["meals"] in (2, 3)
    print("TRACE smt: add incompatible requirement meals == 4")
    assert smt_meals(require_four=True, trace=True) is None


# Check multiple reasoners compose inside the propose-check-repair interaction pattern.
def test_loop():
    heading("propose-check-repair")
    assert propose_check_repair(("type", "Fido", "Mammal"), trace=True)["status"] == "accept"
    assert propose_check_repair(("type", "Fido", "Reptile"), trace=True)["status"] == "repair"
    assert propose_check_repair(("type", "Amelie", "CreativeWork"), trace=True)["status"] == "accept"
    assert propose_check_repair(("type", "I Choose You", "CreativeWork"), trace=True)["status"] == "accept"
    assert propose_check_repair(("health_check", "Fido"), trace=True)["status"] == "accept"
    assert propose_check_repair(("may_enter", "Fido"), trace=True)["status"] == "accept"


# Run all toy reasoners so each test prints its reasoning trace before PASS.
def run():
    tests = [
        test_forward,
        test_backward,
        test_rete,
        test_truth_maintenance,
        test_description_logic,
        test_stratified_negation,
        test_resolution,
        test_smt,
        test_loop,
    ]
    for test in tests:
        test()
        print("PASS", test.__name__)


if __name__ == "__main__":
    run()
