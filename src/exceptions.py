"""Custom exceptions for the Solana ICO CLI application."""

class SolanaIcoError(Exception):
    """Base exception for errors in this application."""
    pass

class ConfigurationError(SolanaIcoError):
    """Exception raised for configuration-related errors."""
    pass

class SolanaConnectionError(SolanaIcoError):
    """Exception raised for errors connecting to the Solana cluster."""
    pass

class KeypairError(SolanaIcoError):
    """Exception raised for errors loading or handling keypairs."""
    pass

class TransactionError(SolanaIcoError):
    """Exception raised for errors during transaction creation or sending."""
    pass

class ICOError(SolanaIcoError):
    """Base exception for ICO-related errors."""
    pass

class ICOInitializationError(ICOError):
    """Exception raised for errors during ICO initialization."""
    pass

class TokenPurchaseError(ICOError):
    """Exception raised for errors during token purchase."""
    pass

class TokenSaleError(ICOError):
    """Exception raised for errors during token sale."""
    pass

class EscrowWithdrawalError(ICOError):
    """Exception raised for errors during escrow withdrawal."""
    pass

class ResourceError(SolanaIcoError):
    """Base exception for resource access-related errors."""
    pass

class ResourceCreationError(ResourceError):
    """Exception raised for errors during resource access creation."""
    pass

class ResourceAccessError(ResourceError):
    """Exception raised for errors during resource access payment."""
    pass

class PDAError(SolanaIcoError):
    """Exception raised for errors related to Program Derived Addresses."""
    pass