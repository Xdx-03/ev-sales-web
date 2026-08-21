"""Project runner: clean evidence, execute pytest and preserve its exit status."""

from __future__ import annotations

import argparse
import os
import shutil
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
    shutil.rmtree(ALLURE_RESULTS, ignore_errors=True)
    if JUNIT_REPORT.exists():
        JUNIT_REPORT.unlink()
    ALLURE_RESULTS.mkdir(parents=True, exist_ok=True)
    JUNIT_REPORT.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    args, pytest_args = parse_args()
    clean_previous_results()
    run_id = create_run_id()
    environment = os.environ.copy()
    environment["EV_TEST_RUN_ID"] = run_id

    command = [
        sys.executable,
        "-m",
        "pytest",
        f"--alluredir={ALLURE_RESULTS}",
        f"--junitxml={JUNIT_REPORT}",
    ]
    if args.config:
        command.append(f"--web-config={args.config}")
    if args.env:
        command.append(f"--web-env={args.env}")
    command.extend(pytest_args)

    print(f"Test run: {run_id}")
    completed = subprocess.run(command, cwd=PROJECT_ROOT, env=environment, check=False)
    if completed.returncode == 0 and not _is_complete_success(JUNIT_REPORT):
        print("执行未产生完整通过结果, 零用例或存在跳过。拒绝以成功状态退出。", file=sys.stderr)
        return 1
    return completed.returncode


def _is_complete_success(report_path: Path) -> bool:
    if not report_path.exists():
        return False
    root = ET.parse(report_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.findall("testsuite"))
    tests = sum(int(suite.attrib.get("tests", 0)) for suite in suites)
    failures = sum(int(suite.attrib.get("failures", 0)) for suite in suites)
    errors = sum(int(suite.attrib.get("errors", 0)) for suite in suites)
    skipped = sum(int(suite.attrib.get("skipped", 0)) for suite in suites)
    return tests > 0 and failures == 0 and errors == 0 and skipped == 0


if __name__ == "__main__":
    raise SystemExit(main())
