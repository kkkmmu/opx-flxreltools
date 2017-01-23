import os
import json

gSetup =  None
SNAP_ROUTE_SRC = '/snaproute/src/'
EXTERNAL_SRC = '/external/src/'
GENERATED_SRC = '/generated/src/'

class setupGenie (object) :
    def __init__ (self, setupInfo, anchorDir , gitUsrName) :
        self.setupInfo = setupInfo
        self.info = None 
        self.homeDir = os.path.expanduser('~')
        self.anchor = self.homeDir + '/' + anchorDir
        self.usrName = gitUsrName

        with open(self.setupInfo) as dataFile:
            self.info = json.load(dataFile)                                                                                 

    def getExternalInstalls(self, comp = None) :
        if comp:
            return { comp+'Deps' : self.info['Externals'] [comp+'Deps']}
        else:
            return self.info['Externals']

    def getGoDeps (self, comp = None) :
        return self.info['GoDeps']

    def getGoDepDirFor (self, comp ) :
        for dep in self.info['GoDeps']:
            if dep['repo'] == comp:
                if dep.has_key('renamedst') :
                    return self.anchor + EXTERNAL_SRC + dep['renamedst'] + dep['repo']
                else:
                    return self.anchor + EXTERNAL_SRC + dep['repo']

    def getSRRepos(self, comp = None) :
        return self.info['Repos']

    def getExtSrcDir (self ) :
        return self.anchor + EXTERNAL_SRC

    def getGenSrcDir (self ) :
        return self.anchor + GENERATED_SRC 

    def getSRSrcDir (self ) :
        return self.anchor + SNAP_ROUTE_SRC 

    def getAllSrcDir (self ) :
        return [ self.anchor + SNAP_ROUTE_SRC, self.anchor + EXTERNAL_SRC, self.anchor + GENERATED_SRC ]

    def getUsrName(self) :
        return self.usrName
        
    def getAnchorDir(self ) :
        return self.anchor 

                
def getSetupHdl (setupInfo='setupInfo.json', anchorDir='git', gitUsrName='') :
    global gSetup
    if not gSetup:
        gSetup = setupGenie(setupInfo, anchorDir, gitUsrName)
    return gSetup

