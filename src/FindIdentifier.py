#!/usr/bin/env python

import DataHandler
import Interface
import SuffixTree
import sys
import gc

#gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)

def usage():
    print("Usage: [python_2.x_bin] FindIdentifier.py [.sqlite file1] [.sqlite file2] [level]")

def printCommonString(sequences, seq, start, stop, occurance):
    print seq, '[' + str(start) + ':' + str(stop) + ']',
    print unichr(10084),'',
    print sequences[seq][start:stop],
    print unichr(10084),'',
    print sequences[seq][:start] +unichr(10073) + sequences[seq][start:stop] + \
          unichr(10073) + sequences[seq][stop:]

def identifierDictFromFile(database):
    requestTokens = DataHandler.tokenDictFromFile(database)
    stringArrayDict = requestTokens.toStringArrayDict()

    identifiers = Interface.IdentifierDict()

    print('=' * 20 + 'Finding Sub-string Start' + '=' * 20)

    numHosts = len(stringArrayDict.keys())
    counterHost = 1
    for host in stringArrayDict.keys():
    #for host in ['twitter.com']:
        print("Host " + str(counterHost) + " / " + str(numHosts) + ": " + host)
        keys, sequences, reqId = stringArrayDict[host]
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)
    
        for shared in st.sharedSubstrings(reqId, 5, 0.5):
            pass
            print('-' * 70)
            stringTable = []
            for seq, start, stop, occurance in shared:
                stringTable.append([sequences[seq], start, stop, keys[seq], reqId[seq]])
                #printCommonString(sequences, seq, start, stop)
    
            newIdentifier = Interface.Identifier(sequences[seq][start:stop], stringTable, occurance)
            print(newIdentifier)
            identifiers.addToDict(host, newIdentifier)
    
        print('=' * 70)
    
        counterHost += 1
        print('Done.\n\n')
    
        del st
        gc.collect()

    return identifiers

def identifierFilration(iden1, iden2, level):
    result = Interface.IdentifierDict()
    commonKey = getCommonKeys(iden1, iden2) 
    for host in commonKey:
        list1 = iden1[host]
        list2 = iden2[host]
        print 'list 1 is :', list1
        print 'list 2 is :', list2
        for i in range(len(list1)):
            for j in range(len(list2)):
                #if tables are similar
                if similar(list1[i][1], list2[j][1], level):
                    #if the identifier strings are different 
                    if list1[i][0] != list2[j][0]:
                       result.addToDict(host, list1[i][0])
    print 'the final results: ', result
    return result

def getCommonKeys(dict1, dict2):
    keys = []
    for key in dict1:
        getKey = dict2.get(key, None)
        if getKey:
            keys.append(key)
    return keys

def similar(table1, table2, level):
    if level == 1:
        if table1 == table2:
            return True
        else:
            return False
    if level == 2:
        if table1[3] == table2[3]:
            return True
        else:
            return False

if __name__ == "__main__":

    #if len(sys.argv) != 4:
    if len(sys.argv) != 2:
        usage()
    else:
        identifierDictFromFile(sys.argv[1])
        #iden1 = identifierDictFromFile(sys.argv[1])
        #iden2 = identifierDictFromFile(sys.argv[2])
        #dict1 = iden1.identifierDict
        #dict2 = iden2.identifierDict
        #table1 = iden1.table
        #print '%'*70
        #print dict1
        #print dict2
        #print '%'*70
        ##how to get the table?
        #level = int(sys.argv[3])
        #if (level != 1) and (level != 2) :
            #print 'only level 1 and 2 are implemented'
        #else:
            #print 'start filration...'
            #print '*'*70
            #identifierFilration(dict1, dict2, level) 
