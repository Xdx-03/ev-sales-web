"""Environment configuration with explicit validation and safe overrides."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "env.yaml"
EXAMPLE_CONFIG = PROJECT_ROOT / "config" / "env.example.yaml"


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str = field(repr=False)

    @property
    def configured(self) -> bool:
        return bool(self.username and self.password)


@dataclass(frozen=True)
class MobileCustomer:
    phone: str = field(repr=False)

    @property
    def configured(self) -> bool:
        return bool(self.phone)


@dataclass(frozen=True)
class WebSettings:
    base_url: str
    h5_base_url: str
    navigation_timeout_ms: int
    action_timeout_ms: int
    headless: bool
    viewport_width: int
    viewport_height: int
    admin: Credentials
    mobile_customer: MobileCustomer

    def require_admin(self) -> Credentials:
        if not self.admin.configured:
            raise ValueError(
                "管理员账号未配置。请设置 EV_WEB_ADMIN_USERNAME 和 EV_WEB_ADMIN_PASSWORD"
            )
        if not _is_local_url(self.base_url) and not self.base_url.startswith("https://"):
            raise ValueError("非本地环境使用账号登录时必须启用 HTTPS")
        return self.admin

    def require_mobile_customer(self) -> MobileCustomer:
        if not self.mobile_customer.configured:
            raise ValueError("移动 H5 客户未配置。请设置 EV_H5_CUSTOMER_PHONE")
        if not re.fullmatch(r"1[3-9]\d{9}", self.mobile_customer.phone):
            raise ValueError("EV_H5_CUSTOMER_PHONE 必须是 11 位测试手机号")
        if not _is_local_url(self.h5_base_url) and not self.h5_base_url.startswith("https://"):
            raise ValueError("非本地 H5 环境使用客户账号登录时必须启用 HTTPS")
        return self.mobile_customer


def load_settings(
    config_path: str | Path | None = None,
    environment: str | None = None,
) -> WebSettings:
    """Load one environment and apply environment-variable overrides."""
    selected_path = Path(config_path) if config_path else DEFAULT_CONFIG
    if not selected_path.exists() and config_path is None:
        selected_path = EXAMPLE_CONFIG
    if not selected_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {selected_path}")

    raw = yaml.safe_load(selected_path.read_text(encoding="utf-8")) or {}
    selected_environment = environment or os.getenv("EV_TEST_ENV", "default")
    if selected_environment not in raw:
        raise ValueError(f"配置中不存在环境: {selected_environment}")

    section = raw[selected_environment] or {}
    web = section.get("web", {})
    admin = section.get("accounts", {}).get("admin", {})
    mobile_customer = section.get("accounts", {}).get("mobile_customer", {})

    settings = WebSettings(
        base_url=os.getenv("EV_WEB_BASE_URL", str(web.get("base_url", ""))).rstrip("/"),
        h5_base_url=os.getenv("EV_H5_BASE_URL", str(web.get("h5_base_url", ""))).rstrip("/"),
        navigation_timeout_ms=_positive_int(
            os.getenv("EV_WEB_NAVIGATION_TIMEOUT_MS", web.get("navigation_timeout_ms", 15000)),
            "navigation_timeout_ms",
        ),
        action_timeout_ms=_positive_int(
            os.getenv("EV_WEB_ACTION_TIMEOUT_MS", web.get("action_timeout_ms", 8000)),
            "action_timeout_ms",
        ),
        headless=_boolean(os.getenv("EV_WEB_HEADLESS", web.get("headless", True))),
        viewport_width=_positive_int(
            os.getenv("EV_WEB_VIEWPORT_WIDTH", web.get("viewport_width", 1440)),
            "viewport_width",
        ),
        viewport_height=_positive_int(
            os.getenv("EV_WEB_VIEWPORT_HEIGHT", web.get("viewport_height", 900)),
            "viewport_height",
        ),
        admin=Credentials(
            username=os.getenv("EV_WEB_ADMIN_USERNAME", str(admin.get("username", ""))).strip(),
            password=os.getenv("EV_WEB_ADMIN_PASSWORD", str(admin.get("password", ""))),
        ),
        mobile_customer=MobileCustomer(
            phone=os.getenv(
                "EV_H5_CUSTOMER_PHONE",
                str(mobile_customer.get("phone", "")),
            ).strip(),
        ),
    )
    _validate_base_url(settings.base_url)
    _validate_base_url(settings.h5_base_url)
    return settings


def _validate_base_url(base_url: str) -> None:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("web.base_url 必须是有效的 HTTP(S) 地址")
    if parsed.username or parsed.password:
        raise ValueError("web.base_url 不得包含账号或密码")


def _is_local_url(base_url: str) -> bool:
    return (urlparse(base_url).hostname or "").lower() in {"127.0.0.1", "localhost", "::1"}


def _positive_int(value: object, field_name: str) -> int:
    try:
        result = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} 必须是正整数") from exc
    if result <= 0:
        raise ValueError(f"{field_name} 必须是正整数")
    return result


def _boolean(value: object) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError("布尔配置只接受 true/false、yes/no、on/off 或 1/0")
