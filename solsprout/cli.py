import argparse
from pathlib import Path

from .config import VERSION, DEFAULT_ADDRESS_INDEX_FROM, DEFAULT_ADDRESS_INDEX_TO
from .core import (
    derive_solana_keypair,
    validate_mnemonic,
    encode_public_key,
    encode_private_key,
    ValidationError,
)
from .io import get_mnemonic_and_passphrase, InputError
from .output import output_json, output_text, clear_sensitive_data


def parse_args():
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
        type=str,
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
        default=DEFAULT_ADDRESS_INDEX_FROM,
        help=f"Start index for multiple addresses per account (default: {DEFAULT_ADDRESS_INDEX_FROM})",
    )

    parser.add_argument(
        "--address-index-to",
        type=int,
        default=DEFAULT_ADDRESS_INDEX_TO,
        help=f"End index for multiple addresses per account (default: {DEFAULT_ADDRESS_INDEX_TO})",
    )

    return parser.parse_args()


def determine_indices(args):
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
        if args.account_index_from is not None and args.account_index_to is not None:
            if args.account_index_from > args.account_index_to:
                raise ValueError(
                    "--account-index-from cannot be greater than --account-index-to"
                )
            acc_indices = range(args.account_index_from, args.account_index_to + 1)
        elif args.account_index_from is None and args.account_index_to is None:
            acc_indices = [0]
        else:
            raise ValueError(
                "Both --account-index-from and --account-index-to must be specified for batch derivation"
            )

        addr_indices = range(args.address_index_from, args.address_index_to + 1)

    return acc_indices, addr_indices


def main():
    args = parse_args()

    yaml_file = Path(args.file) if args.file else None

    try:
        mnemonic, passphrase = get_mnemonic_and_passphrase(
            yaml_file=yaml_file, prompt_passphrase=args.prompt_passphrase
        )
    except InputError as e:
        raise SystemExit(f"Error: {e}")

    try:
        validate_mnemonic(mnemonic)
    except ValidationError as e:
        raise SystemExit(f"Error: {e}")

    acc_indices, addr_indices = determine_indices(args)

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

    if args.output == "json":
        output_json(
            accounts,
            encode_public_key,
            encode_private_key,
            show_private_keys=args.show_private_keys,
        )
    else:
        output_text(
            accounts,
            encode_public_key,
            encode_private_key,
            show_private_keys=args.show_private_keys,
        )

    clear_sensitive_data(accounts, show_private_keys=args.show_private_keys)


if __name__ == "__main__":
    main()
