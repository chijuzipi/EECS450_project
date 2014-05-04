import sys
import sqlite3
import tldextract
import interface
from collections import defaultdict

def transform(idlist):
    output = []
    for i in range(len(idlist)):
        if idlist[i] != 0:
            idlist[i] = track(idlist, i)
            if idlist[i] != -1:
                output.append((i, idlist[i]))
    return output

def track(idlist, i):
    if idlist[i] == i:
        return i
    elif idlist[i] == -1:
        return -1
    else:
        return track(idlist, idlist[i])

def main(argv = None):

    # Check the input arguments
    if argv is None:
        argv = sys.argv
    if (len(argv) != 2):
        print("Usage: python_bin [sqlite_db_file]")
        return

    # Attach the input database 
    inputDatabase = sqlite3.connect(argv[1])

    # Dump the input database to memory
    database = sqlite3.connect(":memory:")
    cursor = database.cursor()

    query = "".join(row for row in inputDatabase.iterdump())
    database.executescript(query)

    inputDatabase.close()

    # Find the root page ID: 
    #     idlist = [(id, rootID), ...]
    i = 0
    parentList = []
    for row in cursor.execute('SELECT * FROM pages'):
        while (i < row[0]):
            parentList.append(0)
            i = i + 1

        parentList.append(row[2])
        i = i + 1

    idList = transform(parentList)


    # Save the idList to table page_root_id
    cursor.execute('''CREATE TABLE page_root_id
                      (id      INTEGER, 
                       root_id INTEGER)''')
    cursor.executemany('INSERT INTO page_root_id VALUES (?,?)',
                       idList)
    database.commit()

    # Query the url, location and request_id
    # and find the third party requests
    thirdPartyQuery = '''SELECT url, location, http_requests.id
                         FROM page_root_id 
                              cross join pages
                              cross join http_requests
                         WHERE page_root_id.id = http_requests.page_id and
                               page_root_id.root_id = pages.id'''

    thirdPartyList = []
    blankPage = "about:blank"
    chromePage = "chrome://browser/content/browser.xul"
    for row in cursor.execute(thirdPartyQuery):
        # The structure of the row:
        #     (URL, location, requests_id)
        domainA = tldextract.extract(row[0])
        domainB = tldextract.extract(row[1])
        if ((domainA[1] != domainB[1]) and
            (blankPage not in row) and
            (chromePage not in row)):
            thirdPartyList.append((domainA[1], row[2]))

    # Save the third party list to a table
    cursor.execute('''CREATE TABLE third_party
                      (domain     TEXT, 
                       request_id INTEGER)''')
    cursor.executemany('INSERT INTO third_party VALUES (?,?)',
                       thirdPartyList)
    database.commit()

    # Query the headers corresponding to third party requests
    headerQuery = '''SELECT value, domain, TP.request_id
                     FROM third_party TP
                          cross join http_request_headers HRH
                     WHERE name = 'cookie' and
                           TP.request_id = HRH.http_request_id
                     ORDER BY domain'''
    keyValueList = []
    for row in cursor.execute(headerQuery):
        keyValuePairList = row[0].split('; ')
        for line in keyValuePairList:
            key, value = line.split('=', 1)
            keyValueList.append((key, value, row[1], row[2]))
            print(key, value, row[1], row[2])

    # Save the key value list to a table
    cursor.execute('''CREATE TABLE key_value_domain
                      (key    TEXT, 
                       value  TEXT, 
                       domain TEXT,
                       request_id INT)''')
    cursor.executemany('INSERT INTO key_value_domain VALUES (?,?,?,?)',
                       keyValueList)
    database.commit()


    database.close()

    return 

if __name__ == '__main__':
    main()
