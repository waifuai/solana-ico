# ContextCoin (CTX) Solana ICO & Resource Management CLI

A comprehensive CLI tool built with Python and Typer for interacting with a Solana program that manages an Initial Coin Offering (ICO) using an on-chain linear bonding curve and controls access to off-chain resources through pay-to-access functionality.

## ✨ Features

- **🔗 Solana Integration**: Seamless interaction with Solana blockchain programs
- **💰 ICO Management**: Initialize, buy, sell tokens with linear bonding curve
- **🔐 Resource Access**: Pay-to-access system for premium content/resources
- **⚙️ Configuration**: Robust environment variable management with validation
- **🛡️ Error Handling**: Comprehensive error handling with helpful messages
- **📊 Balance Checking**: Query SOL balances for any account
- **💸 SOL Transfers**: Send SOL between accounts
- **🔍 Validation**: Input validation and configuration verification

**Note:** This project has undergone significant refactoring. The core logic is now split into modules within the `src/` directory (`solana_client.py`, `ico_manager.py`, `resource_manager.py`, `pda_utils.py`, `config.py`, etc.) and the CLI uses `typer` instead of `argparse`.

## Prerequisites

*   Python 3.8+
*   `pip` package manager
*   A running Solana cluster (e.g., local `solana-test-validator` or a devnet/testnet endpoint)
*   The corresponding Solana program deployed to the target cluster

## 📦 Recent Improvements

The codebase has undergone significant refactoring and quality improvements:

- **🏗️ Modular Architecture**: Functions broken down into smaller, maintainable components
- **🔧 Type Hints**: Comprehensive type annotations throughout the codebase
- **⚙️ Constants**: Magic numbers replaced with named constants
- **🛡️ Input Validation**: Robust validation for all configuration values and user inputs
- **📚 Documentation**: Enhanced docstrings and CLI help text with examples
- **🎯 Error Handling**: Improved error messages with actionable troubleshooting tips
- **🧹 Code Quality**: Consistent formatting, imports organization, and naming conventions

## 🚀 Quick Start

1. **Clone and setup:**
    ```bash
    git clone <repository_url>
    cd solana-ico
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

2. **Configure environment:**
    ```bash
    export SOLANA_CLUSTER_URL="http://localhost:8899"
    export SOLANA_PROGRAM_ID="YourProgramIdHere"
    ```

3. **Verify setup:**
    ```bash
    python -m src.main config verify
    ```

4. **Check token info:**
    ```bash
    python -m src.main info
    ```

## 📦 Installation

1. **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd solana-ico
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt --user
    ```

3. **Set up environment variables:**
    ```bash
    # For local development
    export SOLANA_CLUSTER_URL="http://localhost:8899"
    export SOLANA_PROGRAM_ID="YourDeployedProgramIdHere"

    # Or create a .env file
    echo "SOLANA_CLUSTER_URL=http://localhost:8899" > .env
    echo "SOLANA_PROGRAM_ID=YourDeployedProgramIdHere" >> .env
    ```

## License

This project is licensed under the MIT-0 License. See the [LICENSE](LICENSE) file for details.

## Configuration

The CLI requires two environment variables to be set:

1.  `SOLANA_CLUSTER_URL`: The HTTP URL of the Solana cluster RPC endpoint.
    *   Defaults to `http://localhost:8899` if not set.
    *   Example: `export SOLANA_CLUSTER_URL="https://api.devnet.solana.com"`
2.  `SOLANA_PROGRAM_ID`: The public key (as a base58 string) of the deployed Solana program.
    *   **This must be set.** There is no default.
    *   Example: `export SOLANA_PROGRAM_ID="YourProgramIdGoesHere..."`

You can set these variables directly in your shell or place them in a `.env` file in the project root directory (the CLI uses `python-dotenv` to load it automatically).

```.env
SOLANA_CLUSTER_URL=http://localhost:8899
SOLANA_PROGRAM_ID=YourProgramIdGoesHere...
```

You can verify the configuration and connection using the `config verify` command.

## 🖥️ Usage

The main entry point is `src/main.py`. You can run commands using `python -m src.main <command> [subcommand] [arguments]`.

### 📋 Available Commands

Get help for any command using `--help`:
```bash
python -m src.main --help          # Show all commands
python -m src.main info --help     # Show help for specific command
python -m src.main ico --help      # Show ICO subcommands
```

**General Commands:**

*   `info`: Display ContextCoin token information.
    ```bash
    python -m src.main info
    ```
*   `balance <public_key>`: Get the SOL balance of an account.
    ```bash
    python -m src.main balance <account_pubkey>
    ```
*   `send <keypair_path> <to_public_key> <amount_lamports>`: Send SOL.
    ```bash
    python -m src.main send /path/to/sender_keypair.json <recipient_pubkey> 100000000
    ```

**Configuration Commands:**

*   `config show`: Display the currently loaded configuration.
    ```bash
    python -m src.main config show
    ```
*   `config verify`: Check configuration and connection to the cluster.
    ```bash
    python -m src.main config verify
    ```

**ICO Commands (`ico`):**

*   `ico init <keypair_path> <token_mint> <total_supply> <base_price> <scaling_factor>`: Initialize the ICO (owner only).
    ```bash
    python -m src.main ico init /path/to/owner_keypair.json <token_mint_pubkey> 1000000000 1000 100000
    ```
*   `ico buy <keypair_path> <amount_lamports> <ico_owner_pubkey> <token_mint>`: Buy tokens from the ICO.
    ```bash
    python -m src.main ico buy /path/to/buyer_keypair.json 50000000 <ico_owner_pubkey> <token_mint_pubkey>
    ```
*   `ico sell <keypair_path> <amount_tokens> <ico_owner_pubkey> <token_mint>`: Sell tokens back to the ICO.
    ```bash
    python -m src.main ico sell /path/to/seller_keypair.json 100 <ico_owner_pubkey> <token_mint_pubkey>
    ```
*   `ico withdraw <keypair_path> <amount_lamports>`: Withdraw SOL from escrow (owner only).
    ```bash
    python -m src.main ico withdraw /path/to/owner_keypair.json 100000000
    ```

**Resource Commands (`resource`):**

*   `resource create <keypair_path> <resource_id> <access_fee>`: Create/update resource access info (server only).
    ```bash
    python -m src.main resource create /path/to/server_keypair.json "my_premium_api" 50000
    ```
*   `resource access <keypair_path> <resource_id> <server_pubkey> <amount_lamports>`: Pay to access a resource.
    ```bash
    python -m src.main resource access /path/to/user_keypair.json "my_premium_api" <server_pubkey> 50000
    ```


## Bonding Curve Mechanism

The ICO utilizes a linear bonding curve implemented directly within the deployed Solana program. This means the actual token price calculation, minting, and burning during `ico buy` and `ico sell` operations happen on-chain according to the parameters set during `ico init` (`base_price`, `scaling_factor`).

The `src/curve_estimator.py` module in this CLI provides a *client-side function* (`calculate_price`) to *estimate* the current token price based on the known `tokenomics` constants. This estimation is for informational purposes and may differ slightly from the exact price calculated by the on-chain program at the moment of a transaction due to potential state changes between estimation and execution.

## Testing

The project uses `unittest` and `unittest.mock`. Tests are located in the `src/tests/` directory.

To run the tests, ensure you have `pytest` installed (`pip install pytest --user`) and run it from the project root directory:

```bash
pytest
```

The `pytest.ini` file configures `pytest` to find modules within the `src` directory correctly.

## Troubleshooting

*   **`SolanaConnectionError`:** This usually means the CLI cannot connect to the Solana cluster specified by `SOLANA_CLUSTER_URL`.
    *   **Verify URL:** Run `python -m src.main config show` and check if the displayed 'Cluster URL' is correct.
    *   **Check Environment:** Ensure `SOLANA_CLUSTER_URL` is set correctly in your environment or `.env` file.
    *   **Run Local Validator:** If using a local cluster (like the default `http://localhost:8899`), make sure `solana-test-validator` is running in a separate terminal.
    *   **Verify Connection:** Use `python -m src.main config verify` to test the connection directly.
*   **`ConfigurationError: SOLANA_PROGRAM_ID environment variable is not set`:** You must set the `SOLANA_PROGRAM_ID` environment variable or add it to your `.env` file, pointing to the deployed program's public key.
*   **`KeypairError`:** Check that the path provided to a keypair file is correct and that the file contains a valid secret key (usually a JSON array or comma-separated list of numbers).