#!/usr/bin/env python

import DataHandler
import Interface
import SuffixTree
import sys

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
    #for host in ['google.com']:
      #  print("Host " + str(counterHost) + " / " + str(numHosts) + ": " + host)
        keys, sequences, reqId = stringArrayDict[host]
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)

        for shared in st.sharedSubstrings(reqId, 5, 0.5):
       #     print('-' * 70)
            stringTable = []
            for seq, start, stop, occurance in shared:
                stringTable.append([sequences[seq], start, stop, keys[seq], reqId[seq]])
                #printCommonString(sequences, seq, start, stop)

            newIdentifier = Interface.Identifier(sequences[seq][start:stop], stringTable, occurance)
    #        print(newIdentifier)
            identifiers.addToDict(host, newIdentifier)

     #   print('=' * 70)
    
        counterHost += 1
        del st
        print('Done with process identifiers object\n\n')

    return identifiers

def identifierFilration(iden1, iden2, level):
    result = []
    commonKey = getCommonKeys(iden1, iden2) 
    for host in commonKey:
        #this is identifier list
        list1 = iden1[host]
        list2 = iden2[host]
        commonValue1 = []
        commonValue2 = []
        
        # eliminate the duplicates:
        for i in range(len(list1)):
            for j in range(len(list2)):
                if list1[i].value == list2[j].value:
                    commonValue1.append(list1[i]) 
                    commonValue2.append(list2[j]) 
        set(commonValue1)
        set(commonValue2)
        for item in commonValue1:
            list1.remove(item)
        for item in commonValue2:
            list2.remove(item)
        # start to compare
        for i in range(len(list1)):
            for j in range(len(list2)):
                #if tables are similar
                if similarTable(list1[i].table, list2[j].table, level):
                    #if the identifier strings are different 
                    if list1[i].value != list2[j].value:
                        result.append([host, list1[i].value, list2[j].value])
    print 'the final results: ', result
    return result

def getCommonKeys(dict1, dict2):
    keys = []
    for key in dict1.keys():
        if key in dict2.keys():
            keys.append(key)
    return keys

def similarTable(table1, table2, level):
    len1 = len(table1)
    len2 = len(table2)
    position1 = []
    key1 = []
    position2 = []
    key2 = []
    for i in range(len1):
        position1.append(table1[i][1])
        key1.append(table1[i][3])
    for i in range(len2):
        position2.append(table2[i][1])
        key2.append(table2[i][3])
        
    if level == 1:
        #if the identifiers happens to be from same key
        for item in key1:
            if item in key2:
                return True
        else:
            return False
    if level == 2:
        #if the identifier happes to be from same key and same start position
        for item in key1:
            if item in key2:
                index1 = key1.index(item)
                index2 = key2.index(item)
                if position1[index1] == position2[index2]:
                    return True
        else:
            return False

if __name__ == "__main__":

    if len(sys.argv) != 4:
        usage()
    else:
        iden1 = identifierDictFromFile(sys.argv[1])
        iden2 = identifierDictFromFile(sys.argv[2])
        dict1 = iden1.identifierDict
        dict2 = iden2.identifierDict
        print '%'*70
        print iden1
        print iden2
        print dict1
        print dict2
        print '%'*70
        #how to get the table?
        level = int(sys.argv[3])
        if (level != 1) and (level != 2) :
            print 'only level 1 and 2 are implemented'
        else:
            print 'start filration...'
            print '*'*70
            identifierFilration(dict1, dict2, level) 
