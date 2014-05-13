
import _suffix_tree

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

# scanning through the sequence, find a unique character which does not contained by the sequence
def getTerminator(sequences):
    for i in range(1, 128):
        if chr(i) in sequences:
            continue
        print 'the terminator is : ', chr(i)
        return i 
    print 'no terminator of 128 ASCII code can be used' 

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
            raise "The suffix tree string must not contain terminal symbol!"
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
        '''Build a generalised suffix tree.  The strings must not
contain the special symbols $ or ascii numbers from 1 to the number of
sequences.'''

        self.sequences = sequences
        self.startPositions = [0]
        concatString = ''
        if not terminator:
            print 'use fixed terminator'
            for i in xrange(len(sequences)):
                concatString += sequences[i] + unichr(2) 
                self.startPositions += [len(concatString)]

            self.startPositions += [self.startPositions[-1]+1] # empty string
            self.sequences += ['']
            SuffixTree.__init__(self, concatString, unichr(1))
        else: 
            print 'use array'
            print terminator
            #print 'length of the array:', len(terminator)
            for i in xrange(len(sequences)):
                concatString += sequences[i] + terminator[i+1] 
                self.startPositions += [len(concatString)]

            self.startPositions += [self.startPositions[-1]+1] # empty string
            self.sequences += ['']
            SuffixTree.__init__(self, concatString, terminator[0])
        self._annotateNodes()


    def _translateIndex(self,idx):
        'Translate a concat-string index into a (stringNo,idx) pair.'
        for i in xrange(len(self.startPositions)-1):
            if self.startPositions[i] <= idx < self.startPositions[i+1]:
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

    def sharedSubstrings(self,minimumLength=0):
        '''Iterator through shared sub-strings.  Returned as a list of triples
 (sequence,from,to).'''
        for n in self.innerNodes:
            if len(n.sequences) == len(self.sequences) - 1:
                l = len(n.pathLabel)
                if l >= minimumLength:
                    yield [(seq, idx, idx+l) for (seq,idx) in n.pathIndices]

    # Add minOccurance input, this function return iterator which contain all the 
    # information for the shared substring. The sub-sub strings are filtered.  
    def sharedSubstrings2(self, numRequest, minLength = 0, minOccurance = 1):
        '''Iterator through shared sub-strings.  Returned as a list of triples
 (sequence,from,to).'''
        seqLen = len(self.sequences)
        nArray = []
        # Every inner node will represent a shared
        # substring if its sequences more than 1  
        for n in self.innerNodes:
            #if len(n.sequences) >= minOccurance * (seqLen - 1):
            if len(n.sequences) >= minOccurance * numRequest:
                l = len(n.pathLabel)
                if l >= minLength:
                    #print 'n path indices are :',  n.pathIndices
                    nArray.append(n)     
        output = self.getProcessNodeArray(nArray)
        for nf in output:
            l2 = len(nf.pathLabel)
            yield [(seq, idx, idx+l2) for (seq,idx) in nf.pathIndices]
            
#---------------------------for filter sub-sub strings---------------------
    def getProcessNodeArray(self, nArray):
        nArray2 = nArray[:] 
        for i in xrange(len(nArray)):
            for j in xrange(i + 1, len(nArray)):
                isSubclass, node = self.isSubclass(nArray[i], nArray[j])
                if isSubclass:
                    #print 'these are sub classes:', node.pathIndices
                    if node in nArray2:
                        nArray2.remove(node)
        return nArray2 

    def isSubclass(self, n1, n2):
        list1 = n1.pathIndices
        l1 = len(n1.pathLabel)
        list2 = n2.pathIndices
        l2 = len(n2.pathLabel)
        isn1 = False
        isn2 = False
        seqlist1 = []
        seqlist2 = []
        for i in range(len(list1)):
            for j in range(len(list2)):
                seqlist1.append(list1[i][0])
                seqlist2.append(list2[j][0])
                if list1[i][0] == list2[j][0]:
                    if (list1[i][1] <= list2[j][1]) & ((list1[i][1] + l1) >= (list2[j][1] + l2)):
                        isn2 = True
                    elif (list1[i][1] >= list2[j][1]) & ((list1[i][1] + l1) <= (list2[j][1] + l2)):
                        isn1 = True
                    else: 
                        return False, n2
                
        if len(set(seqlist1)) != len(set(seqlist2)):
            return False, n2
        if isn2: 
            return True, n2
        if isn1: 
            return True, n1
        return False, n2

#----------------------------------------------------------------------------------
#----------------------------------------------------------------------------------


def generalised_test():

    print 'GENERALISED TEST'
    sequences = ['aaaaa111cccc', 'aaaaa111cccc', 'aaaa333cccc']
    terminatorArray = getTerminatorArray(sequences)
    print 'length of the terminatorArray',len(terminatorArray)
    st = GeneralisedSuffixTree(sequences, terminatorArray)
    for shared in st.sharedSubstrings2(3, 3):
        print '-'*70
        for seq,start,stop in shared:
            print seq, '['+str(start)+':'+str(stop)+']',
            print sequences[seq][start:stop],
            print sequences[seq][:start]+'|'+sequences[seq][start:stop]+\
                  '|'+sequences[seq][stop:]
    print '='*70

    print 'done.\n\n'


def test():
    #simple_test()
    generalised_test()


if __name__ == '__main__':
    test()

