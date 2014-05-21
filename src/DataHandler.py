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
    name = 'param'
    value = params
    token = Interface.RequestToken(req_id, name, value, host, referrer_host)
    tokenDict.addToDict(token)
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

def addTokensFromHeader(conn, req_id, referrer_host, host, tokenDict):
    c=conn.cursor()
    for row in c.execute('''SELECT name, value
                                 FROM http_request_headers
                                 WHERE http_request_id = ?''', (req_id, )):
        names = row[0]
        values=row[1]
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
                    print pair
                else:
                    name = "cookie_" + pair.split('=',1)[0]
                    value = pair.split('=',1)[1]
                    token = Interface.RequestToken(req_id, name, value, host, referrer_host)
                    tokenDict.addToDict(token)


def getTopHost(conn, topId):
    c=conn.cursor()
    for row in c.execute("SELECT location FROM pages WHERE id = '%d'" % topId):
        topHost=row[0]
    return getHost(topHost)

def isValidReq(conn, pageId):
    c=conn.cursor()

    for row in c.execute('SELECT location, parent_id FROM pages WHERE id="%d"' % pageId):
        location = row[0]
        parentId = row[1]

        if pageId == -1 or parentId == -1:    # no parent
            #print 'get rid of -1'
            return False

        if location == 'about:blank':
            #print 'get rid of blank page'
            return False

        topParentId = getTopPage(conn, parentId)
        if topParentId == 0:
            return False

        return True



def checkThirdPartyReq(conn, pageId, url):
    c=conn.cursor()
    host = getHost(url)
    for row in c.execute('SELECT location, parent_id FROM pages WHERE id="%d"' % pageId):
        location = row[0]
        parentId = row[1]

        if pageId == -1 or parentId == -1:    # no parent
            #print 'get rid of -1'
            return False

        if location == 'about:blank':
            #print 'get rid of blank page'
            return False

        topParentId = getTopPage(conn, parentId)
        if topParentId == 0:
            return False

        topHost = getTopHost(conn,topParentId)

        if host != topHost: # Third-party requests
            return True
            #print host,
            #print topHost
        else:
            return False


def tokenDictFromFile(sqliteFile):
    conn = sqlite3.connect(sqliteFile)

    c = conn.cursor()
    tokenDict = Interface.RequestTokenDict()

    reqNum=0
    num = 0

    for row in c.execute('SELECT id, url, referrer, page_id FROM http_requests'):
        url = row[1]
        page_id = row[3]
        if isValidReq(conn, page_id)==True:
            num+=1
        if checkThirdPartyReq(conn, page_id, url) != True:
            continue
        req_id = row[0]
        if url == 'error':
            print pageId
        referrer_host = getHost(row[2])
        host = getHost(row[1])
        reqNum+=1
        #print referrer_host
        addTokensFromURL(req_id, referrer_host, host, url, tokenDict)
        #print req_id
        addTokensFromHeader(conn, req_id, referrer_host, host, tokenDict)
            
    conn.close()
    #print "third party pages number",
    print num
    print reqNum
    tokenDict.printDict()

    return tokenDict

if __name__ == "__main__":
    tokenDictFromFile(sys.argv[1])
