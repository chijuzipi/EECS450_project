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

def identifierDictFromFile(database, time):
    requestTokens = DataHandler.tokenDictFromFile(database)
    stringArrayDict = requestTokens.toStringArrayDict()

    identifiers = Interface.IdentifierDict()
    hostList = []

    print('=' * 20 + 'Finding Sub-string Start' + '=' * 20)
    hostMin = time * 100 - 99
    hostMax = time * 100
    numHosts = len(stringArrayDict.keys())
    counterHost = 1
    for host in sorted(stringArrayDict.keys()):
        counterHost += 1
        if counterHost < hostMin: 
            continue
        if counterHost > hostMax: 
            return identifiers, hostList
        if host == 'google.com':
            continue
    #for host in ['alibaba.com', 'ameba.jp', 'sstatic.net', 'scorecardresearch.com', 'xvideos.com','twitter.com','doubleclick.net']:
    #for host in ['alibaba.com']:
      #  print("Host " + str(counterHost) + " / " + str(numHosts) + ": " + host)
        hostList.append(host)
        keys, sequences, reqId = stringArrayDict[host]
    
        print 'domain name:', host
        print 'how many strings:', len(sequences)  
        
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        print 'terminator is determined'
        print 'start buidling the tree....'
        print '@' *70
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
    
        del st
        print 'done with host number:', counterHost
        print('Done with process identifiers object\n\n')

    return identifiers, hostList

def identifierDictFromFilewithHost(database, hostList):
    requestTokens = DataHandler.tokenDictFromFile(database)
    stringArrayDict = requestTokens.toStringArrayDict()

    identifiers = Interface.IdentifierDict()

    print('=' * 20 + 'Finding Sub-string Start' + '=' * 20)

    numHosts = len(stringArrayDict.keys())
    counterHost = 1
    List = []
    for host in stringArrayDict.keys():
        if host in hostList:
            counterHost += 1
            List.append(host)
            keys, sequences, reqId = stringArrayDict[host]
        
            print 'domain name:', host
            print 'how many strings:', len(sequences)  
            
            terminator = SuffixTree.getUnicodeTerminator(sequences)
            print 'terminator is determined'
            print 'start buidling the tree....'
            print '@' *70
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
        
            del st
            print 'done with host number:', counterHost
            print('Done with process identifiers object\n\n')

    return identifiers, List

def identifierFilration(iden1, iden2, level):
    print '*'*70
    print 'start identifier filration....'
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
    print '-----------------FINAL RESULT-----------------------'
    print '-'*70
    print '-'*70
    print '-'*70
    for i in range(len(result)):
        #f1.write(result[i][0])
        #f1.write(result[i][1])
        #f1.write(result[i][2])
        print(result[i][0])
        print(result[i][1])
        print(result[i][2])
    print '-'*70 
    print '-'*70 

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

    if len(sys.argv) != 5:
        usage()
    else:
        time  =  int(sys.argv[4])
        f1 = open('bash_result2.txt', 'a')
        sys.stdout = f1
        iden1, hostList1 = identifierDictFromFile(sys.argv[1], time)
        iden2, hostList2 = identifierDictFromFilewithHost(sys.argv[2], hostList1)
        dict1 = iden1.identifierDict
        dict2 = iden2.identifierDict
        #how to get the table?
        level = int(sys.argv[3])
        if (level != 1) and (level != 2) :
            print 'only level 1 and 2 are implemented'
        else:
            print 'start filration...'
            print '*'*70
            identifierFilration(dict1, dict2, level) 
        f1.close()
#            for host in hostList1:
#                if host not in hostList2:
#                    print 'this host1 not in host2:', host
#            for host2 in hostList2:
#                if host2 not in hostList1:
#                    print 'this host2 not in host 1:', host2
