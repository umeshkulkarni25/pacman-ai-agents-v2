# pacmanAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from pacman import Directions
from game import Agent
from heuristics import *
import random
import math

class RandomAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        actions = state.getLegalPacmanActions()
        # returns random action from all the valide actions
        return actions[random.randint(0,len(actions)-1)]

class RandomSequenceAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        self.actionList = [];
        for i in range(0,10):
            self.actionList.append(Directions.STOP);
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # get all legal actions for pacman
        possible = state.getAllPossibleActions();
        for i in range(0,len(self.actionList)):
            self.actionList[i] = possible[random.randint(0,len(possible)-1)];
        tempState = state;
        for i in range(0,len(self.actionList)):
            if tempState.isWin() + tempState.isLose() == 0:
                tempState = tempState.generatePacmanSuccessor(self.actionList[i]);
            else:
                break;
        # returns random action from all the valide actions
        return self.actionList[0];

class HillClimberAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        #creating and initializing a list of 5 actions
        self.actionList = [];
        for actionCount in range(0,5):
            self.actionList.append(Directions.STOP);
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # TODO: write Hill Climber Algorithm instead of returning Directions.STOP
        possibleActions = state.getAllPossibleActions();
        actionSeqLength = len(self.actionList)
        # generate first set of actions randomly
        for actionCount in range(0, actionSeqLength):
            self.actionList[actionCount] = possibleActions[random.randint(0, len(possibleActions)-1)]
        # execute generated sequence of actions
        tempState = state
        for actionCount in range(0, actionSeqLength):
            if tempState.isWin():
                # if win state is reached we immediately return the first action of the sequence
                return self.actionList[0]
            elif tempState.isLose():
                # if lose state is reached while executing the initial random sequence
                # we do not explore the sequence further we break out of the loop
                # and start generating better random sequences
                break
            else:
                tempState = tempState.generatePacmanSuccessor(self.actionList[actionCount])
                if tempState is None:
                    return self.actionList[0]
        bestGameEval = gameEvaluation(state, tempState)
        # try to generate a better sequence till u reach a terminal state or reach None
        while True:
            newActionList = list(self.actionList)
            for actionCount in range(0, actionSeqLength):
                if random.randint(0, 1) == 0:  # 50% chance of random action
                    newActionList[actionCount] = possibleActions[random.randint(0, len(possibleActions) - 1)]
            tempState = state;
            for actionCount in range(0, actionSeqLength):
                if tempState.isWin():
                    # if win state is reached we immediately return the first action of the sequence
                    return self.actionList[0]
                elif tempState.isLose():
                    # if lose state is reached we do not explore the sequence further and continue
                    # with generation of new random sequence
                    continue
                else:
                    tempState = tempState.generatePacmanSuccessor(newActionList[actionCount])
                    if tempState is None:
                        return self.actionList[0]
            newGameEval = gameEvaluation(state, tempState)

            if newGameEval >= bestGameEval:
                self.actionList = newActionList
                bestGameEval = newGameEval


class GeneticAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        #creating and initializing a list of 5 actions
        self.actionList = [];
        self.populationSize = 8;
        self.actionCount = 5;
        for actionCount in range(0,5):
            self.actionList.append(Directions.STOP);
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # TODO: write Genetic Algorithm instead of returning Directions.STOP
        population = [];
        bestAction = {
            "rootAction": '',
            "evaluation": -99999
        }
        possibleActions = state.getAllPossibleActions();

        # generating initial population
        for populationCount in range(0, self.populationSize):
            actionList = []
            for actionCount in range(0, self.actionCount):
                actionList.append(possibleActions[random.randint(0, len(possibleActions) - 1)])
            population.append(actionList[:])
        while True:
            evaluatedPopulation = []
            for populationIndex in range(0, self.populationSize):
                tempState = state
                currentActionSeq = population[populationIndex]

                for actionIndex in range(0, self.actionCount):
                    if tempState.isWin():
                        return currentActionSeq[0]
                    elif tempState.isLose():
                        break;
                    else:
                        nextState = tempState.generatePacmanSuccessor(currentActionSeq[actionIndex])
                        if nextState is None:
                            return bestAction["rootAction"]
                        else:
                            tempState = nextState
                evaluatedPopulation.append({
                    "actionSeq": currentActionSeq[:],
                    "evaluation": gameEvaluation(state, tempState)
                })
            rankedPopulation = sorted(evaluatedPopulation, key=lambda sequence: sequence["evaluation"])
            bestRankedSeq = rankedPopulation[len(rankedPopulation)-1]
            if bestRankedSeq["evaluation"] >= bestAction["evaluation"]:
                bestAction["rootAction"] = bestRankedSeq["actionSeq"][0]
                bestAction["evaluation"] = bestRankedSeq["evaluation"]
            nextGeneration = []
            for pairCount in range(0, self.populationSize/2):
                candidate1 = rankedPopulation[self.selectRank()]
                candidate2 = rankedPopulation[self.selectRank()]
                # 70% test for crossover
                if random.randint(1,10) <= 7:
                    for childCount in range(0, 2):
                        child = []
                        for actionCount in range(0, self.actionCount):
                            if random.randint(0, 1) == 0:
                                child.append(candidate1['actionSeq'][actionCount])
                            else:
                                child.append(candidate2['actionSeq'][actionCount])
                        nextGeneration.append(child[:])
                else:
                    nextGeneration.append(candidate1['actionSeq'])
                    nextGeneration.append(candidate2['actionSeq'])
            for populationCount in range(0, self.populationSize):
                if random.randint(1, 10) <= 1:
                    nextGeneration[populationCount][random.randint(0, self.actionCount-1)] = possibleActions[random.randint(0, len(possibleActions)-1)]
            population = nextGeneration

    def selectRank(self):
        # sum of ranks is is essentially sum of consecutive numbers
        highestRank = self.populationSize
        sumOfRanks = highestRank * (highestRank+1) / 2
        randomInteger = random.randint(1, sumOfRanks)
        selectedRank = runnerRank = highestRank;
        while runnerRank <= sumOfRanks:
            if randomInteger <= runnerRank:
                return selectedRank-1
            else:
                selectedRank -= 1
                runnerRank += selectedRank



class MCTSAgent(Agent):
    # Initialization Function: Called one time when the game starts
    def registerInitialState(self, state):
        return;

    # GetAction Function: Called with every frame
    def getAction(self, state):
        # TODO: write MCTS Algorithm instead of returning Directions.STOP
        return Directions.STOP
