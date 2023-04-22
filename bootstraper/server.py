from flask import Flask, request
import json
from random import sample,choice
import requests
from datetime import datetime

app = Flask(__name__)


# new process id always increasing
new_node_id = 0

random_node_count = 2

# node and their addresses
alive_node_address = {}


# graph representation 
# graph[i] = set(a,b,c) - node i is connected with node a,b,c
graph = {}

visited = set()
def dfs(u):
    visited.add(u)
    for node in graph[u]:
        if node not in visited:
            dfs(node)

def articulation_handler():

    dfs(list(alive_node_address.keys)[0])
    
    if len(visited) == len(alive_node_address):
        return []
    
    for node in alive_node_address.keys():
        if node not in visited:
            return [node, list(visited)[0]]



def log( m ):
    file = open("BS.log","a")
    date_str = str(datetime.now())
    t = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
    # curr_t = time.strftime("%H:%M:%S.%f",t)
    file.write(str(t)+ " " + m + "\n")
    file.close()

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
    log("INFO\tNEW NODE "+given_id+" "+ip+" "+port)

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
    print('updated graph is:')
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
        log("INFO\tNODE STOPPED "+node_id)
    except:
        return 'ok'

    visited.clear()
    a = articulation_handler()

    # remove failed node from db
    for x in graph[node_id]:
        graph[x].remove(node_id)
        
        
        # check if one responsible then make more responsible
        if len(graph[x]) == 1 and len(graph.keys())>3:
            # find any random node and make them responsible for each other

            a = choice(list(alive_node_address.keys()))
            
            while a == x or a == node_id or (a in graph[x]):
                a = choice(list(alive_node_address.keys()))
            # give responsiblity of atoi and vice versa
            url = f'http://{alive_node_address[a]["ip"]}:{alive_node_address[a]["port"]}/takeResponsibility'
            data = {
                'id':x,
                'ip':alive_node_address[x]["ip"],
                'port':alive_node_address[x]["port"],
            }

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

            graph[x].add(a)
            graph[a].add(x)
            

            try:
                res = requests.post(url,json = data)
            except:
                print(f'node {alive_node_address[x]["ip"]}:{alive_node_address[x]["port"]} is failed or some error occured : cannot connect')

    del graph[node_id]


    print('graph after deleting node',node_id)
    print(graph)
    return "ok"



if __name__ == '__main__':

    file = open("BS.log","w")
    file.close()
    app.run(debug=False, port=8000, host = "0.0.0.0")