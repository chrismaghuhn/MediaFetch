"""GUI-free update checking, download, and notification policy."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Protocol

import requests

from utils.version import is_newer_version

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com/repos/{repo}/releases/latest"


@dataclass(frozen=True)
class UpdateInfo:
    current: str
    latest: str
    url: str
    body: str
    installer_url: str = ""
    installer_sha256: str = ""


class UpdateSettings(Protocol):
    skipped_version: str
    remind_update_after: str


def check_latest(
    github_repo: str,
    current_version: str,
    *,
    session: requests.Session | None = None,
) -> UpdateInfo | None:
    """Return update info when GitHub latest release is newer than current_version."""
    http = session or requests
    try:
        url = GITHUB_API.format(repo=github_repo)
        response = http.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        tag = data.get("tag_name", "")
        latest = tag.lstrip("v")
        if not is_newer_version(current_version, latest):
            return None

        installer_url, installer_sha256 = parse_release_assets(data)
        return UpdateInfo(
            current=current_version,
            latest=latest,
            url=data.get("html_url", ""),
            body=data.get("body", "") or "",
            installer_url=installer_url,
            installer_sha256=installer_sha256,
        )
    except requests.RequestException as exc:
        logger.warning("Update check failed: %s", exc)
        return None


def parse_release_assets(release_data: dict) -> tuple[str, str]:
    """Extract installer download URL and SHA-256 from release assets or body."""
    installer_url = ""
    installer_sha256 = ""

    for asset in release_data.get("assets", []):
        name = str(asset.get("name", ""))
        if name.endswith("-Setup.exe") or name.endswith("Setup.exe"):
            installer_url = str(asset.get("browser_download_url", ""))
            break

    for asset in release_data.get("assets", []):
        name = str(asset.get("name", ""))
        if name.endswith(".sha256") and installer_url and Path(name).stem in installer_url:
            # SHA256 sidecar asset — fetched separately when downloading
            installer_sha256 = ""  # populated via body or dedicated fetch if needed
            break

    body = release_data.get("body") or ""
    for line in body.splitlines():
        line = line.strip()
        if line.lower().startswith("sha256:"):
            installer_sha256 = line.split(":", 1)[1].strip().lower()
        elif line.lower().startswith("installer:") and not installer_url:
            installer_url = line.split(":", 1)[1].strip()

    return installer_url, installer_sha256


def should_notify(update: UpdateInfo, settings: UpdateSettings) -> bool:
    """Respect skipped version and remind-later date from settings."""
    if settings.skipped_version and settings.skipped_version == update.latest:
        return False

    remind_after = settings.remind_update_after
    if remind_after:
        try:
            remind_date = date.fromisoformat(remind_after)
            if date.today() < remind_date:
                return False
        except ValueError:
            logger.debug("Invalid remind_update_after: %s", remind_after)

    return True


def download_file(
    url: str,
    dest: Path,
    *,
    expected_sha256: str | None = None,
    session: requests.Session | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> bool:
    """Download a file and optionally verify SHA-256."""
    http = session or requests
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with http.get(url, stream=True, timeout=120) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            hasher = hashlib.sha256()
            with dest.open("wb") as fh:
                for chunk in response.iter_content(chunk_size=65536):
                    if not chunk:
                        continue
                    fh.write(chunk)
                    hasher.update(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total:
                        progress_callback(downloaded, total)

        if expected_sha256:
            digest = hasher.hexdigest().lower()
            if digest != expected_sha256.lower():
                logger.error("SHA-256 mismatch: expected %s got %s", expected_sha256, digest)
                dest.unlink(missing_ok=True)
                return False
        return True
    except (requests.RequestException, OSError) as exc:
        logger.error("Download failed: %s", exc)
        dest.unlink(missing_ok=True)
        return False


def remind_later_days(days: int = 7) -> str:
    """ISO date string for remind-update-after setting."""
    from datetime import timedelta

    return (date.today() + timedelta(days=days)).isoformat()


def parse_remind_date(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.combine(date.fromisoformat(value), datetime.min.time())
        except ValueError:
            return None
