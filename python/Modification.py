# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 10:20:46 2018

@author: Lusha
"""

import numpy
import scipy
import math

numpy.set_printoptions(threshold=numpy.inf)


def getSVQ(YGmatrix, YBmatrix, Vmag, Vang, nodesOrder, genLen = -1, oneCluster = None, variables = None):
    if variables is not None:
        for nodeid in range(0,len(oneCluster)):
            currentNodeid = oneCluster[nodeid]
            Vmag[currentNodeid] = variables[genLen + nodeid]
    
    
    
    nodeNumber = len(nodesOrder)
    Qcal = numpy.zeros(nodeNumber)
    JVQ = numpy.zeros((nodeNumber,nodeNumber))    
    
    for i in range(0,nodeNumber):
        temp = 0
        for j in range(0, nodeNumber):
            temp = temp - Vmag[i] * Vmag[j] * (YBmatrix[i][j] * math.cos(Vang[j]-Vang[i]) + YGmatrix[i][j] * math.sin(Vang[j]-Vang[i]))
        Qcal[i] = temp
        
        
        
    for i in range(0, nodeNumber):
        for j in range(0, nodeNumber):
            if i != j:
                #Yij = complex(YGmatrix[i][j], YBmatrix[i][j])
                #JVQ[i,j] = -Vmag[i]*numpy.absolute(Yij)*math.sin(numpy.angle(Yij, deg=True)+Vang[j]-Vang[i])
                JVQ[i,j] = -Vmag[i] * (YBmatrix[i][j] * math.cos(Vang[j]-Vang[i]) + YGmatrix[i][j] * math.sin(Vang[j]-Vang[i])) 
                #JVQ[i,j] = Vmag[i]*(YGmatrix[i][j]*math.sin(Vang[i]-Vang[j]) - YBmatrix[i][j]*math.cos(Vang[i]-Vang[j]))
            else:
                JVQ[i,i] = Qcal[i]/Vmag[i]-Vmag[i]*YBmatrix[i][i]
    
   # print "JVQ from exant calculation", JVQ
    SVQ = numpy.linalg.inv(JVQ)

    #print "SVQ", SVQ
    return SVQ
    


    
    

def getAvgSensitivity(oneCluster, SVQ):
    sumAVQ = 0
    count = 0
    if len(oneCluster) > 1:
        for i in range(0, len(oneCluster)):
            for j in range(i+1, len(oneCluster)):
                indexi =  oneCluster[i]
                indexj = oneCluster[j]
                Aij = (SVQ[indexi][indexj]+SVQ[indexj][indexi])/2
                sumAVQ = sumAVQ + Aij
                count = count +1
        avgAVQ = sumAVQ/count
    else:
        avgAVQ = 0
    return avgAVQ


def getQbalanceDegree(oneCluster, networkGraph):
    vs = networkGraph.vs
    Qd = 0
    Qs = 0
    for i in range(0, len(oneCluster)):
        nodeIndex = oneCluster[i]
        Qd = Qd + vs[nodeIndex]["Qdemand"]
        Qs = Qs + vs[nodeIndex]["QsupplyMax"]
    if Qs > Qd or Qd == 0:
        QbalanceDegree = 0
    else:
        QbalanceDegree = 1 - numpy.absolute(Qs/Qd)
    return QbalanceDegree

def modIndex(networkGraph, clustering, SVQ):
    totalAVQ = 0
    totalQbalanceDegree = 0
    for i in range(0, len(clustering)):
        oneCluster = clustering[i]
        avgAVQ = getAvgSensitivity(oneCluster, SVQ)
        QbalanceDegree = getQbalanceDegree(oneCluster, networkGraph)
        totalAVQ = totalAVQ +avgAVQ
        totalQbalanceDegree = totalQbalanceDegree + QbalanceDegree
    modPart = (totalAVQ + totalQbalanceDegree)/len(clustering)
    return modPart
