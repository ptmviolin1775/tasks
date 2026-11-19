import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# Import data (Make sure to parse dates. Consider setting index column to 'date'.)
df = pd.read_csv('fcc-forum-pageviews.csv')
df['date'] = pd.to_datetime(df['date'],format='%Y-%m-%d')
df.index = df['date']
df = df.drop(columns = ['date'])

# Clean data
lower_lim = df.quantile(.025).item()
upper_lim = df.quantile(.975).item()
df = df.loc[(df['value'] >= lower_lim) & (df['value'] <= upper_lim)]


def draw_line_plot():
    plt.ioff()
    plt.plot(df)
    plt.xlabel('Date')
    plt.ylabel('Page Views')
    plt.title('Daily freeCodeCamp Forum Page Views 5/2016-12/2019')
    plt.show()


    # Save image and return fig (don't change this part)
    fig = plt.savefig('line_plot.png')
    return fig

def draw_bar_plot():
    # Copy and modify data for monthly bar plot
    plt.close('all')
    df_bar = df.copy()
    df_bar.reset_index(inplace=True)
    df_bar['year'] = [d.year for d in df_bar.date]
    df_bar['month'] = [d.strftime('%b') for d in df_bar.date]
    df_bar_pivot = df_bar.pivot_table(index = 'year',columns = 'month',values = 'value')
    df_bar_pivot = df_bar_pivot[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']]

    # Draw bar plot
    ax = df_bar_pivot.plot(kind = 'bar') 
    ax.legend(fontsize=10)
    ax.set_xlabel('Years')
    ax.set_ylabel('Average Page Views')

    # Save image and return fig (don't change this part)
    fig = ax.get_figure()
    fig.savefig('bar_plot.png')
    plt.show()
    return fig

def draw_box_plot():
    # Prepare data for box plots (this part is done!)
    df_box = df.copy()
    df_box.reset_index(inplace=True)
    df_box['year'] = [d.year for d in df_box.date]
    df_box['month'] = [d.strftime('%b') for d in df_box.date]

    # Draw box plots (using Seaborn)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    sns.boxplot(data = df_box,x='year',y='value',palette='Set2',ax=axes[0])
    axes[0].set_xlabel('Year')
    axes[0].set_ylabel('Average Page Views')
    axes[0].set_title('Year-wise Box Plot (Trend)')
    sns.boxplot(data = df_box,x='month',y='value',palette='Set2',order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],ax=axes[1])
    axes[1].set_xlabel('Month')
    axes[1].set_ylabel('Page Views')
    axes[1].set_title('Month-wise Box Plot (Seasonality)')
    plt.tight_layout()
    plt.show()


    # Save image and return fig (don't change this part)
    fig.get_figure().savefig('box_plot.png')
    return fig

draw_line_plot()
draw_bar_plot()
draw_box_plot()