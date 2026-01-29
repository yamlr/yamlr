#!/usr/bin/env python3
"""
VERIFY CONFIGURATION SYSTEM
---------------------------
Tests the new Foundation Layer:
1. Loading .akeso.yaml
2. Ignoring files based on glob patterns
3. Overriding health thresholds
"""
import sys
import shutil
import logging
from pathlib import Path
from kubecuro.core.config import ConfigManager
from kubecuro.core.engine import AkesoEngine

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_config")

TEST_ROOT = Path("tests/config_test_env")

def setup_env():
    if TEST_ROOT.exists(): shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir(parents=True)
    
    # create dummy files
    (TEST_ROOT / "valid.yaml").write_text("kind: Service\nmetadata:\n  name: valid", encoding='utf-8')
    (TEST_ROOT / "ignore_me.yaml").write_text("kind: Service\nmetadata:\n  name: ignore", encoding='utf-8')
    (TEST_ROOT / "deep").mkdir()
    (TEST_ROOT / "deep" / "skip.yaml").write_text("kind: Service", encoding='utf-8')

def test_default_config():
    logger.info("TEST 1: Default Configuration")
    config = ConfigManager(TEST_ROOT)
    assert config.health_threshold == 70, f"Default threshold match failed: {config.health_threshold}"
    assert not config.is_ignored("valid.yaml"), "Should not ignore valid file by default"
    logger.info("✅ Default config passed")

def test_custom_config():
    logger.info("TEST 2: Custom .akeso.yaml")
    
    config_content = """
rules:
  threshold: 85
  ignore:
    - "ignore_me.yaml"
    - "deep/*"
"""
    (TEST_ROOT / ".akeso.yaml").write_text(config_content, encoding='utf-8')
    
    # Reload Config
    config = ConfigManager(TEST_ROOT)
    
    # Check Threshold
    assert config.health_threshold == 85, f"Custom threshold failed: {config.health_threshold}"
    
    # Check Ignores
    assert config.is_ignored("ignore_me.yaml"), "Failed to ignore explicit file"
    assert config.is_ignored("deep/skip.yaml"), "Failed to ignore exact glob match"
    assert not config.is_ignored("valid.yaml"), "Incorrectly ignored valid file"
    
    logger.info("✅ Custom config passed")

def test_engine_integration():
    logger.info("TEST 3: Engine Integration")
    
    # Engine should pick up the .akeso.yaml we created in TEST 2
    # We use a dummy catalog path because we don't want to load real heavy schemas for this unit test
    # But Engine constructor forces load, so we point to the distilled one we know exists
    
    catalog_path = "catalog/k8s_v1_distilled.json"
    engine = AkesoEngine(str(TEST_ROOT), catalog_path)
    
    # Audit "ignore_me.yaml" -> Should be IGNORED
    res = engine.audit_and_heal_file("ignore_me.yaml")
    assert res['status'] == "IGNORED", f"Engine failed to ignore file. Status: {res['status']}"
    
    # Audit "valid.yaml" -> Should NOT be ignored
    res = engine.audit_and_heal_file("valid.yaml")
    assert res['status'] != "IGNORED", "Engine incorrectly ignored valid file"
    
    logger.info("✅ Engine integration passed")

if __name__ == "__main__":
    try:
        setup_env()
        test_default_config()
        test_custom_config()
        test_engine_integration()
        print("\n🚀 CONFIG SYSTEM VERIFIED SUCCESSFULLY")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)
