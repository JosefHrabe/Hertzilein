import time
from netBase import getStamp as nb_getStamp, loadDict as nb_loadDict, saveDict as nb_saveDict
import threading
from copy import deepcopy







class BaseLogger:

    def __init__(self, logPath ):
        self.valid=False
        self.__logPath=logPath
        self.logTime=time.time()
        print('Init Sampler : ... ' , end='\r')
        self.data=[]
        self.__interval=2*60
        self.run=False
        self.runSave=True
        self.__saveTaskInstances=0
        self.__interval = 2*60
        self.__remain = 0
        self.__last_file= ''
        self.saveOperationRunning=False

        self.__makePathName()
        threading.Thread(target=self.saveTask).start()
        self.valid=True

    def __logTime(self , topic=''):
        print('{0:<15}{1:.3f}s'.format(topic , time.time()-self.logTime))


    def stop(self):
        if self.runSave:
            print('Save Backup')
            self.__saveData()
        self.runSave=False

    def getRemain(self):
        return self.__remain

    def __makePathName(self):
        stamp = nb_getStamp()
        fldr = stamp.split(' ')[0]
        fn = nb_getStamp(hourOnly=True)
        path = self.__logPath + fldr + '/' + fn + '.txt'
        self.__last_file = path

    def saveTask(self):
        if self.__saveTaskInstances !=0:
            print( 'SaveTask already running')
            raise Exception('SaveTask already running')
            return

        self.__saveTaskInstances+=1
        self.runSave=True
        while True:
            self.__remain=self.__interval
            while self.__remain > 0:
                if not self.runSave : return

                self.__remain-=1
                time.sleep(1)

            self.__makePathName()

            self.saveOperationRunning=True
            # self.logTime=time.time()
            self.__saveData()
            print('save samples : {0}'.format(len( self.data )))
            # self.__logTime('save file')
            self.saveOperationRunning=False

        pass

    def __saveData(self):
        if self.__last_file=='': return

        resData = nb_loadDict( self.__last_file )

        if resData is None:
            print('newList')
            resData=[]

        self.logTime=time.time()
        dc = deepcopy( self.data)
        self.__logTime('dc')
        self.data.clear()

        for s in dc:
            resData.append( s )

        nb_saveDict( self.__last_file , resData )




