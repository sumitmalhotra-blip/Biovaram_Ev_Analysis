"""
NTA Visualization Module

Generates size distribution plots and concentration analysis for Nanoparticle Tracking Analysis (NTA) data.
Supports histograms, cumulative distributions, D10/D50/D90 markers, and multi-sample comparisons.

Author: GitHub Copilot
Date: November 14, 2025
Task: 1.3.2 - NTA Size Distribution Analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, List, Tuple
from loguru import logger

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10


class NTAPlotter:
    """
    Generate publication-quality plots for NTA data.
    
    Features:
    - Size distribution histograms
    - Cumulative distribution curves
    - D10/D50/D90 percentile markers
    - Concentration vs size plots
    - Multi-sample comparison overlays
    """
    
    def __init__(self, output_dir: Path = Path("figures/nta")):
        """
        Initialize NTA plotter.
        
        Args:
            output_dir: Directory to save generated plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"NTA Plotter initialized. Output: {self.output_dir}")
    
    def plot_size_distribution(
        self,
        data: pd.DataFrame,
        title: Optional[str] = None,
        output_file: Optional[Path] = None,
        show_stats: bool = True
    ) -> plt.Figure:
        """
        Create size distribution histogram with statistics.
        
        Args:
            data: DataFrame containing NTA measurements (positions)
            title: Plot title (auto-generated if None)
            output_file: Path to save plot
            show_stats: Show D10/D50/D90 markers and statistics
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract size data (median_size_nm for each position)
        if 'median_size_nm' not in data.columns:
            raise ValueError("Column 'median_size_nm' not found in data")
        
        sizes = data['median_size_nm'].dropna()
        
        # Create histogram
        n, bins, patches = ax.hist(
            sizes,
            bins=20,
            color='steelblue',
            alpha=0.7,
            edgecolor='black',
            linewidth=1.2
        )
        
        # Add statistics if requested
        if show_stats:
            mean_size = sizes.mean()
            median_size = sizes.median()
            
            # Calculate percentiles
            d10 = np.percentile(sizes, 10)
            d50 = np.percentile(sizes, 50)
            d90 = np.percentile(sizes, 90)
            
            # Add vertical lines for percentiles
            ax.axvline(d10, color='red', linestyle='--', linewidth=2, label=f'D10: {d10:.1f} nm')
            ax.axvline(d50, color='green', linestyle='--', linewidth=2, label=f'D50: {d50:.1f} nm')
            ax.axvline(d90, color='orange', linestyle='--', linewidth=2, label=f'D90: {d90:.1f} nm')
            
            # Add text box with statistics
            stats_text = f'Mean: {mean_size:.1f} nm\nMedian: {median_size:.1f} nm\nN positions: {len(sizes)}'
            ax.text(
                0.95, 0.95,
                stats_text,
                transform=ax.transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=10
            )
            
            ax.legend(loc='upper left')
        
        # Labels
        ax.set_xlabel('Particle Size (nm)', fontweight='bold')
        ax.set_ylabel('Frequency', fontweight='bold')
        
        # Title
        if title is None:
            sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else 'Unknown'
            title = f'NTA Size Distribution: {sample_id}'
        ax.set_title(title, fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save if output_file provided
        if output_file:
            output_path = self.output_dir / output_file
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot: {output_path}")
            plt.close(fig)  # Close figure to free memory
        
        return fig
    
    def plot_cumulative_distribution(
        self,
        data: pd.DataFrame,
        title: Optional[str] = None,
        output_file: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create cumulative size distribution curve.
        
        Args:
            data: DataFrame containing NTA measurements
            title: Plot title
            output_file: Path to save plot
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Extract size data
        sizes = data['median_size_nm'].dropna().sort_values()
        
        # Calculate cumulative distribution
        cumulative = np.arange(1, len(sizes) + 1) / len(sizes) * 100
        
        # Plot
        ax.plot(sizes, cumulative, color='steelblue', linewidth=2)
        ax.fill_between(sizes, cumulative, alpha=0.3, color='steelblue')
        
        # Add percentile markers
        d10 = np.percentile(sizes, 10)
        d50 = np.percentile(sizes, 50)
        d90 = np.percentile(sizes, 90)
        
        ax.axvline(d10, color='red', linestyle='--', linewidth=2, alpha=0.7, label=f'D10: {d10:.1f} nm')
        ax.axhline(10, color='red', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.axvline(d50, color='green', linestyle='--', linewidth=2, alpha=0.7, label=f'D50: {d50:.1f} nm')
        ax.axhline(50, color='green', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.axvline(d90, color='orange', linestyle='--', linewidth=2, alpha=0.7, label=f'D90: {d90:.1f} nm')
        ax.axhline(90, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        
        # Labels
        ax.set_xlabel('Particle Size (nm)', fontweight='bold')
        ax.set_ylabel('Cumulative Frequency (%)', fontweight='bold')
        
        # Title
        if title is None:
            sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else 'Unknown'
            title = f'Cumulative Size Distribution: {sample_id}'
        ax.set_title(title, fontweight='bold')
        
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save
        if output_file:
            output_path = self.output_dir / output_file
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot: {output_path}")
        
        return fig
    
    def plot_concentration_profile(
        self,
        data: pd.DataFrame,
        title: Optional[str] = None,
        output_file: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create scatter plot of concentration vs particle size.
        
        Args:
            data: DataFrame containing NTA measurements
            title: Plot title
            output_file: Path to save plot
            
        Returns:
            matplotlib Figure object
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Check required columns
        if 'median_size_nm' not in data.columns or 'concentration_particles_ml' not in data.columns:
            raise ValueError("Required columns not found")
        
        # Plot
        scatter = ax.scatter(
            data['median_size_nm'],
            data['concentration_particles_ml'],
            s=100,
            c=data.get('position', range(len(data))),
            cmap='viridis',
            alpha=0.7,
            edgecolors='black',
            linewidth=1
        )
        
        # Colorbar for positions
        cbar = plt.colorbar(scatter, ax=ax, label='Measurement Position')
        
        # Labels
        ax.set_xlabel('Median Particle Size (nm)', fontweight='bold')
        ax.set_ylabel('Concentration (particles/mL)', fontweight='bold')
        ax.set_yscale('log')  # Log scale for concentration
        
        # Title
        if title is None:
            sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else 'Unknown'
            title = f'Concentration vs Size: {sample_id}'
        ax.set_title(title, fontweight='bold')
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save
        if output_file:
            output_path = self.output_dir / output_file
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot: {output_path}")
        
        return fig
    
    def create_summary_plot(
        self,
        data: pd.DataFrame,
        output_file: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create 2x2 summary plot for NTA data.
        
        Args:
            data: DataFrame containing NTA measurements
            output_file: Path to save plot
            
        Returns:
            matplotlib Figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Get sample info
        sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else 'Unknown'
        
        # Plot 1: Size distribution histogram (top-left)
        sizes = data['median_size_nm'].dropna()
        axes[0, 0].hist(sizes, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
        axes[0, 0].axvline(sizes.median(), color='red', linestyle='--', linewidth=2, label=f'Median: {sizes.median():.1f} nm')
        axes[0, 0].set_xlabel('Particle Size (nm)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Size Distribution')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Cumulative distribution (top-right)
        sizes_sorted = sizes.sort_values()
        cumulative = np.arange(1, len(sizes_sorted) + 1) / len(sizes_sorted) * 100
        axes[0, 1].plot(sizes_sorted, cumulative, color='steelblue', linewidth=2)
        axes[0, 1].fill_between(sizes_sorted, cumulative, alpha=0.3, color='steelblue')
        axes[0, 1].set_xlabel('Particle Size (nm)')
        axes[0, 1].set_ylabel('Cumulative %')
        axes[0, 1].set_title('Cumulative Distribution')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Concentration profile (bottom-left)
        if 'concentration_particles_ml' in data.columns:
            axes[1, 0].scatter(
                data['median_size_nm'],
                data['concentration_particles_ml'],
                s=80,
                alpha=0.6,
                color='coral',
                edgecolors='black'
            )
            axes[1, 0].set_xlabel('Size (nm)')
            axes[1, 0].set_ylabel('Concentration (particles/mL)')
            axes[1, 0].set_yscale('log')
            axes[1, 0].set_title('Concentration vs Size')
            axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Position analysis (bottom-right)
        if 'position' in data.columns:
            position_data = data.groupby('position')['median_size_nm'].mean()
            axes[1, 1].bar(
                position_data.index,
                position_data.values,
                color='forestgreen',
                alpha=0.7,
                edgecolor='black'
            )
            axes[1, 1].set_xlabel('Measurement Position')
            axes[1, 1].set_ylabel('Mean Size (nm)')
            axes[1, 1].set_title('Size by Position')
            axes[1, 1].grid(True, alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, 'Position data\nnot available', 
                          ha='center', va='center', fontsize=12)
            axes[1, 1].axis('off')
        
        # Overall title
        fig.suptitle(f'NTA Summary: {sample_id}', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Save
        if output_file:
            output_path = self.output_dir / output_file
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved summary plot: {output_path}")
        
        return fig


def generate_nta_plots(parquet_file: Path, output_dir: Path = Path("figures/nta")) -> None:
    """
    Convenience function to generate all standard plots for an NTA file.
    
    Args:
        parquet_file: Path to NTA Parquet file
        output_dir: Directory to save plots
    """
    logger.info(f"Generating plots for {parquet_file.name}")
    
    # Load data
    data = pd.read_parquet(parquet_file)
    
    # Initialize plotter
    plotter = NTAPlotter(output_dir=output_dir)
    
    # Get sample ID for filenames
    sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else parquet_file.stem
    
    # Generate size distribution
    plotter.plot_size_distribution(
        data=data,
        output_file=f"{sample_id}_size_distribution.png"
    )
    
    # Generate cumulative distribution
    plotter.plot_cumulative_distribution(
        data=data,
        output_file=f"{sample_id}_cumulative.png"
    )
    
    # Generate concentration profile
    if 'concentration_particles_ml' in data.columns:
        plotter.plot_concentration_profile(
            data=data,
            output_file=f"{sample_id}_concentration.png"
        )
    
    # Generate summary plot
    plotter.create_summary_plot(
        data=data,
        output_file=f"{sample_id}_summary.png"
    )
    
    # Close all figures to free memory
    plt.close('all')
    
    logger.success(f"Γ£à Plots generated for {sample_id}")


if __name__ == "__main__":
    # Example usage
    from pathlib import Path
    
    # Find first NTA file
    nta_dir = Path("data/parquet/nta/measurements")
    nta_files = list(nta_dir.glob("*.parquet"))
    
    if nta_files:
        print(f"Found {len(nta_files)} NTA files")
        print(f"Generating plots for first file: {nta_files[0].name}")
        generate_nta_plots(nta_files[0])
    else:
        print("No NTA Parquet files found!")
