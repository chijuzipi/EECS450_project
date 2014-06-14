import ConfigParser

def processSimpleFile(simpleFile):
    f = open(simpleFile, 'r')
    simpleDict = {}
    simpleHostList = []
    while True:
        host = f.readline().strip()
        if not host: break
        idList = eval(f.readline().strip())
        actualList = []
        for i in range(len(idList)):
            actualList.append(processIdString(idList[i]))
        #print actualList
        simpleDict[host] = actualList 
        simpleHostList.append(host)
    #print 'from simple:', simpleDict 
    print len(simpleHostList)
    return simpleDict, simpleHostList

def processIdString(s):
    indStart = 0
    indEnd = 0
    for i in range(2, len(s)):
        if ((s[i-2] == '-') and (s[i-1] == '-') and (s[i] == '-')):
            indStart = i
            break
    for j in range(1, (len(s))):
        if ((s[j-1] == '~') and (s[j] == '~')):
            indEnd = j 
            break
    return s[indStart+1:indEnd-1]

def processCfgFile(cfgFile):
    config = ConfigParser.RawConfigParser()
    config.read(cfgFile)
    hostList = config.sections()
    print 'suffix tree host number:', len(hostList)
    suffixDict = {}

    for host in hostList: 
        List1 = eval(config.get(host, 'identifiers'))
        List2 = []
        for i in range(len(List1)):
            List2.append(str(List1[i]))
            
        suffixDict[host] = List2 
        
    #print 'from suffix tree:', suffixDict 
    return suffixDict, hostList 

def compare(host, simpleDict, suffixDict):
    hiddenList = []
    simpleList = simpleDict[host]
    suffixList = suffixDict[host]
    for item in suffixList: 
        add = True
        for item2 in simpleList:
            if item in item2:
                add = False
        if add:
            hiddenList.append(item)  
    return hiddenList 

if __name__ == "__main__":

    simpleFile = "output"
    simpleDict, simpleHostList = processSimpleFile(simpleFile)

    cfgFile = "identifier_user1.cfg"
    suffixDict, suffixHostList = processCfgFile(cfgFile)
    
    hiddenId = {}
    addIdHost = []
    new = 0
    newIdentifier = 0
    old = 0
    for host in suffixHostList: 
        if host in simpleHostList:
            List = compare(host, simpleDict, suffixDict)
            if len(List) > 0:   
                hiddenId[host] = List 
                old += len(List)
                addIdHost.append(host)
        if host not in simpleHostList:
            new += 1
            List = suffixDict[host]
            newIdentifier += len(List) 
            hiddenId[host] = List
    print 'new third party trackers are : ', new
    print 'new identifiers for the new third party trackers are : ', newIdentifier
    print 'new identifiers for the old third party trackers are : ', old

