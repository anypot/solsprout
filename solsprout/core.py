import base58

from bip_utils import (
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip32Slip10Ed25519,
    SolAddrEncoder,
)


class DerivationError(Exception):
    pass


class ValidationError(DerivationError):
    pass


def validate_mnemonic(mnemonic: str) -> None:
    if not Bip39MnemonicValidator().IsValid(mnemonic):
        raise ValidationError("Invalid BIP-39 mnemonic")


def derive_solana_keypair(
    mnemonic: str,
    passphrase: str = "",
    account_index: int = 0,
    address_index: int = 0,
) -> tuple[bytes, bytes]:
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    bip32_ctx = Bip32Slip10Ed25519.FromSeed(seed_bytes)

    # Derivation path: m/44'/501'/account'/address' (Phantom/Solflare)
    # derivation_path = f"m/44'/501'/{account_index}'/{address_index}'"
    # Derivation path: m/44'/501'/account'' (Ledger Live)
    derivation_path = f"m/44'/501'/{account_index}'"
    derived_key = bip32_ctx.DerivePath(derivation_path)

    private_key_bytes = derived_key.PrivateKey().Raw().ToBytes()
    public_key_bytes = derived_key.PublicKey().RawCompressed().ToBytes()

    return public_key_bytes, private_key_bytes


def encode_public_key(pub_bytes: bytes) -> str:
    return SolAddrEncoder.EncodeKey(pub_bytes)


def encode_private_key(priv_bytes: bytes) -> str:
    return base58.b58encode(priv_bytes).decode()
