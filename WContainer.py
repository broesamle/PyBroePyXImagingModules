import collections as col
import itertools
import numpy as np
import sys
import numpy.random as rnd

class PartitionedContainer(object):
	def __init__(self):
		self.nextID = 0
		self.allElements = {}
		self.partitions = col.defaultdict(set)
		
	def getNextID(self):
		#print self.nextID
		self.nextID +=1
		return self.nextID
		
	def getPartitionLabels(self):
		return self.partitions.keys()
	
	def addElement(self,el,id=None,partitions=[]):
		#print "ADDEL:", el
		if not id:	id = self.getNextID()
		if id in self.allElements: raise KeyError("ID exists %s" %id)
		else:	self.nextID = id+1
		self.allElements[id] = el
		for p in partitions:
			self.partitions[p].add(id)
		return id
			
	def addElements(self,elements,partitions=[]):
		ids = []
		for el in elements:
			id = self.getNextID()
			ids.append(id)
			self.allElements[id] = el
		as_set = set(ids)
		for p in partitions:
			self.partitions[p] = self.partitions[p].union(as_set)
		return ids
					
	def getPartition(self,pa):
		return self.partitions[pa]
		
	def generateFrom(self,fn,srcPartition,destPartitions,N=1):
		""" srcPartition defines a fixed set of elements which is passed to N calls to fn; the return values are added to the destPartitions. fn is required to take the same number of parameters as there are elements in source partition."""
		
		newelements = [ fn( *self.retrieve(srcPartition) ) for i in range(N)]
		#print N, srcPartition, destPartitions, newelements
		self.addElements(newelements,destPartitions)
	
						
	def generate(self,fn=(lambda x:[x]),srcPartition=None,productChannels=[]):
		if not srcPartition:
			ids = self.allElements.keys()
		else:
			ids = self.partitions[srcPartition]

		output = [ [] for destPartitions in productChannels ]
		for id in ids:
			products = fn(self.allElements[id])
			#print products
			for chan,results in zip(output,products):
				#print results
				chan+=results

		#print output
		returnval = []
		for newelements,productPartitions in zip(output,productChannels):
			#print newelements, productPartitions
			returnval.append(self.addElements(newelements,productPartitions))
		return returnval
	
		
	def apply(self,fn,id=None,partition=None,**kwargs):
		if id:
			self.allElements[id] = fn(self.allElements[id],**kwargs)
		elif partition:
			for id in self.partitions[partition]:
				self.allElements[id] = fn(self.allElements[id],**kwargs)
		else:
			for id,el in self.allElements.iteritems():
				self.allElements[id]=fn(self.allElements[id],**kwargs)
				
	def addTo(self,id,partition):
		if id not in self.allElements:	raise KeyError(id)
		self.partitions[partition].add(id)

	def removeFrom(self,id,partition):
		if id not in self.allElements:	raise KeyError(id)
		self.partitions[partition].remove(id)
		
	def move(self,srcPartition,destPartitions):
		for pa in destPartitions:
			self.partitions[pa] = self.partitions[pa].union(self.partitions[srcPartition])
		self.partitions[srcPartition] = set()
		
	def delete(self,id=None,partition=None):
		#print "DEL", partition, self.partitions
		if id:
			for pa in self.partitions.keys():	
				try:
					self.partitions[pa].remove(id)
				except KeyError:
					pass
		elif partition:
			tobedeleted = self.partitions[partition]
			self.partitions[partition] = set()		# all elements from this partition will be deleted!
			for id in tobedeleted:
				del self.allElements[id]				
				for pa in self.partitions.keys():	
					try:
						self.partitions[pa].remove(id)
					except KeyError:
						pass				
		else:
			raise ValueError("Either id or partition must be specified.")
	
	def deletePartition(self,p):
		del self.partitions[p]

	def retrieve(self,partition):
		return [ self.allElements[k] for k in self.partitions[partition] ]
			
class StochasticInteractionContainer(PartitionedContainer):
	def __init__(self,rnd=None,*args,**kwargs):
		PartitionedContainer.__init__(self,*args,**kwargs)
		
		
	def extract(self,srcPartition=None,destPartitions=[],rate=0.0,move=False):
		if not srcPartition:	
			if move:	raise ValueError("option move requires source partition to be defined")
			ids = self.allElements.keys()
		else:					
			ids = self.partitions[srcPartition]

		extract = [ el for el in itertools.compress ( ids, list(rnd.choice([0,1],len(ids),p=[(1-rate),rate])) ) ]
		as_set = set(extract)
		if destPartitions:
			for pa in destPartitions:
				self.partitions[pa] = self.partitions[pa].union(as_set) 
		if move:	
			self.partitions[srcPartition] -= as_set
		return extract

	def interact(self,srcPartition1,srcPartition2,destPartition1,destPartition2,productChannels=[],interact=(lambda el1,el2:"FEHLER"),rate=1.0):
		""" goes through all combinations of elements in the source channels srcPartition1 x srcPartition2. 
			For each combination, with a propability of rate interact will be applied to the two elements. 
			If the result evaluates to True it is treated as a list with the NEW elements (=PRODUCTS) for each product channel. 
			productChannels specifies partitions for the products, with one partitions list for each output channel.
			len(destChannels) == len(PRODUCTS) 
			If destPartition1/2 is set then the object is "consumed", that is it is moved from its srcPartition1/2 into the respective destPartition1/2. 
			Object identity is preserved here(, which is not the case for the products).
			"""
		
		output = [ [] for destPartitions in productChannels ]
		
		notconsumed = set()
		while self.partitions[srcPartition1]:
			id1 = self.partitions[srcPartition1].pop()
			consumed = False
			for id2 in self.partitions[srcPartition2]:
				if rnd.random()<rate:
					products = interact(self.allElements[id1],self.allElements[id2])
					if products:
						for chan,results in zip(output,products):
							chan+=results
						self.partitions[srcPartition2].remove(id2)
						self.partitions[destPartition2].add(id2)
						consumed=True
						break
			if consumed:
				self.partitions[destPartition1].add(id1)
			else:
				notconsumed.add(id1)
		self.partitions[srcPartition1] = self.partitions[srcPartition1].union(notconsumed)
				
		returnval = []
		for newelements,productPartitions in zip(output,productChannels):
			returnval.append(self.addElements(newelements,productPartitions))
		return returnval
		
		
class ContainerPrinter(object):
	def __init__(self,textOutput=sys.stdout):
		self.out = textOutput
		self.partitions = []
		self.labels = []
		self.widths = []
		
	def addPartition(self,partition,label,width):
		self.partitions.append(partition)
		self.labels.append(label)
		self.widths.append(width)
		
	def printHeader(self):
		for l,w in zip(self.labels,self.widths):
			#print l, w
			form = format(l,'>'+str(w))
			self.out.write( form + '\t')
		self.out.write('\n')
		
	def printPartitionLengths(self,con,textOutput=None):
		if not textOutput:
			textOutput = self.out
		for p,w in zip(self.partitions,self.widths):
			textOutput.write(format(len(con.getPartition(p)),'>'+str(w)) + ' ')
		
		textOutput.write('')	
		for p in con.getPartitionLabels():
			if p not in self.partitions:
				textOutput.write(" %s:%d"%(p,len(con.getPartition(p))))
		textOutput.write('\n')