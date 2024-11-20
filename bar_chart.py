import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from datetime import datetime

def create_animation(df):
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Get unique timestamps (year-month combinations)
    df['timestamp'] = pd.to_datetime(df['Time'].astype(str) + '-' + df['Month'].astype(str), format='%Y-%m')
    timestamps = sorted(df['timestamp'].unique())
    
    def animate(frame):
        ax.clear()
        
        # Get data for current timestamp
        current_time = timestamps[frame]
        current_data = df[df['timestamp'] == current_time]
        
        # Get top 10 populations for current timestamp
        top_10 = current_data.nlargest(10, 'Population')
        
        # Create horizontal bar chart
        bars = ax.barh(top_10['Location'], top_10['Population'])
        
        # Add value labels on the bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{width:,.0f}',
                   ha='left', va='center', fontweight='bold')
        
        # Set fixed title
        ax.set_title('Top 10 Populations', pad=20, fontsize=14, fontweight='bold')
        
        # Add month and year text
        plt.text(.75, 0.95, f'Year: {current_time.year}',
                transform=ax.transAxes,
                fontsize=12, fontweight='bold',
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        plt.text(.75, 0.89, f'Month: {current_time.strftime("%B")}', 
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
                                 interval=100,  # 200ms between frames
                                 repeat=True)
    
    return fig, anim

# Read and prepare the data
df = pd.read_csv('test.csv')

# Create and display the animation
fig, anim = create_animation(df)
plt.show()

# Optional: save the animation
# anim.save('population_animation.gif', writer='pillow')