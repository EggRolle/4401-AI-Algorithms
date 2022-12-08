import sys
from collections import defaultdict
import queue

#Simple python program to create a graph from an input text file and perform ucs, bfs, dfs or astar search between any two points on the graph
#Nophil Mehboob 217395609
#Implements psuedocode from: https://github.com/aimacode/aima-pseudocode, although my implemenatation varies in many places



gEdges = [] #Global list of edges, helps for shortening run time with my implementation of a graph. Each index contains both nodes and the weight of the edge


#Main method, simply calls the appropriate search algorithm based on user input
#@param, typeG, the type of search algorithm to use
#@param file, the name of the file containing the graph
#@param start, the starting point
#@param end, the goal node
#@param heuristic, the file containing the heuristic values
def main(typeG, file, start, end, heuristic):

    graph = makeGraph(file) #Create the graph

    if(typeG == "bfs"):
        bfs(graph, start, end)

    elif(typeG == "dfs"):
        dfs(graph, start, end)

    elif(typeG == "ucs"):
        ucs(graph, start, end)

    elif(typeG == "astar"):
        astar(graph, start, end, heuristic)


#python p1.py bfs  input_file1.txt Richmond Frankfort heuristic_Frankfort.txt
#Creates a graph from the input file. The graph is implemented using only maps. Every index of a node contains a list of adjacent nodes
def makeGraph(file):

    edges = []
    with open(file) as file:
        for line in file:       #Loop through file
            if(line != "END"):
                try:
                    splitted = line.split()                                 
                    edges.append([splitted[0],splitted[1],splitted[2]])     #Split line into seperate parts and 
                    gEdges.append([splitted[0],splitted[1],splitted[2]])
                except:
                    pass

    graph = defaultdict(list)   #Create a map of lists representing nodes connected to eachother

    for edge in edges:
        a = edge[0]
        b =  edge[1]

        graph[a].append(b)      #Add nodes to eachothers map entries
        graph[b].append(a)

    return graph


#Search algorithm for a Breadth First Search, is not optimal
#@param graph, the graph
#@param start, the starting node
#@param end, the goal node
def bfs(graph, start, end):

    if(start == end):
        print("Start is end, invalid path")
        return

    visited = []            #Nodes visited so far
    frontier = []           #FIFO queue for frontier
    frontier.append([start])

    while(frontier):           #While frontier  is not empty

        parent = frontier.pop(0)    #The first node in the friontier queue

        current = parent[-1]     #We store paths, not nodes, so get end of path because we go wide, not deep
        

        if current not in visited:
            neighbours = graph[current]

            for neighbor in neighbours:     #For children of parent node
                new_path = list(parent)
                new_path.append(neighbor)   #Add adjacent node to path
                frontier.append(new_path)   #Add new node to frontier queue

                if neighbor == end:         #If child is a goal then
                    printPath(new_path)  #Print path
                    return

            visited.append(current)         #Done with current node
    printNoPath()
    


#Function used to print out paths for any search algorithm, only requires nodes on the path
def printPath(path):
    print("path: \n")

    currentDist = 0                                             #Distance of current edge
    totalDist = 0                                               #Total distance traveled
    for i in range(0,len(path)-1):                              #For node in path
        for edge in gEdges:                                     #Check edges list for corresponding edge
            if(edge[0] == path[i] and edge[1] == path[i+1]):
                currentDist = edge[2]
                totalDist += int(currentDist)                   #Add to distances
            elif(edge[1] == path[i] and edge[0] == path[i+1]):
                currentDist = edge[2]
                totalDist+= int(currentDist)
        print(path[i], " to ",path[i+1],": ", currentDist, " mi\n") #Print out current location in path
    print("distance: ", totalDist, " mi\n")                     #Print end of path
    


#Search algorithm for a Depth First Search, is not optimal
#@param graph, the graph
#@param start, the starting node
#@param end, the goal node
def dfs(graph, start, end):

    if(start == end):
        print("Start is end, invalid path")
        return

    frontierStack = []     
    frontierStack.append(start)     #The frontier, this time as a stack
    
    previous = {}                   #Running track of the previous node in our search path

    seen = set()                    #Set containing seen nodes
    seen.add(start)

    while(frontierStack):                       #While frontier is not empty
        current = frontierStack.pop()           #Pop current node
        neighbors = graph[current]
        for neighbor in neighbors:              #For each child
            if neighbor not in seen:            #If not already explored
                seen.add(neighbor)
                frontierStack.append(neighbor)  #Add new deeper node to stack, fulfilling depth priority
                previous[neighbor] = current    

    #Search algorithm is now complete, but we must format so that we can use our print function correctly
    bungo = True
    path = []
    currentPath = end       #Start at end
    path.append(end)
    try:
        while(bungo):                           #Keep following previous[] until we reach our starting point
            currentPath = previous[currentPath]
            path.append(currentPath)            #Add current node to total path    
            if(currentPath == start):
                bungo = False
    except:
        printNoPath()
        return

    path.reverse()
    printPath(path)         #Print the path


#Helper function to get a list of all edges adjacent to our current node, used in the UCS algorithm
#@param, our current node in the graph
def adjacentEdges(current_node):
    adjacency = []
    for edge in gEdges:
        if edge[0] == current_node or edge[1] == current_node:  #Check if either end of an edge is our current node
            adjacency.append(edge)
    return adjacency



#Search algorithm for a Uniform Cost Search, is optimal
#@param graph, the graph
#@param start, the starting node
#@param end, the goal node
def ucs(graph, start, end):

    if(start == end):
        print("Start is end, invalid path")
        return

    visited = set()

    frontier = queue.PriorityQueue()        #Priority queue for the frontier
    frontier.put((0,start, [start]))        #Each entry in the frontier includes the node itself, as well the the accumulative cost to reach the node and the path to get there


    while not frontier.empty():                             #While frontier not empty
        costToNode, current_node, path = frontier.get()     #Get lowest cost node
        visited.add(current_node)

        if current_node == end:                             #If we found the end, print path
            printPath(path)
            return path
        else:
            for edge in adjacentEdges(current_node):        #For every adjacent edge
                if edge[0] == current_node:
                    child = edge[1]                         #Checking which node is adjacent
                else:
                    child = edge[0]
                if child not in visited:                    
                    frontier.put((costToNode + int(edge[2]), child, path + [child]))    #Add child to priority queue with updated cost and path
    printNoPath()



#Helper function to read heuristic file and create a map containing the heuristic value for each node    
def hGraph(heuristicFile):
    heuristics = {}                                     #Use map to simplify runtime
    with open(heuristicFile) as file:
        for line in file:
            if ("END" not in line):
                lineS = line.split()
                try:
                    heuristics[lineS[0]] = lineS[1]     #Map at index = city equals hueristic value
                except:
                    pass
    return heuristics



#Search algorithm for an AStar search, is optimal with an admissable heuristic
#@param graph, the graph
#@param start, the starting node
#@param end, the goal node
#@param heuristic, the file containing the heuristic values
def astar(graph, start, end, heuristic):

    if(start == end):
        print("Start is end, invalid path")
        return

    heuristicGraph = hGraph(heuristic)  #Get heuristic values as a map

    frontier = queue.PriorityQueue()    #Friontier as priority queue again
    frontier.put(start, 0)
   
    previous = {}                       #Previous node in ideal path for each node
    costAcc = {}                        #Accuimulative cost to get to any point in the graph

    previous[start] = None
    costAcc[start] = 0
    
    paths = []

    while not frontier.empty():         #While frontier is not empty
        current_node = frontier.get()   

        if current_node == end:
            paths.append([previous,current_node])
            # printPathAstar(previous, current_node)                          #End only if we DEQUEUE! a goal state
            #return()

        neighbors = graph[current_node]
        for neighbor in neighbors:                                          #Check neighbors

            for edge in gEdges:                                             #Find correct edge representing our current node and nieghbor, only necessary because my graph implementation is bad
                if edge[0] == current_node and edge[1] == neighbor:
                    newCostAcc = costAcc[current_node] + int(edge[2])
                elif edge[1] == current_node and edge[0] == neighbor:
                    newCostAcc = costAcc[current_node] + int(edge[2])

            if neighbor not in costAcc or newCostAcc < costAcc[neighbor]:   #If we haven't visited this node yet or this is a cheaper path than before
                costAcc[neighbor] = newCostAcc                              #Save total cost to reach the node
                importance = newCostAcc + int(heuristicGraph[neighbor])     #Importance/priority of new node
                frontier.put(neighbor, importance)                                
                previous[neighbor] = current_node                           #Save shortest path to current node
    if not paths:
        printNoPath()
        return()

    bestCost = paths[0][1]
    #Incase two paths have goal on the fringe
    for path in paths:
        if path[1] <= bestCost:
            bestCost = path[1]
            bestPath = path
    printPathAstar(bestPath[0], bestPath[1])



#Function to print the path for Astar, the path it finds is a little more complicated and needs to printed differently
def printPathAstar(path, current):

    combinedPath = []
    combinedPath.append(current)
    while path[current] != None:            #Iterate from end to start and add nodes on the path to our total path
        combinedPath.append(path[current])
        current = path[current]
    combinedPath = combinedPath[::-1]       #Reverse the path
    printPath(combinedPath)              #Print the path

def printNoPath():
    print("path: ")
    print("none\n")
    print("distance: infinity\n")
    

#Call main without heuristics
if len(sys.argv) == 5:
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[4])

#Call main with heuristics
if len(sys.argv) == 6:
    main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4], sys.argv[5])