"""
This file contains implementations of UCT algorithm
Part of game.py logic
"""


from collections import defaultdict
import util, copy, math, sys
from game import Agent
import time, random

class UCTAgent(Agent):
    """
        UCT agent, inherits after general Agent class
        Implements UCT search algorithm
    """

    class UCBPolicyMod(object):
        """ Class for best child policy based on UCB bound v"""
        def __init__(self, C = math.sqrt(2)):
            self.C = 1/(2*math.sqrt(2))

        def setParams(self, C):
            self.C = C

        def bestChild(self, node):
            """
                UCT Method: Assumes that all childs are expanded
                Implements given policy
            """
            L = [n.getExpectedValue() + self.C*math.sqrt(2*math.sqrt(node.getExpanded())/n.getExpanded()) for n in node.children]
            return node.children[L.index(max(L))]


    class UCBPolicy(object):
        C = math.sqrt(2)
        """ Class for best child policy based on UCB bound v"""
        def __init__(self, C = math.sqrt(2)):
            self.C = 1/(2*math.sqrt(2)) #mozna lepiej rozwiazac
            UCTAgent.UCBPolicy.C = self.C

        def setParams(self, C):
            self.C = C

        @staticmethod
        def getScore(n):
            """ Returns UCB1 score for node (not root) """
            return n.getExpectedValue() + UCTAgent.UCBPolicy.C*math.sqrt(2*math.log(n.parent.getExpanded())/n.getExpanded())

        def bestChild(self, node):
            """
                UCT Method: Assumes that all childs are expanded
                Implements given policy
            """
            L = [n.getExpectedValue() + self.C*math.sqrt(2*math.log(node.getExpanded())/n.getExpanded()) for n in node.children]
            return node.children[L.index(max(L))]

    class EGreedyPolicy(object):
        """ Class for best child policy based on epsilon - greedy """
        def __init__(self, d = 1, c = 0.4):
            self.c = c
            self.d = d

        def setParams(self, c = None, d = None):
            if c is not None: self.c = c
            if d is not None: self.d = d

        def bestChild(self, node):
            """
                UCT Method: Assumes that all childs are expanded
                Implements given policy
            """
            if node.getExpanded() == 0 : return random.choice(node.children)
            en = min(1, (self.c * len(node.children))/(self.d**2 * node.getExpanded()))
            return node.best_child[1] if random.random() > en else random.choice(node.children)



    class UCTNode(object):
        """ Node class for UCT algorithm """
        def __init__(self, state, action = None, parentAgent = None):
            """ Note: doesn't copy state object """
            self.expectedValueDict = defaultdict(float) #for transpositions
            self.children = [] # array of tuples : (state, action) action : action taken to transform to this state
            self.action = action
            self.parentAgent = parentAgent
            self.state = state
            self.leftLegalActions = self.state.getLegalActions()
            random.shuffle(self.leftLegalActions) # randomly permute the list (useful for expand)
            self.N = 0 # increased during the backup phase
            self._initMoves = len(self.leftLegalActions)
            self.Q = 0.0 # sum of all games played through this node
            self.parent = None
            self.children_count = self.leftLegalActions # children count useful for O(1) EGreedyPolicy
            self.best_child = (0,None) # best child pointer usefor for O(1) EGreedyPolicy
            self.best_child_UCB1 = (0, None) # best child pointer according to UCB policy (O(1) pick)
        def getLegalActions():
            return self.leftLegalActions

        def isTerminal(self):
            return self.state.isTerminal()

        def getExpectedValue(self):
            """ returns expected value, if transposition option is on uses dict """
            if self.parentAgent.transpositions == False: return self.Q/float(self.N)
            else: return self.parentAgent.Qdict[self.state]/self.parentAgent.Ndict[self.state]

        def getExpanded(self):
            return self.N if self.parentAgent.transpositions == False else self.parentAgent.Ndict[self.state]

        def addExpanded(self):
            if self.parentAgent.transpositions == False : self.N += 1
            else : self.parentAgent.Ndict[self.state] += 1

        def addExpectedValue(self, value):
            """ adds expected value, if transposition option is on uses dict """
            if self.parentAgent.transpositions == False: self.Q += value
            else : self.parentAgent.Qdict[self.state] += value #Note : expectedValue is merely accumulated Q not divided yet

        def isFullyExpanded(self):
            return len(self.leftLegalActions)==0

    def setPlayer(self, player):
        self.player = player

    def initState(self, state):
        self.root = None
        self.expectedValueDict = defaultdict(float)

    def __init__(self, evaluationFunction, player, timePerMove = 1.0, bestChildPolicy = UCBPolicy, transpositions = True, cutLevel = None, cutFunction = None):
        """
            evaluationFunction: takes state, returns an array of rewards for each player, indexed by currentPlayer field in the gameState class
            best child policy = one of the implemented best child policies included in the UCTAgent class scope
            cutLevel - level after which apply cutFunction which evaluates state :)
        """
        self.cutLevel = cutLevel
        self.cutFunction = cutFunction
        self.Qdict = defaultdict(float)
        self.Ndict = defaultdict(float)
        self.transpositions = transpositions
        self.evaluationFunction = evaluationFunction
        self.timePerMove = timePerMove
        self.player = player
        self.bestChildPolicy = bestChildPolicy.__class__
        print self.bestChildPolicy #mozna rozwiazac bardziej pythonowo
        self.bestChild = bestChildPolicy().bestChild if bestChildPolicy is not None else UCTAgent.UCBPolicy().bestChild
        self.options = {}



    def getAction(self, state):
        """ Using UCT search returns the best action """
        self.Ndict = defaultdict(float) # reset dictionaries
        self.Qdict = defaultdict(float)
        root = UCTAgent.UCTNode(copy.deepcopy(state), parentAgent = self)
        start = time.time()
        counter = 0
        while True:
            counter += 1
            if time.time() - start >= self.timePerMove : break # check time each 100th move
            v = self.treePolicy(root)
            evaluation = self.defaultPolicy(v)
            self.backup(v, evaluation)

        # pick the best action based on the calculated expected values
        L = [n.getExpectedValue() for n in root.children]
        print "{0}".format(root.getExpanded())
        return root.children[L.index(max(L))].action


    def expand(self, node):
        """
            UCT Method: Expands one node ahead by picking a random action
            assumes that actions are randomly permuted (fast picking)
        """
        leftLegalActions = node.leftLegalActions
        action = node.leftLegalActions.pop()
        expanded = node.state.result(action) # deep-copied new state alternated after the chosen (at random) action
        child = UCTAgent.UCTNode(expanded, action, parentAgent = self)
        child.parent = node
        node.children.append( child )
        return child

    def treePolicy(self, node):
        """ UCT method: Expand given node in the game tree down to the leaves """
        while not node.isTerminal():
            if not node.isFullyExpanded():
               return self.expand(node)
            else:
               node = self.bestChild(node)

        return node

    def pickMovePolicy(self, state):
        """ Policy for picking next move in tree search, currently - at random """
        return random.choice(state.getLegalActions())


    # TODO: without result
    def defaultPolicy(self, node):
        """ UCT method: Expand given node in the tree search game """
        default_node = copy.deepcopy(node.state) # (state, parent)
        simulation_depth = 0
        while not default_node.isTerminal():
            if self.cutFunction!=None and self.cutLevel == simulation_depth: return self.cutFunction(default_node)
            default_node = default_node.result(self.pickMovePolicy(default_node), copyState = False) # keep this node
            simulation_depth+=1
#             if simulation_depth > 1: return self.evaluationFunction(default_node)


        return self.evaluationFunction(default_node)

    def backup(self, node, evaluation):
        """ UCT method: backup new evaluation """
        last_node = None
        while node != None:
            node.addExpectedValue(evaluation[self.player])
            node.addExpanded()

            ### PERFORMANCE ISSUES - DYNAMIC CALCULATION OF NODE BEST CHILD ###
            if node.parent != None and  node.getExpectedValue() > node.parent.best_child[0] : node.parent.best_child = (node.Q, node) # update best child pointer # tez moze byc zle
            last_node = node
            node = node.parent




def testUCTExpand():
    import paratroopers
    testGame = paratroopers.ParatroopersGame(3,[1,2,3,4,5,6,7,8,9])
    uctAgent = UCTAgent(paratroopers.paratroopersGreedyHeuristicVector, 1)
    root = UCTAgent.UCTNode(testGame.gameState)
    uctAgent.expand(root)
    print root.children[0].state, root.children[0].action

def testUCTTreePolicy():
    import paratroopers
    testGame = paratroopers.ParatroopersGame(3,[1,2,3,4,5,6,7,8,9])
    uctAgent = UCTAgent(paratroopers.paratroopersGreedyHeuristicVector, 1)
    root = UCTAgent.UCTNode(testGame.gameState)
    for i in xrange(20):
        n = uctAgent.treePolicy(root)
        print n.state
        reward = uctAgent.defaultPolicy(n)
        uctAgent.backup(root, reward)

def testUCTMethod():
    import paratroopers
    testGame = paratroopers.ParatroopersGame(2,[1,2,3,4])
    uctAgent = UCTAgent(paratroopers.paratroopersGreedyHeuristicVector, 1, 2)
    print uctAgent.getAction(testGame.gameState)


def main():
    testUCTMethod()

if __name__ == "__main__":
    main()









