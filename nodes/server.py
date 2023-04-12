from flask import Flask, request
import json
from random import sample,choice
import requests

app = Flask(__name__)

alive_node_address = {}
responsibleFor = {}


@app.route('/')
def entry_point():
    return 'Hello World!'

@app.route('/takeResponsiblity', methods = ['POST','GET'])
def takeResponsiblity():

    node_data = request.json
    node_id = node_data['id']
    node_ip = node_data['ip']
    node_port = node_data['port']

    responsibleFor[node_id] = {'ip':node_ip,'port':node_port}

    return 'ok'

def 





if __name__ == '__main__':
    print("ayush")
    app.run(debug=True, port=8001)