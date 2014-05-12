import sys
import tldextract
import sqlite3
import Interface

def getTopPage(conn, parentId):
    if parentId == -1:
        print 'error'

    gradparentId = -1
    c = conn.cursor()
    for row in c.execute("SELECT parent_id FROM pages WHERE id = ?", (parentId, )):
        gradparentId = row[0]

    if gradparentId == -1:
        #print parentId     #empty page invalid ????????????????
        return 0

    if gradparentId == parentId:
        return parentId
    else:
        return getTopPage(conn, gradparentId)

def getHost(url):
    # Get rid of the empty URL
    #if url == "":
        #return url

    #parts = url.split('//', 1)
    #domain = parts[0] + '//' + parts[1].split('/',1)[0]
    #if domain == 'error':
        #print "!!!!!!!!!error",
        #print url
    host = tldextract.extract(url)
    return host[1] + "." + host[2]

def addTokensFromURL(req_id, referrer_host, host, url, tokenDict):
    params = url.split('//',1)[1].split('/',1)[1]
    name = 'param_path'
    value = params.split('?',1)[0]
    token = Interface.RequestToken(req_id, name, value, host, referrer_host)
    tokenDict.addToDict(token)
    if value == params or params.split('?',1)[1] == '':
        return
    pairs = params.split('?',1)[1].split('&')
    for pair in pairs:
        if pair.find('=') == -1:
            name = "param_"+pair
            value = pair
        else:
            name = "param_"+pair.split('=',1)[0]
            value = pair.split('=',1)[1]
        token = Interface.RequestToken(req_id, name, value, host, referrer_host)
        tokenDict.addToDict(token)

def addTokensFromHeader(req_id, referrer_host, host, names, values, tokenDict):
    if(names == ''):
        print 'error'
    if(names != 'cookie'):
        token = Interface.RequestToken(req_id, names, values, host, referrer_host)
        tokenDict.addToDict(token)
    else:
        pairs = values.split(';')
        for pair in pairs:
            if pair.find('=') == -1:
                print "error!! No = in cookies"
            name = "cookie_" + pair.split('=',1)[0]
            value = pair.split('=',1)[1]
            token = Interface.RequestToken(req_id, name, value, host, referrer_host)
            tokenDict.addToDict(token)

#def getKeyValue(name, value, name_value_pairs):
    #if(name != 'cookie' and name != ''):
        #pair = [name, value]
        ##print pair
    #else:
        #pair_list = value.split(";")
        #for row in pair_list:
            #pair=["cookie_"+row.split("=",1)[0], row.split("=",1)[1]]
            ##print pair
            #name_value_pairs.append(pair)

def getTokens(conn, pageId, tokenDict):
    c = conn.cursor()
    for row in c.execute('''SELECT id, url, referrer
                            FROM http_requests
                            WHERE page_id = ?''', (pageId, )):
        req_id = row[0]
        url = row[1]
        if url == 'error':
            print pageId
        referrer_host = getHost(row[2])
        host = getHost(row[1])
        #print referrer_host
        addTokensFromURL(req_id, referrer_host, host, url, tokenDict)
        #print req_id
        for row2 in c.execute('''SELECT name, value
                                 FROM http_request_headers
                                 WHERE http_request_id = ?''', (req_id, )):
            addTokensFromHeader(req_id, referrer_host, host, row2[0], row2[1], tokenDict)

#def findIdentifier(tokenSet):
    #pairSet=[]
    #for token in tokenSet.storage:
        #for new_pair in token.name_value_pairs:
            #for old_pair in pairSet:
                #if old_pair == new_pair[1]:
                    #print new_pair
            #pairSet.append(new_pair[1])

def tokenDictFromFile(sqliteFile):
    conn = sqlite3.connect(sqliteFile)

    c = conn.cursor()
    tokenDict = Interface.RequestTokenDict()

    num = 0
    for row in c.execute('SELECT id, location, parent_id FROM pages'):
        pageId = row[0]
        location = row[1]
        parentId = row[2]

        if pageId == -1 or parentId == -1:    # no parent
            #print 'get rid of -1'
            continue

        if location == 'about:blank':
            #print 'get rid of blank page'
            continue

        topParentId = getTopPage(conn, parentId)
        if topParentId == 0:
            continue

        if topParentId != pageId: # Third-party requests
            num += 1
            getTokens(conn, pageId, tokenDict)
            #print ('thirdParty pageId is '),
            #print(pageId),
            #print (' topParentId is '),
            #print(topParentId)
        else:
            pass
            #print('Not a third party request')
            
    conn.close()
    #print "third party pages number",
    #print num
    tokenDict.printDict()

    return tokenDict

if __name__ == "__main__":
    tokenDictFromFile(sys.argv[1])
