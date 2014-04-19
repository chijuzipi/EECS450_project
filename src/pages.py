#!/usr/bin/env python 

# idList = [[id, parent], [id, parent], ...]
def parent(filename):
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
            idList[pageId] = parentId
            

    pages.close()

    return idList
