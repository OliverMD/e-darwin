import Trees as Trees
import random
import TreeFunctions


class TreeConfig:
    def __init__(self):
        self.functionProb = 0.6
        self.parameterProb = 0.3
        self.functions = TreeFunctions.arithFunctions


DefaultTreeConfig = TreeConfig()


class ExpressionNode:
    def __init__(self, data, nextnode, func, datapoint):
        self.data = data  # Reference to global data
        self.next = nextnode
        self.func = func
        self.dataPoint = datapoint

    @staticmethod
    def generateRandomExp(data, treeconfig=DefaultTreeConfig):
        return ExpressionNode(data, None, Trees.makeRandomTree(treeconfig.functionProb, treeconfig.parameterProb,
                                                               treeconfig.functions, len(data)),
                              random.randint(0, len(data) - 1))

    def execute(self):
        self.data[self.dataPoint] = self.func.evaluate(self.data)

    def __repr__(self):
        return "========================================\n" + "Expression Node::DataPoint = " + str(
            self.dataPoint) + "\n" + str(
            self.func) + "==========================================="


class BranchNode:
    def __init__(self, data, expression, branchprogs):
        self.expression = expression
        self.branchProgs = branchprogs
        self.data = data

    @staticmethod
    def generateRandomBranch(data, maxdepth=15, treeconfig=DefaultTreeConfig):
        return BranchNode(data,
                          Trees.makeRandomTree(treeconfig.functionProb, treeconfig.parameterProb, treeconfig.functions,
                                               len(data)),
                          [generateRandomProgram(treeconfig.functions, maxdepth, data) for x in
                           range(random.randint(1, 6))])

    def execute(self):
        # Evaluate expression
        self.branchProgs[int(self.expression.evaluate(self.data) % len(self.branchProgs))].execute()

    def __repr__(self):
        return "============================================\n" + "Branch Node\n" + str(self.expression) + "\n" + str(
            self.branchProgs)


class LoopNode:
    def __init__(self, data, program, numberToLoop, next, loopCountExp=None):
        self.data = data
        self.program = program
        self.next = next
        self.numberToLoop = numberToLoop
        if loopCountExp is not None:
            self.loopCntExp = loopCountExp
        else:
            self.loopCntExp = None

    @staticmethod
    def generateRandomLoop(data, loopLim, maxdepth=15, treeconfig = DefaultTreeConfig):
        return LoopNode(data, generateRandomProgram(treeconfig.functions, maxdepth, data), random.randint(1, loopLim), None)

    def execute(self):
        if self.loopCntExp is not None:
            self.numberToLoop = self.loopCntExp.execute()
        for i in range(int(self.numberToLoop)):
            self.program.execute()

    def __repr__(self):
        return "========================================\n" + "Loop Node: Num: " + str(
            self.numberToLoop) + "\n" + "\t" + str(
            self.program) + "\n==========================================="


class Program:
    def __init__(self, memsize, data=None, nodes=None):
        if data is not None:
            self.data = data
        else:
            self.data = [0] * memsize

        if nodes is not None:
            self.nodes = nodes
            self.root = nodes[0]
        else:
            self.nodes = []
            self.root = None

        self.dataSize = memsize

    def execute(self):
        for node in self.nodes:
            node.execute()

    def getMinLength(self):
        return len(self.nodes)

    def getMaxExecLength(self):
        # Returns the maximum number of nodes that caan be executed
        total = 0
        for node in self.nodes:
            if isinstance(node, BranchNode):
                total += 1 + max([x.getMaxExecLength() for x in node.branchProgs])
            elif isinstance(node, LoopNode):
                total += 1 + (node.program.getMaxExecLength() * node.numberToLoop)
            else:
                total += 1
        return total

    def __repr__(self):
        retstr = ""
        for node in self.nodes:
            retstr += str(node) + "\n"
        return retstr


def randomSwapCrossover(male, female):
    point = int(min(male.getMinLength(), female.getMinLength()) / 2)
    retprog = Program(max(len(male.data), len(female.data)))

    retprog.nodes = male.nodes[:point] + female.nodes[point:]
    retprog.nodes[point - 1].next = retprog.nodes[point]
    retprog.root = retprog.nodes[0]

    for i in xrange(len(retprog.data)):
        if i >= len(female.data):
            retprog.data[i] = male.data[i]
        elif i >= len(male.data):
            retprog.data[i] = female.data[i]
        else:
            retprog.data[i] = random.choice([female.data[i], male.data[i]])

    return retprog


def randomMutate(prog, mutateAmount):
    """

    :param prog:
    :param mutateAmount: 0 -> 1.0 What percentage of the program should be changed
    :return:
    """
    for i in range(len(prog.nodes)):
        if random.random() < mutateAmount:
            a = random.random()
            if a < 0.6:
                prog.nodes[i] = ExpressionNode.generateRandomExp(prog.data)
            elif a < 0.8:
                prog.nodes[i] = BranchNode.generateRandomBranch(prog.data)
            else:
                prog.nodes[i] = LoopNode.generateRandomLoop(prog.data, 5)

            if i == 0:
                prog.root = prog.nodes[0]
                if len(prog.nodes) > 1:
                    prog.root.next = prog.nodes[1]
            elif i == len(prog.nodes) - 1:
                prog.nodes[i - 1].next = prog.nodes[i]
            else:
                prog.nodes[i - 1].next = prog.nodes[i]
                prog.nodes[i].next = prog.nodes[i + 1]


def randomMutateData(prog, mutateAmount):
    for i in xrange(len(prog.data)):
        if random.random() < mutateAmount:
            prog.data[i] = random.randint(0, 9)


def generateRandomProgram(functions, maxdepth=2, data=None, mindatasize = 1):
    retProg = None

    if data is None:
        retProg = Program(random.randint(mindatasize, mindatasize + 9))
        retProg.data = [random.randint(0, 9) for i in range(retProg.dataSize)]
    else:
        retProg = Program(len(data), data)

    rootNode = None
    currNode = rootNode
    lastNode = None
    while True:


        """
        if maxdepth <= 1:
            currNode = ExpressionNode.generateRandomExp(retProg.data, functions)
            retProg.nodes.append(currNode)
            if rootNode is None:
                rootNode = currNode
            currNode = currNode.next
        """

        if random.random() < 0.2 and rootNode is not None:
            retProg.root = rootNode
            return retProg

        a = random.random()
        if a < 0.8 or maxdepth <= 1:
            currNode = ExpressionNode.generateRandomExp(retProg.data)
            retProg.nodes.append(currNode)
            if rootNode is None:
                rootNode = currNode
                lastNode = rootNode
                currNode = currNode.next
            else:
                lastNode.next = currNode
                lastNode = currNode
                currNode = currNode.next
        elif a < 0.9:
            currNode = BranchNode.generateRandomBranch(retProg.data, maxdepth=maxdepth - 1)
            if rootNode is None:
                rootNode = currNode
                lastNode = rootNode
            retProg.nodes.append(currNode)
            break
        else:
            currNode = LoopNode.generateRandomLoop(retProg.data, 4, maxdepth=maxdepth - 1)
            retProg.nodes.append(currNode)
            if rootNode is None:
                rootNode = currNode
                lastNode = rootNode
                currNode = currNode.next
            else:
                lastNode.next = currNode
                lastNode = currNode
                currNode = currNode.next
    retProg.root = rootNode
    return retProg


if __name__ == "__main__":
    # tree = Trees.makeRandomTree(0.4, 0.6, TreeFunctions.arithFunctions, 1)
    # prog = generateRandomProgram(TreeFunctions.arithFunctions)
    # print prog.root
    # node = LoopNode.generateRandomLoop([], TreeFunctions.arithFunctions, 1)
    # print node
    # node = BranchNode.generateRandomBranch([], TreeFunctions.arithFunctions, 2)
    prog = generateRandomProgram(TreeFunctions.arithFunctions)
    prog1 = generateRandomProgram(TreeFunctions.arithFunctions)
    print prog
    print prog1
    prog1.execute()
    prog.execute()
    prog2 = randomSwapCrossover(prog, prog1)
    print prog2
    prog2.execute()
    randomMutate(prog2, 0.6)
    randomMutateData(prog2, 0.6)
    prog2.execute()
    print prog2.getMaxExecLength()
    print prog2
