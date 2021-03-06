'''
@author: ak
'''
from scipy.stats import norm
from GM_localViolations import Config



class InputStream:
    '''
    class InputStream
    models a continuous input stream of data having velocities sampled from a normal distribution
    implements a generator of data
    configuration via Config module
    '''

    def __init__(self,status=Config.defStatus,initXData=Config.defInitXData, mean=Config.defMean, std=Config.defStd, interval=Config.defInterval):
        '''
        Constructor
        args:
              status: "static" or "random" velocities
              mean: mean of normal distribution
              std: standard deviation of normal distribution
              interval: update interval in case of changing velocities
        '''
        if status in ["static", "random"]:
            self.status=status
        else:
            print("Bad input: status must be 'static' or 'random'. 'Static' status is assumed")
            self.status='static'
        self.initXData=initXData
        self.mean=mean
        self.std=std
        self.interval=interval
        self.velocity=norm.rvs(mean,std)
        
    
    def getData(self):
        '''
        Generator
        yields new data
        '''
        xData=self.initXData
        while 1:
            if self.status=="random":
                self.velocity=norm.rvs(self.mean,self.std)
            for i in range(self.interval):
                yield xData
                xData=xData+self.velocity
                
if __name__=="__main__":
    '''simple test'''
    ip=InputStream(status='random',initXData=-5,mean=10,interval=3).getData()
    
    print(ip)
    for i in range(20):
        print(ip.next())
        