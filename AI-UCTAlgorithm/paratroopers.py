"""
Game Logic for Paratroopers
"""
import UCT
import copy
from game import Agent
import util
import time
import random

class ParatroopersGameState(object):
    """ ParatrooperGameState class """
    # TODO: link of paratroopergame class / object (so K and map and dirN can be
    # referenced directly)
    gameInstance = None # reference to ParatroopersGame object (paratroopers game params etc.)
    def __init__(self, K):
        self.playerMask = [0,0,0]
        self.currentPlayer = ParatroopersGame.PLAYER1
        self.rewardPlayer = [0,0,0]
        # self.occupiedValue = [0, 0] <-- worth introducing?



    def _getDirN(self, raw_index):
        """ Returns available moves from a given position (better way : map with borders) """
        dirN = []
        if raw_index%ParatroopersGameState.gameInstance.K != 0: dirN.append(-1)
        if raw_index%ParatroopersGameState.gameInstance.K != ParatroopersGameState.gameInstance.K-1: dirN.append(1)
        if raw_index<=(ParatroopersGameState.gameInstance.K**2-1-ParatroopersGameState.gameInstance.K):  dirN.append(ParatroopersGameState.gameInstance.K)
        if raw_index>=ParatroopersGameState.gameInstance.K: dirN.append(-ParatroopersGameState.gameInstance.K)
        return dirN

    def _inside(self, row, column):
        return row >= 0 and row <= (ParatroopersGameState.gameInstance.K-1) and column >=0 and column <= (ParatroopersGameState.gameInstance.K-1)

    def _insideRaw(self, raw_index):
        return raw_index>=0 and raw_index <= (ParatroopersGameState.gameInstance.K**2 - 1)

    def _getRawIndex(self, row,column):
        return row * ParatroopersGameState.gameInstance.K + column

    def _checkOccupancy(self, raw_index):
        """ Private function for bitmap handling, returns state of a cell """

        if not self._insideRaw(raw_index): return ParatroopersGame.OUTSIDECELL
        elif self.playerMask[1] & (1<<(raw_index)): return ParatroopersGame.PLAYER1
        elif self.playerMask[2] & (1<<(raw_index)): return ParatroopersGame.PLAYER2
        else: return ParatroopersGame.FREECELL

    def _getFreeNeighbours(self, raw_index):
        """ Returns encoded list of free neighbouring cells """
        return [raw_index+d for d in self._getDirN(raw_index) if self._checkOccupancy(raw_index+d) == ParatroopersGame.FREECELL]

    def _takeCell(self, raw_index, player):
        self.playerMask[player] |= (1<<raw_index)
        self.playerMask[self._getRevPlayer(player)] &= ~(1<<raw_index)
        self.rewardPlayer[player] += ParatroopersGameState.gameInstance.map[raw_index]

    def _getRevPlayer(self,player):
        if player == ParatroopersGame.PLAYER1 : return ParatroopersGame.PLAYER2
        else: return ParatroopersGame.PLAYER1
    def _switchCurrentPlayer(self):
        self.currentPlayer = self._getRevPlayer(self.currentPlayer)

    def _getPlayerCells(self,player):
        """ Returns list of occupied cells """
        return [i for i in xrange(0,ParatroopersGameState.gameInstance.K**2) if self.playerMask[player] & (1<<i)]

    def addToReward(self,player,reward):
        self.rewardPlayer[player]+=reward

    def getLegalActions(self):
        """
        Return a list of legal actions (row*K + column). Legal action means that we can put there our paratrooper (or by paczkowanie or by deploying:)
        Simplification : no S moves (because always beneficial to capture enemy's troops
        """
        # TODO: can be done in one-liner
        # raw_indexes = list(set(util.flatten([self._getFreeNeighbours(raw_index) for raw_index in self._getPlayerCells(self.currentPlayer)])))
        return ['D'+str(i) for i in xrange(0,ParatroopersGameState.gameInstance.K**2) if self._checkOccupancy(i)==ParatroopersGame.FREECELL] #+ ['S' + str(i) for i in raw_indexes]

    def isTerminal(self):
        return sum(self.rewardPlayer) == ParatroopersGameState.gameInstance.mapsum

    def result(self, action, copyState = True):
        """ Executes action and returns new state """
        raw_index = int(action[1:])


        newState = copy.deepcopy(self) if copyState==True else self
        newState._takeCell(raw_index, newState.currentPlayer )

        ### SIMPLIFICATION ###
#         if action[0:1] == 'S':
        neigh_troop = False
        for d in newState._getDirN(raw_index):
            if newState._checkOccupancy(raw_index+d) == newState.currentPlayer:
                neigh_troop = True
                break
        if neigh_troop == True :
           for d in newState._getDirN(raw_index):
                if newState._checkOccupancy(raw_index+d) == newState._getRevPlayer(newState.currentPlayer):
                    newState._takeCell(raw_index+d,newState.currentPlayer)
                    newState.rewardPlayer[newState._getRevPlayer(newState.currentPlayer)] -= ParatroopersGameState.gameInstance.map[raw_index+d]
        newState._switchCurrentPlayer()
        return newState
    #### Specjalne metody dla pythona, np zeby dzialal slownik ###
    def __hash__(self):
        return hash(self.playerMask[ParatroopersGame.PLAYER1]+self.playerMask[ParatroopersGame.PLAYER2]<<(ParatroopersGameState.gameInstance.K**2-1)) #mozna poprawic zeby dzialalo szybciej

    def __to_string(self):
        lines=[]
        horizLine = '-'*6*ParatroopersGameState.gameInstance.K
        lines.append(horizLine)
        for row in xrange(ParatroopersGameState.gameInstance.K):
            rowStr='| '
            for column in xrange(ParatroopersGameState.gameInstance.K):
                rowStr+='{0:2d}'.format(self._checkOccupancy(self._getRawIndex(row,column)))+'  | '
            lines.append(rowStr)
            lines.append(horizLine)
        return '\n'.join(lines)

    def __str__(self):
        return self.__to_string()

    def __eq__(self,other):
        if self.playerMask[ParatroopersGame.PLAYER1] == other.playerMask[ParatroopersGame.PLAYER1] and self.playerMask[ParatroopersGame.PLAYER2] == other.playerMask[ParatroopersGame.PLAYER2] : return True
        else: return False


class ParatroopersGame(object):
    """ Game state, and all the inside mechanics, that are independent of current game state (i.e. do not change through making moves) """
    PLAYER1, PLAYER2, FREECELL, OUTSIDECELL = 1, 2, 0, -1 # constants for the class

    def __init__(self, K, M):
        """
         K: size of the map
         M: map value matrix
        """
        self.K = K
        self.map = copy.deepcopy(M) # Internally map is represented as 1D list (matrix row by row)!
        self.mapsum = sum(M)
        ParatroopersGameState.gameInstance = self # States references one distinct "game descriptor", so in fact ParatroopersGame is a singleton class
        self.gameState = ParatroopersGameState(K)
        self.options = {"startupTime":1, "getActionTime":10 } # Time constraints

    def resetGame(self):
        self.gameState = ParatroopersGameState(self.K)
        print self.gameState

    def printBoard(self):
		lines=[]
		horizLine = '-'*6*self.K
		lines.append(horizLine)
		for row in range(self.K):
			rowStr='| '
			for column in range(self.K):
				rowStr+='{0:2d}'.format(self.map[row*self.K+column])+'  | '
			lines.append(rowStr)
			lines.append(horizLine)
		print '\n'.join(lines)


    def isOver(self):
        return len(self.gameState.getLegalActions()) == 0

class RandomAgent(Agent):
    """ Simple random player """
    def __init__(self, player):
        self.player = player
        pass

    def getAction(self, state):
        return random.choice(state.getLegalActions())

class GreedyAgent(Agent):
    """ Simple greedy agent that picks an action that maximizes his reward """
    def __init__(self, heuristic, player):
        self.heuristic = heuristic
        self.player = player
    def getAction(self, state):
        actions = state.getLegalActions() # get legal actions
        l = [self.heuristic(state.result(action),self.player) for action in actions]
        return actions[l.index(max(l))] #return best action according to the heuristic
    def initState(self, state):
        """ Register initial state """
        pass

class KeyboardParatroopersAgent(Agent):
    """ Keyboard player """
    def __init__(self,game):
        self.game = game

    def getAction(self, state):
        print "Current board : \n"
        self.game.printBoard()
        return util.input_string()

    def initState(self, state):
        """ Register initial state """
        pass

class GameSimulator(object):
    """ Class for handling game """
    def __init__(self, game, agents, timePerMove = 1, printEachMove = True, printActions = True, printSummary = True):
        """
           timePerMove : time per move in [s]
            Assumption: the game is started by the first agent in the list, so the gameState passed to getAction() has got correct currentPlayer
        """
        self.agents = agents
        self.current_agent = 0
        self.game = game
        self.agentTotalTime = [0 , 0]  #measure time consumption
        self.options = {"printEachMove" : printEachMove, "printSummary" :printSummary, "printActions": printActions, 'timeoutStartup': 1, 'timeoutGetAction': 200000000 } # no timeout
        self.game.options["getActionTime"] = 20000000

    def setSilent(self):
        self.options["printEachMove"] = self.options["printActions"] = self.options["printSummary"] = False

    def playGame(self):
        """ Executes the game """
        ### Agent initialization ###
        for agent in xrange(len(self.agents)):
            initAgentFunc = util.TimeoutFunction(self.agents[agent].initState, self.options["timeoutStartup"])
            try:
                start_time = time.time()
                initAgentFunc(self.game.gameState)
                elapsed_time = time.time() - start_time
                if elapsed_time > self.game.options["startupTime"] : raise util.TimeoutFunctionException()
                self.agentTotalTime[agent] += elapsed_time
            except util.TimeoutFunctionException:
                print 'Agent {agent} timed out on startup'.format(**locals())
                return
        ### Run game simulation ###
        moveCount = 0
        while self.game.isOver() == False:
            action = None
            agent_getAction = util.TimeoutFunction(self.agents[self.current_agent].getAction, self.options["timeoutGetAction"])
            try:
                start_time = time.time()
                action = agent_getAction(self.game.gameState)
                elapsed_time = time.time() - start_time
                if elapsed_time > self.game.options["getActionTime"] : raise util.TimeoutFunctionException()
                self.agentTotalTime[agent] += elapsed_time
            except util.TimeoutFunctionException:
                print 'Agent {agent} timed out on getAction call'.format(**locals())
                return

            if self.options.get("printActions",False) == True: print "Action taken : {action}".format(**locals())

            self.game.gameState = self.game.gameState.result(action)
            moveCount += 1
            if self.options.get("printEachMove",False) == True:
                print "After move {moveCount} by {self.current_agent}".format(**locals())
                print "Rewards {lista}".format(lista = self.game.gameState.rewardPlayer[1:3])
                print str(self.game.gameState)
            self.current_agent = (self.current_agent + 1) % (len(self.agents))
        if self.options.get("printSummary",False)==True:  print 'Total time taken : {self.agentTotalTime}'.format(**locals())
        return self.game.gameState.rewardPlayer[1:3]

def greedyHeuristic(state, player):
    return state.rewardPlayer[player]

def paratroopersGreedyHeuristicVector(state):
    """ Returns reward for player 1 and 2 """
    sum =  state.rewardPlayer[ParatroopersGame.PLAYER1]  + state.rewardPlayer[ParatroopersGame.PLAYER2] # padding 0 - indexing from 1
    return [0, state.rewardPlayer[ParatroopersGame.PLAYER1]/float(sum), state.rewardPlayer[ParatroopersGame.PLAYER2]/float(sum)] # padding 0 - indexing from 1

def paratroopersRandomSetHeuristicVector(state):
    """ Returns reward for player 1 and 2, after having filled the rest of the board randomly """
    state_cpy = copy.deepcopy(state)
    ParatroopersGameState._takeCell
    for d in xrange(ParatroopersGameState.gameInstance.K**2):
        if(state_cpy._checkOccupancy(d) == ParatroopersGame.FREECELL):
            state_cpy._takeCell(d,random.choice([ParatroopersGame.PLAYER1,ParatroopersGame.PLAYER2]))


    sum =  state_cpy.rewardPlayer[ParatroopersGame.PLAYER1]  + state_cpy.rewardPlayer[ParatroopersGame.PLAYER2] # padding 0 - indexing from 1
    return [0, state_cpy.rewardPlayer[ParatroopersGame.PLAYER1]/float(sum), state_cpy.rewardPlayer[ParatroopersGame.PLAYER2]/float(sum)] # padding 0 - indexing from 1



def testMapRepresentation():
    print "hello"
    testGame = ParatroopersGame(3,[1,2,3,4,5,6,7,8,9])
    print testGame.gameState._getFreeNeighbours(1,1)
    testGame.gameState.playerMask[1] |= (1<<(testGame.gameState._getRawIndex(1,0)))
    print testGame.gameState._getFreeNeighbours(1,1)

def testMoves():
    testGame = ParatroopersGame(3,[1,2,3,4,5,6,7,8,9])
    gs = testGame.gameState
    print str(gs.playerMask[1])
    gs_mod = gs.result('D3').result('D4').result('D5').result('D6').result('D0').result('D7')
    print gs_mod.getLegalActions()
    gs_mod = gs_mod.result('S1')
    print str(gs_mod)
    print "Reward = "+str(gs_mod.rewardPlayer[1])
    print locals()
    gs_mod = gs_mod.result('D2')
    gs_mod = gs_mod.result('D8')
    print str(gs_mod)
    print gs_mod.getLegalActions()

def testGameSimRandom():
    """ Example of game simulation """
    testGame = ParatroopersGame(3,[1,2,3,4,5,6,7,8,9])
    agent1 = GreedyParatroopersAgent(greedyHeuristic, ParatroopersGame.PLAYER1)
    agent2 = GreedyParatroopersAgent(greedyHeuristic, ParatroopersGame.PLAYER2)
    gameSimulator = GameSimulator(testGame, (agent1, agent2) )
    gameSimulator.playGame()


def randomBoard(K):
    """ Returns a random board """
    return [random.randint(1,K**2) for i in xrange(K**2)]


def testGameSimMe():
    """ Example of game simulation """
    testGame = ParatroopersGame(4,randomBoard(4))
    testGame.printBoard()
    import UCT
    agent2 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER2, 2)
    agent1 = KeyboardParatroopersAgent(testGame)
    gameSimulator = GameSimulator(testGame, (agent1, agent2), 10)
    gameSimulator.playGame()

def testGameSim():
    """ Example of game simulation """
    testGame = ParatroopersGame(5,randomBoard(5))
    testGame.printBoard()
    import UCT
    agent2 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER1, 3, UCT.UCTAgent.UCBPolicyMod)
    agent1 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER2, 3, transpositions = False)#, UCT.UCTAgent.EGreedyPolicy())
    gameSimulator = GameSimulator(testGame, (agent2, agent1), 10)
    gameSimulator.playGame()


def rankTwoAgents(agent1, agent2, sim_count = 10):
    testGame = ParatroopersGame(6,randomBoard(6))
    testGame.printBoard()
#     paratroopersRandomSetHeuristicVector(testGame.gameState)
    gameSimulator = GameSimulator(testGame, (agent1, agent2),10)
    gameSimulator.setSilent()
    results = [0,0]
    wonGames = [0, 0]
    gameResults = []
    for i in xrange(sim_count):
        testGame.resetGame()
        result_sim = gameSimulator.playGame()
        results[0] += result_sim[i%2]
        results[1] += result_sim[(i%2+1)%2]
        if result_sim[i%2] > result_sim[(i%2+1)%2] :
            wonGames[0]+=1
        else:
            wonGames[1]+=1
        agent1,agent2 = agent2, agent1
        agent1.player, agent2.player = agent2.player, agent1.player
        print result_sim
        gameResults+=result_sim

    print wonGames
    print results
    print gameResults

def main():
    agent1 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER1, 3, transpositions = True, cutLevel =0, cutFunction = paratroopersRandomSetHeuristicVector)
    agent2 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER2, 3, transpositions = True)#, cutLevel =0, cutFunction = paratroopersRandomSetHeuristicVector)A
    rankTwoAgents(agent1,agent2)

if __name__ == "__main__":
    main()

"""
Nowe pomiary

1. UCT+Transpozycje VS UCT zwykle
[4089, 3345]
[312, 219, 262, 269, 261, 270, 213, 318, 341, 190, 235, 296, 209, 322, 215, 316, 280, 251, 240, 291, 209, 322, 171, 360, 269, 262, 173, 358]

komentarz: mimo czasami 10 krotnie mniejszej ilosci rozwinietych wezlow jest czesto lepszy

2. UCT+Transpozycje+UCBMod vs UCT+Transpozycje



3. UCT+Transpozycje+UCBMod+cutFunction vs UCT+Transpozycje


4. UCT+Transpozycje+E-greedy vs UCT+Transpozycje

[3139, 5625]
[119, 507, 279, 347, 161, 465, 348, 278, 118, 508, 314, 312, 137, 489, 319, 307, 169, 457, 354, 272, 176, 450, 349, 277, 243, 383, 403, 223]


"""



"""
uct transpozycje vs uct transpozycje e-greedy
[2655, 8447]
[83, 710, 498, 295, 53, 740, 490, 303, 196, 597, 495, 298, 147, 646, 479, 314, 58, 735, 569, 224, 160, 633, 560, 233, 31, 762, 533, 260]


uct transpozycje UCB1Mod + cutFunction vs uct transpozycje
[5358, 3770]
[326, 326, 303, 349, 334, 318, 260, 392, 409, 243, 243, 409, 380, 272, 300, 352, 386, 266, 268, 384, 447, 205, 261, 391, 362, 290, 215, 437]



uct transpozycje UCB1Mod vs transpozycje bez bound
[4530, 4094]
[243, 373, 265, 351, 393, 223, 296, 320, 462, 154, 311, 305, 226, 390, 323, 293, 279, 337, 267, 349, 271, 345, 288, 328, 382, 234, 288, 328]

uct transpozycje ON vs uct tranposyzcje OFF ##watpliwy wynik###
[6316, 3862]
[481, 246, 179, 548, 565, 162, 284, 443, 449, 278, 235, 492, 386, 341, 211, 516, 425, 302, 315, 412, 367, 360, 335, 392, 457, 270, 344, 383]

random vs uct
[531, 105, 90, 546, 612, 24, 110, 526, 575, 61, 171, 465, 510, 126, 176, 460, 499, 137, 107, 529, 570, 66, 166, 470, 629, 7, 119, 517]
[7439, 1465]
"""
""" Wyniki symulacji
greedy vs uct
[8119, 2361] - """
