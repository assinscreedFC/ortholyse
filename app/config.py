# =============================================================================
# Centralised app configuration: root path resolution + logging setup.
# Importing this module configures logging.basicConfig as a side effect.
# =============================================================================
import logging
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
