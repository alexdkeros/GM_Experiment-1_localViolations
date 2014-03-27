'''
@author: ak
'''
import threading
import random
from blinker import signal
from GM_localViolations.Node import Node
from GM_localViolations import Config

class Coordinator:
    '''
    class Coordinator
    models the Coordinator at a Geometric Monitoring network
    configuration via Config module
    '''


    def __init__(self, event, nodeNum):
        '''
        Constructor
        args:
            event: synchronizing event
            nodes: a node object list
        '''
        #thread configuration-synchronization
        self.event=event
        
        #coordinator data initialization
        self.nodeNum=nodeNum    #network node number
        self.nodes={}   #network node dictionary{key is nodeId:value is weight}
        self.thresh=Config.threshold    #monitoring threshold
        self.v=0    #global statistics vector
        self.e=0    #estimate vector
        self.balancingSet=set() #balancing set (set of tuples) (nodeId,v_value,u_value})
        self.balancingNodeIdSet=set() #balancing set containing only nodeIds
        self.b=0    #balancing vector
        
        #helper
        self.counter=0
        
        #signal configuration
        signal('start').connect(self.start)
        signal('init-node').connect(self.init)
        signal('rep').connect(self.nodeRep)
        
    
    '''
    signal handlers
    '''
    def init(self,nodeId,**kargs):
        '''
        initialising global data
        '''
        self.counter+=1
        
        #populating network dictionary
        self.nodes[nodeId]=kargs['w']
        self.v+=(kargs['w']*kargs['v'])/sum(self.nodes.values())
        self.e=self.v
        #when all data collected, new-est signal
        if self.counter==len(self.nodes):
            signal('new-est').send(newE=self.e)
            
    def nodeRep(self, nodeId, **kargs):
        '''
        new local violation occured
        data tuple is (nodeId, v, u)
        '''
        #pause thread execution
        self.event.clear()

        #add node to balancing set
        self.balancingSet.add((nodeId,kargs['v'],kargs['u']))
        self.balancingNodeIdSet.add(nodeId)
        
        #balancing vector computation
        sw=0
        for s in self.balancingSet:
            self.b+=self.nodes[s[0]]*s[2]   #Sum(w_i*u_i)
            sw+=self.nodes[s[0]]    #Sum(w_i)
        self.b=self.b/sw
        
        if self.b>=self.thresh:
            #pick node to balance at random
            diffSet=set(self.nodes)-self.balancingNodeIdSet
            if len(diffSet):
                signal('req').send(nodeId=random.sample(diffSet,1))
            else:
                signal('global-violation').send()
        else:
            #successful balance
            for s in self.balancingSet:
                dDelta=(self.nodes[s[0]]*self.b)-(self.nodes[s[0]]*s[2])
                signal('adj-slk').send(nodeId=s[0],dDelta=dDelta)
            
            #empty balancing set
            self.balancingSet.clear()
            self.balancingNodeIdSet.clear()
            self.b=0
            #resume
            self.event.set()    
                
                
    def start(self,sender):
        '''
        starting execution
        '''
        self.event.clear()
        signal('init').send()
        #start
        self.event.set()
        
        
        
        
        
    