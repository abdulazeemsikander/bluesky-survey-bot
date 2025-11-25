# automation/poster.py
"""
Thin wrapper around the Bluesky HTTP API for posting a single status.

We use the official atproto endpoints:
  - com.atproto.server.createSession  (login with app password)
  - com.atproto.repo.createRecord     (create app.bsky.feed.post)
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests


BSKY_SERVICE = os.getenv("BSKY_SERVICE", "https://bsky.social")


@dataclass
class BlueskyConfig:
    handle: str
    app_password: str
    user_agent: str = "bluesky-survey-bot/1.0"


class BlueskyClient:
    def __init__(self, cfg: BlueskyConfig):
        if not cfg.handle or not cfg.app_password:
            raise ValueError("BSKY_HANDLE and BSKY_APP_PASSWORD must be set in .env")
        self.cfg = cfg
        self.did = None
        self.access_jwt = None

    # ---------- low-level helpers ----------

    def _headers(self, with_auth: bool = False) -> dict:
        h = {
            "User-Agent": self.cfg.user_agent,
            "Content-Type": "application/json",
        }
        if with_auth and self.access_jwt:
            h["Authorization"] = f"Bearer {self.access_jwt}"
        return h

    def login(self):
        """
        Create a session using the app password to get DID + accessJwt.
        """
        url = f"{BSKY_SERVICE}/xrpc/com.atproto.server.createSession"
        payload = {
            "identifier": self.cfg.handle,
            "password": self.cfg.app_password,
        }
        resp = requests.post(url, json=payload, headers=self._headers())
        if resp.status_code != 200:
            raise RuntimeError(
                f"Bluesky login failed ({resp.status_code}): {resp.text}"
            )

        data = resp.json()
        self.did = data.get("did")
        self.access_jwt = data.get("accessJwt")
        if not self.did or not self.access_jwt:
            raise RuntimeError("Bluesky login response missing did/accessJwt")

    def post_status(self, text: str) -> dict:
        """
        Create a simple text post on the user's feed.
        """
        if self.access_jwt is None or self.did is None:
            self.login()

        url = f"{BSKY_SERVICE}/xrpc/com.atproto.repo.createRecord"
        record = {
            "text": text,
            "createdAt": datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z"),
            "type": "app.bsky.feed.post",
        }

        payload = {
            "repo": self.did,
            "collection": "app.bsky.feed.post",
            "record": record,
        }

        resp = requests.post(
            url, json=payload, headers=self._headers(with_auth=True)
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"Bluesky post failed ({resp.status_code}): {resp.text}"
            )
        return resp.json()


def post_to_bluesky(text: str, dry_run: bool = True) -> None:
    """
    Convenience function used by main.py.
    """
    cfg = BlueskyConfig(
        handle=os.getenv("BSKY_HANDLE", "").strip(),
        app_password=os.getenv("BSKY_APP_PASSWORD", "").strip(),
        user_agent=os.getenv("USER_AGENT", "bluesky-survey-bot/1.0"),
    )

    if dry_run:
        print("[DRY RUN] Would post to Bluesky as", cfg.handle or "<missing handle>")
        print()
        print(text)
        return

    client = BlueskyClient(cfg)
    print("[LIVE] Sending post to Bluesky …")
    result = client.post_status(text)
    uri = result.get("uri", "<no uri>")
    print("[LIVE] Post created with uri:", uri)