'''
@author: ak
'''
import threading
import time
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
        self.lock=threading.Lock()
        
        #coordinator data initialization
        self.nodeNum=nodeNum    #network node number
        self.nodes={}   #network node dictionary{key is nodeId:value is weight}
        self.thresh=Config.threshold    #monitoring threshold
        self.v=0    #global statistics vector
        self.e=0    #estimate vector
        self.balancingSet=set() #balancing set (set of tuples) (nodeId,v_value,u_value})
        self.balancingNodeIdSet=set() #balancing set containing only nodeIds
        self.balancingFlag=False    #balancing flag
        
        #helper
        self.counter=0
        
        #signal configuration
        signal('init-node').connect(self.init)
        signal('rep').connect(self.nodeRep)
        
        #experimental results
        self.expCounter=0
        
    
    '''
    signal handlers
    '''
    def init(self,nodeId,**kargs):
        '''
        initialising global data
        '''
        self.counter+=1
        #DBG
        print('coord:init signal received by node %s, counter is %d, nodeNum is %d'%(nodeId,self.counter, self.nodeNum))
        
        #populating network dictionary
        self.nodes[nodeId]=kargs['w']
        self.v+=(kargs['w']*kargs['v'])/sum(self.nodes.values())
        self.e=self.v
        #when all data collected, new-est signal
        if self.counter==self.nodeNum:
            #DBG
            print('coord: send new estimate')
            signal('new-est').send(newE=self.e)
            
    def nodeRep(self, nodeId, **kargs):
        '''
        new local violation occured
        '''
        #XXX maybe with lock: blah
        self.lock.acquire()
        
        #DBG
        print('coord:rep signal received by node %s, u=%0.2f'%(nodeId,kargs['u']))
        
        #pause thread execution
        self.event.clear()
        
        #DBG
        #time.sleep(4)
        

        #add node to balancing set
        self.balancingSet.add((nodeId,kargs['v'],kargs['u']))
        self.balancingNodeIdSet.add(nodeId)
        
        assert len(self.balancingNodeIdSet)==len(self.balancingSet)
        
        #balancing vector computation
        sw=0
        b=0
        for s in self.balancingSet:
            b+=self.nodes[s[0]]*s[2]   #Sum(w_i*u_i)
            sw+=self.nodes[s[0]]    #Sum(w_i)
        if sw:
            b=b/sw

        
        if b<self.thresh:
        
            #DBG
            print('coord:balance success, b=%0.2f'%b)
            
            #successful balance
            for s in self.balancingSet.copy():
                dDelta=(self.nodes[s[0]]*b)-(self.nodes[s[0]]*s[2])
                signal('adj-slk').send(nodeId=s[0],dDelta=dDelta)
            
            #EXP
            self.expCounter+=1
            
            #empty balancing set
            self.balancingSet.clear()
            self.balancingNodeIdSet.clear()
        
            #XXX
            self.lock.release()

            #resume
            self.event.set()   
        
        
        else:
            
            #pick node to balance at random
            diffSet=set(self.nodes)-self.balancingNodeIdSet
            

            
            #DBG
            print('coord:number of remaining nodes available to balance is %d, b=%0.2f'%(len(diffSet),b))
            
            if len(diffSet):
                nodeIdProbe=random.sample(diffSet,1)[0]
                
                #DBG
                #print('coord:requesting node %s from:'%nodeIdProbe)
                #print(diffSet)
                
                #XXX
                self.lock.release()
                
                signal('req').send(nodeId=nodeIdProbe)
            else:
                #DBG
                print('coord:GLOBAL VIOLATION, counter showed %d previous lvs, sender %s'%(self.expCounter,nodeId))
                
                signal('global-violation').send()
                
                #XXX
                self.lock.release()
                
                time.sleep(3)
                self.event.set() 
                
                
    def start(self):
        '''
        starting execution
        '''
        #DBG
        print('coord:coord started')
        
        self.event.clear()
        signal('init').send()
        #start
        self.event.set()
        
        #DBG
        print('coord:node execution started')
        
    def join(self):
        pass
        
        
        
        
        
    