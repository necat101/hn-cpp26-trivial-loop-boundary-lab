import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).parent.parent
FIXTURES = ROOT / "fixtures" / "cases.json"
EVALUATOR = ROOT / "evaluator.py"


def load_cases():
    return json.loads(FIXTURES.read_text())


def load_results():
    # Run evaluator fresh for test isolation
    import importlib.util, sys
    spec = importlib.util.spec_from_file_location("evaluator_under_test", EVALUATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = load_cases()
    return {r["id"]: r for r in [mod.classify(c) for c in cases]}, {c["id"]: c for c in cases}


class TestCpp26Boundary(unittest.TestCase):

    def test_no_overall_verdict(self):
        results, _ = load_results()
        forbidden = {"cpp26_safe", "portable", "compliant", "overall", "standards_compliant", "is_safe"}
        for rid, r in results.items():
            for k in r.keys():
                self.assertNotIn(k.lower(), forbidden, f"{rid} must not emit overall verdict field {k}")
                # also check no boolean overall field
            self.assertNotIn("verdict", r)

    def test_separate_outputs_present(self):
        results, _ = load_results()
        required = ["trivially_empty", "condition_is_constant_expression", "condition_constant_value", "trivial_infinite_loop", "environment", "yield_replacement_status", "compiler_support_claim"]
        for rid, r in results.items():
            for k in required:
                self.assertIn(k, r, f"{rid} missing {k}")

    def test_independent_oracle_matches(self):
        """Independent re-derivation from raw record without calling evaluator decision helpers."""
        results, cases = load_results()
        for rid, rec in cases.items():
            r = results[rid]
            # Raw facts
            body_empty = bool(rec["body_is_trivially_empty"])
            is_const = bool(rec["condition_is_constant_expression"])
            const_val = rec.get("condition_constant_value")
            env = rec.get("environment", "hosted")
            # Independent trivial_infinite_loop
            expected_til = bool(body_empty and is_const and const_val is True)
            self.assertEqual(r["trivial_infinite_loop"], expected_til, f"{rid} trivial_infinite_loop")
            self.assertEqual(r["trivially_empty"], body_empty, f"{rid} trivially_empty")
            self.assertEqual(r["condition_is_constant_expression"], is_const, f"{rid} const")
            self.assertEqual(r["condition_constant_value"], (const_val if is_const else None), f"{rid} const value")
            # yield status
            if not expected_til:
                exp_yield = "not_applicable"
            elif env == "hosted":
                exp_yield = "replaced_with_yield"
            elif env == "freestanding":
                exp_yield = "implementation_defined"
            else:
                exp_yield = "unknown_environment"
            self.assertEqual(r["yield_replacement_status"], exp_yield, f"{rid} yield")

    def test_trivially_empty_cases(self):
        results, _ = load_results()
        self.assertTrue(results["while_true_semicolon_hosted"]["trivially_empty"])
        self.assertTrue(results["while_true_empty_braces_hosted"]["trivially_empty"])
        self.assertFalse(results["while_true_string_literal_body"]["trivially_empty"])
        self.assertFalse(results["while_true_continue_body"]["trivially_empty"])
        self.assertFalse(results["runtime_infinite_not_trivial"]["trivially_empty"])

    def test_useless_statement_not_trivial(self):
        results, _ = load_results()
        self.assertFalse(results["while_true_string_literal_body"]["trivial_infinite_loop"],
                         "string literal body destroys trivially-empty")
        self.assertFalse(results["while_true_continue_body"]["trivial_infinite_loop"],
                         "continue destroys trivially-empty")

    def test_implicit_true_for(self):
        results, _ = load_results()
        r = results["for_empty_implicit_true_hosted"]
        self.assertTrue(r["condition_is_constant_expression"])
        self.assertTrue(r["condition_constant_value"] is True)
        self.assertTrue(r["trivially_empty"])
        self.assertTrue(r["trivial_infinite_loop"])

    def test_non_constant_not_trivial(self):
        results, _ = load_results()
        r = results["while_non_const_condition_empty"]
        self.assertTrue(r["trivially_empty"])
        self.assertFalse(r["condition_is_constant_expression"])
        self.assertIsNone(r["condition_constant_value"])
        self.assertFalse(r["trivial_infinite_loop"])
        self.assertEqual(r["yield_replacement_status"], "not_applicable")

    def test_runtime_infinite_not_trivial(self):
        results, _ = load_results()
        r = results["runtime_infinite_not_trivial"]
        self.assertFalse(r["trivially_empty"])
        self.assertFalse(r["trivial_infinite_loop"])
        self.assertEqual(r["yield_replacement_status"], "not_applicable")

    def test_constexpr_true_qualifies(self):
        results, _ = load_results()
        r = results["constexpr_true_hosted"]
        self.assertTrue(r["trivially_empty"])
        self.assertTrue(r["condition_is_constant_expression"])
        self.assertTrue(r["trivial_infinite_loop"])
        self.assertEqual(r["yield_replacement_status"], "replaced_with_yield")

    def test_hosted_vs_freestanding_yield(self):
        results, _ = load_results()
        hosted = results["qualifying_hosted_yield"]
        free = results["qualifying_freestanding_impl_defined"]
        self.assertTrue(hosted["trivial_infinite_loop"])
        self.assertTrue(free["trivial_infinite_loop"])
        self.assertEqual(hosted["yield_replacement_status"], "replaced_with_yield")
        self.assertEqual(free["yield_replacement_status"], "implementation_defined")
        self.assertEqual(hosted["environment"], "hosted")
        self.assertEqual(free["environment"], "freestanding")

    def test_constant_false_not_trivial(self):
        results, _ = load_results()
        r = results["while_constexpr_false_empty"]
        self.assertTrue(r["trivially_empty"])
        self.assertTrue(r["condition_is_constant_expression"])
        self.assertIs(r["condition_constant_value"], False)
        self.assertFalse(r["trivial_infinite_loop"])

    def test_compiler_claim_not_normative(self):
        results, _ = load_results()
        for rid, r in results.items():
            csc = r["compiler_support_claim"]
            self.assertIn("claim", csc)
            self.assertIn("is_normative", csc)
            self.assertFalse(csc["is_normative"], f"{rid} compiler claim must not be normative")

    def test_do_while_variant(self):
        results, _ = load_results()
        r = results["do_while_true_empty_braces_hosted"]
        self.assertTrue(r["trivial_infinite_loop"])
        self.assertEqual(r["yield_replacement_status"], "replaced_with_yield")
