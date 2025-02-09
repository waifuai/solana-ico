# ContextCoin (CTX) Solana CLI

This CLI tool is designed to interact with the ContextCoin (CTX) token on the Solana blockchain, facilitating access to resources within the Model Context Protocol (MCP) ecosystem.

## Overview

ContextCoin (CTX) is a Solana-based token designed to provide a secure and scalable solution for accessing resources within the Model Context Protocol (MCP) ecosystem. This token facilitates micro-payments for resource access, effectively preventing spam and DDoS attacks, while encouraging a thriving, decentralized economy.

The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. Think of MCP like a USB-C port for AI applications. Just as USB-C provides a standardized way to connect your devices to various peripherals and accessories, MCP provides a standardized way to connect AI models to different data sources and tools.

## Key Features

*   **Secure Resource Access:** Uses CTX payments to prevent spam and DDoS attacks.
*   **Dynamic Pricing:** Allows resource providers to set prices based on demand.
*   **Micro-payments:** Enables efficient and cost-effective access to resources.
*   **Decentralized:** Leverages the speed and security of the Solana blockchain.
*   **Open-Source:** Encourages community contributions and transparency.
*   **Bonding Curve ICO:** Utilizes a bonding curve model for initial token distribution.
*   **SPL Token:** Uses the standard SPL token program.
*   **Micro-Transactions:** Allows the usage of micro-transactions for resource access.
*   **Customizable:** Uses custom program-derived addresses for ease of use.

## Tokenomics

*   **Name:** ContextCoin
*   **Symbol:** CTX
*   **Total Supply:** 1,000,000,000 CTX (Fixed)
*   **Decimals:** 9
*   **Initial Distribution:**
    *   20% - Team & Development (Locked for 1 year, then vesting)
    *   30% - Ecosystem Fund (Grants, partnerships, future development)
    *   50% - Initial Sale (Bonding curve ICO)
*   **Utility:**
    *   Pay-per-access to resources within the Model Context Protocol (MCP) ecosystem.
    *   Future options for staking and governance.

## Getting Started

### Prerequisites

*   [Python](https://www.python.org/) (latest stable)
*   [Solana Tool Suite](https://docs.solana.com/cli/install-solana-cli-tools) (v1.17 or later)
*   Basic understanding of Solana and smart contracts

### Installation

```bash
pip install solana
```

### Usage

(To be added as the CLI is developed)

## Smart Contract Details

The smart contract is written in Rust and leverages the Solana program library. It provides the following functionality:

*   **ICO Initialization:** Sets up the initial state for token distribution and pricing.
*   **Token Purchasing:** Allows users to buy CTX tokens using SOL, while adhering to the configured bonding curve.
*   **Token Selling:** Allows users to sell back CTX tokens, receiving SOL.
*   **Withdraw Funds:** Allows the owner of the ICO to withdraw the accumulated SOL from the escrow.
*   **Resource Creation:** Enables MCP resource providers to register their resources and set access fees.
*   **Resource Access:** Facilitates pay-per-access to resources, rewarding resource providers and preventing malicious attacks.

## Code Structure

*   `mcp-cli/main.py`: Main CLI entry point.
*   `mcp-cli/tokenomics.py`: Tokenomics details.
*   `mcp-cli/solana_utils.py`: Solana-related helper functions.
*   `mcp-cli/docs/`: Documentation files.

## Contributing

(To be added)

## Future Development

*   Staking and governance mechanisms for CTX holders.
*   Tiered access levels for resources based on CTX holdings.
*   Integration with decentralized exchanges (DEXs) on Solana.
*   More sophisticated bonding curve options.
*   Dynamic fee adjustments based on network conditions.
*   Enhanced security measures and audits.
*   CLI tooling to aid users in building on top of the contracts.

## Disclaimer

This project is provided as-is and is for educational and experimental purposes. Please use it responsibly and do your own due diligence before making any financial decisions. No guarantees are made about the security or stability of the system.

## License

This project is licensed under the MIT-0 License - see the [LICENSE](../LICENSE) file for details.