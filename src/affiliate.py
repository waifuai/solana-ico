import os
import asyncio
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional, Union, Protocol, Dict
from abc import ABC, abstractmethod

from solana.rpc.async_api import AsyncClient
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import transfer as system_transfer
from solders.rpc.responses import SendTransactionResp
from spl.token.async_client import AsyncToken
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import mint_to, transfer, burn

class ClusterType(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"
    LOCALHOST = "localhost"

@dataclass
class BondingCurveConfig:
    base_price: Decimal  # in lamports
    slope: Decimal
    total_supply: int

    @classmethod
    def default(cls) -> "BondingCurveConfig":
        return cls(
            base_price=Decimal("1e4"),
            slope=Decimal("1e6"),
            total_supply=int(1e18)
        )

class TokenSaleError(Exception):
    """Base exception for token sale errors"""
    pass

class InsufficientTokensError(TokenSaleError):
    """Raised when there aren't enough tokens available"""
    pass

class InvalidAmountError(TokenSaleError):
    """Raised when the amount is invalid (e.g., <= 0)"""
    pass

class SolanaClientFactory:
    """Factory for creating Solana clients"""
    
    _CLUSTER_URLS = {
        ClusterType.MAINNET: "https://api.mainnet-beta.solana.com",
        ClusterType.TESTNET: "https://api.testnet.solana.com",
        ClusterType.DEVNET: "https://api.devnet.solana.com",
        ClusterType.LOCALHOST: "http://localhost:8899"
    }

    @classmethod
    def create_client(cls, cluster: Union[ClusterType, str]) -> Union[Client, AsyncClient]:
        """Creates a Solana client based on the cluster type"""
        if isinstance(cluster, str):
            cluster = ClusterType(cluster.lower())
        
        base_url = cls._CLUSTER_URLS.get(cluster, cls._CLUSTER_URLS[ClusterType.DEVNET])
        return AsyncClient(base_url) if asyncio.get_event_loop().is_running() else Client(base_url)

class TokenInterface(Protocol):
    """Protocol defining the interface for token operations"""
    
    @abstractmethod
    async def mint(self, amount: int, destination: Pubkey, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        pass
    
    @abstractmethod
    async def burn(self, amount: int, source: Keypair, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        pass
    
    @abstractmethod
    async def transfer(self, amount: int, source: Keypair, destination: Pubkey, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        pass

class SplToken(TokenInterface):
    """Implementation of TokenInterface for SPL tokens"""
    
    def __init__(
        self,
        mint: Pubkey,
        owner: Keypair,
        payer: Keypair,
        program_id: Pubkey = TOKEN_PROGRAM_ID,
        cluster: Union[ClusterType, str] = ClusterType.DEVNET
    ):
        self.mint = mint
        self.owner = owner
        self.payer = payer
        self.program_id = program_id
        client = SolanaClientFactory.create_client(cluster)
        self.token_client = AsyncToken(client, mint, program_id, payer) if isinstance(client, AsyncClient) else Token(client, mint, program_id, payer)

    async def mint(self, amount: int, destination: Pubkey, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        mint_ix = mint_to(
            mint=self.mint,
            dest=destination,
            mint_authority=self.owner.pubkey(),
            amount=amount,
            program_id=self.program_id
        )
        tx = Transaction().add(mint_ix)
        return await self.token_client.client.send_transaction(
            tx, self.owner, self.payer, opts=TxOpts(preflight_commitment=commitment)
        )

    async def burn(self, amount: int, source: Keypair, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        burn_ix = burn(
            mint=self.mint,
            account=source.pubkey(),
            owner=source.pubkey(),
            amount=amount,
            program_id=self.program_id
        )
        tx = Transaction().add(burn_ix)
        return await self.token_client.client.send_transaction(
            tx, source, opts=TxOpts(preflight_commitment=commitment)
        )

    async def transfer(self, amount: int, source: Keypair, destination: Pubkey, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        transfer_ix = transfer(
            source=source.pubkey(),
            dest=destination,
            owner=source.pubkey(),
            amount=amount,
            program_id=self.program_id
        )
        tx = Transaction().add(transfer_ix)
        return await self.token_client.client.send_transaction(
            tx, source, opts=TxOpts(preflight_commitment=commitment)
        )

class TokenSale:
    """Manages token sales using a bonding curve pricing model with a commission system"""

    def __init__(
        self,
        token: TokenInterface,
        owner: Keypair,
        token_account: Pubkey,
        config: Optional[BondingCurveConfig] = None,
        commission_rate: Decimal = Decimal("0.1")  # 10% commission
    ):
        self.token = token
        self.owner = owner
        self.token_account = token_account
        self.config = config or BondingCurveConfig.default()
        self.total_raised = Decimal(0)
        self.total_tokens_sold = 0
        self.commission_rate = commission_rate
        self.referrers: Dict[Pubkey, Pubkey] = {}  # {buyer: referrer}

    def _calculate_token_price(self, current_supply: int) -> Decimal:
        """Calculates token price based on current supply using bonding curve"""
        return self.config.base_price * (1 + (Decimal(current_supply) / self.config.slope))

    async def buy_tokens(
        self, 
        amount: int, 
        buyer: Pubkey, 
        referrer: Optional[Pubkey] = None,
        commitment: Optional[Commitment] = None
    ) -> SendTransactionResp:
        """Purchase tokens at the current bonding curve price with optional referrer for commission"""
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than 0")

        token_price = self._calculate_token_price(self.total_tokens_sold)
        tokens_to_buy = int(amount / token_price)

        if tokens_to_buy + self.total_tokens_sold > self.config.total_supply:
            raise InsufficientTokensError("Not enough tokens available for sale")

        self.total_tokens_sold += tokens_to_buy
        self.total_raised += Decimal(amount)

        if referrer:
            self.referrers[buyer] = referrer
            commission = Decimal(amount) * self.commission_rate
            await self.token.transfer(int(commission), self.token_account, referrer, commitment)  # Pay commission
            self.total_raised -= commission

        return await self.token.mint(tokens_to_buy, buyer, commitment)

    async def sell_tokens(
        self, 
        tokens_to_sell: int, 
        seller: Keypair, 
        commitment: Optional[Commitment] = None
    ) -> SendTransactionResp:
        """Sell tokens back to the contract at the current bonding curve price"""
        if tokens_to_sell <= 0:
            raise InvalidAmountError("Amount must be greater than 0")

        if self.total_tokens_sold < tokens_to_sell:
            raise InsufficientTokensError("Not enough tokens in circulation")

        token_price = self._calculate_token_price(self.total_tokens_sold - tokens_to_sell)
        amount_to_return = Decimal(tokens_to_sell) * token_price

        self.total_tokens_sold -= tokens_to_sell
        self.total_raised -= amount_to_return

        return await self.token.burn(tokens_to_sell, seller, commitment)

    async def withdraw(self, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        """Withdraw accumulated funds to the owner's account"""
        tx = Transaction().add(
            system_transfer(
                from_pubkey=self.token_account,
                to_pubkey=self.owner.pubkey(),
                lamports=int(self.total_raised)
            )
        )
        return await self.token.token_client.client.send_transaction(
            tx, self.owner, opts=TxOpts(preflight_commitment=commitment)
        )

class TokenSaleProxy:
    """Proxy pattern implementation for TokenSale to allow runtime updates and logging"""
    
    def __init__(self, implementation: TokenSale):
        self._implementation = implementation

    def set_implementation(self, new_implementation: TokenSale) -> None:
        """Update the implementation at runtime"""
        self._implementation = new_implementation

    async def buy_tokens(
        self, 
        amount: int, 
        buyer: Pubkey, 
        referrer: Optional[Pubkey] = None,
        commitment: Optional[Commitment] = None
    ) -> SendTransactionResp:
        print(f"Buying {amount} tokens for {buyer} with referrer {referrer}")
        return await self._implementation.buy_tokens(amount, buyer, referrer, commitment)

    async def sell_tokens(
        self, 
        amount: int, 
        seller: Keypair, 
        commitment: Optional[Commitment] = None
    ) -> SendTransactionResp:
        print(f"Selling {amount} tokens from {seller.pubkey()}")
        return await self._implementation.sell_tokens(amount, seller, commitment)

    async def withdraw(self, commitment: Optional[Commitment] = None) -> SendTransactionResp:
        print(f"Withdrawing {self._implementation.total_raised} lamports")
        return await self._implementation.withdraw(commitment)

async def setup_affiliate_ico(cluster: str = os.environ.get('CLUSTER', ClusterType.DEVNET)):
    # Example usage
    # cluster = os.environ.get('CLUSTER', ClusterType.DEVNET)
    
    # Initialize keys (replace with actual keys in production)
    owner_keypair = Keypair.from_secret_key(bytes([1] * 32))
    token_mint = Pubkey.default()
    token_account = Pubkey.default()
    payer = Keypair()

    # Initialize token and sale
    token = SplToken(token_mint, owner_keypair, payer, cluster=cluster)
    config = BondingCurveConfig.default()
    
    token_sale = TokenSale(token, owner_keypair, token_account, config)
    token_sale_proxy = TokenSaleProxy(token_sale)

    return token_sale_proxy, owner_keypair, payer

async def run_example_transactions(token_sale_proxy: TokenSaleProxy):
    # Example transactions
    buyer = Keypair().pubkey()
    referrer = Keypair().pubkey()
    seller = Keypair()
    
    try:
        await token_sale_proxy.buy_tokens(100, buyer, referrer)
        await token_sale_proxy.sell_tokens(50, seller)
        await token_sale_proxy.withdraw()
    except TokenSaleError as e:
        print(f"Token sale error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
