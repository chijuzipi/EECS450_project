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
    def __init__(self,req_id,name,value,host,referer_host):
        self.id = req_id
        self.name = name
        self.value = value
        self.host = host
        self.referrer_host = referer_host

    def __repr__(self):
        return str(self.id) + "----" + self.name + "-----" + self.value

class RequestTokenDict:
    def __init__(self):
        self.tokenDict = dict()

    def addToDict(self,token):
        if token.host in self.tokenDict.keys():
            self.tokenDict[token.host].append(token)
        else:
            self.tokenDict[token.host] = [token]

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
    #     stringArrayDict[host] = ([values], [request Ids])
    def toStringArrayDict(self):
        stringArrayDict = {}
        for host in self.tokenDict.keys():
            tokenList = self.tokenDict[host]
    
            if host not in stringArrayDict.keys():
                stringArrayDict[host] = ([], [])
    
            for token in tokenList:
                stringArrayDict[host][0].append(token.value)
                stringArrayDict[host][1].append(token.id)
    
        return stringArrayDict

#type == 1: directly comparing key and value, 
#            uniqueness shows how unique it is for this identifier
#type == 2: find LCS from tokens, uniqueness is no use here

class Identifier:
    def __init__(self, token_set, name, value, type, uniqueness, prevalance):
        pass

class IdentifierSet:
    def __init__(self,host):
        pass
