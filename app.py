from flask import Flask, render_template, request, redirect
import requests
import numpy as np
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components

quandl_api_url = 'https://www.quandl.com/api/v3/datasets'
quandl_api_key = 'Not8oPTG5Zsa7RSB5KJM'

def get_script_div(dataset_code,options):
    
    #get json data
    format_str = 'json'
    database_code = 'WIKI'
    address = "{0}/{1}/{2}.{3}?api_key={4}".format(quandl_api_url, database_code, dataset_code, format_str, quandl_api_key)
    r = requests.get(address)
    json_data = r.text
    
    #convert to pandas dataframe
    import pandas as pd
    df = pd.read_json(json_data)
    col_names = df.ix['column_names'][0]
    data_points = pd.read_json(json_data).ix['data'][0]
    stock_data = pd.DataFrame(data_points, columns = col_names)
    
    #auxiliary data
    start_date = df.ix['start_date']
    end_date = df.ix['end_date']
    freq = df.ix['frequency']
    name = df.ix['name'][0]
    stock_code = df.ix['dataset_code'][0]
    
    #generate bokeh plot
    def datetime(x):
        return np.array(x, dtype=np.datetime64)
    
    p = figure(x_axis_type = "datetime")
    p.title = "QUANDL Stock price data"
    p.grid.grid_line_alpha=0.3
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    
    colours = ['red','blue','green','orange']
    for ctr, option in enumerate(options.values()):    
        p.line(datetime(stock_data['Date']), stock_data[option], legend='{0}: {1}'.format(dataset_code,option), color = colours[ctr])

    script, div = components(p)
    
    return script, div
    

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  return render_template('index.html')
  
@app.route('/plot', methods = ['GET','POST'])
def plot():
  form = request.form
  dataset_code = form['dataset_code']
  options = {key: val for key, val in form.items() if key != 'dataset_code'}
  
  script, div = get_script_div(dataset_code, options) 
  return render_template('plot.html', script = script, div = div, dataset_code = dataset_code)

if __name__ == '__main__':
  app.run(port=33507)
