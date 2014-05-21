#!/usr/bin/env python

import DataHandler
import Interface
import SuffixTree
import sys

def usage():
    print("Usage: [python_2.x_bin] FindIdentifier.py [.sqlite file]")

def printCommonString(sequences, seq, start, stop, occurance):
    print seq, '[' + str(start) + ':' + str(stop) + ']',
    print unichr(10084),'',
    print sequences[seq][start:stop],
    print unichr(10084),'',
    print sequences[seq][:start] +unichr(10073) + sequences[seq][start:stop] + \
          unichr(10073) + sequences[seq][stop:]

def main():

    if len(sys.argv) != 2:
        usage()
        return

    database = sys.argv[1]

    requestTokens = DataHandler.tokenDictFromFile(database)
    stringArrayDict = requestTokens.toStringArrayDict()

    identifiers = Interface.IdentifierDict()
    print '=' * 20 + 'Finding Sub-string Start' + '=' * 20
    for host in stringArrayDict.keys():
    #for host in ['google.com']:
        keys, sequences, reqId = stringArrayDict[host]
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)

        for shared in st.sharedSubstrings(reqId, 5, 0.5):
            print '-' * 70
            stringTable = []
            for seq, start, stop, occurance in shared:
                stringTable.append([sequences[seq], start, stop, keys[seq], reqId[seq]])
                #printCommonString(sequences, seq, start, stop)

            newIdentifier = Interface.Identifier(sequences[seq][start:stop], stringTable, occurance)
            print newIdentifier
            identifiers.addToDict(host, newIdentifier)

        print '='*70
    
        print 'done.\n\n'

if __name__ == "__main__":
    main()
