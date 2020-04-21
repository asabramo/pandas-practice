import sys
import pandas as pd
import matplotlib.pyplot as plt


def load_data():
    #Data taken from: https://github.com/CSSEGISandData/COVID-19.git
    df = pd.read_csv("../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df = df.rename(columns={'Country/Region': 'country'})
    return df


def filter_by_country(country, df):
    return df[df['country'] == country]


def keep_only_data_columns(df):
    #column 3 is the Longitude column
    return df.iloc[:,4:]


def add_avg_speed_column(df):
    # TODO:filter out days before the first infection in the country
    num_days = len(df.columns) - 4
    last_column = df.columns[len(df.columns) - 1];
    speed_column = df.apply(lambda df: df[last_column] / num_days, axis = 1)
    df.insert(4, "speed", speed_column)
    return df

if __name__ == '__main__':
    df = load_data()
    df = add_avg_speed_column(df)
    if (len(sys.argv) == 1):
        country = 'Israel'
    else:
        country = sys.argv[1]
    row = filter_by_country(country, df)
    row = keep_only_data_columns(row)
    speed = row.iloc[0,0]
    #Skip the first column - "speed"
    row_data = row.iloc[:,1:]
    row_data.plot(kind='bar')
    title = 'Total COVID-19 infected in {0}'.format(country)
    title += '\nAverage infected per day in {0} is {1} '.format(country, speed)
    plt.title(title)

    plt.show()
