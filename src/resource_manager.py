"""Manages resource access interactions on the Solana blockchain."""

import struct
from typing import List

from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction, AccountMeta
import solders.system_program as system_program
import solders.sysvar as sysvar

# Use relative imports within the 'src' directory
from .solana_client import SolanaClient
from .pda_utils import find_resource_state_pda
from .exceptions import (
    ResourceCreationError,
    ResourceAccessError,
    TransactionError,
    PDAError,
)

# Constants
INSTRUCTION_INDEX_CREATE_RESOURCE = 4
INSTRUCTION_INDEX_ACCESS_RESOURCE = 5

# Helper to create and add instruction (consider moving to a shared utils if used elsewhere)
def _create_and_add_instruction(transaction: Transaction, program_id: Pubkey, *accounts: AccountMeta, data: bytes = b''):
    """Creates an instruction and adds it to the transaction."""
    instruction = Instruction(
        program_id=program_id,
        accounts=list(accounts),
        data=data
    )
    transaction.add(instruction)


def create_resource_access(
    solana_client: SolanaClient,
    program_id_str: str,
    server_keypair: Keypair,
    resource_id: str,
    access_fee: int
) -> str:
    """
    Creates or updates resource access information on the Solana blockchain.

    Args:
        solana_client: An instance of the SolanaClient.
        program_id_str: The program ID as a string.
        server_keypair: The keypair of the server managing the resource.
        resource_id: A unique identifier string for the resource.
        access_fee: The access fee in lamports.

    Returns:
        The transaction signature as a string.

    Raises:
        ResourceCreationError: If the creation/update fails.
        ValueError: If the program ID string is invalid.
        PDAError: If PDA derivation fails (check seed assumptions in pda_utils).
    """
    try:
        program_id_pubkey = Pubkey.from_string(program_id_str)
        server_pubkey = server_keypair.pubkey()

        # 1. Find PDA for the resource state.
        # Note: Assumes seeds are "resource_state", server pubkey, resource_id bytes.
        # Verify this matches the on-chain program logic in pda_utils.py!
        resource_state_pda, _ = find_resource_state_pda(server_pubkey, resource_id, program_id_pubkey)

        # 2. Instruction data
        resource_id_bytes = resource_id.encode('utf-8')
        # Pack format depends on how program expects resource_id (fixed size buffer or length-prefixed?)
        # Assuming length-prefixed string for flexibility:
        # instruction_data = struct.pack(f"<BI{len(resource_id_bytes)}sQ", INSTRUCTION_INDEX_CREATE_RESOURCE, len(resource_id_bytes), resource_id_bytes, access_fee)
        # If fixed size (e.g., 32 bytes), pad/truncate and use:
        # padded_resource_id = resource_id_bytes.ljust(32, b'\0')[:32]
        # instruction_data = struct.pack("<B32sQ", INSTRUCTION_INDEX_CREATE_RESOURCE, padded_resource_id, access_fee)
        # Using a simple variable length packing for now, adjust as needed:
        instruction_data = struct.pack(f"<B{len(resource_id_bytes)}sQ", INSTRUCTION_INDEX_CREATE_RESOURCE, resource_id_bytes, access_fee) # Simple packing, verify program needs

        # 3. Accounts
        accounts = [
            AccountMeta(pubkey=resource_state_pda, is_signer=False, is_writable=True), # Account to create/update
            AccountMeta(pubkey=server_pubkey, is_signer=True, is_writable=True), # Payer for rent, signer
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=sysvar.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False), # Needed for account creation rent
        ]

        # 4. Create instruction and transaction
        transaction = Transaction()
        _create_and_add_instruction(transaction, program_id_pubkey, *accounts, data=instruction_data)

        result = solana_client.send_transaction(transaction, server_keypair)
        # Optional: Confirm transaction
        # solana_client.confirm_transaction(str(result.value))
        return str(result.value)

    except (ValueError, PDAError) as e:
        raise e # Re-raise specific validation/PDA errors
    except TransactionError as e:
         raise ResourceCreationError(f"Transaction failed during resource access creation for '{resource_id}': {e}") from e
    except Exception as e:
        raise ResourceCreationError(f"Failed to create resource access for '{resource_id}': {e}") from e


def access_resource(
    solana_client: SolanaClient,
    program_id_str: str,
    user_keypair: Keypair,
    resource_id: str,
    server_pubkey_str: str, # Added: Server pubkey needed for PDA derivation
    amount_lamports: int
) -> str:
    """
    Pays to access a registered resource.

    Args:
        solana_client: An instance of the SolanaClient.
        program_id_str: The program ID as a string.
        user_keypair: The keypair of the user accessing the resource.
        resource_id: The unique identifier string for the resource being accessed.
        server_pubkey_str: The public key string of the server managing the resource.
        amount_lamports: The amount of SOL (in lamports) to pay (should match fee).

    Returns:
        The transaction signature as a string.

    Raises:
        ResourceAccessError: If the access payment fails.
        ValueError: If public key strings are invalid.
        PDAError: If PDA derivation fails (check seed assumptions in pda_utils).
    """
    try:
        program_id_pubkey = Pubkey.from_string(program_id_str)
        user_pubkey = user_keypair.pubkey()
        server_pubkey = Pubkey.from_string(server_pubkey_str) # Convert server pubkey string

        # 1. Find PDA for the resource state using the server's key.
        # Note: Assumes seeds are "resource_state", server pubkey, resource_id bytes.
        # Verify this matches the on-chain program logic in pda_utils.py!
        resource_state_pda, _ = find_resource_state_pda(server_pubkey, resource_id, program_id_pubkey)

        # 2. Instruction data
        resource_id_bytes = resource_id.encode('utf-8')
        # Adjust packing based on program requirements (see create_resource_access notes)
        instruction_data = struct.pack(f"<B{len(resource_id_bytes)}sQ", INSTRUCTION_INDEX_ACCESS_RESOURCE, resource_id_bytes, amount_lamports) # Simple packing, verify program needs

        # 3. Accounts
        accounts = [
            AccountMeta(pubkey=resource_state_pda, is_signer=False, is_writable=False), # Readonly, to check fee etc.
            AccountMeta(pubkey=user_pubkey, is_signer=True, is_writable=True),          # Payer
            AccountMeta(pubkey=server_pubkey, is_signer=False, is_writable=True),        # Recipient of payment
            AccountMeta(pubkey=system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        ]

        # 4. Create instruction and transaction
        transaction = Transaction()
        _create_and_add_instruction(transaction, program_id_pubkey, *accounts, data=instruction_data)

        result = solana_client.send_transaction(transaction, user_keypair)
        # Optional: Confirm transaction
        # solana_client.confirm_transaction(str(result.value))
        return str(result.value)

    except (ValueError, PDAError) as e:
        raise e # Re-raise specific validation/PDA errors
    except TransactionError as e:
         raise ResourceAccessError(f"Transaction failed during resource access for '{resource_id}': {e}") from e
    except Exception as e:
        raise ResourceAccessError(f"Failed to access resource '{resource_id}': {e}") from e