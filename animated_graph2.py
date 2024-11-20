import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from datetime import datetime, timedelta

def create_animation(csv_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Convert Date to datetime using a specific format with 4-digit year
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    
    # Convert Close/Last to float (remove $ and convert)
    df['Close/Last'] = df['Close/Last'].str.replace('$', '').astype(float)
    
    # Sort by date in ascending order
    df = df.sort_values('Date')
    
    # Create the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Function to animate the plot
    def animate(frame):
        ax.clear()
        
        # Plot data up to the current frame
        data_subset = df.iloc[:frame+1]
        
        # Create the line plot
        ax.plot(data_subset['Date'], data_subset['Close/Last'], 
                color='blue', linewidth=2, marker='o')
        
        # Add the latest price annotation
        if not data_subset.empty:
            latest_price = data_subset['Close/Last'].iloc[-1]
            latest_date = data_subset['Date'].iloc[-1]
            ax.annotate(f'${latest_price:.2f}', 
                       xy=(latest_date, latest_price),
                       xytext=(10, 10), textcoords='offset points',
                       bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
        
        # Customize the plot
        ax.set_title('Stock Price Over Time', fontsize=12, pad=20)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        
        # Format x-axis to show month/day/year
        ax.xaxis.set_major_formatter(DateFormatter('%m/%d/%Y'))
        ax.tick_params(axis='x', rotation=45)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Set dynamic axis limits based on current subset of data
        if not data_subset.empty:
            # Dynamic y-axis limits
            y_min = data_subset['Close/Last'].min() * 0.95
            y_max = data_subset['Close/Last'].max() * 1.05
            ax.set_ylim(y_min, y_max)
            
            # Dynamic x-axis limits
            start_date = data_subset['Date'].min()
            end_date = data_subset['Date'].max()
            
            # Add a small buffer to the right for better visibility
            date_range = end_date - start_date
            buffer = date_range * 0.1  # 10% buffer
            
            ax.set_xlim(start_date, end_date + buffer)
        
        # Adjust layout
        plt.tight_layout()
    
    # Create the animation
    anim = animation.FuncAnimation(fig, animate, 
                                 frames=len(df),
                                 interval=50,  # 50ms between frames
                                 repeat=True)
    
    return fig, anim

# Example usage:
csv_path = 'historical_data.csv'  # Replace with your CSV file path
fig, anim = create_animation(csv_path)
plt.show()

# Optional: save the animation
# anim.save('stock_price_animation.gif', writer='pillow')