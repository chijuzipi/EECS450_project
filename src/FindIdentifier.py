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
        numRequest = requestTokens.getRequestNumber(host)
        print("The number of request for " + host +
              " is " + str(numRequest) )

        sequences = stringArrayDict[host]
        terminator = SuffixTree.getUnicodeTerminator(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)

        for shared in st.sharedSubstrings2(numRequest, 5, 0.5):
            print '-' * 70
            print "The occurance is " + str(sum(1 for x in shared) / float(numRequest));
            for seq,start,stop in shared:
                print seq, '[' + str(start) + ':' + str(stop) + ']',
                print sequences[seq][start:stop],
                print sequences[seq][:start] + '|' + sequences[seq][start:stop] + \
                      '|' + sequences[seq][stop:]
        print '='*70
    
        print 'done.\n\n'

if __name__ == "__main__":
    main()
