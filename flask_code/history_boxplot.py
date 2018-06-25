import datetime

from bokeh.plotting import figure, output_file
from bokeh.layouts import WidgetBox
from bokeh.models import Legend, ColumnDataSource, Span

import numpy as np
import pandas as pd


from api_post import api_post, get_data
import lib 

now = datetime.datetime.now() + datetime.timedelta(hours=7)
end_date_str = now.strftime("%Y-%m-%dT%H:%M:%S")
start_date = now - datetime.timedelta(days=90)
start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")

code = lib.get_conf('refresh_code')

def api_pull(start_date=start_date_str,end_date=end_date_str):
    data = get_data(eval(api_post(code,refresh=True).\
            decode('utf-8'))['access_token'],start_date,end_date)
    new = data.decode('utf-8')
    new = new.replace('null','None')
    df = pd.DataFrame(eval(new)['egvs'])
    
    df['displayTime'] = pd.to_datetime(df['displayTime'])
    df = df[['displayTime','value']]
    #df.append(df_older, ignore_index=True)
    return df

def make_dataset(df,start_date=start_date,end_date=now):
    df = df.loc[(df['displayTime']>=start_date) & (df['displayTime']<=end_date)]
    df['hour'] = df['displayTime'].dt.hour.astype(str) + ":00"
    df2 = df[['hour','value']]
    df2.rename(mapper={'value':'bsugar'},axis=1,inplace=True)
    g = pd.DataFrame(df2.groupby('hour').quantile(0.05))
    g.rename(mapper={'bsugar': 'bsugar005'}, inplace=True, axis=1)
    for val in [0.25,0.5,0.75,0.95]:
        g['bsugar' + str(val).replace('.','')] = df2.groupby('hour').quantile(val)
    g.reset_index(inplace=True)
    return ColumnDataSource(g)
def dateRange(data):
    begin = data['displayTime'].dt.date.min()
    end = data['displayTime'].dt.date.max()
    return begin.strftime("%m-%d-%Y"), end.strftime("%m-%d-%Y")
def boxplot(data, df):
    cats = [str(x) + ":00" for x in range(24)]
    
    p = figure(title= 'Blood Sugar by Hour from ' + dateRange(df)[0] + " to " + dateRange(df)[1], tools=["save"], 
        background_fill_color="#EFE8E2", x_range=cats, width=1325, height=650)
    
    # stems
    r0 = p.segment('hour', 'bsugar005', 'hour', 'bsugar025', line_color="Blue",line_width = 1.5, source=data)
    
    # boxes
    r1 = p.vbar(x='hour',width= 0.7, bottom='bsugar025', top='bsugar05', fill_color="#3B8686", line_color="black", source=data)
    r2 = p.vbar(x='hour',width= 0.7, bottom='bsugar05',top='bsugar075', fill_color="#E08E79", line_color="black", source=data)
     
    r3 = p.segment('hour', 'bsugar095', 'hour', 'bsugar075', line_color="Red",line_width = 1.5, source=data)
   
    # whiskers (almost-0 height rects simpler than segments)
    p.rect('hour', 'bsugar005', 0.2, 0.01, line_color="black", source=data)
    p.rect('hour', 'bsugar095', 0.2, 0.01, line_color="black", source = data)
    
    # add boundaries
    hline1 = Span(location=80, dimension='width', line_color='black', line_width=2)
    hline2 = Span(location=180, dimension='width', line_color='black', line_width=2)
    
    #legend location
    legend = Legend(items=[('5th to 25th Percentile',[r0]),
    ('25th to 50th Percentile', [r1]),
    ('50th to 75th Percentile', [r2]),
    ('75th to 95th Percentile', [r3])] ,location=(0,400))
    p.add_layout(legend,'right')
    
    p.renderers.extend([hline1,hline2])
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = "white"
    p.grid.grid_line_width = 2
    p.xaxis.major_label_text_font_size="12pt"
    p.yaxis.major_label_text_font_size="12pt"
    p.xaxis.axis_label = 'Hour of Day'

    p.yaxis.axis_label = 'mg/dL'
    p.xaxis.axis_label_text_font_size = "14pt"

    p.yaxis.axis_label_text_font_size = "14pt"
    
    return p
