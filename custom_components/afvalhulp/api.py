"""Calendar Client"""

from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin
from aiohttp import ClientError, ClientSession
from .const import BASE_URL, BINS, POSTCODE_URL

class AfvalhulpError(Exception):
    """Afvalhulp API Error"""

@dataclass(frozen=True, slots=True)
class Pickup:
    date: date
    summary: str
    bin_type: str | None

async def discover_calendar_url(
    session: ClientSession, postcode: str, house_number: int, addition: str = ""
) -> str:
    try:
        async with session.get(POSTCODE_URL) as response:
            response.raise_for_status()
            html = await response.text()
        token_match = re.search(r'name=["\']_token["\'][^>]*value=["\']([^"\']+)', html)
        if not token_match:
            token_match = re.search(
                r'name=["\']csrf-token["\']\s+content=["\']([^"\']+)', html
            )
        if not token_match:
            raise AfvalhulpError("Afvalhulp setup token not found")
        async with session.post(
            POSTCODE_URL,
            data={
                "_token": token_match.group(1),
                "postcode": normalize_postcode(postcode),
                "housenumber": str(house_number),
                "addition": addition.strip(),
            },
        ) as response:
            response.raise_for_status()
            await response.read()
        async with session.get(f"{BASE_URL}/pickup-schedule") as response:
            response.raise_for_status()
            html = await response.text()
    except (ClientError, TimeoutError) as err:
        raise AfvalhulpError(str(err)) from err
    match = re.search(
        r'((?:https://mijn\.afvalhulp\.nl)?/api/v1/ical/[a-f0-9-]+/calendar\.ics)',
        html,
        re.IGNORECASE,
    )
    if not match:
        raise AfvalhulpError("No calendar found for this address")
    return urljoin(BASE_URL, match.group(1))

async def fetch_pickups(session: ClientSession, calendar_url: str) -> tuple[Pickup, ...]:
    try:
        async with session.get(calendar_url) as response:
            response.raise_for_status()
            text = await response.text()
    except (ClientError, TimeoutError) as err:
        raise AfvalhulpError(str(err)) from err
    pickups = parse_ical(text)
    if not pickups:
        raise AfvalhulpError("Afvalhulp calendar contains no pickup events")
    return pickups

def normalize_postcode(postcode: str) -> str:
    return re.sub(r"\s+", "", postcode).upper()

def parse_ical(text: str) -> tuple[Pickup, ...]:
    lines: list[str] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        else:
            lines.append(line)
    pickups: list[Pickup] = []
    event: dict[str, str] | None = None
    for line in lines:
        if line == "BEGIN:VEVENT":
            event = {}
            continue
        if event is None:
            continue
        if line == "END:VEVENT":
            pickup = _parse_event(event)
            if pickup:
                pickups.append(pickup)
            event = None
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.split(";", 1)[0]
        if key in ("DTSTART", "SUMMARY"):
            event[key] = value.strip()
    return tuple(sorted(set(pickups), key=lambda item: (item.date, item.summary)))

def _parse_event(event: dict[str, str]) -> Pickup | None:
    raw_date = event.get("DTSTART", "")[:8]
    summary = event.get("SUMMARY", "").strip()
    if len(raw_date) != 8 or not raw_date.isdigit() or not summary:
        return None
    try:
        pickup_date = date.fromisoformat(f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}")
    except ValueError:
        return None
    bin_type = next(
        (
            bin_type
            for bin_type, (_, afvalhulp_summary) in BINS.items()
            if summary.casefold() == afvalhulp_summary.casefold()
        ),
        None,
    )
    return Pickup(pickup_date, summary, bin_type)
