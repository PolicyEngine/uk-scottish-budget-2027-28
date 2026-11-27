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


def test_guard_catches_a_local_directory(tmp_path):
    """receipt.json is served with the page: a costings path recorded in
    full would publish the integrator's home directory."""
    (tmp_path / "receipt.json").write_text(
        json.dumps(
            {"official_costings": {"path": "/Users/someone/repo/costs.csv"}}
        )
    )
    (tmp_path / "ok.json").write_text(
        json.dumps(
            {
                "official_costings": {
                    "path": "data_inputs/official/sfc_costings_2027_28.csv"
                },
                "source": "https://www.gov.scot/publications/",
            }
        )
    )
    problems = check_public_data.check_folder(tmp_path)
    assert len(problems) == 1 and "local directory" in problems[0]


LOCAL = [
    '"path": "/Users/someone/repo/costs.csv"',
    "/tmp/x.csv",
    "see ~/costs.csv",
    "file:///Users/x/costs.csv",
    '"C:\\\\Users\\\\x\\\\costs.csv"',
    "C:\\Users\\x",
    "(/home/x/y)",
    "path=/root/x",
    "at:/Volumes/Disk/x",
    "'/private/var/x'",
]
NOT_LOCAL = [
    "https://www.gov.scot/publications/",
    "https://example.org/home/page",
    "http://host/tmp/x",
    "data_inputs/official/sfc_costings_2027_28.csv",
    "a/home/b",
    "Note:\\nNext line",
    "ratio 3:1",
]


def test_local_path_pattern():
    for text in LOCAL:
        assert check_public_data.LOCAL_PATH.search(text), text
    for text in NOT_LOCAL:
        assert not check_public_data.LOCAL_PATH.search(text), text
