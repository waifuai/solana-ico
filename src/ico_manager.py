"""Manages Initial Coin Offering (ICO) interactions on the Solana blockchain."""

import struct
from solders.pubkey import Pubkey # Corrected
from solders.keypair import Keypair # Corrected
# from solana.transaction import Transaction # Moved
from solders.transaction import Transaction # Corrected import
# from solana.instruction import Instruction, AccountMeta # Moved
from solders.instruction import Instruction, AccountMeta # Corrected import
import solders.system_program as system_program # Corrected
import solders.sysvar as sysvar # Corrected
from spl.token.instructions import ( # Stays (from solana-spl)
    get_associated_token_address,
    create_associated_token_account,
    TOKEN_PROGRAM_ID
)
from solders.rpc.responses import GetAccountInfoResp # Removed RpcResult

# Use relative imports within the 'src' directory
from .solana_client import SolanaClient
from .pda_utils import find_ico_state_pda, find_escrow_pda
from .exceptions import (
    ICOInitializationError,
    TokenPurchaseError,
    TokenSaleError,
    EscrowWithdrawalError,
    TransactionError,
    SolanaIcoError, # For general issues like account not found
    PDAError,
)

# Helper to create and add instruction (consider moving to a shared utils if used elsewhere)
def _create_and_add_instruction(transaction: Transaction, program_id: Pubkey, *accounts: AccountMeta, data: bytes = b''):
    """Creates an instruction and adds it to the transaction."""
    instruction = Instruction(
        program_id=program_id,
        accounts=list(accounts),
        data=data
    )
    transaction.add(instruction)

def initialize_ico(
    solana_client: SolanaClient,
    program_id_str: str,
    owner_keypair: Keypair,
    token_mint_str: str,
    total_supply: int,
    base_price: int,
    scaling_factor: int,
) -> str:
    """
    Initializes the ICO state on the Solana blockchain.

    Args:
        solana_client: An instance of the SolanaClient.
        program_id_str: The program ID as a string.
        owner_keypair: The keypair of the ICO owner.
        token_mint_str: The SPL token mint address as a string.
        total_supply: Total supply of the token.
        base_price: Initial price in lamports.
        scaling_factor: Scaling factor for the bonding curve.
            (These parameters configure the on-chain bonding curve logic.)

    Returns:
        The transaction signature as a string.

    Raises:
        ICOInitializationError: If initialization fails.
        ValueError: If public key strings are invalid.
        PDAError: If PDA derivation fails.
    """
    try:
        program_id_pubkey = Pubkey.from_string(program_id_str)
        token_mint_pubkey = Pubkey.from_string(token_mint_str)
        owner_pubkey = owner_keypair.pubkey()

        # 1. Find PDAs using the utility function
        ico_state_pda, _ = find_ico_state_pda(owner_pubkey, program_id_pubkey)
        escrow_pda, _ = find_escrow_pda(owner_pubkey, program_id_pubkey)

        # 2. Instruction data (using struct.pack for Borsh serialization)
        # Assuming instruction index 0 for InitializeIco
        instruction_data = struct.pack(
            "<BQQQ", # Removed token_mint from pack as it's passed via accounts
            0,  # Instruction index
            total_supply,
            base_price,
            scaling_factor
        )
        # Note: The original struct "<B32sQQQ" included the mint key.
        # Typically, mint is passed as an account, not in instruction data unless required by program.
        # Adjust pack format based on actual program requirements. If mint IS needed in data:
        # instruction_data = struct.pack("<B32sQQQ", 0, bytes(token_mint_pubkey), total_supply, base_price, scaling_factor)


        # 3. Create Accounts for the Instruction (in correct order)
        accounts = [
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner_pubkey, is_signer=True, is_writable=True), # Often writable for rent payment
            AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=False), # Pass mint account
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=sysvar.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]

        # 4. Create the transaction and send using the client wrapper
        transaction = Transaction()
        _create_and_add_instruction(transaction, program_id_pubkey, *accounts, data=instruction_data)

        result = solana_client.send_transaction(transaction, owner_keypair)
        # Optional: Confirm transaction
        # solana_client.confirm_transaction(str(result.value))
        return str(result.value)

    except (ValueError, PDAError) as e:
        raise e # Re-raise specific validation/PDA errors
    except TransactionError as e:
         raise ICOInitializationError(f"Transaction failed during ICO initialization: {e}") from e
    except Exception as e:
        raise ICOInitializationError(f"Failed to initialize ICO: {e}") from e


def _get_token_mint_from_ico_state(solana_client: SolanaClient, ico_state_pda: Pubkey) -> Pubkey:
    """Helper to fetch and parse the token mint from the ICO state account."""
    try:
        ico_account_info: RpcResult[GetAccountInfoResp] = solana_client.get_account_info(ico_state_pda)
        if ico_account_info.value is None or ico_account_info.value.data is None:
            raise SolanaIcoError(f"ICO state account {ico_state_pda} not found or has no data.")

        account_data = ico_account_info.value.data
        # Adjust unpacking based on the *actual* structure of your ICO state account data
        # Example structure assumption (needs verification):
        # owner: Pubkey (32 bytes)
        # token_mint: Pubkey (32 bytes)
        # escrow_account: Pubkey (32 bytes)
        # total_supply: u64 (8 bytes)
        # tokens_sold: u64 (8 bytes)
        # base_price: u64 (8 bytes)
        # scaling_factor: u64 (8 bytes)
        # is_initialized: bool (1 byte)
        # Example unpack format (verify offsets and types):
        # unpacked_data = struct.unpack("<32s32s32sQQQQ?", account_data[:129]) # Example length
        # token_mint_bytes = unpacked_data[1] # Example index

        # --- Placeholder: Replace with actual unpacking logic ---
        # This is a critical part that depends entirely on your on-chain program's state struct.
        # For now, we raise an error indicating it needs implementation.
        # If the mint is *not* stored in the state, this function needs removal/rethinking.
        raise NotImplementedError("Parsing token mint from ICO state account data is not implemented. Verify account structure.")
        # token_mint_pubkey = Pubkey(token_mint_bytes)
        # return token_mint_pubkey
        # --- End Placeholder ---

    except struct.error as e:
        raise SolanaIcoError(f"Failed to unpack ICO state account data for {ico_state_pda}: {e}. Check account structure.") from e
    except SolanaIcoError as e:
        raise e
    except Exception as e:
        raise SolanaIcoError(f"Error fetching or parsing ICO state account {ico_state_pda}: {e}") from e


def buy_tokens(
    solana_client: SolanaClient,
    program_id_str: str,
    buyer_keypair: Keypair,
    amount_lamports: int,
    ico_owner_pubkey_str: str,
    token_mint_str: str # Added: Explicitly require token mint
) -> str:
    """
    Allows a user to buy tokens from the ICO.

    Args:
        solana_client: An instance of the SolanaClient.
        program_id_str: The program ID as a string.
        buyer_keypair: The keypair of the buyer.
        amount_lamports: The amount of SOL (in lamports) to spend.
        ico_owner_pubkey_str: The public key string of the ICO owner (needed for PDA derivation).
        token_mint_str: The SPL token mint address as a string.

    Returns:
        The transaction signature as a string.

    Raises:
        TokenPurchaseError: If the purchase fails.
        ValueError: If public key strings are invalid.
        PDAError: If PDA derivation fails.
        SolanaIcoError: If required accounts (like ICO state) are not found or invalid.
    """
    try:
        program_id_pubkey = Pubkey.from_string(program_id_str)
        buyer_pubkey = buyer_keypair.pubkey()
        ico_owner_pubkey = Pubkey.from_string(ico_owner_pubkey_str) # Owner key needed for PDAs
        token_mint_pubkey = Pubkey.from_string(token_mint_str) # Get mint from argument

        # 1. Find PDAs using owner key
        ico_state_pda, _ = find_ico_state_pda(ico_owner_pubkey, program_id_pubkey)
        escrow_pda, _ = find_escrow_pda(ico_owner_pubkey, program_id_pubkey)

        # 2. Get or Create Associated Token Account (ATA) for Buyer
        buyer_token_account = get_associated_token_address(buyer_pubkey, token_mint_pubkey)

        # Check if ATA exists, create if not
        ata_tx = Transaction()
        try:
            # Use get_account_info which raises if not found via the client wrapper
            solana_client.get_account_info(buyer_token_account)
        except SolanaIcoError: # Assuming get_account_info raises this or similar on not found
             print(f"Buyer ATA {buyer_token_account} not found. Creating...")
             create_assoc_instruction = create_associated_token_account(
                 payer=buyer_pubkey,
                 owner=buyer_pubkey,
                 mint=token_mint_pubkey,
             )
             ata_tx.add(create_assoc_instruction)

        # 4. Instruction data
        # Assuming instruction index 1 for BuyTokens
        instruction_data = struct.pack("<BQ", 1, amount_lamports)

        # 5. Create Accounts
        accounts = [
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=True), # Often writable to update tokens_sold
            AccountMeta(pubkey=buyer_pubkey, is_signer=True, is_writable=True),      # Pays SOL
            AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True),      # Receives SOL
            AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=True), # Mint needs to be writable for minting tokens
            AccountMeta(pubkey=buyer_token_account, is_signer=False, is_writable=True),  # Receives CTX
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False), # Token program needed for minting/transfer
            AccountMeta(pubkey=sysvar.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False), # Needed if creating ATA
        ]

        # 6. Create instruction and transaction
        buy_tx = Transaction()
        _create_and_add_instruction(buy_tx, program_id_pubkey, *accounts, data=instruction_data)

        # Combine ATA creation and buy transaction if needed
        final_tx = ata_tx.combine(buy_tx) if ata_tx.instructions else buy_tx

        result = solana_client.send_transaction(final_tx, buyer_keypair)
        # Optional: Confirm transaction
        # solana_client.confirm_transaction(str(result.value))
        return str(result.value)

    except (ValueError, PDAError, NotImplementedError, SolanaIcoError) as e:
        raise e # Re-raise specific validation/setup errors
    except TransactionError as e:
         raise TokenPurchaseError(f"Transaction failed during token purchase: {e}") from e
    except Exception as e:
        raise TokenPurchaseError(f"Failed to buy tokens: {e}") from e

def sell_tokens(
    solana_client: SolanaClient,
    program_id_str: str,
    seller_keypair: Keypair,
    amount_tokens: int,
    ico_owner_pubkey_str: str,
    token_mint_str: str # Added: Explicitly require token mint
) -> str:
    """
    Allows a user to sell tokens back to the ICO.

    Args:
        solana_client: An instance of the SolanaClient.
        program_id_str: The program ID as a string.
        seller_keypair: The keypair of the seller.
        amount_tokens: The amount of tokens to sell.
        ico_owner_pubkey_str: The public key string of the ICO owner (needed for PDA derivation).
        token_mint_str: The SPL token mint address as a string.

    Returns:
        The transaction signature as a string.

    Raises:
        TokenSaleError: If the sale fails.
        ValueError: If public key strings are invalid.
        PDAError: If PDA derivation fails.
        SolanaIcoError: If required accounts are not found or invalid.
    """
    try:
        program_id_pubkey = Pubkey.from_string(program_id_str)
        seller_pubkey = seller_keypair.pubkey()
        ico_owner_pubkey = Pubkey.from_string(ico_owner_pubkey_str) # Owner key needed for PDAs
        token_mint_pubkey = Pubkey.from_string(token_mint_str) # Get mint from argument

        # 1. Find PDAs using owner key
        ico_state_pda, _ = find_ico_state_pda(ico_owner_pubkey, program_id_pubkey)
        escrow_pda, _ = find_escrow_pda(ico_owner_pubkey, program_id_pubkey)

        # 2. Get Associated Token Account (ATA) for Seller
        seller_token_account = get_associated_token_address(seller_pubkey, token_mint_pubkey)
        # Ensure seller ATA exists (should exist if they bought tokens)
        try:
            solana_client.get_account_info(seller_token_account)
        except SolanaIcoError as e:
            raise TokenSaleError(f"Seller's token account {seller_token_account} not found.") from e


        # 4. Instruction data
        # Assuming instruction index 2 for SellTokens
        instruction_data = struct.pack("<BQ", 2, amount_tokens)

        # 5. Create Accounts
        accounts = [
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=True), # Writable to update tokens_sold
            AccountMeta(pubkey=seller_pubkey, is_signer=True, is_writable=True), # Receives SOL, signs transfer
            AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True), # Pays SOL
            AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=True), # Mint needs to be writable for burning tokens
            AccountMeta(pubkey=seller_token_account, is_signer=False, is_writable=True), # Sends CTX
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False), # Token program needed for burning/transfer
        ]

        # 6. Create instruction and transaction
        transaction = Transaction()
        _create_and_add_instruction(transaction, program_id_pubkey, *accounts, data=instruction_data)

        result = solana_client.send_transaction(transaction, seller_keypair)
        # Optional: Confirm transaction
        # solana_client.confirm_transaction(str(result.value))
        return str(result.value)

    except (ValueError, PDAError, NotImplementedError, SolanaIcoError) as e:
        raise e # Re-raise specific validation/setup errors
    except TransactionError as e:
         raise TokenSaleError(f"Transaction failed during token sale: {e}") from e
    except Exception as e:
        raise TokenSaleError(f"Failed to sell tokens: {e}") from e


def withdraw_from_escrow(solana_client: SolanaClient, program_id_str: str, owner_keypair: Keypair, amount_lamports: int) -> str:
    """
    Allows the ICO owner to withdraw SOL from the escrow account.

    Args:
        solana_client: An instance of the SolanaClient.
        program_id_str: The program ID as a string.
        owner_keypair: The keypair of the ICO owner.
        amount_lamports: The amount of SOL (in lamports) to withdraw.

    Returns:
        The transaction signature as a string.

    Raises:
        EscrowWithdrawalError: If the withdrawal fails.
        ValueError: If the program ID string is invalid.
        PDAError: If PDA derivation fails.
    """
    try:
        program_id_pubkey = Pubkey.from_string(program_id_str)
        owner_pubkey = owner_keypair.pubkey()

        # 1. Find PDAs
        ico_state_pda, _ = find_ico_state_pda(owner_pubkey, program_id_pubkey)
        escrow_pda, _ = find_escrow_pda(owner_pubkey, program_id_pubkey)

        # 2. Instruction data
        # Assuming instruction index 3 for WithdrawFromEscrow
        instruction_data = struct.pack("<BQ", 3, amount_lamports)

        # 3. Create Accounts
        accounts = [
           AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=False), # Readonly usually
           AccountMeta(pubkey=owner_pubkey, is_signer=True, is_writable=True), # Receives SOL
           AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True), # Pays SOL (needs authority via PDA)
           AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False)
        ]

        # 4. Create instruction and transaction
        transaction = Transaction()
        _create_and_add_instruction(transaction, program_id_pubkey, *accounts, data=instruction_data)

        result = solana_client.send_transaction(transaction, owner_keypair)
        # Optional: Confirm transaction
        # solana_client.confirm_transaction(str(result.value))
        return str(result.value)

    except (ValueError, PDAError) as e:
        raise e # Re-raise specific validation/PDA errors
    except TransactionError as e:
         raise EscrowWithdrawalError(f"Transaction failed during escrow withdrawal: {e}") from e
    except Exception as e:
        raise EscrowWithdrawalError(f"Failed to withdraw from escrow: {e}") from e