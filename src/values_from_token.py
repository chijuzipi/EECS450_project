import interface
#from collections import defaultdict

#def stringFromTokenSet(tokenSet):
    #requestString = defaultdict(list)
    #for token in tokenSet.storage:
        #requestString[token.id].append(token.value)

    #return requestString

def stringFromTokenSet(tokenSet):
    requestString = {}
    for token in tokenSet.storage:
        if token.id not in requestString.keys():
            requestString[token.id] = ""
        else:
            requestString[token.id] = requestString[token.id] + token.value

    return requestString

def main():
    data = open('../data/04.18/taobao.data', 'r')
    taobao = interface.RequestTokenSet()
    for line in data.readlines():
        key, value, host, request_id = line.split(" ")
        a = interface.RequestToken(int(request_id), key, value, host, host)
        taobao.add(a)

    print(stringFromTokenSet(taobao))

    data.close()
    return

if (__name__ == '__main__'):
    main()
