# Verification campaign harness

`run_case(project)` sends a VesselProject JSON object through `POST /api/projects` and
`POST /api/projects/{id}/calculate` using FastAPI's TestClient. Its stable envelope is
`{ok, http_status, payload, error}`. On success, `payload` is the service calculation
payload, including `project_number`, `project_name`, `code`, `edition`, `global_mawp_mpa`,
`results`, `errors`, `volume_mass`, and `verification`.

A result row has component and calculation identifiers, clause reference, input snapshot,
intermediate values (`name`, `value`, `unit`), final result, and status. A shortened live
row shape (values abbreviated; see the API output for actual values):

```json
{"component_id":"SHELL-01","component_type":"shell","calculation_type":"internal_pressure",
 "clause_reference":"UG-27(c)(1)","intermediate_values":[{"name":"required_thickness","value":4.2,"unit":"mm"}],
 "final_result":{"required_thickness":4.2},"status":"PASS"}
```

Use a base tank and overrides to start a family. Override dictionaries merge recursively;
lists replace the previous list in full. Keep each family self-contained under
`tools/campaign/families/fNN_name/` and export reproducible `run()` and oracle data.

```python
from pathlib import Path
from tools.campaign.bases import vertical_leg_tank
from tools.campaign.harness import run_case, find_results, value_of
from tools.campaign.compare import CaseResult, judge, write_results

FAMILY = "F01-shell-pressure"

def variants():
    # Vary one input at a time; retain a stable case ID for every result.
    for pressure in (0.8, 1.0, 1.2):
        yield f"P-{pressure}", vertical_leg_tank(
            design_conditions={"design_pressure": pressure}
        )

def run():
    rows = []
    for case_id, project in variants():
        outcome = run_case(project)
        matches = find_results(outcome["payload"] or {},
                               component_id="SHELL-01", clause_prefix="UG-27")
        result = matches[0] if matches else None
        suite = value_of(result, "required_thickness") if result else None
        reference = oracle(case_id)  # family-local, independently sourced value
        diff, verdict = judge(suite, reference, suite_status=(result or {}).get("status"))
        rows.append(CaseResult(case_id, FAMILY, {"pressure": project["design_conditions"]["design_pressure"]},
                               "required_thickness", "mm", suite, reference, "oracle", diff, verdict))
    write_results(Path(__file__).parent, FAMILY, rows, {"code": "ASME VIII-1"})

def oracle(case_id):
    # Replace with the family’s independent equation/source calculation.
    raise NotImplementedError(case_id)

if __name__ == "__main__":
    run()
```

`judge` emits the shared verdict vocabulary; `write_results` stores `results.json`.
`python -m tools.campaign.aggregate` reads family result files and writes the campaign
Markdown/CSV summary under `docs/validation/campaign-2026-10/`.
