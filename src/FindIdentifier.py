#!/usr/bin/env python

import DataHandler
import Interface
import SuffixTree
import sys

def usage():
    print("Usage: [python_bin] FindIdentifier.py [.sqlite file]")

def main():

    if len(sys.argv) != 2:
        usage()
        return

    database = sys.argv[1]

    requestTokens = DataHandler.tokenDictFromFile(database)
    stringArrayDict = requestTokens.toStringArrayDict()

    print '=' * 20 + 'Finding Sub-string Start' + '=' * 20
    for host in stringArrayDict.keys():
    #for host in ['google.com']:
        sequences, reqId = stringArrayDict[host]
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)

        for shared in st.sharedSubstrings(reqId, 5, 0.5):
            print '-' * 70
            
            for seq, start, stop in shared:
                print seq, '[' + str(start) + ':' + str(stop) + ']',
                print unichr(10084),'',
                print sequences[seq][start:stop],
                print unichr(10084),'',
                print sequences[seq][:start] +unichr(10073) + sequences[seq][start:stop] + \
                      unichr(10073) + sequences[seq][stop:]

        print '='*70
    
        print 'done.\n\n'

if __name__ == "__main__":
    main()
