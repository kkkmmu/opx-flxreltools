import os
import sys
import json
import time
import fileinput
import subprocess 
import getpass
from fabric.api import env,local,run,parallel

PACKAGE_BUILD="PKG_BUILD=TRUE"
TEMPLATE_BUILD_TYPE="PKG_BUILD=FALSE"
TEMPLATE_CHANGELOG_VER = "0.0.1"
TEMPLATE_BUILD_DIR = "flexswitch-0.0.1"

def executeCommand (command) :
    out = ''
    if type(command) != list:
        command = [ command]
    for cmd in command:
        print 'Executing command %s' %(cmd)
        local(cmd)
    return out

if __name__ == '__main__':

    pkgfile = "pkgInfo.json"
    with open(pkgfile, "r") as cfgFile:
        pkgInfo = cfgFile.read().replace('\n', '')
        parsedPkgInfo = json.loads(pkgInfo)
    cfgFile.close()
    buildTargetList = parsedPkgInfo['platforms']
    pkgVersion = "snaproute_" + parsedPkgInfo['major']+ '.'\
                  + parsedPkgInfo['minor'] +  '.' + parsedPkgInfo['patch'] + \
                  '.' + parsedPkgInfo['build'] + '.' + parsedPkgInfo['changeindex']
    pkgVersionNum =  parsedPkgInfo['major']+ '.'\
                  + parsedPkgInfo['minor'] +  '.' + parsedPkgInfo['patch'] + \
                  '.' + parsedPkgInfo['build'] + '.' + parsedPkgInfo['changeindex']
    build_dir = "flexswitch-" + pkgVersion
    command = [
            'rm -rf ' + build_dir,
            'make clean_all'
            ]
    executeCommand(command)
    startTime = time.time()
    for buildTargetDetail in buildTargetList:
        print buildTargetDetail
        buildTarget = buildTargetDetail['odm']
        preProcess = [
                'cp -a tmplPkgDir ' + build_dir,
                'cp Makefile ' + build_dir,
                'sed -i s/' + TEMPLATE_BUILD_DIR +'/' + build_dir + '/ ' + build_dir +'/Makefile',
                'sed -i s/' + TEMPLATE_BUILD_TYPE +'/' + PACKAGE_BUILD + '/ ' + build_dir + '/Makefile',
                'sed -i s/' + TEMPLATE_CHANGELOG_VER +'/' + pkgVersionNum+ '/ ' + build_dir + '/debian/changelog',
              ]
        executeCommand(preProcess)
        executeCommand('python buildInfoGen.py')
        os.chdir(build_dir)
        pkgRecipe = [
                'fakeroot debian/rules clean',
                'fakeroot debian/rules build',
                'fakeroot debian/rules binary',
                'make clean_all'
                ]
        executeCommand(pkgRecipe)
        os.chdir("..")
        command = []
        command.append('rm -rf ' + build_dir)
        executeCommand(command)
        pkgName = "flexswitch_" + buildTarget + "-" + pkgVersion + "_amd64.deb"
        cmd = []
        cmd = 'mv flexswitch_' + pkgVersionNum + '*_amd64.deb ' + pkgName
        executeCommand(cmd)
