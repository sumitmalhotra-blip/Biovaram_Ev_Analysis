"""
FCS Visualization Module

Generates scatter plots and density plots for Flow Cytometry (FCS) data.
Supports FSC vs SSC plots, fluorescence channel plots, and gating visualizations.

Author: GitHub Copilot
Date: November 14, 2025
Task: 1.3.1 - FCS Scatter Plot Generation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional, Tuple, List
from loguru import logger

# Set style for publication-quality plots
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10


class FCSPlotter:
    """
    Generate publication-quality scatter plots for Flow Cytometry data.
    
    Features:
    - FSC-A vs SSC-A scatter plots (standard gating view)
    - FL channel scatter plots (marker analysis)
    - Density plots with hexbin or 2D histogram
    - Gate overlays (optional)
    - Batch processing for multiple samples
    """
    
    def __init__(self, output_dir: Path = Path("figures/fcs")):
        """
        Initialize FCS plotter.
        
        Args:
            output_dir: Directory to save generated plots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"FCS Plotter initialized. Output: {self.output_dir}")
    
    def plot_scatter(
        self,
        data: pd.DataFrame,
        x_channel: str,
        y_channel: str,
        title: Optional[str] = None,
        output_file: Optional[Path | str] = None,
        xlim: Optional[Tuple[float, float]] = None,
        ylim: Optional[Tuple[float, float]] = None,
        plot_type: str = "scatter",
        sample_size: int = 10000,
        colormap: str = "viridis"
    ) -> plt.Figure:
        """
        Create scatter plot for two channels.
        
        Args:
            data: DataFrame containing FCS event data
            x_channel: Column name for X-axis (e.g., 'VFSC-A')
            y_channel: Column name for Y-axis (e.g., 'VSSC1-A')
            title: Plot title (auto-generated if None)
            output_file: Path to save plot (auto-generated if None)
            xlim: X-axis limits (auto if None)
            ylim: Y-axis limits (auto if None)
            plot_type: 'scatter', 'hexbin', or 'density'
            sample_size: Number of events to plot (for performance)
            colormap: Color map for density plots
            
        Returns:
            matplotlib Figure object
        """
        # Validate channels exist
        if x_channel not in data.columns:
            raise ValueError(f"Channel '{x_channel}' not found in data")
        if y_channel not in data.columns:
            raise ValueError(f"Channel '{y_channel}' not found in data")
        
        # Sample data if too many events
        if len(data) > sample_size:
            data_plot = data.sample(n=sample_size, random_state=42)
            logger.info(f"Sampling {sample_size} of {len(data)} events for plotting")
        else:
            data_plot = data
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Generate plot based on type
        if plot_type == "scatter":
            scatter = ax.scatter(
                data_plot[x_channel],
                data_plot[y_channel],
                s=1,
                alpha=0.3,
                c='blue',
                edgecolors='none'
            )
            
        elif plot_type == "hexbin":
            hexbin = ax.hexbin(
                data_plot[x_channel],
                data_plot[y_channel],
                gridsize=50,
                cmap=colormap,
                mincnt=1
            )
            plt.colorbar(hexbin, ax=ax, label='Event Count')
            
        elif plot_type == "density":
            # 2D histogram
            h = ax.hist2d(
                data_plot[x_channel],
                data_plot[y_channel],
                bins=100,
                cmap=colormap,
                cmin=1
            )
            plt.colorbar(h[3], ax=ax, label='Event Count')
        
        # Set labels
        ax.set_xlabel(x_channel, fontweight='bold')
        ax.set_ylabel(y_channel, fontweight='bold')
        
        # Set title
        if title is None:
            sample_id = data['sample_id'].iloc[0] if 'sample_id' in data.columns and len(data) > 0 else 'Unknown'
            title = f"{sample_id}: {x_channel} vs {y_channel}"
        ax.set_title(title, fontweight='bold')
        
        # Set limits if provided
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Tight layout
        plt.tight_layout()
        
        # Save if output_file provided
        if output_file:
            output_path = self.output_dir / output_file
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved plot: {output_path}")
            plt.close(fig)  # Close figure to free memory
        
        return fig
    
    def plot_fsc_ssc(
        self,
        data: pd.DataFrame,
        output_file: Optional[Path] = None,
        plot_type: str = "hexbin"
    ) -> plt.Figure:
        """
        Create standard FSC-A vs SSC-A scatter plot (debris gating view).
        
        Args:
            data: DataFrame containing FCS event data
            output_file: Path to save plot
            plot_type: 'scatter', 'hexbin', or 'density'
            
        Returns:
            matplotlib Figure object
        """
        # Determine which FSC/SSC channels are available
        fsc_channels = [col for col in data.columns if 'FSC' in col and col.endswith('-A')]
        ssc_channels = [col for col in data.columns if 'SSC' in col and col.endswith('-A')]
        
        if not fsc_channels or not ssc_channels:
            raise ValueError("No FSC-A or SSC-A channels found in data")
        
        # Use first available channels
        fsc_channel = fsc_channels[0]
        ssc_channel = ssc_channels[0]
        
        logger.info(f"Plotting {fsc_channel} vs {ssc_channel}")
        
        return self.plot_scatter(
            data=data,
            x_channel=fsc_channel,
            y_channel=ssc_channel,
            title=None,  # Auto-generate
            output_file=output_file,
            plot_type=plot_type
        )
    
    def plot_fluorescence_channels(
        self,
        data: pd.DataFrame,
        marker_channels: Optional[List[str]] = None,
        output_prefix: Optional[str] = None
    ) -> List[plt.Figure]:
        """
        Create plots for fluorescence markers vs SSC.
        
        Args:
            data: DataFrame containing FCS event data
            marker_channels: List of fluorescence channels to plot
                            (auto-detect if None)
            output_prefix: Prefix for output filenames
            
        Returns:
            List of matplotlib Figure objects
        """
        # Auto-detect fluorescence channels if not provided
        if marker_channels is None:
            # Look for fluorescence channels (V, B, Y, R prefixes with numbers)
            marker_channels = [
                col for col in data.columns 
                if col.startswith(('V4', 'B5', 'Y5', 'R6', 'R7'))
                and col.endswith('-A')
            ]
        
        if not marker_channels:
            logger.warning("No fluorescence marker channels found")
            return []
        
        # Get SSC channel
        ssc_channels = [col for col in data.columns if 'SSC' in col and col.endswith('-A')]
        if not ssc_channels:
            logger.warning("No SSC-A channel found")
            return []
        
        ssc_channel = ssc_channels[0]
        
        # Generate plots for each marker
        figures = []
        sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else 'Unknown'
        
        for marker in marker_channels:
            logger.info(f"Plotting {marker} vs {ssc_channel}")
            
            # Generate output filename
            if output_prefix:
                output_file = f"{output_prefix}_{marker}_vs_{ssc_channel}.png"
            else:
                output_file = f"{sample_id}_{marker}_vs_{ssc_channel}.png"
            
            fig = self.plot_scatter(
                data=data,
                x_channel=marker,
                y_channel=ssc_channel,
                output_file=output_file,
                plot_type="hexbin"
            )
            figures.append(fig)
        
        return figures
    
    def create_summary_plot(
        self,
        data: pd.DataFrame,
        output_file: Optional[Path] = None
    ) -> plt.Figure:
        """
        Create 2x2 summary plot showing key scatter plots.
        
        Args:
            data: DataFrame containing FCS event data
            output_file: Path to save plot
            
        Returns:
            matplotlib Figure object
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 12))
        
        # Get sample info
        sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else 'Unknown'
        
        # Sample data for performance
        if len(data) > 10000:
            data_plot = data.sample(n=10000, random_state=42)
        else:
            data_plot = data
        
        # Plot 1: FSC-A vs SSC-A (top-left)
        fsc_channels = [col for col in data.columns if 'FSC' in col and col.endswith('-A')]
        ssc_channels = [col for col in data.columns if 'SSC' in col and col.endswith('-A')]
        
        if fsc_channels and ssc_channels:
            axes[0, 0].hexbin(
                data_plot[fsc_channels[0]],
                data_plot[ssc_channels[0]],
                gridsize=30,
                cmap='viridis',
                mincnt=1
            )
            axes[0, 0].set_xlabel(fsc_channels[0])
            axes[0, 0].set_ylabel(ssc_channels[0])
            axes[0, 0].set_title('Forward vs Side Scatter')
            axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2-4: Fluorescence markers vs SSC (top-right, bottom-left, bottom-right)
        fl_channels = [
            col for col in data.columns 
            if col.startswith(('V4', 'B5', 'Y5', 'R6', 'R7'))
            and col.endswith('-A')
        ][:3]  # First 3 fluorescence channels
        
        positions = [(0, 1), (1, 0), (1, 1)]
        for idx, fl_channel in enumerate(fl_channels):
            row, col = positions[idx]
            if ssc_channels:
                axes[row, col].hexbin(
                    data_plot[fl_channel],
                    data_plot[ssc_channels[0]],
                    gridsize=30,
                    cmap='plasma',
                    mincnt=1
                )
                axes[row, col].set_xlabel(fl_channel)
                axes[row, col].set_ylabel(ssc_channels[0])
                axes[row, col].set_title(f'{fl_channel} vs SSC')
                axes[row, col].grid(True, alpha=0.3)
        
        # Overall title
        fig.suptitle(f'FCS Summary: {sample_id}', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        # Save if output_file provided
        if output_file:
            output_path = self.output_dir / output_file
            fig.savefig(output_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved summary plot: {output_path}")
        
        return fig


def generate_fcs_plots(parquet_file: Path, output_dir: Path = Path("figures/fcs")) -> None:
    """
    Convenience function to generate all standard plots for an FCS file.
    
    Args:
        parquet_file: Path to FCS Parquet file
        output_dir: Directory to save plots
    """
    logger.info(f"Generating plots for {parquet_file.name}")
    
    # Load data
    data = pd.read_parquet(parquet_file)
    
    # Initialize plotter
    plotter = FCSPlotter(output_dir=output_dir)
    
    # Get sample ID for filenames
    sample_id = data.get('sample_id', ['Unknown']).iloc[0] if 'sample_id' in data.columns else parquet_file.stem
    
    # Generate FSC vs SSC plot
    plotter.plot_fsc_ssc(
        data=data,
        output_file=f"{sample_id}_FSC_vs_SSC.png"
    )
    
    # Generate fluorescence marker plots
    plotter.plot_fluorescence_channels(
        data=data,
        output_prefix=sample_id
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
    
    # Find first FCS file
    fcs_dir = Path("data/parquet/nanofacs/events")
    fcs_files = list(fcs_dir.glob("*.parquet"))
    
    if fcs_files:
        print(f"Found {len(fcs_files)} FCS files")
        print(f"Generating plots for first file: {fcs_files[0].name}")
        generate_fcs_plots(fcs_files[0])
    else:
        print("No FCS Parquet files found!")
