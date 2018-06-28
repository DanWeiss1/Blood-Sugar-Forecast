# Blood Sugar Forecasting 

**tl;dr:** I used AR models on 3 months of blood sugar data taken from my Dexcom Continuous Glucose Monitor in order to forecast my blood sugar 15 minutes into the future.

I then serve those predictions in a Flask Web App which also allows me to dynamically view historical data and view live predictions.   

## Quick start

The modeling and graphics are generated from the appropriately named 'Modeling and Charts.py'

to run the Flask App on your local computer, you will need to run __init__.py
However, you will first need to follow the Dexcom API instructions here (https://developer.dexcom.com/getting-started) to set up an app and get user data.  then you will need to create conf.yaml following the structure of the template file conf.yaml.template with your own api key, id
and user access tokens


### Python Environment
Python code in this repo utilizes packages that are not part of the common library. To make sure you have all of the 
appropriate packages, please install [Anaconda](https://www.continuum.io/downloads)

Additonally you should pip install bokeh and flask to run the flask app
