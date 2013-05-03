#! /usr/bin/python
"""
File contains search algorithms, that are operating on SearchProblem class. Later are used in agent implementations.
"""

### Import wrappers ###
from game import Agent
from util import Stack,Queue,PriorityQueue
import util
### Abstract class for search problem ####
class SearchProblem:
    def getStartState(self):
        """
        Returns the start state for the search problem
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state
        """
        util.raiseNotDefined()

    def result(self, action):
        """ For given action returns state """
        util.raiseNotDefined()

    def getLegalActions(self, state):
        """
          state: Search state

        For a given state should return list of legal action
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.  The sequence must
        be composed of legal moves
        """
        util.raiseNotDefined()


class SearchAgent(Agent):
    """ Very general search agent, which executes search algorithm on the search problem passed in constructor """
    def __init__(self, fn, problemClass, heuristic ):
        """ Warning : no error checking """
        self.searchFunction = fn
        self.heuristicFunction = heuristic
        self.searchProblemClass = problemClass
        self.path = [] #found path
        pass

    def registerInitState(self, state):
        """ Agent is initialized with zero state = state """
        self.currentState = state
        searchProblem = self.searchProblemClass(state)
        self.path = self.searchFunction(searchProblem, self.heuristicFunction)

    def getAction(self):
        """ Returns the next action """
        return self.path.pop(0) if len(self.path)!=0 else None





def AStarSearch(problem,heuristic):
    S = problem.getStartState()

    Q = PriorityQueue()
    Q.push(S,0)

    visited = {}
    dist = {S:0}
    parent = {S:-1}
    action_performed = {S: -1 }
    g = {S:0}
    infDist = 10000

    expanded_nodes=0
    state=S
    while Q.isEmpty()==False:
        expanded_nodes += 1
        state = Q.pop()
        if problem.isGoalState(state)==True: break
        visited[S] = 1

        for action in problem.getLegalActions(state):
            new_state=problem.result(state,action)
            if visited.get(new_state,-1)==-1:
                g_suggested = g[state] + problem.getActionCost(state,action)
                if g.get(new_state,infDist)>g_suggested:
                    f_suggested = g_suggested + heuristic(new_state)
                    g[new_state]=g_suggested
                    Q.push(new_state,f_suggested)
                    parent[new_state]=state
                    action_performed[new_state] = action

    S = state
    L = list()
    while S != -1:
        a = action_performed[S]
        L.append(a)
        S = parent[S]
    L.reverse()

    return L


def main():
    sa = SearchAgent(AStarSearch,lambda x: 0,'')

if __name__=="__main__":
    main()

