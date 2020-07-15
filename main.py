import flask
from flask import Flask, render_template,url_for,request,send_file
import pandas as pd
import matplotlib.pyplot as plt
import csv
import flask_mysqldb
from flask_mysqldb import MySQL
import yaml
import plotly
import plotly.express as px
import plotly.graph_objects as obj
import dash             
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

server = Flask(__name__)
mysql = MySQL(server)


app1 = dash.Dash(__name__,server=server,url_base_pathname='/tweets/' )
data = pd.read_csv('corona_tweets_01.csv')
fig1=obj.Figure(obj.Scattergl(x=data['tweet_id'][0:2000],
	y=data['sentiment'][0:2000],
	mode = 'markers'))

fig2 = obj.Figure(obj.Scattergl(x=data['tweet_id'][2000:10000],
	y=data['sentiment'][2000:10000],
	mode = 'markers'))

fig3=obj.Figure(obj.Scattergl(x=data['tweet_id'][10000:40000],
	y=data['sentiment'][10000:40000],
	mode = 'markers'))

app1.layout = html.Div(children = [
    html.H1(children = 'Analysis of covid-19 first 2000 tweets'), html.Hr(),
    dcc.Graph(
    	figure=fig1),
    html.H1(children = 'Analysis of covid-19 next 10000 tweets'), html.Hr(),
    dcc.Graph(
    	figure=fig2),
    html.H1(children = 'Analysis of covid-19 next 40000 tweets'), html.Hr(),
    dcc.Graph(
    	figure=fig3)
])

app = dash.Dash(__name__,server=server,url_base_pathname='/dashboard/')
file = pd.read_csv('responsesoflockdown.csv')
app.layout = html.Div([
html.Div([
    html.H1("Showing the dashboard on lockdown response collected from all over the India."),
        html.H2("You can choose from the below options"),html.Hr(),
        dcc.Graph(id='our_graph')
    ],className='nine columns'),
    html.Div([
        
    html.Br(),
    html.Div(id='output_data'),
    html.Br(),

    html.Label(['Choose column:'],style={'font-weight': 'bold', "text-align": "center"}),

    dcc.Dropdown(id='my_dropdown',
        options = [
                    {'label' : 'Uttar Pradesh', 'value' : 'Uttar Pradesh' },
                    {'label' : 'Madhya Pradesh', 'value' : 'Madhya Pradesh' },
                    {'label' : 'Andhra Pradesh', 'value' : 'Andhra Pradesh' },
                    {'label' : 'Assam', 'value' : 'Assam' },
                    {'label' : 'Delhi', 'value' : 'Delhi' },
                    {'label' : 'Karnataka', 'value' : 'Karnataka' },
                    {'label' : 'West Bengal', 'value' : 'West Bengal' },
                    {'label' : 'Telangana', 'value' : 'Telangana' },
                    {'label' : 'Tamil Nadu', 'value' : 'Tamil Nadu' },
                    {'label' : 'Bihar', 'value' : 'Bihar' },
                    {'label' : 'Kerela', 'value' : 'Kerela' },
                    {'label' : 'Jharkhand', 'value' : 'Jharkhand' },
                    {'label' : 'Rajasthan', 'value' : 'Rajasthan' },
                    {'label' : 'Pondicherry', 'value' : 'Pondicherry' },
                    {'label' : 'Maharashtra', 'value' : 'Maharashtra' },
                    {'label' : 'Gujarat', 'value' : 'Gujarat' },
                    {'label' : 'Haryana', 'value' : 'Haryana' },
                    ],
                    optionHeight=35,
                    value = 'Uttar Pradesh',
                    searchable=True,
                    placeholder='Please select...',     
                    clearable=True,
                    style={'width':"100%"},
                ),                                  
                                              
        ],className='three columns'),
    ])

@app.callback(
    Output(component_id='our_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')]
)             
def build_graph(column_chosen):
    df=file
    fig =px.pie(df,names=column_chosen)
    return fig

@app.callback(
    Output(component_id='output_data', component_property='children'),
    [Input(component_id='my_dropdown', component_property='search_value')]
)

def build_graph(data_chosen):
    return ('Search value was: " {} "'.format(data_chosen))


db = yaml.load(open('db.yaml'))
server.config['MYSQL_HOST'] = db['mysql_host']
server.config['MYSQL_USER'] = db['mysql_user']
server.config['MYSQL_PASSWORD'] = db['mysql_password']
server.config['MYSQL_DB'] = db['mysql_db']


@server.route('/')
def home():
    return render_template('home.html')

@server.route('/Save',methods=['GET','POST'])
def Save():
    if request.method =='POST':
        comment = request.form['comment']
        data = comment
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO sentiment(comment) VALUES(%s)",[data])
        mysql.connection.commit()
        cur.execute("select * from sentiment")
        responses = cur.fetchall()
        d={}
        for i in responses:
            d[i] = responses.count(i)
        for key,value in d.items():
            if(value == max(d.values())):
                print(key)
        cur.close()
        f=open("out.txt","a")
        f.write("\n")
        f.write(data)
        f.close()
    return render_template('home.html')

@server.route('/contact', methods=['GET','POST'])
def contact():
    if request.method =='POST':
        name=request.form['comment1']
        email=request.form['comment2']
        suggestion=request.form['comment3']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO contact(name,email,suggestion) VALUES(%s,%s,%s)",[name,email,suggestion])
        mysql.connection.commit()
        cur.execute("select * from contact")
        
    return render_template('home.html')



@server.route('/Predict')
def Predict():
    cur = mysql.connection.cursor()
    cur.execute("select * from sentiment")
    responses = cur.fetchall()
    d={}
    for i in responses:
        d[i] = responses.count(i)
    for key,value in d.items():
        if(value == max(d.values())):
            result = key
    """html = ''
    for i in key:
        html+= '<h2>key :' + i+ '</br>'"""
    cur.close()
    return render_template('predict.html',output = result)
    

@server.route('/Open')
def Open():
    file = pd.read_csv('corona_tweets_01.csv')
    sentiment = file['sentiment']
    anger = [];fear=[];sadness = [];neu = [];surprise = [];trust =[];joy=[]
    for i in sentiment:
	    if(-0.33<=i<=-0.1):
		    anger.append(i)
	    elif(-0.66<=i<=-0.34):
		    fear.append(i)
	    elif(-0.99<=i<=-0.67):
		    sadness.append(i)
	    elif(0.01<=i<=0.33):
		    surprise.append(i)
	    elif(0.34<=i<=0.66):
		    trust.append(i)
	    elif(0.67<=i<=1):
		    joy.append(i)
	    else:
		    neu.append(i)
    plt.title('sentiment analysis based on people tweets')
    y1=[len(anger),len(fear), len(sadness),len(neu),len(surprise),len(trust),len(joy)]
    x1=['anger','fear','sadness','neutral','surprise','trust','joy']
    plt.bar(x1,y1,color='blue')

    for i,num in enumerate(y1):
	    plt.text(i,num+100,num,ha='center',fontsize=10)
    return send_file('Figure_1-1.png')

@server.route('/dashboard')
def dashboard():
    return flask.redirect('/dashboard')

@server.route('/tweets')
def tweets():
    return flask.redirect('/tweets')

@server.route('/Post')
def Post():
    return render_template('postlife.html')
    
@server.route('/Pre')
def Pre():
    return render_template('prelife.html')

if __name__=='__main__':
    server.run(debug = True, port=8080)
