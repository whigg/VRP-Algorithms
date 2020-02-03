import math

from aco import ACO, Graph

# petals with various stages of leaves

def getEuclidInfo(coordList):
    amt = len(coordList)
    adjList = [[-1 for i in range(amt)] for i in range(amt)]
    popList = [-1 for i in range(amt)]

    for i in range(amt):                      # coordList is N x 3 array with (x-coord,y-coord,demand)
        popList[i] = coordList[i][2]
        for j in range(amt):
            adjList[i][j] = math.hypot(coordList[i][0]-coordList[j][0], coordList[i][1]-coordList[j][1])

    return amt, adjList, popList


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

def rankAngle(amt, coordList):
    tanlist = [math.atan2(coord[1],coord[0]) if math.atan2(coord[1],coord[0]) > 0 else math.atan2(coord[1],coord[0]) + 2*math.pi for coord in coordList]
    angleRankd = [[tanlist[i], i] for i in range(1,len(coordList))]
    angleRankd.sort()
    angleRank = [a[1] for a in angleRankd]
    return angleRank

class graph:
    def __init__(self, amt, adjList, popList, angleRank, truckCapacity = None, costMax=None, unloadingTime=None):
        self.adjList = adjList # adjacency matrix
        self.popList = popList # stores population of each POD
        self.amt = amt # stores the amount of nodes
        self.tourList = [] # stores tour sets
        self.infoList = [] # stores population and cost of each tour in tourList
        self.truckCapacity = truckCapacity
        self.costMax = costMax
        self.unloadingTime = unloadingTime
        self.angleRank = angleRank

        if not truckCapacity:
            self.truckCapacity = 125

        if not unloadingTime:
            self.unloadingTime = 0

        if not costMax: # maximum cost per tour, default value is 500
            self.costMax = 10000

    def createPartition(self, nodesUV):
        tot = 0
        par = []
        i = 0
        while i != len(nodesUV) and tot + self.popList[nodesUV[i]] <= self.truckCapacity:
            tot += self.popList[nodesUV[i]]
            par.append(nodesUV[i])
            i+=1
        return par

    def solveTSP(self, vSet):
        key = [i for i in vSet]
        key.insert(0,0)
        distMatrix = []

        for i in key:
            row = []
            for j in key:
                row.append(self.adjList[i][j])
            distMatrix.append(row)

        aco = ACO(10, 100, 1.0, 10.0, 0.5, 10, 2)
        gdraph = Graph(distMatrix, len(distMatrix))
        route, cost = aco.solve(gdraph)

        tour = [key[i] for i in route]
        pos = tour.index(0)
        tour = tour[pos:] + tour[:pos]
        extra = len(tour)

        cost -= self.adjList[tour[0]][tour[-1]]

        while cost > self.costMax:
            cost = cost - self.adjList[tour[-1]][tour[-2]]
            extra -= 1
            tour.pop()

        return tour, cost, extra

    def makeTours(self, nodesUV = None):
        if not nodesUV:
            nodesUV = self.angleRank
        while len(nodesUV) != 0:
            partition = self.createPartition(nodesUV)
            tour, cost, amtX = self.solveTSP(partition)
            self.tourList.append(tour)
            self.infoList.append([cost, None])
            nodesUV = nodesUV[amtX:]

tex = open("petal2Results.txt", "w")
files = ["TestCases/CE/E-n22-k4.vrp","TestCases/CE/E-n23-k3.vrp","TestCases/CE/E-n30-k3.vrp","TestCases/CE/E-n33-k4.vrp","TestCases/CE/E-n51-k5.vrp","TestCases/CE/E-n76-k7.vrp","TestCases/Fisher/F-n45-k4.vrp","TestCases/Fisher/F-n72-k4.vrp","TestCases/Fisher/F-n135-k7.vrp"]
for file in files:
    coordList,truckCapacity, costMax  = getCoordList(file)
    amt, adjList, popList = getEuclidInfo(coordList)
    G = graph(amt, adjList, popList, rankAngle(amt, coordList), truckCapacity, costMax)
    G.makeTours()
    
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

    # tex.write(str(asds))
    tex.write("\n\n")
#http://neo.lcc.uma.es/vrp/vrp-instances/capacitated-vrp-instances/