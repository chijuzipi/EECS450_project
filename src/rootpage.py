import sys

def parsePageId(filename):
    pages = open(filename, 'r')
    idList = []
    for i in range(3000):
        idList.append(0)
    
    for line in pages.readlines():
        if not line.split():
            continue

        key, value = line.strip().split(' =')
        key = key.strip()
        value = value.strip()

        if key == "id":
            pageId = int(value)
        elif key == "parent_id":
            parentId = int(value)
            if parentId >= 0:
                idList[pageId] = parentId

    pages.close()
    return idList

def transform(idlist):
    for i in range(len(idlist)):
        if idlist[i] != 0:
            idlist[i] = track(idlist, i)
    output = []
    for i in range(len(idlist)):
        if idlist[i] != 0:
            output.append((i, idlist[i]))
    return output

def track(idlist, i):
    if idlist[i] == i:
        return i
    else:
        return track(idlist, idlist[i])

def main(argv = None):
    if argv is None:
        argv = sys.argv
    if (len(argv) != 2):
        print("Wrong number of arguments")
        return
    temp_page_list = parsePageId(argv[1])
    idlist = transform(temp_page_list)
    
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
