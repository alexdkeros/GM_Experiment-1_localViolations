'''

@author: ak
'''
import networkx
import blinker
import threading
from GM_localViolations.Coordinator import Coordinator
from GM_localViolations.Node import Node
from GM_localViolations import Config

class GM:
    '''
        class GM
        models the Geometric Monitoring network
        configuration via Config module
    '''

    def __init__(self):
        '''
        Constructor
        '''
    
        #declaring event
        event=threading.Event()
        
        #creating nodes and coordinator
        self.nodes=[]
        for i in range(Config.nodeNum):
            self.nodes.append(Node(event))
        self.nodes.insert(0,Coordinator(event,self.nodes))
        self.coord=self.nodes[0]
        
        #creating star graph, coordinator is node[0]
        self.graph=networkx.Graph()
        self.graph.add_star(self.nodes)
        
        
        
if __name__=="__main__":
    GM()