"""
Defines Nodes for use in expression trees. Also has some helpful functions for using them.
Uses some ideas and code from https://github.com/OliverMD/clever-tree also created by myself.
"""

import random
import copy


class FunctionWrapper:
    """
    Wraps a function in a useful object.
    """

    def __init__(self, name, function, argNum, var=False):
        """
        Creates a FunctionWrapper object.
        :param name: The name of the function
        :param function: The function that the object wraps
        :param argNum: The number of arguments required by function
        :return:
        """
        self.name = name
        self.function = function
        self.argNum = argNum
        if var == False:
            self.var = False
        else:
            self.var = True

    def getArgNum(self):
        if self.var:
            return random.randint(1, self.argNum)
        else:
            return self.argNum


class FunctionNode:
    """
    A class that holds a node of the function tree
    """

    def __init__(self, functionWrapper, children):
        """
        Creates a Node object
        :param functionWrapper: The function wrapper of the function this Node will use
        :param children: List of children Nodes, leftmost nodes come first.
        :return:
        """
        self.functionWrapper = functionWrapper
        self.children = children

    def evaluate(self, parameters):
        """
        Evaluates this nodes children and then this node with parameters given.
        :param parameters: The parameters that will be used by the ParameterNodes
        :return:
        """
        childrenResults = [child.evaluate(parameters) for child in self.children]  # Results from child Nodes
        return self.functionWrapper.function(childrenResults)

    def _asString(self, indent=0):
        """
        Recursive way to generate repr string
        :param indent:
        :return:String
        """
        retString = str(indent) + ':' + ('-' * indent) + self.functionWrapper.name + '\n'
        for child in self.children:
            retString += child._asString(indent + 1)

        # retString += '\n'

        return retString

    def __repr__(self):
        return self._asString(0)


class ParameterNode:
    def __init__(self, parameterIndex):
        self.parameterIndex = parameterIndex

    def evaluate(self, parameters):
        return parameters[self.parameterIndex]

    def _asString(self, indent=0):
        return "{0}:{1}[[{2}]]\n".format(indent, '-' * indent, str(self.parameterIndex))

    def __repr__(self):
        return self._asString(0)


class ConstNode:
    def __init__(self, value):
        self.value = value

    def evaluate(self, parameters):
        return self.value

    def _asString(self, indent=0):
        return "{0}:{1}{2}\n".format(indent, '-' * indent, self.value)

    def __repr__(self):
        return self._asString(0)


def makeRandomTree(functionProb, paramProb, functionSet, noOfParams, maxDepth=3):
    if random.random() < functionProb and maxDepth > 0:
        func = random.choice(functionSet)
        children = [makeRandomTree(functionProb, paramProb, functionSet, noOfParams, maxDepth - 1) for child in
                    range(func.getArgNum())]
        return FunctionNode(func, children)
    elif random.random() < paramProb and noOfParams > 0:
        return ParameterNode(random.randint(0, noOfParams - 1))
    else:
        return ConstNode(random.choice([random.randint(0, 9), random.random()]))


def mutateTree(self, rootNode, mutationAmount, functionset, noOfParams):
    if random.random() < mutationAmount:
        return makeRandomTree(random.random(), random.random(), functionset, noOfParams)
    else:
        result = copy.deepcopy(rootNode)
        if isinstance(result, FunctionNode):
            result.children = [mutateTree(c, mutationAmount, functionset, noOfParams) for c in rootNode.children]
        return result


def crossover(self, maleNode, femaleNode, top=True):
    if random.random() < 0.7 and not top:
        return copy.deepcopy(femaleNode)
    else:
        result = copy.deepcopy(maleNode)
        if isinstance(maleNode, FunctionNode) and isinstance(femaleNode, FunctionNode):
            result.children = [self.crossover(c, random.choice(femaleNode.children), False) for c in maleNode.children]
        return result