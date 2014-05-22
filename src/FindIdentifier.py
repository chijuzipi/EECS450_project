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
    #for host in ['convertro.com']:
        print("Host " + str(counterHost) + " / " + str(numHosts) + ": " + host)
        keys, sequences, reqId = stringArrayDict[host]
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)

        for shared in st.sharedSubstrings(reqId, 5, 0.5):
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
        del st
        print('Done.\n\n')

    return identifiers

#def identifierFilration(iden1, iden2, level):
    #result = Interface.IdentifierDict()
    #commonKey = iden1.Keys.Intersect(iden2.Keys)
    #for host in commonKey:
        #list1 = iden1[host]
        #list2 = iden2[host]
        #for i in range(len(list1)):
            #for j in range(len(list2)):
                ##if tables are similar
                #if similar(list1[i][1], list2[j][1], level):
                    ##if the identifier strings are different 
                    #if list1[i][0] != list2[j][0]:
                        #result.addToDict(host, list1[i][0])
    #print result
    #return result
    
#def similar(table1, table2, level):
    #if level == 1:
        #if table1 == table2:
            #return True
        #elif:
            #return False
    #if level == 2:
        #if table1[3] == table2[3]:
            #return True
        #elif:
            #return False

if __name__ == "__main__":

    if len(sys.argv) != 2:
        usage()
    else:
        #iden1 = identifierDictFromFile(sys.argv[1])
        #iden2 = identifierDictFromFile(sys.argv[2])
        #level = int(sys.argv[3])
        #if (level != 1) or (level != 2) :
            #print 'only level 1 and 2 are implemented'
            #return
        #print 'start filration...'
        #print '*'*70
        #identifierFilration(iden1, iden2, level) 
        identifierDictFromFile(sys.argv[1])
