# Solana ICO & Resource Management CLI

This CLI tool, built with Python and Typer, allows interaction with a Solana program designed for managing an Initial Coin Offering (ICO) using a bonding curve and controlling access to off-chain resources.

**Note:** This project has undergone significant refactoring. The core logic is now split into modules within the `src/` directory (`solana_client.py`, `ico_manager.py`, `resource_manager.py`, `pda_utils.py`, `config.py`, etc.) and the CLI uses `typer` instead of `argparse`.

## Prerequisites

*   Python 3.8+
*   `pip` package manager
*   A running Solana cluster (e.g., local `solana-test-validator` or a devnet/testnet endpoint).
*   The corresponding Solana program deployed to the target cluster.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd solana-ico
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt --user
    ```

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

## Usage

The main entry point is `src/main.py`. You can run commands using `python -m src.main <command> [subcommand] [arguments]`.

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
*   `ico buy <keypair_path> <amount_lamports> <ico_owner_pubkey>`: Buy tokens from the ICO.
    ```bash
    python -m src.main ico buy /path/to/buyer_keypair.json 50000000 <ico_owner_pubkey>
    ```
*   `ico sell <keypair_path> <amount_tokens> <ico_owner_pubkey>`: Sell tokens back to the ICO.
    ```bash
    python -m src.main ico sell /path/to/seller_keypair.json 100 <ico_owner_pubkey>
    ```
*   `ico withdraw <keypair_path> <amount_lamports>`: Withdraw SOL from escrow (owner only).
    ```bash
    python -m src.main ico withdraw /path/to/owner_keypair.json 100000000
    ```
    **Note:** The `buy` and `sell` commands currently require further implementation details regarding how the `token_mint` is determined (see `src/ico_manager.py`).

**Resource Commands (`resource`):**

*   `resource create <keypair_path> <resource_id> <access_fee>`: Create/update resource access info (server only).
    ```bash
    python -m src.main resource create /path/to/server_keypair.json "my_premium_api" 50000
    ```
*   `resource access <keypair_path> <resource_id> <server_pubkey> <amount_lamports>`: Pay to access a resource.
    ```bash
    python -m src.main resource access /path/to/user_keypair.json "my_premium_api" <server_pubkey> 50000
    ```

## Testing

The project uses `unittest` and `unittest.mock`. Tests are located in the `src/tests/` directory.

To run the tests, ensure you have `pytest` installed (`pip install pytest --user`) and run it from the project root directory:

```bash
pytest
```

The `pytest.ini` file configures `pytest` to find modules within the `src` directory correctly.