import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_public_data  # noqa: E402


def test_committed_public_folder_is_clean():
    assert check_public_data.check_folder(ROOT / "dashboard/public/data") == []


def test_guard_catches_ids_floor_and_area_codes(tmp_path):
    (tmp_path / "a.json").write_text(
        json.dumps(
            {
                "rows": [
                    {"person_id": 1},
                    {"avg_change_gbp": 3.0, "n_records": 4},
                    {"code": "S12000033"},
                ]
            }
        )
    )
    (tmp_path / "b.txt").write_text("x")
    problems = check_public_data.check_folder(tmp_path)
    text = "\n".join(problems)
    assert "identifier" in text
    assert "4 records" in text
    assert "area codes" in text
    assert "only .json and .csv" in text
