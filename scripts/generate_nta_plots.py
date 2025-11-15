"""
Batch NTA Plot Generation Script

Processes all NTA Parquet files and generates size distribution plots for each sample.

Usage:
    python scripts/generate_nta_plots.py [--limit N] [--output-dir PATH]

Author: GitHub Copilot
Date: November 14, 2025
Task: 1.3.2 - Batch NTA Visualization
"""

import sys
from pathlib import Path
import argparse
from tqdm import tqdm

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.visualization.nta_plots import generate_nta_plots
from loguru import logger


def batch_generate_nta_plots(
    input_dir: Path,
    output_dir: Path,
    limit: int | None = None
) -> None:
    """
    Generate plots for all NTA Parquet files.
    
    Args:
        input_dir: Directory containing NTA Parquet files
        output_dir: Directory to save plots
        limit: Maximum number of files to process (None = all)
    """
    # Find all NTA files
    nta_files = list(input_dir.glob("*.parquet"))
    
    if not nta_files:
        logger.error(f"No Parquet files found in {input_dir}")
        return
    
    logger.info(f"Found {len(nta_files)} NTA files")
    
    # Limit if specified
    if limit:
        nta_files = nta_files[:limit]
        logger.info(f"Processing first {limit} files")
    
    # Process each file
    success_count = 0
    error_count = 0
    
    for nta_file in tqdm(nta_files, desc="Generating NTA plots"):
        try:
            generate_nta_plots(nta_file, output_dir=output_dir)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {nta_file.name}: {e}")
            error_count += 1
    
    # Summary
    logger.success(f"✅ Complete! {success_count} files processed, {error_count} errors")


def main():
    parser = argparse.ArgumentParser(
        description="Batch generate NTA size distribution plots"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("data/parquet/nta/measurements"),
        help="Directory containing NTA Parquet files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("figures/nta"),
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
    batch_generate_nta_plots(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        limit=args.limit
    )


if __name__ == "__main__":
    main()
