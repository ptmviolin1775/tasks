import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import numpy as np

def draw_plot():
    # Read data from file
    df = pd.read_csv('epa-sea-level.csv')

    # Create scatter plot
    plt.scatter(df['Year'], df['CSIRO Adjusted Sea Level'])

    # Create first line of best fit
    regression_line_1 = linregress(df['Year'], df['CSIRO Adjusted Sea Level'])
    x1 = np.arange(df['Year'].min(),2050,1)
    y1 = x1*regression_line_1.slope + regression_line_1.intercept

    plt.plot(x1,y1)

    # Create second line of best fit
    df_2000 = df[df['Year'] >= 2000]

    regression_line_2 = linregress(df_2000['Year'], df_2000['CSIRO Adjusted Sea Level'])
    x2 = np.arange(2000,2050,1)
    y2 = x2*regression_line_2.slope + regression_line_2.intercept

    plt.plot(x2,y2)

    # Add labels and title
    plt.xlabel('Year')
    plt.ylabel('Sea Level (inches)')
    plt.title('Rise in Sea Level')
    plt.show()
    
    # Save plot and return data for testing (DO NOT MODIFY)
    plt.savefig('sea_level_plot.png')
    return plt.gca()

draw_plot()