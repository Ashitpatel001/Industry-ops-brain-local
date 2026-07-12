#!/usr/bin/env python3
"""
scripts/download_model.py
=========================
Downloads Qwen2.5-3B-Instruct and converts/exports it to OpenVINO INT4 IR format.

Usage:
    python scripts/download_model.py
"""

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("DownloadModel")

# Default model configurations
DEFAULT_MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"
DEFAULT_OV_DIR = Path("models/qwen2.5-3b-int4")


def check_openvino_model(output_dir: Path) -> bool:
    """Check if OpenVINO IR INT4 model already exists."""
    xml_files = list(output_dir.glob("*.xml")) if output_dir.exists() else []
    bin_files = list(output_dir.glob("*.bin")) if output_dir.exists() else []
    if xml_files and bin_files:
        logger.info(f"✅ OpenVINO INT4 model already exists in {output_dir}")
        return True
    return False


def download_openvino(model_id: str, output_dir: Path):
    """Export model to OpenVINO INT4 format using optimum-cli."""
    if check_openvino_model(output_dir):
        return

    logger.info("==========================================================================")
    logger.info(f"🚀 Downloading & Converting to OpenVINO INT4: {model_id}")
    logger.info(f"📂 Output Directory: {output_dir}")
    logger.info("⚡ This will download ~7.6GB of weights and compress to ~2.2GB INT4 IR.")
    logger.info("==========================================================================")

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "optimum-cli",
        "export",
        "openvino",
        "--model",
        model_id,
        "--weight-format",
        "int4",
        "--task",
        "text-generation-with-past",
        str(output_dir),
    ]

    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        logger.info(f"✅ Successfully exported OpenVINO INT4 model to {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to export OpenVINO model: {e}")
        logger.info("💡 Make sure you have installed: pip install openvino-genai optimum[openvino] nncf transformers")
        raise
    except FileNotFoundError:
        logger.error("❌ 'optimum-cli' command not found in PATH.")
        logger.info("💡 Please activate your virtual environment and run: pip install optimum[openvino] nncf openvino-genai transformers")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during Qwen model download/export: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Download and convert Qwen model for Ops Brain Local.")
    parser.add_argument(
        "--model-id",
        type=str,
        default=DEFAULT_MODEL_ID,
        help=f"HuggingFace model ID for OpenVINO export (default: {DEFAULT_MODEL_ID})",
    )
    parser.add_argument(
        "--ov-dir",
        type=Path,
        default=DEFAULT_OV_DIR,
        help=f"Output directory for OpenVINO IR model (default: {DEFAULT_OV_DIR})",
    )

    args = parser.parse_args()

    try:
        download_openvino(args.model_id, args.ov_dir)
        logger.info("🎉 Qwen INT4 model setup complete! You can now run Ops Brain Local offline.")
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
