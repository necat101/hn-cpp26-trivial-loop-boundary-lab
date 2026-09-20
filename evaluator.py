#!/usr/bin/env python3
"""
Deterministic classifier for P2809R3 trivial infinite loop boundary.

Boundary: trivial infinite loop ≠ arbitrary nonterminating loop ≠ busy wait
          ≠ hosted replacement ≠ freestanding replacement ≠ compiler support

Primary normative source: WG21 P2809R3 (isocpp.org/files/papers/P2809R3.html)
  - A trivially empty iteration statement has empty body (semicolon or {} only)
  - A trivial infinite loop is such a statement whose converted controlling
    expression is a constant expression evaluating to true
  - for(;;) gets implicit true
  - Qualifying loop's body is replaced with std::this_thread::yield()
  - On freestanding, whether replacement occurs is implementation-defined
  - A loop merely happening never to terminate at runtime is NOT automatically trivial

No C++ compiler invoked, no binaries run, no hardware inspected — synthetic loop
records only, stdlib only. Produces per-case separate outputs; never an overall
"C++26 safe / portable / compliant" verdict.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
FIXTURES = ROOT / "fixtures" / "cases.json"
RESULTS_JSON = ROOT / "results.json"
RESULTS_MD = ROOT / "RESULTS.md"


def classify(rec: dict) -> dict:
    rid = rec["id"]
    body_is_empty = bool(rec["body_is_trivially_empty"])
    is_const = bool(rec["condition_is_constant_expression"])
    const_val = rec.get("condition_constant_value")
    env = rec.get("environment", "hosted")
    compiler_claim = rec.get("compiler_claim")

    # trivially_empty — directly from record's syntactic fact
    trivially_empty = body_is_empty

    # condition_is_constant_expression — from record
    condition_is_constant_expression = is_const

    # condition_constant_value — from record; None when not constant
    condition_constant_value = const_val if is_const else None
    # Normalize: if declared constant but value missing, treat as None to avoid false positive
    if is_const and const_val is None:
        # record says constant but no value — keep None; loop not trivial
        pass

    # trivial_infinite_loop — P2809R3 narrow conjunction:
    #   trivially empty AND controlling expression is constant expression evaluating to true
    # for(;;) implicit true is already encoded as condition_is_constant_expression=true + value=true
    trivial_infinite_loop = bool(trivially_empty and is_const and const_val is True)

    # yield_replacement_status — P2809R3 §6:
    #   "The statement of a trivial infinite loop is replaced with a call to yield;
    #    it is implementation-defined whether this replacement occurs on freestanding."
    if not trivial_infinite_loop:
        yield_replacement_status = "not_applicable"
    elif env == "hosted":
        yield_replacement_status = "replaced_with_yield"
    elif env == "freestanding":
        yield_replacement_status = "implementation_defined"
    else:
        yield_replacement_status = "unknown_environment"

    # compiler_support_claim — implementation evidence, NOT normative rule
    if compiler_claim:
        compiler_support_claim = {
            "claim": compiler_claim,
            "is_normative": False,
            "note": "Compiler-vendor claim is implementation-support evidence only; does not prove standard requires identical behavior on every compiler/version/mode."
        }
    else:
        compiler_support_claim = {
            "claim": None,
            "is_normative": False,
            "note": "No compiler support claim asserted for this case."
        }

    return {
        "id": rid,
        "trivially_empty": trivially_empty,
        "condition_is_constant_expression": condition_is_constant_expression,
        "condition_constant_value": condition_constant_value,
        "trivial_infinite_loop": trivial_infinite_loop,
        "environment": env,
        "yield_replacement_status": yield_replacement_status,
        "compiler_support_claim": compiler_support_claim,
    }


def main():
    cases = json.loads(FIXTURES.read_text())
    results = [classify(c) for c in cases]
    RESULTS_JSON.write_text(json.dumps(results, indent=2) + "\n")

    lines = []
    lines.append("# hn-cpp26-trivial-loop-boundary-lab — Results")
    lines.append("")
    lines.append(f"Cases: {len(results)}")
    lines.append("")
    lines.append("| id | trivially_empty | const_expr | const_value | trivial_infinite_loop | environment | yield_replacement |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in results:
        lines.append(
            f"| {r['id']} | {r['trivially_empty']} | {r['condition_is_constant_expression']} | {r['condition_constant_value']} | {r['trivial_infinite_loop']} | {r['environment']} | {r['yield_replacement_status']} |"
        )
    lines.append("")
    lines.append("## P2809R3 boundary (checked per case)")
    lines.append("")
    lines.append("- Trivial infinite loop requires BOTH: trivially empty body AND controlling expression is constant expression evaluating to true.")
    lines.append("- Adding even an otherwise useless statement (e.g. `\"x\";` or `continue;`) destroys trivially-empty.")
    lines.append("- `for(;;)` controlling expression is `true` if absent (implicit true).")
    lines.append("- A loop that merely happens never to terminate at runtime is not automatically trivial.")
    lines.append("- Qualifying hosted loop: body replaced with `std::this_thread::yield();`")
    lines.append("- Qualifying freestanding loop: whether replacement occurs is implementation-defined.")
    lines.append("- Compiler support claim is implementation-support evidence only, not normative standard status.")
    lines.append("")
    lines.append("## No overall verdict")
    lines.append("")
    lines.append("No single `cpp26_safe` / `portable` / `compliant` field is emitted. Consumers must read the separate axes above.")
    lines.append("")
    lines.append("## Per-case axes")
    lines.append("")
    for r in results:
        lines.append(
            f"- **{r['id']}**: trivially_empty={r['trivially_empty']}, const_expr={r['condition_is_constant_expression']}, "
            f"const_value={r['condition_constant_value']}, trivial_infinite_loop={r['trivial_infinite_loop']}, "
            f"environment={r['environment']}, yield={r['yield_replacement_status']}, compiler_claim={r['compiler_support_claim']['claim']}"
        )
    lines.append("")
    RESULTS_MD.write_text("\n".join(lines) + "\n")
    print(f"Wrote {RESULTS_JSON} and {RESULTS_MD} ({len(results)} cases)")


if __name__ == "__main__":
    main()
