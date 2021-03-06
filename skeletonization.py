#!/usr/bin/env python
'''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
'''
import inkex
import cubicsuperpath
import simplepath
from lxml import etree
import copy
import math
import re
import random
import cspsubdiv

#p = [[[[204.43019, 315.34689], [204.43019, 315.34689], [204.43019, 315.34689]], [[204.07466000000002, 399.96321], [204.07466000000002, 399.96321], [204.07466000000002, 399.96321]], [[216.87377000000004, 399.96321], [216.87377000000004, 399.96321], [216.87377000000004, 399.96321]], [[216.16271000000003, 342.0117], [216.16271000000003, 342.0117], [216.16271000000003, 342.0117]], [[226.11757000000003, 342.0117], [226.11757000000003, 342.0117], [226.11757000000003, 342.0117]], [[226.47310000000002, 399.96321], [226.47310000000002, 399.96321], [226.47310000000002, 399.96321]], [[237.49456, 399.96321], [237.49456, 399.96321], [237.49456, 399.96321]], [[236.78349, 327.79047], [236.78349, 327.79047], [236.78349, 327.79047]], [[246.73836, 327.07941000000005], [246.73836, 327.07941000000005], [246.73836, 327.07941000000005]], [[247.09389, 400.31875], [247.09389, 400.31875], [247.09389, 400.31875]], [[260.95959, 400.31875], [260.95959, 400.31875], [260.95959, 400.31875]], [[261.31512, 315.70242], [261.31512, 315.70242], [261.31512, 315.70242]], [[204.43019, 315.34689], [204.43019, 315.34689], [204.43019, 315.34689]]]]
#p0 = [[[[80.0, 363.79074], [80.0, 363.79074], [80.0, 363.79074]], [[665.71429, 363.79074], [665.71429, 363.79074], [665.71429, 363.79074]], [[665.71429, 652.3621800000001], [665.71429, 652.3621800000001], [665.71429, 652.3621800000001]], [[80.0, 652.3621800000001], [80.0, 652.3621800000001], [80.0, 652.3621800000001]], [[80.0, 363.79074], [80.0, 363.79074], [80.0, 363.79074]]]]
#p1 = [[[[434.44783, 526.25697], [434.44783, 526.25697], [434.44783, 526.25697]], [[472.469, 468.25453], [472.469, 468.25453], [472.469, 468.25453]], [[599.82217, 551.7358], [599.82217, 551.7358], [599.82217, 551.7358]], [[561.801, 609.73824], [561.801, 609.73824], [561.801, 609.73824]], [[434.44783, 526.25697], [434.44783, 526.25697], [434.44783, 526.25697]]]]


class Point(object):
    def __init__(self, x, y, List = []):
        self.x = x
        self.y = y
        self.List = copy.deepcopy(List)
    def setList(self, List):
        if self.List:
            for i in range(len(List)):
                flag = True
                for j in range(len(self.List)):
                    if List[i]._eq(self.List[j]): flag = False
                if flag: self.List.append(List[i])
        else: self.List = copy.deepcopy(List)

        
    def _eq(self, other):
        if (math.fabs(self.x - other.x)<0.01 and math.fabs(self.y - other.y)<0.01):
            return True
        else: return False
    def ccopy(self):
        return Point(self.x, self.y)
    
    
class Line(object):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1
    def ccopy(self):
        return Line(Point(self.p0.x, self.p0.y), Point(self.p1.x, self.p1.y))

    def dist_points(self):
        return math.sqrt((self.p0.x - self.p1.x) ** 2 + (self.p0.y - self.p1.y) ** 2)
    def paramOfLine(self):
        '''
         a = -(self.p1.y - self.p0.y) / dist_points(self)
         b = (self.p1.x - self.p0.x) / dist_points(self)
         c = (self.p1.y * self.p0.x - self.p0.y * self.p1.x) / dist_points(self)
         return [a,b,c]
        '''
        return [-(self.p1.y - self.p0.y) / Line.dist_points(self),
                (self.p1.x - self.p0.x) / Line.dist_points(self),
                (self.p1.y * self.p0.x - self.p0.y * self.p1.x) / Line.dist_points(self)]
    def _inter(self,line):
        if self.p0._eq(line.p0) or self.p0._eq(line.p1):
            return self.p0
        elif self.p1._eq(line.p0) or self.p1._eq(line.p1):
            return self.p1
        else: return False
    def _eq(self, line):
        if self.p0._eq(line.p0) and self.p1._eq(line.p1):
            return True
        else: return False
    def _reverse(self):
        t = self.p0
        self.p0 = self.p1
        self.p1 = t
    
def inList(activeBis, readyBis):
    if (((isinstance(activeBis[0], Line) and (isinstance(readyBis[0], Line) and activeBis[0]._eq(readyBis[0])
                                                 or isinstance(readyBis[1], Line) and activeBis[0]._eq(readyBis[1])))
         or
         (isinstance(activeBis[0], Point) and (isinstance(readyBis[0], Point) and activeBis[0]._eq(readyBis[0])
                                                  or isinstance(readyBis[1], Point) and activeBis[0]._eq(readyBis[1]))))
        and
        ((isinstance(activeBis[1], Line) and (isinstance(readyBis[0], Line) and activeBis[1]._eq(readyBis[0])
                                                 or isinstance(readyBis[1], Line) and activeBis[1]._eq(readyBis[1])))
         or
         (isinstance(activeBis[1], Point) and (isinstance(readyBis[0], Point) and activeBis[1]._eq(readyBis[0])
                                                  or isinstance(readyBis[1], Point) and activeBis[1]._eq(readyBis[1]))))):
        return True
    else: return False

def getPoints(p):
    points = []
    for i in range(len(p)-1):
        points.append( Point(p[i][1][0],p[i][1][1]))
    return points

 
def getGroupPoints(p):
    points = []
    group_points = []
    for i in range(len(p)):
        points.append([])
        for j in range(2):
            points[i].append( Point(p[i][j][0],p[i][j][1]))
        group_points.append( GroupPoint(points[i]))
    return group_points


# terminal point
# points = getPoints(p)
# X MIN
def termNode(points):
    minXi = min(points[0].x,points[1].x)
    for i in range(2, len(points)):
        minXi = min(minXi,points[i].x)
    temp = []
    for i in range(len(points)):
        if (points[i].x == minXi):
            temp.append(points[i])
    if (len(temp) != 1) :
        minYi = temp[0].y
        for i in range(1,len(temp)) :
            minYi = min(minYi, temp[i].y)
        for i in range(len(temp)):
            if (minYi == temp[i].y):
                return temp[i]
    else :
        return temp[0]

# antiterminal point
# points = getPoints(p)
# X MAX
def atermNode(points):
    maxXi = max(points[0].x,points[1].x)
    for i in range(2, len(points)):
        maxXi = max(maxXi,points[i].x)
    temp = []
    for i in range(len(points)):
        if (points[i].x == maxXi):
            temp.append(points[i])
    if (len(temp) != 1) :
        minYi = temp[0].y
        for i in range(1,len(temp)) :
            minYi = min(minYi, temp[i].y)
        for i in range(len(temp)):
            if (minYi == temp[i].y):
                return temp[i]
    else :
        return temp[0]        

# Y MAX
def ayTermNode(points):
    maxYi = max(points[0].y,points[1].y)
    for i in range(2, len(points)):
        maxYi = max(maxYi,points[i].y)
    temp = []
    for i in range(len(points)):
        if (points[i].y == maxYi):
            temp.append(points[i])
    if (len(temp) != 1) :
        minXi = temp[0].x
        for i in range(1,len(temp)) :
            minXi = min(minXi, temp[i].x)
        for i in range(len(temp)):
            if (minXi == temp[i].x):
                return temp[i]
    else :
        return temp[0] 

# Y MIN
def yTermNode(points):
    minYi = min(points[0].y,points[1].y)
    for i in range(2, len(points)):
        minYi = min(minYi,points[i].y)
    temp = []
    for i in range(len(points)):
        if (points[i].y == minYi):
            temp.append(points[i])
    if (len(temp) != 1) :
        minXi = temp[0].x
        for i in range(1,len(temp)) :
            minXi = min(minXi, temp[i].x)
        for i in range(len(temp)):
            if (minXi == temp[i].x):
                return temp[i]
    else :
        return temp[0]

#  the direction of traversal of a path
def traversePath(p0, p1, p2):
    if ((p1.x - p0.x)*(p2.y - p1.y) < (p1.y - p0.y)*(p2.x - p1.x)):
        return True
    else: return False

#points = getPoints(p)
def getLines(points):

    points.append(points[0])
    lines = []
    n = int(len(points) - 1)
    term = termNode(points)
    for i in range(n):
        if (term in [points[i]]):
            if i==0 :
                if  not traversePath(points[n-1],points[i],points[i+1]):
                    points.reverse()

                lines.append( Line(points[n-1],points[i]))
                for j in range(1, n):
                    lines.append( Line(points[j-1],points[j]))
                return lines
            else:
                if  not traversePath(points[i-1],points[i],points[i+1]):
                    points.reverse()
                    i = n-i

                for j in range(i, n+1):
                    lines.append( Line(points[j-1],points[j]))
                for k in range(1,i):
                    lines.append( Line(points[k-1],points[k]))
                return lines

# lines = getLines(getPoints(p))
def getBypassPoints(lines):
    points = []
    for i in range(len(lines)):
        points.append(lines[i].p0)
    return points

# function returns concave angles
# points = getBypassPoints(getLines(getPoints(p)))
def concaveNodes(points):
    concaveList = []
    n = len(points)-1
    termLines = traversePath(points[0], points[1], points[2])
    for i in range(2,n):
        tempTermLines = traversePath(points[i-1], points[i], points[i+1])
        if termLines == True and tempTermLines == False or termLines == False and tempTermLines == True:
            concaveList.append(points[i])
    tempTermLines = traversePath(points[n-1], points[n], points[0])  
    if termLines == True and tempTermLines == False or termLines == False and tempTermLines == True:
        concaveList.append(points[n])
    tempTermLines = traversePath(points[n], points[0], points[1])  
    if termLines == True and tempTermLines == False or termLines == False and tempTermLines == True:
        concaveList.append(points[0])
    return concaveList  

def termNodes(points, concaveNodes):
    termNodesList = []
    for i in range(len(points)):
        flag = True
        for j in range(len(concaveNodes)):
            if points[i]._eq(concaveNodes[j]):
                flag = False
        if flag : termNodesList.append(points[i])
    return termNodesList

##############################################################################
# Parametrization to find centre of circle in case circle tangents to 3 points
#or 3 lines
##############################################################################

def paramOf3Points(p0, p1, p2):
    '''
     A0 = 2 * (p1.x - p0.x)
     A1 = 2 * (p1.y - p0.y)
     A2 = -(p1.x ** 2 - p0.x ** 2 + p1.y ** 2 - p0.y ** 2)
     B0 = 2 * (p2.x - p0.x)
     B1 = 2 * (p2.y - p0.y)
     B2 = -(p2.x ** 2 - p0.x ** 2 + p2.y ** 2 - p0.y ** 2)]
     A = [A0,A1,A2]
     B = [B0, B1, B2]
     return [[A, B]]
    '''
    return [[[2 * (p1.x - p0.x), 2 * (p1.y - p0.y), -(p1.x ** 2 - p0.x ** 2 + p1.y ** 2 - p0.y ** 2)],
             [2 * (p2.x - p0.x), 2 * (p2.y - p0.y), -(p2.x ** 2 - p0.x ** 2 + p2.y ** 2 - p0.y ** 2)]]]

def paramOf3Line(A0, A1, A2):
    # Ai = [ai,bi,ci] - the coefficients of line
    return [
            [[A1[0] - A0[0], A1[1] - A0[1], (A1[2] - A0[2])],
             [A2[0] + A0[0], A2[1] + A0[1], (A2[2] + A0[2])]],
            [[A1[0] + A0[0], A1[1] + A0[1], (A1[2] + A0[2])],
             [A2[0] - A0[0], A2[1] - A0[1], (A2[2] - A0[2])]],
            [[A1[0] - A0[0], A1[1] - A0[1], (A1[2] - A0[2])],
             [A2[0] - A0[0], A2[1] - A0[1], (A2[2] - A0[2])]],
            [[A1[0] + A0[0], A1[1] + A0[1], (A1[2] + A0[2])],
             [A2[0] + A0[0], A2[1] + A0[1], (A2[2] + A0[2])]]
             ]

def paramOf3Lines(A0, A1, A2):
    
    if not math.fabs((A1[0] - A0[0]) * (A2[1] - A0[1]) - (A2[0] - A0[0]) * (A1[1] - A0[1])) < 0.000001: #lines non-parallel
        return paramOf3Line(A0,A1,A2)
    elif not math.fabs((A2[0] - A0[0]) * (A2[1] - A1[1]) - (A2[0] - A1[0]) * (A2[1] - A0[1])) < 0.000001:
        return paramOf3Line(A2,A0,A1)
    else:
        return paramOf3Line(A1,A0,A2)

# return centre in case circle tangents to 3 points or 3 lines
def centreOfFirstCase(A):
    # if 3 lines
    if len(A) != 1: 
        temp = []
        for i in range(len(A)):
            if not (math.fabs(A[i][0][0]) < 0.000001 or  
                    math.fabs(A[i][0][0]*A[i][1][1] - A[i][0][1]*A[i][1][0]) < 0.000001) :
                Yc = (-(A[i][0][0] * A[i][1][2] - A[i][1][0] * A[i][0][2]) /
                      (A[i][0][0] * A[i][1][1] - A[i][0][1] * A[i][1][0]))
                temp.append([-A[i][0][2] / A[i][0][0] - A[i][0][1] * Yc / A[i][0][0], Yc])
            if (math.fabs(A[i][0][0]) < 0.000001 and 
                not math.fabs(A[i][0][0]*A[i][1][1] - A[i][0][1]*A[i][1][0]) < 0.000001):
                Yc1 = -A[i][0][2] / A[i][0][1]
                temp.append([-A[i][1][2] / A[i][1][0] - A[i][1][1] / A[i][1][0] * Yc1, Yc1])
        return temp
    # if 3 points
    else:
        if not (math.fabs(A[0][0][0]) < 0.000001 or math.fabs(A[0][0][0]*A[0][1][1] - A[0][0][1]*A[0][1][0]) < 0.000001):
            Yc = -((A[0][0][0] * A[0][1][2] - A[0][1][0] * A[0][0][2]) / 
                   (A[0][0][0] * A[0][1][1] - A[0][0][1] * A[0][1][0]))
            return [-A[0][0][2] / A[0][0][0] - A[0][0][1] * Yc / A[0][0][0], Yc]
        else:
            Yc = -A[0][0][2] / A[0][0][1]
            return [-A[0][1][2] / A[0][1][0] - A[0][1][1] / A[0][1][0] * Yc, Yc]
        

##############################################################################
# Parametrization to find centre of circle in case circle tangents to 2 points
#and line or 2 lines and point
##############################################################################
# 2 lines and 1 point
def paramA1( A0, A1, point):
    # Ai = [ai,bi,ci] - the coefficients of line
    if not math.fabs(A0[0] - A1[0]) < 0.000001 :
        return [[-(A0[2] - A1[2]) / (A0[0] - A1[0])],
                [- (A0[1] - A1[1]) / (A0[0] - A1[0])]]
    elif math.fabs(A0[0] - A1[0]) < 0.000001 and not math.fabs(A0[1] - A1[1]) < 0.000001:
        return [[-(A0[2] - A1[2]) / (A0[1] - A1[1])]]
    
    else:
        X = [[[A0[1], A0[0], -A0[0]*point.y - A0[1]*point.x],[A1[0], A1[1], A1[2]]],
             [[A0[1], A0[0], -A0[0]*point.y - A0[1]*point.x], [A0[0], A0[1], A0[2]]]]
        X1 = centreOfFirstCase([X[0]])
        X2 = centreOfFirstCase([X[1]])
        xn = (X1[0]+X2[0])/2
        yn = (X1[1]+X2[1])/2
        d = Line(point,Point(xn, yn)).dist_points()
        if not math.fabs(xn - point.x) < 0.001:
            return [[(d**2 - point.x**2 + xn**2 - point.y**2 + yn**2)/2/(xn - point.x)],
                    [-(yn - point.y)/(xn - point.x)]]
        else:
            return [[(d**2 - point.y + yn**2)/2/(yn - point.y)]]
    '''elif not math.fabs(A0[0]) < 0.000001:
        return [[-(A0[2] + A1[2]) / 2/ A0[0]],[-A0[1] / A0[0]]]
    else: return [[-(A0[2] + A1[2]) / 2 / A1[1]]]'''

# 2 points and 1 line
def paramA2(p0, p1):
    if (p1.x - p0.x) != 0:
        return [[(p1.x ** 2 - p0.x ** 2 + p1.y ** 2 - p0.y ** 2) / (2 * (p1.x - p0.x))],
                [-(p1.y - p0.y) / (p1.x - p0.x)]]
    else: return [[(p1.y + p0.y) / 2]]



def paramB(line1, line2, point):
    A = line1.paramOfLine()
    if line2 != [] : B = line2.paramOfLine()
    # A = [a, b, c]
    if ((line2 != [] and math.fabs(A[0] * line2.paramOfLine()[1] - A[1] * line2.paramOfLine()[0])>0.000001) 
         or not line2 != []):
        return [A[0] ** 2 - 1,
                A[0] * A[2] + point.x,
                A[1] ** 2 - 1,
                A[1] * A[2] + point.y,
                A[0] * A[1],
                A[2] ** 2 - point.x ** 2 - point.y ** 2]
    else:
        X = [[[A[1], A[0], -A[0]*point.y - A[1]*point.x],[B[0], B[1], B[2]]],
             [[A[1], A[0], -A[0]*point.y - A[1]*point.x], [A[0], A[1], A[2]]]]
        X1 = centreOfFirstCase([X[0]])
        X2 = centreOfFirstCase([X[1]])
        if not comparePoints(Point(X1[0],X1[1]),point,0.001) or not comparePoints(Point(X2[0],X2[1]),point,0.001):
            return [(X1[0]+X2[0])/2, (X1[1]+X2[1])/2]
        elif math.fabs(Line(point, Point((X1[0]+X2[0])/2, (X1[1]+X2[1])/2)).dist_points())<0.001:
            return centreOfFirstCase(paramOf3Lines(A,B,Line(Point(X1[0],X1[1]),Point(X2[0],X2[1])).paramOfLine()))
        else:
            xn = (X1[0]+X2[0])/2
            yn = (X1[1]+X2[1])/2
            R = Line(Point(X1[0],X1[1]),Point(xn, yn)).dist_points()
            d = Line(point,Point(xn, yn)).dist_points()
            return [1,
                    -point.x,
                    1,
                    -point.y,
                    0,
                    point.x**2 + point.y**2 - R**2]
    
    '''
    elif (line2 != [] and line1 != [] and 
          (math.fabs(A[0]*point.x + A[1]*point.y + A[2])<0.000001 or 
           math.fabs(B[0]*point.x + B[1]*point.y + B[2])<0.000001)):
        C0 = [[[-A[1], A[0], A[1]*point.x - A[0]*point.y],
               [A[0],A[1],A[2]]]]
        C1 = [[[-B[1], B[0], B[1]*point.x - B[0]*point.y],
               [B[0],B[1],B[2]]]]
        point0 = centreOfFirstCase(C0)
        point1 = centreOfFirstCase(C1)
        x = (point0[0]+point1[0])/2
        y = (point0[1]+point1[1])/2
        return [x,y]
    
    else:
       
        B = line2.paramOfLine()

        C0 = [[[-A[1], A[0], A[1]*point.x - A[0]*point.y],
               [A[0],A[1],A[2]]]]
        C1 = [[[-B[1], B[0], B[1]*point.x - B[0]*point.y],
               [B[0],B[1],B[2]]]]
        point0 = centreOfFirstCase(C0)
        point1 = centreOfFirstCase(C1)
        x = (point0[0]+point1[0])/2
        y = (point0[1]+point1[1])/2
        R = Line(Point(x,y),Point(point0[0],point0[1])).dist_points()
        return [1,
                -x,
                1,
                -y,
                0,
                Line(Point(x,y),point).dist_points() ** 2 - R ** 2 + x**2 + y**2]
    '''
def paramC(A, B):
    if len(A) != 1 and len(B) == 6:
        return [B[0] * A[1][0] ** 2 + B[2] + 2 * A[1][0] * B[4],
                B[0] * A[0][0] * A[1][0] + A[1][0] * B[1] + B[3] + B[4] * A[0][0],
                B[0] * A[0][0] ** 2 + 2 * A[0][0] * B[1] + B[5]]
    elif len(B) == 2: return B
    else:
        return [B[0], B[1] + B[4] * A[0][0], B[2] * A[0][0] ** 2 + 2 * A[0][0] * B[3] + B[5]]

# return centre in case circle tangents to 2 points and line or 2 lines and
# point
def centreOfSecondCase(A, C):
    if len(C) == 2: return [C,C]
    if C[0] == 0:
        if len(A) == 2:
            Yc1 = -C[2] / 2 / C[1]
            return [[A[0][0] + A[1][0] * Yc1, Yc1],
                    [A[0][0] + A[1][0] * Yc1, Yc1]]
        else:
            Xc1 = -C[2] / 2 / C[1]
            return [[Xc1, A[0][0]],[Xc1, A[0][0]]]
        
    elif math.fabs((C[1] / C[0]) ** 2 - C[2] / C[0]) < 0.000001:
       if len(A) == 2:
          Yc1 = -C[1] / C[0]
          return [[A[0][0] + A[1][0] * Yc1, Yc1],
                  [A[0][0] + A[1][0] * Yc1, Yc1]]
       else:
          Xc1 = -C[1] / C[0]
          return [[Xc1, A[0][0]],[Xc1, A[0][0]]]
       
    elif (((C[1] / C[0]) ** 2) - (C[2] / C[0])) > 0 :
        if len(A) == 2:
            Yc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Yc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[A[0][0] + A[1][0] * Yc1, Yc1],
                    [A[0][0] + A[1][0] * Yc2, Yc2]]
        else:
            Xc1 = -C[1] / C[0] + math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            Xc2 = -C[1] / C[0] - math.sqrt((C[1] / C[0]) ** 2 - C[2] / C[0])
            return [[Xc1, A[0][0]],[Xc2, A[0][0]]]

    else : return False

##############################################################################
# Parametrization to find virtual point of Bezier Curve
##############################################################################

# get projection of the point
def projectionC(line, point):
    coef = (line.p1.x - line.p0.x) * (point.x - line.p0.x) + (line.p1.y - line.p0.y) * (point.y - line.p0.y)
    return  Point(line.p0.x + (line.p1.x - line.p0.x) * coef / line.dist_points() ** 2,
            line.p0.y + (line.p1.y - line.p0.y) * coef / line.dist_points() ** 2)
def coordVectors(A, C):
    return Line(Point(C[0].x - A.x, C[0].y - A.y),
            Point(C[1].x - A.x, C[1].y - A.y))

def paramSystemV(vectors, V0, V1):
    return [[vectors.p0.x, vectors.p0.y, -(vectors.p0.x * V0.x + vectors.p0.y * V0.y)],
            [vectors.p1.x, vectors.p1.y, -(vectors.p1.x * V1.x + vectors.p1.y * V1.y)]]
##############################################################################
# Testing found second end point of temp bisector
##############################################################################
# testing centre of circle
def testingCentre(Xc, line):
    
    a = (Xc.x - line.p0.x) * (line.p1.x - line.p0.x) + (Xc.y - line.p0.y) * (line.p1.y - line.p0.y)
    if (((math.fabs(a) < 0.005) or (0 <= a <= line.dist_points() ** 2) or (math.fabs(a - line.dist_points() ** 2) < 0.01))):

        return Xc
    else: return False

# comparison between 2 end points
def comparePoints(centre, actbis,e):
    if (math.fabs(centre.x - actbis.x) < e and math.fabs(centre.y - actbis.y) < e): return False
    else: return True
# find intersection between radius of curve and segments of polygonal figure
def testingIntersections(centre, line, point, segments, points):
    if line:
        pLine = line.paramOfLine()
        distLine = math.fabs(pLine[0] * centre.x + pLine[1] * centre.y + pLine[2])
        if intersectionSegments(centre, line, point, segments, points, distLine):
            return True
    if point:
        distPoint = Line(centre,point).dist_points()
        if intersectionSegments(centre, line, point, segments, points, distPoint):
           return True
    return False
# this function used in testingProjections-function
def intersectionSegments(centre, line, point, segments, points,dist):
    for i in range(len(segments)):
        for k in range(len(points)):
            if testingCentre(projectionC(segments[i],centre),segments[i]):
                distSegment = Line(projectionC(segments[i],centre),centre).dist_points()
                distPoint = Line(centre,points[k]).dist_points()
                if ((distSegment > dist or math.fabs(distSegment - dist) < 0.03) and 
                    (distPoint > dist or math.fabs(distPoint - dist) < 0.03)):0
                else: return False
    return True
##############################################################################
# Add to lists
##############################################################################
#
def orderSites(lines,sites):
    tempList = []
    for i in range(len(lines)):
        for site in sites:
            if ((isinstance(site[1],Point) and site[1]._eq(lines[i].p0))
                or
                (isinstance(site[1],Line) and 
                 (site[1].p0._eq(lines[i].p0) and site[1].p1._eq(lines[i].p1))) 
                ):
                tempList.append(site) 
                break      
    return tempList
# add ends point of bissector to skeletNodes-list
# add ready bisector to readyBisector-list
# add new active bisectors to activeBisector-list
def addInLists(tempNodes, activeBis, readyBisector, skeletNodes, segment,lines):
    node = []
    virtualNode = []
    node.append([[],activeBis[0][1].ccopy()])
    aPoint = activeBis[0][2].ccopy()
    if segment:
        '''
        i = 0
        while i != len(tempNodes):
            Cos =  (segment.p1.y - segment.p0.y)*(projectionC(segment,tempNodes[i][0]).y - projectionC(segment,aPoint).y) 
            Cos += (segment.p1.x - segment.p0.x)*(projectionC(segment,tempNodes[i][0]).x - projectionC(segment,aPoint).x)
            Cos /= segment.dist_points()*Line(projectionC(segment,tempNodes[i][0]),projectionC(segment,aPoint)).dist_points()
            if Cos == 1 and len(skeletNodes) != 1:
                tempNodes.remove(tempNodes[i])
            else: i+=1
        '''
        Cos = 0
        if len(tempNodes) != 1:
            Cos =  (projectionC(segment,tempNodes[0][0]).y - projectionC(segment,aPoint).y)*(projectionC(segment,tempNodes[1][0]).y - projectionC(segment,aPoint).y) 
            Cos += (projectionC(segment,tempNodes[0][0]).x - projectionC(segment,aPoint).x)*(projectionC(segment,tempNodes[1][0]).x - projectionC(segment,aPoint).x)
            Cos /= Line(projectionC(segment,tempNodes[0][0]),projectionC(segment,aPoint)).dist_points()*Line(projectionC(segment,tempNodes[1][0]),projectionC(segment,aPoint)).dist_points()
            if Cos <= 0 :
                maxDistNodes = Line(projectionC(segment,aPoint),projectionC(segment,tempNodes[0][0])).dist_points()
                for nodes in tempNodes:
                    maxDistNodes = max(maxDistNodes,Line(projectionC(segment,aPoint),projectionC(segment,nodes[0])).dist_points())
                for nodes in tempNodes:
                    if math.fabs(maxDistNodes - Line(projectionC(segment,aPoint),projectionC(segment,nodes[0])).dist_points()) < 0.005:
                        node.append(nodes)
        if Cos >= 0 or len(tempNodes) == 1:
            minDistNodes = Line(projectionC(segment,aPoint),projectionC(segment,tempNodes[0][0])).dist_points()
            for nodes in tempNodes:
                minDistNodes = min(minDistNodes,Line(projectionC(segment,aPoint),projectionC(segment,nodes[0])).dist_points())
            for nodes in tempNodes:
                if math.fabs(minDistNodes - Line(projectionC(segment,aPoint),projectionC(segment,nodes[0])).dist_points()) < 0.005:
                    node.append(nodes)
                
        if isinstance(activeBis[0][0], Line) and isinstance(activeBis[0][1], Line):
                    skeletNodes.append([aPoint, node[1][0]])
        else:
                    virtualNode.append(centreOfFirstCase([paramSystemV(coordVectors([point for point in activeBis[0] if isinstance(point, Point)][0],
                                                                                    [projectionC(segment,aPoint),
                                                                                     projectionC(segment, nodes[0])]),
                                                                       aPoint, nodes[0])]))
                    skeletNodes.append([aPoint, Point(virtualNode[0][0],virtualNode[0][1]), node[1][0]])
    else:
        minDistNodes = Line(aPoint,tempNodes[0][0]).dist_points()
        for nodes in tempNodes:
            minDistNodes = min(minDistNodes,Line(aPoint,nodes[0]).dist_points())
        for nodes in tempNodes:
            if math.fabs(minDistNodes - Line(aPoint,nodes[0]).dist_points()) < 0.005:
                node.append(nodes)
        
        skeletNodes.append([aPoint, node[1][0]])
    node.append([[],activeBis[0][0].ccopy()])

    # reverse node-list in order touch sites circle from left active bisector
    # to right active bisector
    if len(node) != 3:
        del node[0]
        del node[-1]
        node = orderSites(lines,node)
        node.insert(0,[[],activeBis[0][1].ccopy()])
        node.append([[],activeBis[0][0].ccopy()])

    flag = True
    for readyBis in readyBisector:
        if inList(activeBis[0], readyBis) or not [k for k in range(len(skeletNodes)) if not comparePoints(readyBis[2], skeletNodes[k][-1], 0.02) ]:
            flag = False
            for i in range(3): activeBis[0].remove(activeBis[0][0])
            activeBis.remove(activeBis[0])
            for i in range(len(node) - 3): skeletNodes.remove(skeletNodes[-1])
            break
    if flag:
        readyBisector.append([activeBis[0][0].ccopy(),activeBis[0][1].ccopy(), activeBis[0][2].ccopy()])
        for i in range(3): activeBis[0].remove(activeBis[0][0])
        activeBis.remove(activeBis[0])

        # add in activeBisector
        for i in range(len(node) - 1):
            activeBis.append([node[i][1],node[i + 1][1], node[1][0]])
    

            




##############################################################################
# Skeletization of polygonal figure
##############################################################################
def Skeletonization(term, Lines, Points):
    activeBis = []
    activeBis.append([Lines[0], Lines[1], term])
    readyBisector = []
    skeletNodes = []
    skeletNodes.append([ [], term])
    
    while activeBis:
        

            if isinstance(activeBis[0][0], Line) and isinstance(activeBis[0][1], Line):
                
                tempNode = activeBis[0][0]._inter(activeBis[0][1])
                
                if tempNode and not tempNode._eq(activeBis[0][2]) :
                    skeletNodes.append([activeBis[0][2].ccopy(), tempNode])
                    
                    readyBisector.append([activeBis[0][0].ccopy(), activeBis[0][1].ccopy(), activeBis[0][2].ccopy()])
                    for i in range(3): activeBis[0].remove(activeBis[0][0])
                    activeBis.remove(activeBis[0])
                else:
                    tempNodes = []
                    for T in Points:
                         if (not [i for i in range(len(skeletNodes)) if T._eq( skeletNodes[i][-1])]):


                             Xc = centreOfSecondCase(paramA1(activeBis[0][0].paramOfLine(), activeBis[0][1].paramOfLine(), T),
                                                     paramC(paramA1(activeBis[0][0].paramOfLine(), activeBis[0][1].paramOfLine(),T),
                                                            paramB(activeBis[0][1], activeBis[0][0], T)))
                             if Xc:
                                    for xc in Xc :
                                        xc = Point(xc[0],xc[1])
                                        node = []
                                        node.append([testingCentre(xc, activeBis[0][0]),testingCentre(xc, activeBis[0][1])])

                                        if ((node[0][0] and node[0][1])   and comparePoints(node[0][0], activeBis[0][2], 0.05) 
                                            #and not [k for k in range(len(skeletNodes)) if not comparePoints(node[0][0], skeletNodes[k][-1], 0.05) ]
                                            and testingIntersections(node[0][0], [], T, Lines, Points)):
                                            tempNodes.append([node[0][0], T])
                                            break
                    for T in Lines:
                        if not (T._eq(activeBis[0][0]) or T._eq(activeBis[0][1]) ):

                            Xc = centreOfFirstCase(paramOf3Lines(T.paramOfLine(), activeBis[0][0].paramOfLine(), activeBis[0][1].paramOfLine()))

                            if Xc:
                                for xc in Xc:
                                    xc = Point(xc[0],xc[1])
                                    node = []
                                    node.append([testingCentre(xc, activeBis[0][0]), testingCentre(xc, activeBis[0][1]), testingCentre(xc, T)])
                       
                                    if ((node[0][0] and node[0][1] and node[0][2])   and comparePoints(node[0][0], activeBis[0][2], 0.05) 
                                        #and not [k for k in range(len(skeletNodes)) if not comparePoints(node[0][0], skeletNodes[k][-1], 0.05) ]
                                        and testingIntersections(node[0][0], activeBis[0][0], [], Lines, Points)):
                                        tempNodes.append([node[0][0], T])
                    if tempNodes:
                        addInLists(tempNodes, activeBis, readyBisector, skeletNodes, activeBis[0][1], Lines)
                    else: 
                        for i in range(3): activeBis[0].remove(activeBis[0][0])
                        activeBis.remove(activeBis[0])
            elif isinstance(activeBis[0][0], Point) and isinstance(activeBis[0][1], Point):
                tempNodes = []
                for T in Points:
                    if (not T._eq(activeBis[0][0]) and not T._eq(activeBis[0][1]) and not [g for g in range(len(skeletNodes)) if T._eq(skeletNodes[g][-1])]):
                         Xc = centreOfFirstCase(paramOf3Points(activeBis[0][0],activeBis[0][1], T))
                         Xc = Point(Xc[0],Xc[1])
                         if (  comparePoints(Xc, activeBis[0][2],0.05)
                             #and not [k for k in range(len(skeletNodes)) if not comparePoints(Xc, skeletNodes[k][-1], 0.05) ]
                             and testingIntersections(Xc, [], activeBis[0][0], Lines, Points)):
                             tempNodes.append([Xc, T])
                for T in Lines:
                    Xc = centreOfSecondCase(paramA2(activeBis[0][0], activeBis[0][1]),
                                            paramC(paramA2(activeBis[0][0], activeBis[0][1]),
                                                   paramB(T, [], activeBis[0][1])))
                    if Xc:
                        for xc in Xc :
                            xc = Point(xc[0],xc[1])
                            node = testingCentre(xc, T)
                            if (node   and comparePoints(node, activeBis[0][2], 0.05)
                                #and not [k for k in range(len(skeletNodes)) if not comparePoints(node, skeletNodes[k][-1], 0.05) ] 
                                and testingIntersections(node, [], activeBis[0][0], Lines, Points)):
                                tempNodes.append([node, T])
                                break
                if tempNodes:
                    addInLists(tempNodes, activeBis, readyBisector, skeletNodes, [], Lines)
                else: 
                    for i in range(3): activeBis[0].remove(activeBis[0][0])
                    activeBis.remove(activeBis[0])
            else:
                point = None
                line = None
                if isinstance(activeBis[0][0], Point):
                    point = activeBis[0][0]
                    line = activeBis[0][1]
                else:
                    point = activeBis[0][1]
                    line = activeBis[0][0]
                if not Line(point,point)._inter(line):
                    tempNodes = []
                    for T in Points:
                        if (not T._eq(point) and not [j for j in range(len(skeletNodes)) if T._eq(skeletNodes[j][-1])]):
                            
                            Xc = centreOfSecondCase(paramA2(T,point),
                                                    paramC(paramA2(T,point),
                                                           paramB(line, [], T)))
                            if Xc :
                                for xc in Xc :
                                    xc = Point(xc[0],xc[1])
                                    node = testingCentre(xc, line)
                                    if (node   and comparePoints(node, activeBis[0][2],0.05)
                                        #and not [k for k in range(len(skeletNodes)) if not comparePoints(node, skeletNodes[k][-1], 0.05) ] 
                                        and testingIntersections(node, [], T, Lines, Points)):
                                        tempNodes.append([node, T])
                                        break
                    for T in Lines:
                        if  not T._eq(line):
                            Xc = centreOfSecondCase(paramA1(line.paramOfLine(), T.paramOfLine(), point),
                                                    paramC(paramA1(line.paramOfLine(), T.paramOfLine(), point),
                                                           paramB(T, line, point)))
                            if Xc :
                                for xc in Xc :
                                    xc = Point(xc[0],xc[1])
                                    node = []
                                    node.append([testingCentre(xc, line), testingCentre(xc, T)])
                                    if (node[0][0] and node[0][1]
                                        #and not [k for k in range(len(skeletNodes)) if not comparePoints(node[0][0], skeletNodes[k][-1], 0.05) ]
                                        and comparePoints(node[0][0], activeBis[0][2],0.05)
                                        and testingIntersections(node[0][0], [], point, Lines, Points)):
                                        tempNodes.append([node[0][0], T])
                                        break
                    if tempNodes:
                        addInLists(tempNodes, activeBis, readyBisector, skeletNodes, line, Lines)
                    else: 
                        for i in range(3): activeBis[0].remove(activeBis[0][0])
                        activeBis.remove(activeBis[0])
                else: 
                    for i in range(3): activeBis[0].remove(activeBis[0][0])
                    activeBis.remove(activeBis[0])
        
    return skeletNodes

def AbsPath(sk):
    a = []
    for i in range(len(sk)):
        if len(sk[i]) == 2:
            a.append(['M', [sk[i][0].x,sk[i][0].y]])
            a.append(['L', [sk[i][1].x,sk[i][1].y]])
        else:
            a.append(['M', [sk[i][0].x,sk[i][0].y]])
            a.append(['C', [sk[i][1].x,sk[i][1].y] + [sk[i][2].x,sk[i][2].y] + [sk[i][2].x,sk[i][2].y]])
    return a

#the intersection of polygons
# true if intersection of poligons exist
def poligonIntersection(Lines0, Lines1):

    for i in range(len(Lines0)-1):
        for k in range(len(Lines1)-1):
            Z0 = (Lines1[k].p0.x - Lines0[i].p0.x)*(Lines0[i].p1.y - Lines0[i].p0.y)
            Z0 -= (Lines1[k].p0.y - Lines0[i].p0.y)*(Lines0[i].p1.x - Lines0[i].p0.x)
            Z1 = (Lines1[k].p1.x - Lines0[i].p0.x)*(Lines0[i].p1.y - Lines0[i].p0.y)
            Z1 -= (Lines1[k].p1.y - Lines0[i].p0.y)*(Lines0[i].p1.x - Lines0[i].p0.x)
            Z2 = (Lines0[i].p0.x - Lines1[k].p0.x)*(Lines1[k].p1.y - Lines1[k].p0.y)
            Z2 -= (Lines0[i].p0.y - Lines1[k].p0.y)*(Lines1[k].p1.x - Lines1[k].p0.x)
            Z3 = (Lines0[i].p1.x - Lines1[k].p0.x)*(Lines1[k].p1.y - Lines1[k].p0.y)
            Z3 -= (Lines0[i].p1.y - Lines1[k].p0.y)*(Lines1[k].p1.x - Lines1[k].p0.x)
            if Z0*Z1<0 and Z2*Z3<0:
                return True
            if Z0*Z1 ==0 and Z2*Z3==0:
                if (max(min(Lines0[i].p0.x,Lines0[i].p1.x),min(Lines1[k].p0.x,Lines1[k].p1.x)) < 
                    min(max(Lines0[i].p0.x,Lines0[i].p1.x), max(Lines1[k].p0.x,Lines1[k].p1.x))):
                    return True

    return False

# mutual arrangement of polygons
def arrPolygons(termPoints, atermPoints, yTermPoints, ayTermPoints):
    if not(termPoints[0].x > termPoints[1].x or atermPoints[0].x < atermPoints[1].x
           or yTermPoints[0].y > yTermPoints[1].y or ayTermPoints[0].y < ayTermPoints[1].y):
        return True #inside
    else: return False #outside

# sort of termNode
def qsort(L):
    if L: return qsort([x for x in L[1:] if x<L[0]]) + L[0:1] + qsort([x for x in L[1:] if x>=L[0]])
    return []

def sortLists(List):
    resultList = []
    llist = []
    for i in range(len(List)):
        llist.append(List[i][0].x)
    llist = qsort(llist)
    for k in range(len(List)):
        for m in range(len(llist)):
            if math.fabs(llist[k] - List[m][0].x)<0.000001:
                resultList.append(List[m])
    return resultList

def getExternalAngles(lines, concaveAngles):
    externalAngles = []
    for i in range(len(lines)):
        flag = True
        for k in range(len(concaveAngles)):
            
            if not lines[i].p0._eq(concaveAngles[k]): flag = True
            else: flag = False
        if flag: externalAngles.append(lines[i].p0)

    return externalAngles

# merging lists of Poligonal segments
def mergeLists(List):
    resultList = []
    for i in range(len(sortLists(List))): resultList.append(sortLists(List)[i])
    n = len(resultList)
    i = 0
    while i < n :
        concavePolygonList = []
        y = i + 1
        for m in range(i+2, n):
            if (arrPolygons([resultList[i][0], resultList[m][0]], [resultList[i][3], resultList[m][3]], 
                            [resultList[i][4], resultList[m][4]], [resultList[i][5], resultList[m][5]])
                and
                not arrPolygons([resultList[y][0], resultList[m][0]], [resultList[y][3], resultList[m][3]], 
                                [resultList[y][4], resultList[m][4]], [resultList[y][5], resultList[m][5]])):
                concavePolygonList.append(resultList[m])
                y = m
        if arrPolygons([resultList[i][0], resultList[i+1][0]], [resultList[i][3], resultList[i+1][3]], 
                       [resultList[i][4], resultList[i+1][4]], [resultList[i][5], resultList[i+1][5]]):
            concavePolygonList.append(resultList[i+1])
        if concavePolygonList:
            for x in range(len(concavePolygonList)):
                #reverse segments
                concavePolygonList[x][1].reverse()
                for k in range(len(concavePolygonList[x][1])): concavePolygonList[x][1][k]._reverse()
                #external angles
                temp = []
                temp.append(concavePolygonList[x][6])
                #for k in range(len(concavePoligonList[x][2])):
                #    concavePolygonList[x][6].append(concavePoligonList[x][2][k].ccopy())
                concavePolygonList[x].remove(concavePolygonList[x][2])
                concavePolygonList[x].insert(2,[])
                for l in range(len(temp[0])):
                    concavePolygonList[x][2].append(temp[0][l])
                #merge with i-list 
                for j in range(len(concavePolygonList[x][1])):
                    resultList[i][1].append(concavePolygonList[x][1][j])
                for p in range(len(concavePolygonList[x][2])):
                    resultList[i][2].append(concavePolygonList[x][2][p])
                resultList.remove(concavePolygonList[x])
        i += 1    
        n = len(resultList)
    return resultList

'''
def clippingNodes(skeletNodes):
    for i in range(len(skeletNodes)):
        if len(skeletNodes[i]) == 3:
            line = Line(skeletNodes[i][0],skeletNodes[i][2]).paramOfLine()
            if math.fabs(line[0]*skeletNodes[i][1].x + line[1]*skeletNodes[i][1].y + line[2]) < 1 :
                skeletNodes[i].remove(skeletNodes[i][1])

    return skeletNodes
'''


def Regularization(skeletNodes,Points, e):
    
    skeletNodes.remove(skeletNodes[0])
    if e > 0:
        lenPoints = len(Points)
        lenSkeletNodes = len(skeletNodes)
        count = 0
        while Points:
            numb = None
            tempList = []
            termLine = []
            concaveNode = []
            filletNodes = []
            #find termLine
            if skeletNodes:
                for i in range(lenSkeletNodes):
                    if skeletNodes[i][-1]._eq(Points[0]) or skeletNodes[i][0]._eq(Points[0]): 
                        numb = i
                        if skeletNodes[i][-1]._eq(Points[0]): concaveNode.append(skeletNodes[i][0])
                        else: concaveNode.append(skeletNodes[i][-1])
                        break
                # find fillet nodes
                if Points[0].List : 
                    for k in range(len(Points[0].List)): filletNodes.append(Points[0].List[k])
                else: filletNodes.append(Points[0])
                if concaveNode[0].List:
                    for k in range(len(concaveNode[0].List)): filletNodes.append(concaveNode[0].List[k])

                #find all term lines from concave node
                for i in range(lenSkeletNodes):
                    if (skeletNodes[i][0]._eq(concaveNode[0])  or
                        skeletNodes[i][-1]._eq(concaveNode[0]) ):
                        tempList.append(skeletNodes[i])
                
                #find max distance
                if filletNodes: 
                    maxD = Line(filletNodes[0], concaveNode[0]).dist_points()
                    for i in range(1, len(filletNodes)):
                        maxD = max(maxD, Line(filletNodes[i], concaveNode[0]).dist_points())
                    if maxD < e:
                        # check term point
                        for i in range(len(tempList)): 
                            if tempList[i][0]._eq(concaveNode[0]): tempList[i][0].setList(filletNodes)
                            else: tempList[i][-1].setList(filletNodes)

                
                        if len(tempList) == 2:
                            Points.append(concaveNode[0])
                
                        skeletNodes.remove(skeletNodes[numb])
                        lenSkeletNodes = len(skeletNodes)
            Points.remove(Points[0])
            lenPoints = len(Points)
            lenSkeletNodes = len(skeletNodes)
    if skeletNodes == []:
            inkex.errormsg(("You have entered is too large exponent value."))
            
    return skeletNodes

class Skeleton(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)

        self.OptionParser.add_option("-c", "--copymode",
                                     action="store", type="inkbool",
                                     dest="copymode", default=True,
                                     help="duplicate pattern before skeletonization")
        self.OptionParser.add_option("-e", "--exponent",
                                     action="store", type="int",
                                     dest="exponent", default=0,
                                     help="regularization")
        self.OptionParser.add_option("-f", "--flatness",
                        action="store", type="float", 
                        dest="flat", default=10.0,
                        help="Minimum flatness of the subdivided curves")
    def duplicateNodes(self, aList):
        clones={}
        for id,node in aList.iteritems():
            clone=copy.deepcopy(node)
            myid = node.tag.split('}')[-1]
            clone.set("id", self.uniqueId(myid))
            node.getparent().append(clone)
            clones[clone.get("id")]=clone
        return(clones)
    
    def uniqueId(self, prefix):
        id="%s%04i"%(prefix,random.randint(0,9999))
        while len(self.document.getroot().xpath('//*[@id="%s"]' % id,namespaces=inkex.NSS)):
            id="%s%04i"%(prefix,random.randint(0,9999))
        return(id)


    def effect(self):
        if len(self.options.ids)==0:
            inkex.errormsg(("This extension requires greater than or equal to 1 selected paths."))
            return
        List = []
        P = []
        Id = 0
        for id, node in self.selected.iteritems():

            if node.tag == inkex.addNS('path','svg'):
                Id=id
                p = cubicsuperpath.parsePath(node.get('d'))
                cspsubdiv.cspsubdiv(p, self.options.flat)
                #inkex.debug("nodes: %s" % p)
                List.append([termNode(getPoints(p[0])),getLines(getPoints(p[0])),concaveNodes(getBypassPoints(getLines(getPoints(p[0])))), 
                             atermNode(getPoints(p[0])), yTermNode(getPoints(p[0])), ayTermNode(getPoints(p[0])),
                            termNodes(getBypassPoints(getLines(getPoints(p[0]))), concaveNodes(getBypassPoints(getLines(getPoints(p[0]))))) ])
        
        if len(List) == 1:
            self.patternNode=self.selected[Id]
            self.gNode = etree.Element('{http://www.w3.org/2000/svg}g')
            self.patternNode.getparent().append(self.gNode)
            if self.options.copymode:
                duplist=self.duplicateNodes({id:self.patternNode})
                self.patternNode = duplist.values()[0]

            node.set('d',simplepath.formatPath(AbsPath(Regularization(Skeletonization(List[0][0],List[0][1],List[0][2]), List[0][6], self.options.exponent))))

    
        else:
            L = mergeLists(List)
            for id, node in self.selected.iteritems():
                if node.tag == inkex.addNS('path','svg'):
                    p = cubicsuperpath.parsePath(node.get('d'))
                    n=-1
                    for l in range(len(L)):
                        if termNode(getPoints(p[0]))._eq(L[l][0]): n=l
                    if n!=-1:
                        self.patternNode=self.selected[id]
                        self.gNode = etree.Element('{http://www.w3.org/2000/svg}g')
                        self.patternNode.getparent().append(self.gNode)
                        if self.options.copymode:
                            duplist=self.duplicateNodes({id:self.patternNode})
                            self.patternNode = duplist.values()[0]
                        node.set('d',simplepath.formatPath(AbsPath(Regularization(Skeletonization(L[n][0],L[n][1],L[n][2]), L[n][6], self.options.exponent))))

if __name__ == '__main__':
    e = Skeleton()
    e.affect() 


#print(AbsPath(Regularization(Skeletonization(termNode(getPoints(p[0])),getLines(getPoints(p[0])),concaveNodes(getBypassPoints(getLines(getPoints(p[0]))))), termNodes(getBypassPoints(getLines(getPoints(p[0]))), concaveNodes(getBypassPoints(getLines(getPoints(p[0]))))), 0 )))


#Lllist = []
#Lllist.append([termNode(getPoints(p0[0])),getLines(getPoints(p0[0])),concaveNodes(getBypassPoints(getLines(getPoints(p0[0])))), 
#                             atermNode(getPoints(p0[0])), yTermNode(getPoints(p0[0])), ayTermNode(getPoints(p0[0])),
#                            termNodes(getBypassPoints(getLines(getPoints(p0[0]))), concaveNodes(getBypassPoints(getLines(getPoints(p0[0]))))) ])
#Lllist.append([termNode(getPoints(p1[0])),getLines(getPoints(p1[0])),concaveNodes(getBypassPoints(getLines(getPoints(p1[0])))), 
#                             atermNode(getPoints(p1[0])), yTermNode(getPoints(p1[0])), ayTermNode(getPoints(p1[0])),
#                            termNodes(getBypassPoints(getLines(getPoints(p1[0]))), concaveNodes(getBypassPoints(getLines(getPoints(p1[0]))))) ])
#Lllist.append([termNode(getPoints(p2[0])),getLines(getPoints(p2[0])),concaveNodes(getBypassPoints(getLines(getPoints(p2[0])))), atermNode(getPoints(p2[0])), yTermNode(getPoints(p2[0])), ayTermNode(getPoints(p2[0])) ])
#Lllist.append([termNode(getPoints(p3[0])),getLines(getPoints(p3[0])),concaveNodes(getBypassPoints(getLines(getPoints(p3[0])))), atermNode(getPoints(p3[0])), yTermNode(getPoints(p3[0])), ayTermNode(getPoints(p3[0])) ])

#Lll = mergeLists(Lllist)

#print(AbsPath(Skeletonization(Lll[0][0],Lll[0][1],Lll[0][2])))

#print(AbsPath(Regularization(Skeletonization(Lll[0][0],Lll[0][1],Lll[0][2]), Lll[0][6], 0 )))
