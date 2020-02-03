# Arnav Iyer | arnaviyer@my.unt.edu

# Main RSS Algorithm

import csv
import math

# Fills the adjacency list for the graph in question from the coordinates in coordList.
# Input: List of coordinates of PODs
# Output: the amount of PODs, an adjacency list
def getEuclidInfo(coordList):
    amt = len(coordList)

    adjList = [[-1 for i in range(amt)] for i in range(amt)]
    popList = [-1 for i in range(amt)]

    for i in range(amt):                      # coordList is N x 3 array with (x-coord,y-coord,demand)
        popList[i] = coordList[i][2]
        for j in range(amt):
            adjList[i][j] = math.hypot(coordList[i][0]-coordList[j][0], coordList[i][1]-coordList[j][1])

    return amt, adjList, popList

# Collects data for location and capacity from a local file in a specific format
# Input: a filename, the name of the file that contains the data
# Output: The list of coordinates of each POD, the capacity of the truck, and the maximum travel cost, in this case euclidean distance
def getCoordList(filename):
    file = open(filename, "r") 
    info = file.readlines()
    file.close()
    amt = len(info)-1
    coordList = [[-1 for i in range(3)] for i in range(amt)]
    for i in range(amt):
        r = info[i].split()
        for j in range(3):
            coordList[i][j] = float(r[j])
    
    truckCapacity = int(info[amt].split()[0])
    costMax = int(info[amt].split()[1])

    return coordList, truckCapacity, costMax

# Previously used to parse data from ArcGIS
def inputData():
    filename = "inputfile.csv"
    header = []
    rows = []
    amt = 0
    
    with open(filename, 'r') as csvfile:
        fin = csv.reader(csvfile)
        header = next(fin)
        stillRSS = True
        for row in fin:
            if int(row[0]) == 1 and stillRSS:
                stillRSS = False
                amt = fin.line_num - 1
            rows.append(row)
 
    adjList = [[-1 for i in range(amt)] for i in range(amt)]
    popList = [-1 for i in range(amt)]
    count = -1
    for row in rows:
        count += 1
        if count % 151 == 0 and count != 0:
            popList[int(row[0])] = int(row[2])
        if int(row[3]) == 152:     
            adjList[int(row[0])][0] = float(row[5])
        else:
            adjList[int(row[0])][int(row[3])] = float(row[5])
    
    return amt, adjList, header, rows, popList

# Returns an array which contains all PODs sorted by distance to the RSS
# Input: adjacency list and amount of PODs
# Output: array of PODs ordered by their distance to the RSS
def rankDist(adjList, amt):
    distRank = []
    for i in range(amt):
        distRank.append([[adjList[i]][0],i])
    distRank.sort()
    return distRank

class graph:
    
    # parameterized constructor
    def __init__(self, amt, adjList, popList, truckCapacity = None, costMax=None, unloadingTime=None):
        self.adjList = adjList # adjacency matrix
        self.popList = popList # stores population of each POD
        self.amt = amt # stores the amount of nodes
        self.tourList = [] # stores tour sets
        self.infoList = [] # stores population and cost of each tour in tourList
        self.podVehicle = [] # stores maximum vehicle size per pod 
        self.truckCapacity = truckCapacity
        self.costMax = costMax
        self.unloadingTime = unloadingTime
        self.distRank = rankDist(adjList, amt)

        if not truckCapacity:
            self.truckCapacity = 125

        if not unloadingTime:
            self.unloadingTime = 0

        if not costMax: # maximum cost per tour, default value is 500
            self.costMax = 10000
    
    # Gets the farthest two nodes given a set
    # Input: set of nodes to use
    # Output: two nodes which have the farthest distance from each other in the specified set
    def getFarthest(self,Xset = None):
        if not Xset:
            Xset = set([i for i in range(self.amt)])
        maxdist = 0
        maxi = 0
        maxj = 0
        for i in Xset:       # Iterates through adjacency matrix values from the set
            for j in Xset:
                if i==j:
                    continue
                if self.adjList[i][j] == float(-1):
                    continue
                if self.adjList[i][j] > maxdist:    # finds the max distance and saves the two nodes
                    maxdist = self.adjList[i][j]
                    maxi = i
                    maxj = j
        return maxi, maxj

    # Adds the rss to the closest end of each route in the tourlist
    # or
    # Returns the distance from one of the routes to the rss
    # Input: Either you give it a tour (list of PODs), or not.
    # output: If you give it a tour, it will return the minimum distance from the rss to the tour. 
    #        If you don't give it a tour, it will add all the RSS to each route using the minimum distance from each route to the RSS
    def addRSS(self, tour=None):
        if not tour:
            for i in range(len(self.tourList)):
                if (adjList[self.tourList[i][0]][0] >= adjList[self.tourList[i][-1]][0]):
                    self.infoList[i][0] += self.adjList[0][self.tourList[i][-1]]
                    self.tourList[i].append(0)
                else:
                    self.tourList[i].reverse()                                                 
                    self.infoList[i][0] += self.adjList[0][self.tourList[i][-1]]
                    self.tourList[i].append(0)
        else:
            return min(self.adjList[tour[0]][0] , self.adjList[tour[-1]][0])

    def findClosest(self,  one,  neg):
        if (one>neg): 
            return -1
        else: 
            return 0
    
    # Makes sure all of the routes are capacity compliant
    def checkCapacity(self):    #go through each route and check if the capacity of the route isn't over. add all the nodes to the 
        extraNodes = [] # stores nodes that are removed from routes bc of excess capacity
        extraTotal = 0
        extraPop = 0
        for i in range(len(self.tourList)):             
            while (self.infoList[i][1] > self.truckCapacity):   # while the population of the tour is in excess, remove a node from the end closest to the RSS
                end = self.findClosest(adjList[self.tourList[i][0]][0],adjList[self.tourList[i][-1]][0])

                extraNodes.append(self.tourList[i][end])
                self.infoList[i][1] -= self.popList[self.tourList[i][end]]
                self.infoList[i][0] -= self.unloadingTime
                second = 1 if end == 0 else -2
                self.infoList[i][0] -= self.adjList[self.tourList[i][end]][self.tourList[i][second]]
                
                del self.tourList[i][end]
        
        #Can I route the extra notes in one route?
        extraRoute = []
        for pod in self.distRank:
            if (extraNodes.count(pod[1]) == 1):
                extraRoute.append(pod[1])
                extraPop += self.popList[pod[1]]
                if len(extraRoute) > 1:
                    extraTotal += self.adjList[extraRoute[-1]][extraRoute[-2]]       
                    extraTotal += self.unloadingTime
        
        

        if (extraTotal > self.costMax or extraPop > self.truckCapacity):
            self.makeTours(extraNodes,True)

        elif (len(extraNodes)!=0):
            self.tourList.append(extraNodes)
            self.infoList.append([extraTotal,extraPop])

        return

    # Returns effective total cost of each route, used to choose which route to add tours to
    # Input: tour (list of PODs), and total cost of that tour
    def rssDist(self, tour, total):
        return total+min(self.adjList[tour[0]][0], self.adjList[tour[-1]][0])

    # Given a set of nodes, it creates tours based on self.costMax and appends tours to self.toursList.
    # Then, it calles self.checkCapacity(), making all the routes capacity compliant.
    # At the end of the recursive process, all the routes will be time compliant and capacity compliant
    def makeTours(self, nodesUV=None, withCapacity=None):

        # if set isn't specified, creates a set of nodes
        if not nodesUV:
            nodesUV = set([i for i in range(1,self.amt)]) 

        if not withCapacity:
            withCapacity = False

        end1, end2 = self.getFarthest(nodesUV) # gets endpoints of the two tours
        nodesUV.remove(end1)    # remove endpoints from unvisited nodes
        nodesUV.remove(end2)

        total1 = self.unloadingTime  #stores total cost for tour 1
        total2 = self.unloadingTime  #stores total cost for tour 2
        pop1 = self.popList[end1]    #
        pop2 = self.popList[end2]
        tour1 = [end1] 
        tour2 = [end2]
        end = True

        while len(nodesUV) != 0: # While there aren't any unvisited nodes
            miin = math.inf
            nextnode = 0
            t1 = False  
            t2 = False
            if self.rssDist(tour1,total1) > self.rssDist(tour2,total2):	# which route is currently shorter? CONSIDER DISTANCE TO RSS
                t2 = True
            elif self.rssDist(tour1,total1) < self.rssDist(tour2,total2):
                t1 = True
            else:
                if total1 >= total2:
                    t2 = True
                else:
                    t1 = True
            for node in nodesUV:    # loop through all unvisited nodes, find closest one to route with least length IF SAME LENGTH, CHOOSE ONE FURTHEST AWAY
                if t1 and (self.adjList[node][tour1[-1]] > 0) and (self.adjList[node][tour1[0]]) and ((miin > self.adjList[node][tour1[-1]]) or (miin > self.adjList[node][tour1[0]])):
                    nextnode = node
                    miin = min(self.adjList[node][tour1[-1]], self.adjList[node][tour1[0]])
                    if (miin == self.adjList[node][tour1[-1]]):
                        end = True
                    else:
                        end = False
                if t2 and (self.adjList[node][tour2[-1]] > 0) and (self.adjList[node][tour2[0]]) and ((miin > self.adjList[node][tour2[-1]]) or (miin > self.adjList[node][tour2[0]])):
                    nextnode = node
                    miin = min(self.adjList[node][tour2[-1]], self.adjList[node][tour2[0]])
                    if (miin == self.adjList[node][tour2[-1]]):
                        end = True
                    else:
                        end = False
            if t1:
                pop1 += self.popList[nextnode]
                if end:
                    tour1.append(nextnode) # add the node to the correct tour
                else:
                    tour1.insert(0,nextnode)
                total1 += miin         # update the total cost of tour
                total1 += self.unloadingTime
            if t2:
                pop2 += self.popList[nextnode]
                if end:
                    tour2.append(nextnode) # add the node to the correct tour
                else:
                    tour2.insert(0,nextnode)
                total2 += miin
                total2 += self.unloadingTime
            nodesUV.remove(nextnode)   # remove node just added from unvisited list

        rsscost = self.addRSS(tour1)   # add the cost of traveling back to node 0, the RSS
        total1 += rsscost
        
        if total1 <= self.costMax:          # if the cost of the tour is under the costMax, add the RSS back and add tour to self.tourList
            total1 -= rsscost
            self.tourList.append(tour1)
            self.infoList.append([total1, pop1])
        else:                               # if the cost of the tour is too much, divide the tour into two tours with the same algorithm
            self.makeTours(tour1)

        rsscost = self.addRSS(tour2)
        total2 += rsscost

        if total2 <= self.costMax:
            total2 -= rsscost
            self.tourList.append(tour2)
            self.infoList.append([total2, pop2])
        else:
            self.makeTours(tour2)

        self.checkCapacity()

        return

tex = open("RSSresults.txt", "w")
files = ["TestCases/CE/E-n22-k4.vrp","TestCases/CE/E-n23-k3.vrp","TestCases/CE/E-n30-k3.vrp","TestCases/CE/E-n33-k4.vrp","TestCases/CE/E-n51-k5.vrp","TestCases/CE/E-n76-k7.vrp","TestCases/Fisher/F-n45-k4.vrp","TestCases/Fisher/F-n72-k4.vrp","TestCases/Fisher/F-n135-k7.vrp"]
for file in files:
    coordList,truckCapacity, costMax  = getCoordList(file)
    amt, adjList, popList = getEuclidInfo(coordList)
    G = graph(amt, adjList, popList, truckCapacity, costMax)
    #G.splitPods()
    G.makeTours()
    G.addRSS()
    asds = 0

    tex.write(file)
    tex.write("\n")
    if (len(G.infoList)==len(G.tourList)):
        tex.write(str(len(G.infoList)))
        tex.write("\n")

    for i in range(len(G.tourList)):
        tex.write(str(i))
        tex.write("\n")
        tex.write(str(G.tourList[i]))
        tex.write("\n")
        tex.write(str(G.infoList[i]))
        tex.write("\n")
        asds += G.infoList[i][0]

    tex.write("\n\n")