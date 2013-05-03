"""
Game Logic for Paratroopers
"""
import UCT, copy
from game import Agent
import util
import time
import random
import paratroopers
from optparse import OptionParser
from paratroopers import ParatroopersGame, RandomAgent, GreedyAgent, GameSimulator, randomBoard

def testGameSim():
    """ Example of game simulation """
    testGame = ParatroopersGame(5,randomBoard(5))
    testGame.printBoard()
    import UCT
    agent2 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER1, 3, UCT.UCTAgent.UCBPolicyMod)
    agent1 = UCT.UCTAgent(paratroopersGreedyHeuristicVector, ParatroopersGame.PLAYER2, 3, transpositions = False)#, UCT.UCTAgent.EGreedyPolicy())
    gameSimulator = GameSimulator(testGame, (agent2, agent1), 10)
    gameSimulator.playGame()


def rankTwoAgents(testGame, gameSimulator, agent1, agent2, sim_count = 10):
    results = [0,0]
    gameResults = []
    wonGames = [0,0]
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

    print "Simulation has ended"
    print wonGames
    print results
    print gameResults

def create_parser():
    """ Configure options and return parser object """
    parser = OptionParser()
    parser.add_option("-r", "--random_board", default=1, type="int", dest="rand_board",help="If set to 0  expects only board size (K), else (K) and row-wise map cells")
    parser.add_option("-v", "--verbose",default=True, type="int", dest="verbose", help="If set prints simulation steps")
    parser.add_option( "--agent_1", type="string",default="UCTAgent", dest="agent1", help="""Set agent1 to "UCTAgent","UCTAgentTran", "UCTAgentTranCut", "RandomAgent", "GreedyAgent" """)
    parser.add_option( "--agent_2", type="string", default="GreedyAgent", dest="agent2", help="""Set agent2 to "UCTAgent", "UCTAgentTran", "UCTAgentTranCut",  "RandomAgent", "GreedyAgent" """)
    parser.add_option("-t", "--time_per_move",default=3, type="int", dest="time_per_move", help="Set time per move, default is 2s")
    parser.add_option("-n", "--number_of_simulations", default=10, type="int", dest="num_sim", help="Sets number of simulations, default is 10")
    return parser



def create_agent(description, player, time):
    """ Aux function for creating agents """
    if description=="UCTAgent":
        return UCT.UCTAgent(paratroopers.paratroopersGreedyHeuristicVector, player, transpositions = False)
    if description=="GreedyAgent":
        return GreedyAgent(paratroopers.greedyHeuristic, player)
    if description=="RandomAgent":
        return RandomAgent(player)
    if description=="UCTAgentTran":
        return UCT.UCTAgent(paratroopers.paratroopersGreedyHeuristicVector, player, transpositions = True)
    if description=="UCTAgentTranCut":
        return UCT.UCTAgent(paratroopers.paratroopersGreedyHeuristicVector, player, transpositions = True, cutLevel = 0, cutFunction = paratroopers.paratroopersRandomSetHeuristicVector)
    else : raise NotImplementedError("Not implemented agent!")

def main():
    (options, args) = create_parser().parse_args()
    K = input()

    ### GENERATE THE BOARD ###
    board = []
    if options.rand_board == 0:
        for i in xrange(K):
            s = raw_input("Enter row: \n")
            board += [int(x) for x in s.split(' ')]
    else : board = randomBoard(K)

    testGame = ParatroopersGame(K,board)
    print "Board:"
    testGame.printBoard()

    ### CREATE AGENTS ###
    agent1 = create_agent(options.agent1,ParatroopersGame.PLAYER1, options.time_per_move)
    agent2 = create_agent(options.agent2,ParatroopersGame.PLAYER2, options.time_per_move)

    ### CREATE GAME SIMULATOR ###
    gameSimulator = GameSimulator(testGame, (agent1, agent2), 10)
    if options.verbose==False : gameSimulator.setSilent()

    ### RUN GAME SIMULATION ###
    rankTwoAgents(testGame, gameSimulator,agent1,agent2, sim_count= options.num_sim)

if __name__ == "__main__":
    main()


