# FIT3155 Assignment 2 Task 1
# Name: Chong Chiu Gin
# Student ID: 28842022

import sys

class Node:
    """
    Class for Node objects in suffix tree.
    Each node stores start and end index of the incoming edge
    instead of storing characters on edge (Trick 2 Edge representation).
    """

    def __init__(self):
        self.children = [None for x in range(256)]
        self.suffixlink = None
        self.start = None
        self.end = None
        self.index = -1  # to store the suffix index


class End:
    """
    Global end for end index of nodes.
    Useful for leaf nodes to automatically update their end index using increase() function
    """

    def __init__(self, end):
        self.end = end

    def increase(self):
        self.end = self.end + 1


class Active:
    """
    Represents the active pointer achieved by traversing the active length on active edge from active node
    """

    def __init__(self, node):
        self.actNode = node
        self.actEdge = -1  # stores the index of the first letter of edge
        self.actLength = 0


class Tree:
    """
    Class for the suffix tree
    """

    def __init__(self):
        self.root = None
        self.end = None  # for global end
        self.active = None  # to indicate active point
        self.nodeCreatedInSamePhase = None
        self.suffixarray = []

    def build_suffix_tree(self, string):

        string = string + '$'
        n = len(string)

        # initiliasing tree for root node and setting active node as root node
        # global end is set to -1 in the beginning
        self.root = Node()
        self.active = Active(self.root)
        self.end = End(-1)

        i = 0  # to represent current phase
        j = 0  # to represent index of current suffix needed to be added into tree
        while i < n:

            self.nodeCreatedInSamePhase = None  # set to None every time a new phase starts
            self.end.increase()  # this step does Rule 1 extension using Trick 1 (once a leaf, always a leaf) by extending all the leaves by one

            while j <= i:

                # if active length is 0, set active edge to the edge of current phase character
                if self.active.actLength == 0:
                    self.active.actEdge = i

                # if there is no outgoing edge for current phase character (string[i]), add new node for Rule 2
                if self.active.actNode.children[ord(string[self.active.actEdge])] is None:

                    # create new node, set its start and end index as well as suffix index
                    newNode = Node()
                    newNode.start = i
                    newNode.end = self.end
                    newNode.index = j
                    # link the newly created node to its parent
                    self.active.actNode.children[ord(string[self.active.actEdge])] = newNode

                    # if a node was previously created, set suffix link of that node to current active node
                    # then nodeCreatedInSamePhase is set to None because there is more node needing a suffix link
                    if self.nodeCreatedInSamePhase is not None:
                        self.nodeCreatedInSamePhase.suffixlink = self.active.actNode
                        self.nodeCreatedInSamePhase = None

                else:  # the outgoing edge for current phase character exists in tree already

                    # this activeNext variable is storing data type Node() and refers to the next node by travelling the active Edge from active Node
                    activeNext = self.active.actNode.children[ord(string[self.active.actEdge])]

                    edgeLen = activeNext.end.end - activeNext.start + 1  # length of the active edge, meaning the number of chars on the edge
                    # if active length is more than the number of chars in current active edge, keep setting new active node, edge and length until reaches right active point
                    # This is trick 3 (Skip count traversal)
                    if self.active.actLength >= edgeLen:
                        self.active.actNode = activeNext
                        self.active.actEdge += edgeLen
                        self.active.actLength -= edgeLen
                        continue

                    # current character exists in tree. This is Rule 3 extension
                    if string[activeNext.start + self.active.actLength] == string[i]:

                        #  if a node was previously created, set suffix link of that node to current active node
                        if self.nodeCreatedInSamePhase is not None and self.active.actNode != self.root:
                            self.nodeCreatedInSamePhase.suffixlink = self.active.actNode
                            self.nodeCreatedInSamePhase = None  # because we didn't create any new node

                        self.active.actLength += 1

                        # Trick 4 (showstopper) when encountered Rule 3 extension
                        break  # exit to next phase

                    # current character does not exist in tree. Create new internal node and leaf node for Rule 2 extension

                    # changing start index
                    oldStart = activeNext.start
                    activeNext.start += self.active.actLength

                    # create new internal node and set its start and end
                    internalNode = Node()
                    internalNode.start = oldStart
                    internalNode.end = End(oldStart + self.active.actLength - 1)

                    # create new leaf node and set its start and end
                    leafNode = Node()
                    leafNode.start = i
                    leafNode.end = self.end
                    leafNode.index = j

                    # linking all the children to the parent
                    internalNode.children[ord(string[activeNext.start])] = activeNext
                    internalNode.children[ord(string[leafNode.start])] = leafNode
                    self.active.actNode.children[ord(string[internalNode.start])] = internalNode

                    # if a node was previously created, set suffix link of that node to new internal node
                    # and then make new internal node as the current nodeCreatedInSamePhase
                    if self.nodeCreatedInSamePhase is not None:
                        self.nodeCreatedInSamePhase.suffixlink = internalNode
                    self.nodeCreatedInSamePhase = internalNode
                    internalNode.suffixlink = self.root

                j += 1

                if self.active.actNode == self.root and self.active.actLength > 0:
                    self.active.actEdge = j  # active edge points to j which is the first character of current suffix we need to insert in tree
                    self.active.actLength -= 1
                elif self.active.actNode != self.root:  # follow suffixlink to the next node
                    self.active.actNode = self.active.actNode.suffixlink
                else:
                    pass

            i += 1


    def find_matching(self,txt,pat,node,patternPointer,matched):
        """
        Recursive function to check if pattern exists in tree by travelling over edges in suffix tree
        :param txt: the text
        :param pat: the pattern
        :param node: the current active node
        :param patternPointer: pointer on pattern to indicate the characters that needed to be compared
        :param matched: list of index position where pattern is found in text
        :return: matched
        """

        m = len(pat)
        uncheckedNodes= []

        if patternPointer < m: #still has characters in pattern needed to be compared
            firstCharToCompare = pat[patternPointer] # the first character of the characters left to compare in pattern

            if firstCharToCompare == "?":
                # all outgoing edges of this node is possible due to wildcard
                # add all the nodes of outgoing edges into a list of unchecked nodes
                for edge in node.children:
                    if edge is not None:
                        uncheckedNodes.append(edge)

                # look through each unchecked nodes
                # check if characters of outgoing edge matches the given pattern
                # if yes, reset pattern pointer and call recursion to check outgoing edge of next node
                for node in uncheckedNodes:
                    tempPatternPointer = patternPointer
                    if self.edge_match(node,tempPatternPointer,pat,txt):
                        edgeLen = node.end.end - node.start + 1
                        tempPatternPointer = tempPatternPointer + edgeLen
                        matched = self.find_matching(txt,pat,node,tempPatternPointer,matched)
                return matched


            else: #character to be compared is not a wildcard
                # check to see if edge exists for this character
                #if yes then go into edge and check if all chars on edge matches pattern
                tempoPatternPointer = patternPointer
                if node.children[ord(firstCharToCompare)] is not None:
                    childnode = node.children[ord(firstCharToCompare)]
                    edgeLen = childnode.end.end - childnode.start + 1
                    if self.edge_match(childnode,tempoPatternPointer,pat,txt):
                        # reset pattern pointer and call recursion to check outgoing edge of next node
                        tempoPatternPointer = tempoPatternPointer + edgeLen
                        matched = self.find_matching(txt,pat,childnode,tempoPatternPointer,matched)
                return matched

        else:
            #no more chars to compare, meaning matching pattern is found in text
            #so obtain all the leaves from this node

            if node.index != -1: #node is a leaf node so append the suffix index of node to matched
                matched.append(node.index+1)
            else:
                # node is not a leaf node
                # so dfs travel to get all its leaf nodes
                self.get_all_leaf_index(node,matched)
            return matched


    def edge_match(self,node,currPointer,pat,txt):
        """
        This function matches to see the characters on the edge is same as pattern
        :param node: current node
        :param currPointer: pointer on the pattern to indicate characters left to be matched
        :param pat: the pattern
        :param txt: the text
        :return: True if match passes
                 False if match fails
        """

        edgeLen = node.end.end - node.start + 1 #number of chars on the edge
        edgeChars = txt[node.start:node.end.end+1] #the characters on that edge
        charsLeftToCompare = len(pat) - currPointer #number of characters in pattern that still needs to be compared

        i = 0
        while i<edgeLen and charsLeftToCompare>0:
            if (pat[currPointer+i] == '?'and edgeChars[i] != '$' ) or edgeChars[i] == pat[currPointer+i]:
                pass
            else:
                return False
            i+=1
            charsLeftToCompare-=1
        return True


    def get_all_leaf_index(self,node,leafArray):
        """
        performs DFS travel on the current node to obtained all it's leaf nodes
        """
        if node is None:
            return leafArray

        if node.index == -1: #-1 means the node is not a leaf
            for i in range(36,123):
                if node.children[i] is not None:
                    leafArray = self.get_all_leaf_index(node.children[i],leafArray)

        else: #node is leaf node
            leafArray.append(node.index+1)

        return leafArray


if __name__ == "__main__":

    text = ""
    pattern = ""
    output = []

    text_file = sys.argv[1]
    pattern_file = sys.argv[2]

    ftext = open(text_file, "r")
    for line in ftext:
        text = line

    fpat = open(pattern_file, "r")
    for line in fpat:
        pattern = line

    suffixTree = Tree()
    suffixTree.build_suffix_tree(text)

    output = suffixTree.find_matching(text+"$",pattern,suffixTree.root,0,output)

    with open("output_wildcard_matching.txt", "w") as fout:
        fout.write("\n".join(map(str, output)))

    ftext.close()
    fpat.close()
    fout.close()
