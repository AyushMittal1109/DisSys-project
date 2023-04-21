from flask import Flask, request
import json
from random import sample,choice
import requests

app = Flask(__name__)


# new process id always increasing
new_node_id = 0

random_node_count = 2

# node and their addresses
alive_node_address = {}


# graph representation 
# graph[i] = set(a,b,c) - node i is connected with node a,b,c
graph = {}

@app.route('/')
def entry_point():
    return 'Hello World!'

@app.route('/initializeMe',methods = ['POST','GET'])
def initializeMe():
    
    global new_node_id

    new_node_data = request.json

    ip = new_node_data['ip']
    port = new_node_data['port']


    # choose any two nodes
    try:
        random_selected_nodes = sample(list(alive_node_address.keys()),random_node_count)
    except:
        random_selected_nodes = list(alive_node_address.keys())


    # random_selected_nodes
    # adding node to alive nodes

    given_id = str(new_node_id)
    new_node_id += 1
    alive_node_address[given_id] = {'ip':ip,
                                 'port':port}
    
    # telling node a,b to take responsibility of node i
    for node in random_selected_nodes:
        url = f'http://{alive_node_address[node]["ip"]}:{alive_node_address[node]["port"]}/takeResponsibility'
        data = {
            'id':given_id,
            'ip':ip,
            'port':port,
        }
        x = requests.post(url,json = data)


    # make changes in map
    graph[given_id]=set(random_selected_nodes)
    for node in random_selected_nodes:
        graph[node].add(given_id)

    # to send whole database and nodes a,b

    print(graph)

    toSend = {'database':alive_node_address,'responsibility':random_selected_nodes, 'node_id':given_id}
    
    
    return json.dumps(toSend)


@app.route('/node_x_failed',methods = ['POST','GET'])
def nodeFailed():
    failed_node_data = request.json
    node_id = failed_node_data['node_id']

    # manage responsibility taken by failed node
    try:
        del alive_node_address[node_id]
    except:
        return 'ok'



    # remove failed node from db
    print("monty",graph)
    print("am",graph[node_id])

    for x in graph[node_id]:
        graph[x].remove(node_id)
        print(graph)
        
        
        # check if one responsible then make more responsible
        if len(graph[x]) == 1 and len(graph.keys())>3:
            # find any random node and make them responsible for each other

            a = choice(list(alive_node_address.keys()))
            
            while a == x or a == node_id or (a in graph[x]):
                print(type(a),type(x),type(node_id),a,x,node_id)
                a = choice(list(alive_node_address.keys()))
            print(type(a),type(x),type(node_id),a,x,node_id)
            # give responsiblity of atoi and vice versa
            url = f'http://{alive_node_address[a]["ip"]}:{alive_node_address[a]["port"]}/takeResponsibility'
            data = {
                'id':x,
                'ip':alive_node_address[x]["ip"],
                'port':alive_node_address[x]["port"],
            }
            print("3")

            try:
                res = requests.post(url,json = data)
            except:
                print(f'node {alive_node_address[x]["ip"]}:{alive_node_address[x]["port"]} is failed or some error occured : cannot connect')


            url = f'http://{alive_node_address[x]["ip"]}:{alive_node_address[x]["port"]}/takeResponsibility'
            data = {
                'id':a,
                'ip':alive_node_address[a]["ip"],
                'port':alive_node_address[a]["port"],
            }
            print("4")

            graph[x].add(a)
            graph[a].add(x)
            

            try:
                res = requests.post(url,json = data)
            except:
                print(f'node {alive_node_address[x]["ip"]}:{alive_node_address[x]["port"]} is failed or some error occured : cannot connect')

    del graph[node_id]
    

    return "ok"



if __name__ == '__main__':
    print("ayush")
    app.run(debug=False, port=8000)