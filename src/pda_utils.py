"""Utilities for deriving Program Derived Addresses (PDAs)."""

from solders.pubkey import Pubkey # Corrected import
from .exceptions import PDAError

def find_ico_state_pda(owner_pubkey: Pubkey, program_id: Pubkey) -> tuple[Pubkey, int]:
    """
    Finds the Program Derived Address (PDA) for the ICO state account.

    Args:
        owner_pubkey: The public key of the ICO owner.
        program_id: The public key of the Solana program.

    Returns:
        A tuple containing the PDA public key and the bump seed.

    Raises:
        PDAError: If the PDA derivation fails.
    """
    try:
        pda, bump = Pubkey.find_program_address(
            [b"ico_state", bytes(owner_pubkey)],
            program_id
        )
        return pda, bump
    except Exception as e:
        raise PDAError(f"Failed to find ICO state PDA: {e}") from e

def find_escrow_pda(owner_pubkey: Pubkey, program_id: Pubkey) -> tuple[Pubkey, int]:
    """
    Finds the Program Derived Address (PDA) for the escrow account.

    Args:
        owner_pubkey: The public key of the ICO owner.
        program_id: The public key of the Solana program.

    Returns:
        A tuple containing the PDA public key and the bump seed.

    Raises:
        PDAError: If the PDA derivation fails.
    """
    try:
        pda, bump = Pubkey.find_program_address(
            [b"escrow_account", bytes(owner_pubkey)],
            program_id
        )
        return pda, bump
    except Exception as e:
        raise PDAError(f"Failed to find escrow PDA: {e}") from e

def find_resource_state_pda(server_pubkey: Pubkey, resource_id: str, program_id: Pubkey) -> tuple[Pubkey, int]:
    """
    Finds the Program Derived Address (PDA) for the resource state account.
    NOTE: The seeds used here might need adjustment based on the actual
    on-chain program's implementation for resource state derivation.
    This assumes derivation based on server key and resource ID.

    Args:
        server_pubkey: The public key of the server managing the resource.
        resource_id: The unique identifier string for the resource.
        program_id: The public key of the Solana program.

    Returns:
        A tuple containing the PDA public key and the bump seed.

    Raises:
        PDAError: If the PDA derivation fails.
    """
    try:
        # Assuming seeds are "resource_state", server pubkey, and resource_id bytes
        # Verify this matches the on-chain program logic!
        resource_id_bytes = resource_id.encode('utf-8')
        pda, bump = Pubkey.find_program_address(
            [b"resource_state", bytes(server_pubkey), resource_id_bytes],
            program_id
        )
        return pda, bump
    except Exception as e:
        raise PDAError(f"Failed to find resource state PDA for resource '{resource_id}': {e}") from e