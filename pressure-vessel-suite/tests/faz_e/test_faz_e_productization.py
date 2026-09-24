import math
import sqlite3

import pytest

from calc_core import GoldenCase, TolerancePolicy, assert_monotonic, verify_golden_case
from calc_core.result import CalculationResult
from domain import CalculationRunStore


def test_golden_case_tolerance_and_monotonicity():
    case = GoldenCase("shell-normal", {"mawp": 1.25}, TolerancePolicy(relative=1e-4))
    assert verify_golden_case(case, {"mawp": 1.25001}).passed
    assert not verify_golden_case(case, {"mawp": 1.3}).passed
    assert assert_monotonic([1.0, 1.1, 1.1])
    assert not assert_monotonic([1.0, 0.9])


def test_golden_case_rejects_non_finite_values_and_invalid_tolerances():
    case = GoldenCase("finite-only", {"mawp": 1.25})
    assert not verify_golden_case(case, {"mawp": math.inf}).passed
    assert not verify_golden_case(case, {"mawp": "not numeric"}).passed
    with pytest.raises(ValueError, match="negatif"):
        TolerancePolicy(relative=-1e-6)


def test_result_verification_rejects_non_finite():
    result = CalculationResult(component_id="S1")
    result.final_result = math.inf
    result.set_pass()
    assert "NaN/inf" in " ".join(__import__("calc_core").validate_result(result))


def test_run_store_is_transactional_and_audited(tmp_path):
    store = CalculationRunStore(tmp_path / "runs.sqlite")
    run_id = store.create_run("P-1", "A", {"global_mawp": 1.2}, "engineer")
    run = store.get_run(run_id)
    assert run["payload"] == {"global_mawp": 1.2}
    assert len(store.audit_log(run_id)) == 1
    store.approve(run_id, "checker", "reviewer", "checked")
    assert store.get_run(run_id)["approvals"][0]["role"] == "checker"
    with pytest.raises(sqlite3.IntegrityError, match="immutable"):
        store._db.execute("UPDATE calculation_runs SET revision='B' WHERE run_id=?", (run_id,))
    with pytest.raises(ValueError):
        store.create_run("P-1", "B", {"unsafe": math.nan}, "engineer")
    assert len(store.audit_log(run_id)) == 2
    store.close()
