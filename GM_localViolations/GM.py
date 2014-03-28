'''

@author: ak
'''
import sys
import networkx
import threading
import uuid
from blinker import signal
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
            self.nodes.append(Node(event,uuid.uuid4()))
        self.nodes.insert(0,Coordinator(event,len(self.nodes)))
        self.coord=self.nodes[0]
        
        #DBG
        print('nodes initialized')
        
        #creating star graph, coordinator is node[0]
        self.graph=networkx.Graph()
        self.graph.add_star(self.nodes)
        
        #DBG
        print('graph created')
        
        

        
    def start(self):
        print('starting threads')
        for n in self.nodes:
            n.start()
            
    def waitThreads(self):
        for n in self.nodes:
            n.join()
            
    def getLVs(self):
        print('------------------LVs:%d----------------------------'%self.coord.getLVs())
        
        
if __name__=="__main__":
    print('------------------Starting experiment---------------')
    gm=GM()
    gm.start()
    gm.waitThreads()
    gm.getLVs()