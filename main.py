import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_data():
    #Data taken from: https://github.com/CSSEGISandData/COVID-19.git
    df = pd.read_csv("../COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
    df = df.rename(columns={'Country/Region': 'country'})
    df.columns = df.columns[:4].to_list() + pd.to_datetime(df.columns[4:]).to_list()
    return df


def filter_by_country(country, df):
    return df[df['country'] == country]


def keep_only_data_columns(df):
    #column 3 is the Longitude column
    return df.iloc[:,4:]

def get_only_metadata_columns(df):
    return df.iloc[:, :4]

def add_avg_speed_column(df):
    # TODO:filter out days before the first infection in the country
    num_days = len(df.columns) - 4
    last_column = df.columns[len(df.columns) - 1];
    speed_column = df.apply(lambda df: df[last_column] / num_days, axis = 1)
    df.insert(4, "speed", speed_column)
    return df


def create_deltas_dataframe(df):
    pad_column = df.apply(lambda x: 0, axis = 1)
    shifted_df = df.copy()
    shifted_df.insert(0, "pad", pad_column)
    trimmed_df = shifted_df.iloc[:,:-1]
    trimmed_df.columns = df.columns
    deltas_df = df - trimmed_df
    return deltas_df


def chart_country_data(df, country, title, filename=None):
    row = filter_by_country(country, df)
    row = keep_only_data_columns(row)
    print(row)
    row_data = row.T
    # set ggplot style
    # plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(15,7))
    ax.set_title(title)
    ax.set_ylabel('Count')
    ax.set_xlabel('Date')
    # set ticks every week
    ax.xaxis.set_major_locator(mdates.WeekdayLocator())
    # # # # format date
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax.bar(row_data.index, row_data.iloc[:, 0])
    if (filename is None):
        plt.show()
    else:
        plt.savefig(filename)

def write_html(country):
    f = open('{0}.html'.format(country), 'w')
    header = '''<html>
    <header> <title> Charts from Pandas </title> </header>
    <style>
    .row {
  display: flex;
  flex-wrap: wrap;
  padding: 0 4px;
}

/* Create four equal columns that sits next to each other */
.column {
  flex: 40%;
  max-width: 40%;
  padding: 0 4px;
}

.column img {
  margin-top: 8px;
  vertical-align: middle;
  width: 100%;
}

/* Responsive layout - makes a two column-layout instead of four columns */
@media screen and (max-width: 800px) {
  .column {
    flex: 40%;
    max-width: 40%;
  }
}

/* Responsive layout - makes the two columns stack on top of each other instead of next to each other */
@media screen and (max-width: 600px) {
  .column {
    flex: 100%;
    max-width: 100%;
  }
}
    }
    </style>
    <body>
    Here are some charts I made by myself.
    '''
    str = ''
    str += '<div class="row"<div class="column"><img src="abs_{0}.png" alt="absolute"></div></div>\n'.format(
        country)
    str += '<div class="row"><div class="column"><img src="vel_{0}.png" alt="velocity"></div>\n'.format(country)
    str += '<div class="column"><img src="acc_{0}.png" alt="acceleration"></div></div>\n'.format(country)
    footer = '''
    </body>
    </html>
    '''
    f.write(header + str + footer)
    f.close()

if __name__ == '__main__':
    test_deltas = 0
    if (test_deltas):
        test_deltas =  pd.DataFrame( {"a" : [4 ,5, 6],
                                      "b" : [7, 8, 9],
                                      "c" : [10, 11, 12]
                                      })
        print(test_deltas)
        create_deltas_dataframe(test_deltas)

    df = load_data()
    print(keep_only_data_columns(df))
    md_cols = get_only_metadata_columns(df)
    print("Calculating Velocity DF")
    velocity_df = create_deltas_dataframe(keep_only_data_columns(df))
    print("Calculating Accelaration DF")
    accelaration_df = create_deltas_dataframe(velocity_df)
    velocity_df = pd.concat([md_cols, velocity_df], axis=1)
    accelaration_df = pd.concat([md_cols, accelaration_df], axis=1)

    country = 'Israel'
    if (len(sys.argv) >= 2):
        country = sys.argv[1]

    chart_type = None
    if (len(sys.argv) >= 3):
        chart_type = sys.argv[2]

    if (chart_type is None or chart_type == "abs"):
        title = 'Total infected COVID-19 over time in {0}'.format(country)
        # Graph the absolute numbers:
        chart_country_data(df, country, title, 'abs_{0}'.format(country))
        #title += '\nAverage infected per day in {0} is {1} '.format(country, speed)
    if (chart_type is None or chart_type == "vel"):
        title = 'Velocity: Infection rate over time of COVID-19 in {0}'.format(country)
        # Graph the velocity:
        chart_country_data(velocity_df, country, title, 'vel_{0}'.format(country))
    if (chart_type is None or chart_type == "acc"):
        title = 'Acceleration: Change in infection rate over time of COVID-19 in {0}'.format(country)
        # Graph the accelaration:
        chart_country_data(accelaration_df, country, title, 'acc_{0}'.format(country))
    write_html(country)
    print("DONE :-)")
