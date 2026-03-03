import sys
import logging
from src.services.vault_initializer import VaultInitializer
from src.config.settings import Config

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def main():
    """Initializes the vault from the command line."""
    print("--- Bronze Vault Initialization ---")
    
    # Enable live execution by overriding dry_run to False for setup
    initializer = VaultInitializer(dry_run=False)
    
    try:
        Config.validate()
        result = initializer.perform()
        print(f"\nResult: {result['status'].upper()} - {result['message']}")
    except Exception as e:
        print(f"\nError initializing vault: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
