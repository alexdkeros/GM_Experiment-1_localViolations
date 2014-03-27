'''
@author: ak
'''
import threading
from blinker import signal
from GM_localViolations.InputStream import InputStream
from GM_localViolations import Config


class Node(threading.Thread):
    '''
    class Node
    models a node at a Geometric Monitoring network
    configuration via Config module
    '''

    def __init__(self, event, nodeId, weight=1, initialV=0):
        '''
        Constructor
        args:
            event: synchronizing event
            weight: the node weight
            initialV: the initial local statistics vector
        '''
        #thread configuration
        threading.Thread.__init__(self)
        self.event=event
        self.runFlag=True

        #node data initialization
        self.id=nodeId
        self.inputGenerator=InputStream().getData() #data generator
        self.thresh=Config.threshold    #monitoring threshold
        self.weight=weight  #node weight
        self.v=initialV    #local statistics vector
        self.vLast=self.v    #last sent local statistics vector
        self.u=0    #drift vector
        self.e=0   #estimate vector
        self.delta=0    #slack vector
        
        #signal configuration
        signal('init').connect(self.init)
        signal('req').connect(self.req)
        signal('adj-slk').connect(self.adjSlk)
        signal('new-est').connect(self.newEst)
        signal('global-violation').connect(self.globalViolation)
        
        #DBG
        print('node %s created'%self.id)
       
       
        
    '''
    signal handlers
    '''
    def init(self,sender):
        '''
        "init" signal handler
        '''
        #DBG
        print('init signal received at node %s'%self.id)
        
        signal('init-node').send(self.id,v=self.vLast,w=self.weight)
        
    def req(self,sender,**kargs):
        '''
        req signal handler
        '''
        if kargs['nodeId']==self.id:
            #DBG
            print('req signal received at node %s'%self.id)
            
            signal('rep').send(self.id,v=self.vLast,u=self.u)
        
    def adjSlk(self,sender,**kargs):
        '''
        adj-slk signal handler
        '''
        if kargs['nodeId']==self.id:            
            #DBG
            print('adjSlk signal received at node %s, dDelta: %0.2f'%(self.id,kargs['dDelta']))
        
            self.delta+=kargs['dDelta']
    
    def newEst(self,sender,**kargs):
        '''
        new-est signal handler
        '''
        #DBG
        print('new-est signal received at node %s'%self.id)
        
        self.e=kargs['newE']
        self.v=self.u
        self.delta=0
        
    def globalViolation(self,sender):
        '''
        global-violation signal handler
        '''
        #DBG
        print('global-violation signal received at node %s'%self.id)
        
        self.runFlag=False
    
    
    '''
    monitoring operation
    ''' 
    def run(self):
        '''
        main node execution
        '''
        while self.runFlag:
            
            #thread synchronization
            self.event.wait()
            
            #normal operation
            self.v=self.inputGenerator.next()
            self.u=self.e+(self.v-self.vLast)+(self.delta/self.weight)
            
            #DBG
            print('node %s running, data is v=%0.2f, u=%0.2f'%(self.id,self.v,self.u))
            
            #monochromaticity check
            if self.u>=self.thresh:
                
                #DBG
                print('local violation at node %s, u=%0.2f'%(self.id,self.u))
                
                self.vLast=self.v
                signal('rep').send(self.id,v=self.vLast,u=self.u)
                #at rep signal coordinator issues event.clear(), so we wait
            
        
        
        
    
    
    