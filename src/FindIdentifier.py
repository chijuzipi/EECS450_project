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

    print '=' * 70 + 'Finding Sub-string Start'
    for host in stringArrayDict.keys():
    #for host in ["xinhuanet.com"]:
        numRequest = requestTokens.getRequestNumber(host)
        print("The number of request for " + host +
              " is " + str(numRequest) )

        sequences = stringArrayDict[host]
        terminator = SuffixTree.getTerminatorArray(sequences)
        st = SuffixTree.GeneralisedSuffixTree(sequences, terminator)

        for shared in st.sharedSubstrings2(numRequest, 5, 0.5):
            print '-' * 70
            for seq,start,stop in shared:
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
