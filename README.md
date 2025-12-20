# solsprout

`solsprout` is a **CLI tool to derive Solana addresses and private keys** from a BIP-39 mnemonic.  
It supports **batch derivation**, **JSON/text output**, **address-only mode by default**, and **secure handling** of sensitive data.

---

## ⚡ Features

- Derive **single or multiple Solana accounts** from a mnemonic
- Read mnemonic and optional passphrase from:
  - YAML file
  - Secure prompt
  - Environment variables `SOLSPROUT_MNEMONIC` and `SOLSPROUT_PASSPHRASE` (override YAML/prompt)
- **Batch derivation** using `--account-index-from` / `--account-index-to` and `--address-index-from` / `--address-index-to`
- **Single account/address derivation** using `-a / --account-address` in format `<account_index>:<address_index>`
- Output formats:
  - **Text** (default)
  - **JSON** (valid array for multiple accounts)
- **Address-only by default**; include private keys with `--show-private-keys`
- **Secure handling**:
  - Overwrites mnemonic, passphrase, and private keys in memory after use
- CLI version: `--version`
- Works with **Python 3.13+** and integrates with **UV environment**

---

## 🔧 Installation (with UV, cross-platform)

You can run the following commands depending on your platform. This will **create a virtual environment and install dependencies** in one go.

### Linux / macOS (bash/zsh)

```bash
uv venv && source .venv/bin/activate && uv pip install -e . && deactivate
````

### Windows (Command Prompt)

```cmd
uv venv && .venv\Scripts\activate.bat && uv pip install -e . && deactivate
```

### Windows (PowerShell)

```powershell
uv venv; .\.venv\Scripts\Activate.ps1; uv pip install -e .; deactivate
```

> After this, your environment is ready, and you can run the CLI via UV.

---

## 🚀 Usage (UV-aligned)

### 📌 Example YAML + CLI Workflow

```bash
# wallet.yaml
mnemonic: "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
passphrase: "mysecretpass"

# CLI
uv run solsprout -f wallet.yaml --account-index-from 0 --account-index-to 2 --output json
```

### Basic usage

```bash
# Read mnemonic from YAML, derive account 0, addresses 0-2 (default)
uv run solsprout -f wallet.yaml

# Prompt for mnemonic
uv run solsprout -p --account-index-from 0 --account-index-to 0
```

### Batch derivation

```bash
# Derive accounts 0 to 3, addresses 0 to 2
uv run solsprout -f wallet.yaml --account-index-from 0 --account-index-to 3
```

### Single account/address derivation

```bash
# Derive only account 1, address 2
uv run solsprout -f wallet.yaml -a 1:2
```

### Show private keys

```bash
# Include private keys in output
uv run solsprout -f wallet.yaml --account-index-from 0 --account-index-to 2 --show-private-keys
```

### JSON output

```bash
# Batch derive accounts 0 to 3 in JSON format
uv run solsprout -f wallet.yaml --account-index-from 0 --account-index-to 3 --output json
```

**Example JSON output (with private keys):**

```json
[
  {
    "account_index": 0,
    "address_index": 0,
    "address": "7W9uJ9bQ1FJ...",
    "public_key": "7W9uJ9bQ1FJ...",
    "private_key": "3sQJ2p8D..."
  },
  {
    "account_index": 0,
    "address_index": 1,
    "address": "5HgK8f1A2Kx...",
    "public_key": "5HgK8f1A2Kx...",
    "private_key": "7YwT9rKp..."
  }
]
```

### Address-only mode (default)

```bash
# Derive addresses only (default), without private keys
uv run solsprout -f wallet.yaml --account-index-from 0 --account-index-to 3
```

**Example output (text):**

```
=== solsprout — Solana Key Derivation ===
Account Index: 0, Address Index: 0
Address / Public Key: 7W9uJ9bQ1FJ...

=== solsprout — Solana Key Derivation ===
Account Index: 0, Address Index: 1
Address / Public Key: 5HgK8f1A2Kx...
```

### Prompt for passphrase

```bash
# Prompt for mnemonic and passphrase securely
uv run solsprout -p --prompt-passphrase --account-index-from 0 --account-index-to 2
```

---

## 🛡 Security Notes

* The script **overwrites mnemonic, passphrase, and private keys in memory** after use to reduce exposure
* By default only addresses are derived; **private keys are included only with `--show-private-keys`**
* **Never share your private keys**. Keep your mnemonic and YAML file secure.

---

## ⚙ CLI Options

| Option                      | Description                                                   |
| --------------------------- | ------------------------------------------------------------- |
| `-f, --file PATH`           | YAML file containing mnemonic and optional passphrase         |
| `-p, --prompt`              | Prompt for mnemonic securely                                  |
| `--prompt-passphrase`       | Prompt for passphrase instead of reading from file/env        |
| `-a, --account-address STR` | Single account/address pair `<account_index>:<address_index>` |
| `--account-index-from INT`  | Start index for batch derivation of accounts                  |
| `--account-index-to INT`    | End index for batch derivation of accounts                    |
| `--address-index-from INT`  | Start index for multiple addresses per account                |
| `--address-index-to INT`    | End index for multiple addresses per account                  |
| `--output {text,json}`      | Output format (default: text)                                 |
| `--show-private-keys`       | Include private keys in output (default: addresses only)      |
| `--version`                 | Show CLI version                                              |

---

## 📝 Notes

* Solana addresses **are the same as public keys**, so in outputs, `address` and `public_key` are identical.
* JSON output always produces a **valid array**, even when deriving multiple accounts.
* Environment variables `SOLSPROUT_MNEMONIC` and `SOLSPROUT_PASSPHRASE` can override YAML or prompt input.

---

## ⚡ Version

`v0.1.0` — Initial version: batch derivation, JSON/text output, address-only default, optional private keys with `--show-private-keys`, single account/address support, direct CLI via UV.
