import pytest
import shutil
from pathlib import Path
from src.services.vault_initializer import VaultInitializer
from src.config.settings import Config

@pytest.fixture
def temp_vault(tmp_path, monkeypatch):
    """Sets up a temporary vault root for testing."""
    vault_root = tmp_path / "AI_Employee_Vault"
    monkeypatch.setattr(Config, "VAULT_ROOT", vault_root)
    yield vault_root
    if vault_root.exists():
        shutil.rmtree(vault_root)

def test_vault_initializer_full_setup(temp_vault):
    """Verifies that the initializer creates all folders and seed files."""
    initializer = VaultInitializer(dry_run=False)
    result = initializer.perform()
    
    assert result["status"] == "success"
    assert temp_vault.exists()
    
    # 1. Check folders
    for folder in VaultInitializer.FOLDERS:
        assert (temp_vault / folder).is_dir(), f"Folder missing: {folder}"
        
    # 2. Check seed files
    for seed_file in VaultInitializer.SEED_FILES.keys():
        assert (temp_vault / seed_file).is_file(), f"Seed file missing: {seed_file}"
        
def test_vault_initializer_dry_run(temp_vault):
    """Verifies that dry_run=True doesn't create any files."""
    initializer = VaultInitializer(dry_run=True)
    result = initializer.perform()
    
    assert result["status"] == "dry_run"
    assert not temp_vault.exists()
