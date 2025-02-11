from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.publickey import Pubkey
from solana.instruction import Instruction, AccountMeta
from spl.token.instructions import (
    get_associated_token_address,
    create_associated_token_account,
    TOKEN_PROGRAM_ID
)
import struct
import os
import solana.sysvar.rent

SOLANA_CLUSTER_URL = os.environ.get("SOLANA_CLUSTER_URL", "http://localhost:8899")

# --- Helper Functions ---

def _create_and_add_instruction(transaction: Transaction, program_id: Pubkey, *accounts: AccountMeta, data: bytes = b''):
    """Creates an instruction and adds it to the transaction."""
    instruction = Instruction(
        program_id=program_id,
        accounts=list(accounts),
        data=data
    )
    transaction.add(instruction)

# --- Core Solana Interaction Functions ---

def connect_to_cluster(cluster_url: str = SOLANA_CLUSTER_URL) -> Client:
    """Connects to the Solana cluster."""
    return Client(cluster_url)

def load_keypair(keypair_path: str) -> Keypair:
    """Loads a keypair from a file."""
    with open(keypair_path, 'r') as f:
        secret_key = list(map(int, f.readline().strip().split(',')))
    return Keypair.from_secret_key(secret_key)

def get_balance(client: Client, public_key: str) -> int:
    """Gets the balance of a Solana account."""
    try:
        response = client.get_balance(public_key)
        return response['result']['value']
    except Exception as e:
        raise Exception(f"Failed to get balance: {e}")

def send_sol(client: Client, from_keypair: Keypair, to_public_key: str, amount: int) -> str:
    """Sends SOL from one account to another."""
    try:
        to_pubkey = Pubkey(to_public_key)  # Validate public key
        params = TransferParams(from_pubkey=from_keypair.pubkey(), to_pubkey=to_pubkey, lamports=amount)
        transfer_instruction = transfer(params)
        transaction = Transaction().add(transfer_instruction)
        result = client.send_transaction(transaction, from_keypair)  # Use send_transaction
        return result['result']
    except Exception as e:
        raise Exception(f"Failed to send SOL: {e}")

def initialize_ico(
    client: Client,
    program_id: str,
    owner_keypair: Keypair,
    token_mint_str: str,
    total_supply: int,
    base_price: int,
    scaling_factor: int,
) -> str:
    """Initializes the ICO state."""
    try:
        program_id_pubkey = Pubkey(program_id)
        token_mint_pubkey = Pubkey(token_mint_str)
        owner_pubkey = owner_keypair.pubkey()

        # 1. Find PDAs
        ico_state_pda, ico_bump = Pubkey.find_program_address([b"ico_state", bytes(owner_pubkey)], program_id_pubkey)
        escrow_pda, escrow_bump = Pubkey.find_program_address([b"escrow_account", bytes(owner_pubkey)], program_id_pubkey)

        # 2. Instruction data (using struct.pack for Borsh serialization)
        instruction_data = struct.pack(
            "<B32sQQQ",
            0,  # Instruction index for InitializeIco (adjust if needed)
            bytes(token_mint_pubkey),
            total_supply,
            base_price,
            scaling_factor
        )

        # 3. Create Accounts for the Instruction (in correct order)
        accounts = [
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=owner_pubkey, is_signer=True, is_writable=False),
            AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=solana.sysvar.rent.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]

        # 4. Create the instruction
        instruction = Instruction(
            program_id=program_id_pubkey,
            accounts=accounts,
            data=instruction_data
        )

        # 5. Create the transaction and sign
        transaction = Transaction().add(instruction)
        result = client.send_transaction(transaction, owner_keypair)  # Use send_transaction
        return result['result']

    except Exception as e:
        raise Exception(f"Failed to initialize ICO: {e}")

def buy_tokens(client: Client, program_id: str, buyer_keypair: Keypair, amount: int) -> str:
    """Allows a user to buy CTX tokens."""
    try:
        program_id_pubkey = Pubkey(program_id)
        buyer_pubkey = buyer_keypair.pubkey()

        # 1. Find PDAs and other account addresses
        ico_state_pda, _ = Pubkey.find_program_address([b"ico_state", bytes(buyer_pubkey)], program_id_pubkey)  # Replace with actual owner pubkey
        escrow_pda, _ = Pubkey.find_program_address([b"escrow_account", bytes(buyer_pubkey)], program_id_pubkey) # Replace with actual owner pubkey
        
        # Fetch the ICO State Account
        ico_account_data = client.get_account_info(ico_state_pda)

        # Get the token mint from the state data
        account_data = ico_account_data['result']['value']['data'][0]
        if account_data is None:
            raise Exception("ICO state account data is None")
        unpacked_data = struct.unpack("<B32s32sQQQQ32sB?", account_data.encode('base64'))
        token_mint_pubkey = Pubkey(unpacked_data[2]) # The token mint

        # 2. Get associated token account (create if it doesn't exist)
        buyer_token_account = get_associated_token_address(buyer_pubkey, token_mint_pubkey)
        
        #Check if the buyer token account is created, if not then create it
        try:
            client.get_account_info(buyer_token_account)
        except:
            create_assoc_instruction = create_associated_token_account(
            payer=buyer_pubkey,
            owner=buyer_pubkey,
            mint=token_mint_pubkey,
            )
            
            transaction = Transaction().add(create_assoc_instruction)
            client.send_transaction(transaction, buyer_keypair)

        # 3. Instruction data
        instruction_data = struct.pack("<BQ", 1, amount)  # Instruction index 1 for BuyTokens

        # 4. Create Accounts
        accounts = [
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=False),  # Readonly
            AccountMeta(pubkey=buyer_pubkey, is_signer=True, is_writable=True),      # Pays SOL
            AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=False),
            AccountMeta(pubkey=buyer_token_account, is_signer=False, is_writable=True),  # Receives CTX
            AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True),      # Escrow
            AccountMeta(pubkey=solana.system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=solana.sysvar.rent.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]
    
        # 5. Create instruction and transaction
        instruction = Instruction(
            program_id=program_id_pubkey,
            accounts=accounts,
            data=instruction_data
        )
        transaction = Transaction().add(instruction)
        result = client.send_transaction(transaction, buyer_keypair)  # Use send_transaction
        return result['result']

    except Exception as e:
        raise Exception(f"Failed to buy tokens: {e}")
    
def sell_tokens(client: Client, program_id: str, seller_keypair: Keypair, amount: int) -> str:
    """Allows a user to sell CTX tokens."""
    try:
        program_id_pubkey = Pubkey(program_id)
        seller_pubkey = seller_keypair.pubkey()

        # 1. Find PDAs and other account addresses
        ico_state_pda, _ = Pubkey.find_program_address([b"ico_state", bytes(seller_pubkey)], program_id_pubkey) # Replace with actual owner pubkey
        escrow_pda, _ = Pubkey.find_program_address([b"escrow_account", bytes(seller_pubkey)], program_id_pubkey)  # Replace with actual owner pubkey

        # Fetch the ICO State Account
        ico_account_data = client.get_account_info(ico_state_pda)
        if ico_account_data['result']['value'] is None:
            raise Exception("ICO state account not found")

        # Get the token mint from the state data
        account_data = ico_account_data['result']['value']['data'][0]
        if account_data is None:
            raise Exception("ICO state account data is None")
        unpacked_data = struct.unpack("<B32s32sQQQQ32sB?", account_data.encode('base64'))
        token_mint_pubkey = Pubkey(unpacked_data[2]) # The token mint

        # 2. Get associated token account
        seller_token_account = get_associated_token_address(seller_pubkey, token_mint_pubkey)
        
        # 3.  Instruction data
        instruction_data = struct.pack("<BQ", 2, amount)
        
        # 4.  Create Accounts
        accounts = [
            AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=seller_pubkey, is_signer=True, is_writable=True),
            AccountMeta(pubkey=token_mint_pubkey, is_signer=False, is_writable=False),
            AccountMeta(pubkey=seller_token_account, is_signer=False, is_writable=True),
            AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=solana.system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=solana.sysvar.rent.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False)
        ]

        # 5. Create instruction and transaction
        instruction = Instruction(
            program_id=program_id_pubkey,
            accounts=accounts,
            data=instruction_data
        )
        transaction = Transaction().add(instruction)
        result = client.send_transaction(transaction, seller_keypair)  # Use send_transaction
        return result['result']
    
    except Exception as e:
        raise Exception(f"Failed to sell tokens: {e}")

def withdraw_from_escrow(client: Client, program_id: str, owner_keypair: Keypair, amount: int) -> str:
    """Allows the owner to withdraw SOL from the escrow."""
    try:
        program_id_pubkey = Pubkey(program_id)
        owner_pubkey = owner_keypair.pubkey()

        # 1. Find PDAs
        ico_state_pda, _ = Pubkey.find_program_address([b"ico_state", bytes(owner_pubkey)], program_id_pubkey)
        escrow_pda, _ = Pubkey.find_program_address([b"escrow_account", bytes(owner_pubkey)], program_id_pubkey)

        # 2. Instruction data
        instruction_data = struct.pack("<BQ", 3, amount) # Instruction index 3 for WithdrawFromEscrow

        # 3. Create Accounts
        accounts = [
           AccountMeta(pubkey=ico_state_pda, is_signer=False, is_writable=False),
           AccountMeta(pubkey=owner_pubkey, is_signer=True, is_writable=True),
           AccountMeta(pubkey=escrow_pda, is_signer=False, is_writable=True),
           AccountMeta(pubkey=solana.system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False)
        ]

        # 4. Create instruction and transaction
        instruction = Instruction(
            program_id=program_id_pubkey,
            accounts=accounts,
            data=instruction_data
        )
        transaction = Transaction().add(instruction)
        result = client.send_transaction(transaction, owner_keypair)  # Use send_transaction and owner keypair
        return result['result']

    except Exception as e:
        raise Exception(f"Failed to withdraw from escrow: {e}")

def create_resource_access(client: Client, program_id: str, server_keypair: Keypair, resource_id: str, access_fee: int) -> str:
    """Creates or updates resource access information."""
    try:
        program_id_pubkey = Pubkey(program_id)
        server_pubkey = server_keypair.pubkey()

        # 1. Find PDA
        resource_state_pda, _ = Pubkey.find_program_address([b"resource_state", bytes(server_pubkey)], program_id_pubkey) # Replace with actual server pubkey

        # 2. Instruction data
        resource_id_bytes = resource_id.encode('utf-8')
        instruction_data = struct.pack(f"<B{len(resource_id_bytes)}sQ", 4, resource_id_bytes, access_fee)  # Instruction 4

        # 3. Accounts
        accounts = [
            AccountMeta(pubkey=resource_state_pda, is_signer=False, is_writable=True),
            AccountMeta(pubkey=server_pubkey, is_signer=True, is_writable=False),
            AccountMeta(pubkey=solana.sysvar.rent.SYSVAR_RENT_PUBKEY, is_signer=False, is_writable=False),
        ]

        # 4. Create instruction and transaction
        instruction = Instruction(program_id_pubkey, accounts, instruction_data)
        transaction = Transaction().add(instruction)
        result = client.send_transaction(transaction, server_keypair)  # Use send_transaction
        return result['result']

    except Exception as e:
        raise Exception(f"Failed to create resource access: {e}")
    
def access_resource(client: Client, program_id: str, user_keypair: Keypair, resource_id: str, amount: int) -> str:
    """Pays to access a registered resource."""
    try:
        program_id_pubkey = Pubkey(program_id)
        user_pubkey = user_keypair.pubkey()

        # 1. Find PDA.  We need the *server's* key, not the user's
        #resource_state_pda, _ = Pubkey.find_program_address([b"resource_state", bytes(user_pubkey)], program_id_pubkey)  # This is wrong, needs to be server's key
        # Fetch the Resource State Account
        #resource_account_data = client.get_account_info(resource_state_pda)

        # Get the server address from the state data
        #unpacked_data = struct.unpack(f"<{len(resource_id)}s32sQB?", resource_account_data['result']['value']['data'][0].encode('base64'))
        #server_pubkey = Pubkey(unpacked_data[1]) # The server pubkey
        
        # Correct PDA derivation:  The resource_state PDA is derived using the server's key, not the user's.  We need the resource ID to look it up.
        # This requires a change:  We need to store the server's key *and* the resource ID in the resource_state account to look it up correctly.  For now, this won't work correctly without knowing the server's key.

        # 2. Instruction data
        resource_id_bytes = resource_id.encode('utf-8')
        instruction_data = struct.pack(f"<B{len(resource_id_bytes)}sQ", 5, resource_id_bytes, amount)  # Instruction 5

        # 3. Accounts
        #accounts = [
        #    AccountMeta(pubkey=resource_state_pda, is_signer=False, is_writable=False),  # Readonly
        #    AccountMeta(pubkey=user_pubkey, is_signer=True, is_writable=True),          # Pays
        #    AccountMeta(pubkey=server_pubkey, is_signer=False, is_writable=True),        # Receives payment
        #    AccountMeta(pubkey=solana.system_program.SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        #]
        raise Exception("access_resource not fully implemented due to server key retrieval issue.  Needs resource_state_pda derivation with server key.")

        # 4. Create instruction and transaction
        #instruction = Instruction(program_id_pubkey, accounts, instruction_data)
        #transaction = Transaction().add(instruction)
        #result = client.send_transaction(transaction, user_keypair)  # Use send_transaction
        #return result['result']

    except Exception as e:
        raise Exception(f"Failed to access resource: {e}")