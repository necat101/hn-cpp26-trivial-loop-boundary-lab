# hn-cpp26-trivial-loop-boundary-lab — Results

Cases: 12

| id | trivially_empty | const_expr | const_value | trivial_infinite_loop | environment | yield_replacement |
|---|---|---|---|---|---|---|
| while_true_semicolon_hosted | True | True | True | True | hosted | replaced_with_yield |
| while_true_empty_braces_hosted | True | True | True | True | hosted | replaced_with_yield |
| for_empty_implicit_true_hosted | True | True | True | True | hosted | replaced_with_yield |
| do_while_true_empty_braces_hosted | True | True | True | True | hosted | replaced_with_yield |
| constexpr_true_hosted | True | True | True | True | hosted | replaced_with_yield |
| while_true_string_literal_body | False | True | True | False | hosted | not_applicable |
| while_non_const_condition_empty | True | False | None | False | hosted | not_applicable |
| runtime_infinite_not_trivial | False | True | True | False | hosted | not_applicable |
| qualifying_hosted_yield | True | True | True | True | hosted | replaced_with_yield |
| qualifying_freestanding_impl_defined | True | True | True | True | freestanding | implementation_defined |
| while_constexpr_false_empty | True | True | False | False | hosted | not_applicable |
| while_true_continue_body | False | True | True | False | hosted | not_applicable |

## P2809R3 boundary (checked per case)

- Trivial infinite loop requires BOTH: trivially empty body AND controlling expression is constant expression evaluating to true.
- Adding even an otherwise useless statement (e.g. `"x";` or `continue;`) destroys trivially-empty.
- `for(;;)` controlling expression is `true` if absent (implicit true).
- A loop that merely happens never to terminate at runtime is not automatically trivial.
- Qualifying hosted loop: body replaced with `std::this_thread::yield();`
- Qualifying freestanding loop: whether replacement occurs is implementation-defined.
- Compiler support claim is implementation-support evidence only, not normative standard status.

## No overall verdict

No single `cpp26_safe` / `portable` / `compliant` field is emitted. Consumers must read the separate axes above.

## Per-case axes

- **while_true_semicolon_hosted**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=hosted, yield=replaced_with_yield, compiler_claim=gcc14_implements_p2809
- **while_true_empty_braces_hosted**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=hosted, yield=replaced_with_yield, compiler_claim=None
- **for_empty_implicit_true_hosted**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=hosted, yield=replaced_with_yield, compiler_claim=None
- **do_while_true_empty_braces_hosted**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=hosted, yield=replaced_with_yield, compiler_claim=None
- **constexpr_true_hosted**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=hosted, yield=replaced_with_yield, compiler_claim=clang18_claims_p2809
- **while_true_string_literal_body**: trivially_empty=False, const_expr=True, const_value=True, trivial_infinite_loop=False, environment=hosted, yield=not_applicable, compiler_claim=None
- **while_non_const_condition_empty**: trivially_empty=True, const_expr=False, const_value=None, trivial_infinite_loop=False, environment=hosted, yield=not_applicable, compiler_claim=None
- **runtime_infinite_not_trivial**: trivially_empty=False, const_expr=True, const_value=True, trivial_infinite_loop=False, environment=hosted, yield=not_applicable, compiler_claim=None
- **qualifying_hosted_yield**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=hosted, yield=replaced_with_yield, compiler_claim=claimed_hosted_yield
- **qualifying_freestanding_impl_defined**: trivially_empty=True, const_expr=True, const_value=True, trivial_infinite_loop=True, environment=freestanding, yield=implementation_defined, compiler_claim=gcc_freestanding_claim
- **while_constexpr_false_empty**: trivially_empty=True, const_expr=True, const_value=False, trivial_infinite_loop=False, environment=hosted, yield=not_applicable, compiler_claim=None
- **while_true_continue_body**: trivially_empty=False, const_expr=True, const_value=True, trivial_infinite_loop=False, environment=hosted, yield=not_applicable, compiler_claim=None
