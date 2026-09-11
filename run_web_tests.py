"""Project runner: clean evidence, execute pytest and preserve its exit status."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from ev_web.run_context import create_run_id

PROJECT_ROOT = Path(__file__).resolve().parent
ALLURE_RESULTS = PROJECT_ROOT / "allure-results"
JUNIT_REPORT = PROJECT_ROOT / "reports" / "junit.xml"


def parse_args() -> tuple[argparse.Namespace, list[str]]:
    parser = argparse.ArgumentParser(description="运行 EV Sales Web UI 自动化")
    parser.add_argument("--config", help="YAML 环境配置路径")
    parser.add_argument("--env", help="YAML 中的环境名称")
    args, pytest_args = parser.parse_known_args()
    if pytest_args[:1] == ["--"]:
        pytest_args = pytest_args[1:]
    return args, pytest_args


def clean_previous_results() -> None:
    # Validate every target and ancestor before any deletion, including Windows junctions.
    for output in (ALLURE_RESULTS, JUNIT_REPORT):
        _validate_output_path(output)
    if ALLURE_RESULTS.is_dir():
        shutil.rmtree(ALLURE_RESULTS)
    elif ALLURE_RESULTS.exists():
        ALLURE_RESULTS.unlink()
    if JUNIT_REPORT.exists():
        JUNIT_REPORT.unlink()
    ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)
    JUNIT_REPORT.parent.mkdir(parents=True, exist_ok=True)


def _validate_output_path(output: Path) -> None:
    root = PROJECT_ROOT.resolve()
    try:
        relative = output.resolve().relative_to(root)
        lexical = output.absolute().relative_to(PROJECT_ROOT.absolute())
    except ValueError:
        raise ValueError("Refusing to clean a report output outside the project root.") from None
    if not relative.parts or not lexical.parts:
        raise ValueError("Refusing to clean the project root itself.")
    for path in (output, *output.parents):
        if path == PROJECT_ROOT:
            break
        try:
            attributes = getattr(path.lstat(), "st_file_attributes", 0)
        except FileNotFoundError:
            continue
        if path.is_symlink() or attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError("Refusing to clean a linked report output or ancestor.")


def main() -> int:
    args, pytest_args = parse_args()
    clean_previous_results()
    run_id = create_run_id()
    environment = os.environ.copy()
    environment["EV_TEST_RUN_ID"] = run_id

    command = [sys.executable, "-m", "pytest"]
    command.extend(pytest_args)
    if args.config:
        command.append(f"--web-config={args.config}")
    if args.env:
        command.append(f"--web-env={args.env}")
    command.extend([f"--alluredir={ALLURE_RESULTS}", f"--junitxml={JUNIT_REPORT}"])

    print(f"Test run: {run_id}")
    completed = subprocess.run(command, cwd=PROJECT_ROOT, env=environment, check=False)
    if completed.returncode == 0 and not _is_complete_success(JUNIT_REPORT):
        print(
            "JUnit报告缺失/损坏, 或执行存在零用例、跳过、失败、错误。拒绝以成功状态退出。",
            file=sys.stderr,
        )
        return 1
    return completed.returncode


def _is_complete_success(report_path: Path) -> bool:
    try:
        root = ET.parse(report_path).getroot()
    except (OSError, ET.ParseError):
        return False
    if root.tag not in {"testsuite", "testsuites"}:
        return False
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    try:
        counts = [
            [int(suite.attrib[key]) for key in ("tests", "failures", "errors", "skipped")]
            for suite in suites
        ]
    except (KeyError, ValueError):
        return False
    return (
        all(all(value >= 0 for value in row) and sum(row[1:]) <= row[0] for row in counts)
        and sum(row[0] for row in counts) > 0
        and all(sum(row[1:]) == 0 for row in counts)
    )


if __name__ == "__main__":
    raise SystemExit(main())
