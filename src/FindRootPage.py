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
    host = tldextract.extract(url)
    return host[1] + "." + host[2]

def getTopHost(conn, pageId):
    c=conn.cursor()
    topId = getTopPage(conn, pageId)
    for row in c.execute("SELECT location FROM pages WHERE id = '%d'" % topId):
        topHost=row[0]
    	return getHost(topHost)

def getRootPage(requestIdSet, sqliteFile):
	conn = sqlite3.connect(sqliteFile)
	c = conn.cursor()
	rootPageDict = dict()
	for requestId in requestIdSet:
		for row in c.execute("SELECT page_id FROM http_requests WHERE id = '%d'" % requestId):
			rootPage = getTopHost(conn,row[0])
			if rootPage in rootPageDict.keys():
				rootPageDict[rootPage]+=1
			else:
				rootPageDict[rootPage]=1
	print rootPageDict

# for test
if __name__ == "__main__":
	requestIdSet=set()
	requestIdSet.add(100)
	requestIdSet.add(200)
	getRootPage(requestIdSet, sys.argv[1])