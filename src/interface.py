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
    def __init__(self,req_id,key,value,host,referer_host):
        self.id = req_id
        self.key = key
        self.value = value
        self.host = host
        self.referer_host = referer_host


class RequestTokenSet:
    def __init__(self):
        self.storage = []
        self.host = None

    def add(self,token):
        if self.host == None:
            self.host = token.host
        elif self.host != token.host:
            #print("Error, hosts are not consistent", file = sys.stderr)
            print >> sys.stderr,"Error, hosts are not consistent"
            return
        if self.findToken(token):
            #print("Error, " + token.id + " exist in this set", file = sys.stderr)
            print >> sys.stderr,"Error, ", token, " exist in this set"
            return

        self.storage.append(copy.copy(token))

    def findToken(self,token):
        for t in self.storage:
            if ((token.id == t.id) and 
                (token.key == t.key) and
                (token.value == t.value) and 
                (token.host == t.host)) :
                return True

        return False

#type == 1: directly comparing key and value, 
#            uniqueness shows how unique it is for this identifier
#type == 2: find LCS from tokens, uniqueness is no use here

class Identifier:
    def __init__(self, token_set, name, value, type, uniqueness, prevalance):
        pass

class IdentifierSet:
    def __init__(self,host):
        pass



