import base58

from bip_utils import (
    Bip39SeedGenerator,
    Bip39MnemonicValidator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
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

    return public_key_bytes, private_key_bytes


def encode_public_key(pub_bytes: bytes) -> str:
    return base58.b58encode(pub_bytes).decode()


def encode_private_key(priv_bytes: bytes) -> str:
    return base58.b58encode(priv_bytes).decode()
