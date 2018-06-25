import datetime

from bokeh.plotting import figure
from bokeh.layouts import WidgetBox
from bokeh.models import Range1d, ColumnDataSource, Span

import numpy as np
import pandas as pd

ar1 = 1.1302381703714106
ar2 = 0.16085155846011429
ar3 = -0.307735412458097
constant = 0.6722152278755241

def make_future(data):
    last_timestamp = data['displayTime'].max()
    time_limit = last_timestamp - datetime.timedelta(hours=2)
    chart_data = data.loc[data['displayTime']>=time_limit][['displayTime','value']]
    chart_data['historical'] = 1
    chart_data.sort_values(by='displayTime',inplace=True)
    for i in [24,25,26]:
        chart_data.loc[i] = 0
        chart_data.at[i,'displayTime'] = chart_data.iloc[i-1]['displayTime'] + datetime.timedelta(minutes=5)
        chart_data.at[i,'value'] = constant + chart_data.iloc[i-1]['value'] * ar1 + chart_data.iloc[i-1]['value'] * ar2 + chart_data.iloc[i-3]['value'] * ar3
    chart_data['forecast'] = np.where(chart_data['historical'] == 0, chart_data['value'], np.NaN)
    chart_data['value'] = np.where(chart_data['historical'] == 1, chart_data['value'], np.NaN)
    chart_data['forecast_lower'] = np.NAN
    chart_data['forecast_upper'] = np.NAN
    for i, loc in enumerate([24,25,26]):
        chart_data.at[loc,'forecast_lower'] = chart_data.loc[loc]['forecast'] - 4.5 * (i+1)
        chart_data.at[loc,'forecast_upper'] = chart_data.loc[loc]['forecast'] + 4.5 * (i+1)
   
    chart_data['Time'] = chart_data['displayTime'].dt.time
    return chart_data

def forecast_plot(data): 
    last_timestamp = data['displayTime'].dt.time.max()
    last_timestamp = last_timestamp.strftime('%H:%M')
    day =  data['displayTime'].dt.date.max()
    day = day.strftime('%m/%d/%Y')
    source = ColumnDataSource(data)
    
    
    p = figure(title= 'Blood Sugar Forecast at ' + last_timestamp + ' on ' + day, tools=["save"], 
        background_fill_color="#A9A9A9", width=1250, height=600, x_axis_type='datetime')
    p.title.text_font_size = "25px"
    p.title.align = "center"
    p.circle('displayTime','value',source=source,size=15, color="black", alpha=0.5, legend = 'Historical Values')
    p.circle('displayTime','forecast',source=source,size=15, color="green", alpha=0.5, legend = 'Forecast Values')
    p.circle('displayTime','forecast_lower',source=source,size=15, color="red", alpha=0.5, legend = 'Lower Bound')
    p.circle('displayTime','forecast_upper',source=source,size=15, color="blue", alpha=0.5, legend = 'Upper Bound')
    
    # add boundaries
    hline1 = Span(location=80, dimension='width', line_color='black', line_width=2)
    hline2 = Span(location=180, dimension='width', line_color='black', line_width=2)
    p.renderers.extend([hline1,hline2])
    
    p.xaxis.axis_label = 'Hour of Day'

    p.yaxis.axis_label = 'mg/dL'
    p.xaxis.axis_label_text_font_size = "14pt"
    
    x_min = data['displayTime'].min() - datetime.timedelta(minutes=2)
    x_max = data['displayTime'].max() + datetime.timedelta(minutes=2)
    p.yaxis.axis_label_text_font_size = "14pt"
    p.y_range = Range1d(20,400) 
    p.x_range = Range1d(x_min, x_max)
    return p
    
 

