import argparse
import base58
import json
import getpass
import os
import yaml
from pathlib import Path

from bip_utils import (
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
)

VERSION = "0.1.0"


def read_yaml_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "mnemonic" not in data or not data["mnemonic"]:
        raise ValueError("YAML file must contain a non-empty 'mnemonic'")

    passphrase = data.get("passphrase", "")
    return data["mnemonic"], passphrase


def get_secret(prompt_msg: str) -> str:
    """Read secret from prompt safely"""
    return getpass.getpass(prompt_msg).strip()


def get_mnemonic_and_passphrase(yaml_file=None, prompt_passphrase=False):
    """
    Priority order:
    1. Environment variables
    2. YAML file
    3. Interactive prompt (mnemonic always)
    """

    mnemonic = None
    passphrase = None

    # 1. Check environment variables first
    mnemonic = os.getenv("SOLSPROUT_MNEMONIC")
    passphrase = os.getenv("SOLSPROUT_PASSPHRASE")

    if mnemonic and passphrase is None:
        passphrase = ""  # default empty if only mnemonic is set

    # 2. Fallback to YAML if env var not set
    if not mnemonic and yaml_file:
        mnemonic, yaml_passphrase = read_yaml_file(yaml_file)
        if passphrase is None:
            passphrase = yaml_passphrase

    # 3. Fallback to interactive prompt
    if not mnemonic:
        mnemonic = get_secret("Enter mnemonic (hidden): ")
        if not mnemonic:
            raise ValueError("Mnemonic cannot be empty")

    # 4. Prompt for passphrase if requested or empty
    if prompt_passphrase or passphrase is None:
        passphrase_input = get_secret(
            "Enter passphrase (hidden, leave empty for none): "
        )
        passphrase = passphrase_input if passphrase_input else passphrase or ""

    return mnemonic, passphrase


def validate_mnemonic(mnemonic: str):
    if not Bip39MnemonicValidator().IsValid(mnemonic):
        raise ValueError("Invalid BIP-39 mnemonic")


def derive_solana_keypair(
    mnemonic: str,
    passphrase: str = "",
    account_index: int = 0,
    address_index: int = 0,
):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    bip44_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.SOLANA)

    account = (
        bip44_ctx.Purpose()
        .Coin()
        .Account(account_index)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(address_index)
    )

    private_key_bytes = account.PrivateKey().Raw().ToBytes()
    public_key_bytes = account.PublicKey().RawCompressed().ToBytes()

    return public_key_bytes, private_key_bytes  # public key = address


def output_result_batch(accounts, fmt, show_private_keys=False):
    """
    accounts: list of tuples (account_index, address_index, public_key_bytes, private_key_bytes)
    """
    if fmt == "json":
        json_list = []
        for acc_idx, addr_idx, pub_bytes, priv_bytes in accounts:
            address = base58.b58encode(pub_bytes).decode()
            entry = {
                "account_index": acc_idx,
                "address_index": addr_idx,
                "address": address,
                "public_key": address,
            }
            if show_private_keys:
                private_key = base58.b58encode(priv_bytes).decode()
                entry["private_key"] = private_key
            json_list.append(entry)
        print(json.dumps(json_list, indent=2))
    else:
        for acc_idx, addr_idx, pub_bytes, priv_bytes in accounts:
            address = base58.b58encode(pub_bytes).decode()
            print("\n=== solsprout — Solana Key Derivation ===")
            print(f"Account Index: {acc_idx}, Address Index: {addr_idx}")
            print("Address / Public Key:", address)
            if show_private_keys:
                private_key = base58.b58encode(priv_bytes).decode()
                print("Private Key (DO NOT SHARE):", private_key)


def clear_sensitive_data(mnemonic, passphrase, accounts, show_private_keys=False):
    """
    Overwrite sensitive variables to reduce memory exposure
    """
    if mnemonic is not None:
        mnemonic = None
    if passphrase is not None:
        passphrase = None

    if show_private_keys:
        for i in range(len(accounts)):
            acc_idx, addr_idx, pub_bytes, priv_bytes = accounts[i]
            if priv_bytes is not None:
                priv_array = bytearray(priv_bytes)
                for j in range(len(priv_array)):
                    priv_array[j] = 0
                accounts[i] = (acc_idx, addr_idx, pub_bytes, None)


def parse_args():
    """Parse CLI arguments and return args"""
    parser = argparse.ArgumentParser(
        description="solsprout — Solana key derivation CLI"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"solsprout {VERSION}",
    )

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-f",
        "--file",
        type=Path,
        help="YAML file containing mnemonic and optional passphrase",
    )
    group.add_argument(
        "-p",
        "--prompt",
        action="store_true",
        help="Read mnemonic from secure prompt",
    )

    parser.add_argument(
        "-a",
        "--account-address",
        type=str,
        help="Single account/address pair in format <account_index>:<address_index> (e.g., 0:2)",
    )

    parser.add_argument(
        "--account-index-from",
        type=int,
        default=None,
        help="Start index for batch derivation of accounts",
    )

    parser.add_argument(
        "--account-index-to",
        type=int,
        default=None,
        help="End index for batch derivation of accounts",
    )

    parser.add_argument(
        "--prompt-passphrase",
        action="store_true",
        help="Prompt for passphrase instead of reading from file/env",
    )

    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--show-private-keys",
        action="store_true",
        help="Include private keys in output (default: addresses only)",
    )

    parser.add_argument(
        "--address-index-from",
        type=int,
        default=0,
        help="Start index for multiple addresses per account (default: 0)",
    )

    parser.add_argument(
        "--address-index-to",
        type=int,
        default=2,
        help="End index for multiple addresses per account (default: 2)",
    )

    return parser.parse_args()


def determine_indices(args):
    """
    Determine account and address indices to derive based on CLI arguments.
    Returns two lists: acc_indices, addr_indices
    """
    if args.account_address:
        try:
            acc_str, addr_str = args.account_address.split(":")
            acc_indices = [int(acc_str)]
            addr_indices = [int(addr_str)]
        except Exception:
            raise ValueError(
                "Invalid format for -a/--account-address. Use <account_index>:<address_index>, e.g., 0:2"
            )
    else:
        # Account batch
        if args.account_index_from is not None and args.account_index_to is not None:
            if args.account_index_from > args.account_index_to:
                raise ValueError(
                    "--account-index-from cannot be greater than --account-index-to"
                )
            acc_indices = range(args.account_index_from, args.account_index_to + 1)
        elif args.account_index_from is None and args.account_index_to is None:
            acc_indices = [0]  # default account index
        else:
            raise ValueError(
                "Both --account-index-from and --account-index-to must be specified for batch derivation"
            )

        # Address batch
        addr_indices = range(args.address_index_from, args.address_index_to + 1)

    return acc_indices, addr_indices


def main():
    args = parse_args()

    mnemonic, passphrase = get_mnemonic_and_passphrase(
        yaml_file=args.file, prompt_passphrase=args.prompt_passphrase
    )

    validate_mnemonic(mnemonic)

    # Determine account and address indices
    acc_indices, addr_indices = determine_indices(args)

    # Derive accounts & addresses
    accounts = []
    for acc_idx in acc_indices:
        for addr_idx in addr_indices:
            pub_bytes, priv_bytes = derive_solana_keypair(
                mnemonic,
                passphrase=passphrase,
                account_index=acc_idx,
                address_index=addr_idx,
            )
            accounts.append((acc_idx, addr_idx, pub_bytes, priv_bytes))

    output_result_batch(accounts, args.output, show_private_keys=args.show_private_keys)

    clear_sensitive_data(
        mnemonic, passphrase, accounts, show_private_keys=args.show_private_keys
    )


if __name__ == "__main__":
    main()
