from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.pubkey import Pubkey
from solana.instruction import Instruction
import struct

SOLANA_CLUSTER_URL = "http://localhost:8899"  # Default local cluster URL

def create_keypair():
    """Creates a new Solana keypair."""
    return Keypair()

def get_balance(public_key: str):
    """Gets the balance of a Solana account."""
    solana_client = Client(SOLANA_CLUSTER_URL)
    return solana_client.get_balance(public_key).value

def send_sol(from_keypair: Keypair, to_public_key: str, amount: int):
    """Sends SOL from one account to another."""
    solana_client = Client(SOLANA_CLUSTER_URL)
    params = TransferParams(
        from_pubkey=from_keypair.pubkey(),
        to_pubkey=to_public_key,
        lamports=amount
    )
    transfer_instruction = transfer(params)
    transaction = Transaction().add(transfer_instruction)
    transaction.sign(from_keypair)
    result = solana_client.send_raw_transaction(transaction.serialize())
    return result

def initialize_ico(
    program_id: str,
    keypair_path: str,
    token_mint: str,
    total_supply: int,
    base_price: int,
    scaling_factor: int,
):
    """Initializes the ICO state."""
    solana_client = Client(SOLANA_CLUSTER_URL)
    keypair = Keypair.from_seed(bytes([1]*32)) # Placeholder, replace with actual keypair loading
    program_id_pubkey = Pubkey(program_id)
    
    # 1.  Create instruction data
    instruction_data = struct.pack("<B32sQQQ", 0, bytes.fromhex(token_mint), total_supply, base_price, scaling_factor) # Assuming instruction 0 is InitializeIco

    # 2.  Create accounts
    ico_state_pda, ico_bump = Pubkey.find_program_address(
        [b"ico_state", bytes(keypair.pubkey())], program_id_pubkey
    )
    
    # 3.  Create instruction
    instruction = Instruction(
        program_id=program_id_pubkey,
        accounts=[
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=keypair.pubkey(), is_signer=True, is_writable=False),
            AccountMeta(pubkey=solana.sysvar.rent.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ],
        data=instruction_data,
    )

    # 4.  Create transaction
    transaction = Transaction().add(instruction)
    transaction.sign(keypair)

    # 5.  Send transaction
    result = solana_client.send_raw_transaction(transaction.serialize())
    return result