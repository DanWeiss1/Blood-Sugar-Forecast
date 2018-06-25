import datetime

from bokeh.embed import components
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template

import pandas as pd

from api_post import api_post, get_data
from history_boxplot import boxplot, make_dataset, api_pull
from forecastchart import forecast_plot, make_future

now = datetime.datetime.now()

def cutoff(i):
    return (now - datetime.timedelta(days= int(i))).strftime("%Y-%m-%dT%H:%M:%S")


app = Flask(__name__)

df = api_pull()

@app.route("/")
def home_page():
    return(render_template('home_page.html'))
    
@app.route("/history")
def history():
    
    plot_data = make_dataset(df)    
    script, div = components(boxplot(plot_data, df))
    return render_template("past.html", the_div=div, the_script=script)

@app.route("/history", methods=['GET','POST'])
def history_post():
    start_date = datetime.datetime.strptime(request.form['start'], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(request.form['end'],"%Y-%m-%d") + datetime.timedelta(days= 1)
    date_df = df.loc[(df['displayTime']>= start_date) & (df['displayTime']<= end_date)]    
    plot_data = make_dataset(df,start_date.strftime("%Y-%m-%dT%H:%M:%S"),end_date.strftime("%Y-%m-%dT%H:%M:%S"))
    script, div = components(boxplot(plot_data, date_df))
    return render_template("past.html", the_div=div, the_script=script)
    
 
@app.route("/forecast")
def show_forecast():
    future_df = make_future(df)
    script, div = components(forecast_plot(future_df))
    return render_template("future.html", the_div=div, the_script=script)
    
    
    
    
if __name__ == "__main__":
    app.run(debug=True)