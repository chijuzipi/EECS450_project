import sys
reload(sys)
import _suffix_tree
sys.setdefaultencoding("utf-8")

def postOrderNodes(node):
    '''Iterator through all nodes in the sub-tree rooted in node in
    post-order.'''
    def dfs(n):
        c = n.firstChild
        while c is not None:
            for m in dfs(c):
                yield m
            c = c.next
        yield n
    for n in dfs(node):
        yield n

def preOrderNodes(node):
    '''Iterator through all nodes in the sub-tree rooted in node in
    pre-order.'''
    def dfs(n):
        yield n
        c = n.firstChild
        while c is not None:
            for m in dfs(c):
                yield m
            c = c.next
    for n in dfs(node):
        yield n

def leaves(node):
    'Iterator through all leaves in the tree rooted in node.'
    for n in postOrderNodes(node):
        if n.isLeaf:
            yield n

def innerNodes(node):
    'Iterator through all inner nodes in the tree rooted in node.'
    for n in postOrderNodes(node):
        if not n.isLeaf:
            yield n

def children(node):
    'Iterate through all immediate children of node.'
    c = node.firstChild
    while c is not None:
        yield c
        c = c.next

# Scanning through the sequence, find a unique character which does not contained by the sequence
def getTerminator(sequences):
    for i in range(1, 128):
        if chr(i) in sequences:
            continue
        print 'The terminator is : ', chr(i)
        return i 
    print 'No terminator of 128 ASCII code can be used' 

def getUnicodeTerminator(sequences):
    for i in range(1000, 10000):
        for j in xrange(len(sequences)):
            if unichr(i) not in sequences[j]:
                print 'The terminator is : ', unichr(i)
                return i 
    print 'No terminator of Unicode can be used' 

def getTerminatorArray(sequences):
    termList = []
    for i in range(1, 128):
        if chr(i) not in sequences:
            termList.append(chr(i))
    if len(termList) > len(sequences):
        return termList
    else:
        return False

class SuffixTree(_suffix_tree.SuffixTree):

    """A higher-level wrapper around the C suffix tree type,
_suffix_tree.SuffixTree.  This class adds a few methods to the suffix
tree, methods that are more easily expressed in Python than in C, and
that can be written using the primitives exported from C.  """

    
    def __init__(self,s,t='$'):
        '''Build a suffix tree from the input string s. The string
must not contain the special symbol $.'''
        if t in s:
            raise Exception, "The suffix tree string must not contain terminal symbol!"
        _suffix_tree.SuffixTree.__init__(self,s,t)

    def generatePostOrderNodes(self):
        'Iterator through all nodes in the tree in post-order.'
        for n in postOrderNodes(self.root):
            yield n

    def generatePreOrderNodes(self):
        'Iterator through all nodes in the tree in pre-order.'
        for n in preOrderNodes(self.root):
            yield n

    def generateLeaves(self):
        'Iterator through all leaves in the tree.'
        for n in leaves(self.root):
            yield n

    def generateInnerNodes(self):
        'Iterator through all leaves in the tree.'
        for n in innerNodes(self.root):
            yield n

    # set class properties
    postOrderNodes = property(generatePostOrderNodes, None, None,
                              "postOrderNodes")
    preOrderNodes = property(generatePreOrderNodes, None, None,
                             "preOrderNodes")
    
    leaves = property(generateLeaves, None, None, "leaves")
    innerNodes = property(generateInnerNodes, None, None, "innerNodes")

class GeneralisedSuffixTree(SuffixTree):

    """A suffix tree for a set of strings."""
# specify what terminator will use
    def __init__(self, sequences, terminator):        
        '''Build a generalised suffix tree. 
           The strings must not contain the special
           symbols $ or ascii numbers from 1 to the
           number of sequences.'''

        self.sequences = sequences
        self.startPositions = [0]
        concatString = u''

        for i in xrange(len(sequences)):
            if unichr(terminator + i + 1) in sequences[i]:
                print("The suffix tree string must not contain chr(%d)!"%(terminator + i + 1))
            concatString += sequences[i] + unichr(terminator + i + 1)
            self.startPositions += [len(concatString)]

        self.startPositions += [self.startPositions[-1] + 1] # empty string
        self.sequences += ['']
        #print concatString
        #print sequences
        # The whole concatString will also concated with a terminator "terminator"

        SuffixTree.__init__(self, concatString, unichr(terminator))
        self._annotateNodes()


    def _translateIndex(self,idx):
        'Translate a concat-string index into a (stringNo,idx) pair.'
        for i in xrange(len(self.startPositions) - 1):
            if self.startPositions[i] <= idx < self.startPositions[i + 1]:
                return (i,idx-self.startPositions[i])
        raise IndexError, "Index out of range: "+ str(idx)

    def _annotateNodes(self):
        for n in self.postOrderNodes:
            if n.isLeaf:
                seq,idx = self._translateIndex(n.index)
                n.pathIndices = [(seq, idx)]
                n.sequences = [seq]
            else:
                pathIndices = [] ; sequences = []
                c = n.firstChild
                while c is not None:
                    pathIndices += c.pathIndices
                    sequences += c.sequences
                    c = c.next

                seqsInSubtree = {}
                for s in sequences:
                    seqsInSubtree[s] = 1

                n.pathIndices = pathIndices
                n.sequences = [s for s in seqsInSubtree]

    # Add minOccurance input, this function return iterator which contain all the 
    # information for the shared substring. The sub-sub strings are filtered.  
    def sharedSubstrings(self, requestId, minLength = 0, minOccurance = 1):
        #Iterator through shared sub-strings.
        #Returned as a list of triples (sequence,from,to).
        nArray = []
        numRequest = len(set(requestId))
        print "The number of requests is " + str(numRequest)

        # Every inner node will represent a shared
        # substring if its sequences more than 1  
        for n in self.innerNodes:
            if len(n.sequences) <= len(self.sequences) - 1:
                # s is the shared string
                s = n.pathLabel
                requestIdList = []
                for (seq, idx) in n.pathIndices:
                    requestIdList.append(requestId[seq])
    
                occurance = len(set(requestIdList)) / float(numRequest)
                if (len(s) >= minLength) and (occurance >= minOccurance):
                    nArray.append((n, occurance))     
                    #l = len(n.pathLabel)
                    #yield [(seq, idx, idx + l, occurance) for (seq, idx) in n.pathIndices]

        for n, occurance in self.filterSubSubstrings(nArray):
            l = len(n.pathLabel)
            yield [(seq, idx, idx + l, occurance) for (seq, idx) in n.pathIndices]
            
    def filterSubSubstrings(self, nArray):
        resultArray = []
        toAppend = True
        for n, occurance in nArray:
            for refNode, refOccurance in nArray:
                if (n.pathLabel != refNode.pathLabel and
                    n.pathLabel in refNode.pathLabel):
                    toAppend = False
                    break

            if toAppend:
                resultArray.append((n, occurance))

            toAppend = True

        return resultArray

def generalised_test():

    print 'GENERALISED TEST'
    sequences = ['aaaaa111cccc', 'aaaaa111cccc', 'aaaa333cccc']
    #terminatorArray = getTerminatorArray(sequences)
    #print 'length of the terminatorArray',len(terminatorArray)
    #st = GeneralisedSuffixTree(sequences, terminatorArray)
    terminator = getUnicodeTerminator(sequences)
    st = GeneralisedSuffixTree(sequences, terminator)
    for shared in st.sharedSubstrings([1, 1, 1], 2, 0):
        print '-'*70
        for seq,start,stop in shared:
            print seq, '['+ str(start) + ':' + str(stop) + ']',
            print sequences[seq][start:stop],
            print sequences[seq][:start]+'|'+sequences[seq][start:stop]+\
                  '|'+sequences[seq][stop:]
    print '='*70

    print 'done.\n\n'


def test():
    generalised_test()


if __name__ == '__main__':
    test()

