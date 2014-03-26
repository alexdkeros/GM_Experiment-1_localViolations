'''
@author: ak
'''

class Coordinator:
    '''
    class Coordinator
    models the Coordinator at a Geometric Monitoring network
    configuration via Config module
    '''


    def __init__(self, event, nodes):
        '''
        Constructor
            nodes: a node object list
        '''
        self.event=event
        self.nodes=nodes
        self.v=0    #global statistics vector
        self.e=0    #estimate vector
        self.threshold=0
        self.test()
        
    def test(self):
        print(self.nodes)

        
        
        
    