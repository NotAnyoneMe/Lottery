import os
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional

from dotenv import load_dotenv, find_dotenv


@dataclass
class Settings:
    bot_token: str
    admin_ids: List[int]
    group_chat_id: int
    log_channel_id: Optional[int] = None
    channel_username: Optional[str] = None
    updates_channel_username: Optional[str] = None


def _parse_admin_ids(value: str) -> List[int]:
    if not value:
        return []
    result: List[int] = []
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(int(part))
        except ValueError:
            raise ValueError("ADMIN_IDS должен быть списком чисел, разделённых запятыми")
    return result


def load_settings() -> Settings:
    # 1) Try to find .env, going up from current working directory
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(dotenv_path=env_path, override=True, encoding="utf-8")
    else:
        # 2) Try .env next to current module (project path on direct run)
        module_env = Path(__file__).parent.parent.parent / ".env"
        if module_env.exists():
            load_dotenv(dotenv_path=module_env.as_posix(), override=True, encoding="utf-8")
        else:
            # 3) Last attempt — standard search in CWD
            load_dotenv(override=True, encoding="utf-8")

    # Get BOT_TOKEN (try both BOT_TOKEN and TOKEN for compatibility)
    bot_token = os.getenv("BOT_TOKEN", "").strip() or os.getenv("TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN or TOKEN not specified in environment")

    # Get GROUP_CHAT_ID (required)
    group_chat_id_raw = os.getenv("GROUP_CHAT_ID", "").strip()
    if not group_chat_id_raw:
        raise RuntimeError("GROUP_CHAT_ID not specified in environment")
    try:
        group_chat_id = int(group_chat_id_raw)
    except ValueError as exc:
        raise RuntimeError("GROUP_CHAT_ID must be a number") from exc

    # Get ADMIN_IDS (required)
    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
    admin_ids = _parse_admin_ids(admin_ids_raw)

    if not admin_ids:
        raise RuntimeError("ADMIN_IDS list is empty. Specify at least one administrator")

    # Get optional LOG_CHANNEL_ID
    log_channel_id = None
    log_channel_id_raw = os.getenv("LOG_CHANNEL_ID", "").strip()
    if log_channel_id_raw:
        try:
            log_channel_id = int(log_channel_id_raw)
        except ValueError:
            print("Warning: LOG_CHANNEL_ID is not a valid number, logging to channel disabled")

    # Get optional channel usernames
    channel_username = os.getenv("CHANNEL_USERNAME", "").strip() or None
    updates_channel_username = os.getenv("UPDATES_CHANNEL_USERNAME", "").strip() or None

    return Settings(
        bot_token=bot_token,
        admin_ids=admin_ids,
        group_chat_id=group_chat_id,
        log_channel_id=log_channel_id,
        channel_username=channel_username,
        updates_channel_username=updates_channel_username,
    )
