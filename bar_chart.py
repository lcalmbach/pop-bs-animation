import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import numpy as np
from PIL import Image

def create_animation(df, flag_folder):
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Dictionary to store flag images (load once for efficiency)
    flag_images = {}
    
    # Load all unique flags
    for iso_code in df['ISO3_code'].unique():
        try:
            flag_path = f"{flag_folder}/{iso_code}.png"
            img = Image.open(flag_path)
            # Resize for better performance
            img.thumbnail((50, 30), Image.Resampling.LANCZOS)
            flag_images[iso_code] = img
        except:
            print(f"Could not load flag for {iso_code}")
    
    # Get unique timestamps
    df['timestamp'] = pd.to_datetime(df['Time'].astype(str) + '-' + df['Month'].astype(str), format='%Y-%m')
    timestamps = sorted(df['timestamp'].unique())
    
    def animate(frame):
        ax.clear()
        
        # Get data for current timestamp
        current_time = timestamps[frame]
        current_data = df[df['timestamp'] == current_time]
        
        # Get top 10 populations
        top_10 = current_data.nlargest(10, 'Population')
        
        # Create bars
        bars = ax.barh(range(len(top_10)), top_10['Population'], alpha=0.3)
        
        # Add flags and labels
        for i, (_, row) in enumerate(top_10.iterrows()):
            # Add flag
            if row['ISO3_code'] in flag_images:
                flag_img = flag_images[row['ISO3_code']]
                img_box = OffsetImage(flag_img, zoom=0.5)
                ab = AnnotationBbox(img_box, (0, i),
                                  frameon=False,
                                  box_alignment=(0, 0.5),
                                  xybox=(-50, 0),
                                  xycoords=('data', 'data'),
                                  boxcoords="offset points")
                ax.add_artist(ab)
            
            # Add population value
            ax.text(row['Population'], i,
                   f' {row["Population"]:,.0f}',
                   va='center', ha='left', fontweight='bold')
            
            # Add country name
            ax.text(-0.1, i, f"{row['Location']}", 
                   ha='right', va='center', transform=ax.get_yaxis_transform())
        
        # Remove y-axis labels since we're adding them manually
        ax.set_yticks([])
        
        # Set fixed title
        ax.set_title('Top 10 Populations', pad=20, fontsize=14, fontweight='bold')
        
        # Add month and year text
        plt.text(0.75, 0.95, f'Year: {current_time.year}',
                transform=ax.transAxes,
                fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        plt.text(0.75, 0.89, f'Month: {current_time.strftime("%B")}', 
                transform=ax.transAxes,
                fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        
        ax.set_xlabel('Population')
        
        # Format x-axis with comma separator
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # Add grid lines
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # Remove frame
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Adjust layout
        plt.tight_layout()
    
    # Create animation
    anim = animation.FuncAnimation(fig, animate,
                                 frames=len(timestamps),
                                 interval=50,
                                 repeat=True)
    
    return fig, anim

# Read and prepare the data
df = pd.read_csv('test.csv')

# Example usage
flag_folder = "./flags"  # Replace with actual path
fig, anim = create_animation(df, flag_folder)
plt.show()