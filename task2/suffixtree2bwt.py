# FIT3155 Assignment 2 Task 2
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


    def get_suffix_array(self):
        self.tree_traversal(self.root)
        return self.suffixarray

    def tree_traversal(self, node):
        if node is None:
            return

        if node.index == -1: #-1 means the node is not a leaf so continue traversal
            for i in range(36,123):
                if node.children[i] is not None:
                    self.tree_traversal(node.children[i])
        else: #reach leaf node so append suffix index into suffix array
            self.suffixarray.append(node.index)
            return


def get_bwt_string(suffixarray,string):
    """
    Function to obtain BWT string of a text based on the suffix array
    :param suffixarray of text
    :param string: the text
    :return: BWT string
    """

    bwt = []

    for x in suffixarray:
        if x==0:
            bwt.append('$')
        else:
            bwt.append(string[x-1])

    return bwt




if __name__ == "__main__":

    output = ""
    text_file = sys.argv[1]

    ftext = open(text_file, "r")
    for line in ftext:
        text = line
        suffixTree = Tree()
        suffixTree.build_suffix_tree(text)
        suffixArray = suffixTree.get_suffix_array()
        bwt = get_bwt_string(suffixArray, text+"$")
        output = "".join(bwt)


    with open("output_bwt.txt", "w") as fout:
        fout.write(output)

    ftext.close()
    fout.close()
