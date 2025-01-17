import sys
import copy

#This file include the interface for longest common substring (LCS) algorithm

#This class records a token in a request
#For non-cookie headers, the key is the header name (e.g. "if-none-match")
#For cookie, the key is cookie_`cookie_name` (e.g. "cookie_bid")
#For reuqest's parameters, 
#    1). the key is param_`param_name` (e.g. "param_id") for each parameter pair
#    2). the key is param for the whole parameters
#For request's path, the key is param_path 
class RequestToken:
    def __init__(self, req_id, name, value, host, referer_host):
        self.id = req_id
        self.name = name
        self.value = value
        self.host = host
        self.referrer_host = referer_host

    def __repr__(self):
        return self.name + "---" + self.value

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value and self.host==other.host

    def __hash__(self):
        return hash(self.name) ^ hash(self.value) ^ hash(self.host)

class RequestTokenDict:
    def __init__(self):
        self.tokenDict = dict()
        self.reqNum = dict()
        self.idDict = dict()

    def addToDict(self,token):
        if token.host in self.tokenDict.keys():
            self.tokenDict[token.host].append(token)
        else:
            self.tokenDict[token.host] = [token]

    def findIdentifier(self):
        for host in self.tokenDict.keys():
            '''
            if "doubleclick" not in host:
                continue
            #print host
            #print self.tokenDict[host]
            '''
            if self.reqNum[host]<10:
                continue
            valueDict = []
            identifier = dict()
            for token in self.tokenDict[host]:
                if token.value in valueDict:
                    if token in identifier[token.value].keys():
                        identifier[token.value][token]+=1
                    else:
                        identifier[token.value][token]=1
                else:
                    valueDict.append(token.value)
                    tokenNumDict=dict()
                    tokenNumDict[token]=1
                    identifier[token.value]=tokenNumDict
            if identifier:
                for v in identifier.keys():
                    num = 0
                    for t in identifier[v].keys():
                        num+=identifier[v][t]
                    if num < self.reqNum[host]:
                        del identifier[v]
                if identifier:
                    self.idDict[host]=identifier
                    #print host + str(self.reqNum[host])

    def printDict(self):
        textFile = open ("output","w")
        hostNum = 0
        tokenNum = 0
        for host in self.tokenDict.keys():
            hostNum += 1
            for token in self.tokenDict[host]:
                tokenNum += 1
                if host == "http://ad.doubleclick.net":
                    print >> textFile, token
        print "host number",
        print hostNum
        print "token number",
        print tokenNum
        textFile.close()

    # The StringArrayDict has a tuple of lists for each host
    #     stringArrayDict[host] = ([keys], [values], [request Ids])
    def toStringArrayDict(self):
        stringArrayDict = {}
        for host in self.tokenDict.keys():
            tokenList = self.tokenDict[host]
    
            if host not in stringArrayDict.keys():
                stringArrayDict[host] = ([], [], [])
    
            for token in tokenList:
                stringArrayDict[host][0].append(token.name)
                stringArrayDict[host][1].append(token.value)
                stringArrayDict[host][2].append(token.id)
    
        return stringArrayDict

#type == 1: directly comparing key and value, 
#            uniqueness shows how unique it is for this identifier
#type == 2: find LCS from tokens, uniqueness is no use here

class Identifier:
    def __init__(self, value, table, occurance):
        self.value = value
        self.table = table
        self.occurance = occurance

    def __repr__(self):
        return self.value + "----" + str(self.occurance)

    def __eq__(self, other):
        return self.value == other.value and self.table == other.table and self.occurance == other.occurance

    def __hash__(self):
        return hash(self.value) ^ hash(self.table) ^ hash(self.occurance)

class IdentifierDict:
    def __init__(self):
        self.identifierDict = dict()

    def addToDict(self, host, identifier):
        if host in self.identifierDict.keys():
            self.identifierDict[host].append(identifier)
        else:
            self.identifierDict[host] = [identifier]
