"""
Launch multiple bot processes from a single service.

Uses API_KEYS (comma-separated). Optional WALLET_ADDRESSES (comma-separated).
Optional TARGET_GAME_IDS (comma-separated).
Optional AGENT_NAMES (comma-separated).
If WALLET_ADDRESSES has 1 value, it is reused for all keys.
If TARGET_GAME_IDS has 1 value, it is reused for all keys.
If AGENT_NAMES has 1 value, it is reused for all keys.
"""

import os
import signal
import subprocess
import sys
import time
from typing import List

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def _split_env_list(raw: str) -> List[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def _build_env(
    base_env: dict,
    api_key: str,
    wallet_address: str,
    target_game_id: str,
    agent_name: str,
) -> dict:
    env = dict(base_env)
    env["API_KEY"] = api_key
    if wallet_address:
        env["WALLET_ADDRESS"] = wallet_address
    if target_game_id:
        env["TARGET_GAME_ID"] = target_game_id
    if agent_name:
        env["AGENT_NAME"] = agent_name
    return env


def _resolve_wallets(keys: List[str], wallets: List[str]) -> List[str]:
    if not wallets:
        return [""] * len(keys)
    if len(wallets) == 1:
        return wallets * len(keys)
    if len(wallets) != len(keys):
        raise ValueError("WALLET_ADDRESSES must have 1 value or match API_KEYS count")
    return wallets


def _resolve_game_ids(keys: List[str], game_ids: List[str]) -> List[str]:
    if not game_ids:
        return [""] * len(keys)
    if len(game_ids) == 1:
        return game_ids * len(keys)
    if len(game_ids) != len(keys):
        raise ValueError("TARGET_GAME_IDS must have 1 value or match API_KEYS count")
    return game_ids


def _resolve_agent_names(keys: List[str], agent_names: List[str]) -> List[str]:
    if not agent_names:
        return [""] * len(keys)
    if len(agent_names) == 1:
        return agent_names * len(keys)
    if len(agent_names) != len(keys):
        raise ValueError("AGENT_NAMES must have 1 value or match API_KEYS count")
    return agent_names


def main() -> int:
    raw_keys = os.environ.get("API_KEYS", "")
    keys = _split_env_list(raw_keys)
    if not keys:
        # Fallback to single-key mode for local/dev usage.
        api_key = os.environ.get("API_KEY", "").strip()
        if not api_key:
            print("Missing API_KEYS or API_KEY", file=sys.stderr)
            return 1
        keys = [api_key]

    raw_wallets = os.environ.get("WALLET_ADDRESSES", "")
    wallets = _split_env_list(raw_wallets)
    raw_game_ids = os.environ.get("TARGET_GAME_IDS", "")
    game_ids = _split_env_list(raw_game_ids)
    raw_agent_names = os.environ.get("AGENT_NAMES", "")
    agent_names = _split_env_list(raw_agent_names)
    try:
        wallet_list = _resolve_wallets(keys, wallets)
        game_id_list = _resolve_game_ids(keys, game_ids)
        agent_name_list = _resolve_agent_names(keys, agent_names)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    base_env = os.environ.copy()
    base_env.pop("API_KEYS", None)
    base_env.pop("WALLET_ADDRESSES", None)
    base_env.pop("TARGET_GAME_IDS", None)
    base_env.pop("AGENT_NAMES", None)

    procs: List[subprocess.Popen] = []

    def _shutdown(_signum, _frame):
        for proc in procs:
            if proc.poll() is None:
                proc.terminate()
        deadline = time.time() + 10
        for proc in procs:
            if proc.poll() is None:
                timeout = max(0.0, deadline - time.time())
                try:
                    proc.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    proc.kill()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    for idx, (key, wallet, game_id, agent_name) in enumerate(
        zip(keys, wallet_list, game_id_list, agent_name_list),
        start=1,
    ):
        env = _build_env(base_env, key, wallet, game_id, agent_name)
        print(f"Starting bot {idx}/{len(keys)}")
        procs.append(subprocess.Popen([sys.executable, "main.py"], env=env))

    # Keep parent alive and exit if any child exits unexpectedly.
    while True:
        for proc in procs:
            code = proc.poll()
            if code is not None:
                print(f"Bot exited with code {code}. Shutting down.", file=sys.stderr)
                _shutdown(None, None)
        time.sleep(1)


if __name__ == "__main__":
    raise SystemExit(main())
