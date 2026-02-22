import getpass
import os
from pathlib import Path

import yaml

from .config import ENV_MNEMONIC, ENV_PASSPHRASE
from .core import ValidationError


class InputError(Exception):
    pass


def read_yaml_file(path: Path) -> tuple[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "mnemonic" not in data or not data["mnemonic"]:
        raise ValueError("YAML file must contain a non-empty 'mnemonic'")

    passphrase = data.get("passphrase", "")
    return data["mnemonic"], passphrase


def get_secret(prompt_msg: str) -> str:
    return getpass.getpass(prompt_msg).strip()


def get_mnemonic_and_passphrase(yaml_file=None, prompt_passphrase=False):
    mnemonic = None
    passphrase = None

    mnemonic = os.getenv(ENV_MNEMONIC)
    passphrase = os.getenv(ENV_PASSPHRASE)

    if mnemonic and passphrase is None:
        passphrase = ""

    if not mnemonic and yaml_file:
        mnemonic, yaml_passphrase = read_yaml_file(yaml_file)
        if passphrase is None:
            passphrase = yaml_passphrase

    if not mnemonic:
        mnemonic = get_secret("Enter mnemonic (hidden): ")
        if not mnemonic:
            raise InputError("Mnemonic cannot be empty")

    if prompt_passphrase or passphrase is None:
        passphrase_input = get_secret(
            "Enter passphrase (hidden, leave empty for none): "
        )
        passphrase = passphrase_input if passphrase_input else passphrase or ""

    return mnemonic, passphrase
