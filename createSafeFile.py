#!/usr/bin/python
#-*-coding:utf-8-*-
# Author: Kaysen
# Date: 2015-05-20

import sys
import os
import socket
import copy
import string

reload(sys)
socket.setdefaulttimeout(30)
sys.setdefaultencoding('utf-8')

class createSafeFile:

    def __init__(self, webdir, removePathList, logFile):
        self.webDir = webdir
        self.removePathList = removePathList
        self.logFile = logFile

    def removePathFunc(self, pathList, removePathList):
        newPathList =  copy.deepcopy(pathList)

        for item in pathList:
            for reItem in removePathList:
                if(item == reItem):
                    currIndex = newPathList.index(item)
                    del newPathList[currIndex]

        return newPathList

    def arg_type(self, args):
        if(string.join(args) == 'create'):
            self.createFileFunc()
        elif(string.join(args) == 'delete'):
            self.deleteFileFunc()
        else:
            print 'Parameter error'

    def empty(self, variable):
        if not variable:
            return True
        return False

    def isRemovePath(self, currPath):
        for item in self.removePathList:
            if(currPath.find(item) != -1):
                return True
        return False

    def createFileFunc(self):
        fileSize = 0
        yid = os.walk(self.webDir)

        if(os.path.isfile(self.logFile) == True):
            os.chmod(self.logFile, 0777)

        for rootDir, pathList, fileList in yid:
            if(self.isRemovePath(rootDir) == True):
                continue
            newPathList = copy.deepcopy(self.removePathFunc(pathList, self.removePathList))
            if(self.empty(pathList) == True or self.empty(newPathList) == True):
                continue
            for path in newPathList:
                path = os.path.join(rootDir, path)
                path = copy.deepcopy(self.removePathFunc(path, self.removePathList))

                if(path.find('\\') != -1):
                    path += '\index.html'
                else:
                    path += '/index.html'

                if(os.path.isfile(path) == False):
                    fobj = open(path, 'w')
                    fobj.close()

                    print 'Create: ' + path
                    self.addLogs(path)
                    fileSize = fileSize + 1

        print '#####################################'
        print 'Status: Create'
        print 'WebDir: ' + self.webDir
        print 'TotalRow: ' + str(fileSize)
        print '#####################################'

    def deleteFileFunc(self):

        file = open(self.logFile, 'r')
        content = file.readlines()

        fileSize = 0

        for item in content:

            logFile = item.replace('\n', '')

            fileSize = fileSize + 1

            if os.path.exists(logFile):
                os.remove(logFile)
                print 'Delete: ' + logFile

        self.truncateLogs()
        print '#####################################'
        print 'Status: Delete'
        print 'WebDir: ' + self.webDir
        print 'TotalRow: ' + str(fileSize)
        print '#####################################'

    def addLogs(self, filePath):
        fobj = open(self.logFile, 'a')
        fobj.writelines(filePath + '\n')
        fobj.close()

    def truncateLogs(self):
        fobj = open(self.logFile, 'w')
        fobj.truncate()
        fobj.close()

    def arg_help(self, args):
        strHelp = "Usage: ps [-options] [args...] where option include:"
        strHelp += """
        -? -help            print this help message
        -t -type:[create]   create all names is the index.html file
        -t -type:[delete]   Delete all the name is the index.html file """

        print strHelp

if __name__ == "__main__":
    argsDic = {'arg_help' : ['-?', '-help'], 'arg_type' : ['-t', '-type']}

    removePathList = ['.svn', '.settings', 'ThinkPHP', 'Scripts']
    webPath = r'E:\htdocs\xxx'
    logFile = r'E:\htdocs\xxx\Scripts\log.log'

    if(os.path.exists(webPath) == False):
        print 'Web Path is not existed'
        sys.exit()

    obj = createSafeFile(webPath, removePathList, logFile)

    if len(sys.argv) <= 1:
        obj.arg_help(sys.argv)
    else:
        args = ''
        for i in sys.argv[1:]:
            math = False
            for j in argsDic.items():
                if i in j[1]:
                    args = j[0]
                    math = True
                    break
            if math:
                break
        if args:
            try:
                getattr(obj, args)(sys.argv[2:])
            except Exception, error:
                print error
                sys.exit()
        else:
            print 'Error: "%s" isn\'t validate arg.' % ' '.join(sys.argv[1:])
            del obj
