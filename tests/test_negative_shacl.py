import pytest
from rdflib import Graph
import os

from runtime.kernel_gate import validate_abox

# Fixtures for loading negative examples
@pytest.fixture
def abox_targetref_missing_isaboutentity():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'negative_examples', 'targetref_missing_isaboutentity.ttl')
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def abox_targetref_two_isaboutentity():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'negative_examples', 'targetref_two_isaboutentity.ttl')
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def abox_stipulation_two_stipulateson():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'negative_examples', 'stipulation_two_stipulateson.ttl')
    # This example needs its dummy TargetRefs, so ensure they are included or pass a combined graph
    # For simplicity, we assume this file already contains the necessary context to be self-contained for validation.
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def abox_evaluator_missing_measurementspec():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'negative_examples', 'evaluator_missing_measurementspec.ttl')
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def abox_restriction_missing_ruleexpression():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'negative_examples', 'restriction_missing_ruleexpression.ttl')
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def abox_promotionrecord_two_truthassertions():
    file_path = os.path.join(os.path.dirname(__file__), '..', 'ontology', 'negative_examples', 'promotionrecord_two_truthassertions.ttl')
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Test functions for each negative scenario
def test_targetref_missing_isaboutentity_fails(abox_targetref_missing_isaboutentity):
    conforms, _, results_text = validate_abox(abox_targetref_missing_isaboutentity)
    assert conforms is False, f"Expected validation failure, but got success:\n{results_text}"
    assert "Less than 1 values on" in results_text
    assert "kern:isAboutEntity" in results_text

def test_targetref_two_isaboutentity_fails(abox_targetref_two_isaboutentity):
    conforms, _, results_text = validate_abox(abox_targetref_two_isaboutentity)
    assert conforms is False, f"Expected validation failure, but got success:\n{results_text}"
    assert "More than 1 values on" in results_text
    assert "kern:isAboutEntity" in results_text

def test_stipulation_two_stipulateson_fails(abox_stipulation_two_stipulateson):
    conforms, _, results_text = validate_abox(abox_stipulation_two_stipulateson)
    assert conforms is False, f"Expected validation failure, but got success:\n{results_text}"
    assert "More than 1 values on" in results_text
    assert "kern:stipulatesOn" in results_text

def test_evaluator_missing_measurementspec_fails(abox_evaluator_missing_measurementspec):
    conforms, _, results_text = validate_abox(abox_evaluator_missing_measurementspec)
    assert conforms is False, f"Expected validation failure, but got success:\n{results_text}"
    assert "ex:NegativeEvaluatorStipulation_1" in results_text # Check for the specific node

def test_restriction_missing_ruleexpression_fails(abox_restriction_missing_ruleexpression):
    conforms, _, results_text = validate_abox(abox_restriction_missing_ruleexpression)
    assert conforms is False, f"Expected validation failure, but got success:\n{results_text}"
    assert "ex:NegativeRestrictionStipulation_1" in results_text # Check for the specific node

def test_promotionrecord_two_truthassertions_fails(abox_promotionrecord_two_truthassertions):
    conforms, _, results_text = validate_abox(abox_promotionrecord_two_truthassertions)
    assert conforms is False, f"Expected validation failure, but got success:\n{results_text}"
    assert "More than 1 values on" in results_text
    assert "kern:producesAcceptedAssertion" in results_text
