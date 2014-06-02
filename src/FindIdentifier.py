#!/usr/bin/env python

import DataHandler
import Interface
import SuffixTree
import ConfigParser
import sys
import gc

#gc.set_debug(gc.DEBUG_STATS | gc.DEBUG_LEAK)

def usage():
    print("Usage: [python_2.x_bin] FindIdentifier.py [.sqlite file1] [.sqlite file2] [level]")
    print("       or set up your own config file")

def printCommonString(sequences, seq, start, stop, occurance):
    print seq, '[' + str(start) + ':' + str(stop) + ']',
    print unichr(10084),'',
    print sequences[seq][start:stop],
    print unichr(10084),'',
    print sequences[seq][:start] +unichr(10073) + sequences[seq][start:stop] + \
          unichr(10073) + sequences[seq][stop:]

# FUNCTION:
#     generateHostList: Extract the host list from SQLite database given the constraints
# INPUT:
#     database1  - SQLite database file 1
#     database2  - SQLite database file 2
#     hostList   - The host list to be processed (Optional)
#     exceptList - The host list to be ignored during processing (Optional)
#     minHost    - The start number of the host (Optional)
#     maxHost    - The end number of the host (Optional)
# OUTPUT:
#     stringArrayDict1
#     stringArrayDict2
#     candidateHostList

def generateHostList(database1, database2, hostList = None, excepList = None,
                     minHost = None, maxHost = None):
    requestTokens1 = DataHandler.tokenDictFromFile(database1)
    stringArrayDict1 = requestTokens1.toStringArrayDict()
    print "Finish loading data from " + database1

    requestTokens2 = DataHandler.tokenDictFromFile(database2)
    stringArrayDict2 = requestTokens2.toStringArrayDict()
    print "Finish loading data from " + database2

    candidateHostList = set(stringArrayDict1.keys()).intersection(set(stringArrayDict2.keys()))

    if hostList:
        candidateHostList = candidateHostList.intersection(set(hostList))

    if excepList:
        candidateHostList = candidateHostList.difference(set(excepList))

    if minHost and maxHost and (minHost >= maxHost):
        raise IndexError, "The MIN value is larger than the MAX value"

    if maxHost:
        candidateHostList = list(candidateHostList)[:maxHost]

    if minHost:
        candidateHostList = list(candidateHostList)[minHost:]

    return stringArrayDict1, stringArrayDict2, list(candidateHostList)


# FUNCTION: filterOverlapValues
#     Clean up the repeated values in the two databases for the same host
# INPUT: 
#     stringArrayDict1   : Converted from RequestTokenDict object
#     stringArrayDict2   : Converted from RequestTokenDict object
#     candidateHostList  : The list of hosts to be processed(Optional)
# OUTPUT:
#     stringArrayDict1   : Updated from the input
#     stringArrayDict2   : Updated from the input
#     newHostList        : Remove the host with no sequences after filtering

def filterOverlapValues(stringArrayDict1, stringArrayDict2, hostList):
    newHostList = []
    for host in hostList:
        keys1, sequences1, reqId1 = stringArrayDict1[host]
        keys2, sequences2, reqId2 = stringArrayDict2[host]

        overlap = set(sequences1).intersection(set(sequences2))

        tokens1 = zip(keys1, sequences1, reqId1)
        tokens2 = zip(keys2, sequences2, reqId2)

        stringArrayDict1[host] = [list(l) for l in zip(*[t for t in tokens1 if t[1] not in overlap])]
        stringArrayDict2[host] = [list(l) for l in zip(*[t for t in tokens2 if t[1] not in overlap])]

        if (len(stringArrayDict1[host]) != 0 and 
            len(stringArrayDict2[host]) != 0):
            if (len(stringArrayDict1[host][1]) > 1 and 
                len(stringArrayDict2[host][1]) > 1):
                newHostList.append(host)

    return stringArrayDict1, stringArrayDict2, newHostList


# FUNCTION: identifierDictFromFile
#     Extract the identifiers from the stringArrayDict and given host list
# INPUT: 
#     stringArrayDict    : Converted from RequestTokenDict object
#     candidateHostList  : The list of hosts to be processed(Optional)
# OUTPUT:
#     identifierDict     : The dictionay of identifiers for the hosts

def identifierDictFromFile(stringArrayDict, candidateHostList = None,
                           minLength = 5, occurance = 0.5):

    identifiers = Interface.IdentifierDict()

    print('=' * 20 + 'Finding Sub-string Start' + '=' * 20)

    if candidateHostList:
        hostList = candidateHostList
    else:
        hostList = stringArrayDict.keys()

    numHosts = len(hostList)
    counterHost = 1
    for host in hostList:
        print("Host " + str(counterHost) + " / " + str(numHosts) + ": " + host)

        keys, sequences, reqId = stringArrayDict[host]
    
        print('The number of strings:' + str(len(sequences)))
        
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        print('Terminator is determined')

        print('Start buidling the tree....')
        print('-' * 70)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)
    
        # The stringTable is a 2D list. The format of each row is
        #     String, Start_position, End_position, Key, RequestId
        for shared in st.sharedSubstrings(reqId, minLength, occurance):
            stringTable = []
            for seq, start, stop, occurance in shared:
                stringTable.append([sequences[seq], start, stop, keys[seq], reqId[seq]])
    
            newIdentifier = Interface.Identifier(sequences[seq][start:stop], stringTable, occurance)
            identifiers.addToDict(host, newIdentifier)
    
        print('=' * 70)
        print('Done with host number:' + str(counterHost))
        print('Done with process identifiers object\n\n')

        counterHost += 1
        
        del st

    return identifiers

def identifierFiltration(iden1, iden2, hostList, level):
    print('*' * 70)
    print('Start identifier filration....')

    result = []
    resultDict1 = {}
    resultDict2 = {}
    #commonKey = getCommonKeys(iden1, iden2) 
    for host in hostList:
        # Filter out the host without identifiers
        if (host not in iden1.keys() or
            host not in iden2.keys()):
            continue

        # This is identifier list
        list1 = iden1[host]
        list2 = iden2[host]
        commonValue1 = []
        commonValue2 = []
        
        # Eliminate the duplicates:
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
        # Start to compare
        for i in range(len(list1)):
            for j in range(len(list2)):
                # If tables are similar
                if similarTable(list1[i].table, list2[j].table, level):
                    # If the identifier strings are different 
                    if list1[i].value != list2[j].value:
                        if host not in resultDict1.keys():
                            resultDict1[host] = []

                        if host not in resultDict2.keys():
                            resultDict2[host] = []

                        resultDict1[host].append(list1[i])
                        resultDict2[host].append(list2[j])
                        result.append([host, list1[i].value, list2[j].value])

    print '-----------------FINAL RESULT-----------------------'
    print '-'*70
    print '-'*70
    print '-'*70
    for i in range(len(result)):
        print(result[i][0])
        print(result[i][1])
        print(result[i][2])
    print '-'*70 
    print '-'*70 

    return resultDict1, resultDict2

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
    position2 = []

    key1 = []
    key2 = []

    for i in range(len1):
        position1.append(table1[i][1])
        key1.append(table1[i][3])
    for i in range(len2):
        position2.append(table2[i][1])
        key2.append(table2[i][3])
        
    if level == 1:
        # If the identifiers happens to be from same key
        for item in key1:
            if item in key2:
                return True
        else:
            return False
    if level == 2:
        # If the identifier happes to be from same key and same start position
        for item in key1:
            if item in key2:
                index1 = key1.index(item)
                index2 = key2.index(item)
                if position1[index1] == position2[index2]:
                    return True
        else:
            return False

def writeCfg(resultDict, filename):
    config = ConfigParser.RawConfigParser()
    for host in resultDict.keys():
        idList = resultDict[host]
        idValues = [v.value for v in idList]
        idKeys = [list(zip(*v.table)[3]) for v in idList]
        idRequests = [list(zip(*v.table)[4]) for v in idList]

        config.add_section(host)
        config.set(host, 'identifiers', idValues)
        config.set(host, 'keys', idKeys)
        config.set(host, 'requests', idRequests)

        with open(filename, 'wb') as configfile:
            config.write(configfile)

if __name__ == "__main__":

    #if len(sys.argv) != 4:
        #usage()
    #else:
    config = ConfigParser.RawConfigParser()
    config.read('identifier.cfg')
    database1 = config.get('databases', 'database1')
    database2 = config.get('databases', 'database2')
    level = config.getint('identifiers', 'level')
    try:
        hostList = eval(config.get('hosts', 'host_list'))
    except:
        hostList = None

    try:
        excepList = eval(config.get('hosts', 'excep_list'))
    except:
        excepList = None

    print("Generating the available host list.....")
    stringArrayDict1, stringArrayDict2, candidateHostList = generateHostList(database1, database2,
                                                                             hostList = hostList,
                                                                             excepList = excepList)

    print("Cleaning the overlap values of the two databases....")
    stringArrayDict1, stringArrayDict2, candidateHostList = filterOverlapValues(stringArrayDict1,
                                                                                stringArrayDict2,
                                                                                candidateHostList)
    if candidateHostList == []:
        raise IndexError, "The host list is empty!"

    iden1 = identifierDictFromFile(stringArrayDict1, candidateHostList)
    iden2 = identifierDictFromFile(stringArrayDict2, candidateHostList)
    dict1 = iden1.identifierDict
    dict2 = iden2.identifierDict

    if (level != 1) and (level != 2) :
        print 'Only level 1 and 2 are implemented'
    else:
        print('Start filtration...')
        print('*' * 70)
        resDict1, resDict2 = identifierFiltration(dict1, dict2, candidateHostList, level) 

        # Write the results into config files
        print('Writing the identifiers to identifier_user1.cfg')
        writeCfg(resDict1, 'identifier_user1.cfg')

        print('Writing the identifiers to identifier_user2.cfg')
        writeCfg(resDict2, 'identifier_user2.cfg')
