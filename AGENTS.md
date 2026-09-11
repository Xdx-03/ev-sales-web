# Repository Guidelines

## Project Boundary

This repository contains black-box Playwright tests for the management Web client
and customer mobile H5 client. It does not contain application source or white-box
unit tests. Review browser behavior, cross-client coverage, isolation, evidence,
and framework maintainability within that boundary.

`framework_checks/` separately tests this repository's runner and pytest resource
lifecycle using synthetic suites and controlled browser-context substitutes. It
does not test application internals or launch a real browser. Keep it separate
from business counts and the default `testpaths = tests` selection.

## Required Static Checks

Run these checks without claiming that they exercised a live application:

```bash
python -m ruff format --check .
python -m ruff check .
python -m mypy
python -m compileall -q ev_web tests framework_checks scripts run_web_tests.py
python -m pytest --collect-only -q
python -m pytest framework_checks -q --junitxml=reports/framework-checks.xml
```

Live Chrome execution requires the documented isolated Web/H5 environment and
dedicated test accounts. Collection success is not a browser regression result.

## Commit Messages

- Use `type: 中文说明`, for example `test: 补充移动端售后场景`.
- Allowed types are `feat`, `fix`, `test`, `docs`, `refactor`, `ci`, `chore`,
  `perf`, `build`, `style`, and `revert`; an optional lowercase scope is allowed.
- Keep the subject within 72 characters and start the description with Chinese text.

## Code Review Rules

### P0: environment and evidence safety

- Reject committed credentials, tokens, customer data, private URLs, screenshots,
  traces, videos, or reports containing sensitive information.
- Reject production or shared-environment defaults and any UI scenario that can
  create or modify uncontrolled business data.
- Credentials must come from environment variables or ignored local config, and
  password-bearing configuration objects must not reveal values in repr or errors.

### P1: Playwright correctness

- Reject fixed sleeps, silent retries, order dependencies, and shared mutable
  browser contexts. Use Playwright locators, assertions, and condition waits.
- Prefer accessible roles, labels, placeholders, or stable test attributes. Flag
  brittle absolute XPath, layout-dependent selectors, or ambiguous text locators.
- Keep selectors and page interactions in Page Objects or reusable components;
  keep business expectations in tests and reusable journeys in flows.
- Each test must own an isolated BrowserContext and must leave enough evidence to
  diagnose a failure without leaking credentials or personal data.
- Assertions must verify meaningful navigation, state, permissions, or content;
  page load and element existence alone are insufficient for business scenarios.

### P1: multi-client maintainability

- Keep management Web and customer H5 fixtures, pages, routes, and test data
  explicit. Share only stable technical behavior, not unrelated business details.
- Do not duplicate login, context setup, navigation waiting, screenshots, or
  report setup across modules.
- Register every marker in `pytest.ini`; keep smoke, regression, critical,
  permission, mobile, and H5 intent visible at the scenario.
- When scenario counts or real execution evidence changes, update README and the
  PR description. Missing required credentials and any skipped live scenario must
  fail the runner instead of producing an incomplete green regression.

### Evidence and review focus

- “Passed” requires a recorded run against the isolated application. Otherwise use
  “not executed” or “collection validated”.
- Do not request white-box/unit-test coverage for this repository. Recommend an
  observable Web/H5 behavior or API-side test for the application instead.
  Framework reliability regressions belong in `framework_checks/`.
- Avoid style-only comments already enforced by Ruff and Mypy. Focus on P0/P1
  correctness, selector stability, false-green risk, isolation, and maintainability.
