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

    # ip = request.remote_addr
    # port = str(request.environ['REMOTE_PORT'])

    ip = request.args.get("ip")
    port = request.args.get("port")

    # choose any two nodes
    try:
        random_selected_nodes = sample(list(alive_node_address.keys()),random_node_count)
    except:
        random_selected_nodes = list(alive_node_address.keys())

    print(random_selected_nodes)
    # random_selected_nodes
    # adding node to alive nodes
    alive_node_address[new_node_id] = {'ip':ip,
                                 'port':port}
    new_node_id += 1

    # telling node a,b to take responsiblity of node i
    for node in random_selected_nodes:
        url = f'{alive_node_address[node]["ip"]}:{alive_node_address[node]["port"]}/takeResponsiblity'
        data = {
            'id':new_node_id-1,
            'ip':ip,
            'port':port,
        }
        x = requests.post(url,json = data)


    # make changes in map
    graph[new_node_id-1]=set(random_selected_nodes)
    for node in random_selected_nodes:
        graph[node].add(new_node_id-1)

    # to send whole database and nodes a,b

    toSend = {'database':alive_node_address,'responsiblity':random_selected_nodes}

    return json.dumps(toSend)


@app.route('/nodeFailed',methods = ['POST','GET'])
def nodeFailed():
    failed_node_data = request.json
    node_id = failed_node_data['id']

    # manage responsiblity taken by failed node



    # remove failed node from db
    for x in graph[node_id]:
        graph[x].remove(node_id)
        # check if one responsible then make more responsible
        if len(graph[x]) == 1 and len(graph.keys())>1:
            # find any random node and make them responsible for each other
            a = choice(alive_node_address.keys())
            while a == x:
                a = choice(alive_node_address.keys())

            # give responsiblity of atoi and vice versa
            url = f'{alive_node_address[a]["ip"]}:{alive_node_address[a]["port"]}/takeResponsiblity'
            data = {
                'id':node_id,
                'ip':alive_node_address[node_id]["ip"],
                'port':alive_node_address[node_id]["port"],
            }
            x = requests.post(url,json = data)

            url = f'{alive_node_address[node_id]["ip"]}:{alive_node_address[node_id]["port"]}/takeResponsiblity'
            data = {
                'id':a,
                'ip':alive_node_address[a]["ip"],
                'port':alive_node_address[a]["port"],
            }
            graph[node_id].add(a)
            graph[a].add(node_id)
            


            x = requests.post(url,json = data)

    del graph[node_id]
    del alive_node_address[node_id]






    return "ok"



if __name__ == '__main__':
    print("ayush")
    app.run(debug=True, port=8000)