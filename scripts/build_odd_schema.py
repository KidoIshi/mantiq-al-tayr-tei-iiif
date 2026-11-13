#!/usr/bin/env python3
"""Build the project Relax NG schema from the TEI ODD customization."""

from __future__ import annotations

import hashlib
import json
import shutil
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from lxml import etree
from saxonche import PySaxonProcessor

from rng_tools import validate_with_jing


ROOT = Path(__file__).resolve().parents[1]
ODD = ROOT / "schema" / "mantiq.odd"
OUTPUT_RNG = ROOT / "schema" / "mantiq.rng"
REPORT = ROOT / "outputs" / "odd-build-report.json"
WORK = ROOT / "work" / "odd-toolchain"

TEI_VERSION = "4.12.0"
STYLESHEETS_VERSION = "7.61.0"
STYLESHEETS_COMMIT = "81408afc9a25c9170c49adadb0df508ead8ba959"

RESOURCES = {
    "stylesheets.zip": {
        "url": f"https://github.com/TEIC/Stylesheets/archive/{STYLESHEETS_COMMIT}.zip",
        "sha256": "e61bc7f852035f50c2300df085a3249f0a8f7783dab138bd150d31cddfac44ef",
    },
    "p5subset.xml": {
        "url": f"https://www.tei-c.org/Vault/P5/{TEI_VERSION}/xml/tei/odd/p5subset.xml",
        "sha256": "5b89720edc6f3821ab3d0aa242aa5dc922bfbafabfb103d2de9d211001c33e26",
    },
    "tei_odds.rng": {
        "url": f"https://www.tei-c.org/Vault/P5/{TEI_VERSION}/xml/tei/custom/schema/relaxng/tei_odds.rng",
        "sha256": "655113c0d40b798847d6f41b15c95a75055c0ee3e8ad6fb923c49ad7ebc87df1",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(name: str) -> Path:
    specification = RESOURCES[name]
    destination = WORK / name
    if destination.exists() and sha256(destination) == specification["sha256"]:
        return destination
    WORK.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        specification["url"], headers={"User-Agent": "mantiq-tei-odd-builder/0.1"}
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        destination.write_bytes(response.read())
    actual = sha256(destination)
    if actual != specification["sha256"]:
        destination.unlink(missing_ok=True)
        raise RuntimeError(f"Checksum mismatch for {name}: {actual}")
    return destination


def prepare_toolchain() -> tuple[Path, Path, Path]:
    archive = download("stylesheets.zip")
    p5_download = download("p5subset.xml")
    odds_schema = download("tei_odds.rng")

    stylesheets = WORK / f"Stylesheets-{STYLESHEETS_COMMIT}"
    if not stylesheets.exists():
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(WORK)

    p5subset = WORK / "tei-vault" / TEI_VERSION / "xml" / "tei" / "odd" / "p5subset.xml"
    p5subset.parent.mkdir(parents=True, exist_ok=True)
    if not p5subset.exists() or sha256(p5subset) != RESOURCES["p5subset.xml"]["sha256"]:
        shutil.copyfile(p5_download, p5subset)
    return stylesheets, p5subset, odds_schema


def transform(source: Path, stylesheet: Path, output: Path, parameters: dict[str, str]) -> None:
    with PySaxonProcessor(license=False) as processor:
        xslt = processor.new_xslt30_processor()
        executable = xslt.compile_stylesheet(stylesheet_file=str(stylesheet))
        for name, value in parameters.items():
            executable.set_parameter(name, processor.make_string_value(value))
        executable.transform_to_file(source_file=str(source), output_file=str(output))


def main() -> int:
    stylesheets, p5subset, odds_schema = prepare_toolchain()
    odd_valid, odd_errors = validate_with_jing(ODD, odds_schema)
    if not odd_valid:
        raise RuntimeError("ODD is not valid against tei_odds.rng: " + "; ".join(odd_errors))

    compiled = WORK / "mantiq.compiled.odd"
    generated = WORK / "mantiq.generated.rng"
    source_uri = p5subset.as_uri()
    vault_uri = (WORK / "tei-vault").as_uri().rstrip("/") + "/"
    parameters = {
        "defaultSource": source_uri,
        "defaultTEIServer": vault_uri,
        "useFixedDate": "true",
        "verbose": "false",
    }
    transform(ODD, stylesheets / "odds" / "odd2odd.xsl", compiled, parameters)
    transform(compiled, stylesheets / "odds" / "odd2relax.xsl", generated, parameters)

    generated_text = generated.read_text(encoding="utf-8")
    generated_text = generated_text.replace(
        vault_uri + TEI_VERSION + "/",
        f"https://www.tei-c.org/Vault/P5/{TEI_VERSION}/",
    )
    generated_text = "\n".join(line.rstrip() for line in generated_text.splitlines()) + "\n"
    generated.write_text(generated_text, encoding="utf-8", newline="\n")

    etree.parse(str(generated))
    shutil.copyfile(generated, OUTPUT_RNG)
    sample_valid, sample_errors = validate_with_jing(
        ROOT / "data" / "tei" / "bnf-persan-348-f6-sample.xml", OUTPUT_RNG
    )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "odd": str(ODD.relative_to(ROOT)),
        "odd_sha256": sha256(ODD),
        "odd_valid": odd_valid,
        "tei_p5_version": TEI_VERSION,
        "tei_stylesheets_version": STYLESHEETS_VERSION,
        "tei_stylesheets_commit": STYLESHEETS_COMMIT,
        "generated_schema": str(OUTPUT_RNG.relative_to(ROOT)),
        "generated_schema_sha256": sha256(OUTPUT_RNG),
        "generated_schema_validator": "Jing 20241231 via jingtrang 0.3.0",
        "sample_valid_against_generated_schema": sample_valid,
        "sample_errors": sample_errors,
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if odd_valid and sample_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
