"""
Batch FCS Plot Generation Script

Processes all FCS Parquet files and generates scatter plots for each sample.

Usage:
    python scripts/generate_fcs_plots.py [--limit N] [--output-dir PATH]

Author: GitHub Copilot
Date: November 14, 2025
Task: 1.3.1 - Batch FCS Visualization
"""

import sys
from pathlib import Path
import argparse
from tqdm import tqdm
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization.fcs_plots import generate_fcs_plots
from loguru import logger


def batch_generate_fcs_plots(
    input_dir: Path,
    output_dir: Path,
    limit: int | None = None
) -> None:
    """
    Generate plots for all FCS Parquet files.
    
    Args:
        input_dir: Directory containing FCS Parquet files
        output_dir: Directory to save plots
        limit: Maximum number of files to process (None = all)
    """
    # Find all FCS files
    fcs_files = list(input_dir.glob("*.parquet"))
    
    if not fcs_files:
        logger.error(f"No Parquet files found in {input_dir}")
        return
    
    logger.info(f"Found {len(fcs_files)} FCS files")
    
    # Limit if specified
    if limit:
        fcs_files = fcs_files[:limit]
        logger.info(f"Processing first {limit} files")
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for fcs_file in tqdm(fcs_files, desc="Generating FCS plots"):
        try:
            generate_fcs_plots(fcs_file, output_dir=output_dir)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {fcs_file.name}: {e}")
            error_count += 1
    
    # Summary
    logger.success(f"✅ Complete! {success_count} files processed, {error_count} errors")


def main():
    parser = argparse.ArgumentParser(
        description="Batch generate FCS scatter plots"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/parquet/nanofacs/events"),
        help="Directory containing FCS Parquet files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("figures/fcs"),
        help="Directory to save plots"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of files to process"
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    # Run batch processing
    batch_generate_fcs_plots(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
