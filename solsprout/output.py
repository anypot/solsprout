import json


AccountData = tuple[int, int, bytes, bytes | None]


def format_account(
    acc_idx: int,
    addr_idx: int,
    pub_bytes: bytes,
    priv_bytes: bytes | None,
    encode_pub,
    encode_priv,
    show_private_keys: bool = False,
) -> dict:
    address = encode_pub(pub_bytes)
    entry = {
        "account_index": acc_idx,
        "address_index": addr_idx,
        "address": address,
        "public_key": address,
    }
    if show_private_keys and priv_bytes is not None:
        entry["private_key"] = encode_priv(priv_bytes)
    return entry


def output_json(
    accounts: list[AccountData],
    encode_pub,
    encode_priv,
    show_private_keys: bool = False,
):
    json_list = [
        format_account(
            acc_idx,
            addr_idx,
            pub_bytes,
            priv_bytes,
            encode_pub,
            encode_priv,
            show_private_keys,
        )
        for acc_idx, addr_idx, pub_bytes, priv_bytes in accounts
    ]
    print(json.dumps(json_list, indent=2))


def output_text(
    accounts: list[AccountData],
    encode_pub,
    encode_priv,
    show_private_keys: bool = False,
):
    for acc_idx, addr_idx, pub_bytes, priv_bytes in accounts:
        address = encode_pub(pub_bytes)
        print("\n=== solsprout — Solana Key Derivation ===")
        print(f"Account Index: {acc_idx}, Address Index: {addr_idx}")
        print("Address / Public Key:", address)
        if show_private_keys and priv_bytes is not None:
            private_key = encode_priv(priv_bytes)
            print("Private Key (DO NOT SHARE):", private_key)


def clear_sensitive_data(
    accounts: list[AccountData], show_private_keys: bool = False
) -> None:
    if show_private_keys:
        for i in range(len(accounts)):
            acc_idx, addr_idx, pub_bytes, priv_bytes = accounts[i]
            if priv_bytes is not None:
                priv_array = bytearray(priv_bytes)
                for j in range(len(priv_array)):
                    priv_array[j] = 0
                accounts[i] = (acc_idx, addr_idx, pub_bytes, None)
