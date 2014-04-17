import sys

def parseRequest(filename):
    pages = open(filename, 'r')
    requestList = []
    for line in pages.readlines():
        if not line.split():
            continue

        key, value = line.strip().split(' =')
        key = key.strip()
        value = value.strip()

        if key == "url":
            urlTo = value
        elif key == "location":
            urlFrom = value
            requestList.append((urlTo, urlFrom))
    pages.close()
    return requestList

def thirdParty(rlist):
    for i in range(1):
        for j in range(len(rlist[i][0])):
            if rlist[i][0][j] == '/' & rlist[i][0][j+1] != '/':
                mark1 = j+1
            if rlist[i][0][j] == '.':
                mark2 = j


        #print(rlist[i][0], len(rlist[i][0]), rlist[i][0][5])
        

def main(argv = None):
    if argv is None:
        argv = sys.argv
    if (len(argv) != 2):
        print("Wrong number of arguments")
        return
    requestList = parseRequest(argv[1])
    thirdParty(requestList)
    return

if __name__ == '__main__':
    main()
