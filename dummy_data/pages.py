#!/usr/bin/env python 

# idList = [[id, parent], [id, parent], ...]
def parent(filename):
    pages = open(filename, 'r')
    idPair = []
    idList = []
    for line in pages.readlines():
        if not line.split():
            continue

        key, value = line.strip().split(' =')
        key = key.strip()
        value = value.strip()

        if key == "id":
            idPair.append(value)
        elif key == "parent_id":
            idPair.append(value)
            idList.append(idPair)
            idPair = []

    pages.close()

    return idList
