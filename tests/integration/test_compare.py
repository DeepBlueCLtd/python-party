"""Migration-safety comparison tests (T023, US3 / FR-015, SC-005).

These encode the contract that a *meaningful* difference is surfaced while cosmetic
differences (attribute order, whitespace, namespace prefix, comments) are ignored — so the
comparison catches the dangerous "schema-valid but different" case without crying wolf.
"""

from __future__ import annotations

from acoustic_dataset import compare, validate
from acoustic_dataset.cli import main

# --- cosmetic differences MUST be ignored (no false positives) ---------------------------


def test_identical_documents_match(golden_path):
    result = compare.compare(golden_path, golden_path)
    assert result.equal
    assert result.diff == ""


def test_whitespace_and_indentation_are_cosmetic(golden_path):
    text = golden_path.read_text(encoding="utf-8")
    squashed = "".join(line.strip() for line in text.splitlines())  # strip all indentation
    assert squashed != text
    assert compare.compare(squashed, text).equal


def test_namespace_prefix_is_cosmetic():
    # The contract is no-namespace, but the equality key still rewrites prefixes, so the same
    # document under a prefix vs the default namespace compares equal.
    default_ns = '<R xmlns="urn:x"><E>1</E></R>'
    prefixed = '<p:R xmlns:p="urn:x"><p:E>1</p:E></p:R>'
    assert compare.compare(default_ns, prefixed).equal


def test_attribute_order_is_cosmetic():
    a = '<R xmlns="urn:x"><E a="1" b="2"/></R>'
    b = '<R xmlns="urn:x"><E b="2" a="1"/></R>'
    assert compare.compare(a, b).equal


def test_comment_banner_is_cosmetic(golden_path):
    text = golden_path.read_text(encoding="utf-8")
    with_banner = text.replace("<Platform", "<!-- a trial-file banner -->\n<Platform", 1)
    assert with_banner != text
    assert compare.compare(with_banner, text).equal


def test_shipped_reference_matches_the_pipeline_output(golden_path, reference_path):
    # `make pipeline` writes the golden's content; comparing it to the committed known-good
    # reference must report a clean match (the documented happy path / SC-005).
    assert compare.compare(golden_path, reference_path).ok


# --- meaningful differences MUST be surfaced ---------------------------------------------


def test_schema_valid_but_different_is_surfaced(golden_path, schema_path):
    text = golden_path.read_text(encoding="utf-8")
    # 144.000 dB is still inside the schema's Decibels band [-200, 300] -> schema-valid...
    different = text.replace(
        "<SectorLevel>134.000</SectorLevel>", "<SectorLevel>144.000</SectorLevel>", 1
    )
    assert different != text
    assert validate.schema_errors(different, schema_path) == []  # ...yet schema-valid

    result = compare.compare(text, different)
    assert not result.equal  # ...and the difference is caught, not silently passed
    assert "134.000" in result.diff
    assert "144.000" in result.diff


def test_diff_is_oriented_reference_to_generated(golden_path):
    text = golden_path.read_text(encoding="utf-8")
    generated = text.replace(
        "<SectorLevel>134.000</SectorLevel>", "<SectorLevel>144.000</SectorLevel>", 1
    )
    diff = compare.compare(generated, text).diff
    # reference (134.000) removed, generated (144.000) added
    assert "-          <SectorLevel>134.000</SectorLevel>" in diff
    assert "+          <SectorLevel>144.000</SectorLevel>" in diff


# --- CLI exit-code contract (contracts/cli-commands.md §compare) --------------------------


def test_cli_clean_match_exits_zero(golden_path, reference_path, capsys):
    rc = main(["compare", str(golden_path), str(reference_path)])
    assert rc == 0
    assert "match" in capsys.readouterr().out


def test_cli_meaningful_difference_exits_nonzero(tmp_path, golden_path, capsys):
    different = tmp_path / "generated.xml"
    different.write_text(
        golden_path.read_text(encoding="utf-8").replace(
            "<SectorLevel>134.000</SectorLevel>", "<SectorLevel>144.000</SectorLevel>", 1
        ),
        encoding="utf-8",
    )
    rc = main(["compare", str(different), str(golden_path)])
    assert rc == 1
    err = capsys.readouterr().err
    assert "different" in err
    assert "144.000" in err  # the diff is printed for the human


def test_cli_missing_file_exits_nonzero(tmp_path, golden_path, capsys):
    rc = main(["compare", str(tmp_path / "nope.xml"), str(golden_path)])
    assert rc == 1
    assert "not found" in capsys.readouterr().err
