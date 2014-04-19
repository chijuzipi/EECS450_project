import sys
import tldextract

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
        elif key == "id":
            requeId = value
            requestList.append((urlTo, urlFrom,requeId))
    pages.close()
    return requestList

def thirdParty(rlist):
    output = []
    print(tldextract.extract("chrome://browser/content/browser.xul"))
    for i in range(len(rlist)):
        parsed_uriA = []   
        parsed_uriB = []   
        parsed_uriA = tldextract.extract( rlist[i][0] )
        parsed_uriB = tldextract.extract( rlist[i][1] )
        if parsed_uriA[1] != parsed_uriB[1]:
            if (rlist[i][0] != "about:blank") & (rlist[i][1] != "about:blank") & (rlist[i][0] !=
            "chrome://browser/content/browser.xul") & (rlist[i][1] != "chrome://browser/content/browser.xul") :
                    output.append((parsed_uriA[1], rlist[i][2])) # domain name + request id
    return output

def main(argv = None):
    if argv is None:
        argv = sys.argv
    if (len(argv) != 3):
        print("Wrong number of arguments")
        return
    requestList = parseRequest(argv[1])
    output = thirdParty(requestList)
    
    origin_stdout = sys.stdout
    w = open (argv[2], 'w')
    sys.stdout = w
    for i in range(len(output)):
        print(output[i][0], ',', output[i][1])
    sys.stdout = origin_stdout
    w.close()
    return

if __name__ == '__main__':
    main()
