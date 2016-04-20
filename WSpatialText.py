import warnings

class SpatialString_deprecated(unicode):
	""" provides s Unicode String which, for each character, has an additional component for handling position data."""
	
	def __new__(self, value, positions = None):
		return unicode.__new__(self, value)

	def __init__(self, value, positions = None):
		if positions == None:	## haessliche variante mit einer zeile N (None,None) tupel zu machen 
								self.pos = [[(None,None)] * len(self)][0]
		else:					self.pos = positions
		warnings.warn(DeprecationWarning("SpatialStringB should be used, which adds an extra position behind the last character."))
	
	def __getslice__(self,a,b):
		return SpatialString(unicode.__getslice__(self,a,b),self.pos[a:b])
	
	def __getitem__(self,i):
		#print "getitem", i, self, self.pos
		return SpatialString(unicode.__getitem__(self,i),self.pos[i])

	def setPosIdx(self,idx,pos):
		self.pos[idx] = pos
		
	def setAllPos(self,P):
		if len(P) != len(self):	raise ValueError("Positions List must be of same length!")
		self.pos = P
		
	def __repr__(self):
		s = str.__repr__(self) + unicode(self.pos)
		return s

class SpatialStringB(unicode):
	def __new__(self, value, positions = None):
		return unicode.__new__(self, value)

	def __init__(self, value, positions = None):
		if positions == None:	self.pos = [ (None,None) for i in range(len(self)+1) ]
		else:					self.setAllPos(positions)
	
	def setAllPos(self,positions):
		#print positions
		#print positions, self
		if len(positions) != len(self)+1:	raise ValueError("Positions List must be one element longer than the string!")
		self.pos = positions
		
	def __getslice__(self,a,b):
		return SpatialStringB(unicode.__getslice__(self,a,b),self.pos[a:b+1])
	
	def __getitem__(self,i):
		#print "getitem", i, self, self.pos
		return SpatialStringB(unicode.__getitem__(self,i),self.pos[i:i+2])
		
	def getStartStopPos(self):
		return self.pos[0],self.pos[-1]

	def __repr__(self):
		s = str.__repr__(self) + unicode(self.pos)
		return s
		