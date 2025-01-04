# most of the code originates from the repo: https://github.com/KeithGalli/time-series-animations
# explained by its author on the excellent youtube channel: https://www.youtube.com/watch?v=mafzIn8TneQ
# I have simply adapted the datasource which is now a csv file from the Basel Open Data Portal showing the
# ratio of different nationalities in Basel, Switzerland since 1979.

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
from pathlib import Path

__version__ = '0.1.0'

def load_flag_images(df, flag_folder):
    """Load and resize all flag images once at startup"""
    flag_images = {}
    for iso_code in df['iso3_code'].unique():
        try:
            img = Image.open(f"{flag_folder}/{iso_code}.png")
            img.thumbnail((50, 30), Image.Resampling.LANCZOS)
            flag_images[iso_code] = img
        except:
            print(f"Could not load flag for {iso_code}")
    return flag_images

def setup_plot_style(ax):
    """Apply consistent plot styling"""
    ax.set_yticks([])
    ax.set_xlabel('population')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_title('Top 10 nationalities in Basel/Switzerland', pad=20, fontsize=14, fontweight='bold')

def add_timestamp_text(ax, current_time):
    """Add year and month text to plot"""
    plt.text(0.75, 0.15, f'Year: {current_time.year}',
            transform=ax.transAxes, fontsize=12, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
    plt.text(0.75, 0.09, f'Month: {current_time.strftime("%B")}', 
            transform=ax.transAxes, fontsize=12, fontweight='bold',
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

def create_animation(df, flag_folder):
    # Initial setup
    fig, ax = plt.subplots(figsize=(12, 6))
    flag_images = load_flag_images(df, flag_folder)
    
    # Prepare timeline
    df['timestamp'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str), format='%Y-%m')
    timestamps = sorted(df['timestamp'].unique())

    # Countries needing extra space to prevent jitter
    unstable_names = {'Germany', 'Mexico', 'Ethiopia', 'Bangladesh'}
    
    def animate(frame):
        ax.clear()
        
        # Get current data
        current_time = timestamps[frame]
        top_10 = df[df['timestamp'] == current_time].nlargest(10, 'population')
        top_10 = top_10.sort_values('population', ascending=True).reset_index(drop=True)
        
        # Create base bars
        bars = ax.barh(top_10['nationality'], top_10['population'], alpha=0.3)
        
        # Add visual elements for each country
        for i, row in top_10.iterrows():
            # Add flag
            if row['iso3_code'] in flag_images:
                img_box = OffsetImage(flag_images[row['iso3_code']], zoom=0.5)
                ab = AnnotationBbox(img_box, (0, i),
                                    frameon=False,
                                    box_alignment=(0, 0.5),
                                    xybox=(-50, 0),
                                    xycoords=('data', 'data'),
                                    boxcoords="offset points")
                ax.add_artist(ab)
            
            # Add labels
            ax.text(row['population'], i,
                    f' {row["population"]:,.2f}',
                    va='center', ha='left', fontweight='bold')
            
            country_name = f"{row['nationality']}  " if row['nationality'] in unstable_names else row['nationality']
            ax.text(-0.1, i, country_name, 
                    ha='right', va='center', transform=ax.get_yaxis_transform())
        
        # Set x-axis limits to keep it constant
        # ax.set_xlim(0, 150000)
        
        # Style the plot
        setup_plot_style(ax)
        add_timestamp_text(ax, current_time)
        plt.tight_layout()
    
    # Create and return animation
    return animation.FuncAnimation(
        fig, animate, frames=len(timestamps),
        interval=600, repeat=False
    )

def get_data():
    """
    Reads and processes population data from CSV files.

    This function reads raw population data from a CSV file, cleans it, and processes it to generate a cleaned dataset.
    If a cleaned dataset already exists, it reads from the cleaned file instead. The function also merges the population
    data with country information to add ISO3 codes for flags.

    Returns:
        pd.DataFrame: A DataFrame containing the processed population data with columns:
                      - 'date': The date of the record.
                      - 'year': The year of the record.
                      - 'month': The month of the record (set to 12).
                      - 'nationality': The nationality of the population.
                      - 'population': The population count.
                      - 'iso3_code': The ISO3 code of the country.
    """

    raw_file = 'https://data.bs.ch/api/explore/v2.1/catalog/datasets/100126/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%3B'
    cleaned_file = './data/100126_cleaned.csv'
    country_file = './data/countries.csv'

    if Path.is_file(Path(cleaned_file)):
        df = pd.read_csv(cleaned_file, sep=';')
    else:
        df = pd.read_csv(raw_file, sep=';')
        df = df[~df['staatsangehoerigkeit'].str.contains('unbekannt', na=False)]
        df = df[df['staatsangehoerigkeit'] != 'Staat unbekannt oder nicht angegeben']
        df_total_population = df.groupby(['datum', 'jahr', 'staatsangehoerigkeit'], as_index=False)['anzahl'].sum()
        df_total_population.columns = ['date', 'year', 'nationality', 'population']
        df_total_population['month'] = 12
        df_total_population = df_total_population[['date', 'year', 'month', 'nationality', 'population']]
        df_countries = pd.read_csv(country_file, sep=';')
        # add iso3 code for flags
        df = df_total_population.merge(
            df_countries[['german', 'iso3_code']],  # Select only relevant columns from df_countries
            left_on='nationality',  # Column name in the left table
            right_on='german',  # Column name in the right table
            how='left'  # Use a left join to keep all rows from df_total_population
        )
        df.to_csv(cleaned_file, index=False, sep=';')
    return df


if __name__ == "__main__":
    df = get_data()
    anim = create_animation(df, "./flags")
    anim.save('outputs/population_bs_animation.mp4', writer='ffmpeg', fps=5)
    plt.show()