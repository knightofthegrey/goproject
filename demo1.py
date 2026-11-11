#Go demo
import copy
from queue import Queue

class run:
    def __init__(self):
        self.initializegame()

class game:
    def __init__(self,dims,c1,c2):
        self.board = board(dims,c1,c2)
        self.c1 = c1
        self.c2 = c2
        self.turn = c1
        self.captures = [0,0]
        
    def move(self,point):
        #To move: Attempt a move
        result = self.board.move(point,self.turn)
        if result == []:
            return False
        else:
            if self.turn == self.c1:
                self.captures[0] += (len(result) - 1)
                self.turn = self.c2
            else:
                self.captures[1] += (len(results) - 1)
                self.turn = self.c1
            return True
    
    def scoring(self):
        outscore = [[0,0],[0,0]]
        #Territory scoring adds to both
        ts = self.territoryscore()
        outscore[0][0] += ts[0]
        outscore[1][0] += ts[0]
        outscore[0][1] += ts[1]
        outscore[1][1] += ts[1]
        
        #Capture score adds to mode 1 (Japanese scoring) only
        outscore[0][0] += self.captures[0]
        outscore[0][1] += self.captures[1]
        
        #Stone score adds to mode 2 (Chinese scoring) only
        ascore = self.stonescore()
        outscore[1][0] += ascore[0]
        outscore[1][1] += ascore[1]
        
        return outscore
        
    
    def territoryscore(self):
        checked = []
        terrscore = [0,0]
        for a in range(self.board.state.bounds):
            for b in range(self.board.state.bounds):
                if self.board.state.colorat((a,b)) == 0:
                    if (a,b) not in checked:
                        terrcheck = self.board.state.checkterritory((a,b))
                        if terrcheck[0] == self.c1:
                            terrscore[0] += len(terrcheck[1])
                        elif terrcheck[0] == self.c2:
                            terrscore[0] += len(terrcheck[1])
                        checked += terrcheck[1]
        return terrscore
    
    def stonescore(self):
        stonescore = [0,0]
        for a in range(self.board.state.bounds):
            for b in range(self.board.state.bounds):
                if self.board.state.colorat((a,b)) == self.c1:
                    stonescore[0] += 1
                elif self.board.state.colorat((a,b)) == self.c2:
                    stonescore[1] += 1
        return stonescore
                
        

class board:
    def __init__(self,dims,c1,c2):
        self.state = state(dims)
        self.c1 = c1
        self.c2 = c2
        self.h1 = state(dims)
        self.h2 = state(dims)
    
    #Go scoring: Japanese go counts empty intersections
    
    def move(self,point,color):
        if color == self.c1: opposed = self.c2
        else: opposed = self.c1
        
        #Attempt move
        result = self.state.move(point,color,opposed)
        #If result is nothing, return empty array, illegal move
        if result == []:
            return []
        else:
            #Check for ko
            if self.state.kocheck(self.h2):
                self.state.revert(result)
                return []
            else:
                #If it was a legal move:
                self.h2 = copy.deepcopy(self.h1)
                self.h1 = copy.deepcopy(self.state)
                return result

    def displayboard(self):
        self.state.displaystate()
    
    def simulate(self,x,y,color):
        temp = state(self)
        temp.flip(x,y,color)
        return temp

class state:
    def __init__(self,arg):
        if isinstance(arg,int):
            self.bounds = dims
            self.array = [[0]*dims]*dims
        elif isinstance(arg,board):
            self.bounds = board.state.dims
            self.array = copy.deepcopy(board.state.array)
    
    def displaystate(self):
        for a in range(self.bounds):
            print(self.array[a])
    
    def move(self,point,color,opposed):
        #Go through all required steps to make a move at a point
        #Including check for capture and executing captures
        #First step: Is move into an empty space?
        if self.colorat(point) != 0:
            return []
        else:
            #Second step: Do a flip
            self.flip(point,color)
            
            #Third step: Attempt all captures
            capturelist = []
            for a in self.neighborset(point):
                #For each adjacent point, if wrong color:
                if self.colorat(a) == opposed:
                    #Attempt to capture
                    capturelist += self.capturegroup(a)
            
            #Fourth step: Attempt to capture moved stone to check for suicide
            selfcap = self.capturelist(point)
            if len(selfcap) > 0:
                #If suicide, revert
                for a in selfcap:
                    self.flip(a,color)
                for b in capturelist:
                    self.flip(b,opposed)
                return []
            
            #If legal spot and no suicide, don't revert captures
            #Do send a list of flips to the board class so it can check for ko
            return [(point,color)] + [(a,opposed) for a in capturelist]
                     
    def revert(self,pointlist):
        for a in pointlist:
            self.flip(a[0],a[1])

    def flip(self,point,color):
        self.array[point[1]][point[0]] = color
    
    def capturegroup(self,stone):
        #Attempt capture on group connected to a stone
        #If group has liberties remaining, then no capture executed
        #Otherwise, flip connected points to 0
        conns,libs = self.checkgroup(stone)
        if len(libs) == 0:
            #If group has no remaining liberties:
            for point in conns:
                self.flip(point,0)
            return conns
        else:
            return []
    
    def checkgroup(self,stone):
        color = self.colorat((x,y))
        conngroup = []
        libgroup = []
        taskgroup = Queue()
        taskgroup.put(stone)
        while not taskgroup.empty():
            tempstone = taskgroup.get()
            if tempstone not in conngroup:
                conngroup.append(tempstone)
                for a in self.neighborset(tempstone):
                    if self.colorat(a) == color:
                        taskgroup.put(a)
                    elif self.colorat(a) == 0:
                        libgroup.append(a)
        return conngroup,libgroup
    
    def checkterritory(self,stone):
        #Check if all stones surrounding an area are the same color
        conngroup = []
        c1 = 0
        c2 = 0
        boundary = [0,0]
        taskgroup = Queue()
        taskgroup.put(stone)
        while not taskgroup.empty():
            tempstone = taskgroup.get()
            if tempstone not in conngroup:
                conngroup.append(tempstone)
                for a in self.neighborset(tempstone):
                    if self.colorat(a) == 0:
                        if a not in conngroup:
                            conngroup.append(a)
                            taskgroup.put(a)
                    else:
                        #Cases: [0,0],[1,0],[1,1] for c1, c2
                        if c1 == 0:
                            c1 = self.colorat(a)
                        if self.colorat(a) == c1:
                            boundary[0] += 1
                        #If c1 not assigned, assign c1. Then check if color is c1, and add if yes.
                        #Covers three cases
                        else:
                            #Covers the other cases
                            if c2 == 0:
                                c2 = self.colorat(a)
                            if self.colorat(a) == c2:
                                boundary[1] += 1
        #Territory score then requires:
        if boundary[0] == 0:
            return c2, conngroup
        elif boundary[1] == 0:
            return c1, conngroup
        else:
            return 0, conngroup
                                
            
    
    def colorat(self,stone):
        return self[stone[1]][stone[0]]
    
    def neighborset(self,stone):
        #Gets a list of neighboring squares to check
        outlist = []
        if stone[0] > 0:
            outlist.append((x-1,y))
        if stone[0] < self.dims - 1:
            outlist.append((x+1,y))
        if stone[1] > 0:
            outlist.append((x,y-1))
        if stone[1] < self.dims - 1:
            outlist.append((x,y+1))
        
        return outlist
    
    def kocheck(self,other):
        if self.bounds != other.bounds:
            return False
        else:
            for a in range(self.bounds):
                for b in range(self.bounds):
                    if self.array[a][b] != other.array[a][b]:
                        return False
            return True
                
            
            
        
        
        
    
    
        