"""Shared Jing-based RELAX NG validation helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import jingtrang


ROOT = Path(__file__).resolve().parents[1]


def find_java() -> Path:
    java_home = os.environ.get("JAVA_HOME")
    candidates: list[Path] = []
    if java_home:
        candidates.append(Path(java_home) / "bin" / ("java.exe" if os.name == "nt" else "java"))
    path_java = shutil.which("java")
    if path_java:
        candidates.append(Path(path_java))
    candidates.extend((ROOT / "work" / "java").glob("**/bin/java.exe"))
    candidates.extend((ROOT / "work" / "java").glob("**/bin/java"))
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise RuntimeError("Java 17 or later is required for Jing RELAX NG validation.")


def validate_with_jing(xml_path: Path, rng_path: Path) -> tuple[bool, list[str]]:
    java = find_java()
    jing_jar = Path(jingtrang.__file__).with_name("jing.jar")
    completed = subprocess.run(
        [str(java), "-jar", str(jing_jar), str(rng_path), str(xml_path)],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    messages = [line for line in (completed.stdout + completed.stderr).splitlines() if line.strip()]
    return completed.returncode == 0, messages
