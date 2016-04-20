import pyx	
from WRender import PyXMultipageRenderer
import os, sys, collections
import numpy as np
#import logging
#from pyx.unit import x_mm,x_pt,w_mm,u_mm,v_mm

#import random
import numpy.random as rnd

from WContainer import PartitionedContainer,StochasticInteractionContainer,ContainerPrinter	

### PLUGIN methods for PyX paths
### (enriching generic path behaviour)
def rndPointAt(shape):
	return shape.at ( rnd.uniform ( 0, pyx.unit.tocm(shape.arclen()) ) )
pyx.path.path.rndPointAt = rndPointAt 

def rndPointInBBox(bbox):
	x = rnd.uniform(pyx.unit.tocm(bbox.left()),pyx.unit.tocm(bbox.right()))
	y = rnd.uniform(pyx.unit.tocm(bbox.bottom()),pyx.unit.tocm(bbox.top()))
	return x,y
pyx.bbox.bbox_pt.rndPointIn = rndPointInBBox


class ContainerRenderer(PyXMultipageRenderer):
	def __init__(self,*args,**kwargs):
		PyXMultipageRenderer.__init__(self, *args, **kwargs)
		self.partitionStyles = collections.OrderedDict()
				
	def addPartitionStyle(self,pa,style):
		if not self.simulate:
			self.partitionStyles[pa] = style

	def render(self,container):
		if not self.simulate:
			for pa,sty in self.partitionStyles.iteritems():
				for el in container.retrieve(pa):
					self.can.stroke(el,sty)


class SensorGeometrieReaktorA(StochasticInteractionContainer):
	def __init__(self,*args,**kwargs):
		StochasticInteractionContainer.__init__(self,*args,**kwargs)
	
	def getMaxIntersectingPath(self,sensePartition,destPartition):
		"""Returns the Path Element in sensePartition which has the highest number of intersections with elements in destPartition.
		Returns a tuple: (mostIntersectingPath,intersections) """
		currID = None
		currpath = None
		currisects = []
		for sen in self.partitions[sensePartition]:
			isects = []
			for el in self.partitions[destPartition]:
				isectssen,isectsel = self.allElements[sen].intersect(self.allElements[el])
				isects += isectssen
			if len(currisects) <= len(isects):
				currID = sen
				currpath = self.allElements[currID]
				currisects = isects
		return currID, currpath, currisects

	def getMinIntersectingPath(self,sensePartition,destPartition):
		""" cf. getMaxIntersectingPath """
		currID = None
		currpath = None
		currisects = None
		for sen in self.partitions[sensePartition]:
			#print sen
			isects = []
			for el in self.partitions[destPartition]:
				#print sen, el
				isectssen,isectsel = self.allElements[sen].intersect(self.allElements[el])
				isects += isectssen
				
			if currisects == None or len(currisects) >= len(isects):
				currID = sen
				currpath = self.allElements[currID]
				currisects = isects
		return currID, currpath, currisects
		
	def getBestIntersectingPath(self,sensePartition,destPartition,intersectNum):
		curreval = 0.0
		currID = None
		currpath = None
		currisects = None
		for sen in self.partitions[sensePartition]:
			isects = []
			for el in self.partitions[destPartition]:
				isectssen,isectsel = self.allElements[sen].intersect(self.allElements[el])
				isects += isectssen
			ev = 1.0 / (1+abs(len(isects)-intersectNum))
			if ev >= curreval:
				curreval = ev
				currID = sen
				currpath = self.allElements[currID]
				currisects = isects
				
		return currID, currpath, currisects

	
		
class GeometrieReaktorB(StochasticInteractionContainer):
	infinity = pyx.path.circle(0,0,100)
	
	def __init__(self,*args,**kwargs):
		StochasticInteractionContainer.__init__(self,*args,**kwargs)
		self.bboxes = {}
		
	@staticmethod
	def generateRay(el):
		x1,y1 = GeometrieReaktorB.getRndPoint(el)
		x2,y2 = GeometrieReaktorB.getInfinityPoint()
		results = [[pyx.path.line(x1,y1,x2,y2)]]	## why a list of one list with one element?
													## one element in one product channel -- other generators might want to generate two types of objects for different partitions/channels -- and maybe more than one object per channel
		return results

	@staticmethod
	def getInfinityPoint():
		return GeometrieReaktorB.getRndPoint(GeometrieReaktorB.infinity)
		
	@staticmethod
	def interactRayFissile(atom,ray):
		""" Interaction between one ray and a fissile atom. If an interaction is possible, products are
			send to the channels ['newcastRAYS','absRAYS','inFISS']."""	
		isects = atom.intersect(ray)[0]
		if isects:
			param = rnd.sample(isects,1)[0]
			x0,y0 = ray.atbegin()
			x1,y1 = atom.at(param)
			x2,y2 = GeometrieReaktorB.getInfinityPoint()
			x3,y3 = GeometrieReaktorB.getInfinityPoint()
			products = [[pyx.path.line(x1,y1,x2,y2),pyx.path.line(x1,y1,x3,y3)],	# newly cast rays
						[pyx.path.line(x0,y0,x1,y1)]]								# absorbed ray
			return products
		else: 
			return []
		
	@staticmethod
	def getRndPoint(shape):
		return shape.at ( rnd.uniform ( 0, pyx.unit.tocm(shape.arclen()) ) )	

			
	def decay(self,rate=0.1):
		self.delete(partition='inDECAY')
		self.extract(srcPartition='FISSILE',destPartitions=['inDECAY'],move=True,rate=rate)
		self.generate(GeometrieReaktorB.generateRay,srcPartition='inDECAY',productChannels=[['castRAYS']])

	def fission(self,fissilePartitions,rate=1.0):
		self.delete(partition='inFISS')
		self.delete(partition='absRAYS')
		self.delete(partition='emmiRAYS')
		self.intersectLinesBoundCircles(
			linesPartition='castRAYS',circlesSource=fissilePartitions,
			linesDestination='XXX',circlesDestination='inFISS',
			productChannels=[['newcastRAYS'],['absRAYS']],rate=rate)
		self.delete(partition='XXX')
		self.deletePartition('XXX')
		self.move(srcPartition='castRAYS',destPartitions=['emmiRAYS'])
		self.move(srcPartition='newcastRAYS',destPartitions=['castRAYS'])

	def addBlock(self,x1,y1,x2,y2,r,N,partition):
		print partition, x1,y1,x2,y2
		X=list(rnd.uniform(x1,x2,N))
		Y=list(rnd.uniform(y1,y2,N))
		#print X
		#print Y
		collection = [pyx.path.circle(x,y,r) for x,y in zip(X,Y)]
		self.addElements(collection,["FISSILE",partition])
		#self.bboxPartition(partition)
		
	def addBlockSubdiv(self,x1,y1,x2,y2,xdiv,ydiv,r,N,partitionPrefix):
		xstep = 1.0*(x2-x1) / xdiv
		ystep = 1.0*(y2-y1) / ydiv
		partitions = []
		for X in range(xdiv):
			for Y in range(ydiv):
				part = "%s_%d_%d" % (partitionPrefix,X,Y)
				self.addBlock ( x1 + X*xstep, y1 + Y*ystep, x1 + (X+1)*xstep, y1 + (Y+1)*ystep, r, round(1.0*N/(xdiv*ydiv)),  part) 
				partitions.append(part)
				self.bboxPartition(part)
		return partitions
		
	def bboxPartition (self,p):
		if self.partitions[p]:
			collection = list(self.partitions[p])
			bbox = self.allElements[collection[0]].bbox()
			for id in collection[1:]:
				bbox += self.allElements[id].bbox()
			self.bboxes[p] = bbox
			#self.addElement(bbox.rect(),partitions=['BBOX'])
		else:
			try:
				del self.bboxes[p]
			except KeyError:
				pass

	def intersectLinesBoundCircles(self,linesPartition,circlesSource,linesDestination,circlesDestination,productChannels=[],rate=1.0):
		output = [ [] for destPartitions in productChannels ]
		notconsumed = set()
		while self.partitions[linesPartition]:
			id1 = self.partitions[linesPartition].pop()
			isLineConsumed = False
			for cpart in circlesSource:
				bboxrect = self.bboxes[cpart].path()
				#print cpart, '\n---',  self.bboxes[cpart], '\n---', bboxrect, '\n---', self.allElements[id1]
				hit = bboxrect.intersect(self.allElements[id1])
				if hit == ([],[]):
					continue	## jump to the next circlesSource
				#self.addElement(bboxrect,partitions=['BBOX'])
				for id2 in self.partitions[cpart]:
					if rnd.random()<rate:
						products = GeometrieReaktorB.interactRayFissile(self.allElements[id2],self.allElements[id1])	## =~ interact(ATOM,RAY)
						if products:
							for chan,results in zip(output,products):
								chan+=results
							self.partitions[cpart].remove(id2)
							self.partitions[circlesDestination].add(id2)
							isLineConsumed=True
							break
				if isLineConsumed:
					break				
			if isLineConsumed:
				self.partitions[linesDestination].add(id1)
			else:
				notconsumed.add(id1)
		self.partitions[linesPartition] = self.partitions[linesPartition].union(notconsumed)
				
				
		returnval = []
		for newelements,productPartitions in zip(output,productChannels):
			returnval.append(self.addElements(newelements,productPartitions))
		return returnval
