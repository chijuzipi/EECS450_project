#!/usr/bin/env python

import DataHandler
import Interface
import SuffixTree
import ConfigParser
import sys

def usage():
    print("Usage: [python_2.x_bin] FindIdentifier.py")
    print("       or set up your own config file")

def printCommonString(sequences, seq, start, stop, occurance):
    print seq, '[' + str(start) + ':' + str(stop) + ']',
    print unichr(10084),'',
    print sequences[seq][start:stop],
    print unichr(10084),'',
    print sequences[seq][:start] +unichr(10073) + sequences[seq][start:stop] + \
          unichr(10073) + sequences[seq][stop:]

# FUNCTION:
#     stringArrayDictFromFile: Extract the dict of strings from the database. Each key is host, each value is tuple
#     (key, sequence, request id)  
# INPUT:
#     database  - SQLite database
# OUTPUT:
#     A stringArrayDict corresponding to the input database

def stringArrayDictFromFile(database):
    requestTokens = DataHandler.tokenDictFromFile(database)
    return requestTokens.toStringArrayDict()


# FUNCTION:
#     generateHostList: Extract the host list from SQLite database given the constraints
# INPUT:
#     stringArrayDict1  - The stringArrayDict extracted from the first database
#     stringArrayDict2  - The stringArrayDict extracted from the second database
#     hostList          - The host list to be processed (Optional)
#     exceptList        - The host list to be ignored during processing (Optional)
#     minHost           - The start number of the host (Optional)
#     maxHost           - The end number of the host (Optional)
# OUTPUT:
#     candidateHostList - The generated candidate host list

def generateHostList(stringArrayDict1, stringArrayDict2,
                     hostList = None, excepList = None,
                     minHost = None, maxHost = None):

    candidateHostList = set(stringArrayDict1.keys()).intersection(set(stringArrayDict2.keys()))

    if hostList:
        candidateHostList = candidateHostList.intersection(set(hostList))

    if excepList:
        candidateHostList = candidateHostList.difference(set(excepList))

    # Some exceptions check for minHost and maxHost
    if minHost and maxHost and (minHost >= maxHost):
        raise IndexError, "The MIN value is larger than the MAX value"

    if maxHost:
        candidateHostList = list(candidateHostList)[:maxHost]

    if minHost:
        candidateHostList = list(candidateHostList)[minHost:]

    return list(candidateHostList)


# FUNCTION: filterOverlapValues
#     Clean up the repeated values in the two databases for the same host
# INPUT: 
#     stringArrayDict1   - Converted from RequestTokenDict object
#     stringArrayDict2   - Converted from RequestTokenDict object
#     candidateHostList  - The list of hosts to be processed(Optional)
# OUTPUT:
#     stringArrayDict1   - Updated from the input
#     stringArrayDict2   - Updated from the input
#     newHostList        - Remove the host with no sequences after filtering

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
#     Extract the identifiers from the stringArrayDict and given host list with generalized suffix tree algorithms 
# INPUT: 
#     stringArrayDict    - Converted from RequestTokenDict object
#     candidateHostList  - The list of hosts to be processed(Optional)
#     minLength          - The minimum length of the common string(Default value is 5)
#     occurance          - The minimum occurance of the common string among the requestes(Default values is 0.5)
# OUTPUT:
#     identifierDict     - The dictionay of identifiers for the hosts

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
                printCommonString(sequences, seq, start, stop, occurance)

            print '-' * 70
    
            newIdentifier = Interface.Identifier(sequences[seq][start:stop], stringTable, occurance)
            identifiers.addToDict(host, newIdentifier)
    
        print('=' * 70)
        print('Done with host number:' + str(counterHost))
        print('Done with process identifiers object\n\n')

        counterHost += 1
        
        del st

    return identifiers

# FUNCTION: identifierFiltration
#     Compare two common strings found in two database, to tell if they have similary property table but different
#     string characters.  
# INPUT: 
#     iden1       - The dictionary stored in the identifierDict object from the first database
#     iden2       - The dictionary stored in the identifierDict object from the second database
#     hostList    - The list of hosts to be processed
#     level       - Different levels of comparison.
# OUTPUT:
#     resultDict1 - The result dictionary of the first database
#     resultDict2 - The result dictionary of the second database

def identifierFiltration(iden1, iden2, hostList, level):
    print('*' * 70)
    print('Start identifier filration....')

    result = []
    resultDict1 = {}
    resultDict2 = {}

    for host in hostList:
        # Filter out the host without identifiers
        if (host not in iden1.keys() or
            host not in iden2.keys()):
            continue

        # Get the identifier list
        idList1 = iden1[host]
        idList2 = iden2[host]
        
        # Eliminate the duplicates identifiers between two databases
        valueList1 = [i.value for i in idList1]
        valueList2 = [i.value for i in idList2]
        commonValue = set(valueList1).intersection(set(valueList2))

        list1 = [i for i in idList1 if i.value not in commonValue]
        list2 = [i for i in idList2 if i.value not in commonValue]
            
        # Start to compare
        for id1 in list1:
            for id2 in list2:
                # If tables are similar and the identifier strings are different 
                if (similarTable(id1.table, id2.table, level) and
                    id1.value != id2.value):
                    if host not in resultDict1.keys():
                        resultDict1[host] = []

                    if host not in resultDict2.keys():
                        resultDict2[host] = []

                    if id1 not in resultDict1[host]:
                        resultDict1[host].append(id1)

                    if id2 not in resultDict2[host]:
                        resultDict2[host].append(id2)

                    result.append([host, id1.value, id2.value])

    # Print out the result and return the dictionaries
    print '---------------------- FINAL RESULT -----------------------'
    print '-' * 70
    print '-' * 70
    print '-' * 70
    for i in range(len(result)):
        print(result[i][0])
        print(result[i][1])
        print(result[i][2])
    print '-' * 70 
    print '-' * 70 

    return resultDict1, resultDict2

def similarTable(table1, table2, level):
    keyPos1 = []
    keyPos2 = []

    for row in table1:
        keyPos1.append((row[1], row[3]))

    for row in table2:
        keyPos2.append((row[1], row[3]))
        
    if level == 1:
        # If the identifiers happens to be from same key
        for item in zip(*keyPos1)[0]:
            if item in zip(*keyPos2)[0]:
                return True
        return False

    if level == 2:
        # If the identifier happes to be from same key and same start position
        for item in keyPos1:
            if item in keyPos2:
                return True
        return False

# FUNCTION:
#     getHostConstraints: Read the constraints parameters from the config file
# INPUT:
#     config   - The ConfigParse object associated with the config file
#     keyword  - The parameter name in the config file
# OUTPUT:
#     constraint - The value of the constraint parameter

def getHostConstraints(config, keyword):
    validKeyword = ["host_list", "excep_list", "min_host", "max_host"]
    if keyword not in validKeyword:
        raise ValueError, "The keyword " + keyword + " is not valid!"

    try:
        constraint = eval(config.get("hosts", keyword))
    except:
        print("The " + keyword + " is not found, use None instead")
        constraint = None

    return constraint


# FUNCTION:
#     writeCfg: Write the identifier comparison results into a config file
# INPUT:
#     resultDict - A dictionary stored the identifier information
#     filename   - The config file to write

def writeCfg(resultDict, filename):
    print('Writing the identifiers to ' + filename)

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

    if len(sys.argv) == 1:
        cfgFile = "identifier.cfg"
    elif len(sys.argv) == 2:
        cfgFile = sys.argv[1]
    else:
        usage()
        sys.exit(0)


    # ----------------------------------------------
    # Read the parameters from the given config file
    # ----------------------------------------------
    config = ConfigParser.RawConfigParser()
    config.read(cfgFile)

    database1 = config.get('databases', 'database1')
    database2 = config.get('databases', 'database2')

    hostList = getHostConstraints(config, 'host_list')
    excepList = getHostConstraints(config, 'excep_list')
    minHost = getHostConstraints(config, 'min_host')
    maxHost = getHostConstraints(config, 'max_host')

    level = config.getint('identifiers', 'level')
    if (level != 1) and (level != 2) :
        raise ValueError, 'Only level 1 and 2 filtration are implemented'


    # ----------------------------------------------
    # Begin to process the databases
    # ----------------------------------------------
    stringArrayDict1 = stringArrayDictFromFile(database1)
    print("Finish processing " + database1 + '\n')

    stringArrayDict2 = stringArrayDictFromFile(database2)
    print("Finish processing " + database2 + '\n')


    # -------------------------------------------------
    # Update the host list according to the constraints
    # -------------------------------------------------
    print("Generating the available host list.....\n")
    candidateHostList = generateHostList(stringArrayDict1, stringArrayDict2,
                                         hostList = hostList, excepList = excepList)

    print("Cleaning the overlap values of the two databases....\n")
    stringArrayDict1, stringArrayDict2, candidateHostList = filterOverlapValues(stringArrayDict1,
                                                                                stringArrayDict2,
                                                                                candidateHostList)
    if candidateHostList == []:
        raise ValueError, "The host list is empty!"


    # --------------------------------------
    # Find the identifiers for each database
    # --------------------------------------
    iden1 = identifierDictFromFile(stringArrayDict1, candidateHostList)
    iden2 = identifierDictFromFile(stringArrayDict2, candidateHostList)
    dict1 = iden1.identifierDict
    dict2 = iden2.identifierDict


    # ---------------------------------------
    # Filter out the identifers by comparison
    # ---------------------------------------
    print('Start identifier filtration...')
    print('*' * 70)
    resDict1, resDict2 = identifierFiltration(dict1, dict2, candidateHostList, level) 


    # --------------------------------
    # Write the results into cfg files
    # --------------------------------
    writeCfg(resDict1, 'identifier_user1.cfg')
    writeCfg(resDict2, 'identifier_user2.cfg')
