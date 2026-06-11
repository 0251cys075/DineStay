"""
DineStay — auth_handler.py  (Enhanced v2)
Manages user registration, login, and password hashing.

Storage backends (auto-selected):
  Local dev  → data/users.json + data/admin.json (file-based, reliable)
  Vercel     → ADMIN_CREDS + USERS_DATA env vars, updated via Vercel REST API
               so data survives container cold-starts.

Security:
  - Passwords hashed with werkzeug scrypt
  - Admin credential changes require old-password verification
  - Writes are atomic locally; in-memory + Vercel env API on serverless
  - In-memory cache avoids redundant reads within a single request
"""

import os
import json
import tempfile
import shutil
import urllib.request
import urllib.error
from typing import Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ── Detect environment ─────────────────────────────────────────────────────────
_ON_VERCEL = bool(os.environ.get("VERCEL"))

# ── File paths (can be overridden by app.py for Vercel /tmp) ──────────────────
USERS_FILE = os.path.join("data", "users.json")
ADMIN_FILE = os.path.join("data", "admin.json")

# Default admin credentials (used only when no stored creds exist)
_DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
_DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "DineStay@2024")

# ── In-memory cache — avoids redundant file / API reads within a request ───────
_cache: dict = {
    "admin": None,  # dict or None
    "users": None,  # list or None
}


# ══════════════════════════════════════════════════════════
# VERCEL ENV VAR PERSISTENCE
# Stores admin creds + users as encrypted env vars so they
# survive container cold-starts (ephemeral /tmp does not).
# ══════════════════════════════════════════════════════════

def _vercel_update_env(name: str, value: str) -> bool:
    """
    Update or create a Vercel environment variable via the Vercel REST API.
    Returns True on success, False on failure (missing token, network error, etc.).

    Required env vars:
      VERCEL_TOKEN       — Personal access token from vercel.com/account/tokens
      VERCEL_PROJECT_ID  — Found in vercel.com → Project → Settings → General
    """
    token      = os.environ.get("VERCEL_TOKEN", "").strip()
    project_id = os.environ.get("VERCEL_PROJECT_ID", "").strip()

    if not token or not project_id:
        return False  # Silently skip — caller handles local fallback

    try:
        # ── Step 1: list existing env vars to find the target ID ──────────────
        list_url = f"https://api.vercel.com/v9/projects/{project_id}/env"
        req = urllib.request.Request(
            list_url,
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            env_data = json.loads(resp.read().decode())

        env_vars = env_data.get("envs", [])
        existing = next(
            (e for e in env_vars
             if e["key"] == name and "production" in (e.get("target") or [])),
            None,
        )

        if existing:
            # ── Step 2a: PATCH the existing env var ───────────────────────────
            patch_url = f"https://api.vercel.com/v9/projects/{project_id}/env/{existing['id']}"
            payload = json.dumps({
                "value": value,
                "type": "encrypted",
                "target": ["production", "preview"],
            }).encode()
            req = urllib.request.Request(
                patch_url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="PATCH",
            )
        else:
            # ── Step 2b: POST a new env var ───────────────────────────────────
            payload = json.dumps({
                "key": name,
                "value": value,
                "type": "encrypted",
                "target": ["production", "preview"],
            }).encode()
            req = urllib.request.Request(
                list_url,
                data=payload,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )

        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status in (200, 201)

    except Exception:
        return False  # Network / auth errors are non-fatal — data still in-memory


# ══════════════════════════════════════════════════════════
# INTERNAL HELPERS
# ══════════════════════════════════════════════════════════

def _ensure_data_dir() -> None:
    """Create the data directory if it does not exist."""
    data_dir = os.path.dirname(ADMIN_FILE)
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)


def _atomic_write(filepath: str, data) -> None:
    """
    Write JSON data to filepath atomically (temp file → rename).
    Prevents corruption if the process crashes mid-write.
    """
    _ensure_data_dir()
    dir_path = os.path.dirname(filepath) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        shutil.move(tmp_path, filepath)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


# ══════════════════════════════════════════════════════════
# REGULAR USERS  (data/users.json  OR  USERS_DATA env var)
# ══════════════════════════════════════════════════════════

def load_users() -> list:
    """Return list of all registered user dicts."""
    # 1. In-memory cache hit (valid for the lifetime of this container)
    if _cache["users"] is not None:
        return _cache["users"]

    users: list = []

    if _ON_VERCEL:
        # 2. Read from USERS_DATA environment variable (JSON array string)
        raw = os.environ.get("USERS_DATA", "").strip()
        if raw:
            try:
                users = json.loads(raw)
            except (json.JSONDecodeError, ValueError):
                users = []
    else:
        # 2. Read from local JSON file
        _ensure_data_dir()
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as f:
                    users = json.load(f)
            except (json.JSONDecodeError, IOError):
                users = []

    _cache["users"] = users
    return users


def save_users(users: list) -> None:
    """
    Persist user list.
    - Always updates the in-memory cache immediately.
    - Local:  writes to data/users.json atomically.
    - Vercel: updates os.environ["USERS_DATA"] for the current container
              AND calls the Vercel API so the value survives cold-starts.
    """
    _cache["users"] = users  # Update cache first so current request sees it

    if _ON_VERCEL:
        serialized = json.dumps(users, ensure_ascii=False)
        os.environ["USERS_DATA"] = serialized          # Current container
        _vercel_update_env("USERS_DATA", serialized)   # Future containers
    else:
        _atomic_write(USERS_FILE, users)


def register_user(username: str, password: str) -> dict:
    """
    Register a new regular user.
    Raises ValueError if username already taken or validation fails.
    Returns the new user dict.
    """
    username = username.strip().lower()
    if not username or not password:
        raise ValueError("Username and password cannot be empty.")
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters.")
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters.")

    users = load_users()
    if any(u["username"] == username for u in users):
        raise ValueError(f"Username '{username}' is already taken.")

    user = {
        "username":      username,
        "display_name":  username.capitalize(),
        "password_hash": generate_password_hash(password),
        "role":          "user",
        "created_at":    datetime.now().isoformat(),
    }
    users.append(user)
    save_users(users)
    return user


def verify_user(username: str, password: str) -> Optional[dict]:
    """
    Verify credentials for a regular user.
    Returns user dict if valid, None otherwise.
    """
    username = username.strip().lower()
    users = load_users()
    for user in users:
        if user["username"] == username:
            if check_password_hash(user["password_hash"], password):
                return user
    return None


def get_user(username: str) -> Optional[dict]:
    """Fetch a user dict by username."""
    username = username.strip().lower()
    users = load_users()
    return next((u for u in users if u["username"] == username), None)


def get_all_users() -> list:
    """Return all registered users (without password hashes)."""
    return [
        {k: v for k, v in u.items() if k != "password_hash"}
        for u in load_users()
    ]


def delete_user(username: str) -> bool:
    """
    Delete a regular user account by username.
    Returns True if deleted, False if not found.
    """
    username = username.strip().lower()
    users = load_users()
    new_users = [u for u in users if u["username"] != username]
    if len(new_users) == len(users):
        return False  # Not found
    save_users(new_users)
    return True


def change_user_password(username: str, old_password: str, new_password: str) -> None:
    """
    Change a regular user's password after verifying the old one.
    Raises ValueError on any validation failure.
    """
    username = username.strip().lower()
    if not old_password:
        raise ValueError("Current password is required.")
    if not new_password or len(new_password.strip()) < 6:
        raise ValueError("New password must be at least 6 characters.")
    if old_password == new_password:
        raise ValueError("New password must differ from the current password.")

    users = load_users()
    for user in users:
        if user["username"] == username:
            if not check_password_hash(user["password_hash"], old_password):
                raise ValueError("Current password is incorrect.")
            user["password_hash"] = generate_password_hash(new_password.strip())
            user["updated_at"]    = datetime.now().isoformat()
            save_users(users)
            return
    raise ValueError(f"User '{username}' not found.")


# ══════════════════════════════════════════════════════════
# ADMIN CREDENTIALS  (data/admin.json  OR  ADMIN_CREDS env var)
# ══════════════════════════════════════════════════════════

def _build_default_admin() -> dict:
    """Return a fresh admin credential dict using default/env-var values."""
    return {
        "username":      _DEFAULT_ADMIN_USERNAME,
        "password_hash": generate_password_hash(_DEFAULT_ADMIN_PASSWORD),
        "created_at":    datetime.now().isoformat(),
    }


def _bootstrap_admin_file() -> None:
    """
    Create data/admin.json with default credentials if it doesn't exist.
    Only runs in local (non-Vercel) environments.
    """
    if not _ON_VERCEL and not os.path.exists(ADMIN_FILE):
        try:
            _atomic_write(ADMIN_FILE, _build_default_admin())
        except Exception:
            pass  # Read-only FS — fall back silently


# Auto-bootstrap on module load (local only)
_bootstrap_admin_file()


def load_admin_credentials() -> dict:
    """
    Load admin credentials from the appropriate backend.
    Priority:
      1. In-memory cache
      2a. Vercel: ADMIN_CREDS env var (JSON blob)
      2b. Vercel: ADMIN_USERNAME + ADMIN_PASSWORD_HASH individual env vars
      2c. Vercel: ADMIN_USERNAME + ADMIN_PASSWORD (plain, hashed at runtime)
      3.  Local:  data/admin.json
      4.  Fallback: built-in defaults
    """
    # 1. Cache hit
    if _cache["admin"] is not None:
        return _cache["admin"]

    creds: Optional[dict] = None

    if _ON_VERCEL:
        # 2a. Full JSON blob (set by _save_admin_credentials)
        raw = os.environ.get("ADMIN_CREDS", "").strip()
        if raw:
            try:
                data = json.loads(raw)
                if "username" in data and "password_hash" in data:
                    creds = data
            except Exception:
                pass

        # 2b. Individual env vars with pre-hashed password
        if creds is None:
            username = os.environ.get("ADMIN_USERNAME", "").strip()
            pw_hash  = os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
            if username and pw_hash:
                creds = {
                    "username":      username,
                    "password_hash": pw_hash,
                    "created_at":    datetime.now().isoformat(),
                }

        # 2c. Plain-text ADMIN_PASSWORD — hash it now and cache
        if creds is None:
            username = os.environ.get("ADMIN_USERNAME", "admin").strip()
            raw_pw   = os.environ.get("ADMIN_PASSWORD", _DEFAULT_ADMIN_PASSWORD)
            creds = {
                "username":      username,
                "password_hash": generate_password_hash(raw_pw),
                "created_at":    datetime.now().isoformat(),
            }
    else:
        # 3. Local file
        if os.path.exists(ADMIN_FILE):
            try:
                with open(ADMIN_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "username" in data and "password_hash" in data:
                        creds = data
            except Exception:
                pass

    if creds is None:
        creds = _build_default_admin()

    _cache["admin"] = creds
    return creds


def _save_admin_credentials(creds: dict) -> None:
    """
    Internal: persist admin credentials to the appropriate backend.
    - Always updates in-memory cache first.
    - Local:  writes atomically to data/admin.json.
    - Vercel: updates os.environ["ADMIN_CREDS"] for the current container
              AND pushes to Vercel API for future containers.
    """
    _cache["admin"] = creds  # Current container sees change immediately

    if _ON_VERCEL:
        serialized = json.dumps(creds, ensure_ascii=False)
        os.environ["ADMIN_CREDS"] = serialized          # Current container
        _vercel_update_env("ADMIN_CREDS", serialized)   # Future containers
    else:
        _atomic_write(ADMIN_FILE, creds)


def get_admin_username() -> str:
    """Return the current admin username."""
    return load_admin_credentials()["username"]


def verify_admin(username: str, password: str) -> bool:
    """Verify admin login credentials against stored hash."""
    creds = load_admin_credentials()
    if username.strip() == creds["username"]:
        return check_password_hash(creds["password_hash"], password)
    return False


def verify_admin_password(password: str) -> bool:
    """
    Check whether `password` matches the currently stored admin password.
    Used to validate the old password before allowing a credential change.
    """
    creds = load_admin_credentials()
    return check_password_hash(creds["password_hash"], password)


def update_admin_credentials(
    new_username: str,
    new_password: Optional[str] = None,
    *,
    old_password: Optional[str] = None,
    require_old_password: bool = False,
) -> None:
    """
    Update admin username and/or password.

    Args:
        new_username:         Desired new username (required).
        new_password:         Desired new password (optional; leave None to keep current).
        old_password:         The current password for verification.
        require_old_password: If True, raises ValueError when old_password is wrong.

    Raises:
        ValueError: On validation failure or wrong old password.
    """
    new_username = new_username.strip()
    if not new_username:
        raise ValueError("Admin username cannot be empty.")
    if len(new_username) < 3:
        raise ValueError("Admin username must be at least 3 characters.")

    if require_old_password:
        if not old_password:
            raise ValueError("Current password is required to make changes.")
        if not verify_admin_password(old_password):
            raise ValueError("Current password is incorrect.")

    creds = load_admin_credentials()
    creds["username"]   = new_username
    creds["updated_at"] = datetime.now().isoformat()

    if new_password:
        new_password = new_password.strip()
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters.")
        creds["password_hash"] = generate_password_hash(new_password)

    _save_admin_credentials(creds)


def change_admin_password(old_password: str, new_password: str) -> None:
    """
    Change admin password after verifying the old one.
    Raises ValueError on any validation failure.
    """
    if not old_password:
        raise ValueError("Current password is required.")
    if not verify_admin_password(old_password):
        raise ValueError("Current password is incorrect.")
    if not new_password or len(new_password.strip()) < 6:
        raise ValueError("New password must be at least 6 characters.")
    if old_password == new_password:
        raise ValueError("New password must differ from the current password.")

    creds = load_admin_credentials()
    creds["password_hash"] = generate_password_hash(new_password.strip())
    creds["updated_at"]    = datetime.now().isoformat()
    _save_admin_credentials(creds)
