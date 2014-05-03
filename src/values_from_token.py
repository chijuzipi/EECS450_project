import interface

def stringFromTokenSet(tokenSet):
    strings = []
    for token in tokenSet.storage:
        strings.append(token.value)

    return strings

def main():
    a = interface.RequestToken(25, 'fads', '4312', '3m.com', 'google.com')
    b = interface.RequestToken(5, '33ds', '41212', '3m.com', 'ggle.com')

    c = interface.RequestTokenSet()
    c.add(a)
    c.add(b)
    print(stringFromTokenSet(c))

    return
