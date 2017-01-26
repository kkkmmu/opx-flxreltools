import os
from fabric.api import local, run, env
from fabric.context_managers import lcd
from fabric.operations import prompt
from fabric.context_managers import settings
from setupTool import  setupGenie, getSetupHdl

env.use_ssh_config = True
gAnchorDir = ''
gGitUsrName = ''

def _askDetails ():
    global gAnchorDir, gGitUsrName
    gAnchorDir = prompt('Host directory:', default='git')
    gGitUsrName = prompt('Git username:')

def setupHandler():
    global gAnchorDir, gGitUsrName
    if '' in [gAnchorDir, gGitUsrName]:
        _askDetails()
    return getSetupHdl('setupInfo.json', gAnchorDir, gGitUsrName)

def setupExternals (comp=None):
    print 'Installing all External dependencies....'
    info = setupHandler().getExternalInstalls(comp)
    for comp, deps in info.iteritems(): 
        print 'Installing dependencies for %s' %(comp)
        for dep in deps:
            cmd = 'sudo apt-get install -y ' + dep
    	    with settings(prompts={'Do you want to continue [Y/n]? ': 'Y'}):
                local(cmd)

def _setupGitRepo (repo, srcDir, repoPrefix): 
    with lcd(srcDir):
        if not (os.path.exists(srcDir + repo)  and os.path.isdir(srcDir+ repo)):
            cmd = 'git clone '+ repoPrefix + repo 
            local(cmd)

def setupGoDeps(comp=None):
    print 'Fetching external  Golang repos ....'
    info = setupHandler().getGoDeps(comp)
    extSrcDir = setupHandler().getExtSrcDir()
    for rp in info:
        with lcd(extSrcDir):
            repoUrl = 'https://github.com/OpenSnapRoute/%s' %(rp['repo'])
            dstDir =  rp['renamedst'] if rp.has_key('renamedst') else ''
            dirToMake = dstDir 
            cloned = False
            if not (os.path.exists(extSrcDir+ dstDir + '/' + rp['repo'])):
                cmd = 'git clone '+ repoUrl
                local(cmd)
                cloned = True
                if rp.has_key('reltag'):
                    cmd = 'git checkout tags/'+ rp['reltag']
                    with lcd(extSrcDir+rp['repo']):
                        local(cmd)

            if not dstDir.endswith('/'):
                dirToMake = dstDir[0:dstDir.rfind('/')]
            if dirToMake:
                cmd  =  'mkdir -p ' + dirToMake
                local(cmd)
            if rp.has_key('renamesrc') and cloned:
                cmd = 'mv ' + extSrcDir+ rp['renamesrc']+ ' ' + extSrcDir+ rp['renamedst']
                local(cmd)

def setupSRRepos():
    print 'Fetching Snaproute repositories dependencies....'
    global gAnchorDir, gGitUsrName
    gAnchorDir = prompt('Host directory:', default='git')
    gGitUsrName = prompt('Git username:')
    srRepos = setupHandler().getSRRepos()
    usrName =  setupHandler().getUsrName()
    srcDir = setupHandler().getSRSrcDir()
    anchorDir = setupHandler().getAnchorDir()

    if not os.path.isfile(srcDir+'/Makefile' ):
        cmd = 'ln -s ' + anchorDir+  '/reltools/Makefile '+  srcDir + 'Makefile'
        local(cmd)
        repoPrefix   = 'https://github.com/open-switch/'

    for repo in srRepos:
        with lcd(srcDir):
            if not (os.path.exists(srcDir + repo['renameRepo'])  and os.path.isdir(srcDir+ repo['renameRepo'])):
                cmd = 'git clone '+ repoPrefix + repo['repo'] + ' ' + repo['renameRepo']
                local(cmd)

def installThrift():
    TMP_DIR = ".tmp"
    thriftVersion = '0.9.3'
    thriftPkgName = 'thrift-'+thriftVersion 
    if _verifyThriftInstallation(thriftVersion):
        print 'Thrift Already installed. Skipping installation'
        return

    thrift_tar = thriftPkgName +'.tar.gz'
    local('mkdir -p '+TMP_DIR)
    local('wget -O '+ TMP_DIR + '/' +thrift_tar+ ' '+ 'http://www-us.apache.org/dist/thrift/0.9.3/thrift-0.9.3.tar.gz')
    
    with lcd(TMP_DIR):
        local('tar -xvf '+ thrift_tar)
        with lcd (thriftPkgName):
            local ('./configure --with-java=false')
            local ('make')
            local ('sudo make install')
        

def installNanoMsgLib ():
    srcDir = setupHandler().getGoDepDirFor('nanomsg')
    with lcd(srcDir):
        cmdList = ['sudo apt-get install -y libtool',
                'libtoolize',
                './autogen.sh',
                './configure',
                'make',
                'sudo make install',
                ]
        for cmd in cmdList:
            local(cmd)

def installIpTables():
    extSrcDir = setupHandler().getExtSrcDir()
    nfLoc = extSrcDir + 'github.com/netfilter/'
    libipDir = 'libiptables'
    allLibs = ['libmnl', 'libnftnl', 'iptables']
    prefixDir = nfLoc + libipDir
    cflagsDir = nfLoc + libipDir + "/include"
    ldflagsDir = nfLoc + libipDir + "/lib"

    for lib in allLibs:
        with lcd(nfLoc + lib):
            cmdList = []
            cmdList.append('./autogen.sh')
            if lib == 'libmnl':
                cmdList.append('./configure')
            elif lib == 'libnftnl':
                #os.environ["LIBMNL_CFLAGS"]= nfLoc + libipDir + "/include/libmnl"
                #os.environ["LIBMNL_LIBS"]= nfLoc + libipDir + "/lib/pkgconfig"
                cmdList.append('./configure')
            elif lib == 'iptables':
                cmdList.append('./configure')
            cmdList.append('make')
            cmdList.append('sudo make install')
            for cmd in cmdList:
                local(cmd)

def _createDirectoryStructure() :
    dirs = setupHandler().getAllSrcDir()
    for everydir in dirs:
        local('mkdir -p '+ everydir) 

def _verifyThriftInstallation(thriftVersion='0.9.3'):
    with settings(warn_only=True):
        ret = local('which thrift', capture=True)
        if ret.failed:
           return False
    resp =  local('thrift -version', capture=True)
    return thriftVersion in resp

def printInstruction():
    global gAnchorDir
    print "###########################"
    print "Please add the following lines in your ~/.bashrc file"
    print "###########################"
    print "export PATH=$PATH:/usr/local/go/bin"
    print "export SR_CODE_BASE=$HOME/" + gAnchorDir
    print "export GOPATH=$SR_CODE_BASE/snaproute/:$SR_CODE_BASE/external/:$SR_CODE_BASE/generated/"
    print "###########################"

def setupDevEnv() :
    _askDetails()
    local('git config --global credential.helper \"cache --timeout=3600\"')
    _createDirectoryStructure()
    setupHandler()
    setupExternals()
    setupGoDeps()
    installThrift()
    installNanoMsgLib()
    installIpTables()
    setupSRRepos()
    printInstruction()
