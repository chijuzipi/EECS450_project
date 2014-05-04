import copy
import interface
import values_from_token
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

def getTerminator(sequences):
    for i in range(1, 128):
        if chr(i) in sequences[i]:
            continue
        print 'the terminator is : ', chr(i)
        return i
    print 'no terminator of 128 ASCII code can be used' 

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
        'Iterator through all inner nodes in the tree.'
        for n in innerNodes(self.root):
            yield n

    def generateQuasiRootNode(self):
        'Iterator through all node that immediately follow the root'
        for n in children(self.root):
            yield n

    # set class properties
    postOrderNodes = property(generatePostOrderNodes, None, None,
                              "postOrderNodes")
    preOrderNodes = property(generatePreOrderNodes, None, None,
                             "preOrderNodes")
    
    leaves = property(generateLeaves, None, None, "leaves")
    innerNodes = property(generateInnerNodes, None, None, "innerNodes")
    quasiRootNodes = property(generateQuasiRootNode, None, None, "QuasiRootNode")

class GeneralisedSuffixTree(SuffixTree):

    """A suffix tree for a set of strings."""

    def __init__(self,sequences, terminator):        
        '''Build a generalised suffix tree.  The strings must not
contain the special symbols $ or ascii numbers from 1 to the number of
sequences.'''

        self.sequences = sequences
        self.startPositions = [0]
        concatString = ''
        for i in xrange(len(sequences)):
            if unichr(i+1+terminator) in sequences[i]:
                raise "The suffix tree string must not contain chr(%d)!"%(i+1)
            concatString += sequences[i]+chr(i+1+terminator)
            self.startPositions += [len(concatString)]

        self.startPositions += [self.startPositions[-1]+1] # empty string
        self.sequences += ['']
        SuffixTree.__init__(self,concatString, chr(terminator))#F0000
        self._annotateNodes()

    
    def _translateIndex(self,idx):
        'Translate a concat-string index into a (stringNo,idx) pair.'
        for i in xrange(len(self.startPositions)-1):
            if self.startPositions[i] <= idx < self.startPositions[i+1]:
                return (i,idx-self.startPositions[i])
        raise IndexError, "Index out of range: "+str(idx)

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
    
    def sharedSubstrings(self, minimumLength=0, minimumOccurance=1):
        '''Iterator through shared sub-strings.  Returned as a list of triples
 (sequence,from,to).'''
        seqLen = len(self.sequences)
        #every inner node will represent a shared substring if its sequences more than 1  
        for n in self.innerNodes:
            if len(n.sequences) >= minimumOccurance*(seqLen-1):
                l = len(n.pathLabel)
                if l >= minimumLength:
                    print 'node is qualified'
                    yield [(seq, idx, idx+l) for (seq,idx) in n.pathIndices]
    
    def sharedSubstrings2(self, minimumLength=0, minimumOccurance=1):
        '''Iterator through shared sub-strings.  Returned as a list of triples
 (sequence,from,to).'''
        seqLen = len(self.sequences)
        nArray = []
        #every inner node will represent a shared substring if its sequences more than 1  
        for n in self.innerNodes:
            if len(n.sequences) >= minimumOccurance*(seqLen-1):
                l = len(n.pathLabel)
                if l >= minimumLength:
                    #print 'n path indices are :',  n.pathIndices
                    nArray.append(n)     
        output = self.getProcessNodeArray(nArray)
        for nf in output:
            l2 = len(nf.pathLabel)
            yield [(seq, idx, idx+l2) for (seq,idx) in nf.pathIndices]
            

    def getProcessNodeArray(self, nArray):
        nArray2 = nArray[:] 
        for i in range(len(nArray)):
            for j in range(i+1, len(nArray)):
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
                    
                
def process_test():
    print 'PROCESS TEST'
    #sequences = ['aaaaa111cccc', 'aaaaa222cccc', 'aaaa333cccc']

    data = open('../data/04.18/taobao.data', 'r')
    hostSet = interface.RequestTokenSet()
    for line in data.readlines():
        key, value, host, request_id = line.split(" ")
        a = interface.RequestToken(int(request_id), key, value, host, host)
        hostSet.add(a)
    requestString = values_from_token.stringFromTokenSet(hostSet)
    sequences = [value for value in requestString.values()]

    terminator = getTerminator(sequences)
    st = GeneralisedSuffixTree(sequences, terminator)
    print '-'*70
    for shared in st.sharedSubstrings2(3, 0.5):
        for seq,start,stop in shared:
            print seq, '['+str(start)+':'+str(stop)+']',
            print sequences[seq][start:stop],
            print sequences[seq][:start]+'|'+sequences[seq][start:stop]+\
                  '|'+sequences[seq][stop:]
        print '------>'
    print '='*70
    
def generalised_test():
    print 'GENERALISED TEST'
    sequences = ['aaaaa111cccc@#$', 'aaaaa222cccc@#$*()', '!@#$%^&*()_+{}":?><"']
    terminator = getTerminator(sequences)
    st = GeneralisedSuffixTree(sequences, terminator)
    print '-'*70
    for shared in st.sharedSubstrings(3, 0.5):
        for seq,start,stop in shared:
            print seq, '['+str(start)+':'+str(stop)+']',
            print sequences[seq][start:stop],
            print sequences[seq][:start]+'|'+sequences[seq][start:stop]+\
                  '|'+sequences[seq][stop:]
        print '------>'
    print '='*70

    print 'done.\n\n'

def test():
    generalised_test()
    process_test()

if __name__ == '__main__':
    test()
