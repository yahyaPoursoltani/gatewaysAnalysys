#!/usr/bin/env python
# coding: utf-8

# # Parse BPMN File to Networkx Graph
# Yahya Poursoltani

# In[1]:


#pip install SpiffWorkflow --user


# In[2]:


#pip install Networkx --user


# # XML Parser : List of Tasks

# In[3]:


import networkx as nx
from xml.dom import minidom
data = minidom.parse("Models/ex05.bpmn");
process_graph= nx.MultiDiGraph()


# ## Gateways 

# ### extract gateways

# In[4]:


xors= data.getElementsByTagName('exclusiveGateway')
ors= data.getElementsByTagName('inclusiveGateway')
parallels= data.getElementsByTagName('parallelGateway')


# ### create gateways nodes

# In[5]:


for xor in xors:
    process_graph.add_node(str(xor.attributes['id'].value),
                         node_id= xor.attributes['id'].value,
                         node_type='xor_gateway')
for parallel in parallels:
    process_graph.add_node(str(parallel.attributes['id'].value),
                         node_id= parallel.attributes['id'].value,
                         node_type='parallel_gateway')

for inor in ors:
    process_graph.add_node(str(inor.attributes['id'].value,
                          node_id=inor.attributes['id'].value),
                          node_type='or_gateway')
      


# ## Events

# ### extract events

# In[6]:


intermediate_events_thrown= data.getElementsByTagName('intermediateThrowEvent')
intermediate_events_catched= data.getElementsByTagName('intermediateCatchEvent')
startEvents= data.getElementsByTagName('startEvent')
endEvents= data.getElementsByTagName('endEvent')
intermediate_events= intermediate_events_catched+intermediate_events_thrown


# ### create event nodes

# In[7]:


for se in startEvents:
    process_graph.add_node(str(se.attributes['id'].value),
                         node_id= se.attributes['id'].value,
                         node_type='start_event')


for inter in intermediate_events:
    process_graph.add_node(str(inter.attributes['id'].value),
                              node_id=inter.attributes['id'].value,
                          node_type='intermediate_gateway')
    
for ee in endEvents:
    process_graph.add_node(str(ee.attributes['id'].value),
                         node_id= ee.attributes['id'].value,
                         node_type='end_event')


# ## Activities

# ### extract activities

# In[8]:


tasks= data.getElementsByTagName('task')
user_tasks= data.getElementsByTagName('userTask')
service_tasks= data.getElementsByTagName('serviceTask')
send_tasks= data.getElementsByTagName('sendTask')
script_tasks= data.getElementsByTagName('scriptTask')
manual_tasks= data.getElementsByTagName('manualTask')
business_rule_tasks= data.getElementsByTagName('businessRuleTask')


# In[9]:


activities = tasks+user_tasks+service_tasks+send_tasks+script_tasks+manual_tasks+business_rule_tasks
boundry_tasks=[]


# ### Handling Boundry events

# In[10]:


for task in activities:
    process_graph.add_node(str(task.attributes['id'].value),
                         node_id= task.attributes['id'].value,
                         node_lable=task.attributes['name'].value,
                         node_type='activity')


# In[11]:


boundry_events= data.getElementsByTagName('boundaryEvent')
boundry_event_id=[]
for be in boundry_events:
    if process_graph.has_node(be.attributes['attachedToRef'].value):
        process_graph.remove_node(be.attributes['attachedToRef'].value)
        
    process_graph.add_node(str(be.attributes['attachedToRef'].value),
                         node_id= be.attributes['id'].value,
                         task_id=be.attributes['attachedToRef'].value,
                         node_type='boundry_activity')
    boundry_event_id.append(be.attributes['id'].value)


# In[12]:


for be in endEvents:
    process_graph.add_node(str(ee.attributes['id'].value),
                         node_id= ee.attributes['id'].value,
                         node_type='end_event')
list(process_graph.nodes(data=True))


# # List of Arcs

# In[13]:


arcs= data.getElementsByTagName("sequenceFlow")
edges=[]


# In[14]:


for arc in arcs:
    #print('id:',arc.attributes['id'].value)
    source = arc.attributes['sourceRef'].value
    target = arc.attributes['targetRef'].value
    edges.append((source,target))
    
for edge in edges:
    print(edge)


# In[15]:


process_graph.add_edges_from(edges)


# # Draw Graph

# In[16]:


def draw_process_graph(processGraph):
    nodes_color_map=[]
    for node in list(processGraph.nodes):
        if processGraph.nodes[node]["node_type"]== "activity":
            nodes_color_map.append("blue")
        elif processGraph.nodes[node]["node_type"]== "boundry_activity":
            nodes_color_map.append("orange")
        elif processGraph.nodes[node]["node_type"]== "parallel_gateway":
            nodes_color_map.append("red")
        elif processGraph.nodes[node]["node_type"]== "xor_gateway":
            nodes_color_map.append("green")
        elif processGraph.nodes[node]["node_type"]== "or_gateway":
            nodes_color_map.append("green")
        elif processGraph.nodes[node]["node_type"]== "intermediate_event":
            nodes_color_map.append("purple")
        elif processGraph.nodes[node]["node_type"]== "start_event":
            nodes_color_map.append("#c8f8cb")
        elif processGraph.nodes[node]["node_type"]== "end_event":
            nodes_color_map.append("#f1a2a2")
    nx.draw(processGraph,node_size=500,node_color=nodes_color_map,with_labels=False)
draw_process_graph(process_graph)


# # Basic Functions

# ## Check for and/or split/join

# In[17]:


def is_and_split(process_graph,node_id):
    has_this_node= node_id in process_graph
    is_and=False
    deg_state=False
    
    if process_graph.nodes[node_id]["node_type"] == "parallel_gateway":
        is_and=True
    
    if process_graph.in_degree(node_id) == 1 and process_graph.out_degree(node_id)>=1:
        deg_state=True
        
    return has_this_node and is_and and deg_state


# In[18]:


def is_and_join(process_graph,node_id):
    has_this_node= node_id in process_graph
    is_and=False
    deg_state=False
    
    if process_graph.nodes[node_id]["node_type"] == "parallel_gateway":
        is_and=True
    
    if process_graph.in_degree(node_id) >= 1 and process_graph.out_degree(node_id)==1:
        deg_state=True
        
    return has_this_node and is_and and deg_state


# In[19]:


def is_or_split(process_graph,node_id):
    has_this_node= node_id in process_graph
    is_or=False
    deg_state=False
    
    if process_graph.nodes[node_id]["node_type"] == "or_gateway" or process_graph.nodes[node_id]["node_type"] == "xor_gateway":
        is_or=True
    
    if process_graph.in_degree(node_id) == 1 and process_graph.out_degree(node_id)>=1:
        deg_state=True
        
    return has_this_node and is_or and deg_state


# In[20]:


def is_or_join(process_graph,node_id):
    has_this_node= node_id in process_graph
    is_or=False
    deg_state=False
    
    if process_graph.nodes[node_id]["node_type"] == "or_gateway" or process_graph.nodes[node_id]["node_type"] == "xor_gateway":
        is_or=True
    
    if process_graph.in_degree(node_id) >= 1 and process_graph.out_degree(node_id)==1:
        deg_state=True
        
    return has_this_node and is_or and deg_state


# In[21]:


def remove_and_reconnect(graph,node_id):
    reverse_graph = graph.reverse(copy= True)
    privious_nodes = list(reverse_graph.neighbors(node_id))
    next_nodes = list(graph.neighbors(node_id))
    for privious in privious_nodes:
        for next_node in next_nodes:
            graph.add_edge(privious,next_node)
    graph.remove_node(node_id)


# # Backward Analysis

# In[22]:


def remove_pattern_subgraph(graph, node_id_1, node_id_2):
    pattern_subgraph = graph.subgraph([node_id_1,node_id_2])
    reverse_graph = graph.reverse(copy= True)
    privious_nodes = list(reverse_graph.neighbors(node_id_1))
    next_nodes = list(graph.neighbors(node_id_2))
    for privious in privious_nodes:
        for next_node in next_nodes:
            graph.add_edge(privious,next_node)
    
    for edg in list(pattern_subgraph.edges):
        graph.remove_edge(edg[0],edg[1])
    for nod in list(pattern_subgraph.nodes):
        graph.remove_node(nod)
    return graph


# ## Pattern Detectors 

# ### OR- Patterns

# In[23]:


def is_or_pattern(processGraph,node_id_1,node_id_2):
    is_adj=False
    is_node_type_correct = False
    degree_condition=False
    is_in_cycle=False
    
    node1 = processGraph.nodes[node_id_1]
    node2 = processGraph.nodes[node_id_2]
    cycles= list(nx.simple_cycles(processGraph))
    
    for cycle in cycles:
        if (node_id_1 in cycle) and (node_id_2 in cycle) and (len(cycle)==2):
            is_in_cycle= True
    
    is_adj= (node_id_1,node_id_2) in list(processGraph.edges())
    is_node_type_correct= is_or_split(processGraph,node_id_1) and is_or_join(processGraph,node_id_2)
    degree_condition = (processGraph.out_degree(node_id_1)>1) and (processGraph.in_degree(node_id_2)>1) 
    return is_adj and is_node_type_correct and degree_condition and (not(is_in_cycle))


# In[24]:


def is_and_pattern(processGraph,node_id_1,node_id_2):
    is_adj=False
    is_node_type_correct = False
    degree_condition=False
    
    node1 = processGraph.nodes[node_id_1]
    node2 = processGraph.nodes[node_id_2]
    
    is_adj= (node_id_1,node_id_2) in list(processGraph.edges())
    is_node_type_correct= is_and_split(processGraph,node_id_1) and is_and_join(processGraph,node_id_2)
    degree_condition = (processGraph.out_degree(node_id_1)>=1) and (processGraph.in_degree(node_id_2)>=1)
    return is_adj and is_node_type_correct and degree_condition


# In[25]:


def is_iteration_pattern(processGraph,node_id_1,node_id_2):
    is_adj=False
    is_node_type_correct = False
    degree_condition=False
    is_in_cycle=False
    
    node1 = processGraph.nodes[node_id_1]
    node2 = processGraph.nodes[node_id_2]
    cycles= list(nx.simple_cycles(processGraph))
    
    for cycle in cycles:
        if (node_id_1 in cycle) and (node_id_2 in cycle) and (len(cycle)==2):
            is_in_cycle= True
    
    is_adj= (node_id_1,node_id_2) in list(processGraph.edges())
    is_node_type_correct= is_or_split(processGraph,node_id_1) and is_or_join(processGraph,node_id_2)
    degree_condition = (processGraph.out_degree(node_id_1)>1) and (processGraph.in_degree(node_id_2)>1) 
    return is_adj and is_node_type_correct and degree_condition and is_in_cycle


# ## extract patterns

# ### OR-Patterns

# In[26]:


def get_or_patterns(processGraph):
    or_patterns_pairs=[]
    for node in list(processGraph.nodes):
        if is_or_split(processGraph,node):
            next_nodes=list(processGraph.neighbors(node))
            for next_node in next_nodes:
                if is_or_pattern(processGraph,node, next_node):
                    or_patterns_pairs.append((node,next_node))
    return or_patterns_pairs


# In[27]:


def remove_or_patterns(processGraph,or_patterns_pairs):
    for or_pattern in or_patterns_pairs:
        common_degree= processGraph.number_of_edges(or_pattern[0],or_pattern[1])
        outer_split_degree= processGraph.out_degree(or_pattern[0])
        inner_join_degree= processGraph.in_degree(or_pattern[1])
        if (common_degree<outer_split_degree) or (common_degree<inner_join_degree):
            processGraph.remove_edge(or_pattern[0],or_pattern[1])
        else:
            processGraph = remove_pattern_subgraph(processGraph,or_pattern[0],or_pattern[1])    
    return processGraph

# ### Iteration Pattern

# In[28]:


def get_iteration_patterns(processGraph):
    iteration_patterns_pairs=[]
    for node in list(processGraph.nodes):
        if is_or_split(processGraph,node):
            next_nodes=list(processGraph.neighbors(node))
            for next_node in next_nodes:
                if is_iteration_pattern(processGraph,node, next_node):
                    iteration_patterns_pairs.append((node,next_node))
    return iteration_patterns_pairs


# In[29]:


def remove_iteration_patterns(processGraph,iteration_patterns_pairs):
    for iteration_pattern in iteration_patterns_pairs:
        processGraph = remove_pattern_subgraph(processGraph,iteration_pattern[0],iteration_pattern[1])
    return processGraph


# ### And-Pattern

# In[30]:


def get_and_patterns(processGraph):
    and_patterns_pairs=[]
    for node in list(processGraph.nodes):
        if is_and_split(processGraph,node):
            next_nodes=list(processGraph.neighbors(node))
            for next_node in next_nodes:
                if is_and_pattern(processGraph,node, next_node):
                    and_patterns_pairs.append((node,next_node))
    return and_patterns_pairs


# In[31]:


def remove_and_patterns(processGraph,and_patterns_pairs):
    for and_pattern in and_patterns_pairs:
        common_degree= processGraph.number_of_edges(and_pattern[0],and_pattern[1])
        outer_split_degree= processGraph.out_degree(and_pattern[0])
        inner_join_degree= processGraph.in_degree(and_pattern[1])
        if (common_degree<outer_split_degree) or (common_degree<inner_join_degree):
            processGraph.remove_edge(and_pattern[0],and_pattern[1])
        else:
            processGraph = remove_pattern_subgraph(processGraph,and_pattern[0],and_pattern[1])
    return processGraph
    


# ## Backward Static Analysis

# In[32]:


list(process_graph.edges())


# In[33]:


def backward_analysis(processGraph):
    process= processGraph.copy(as_view=True)
    has_any_patterns = True
    i=1
    while(has_any_patterns):
        
        and_patterns = get_and_patterns(process)
        or_patterns = get_or_patterns(process)
        iteration_patterns= get_iteration_patterns(process)
        
        if len(and_patterns)>0:
            process = remove_and_patterns(processGraph,and_patterns)
        elif len(or_patterns)>0:
            process = remove_or_patterns(processGraph,and_patterns)
        elif len(iteration_patterns)>0:
            process = remove_iteration_patterns(processGraph,or_patterns)
        else:
            has_any_patterns=False
        i=i+1
    return process
    


# In[34]:


backward_analysis(process_graph)
draw_process_graph(process_graph)


# In[ ]:


process_graph.nodes


# In[ ]:


draw_process_graph(process_graph)


# In[ ]:


graph = nx.MultiDiGraph([(1,2),(1,3), (3,4),(1,3)])
nx.draw_networkx(graph)


# In[ ]:


source = 1
dest=3
commons=[]
all_common_start = list(graph.edges(source,dest))
for edge in all_common_start:
    if(edge[1] == dest):
        commons.append((source,dest))


# In[ ]:


commons


# In[ ]:




