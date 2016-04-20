from sys import argv

import re
import pyx
import random 
from collections import defaultdict

from WSpatialText import SpatialStringB

class ProtocolCanvas(pyx.canvas.canvas):
	def __init__(self,*args,**kwargs):
		self.spatialstrings = []
		self.spstrByID = {}
		self.spstrByText = defaultdict(list)
		return pyx.canvas.canvas.__init__(self,*args,**kwargs)
		
	def makeLaTeXt(self,str):
		#return str.encode('latex').replace("\\","$\\backslash$").replace("^","$\\wedge$").replace("|","$|$").replace("<","$<$").replace(">","$>$").replace("&","\&")
		return pyx.text.escapestring(str)
		
	def placeText(self,x,y,text,*args,**kwargs):
		markers = []
		markedsnippet = u""
		for i,c  in enumerate(text):
			markers.append("M%05d" % i)
			markedsnippet += "\\PyXMarker{%s}{\\tt %s}" % (markers[i],  self.makeLaTeXt(c))		
		markers.append("M%05d" % (i+1))
		markedsnippet += "\\PyXMarker{%s}" % markers[i+1]
		
		t = pyx.canvas.canvas.text(self,x,y,markedsnippet,*args,**kwargs)
		mks = [ t.marker(m) for m in markers ]

		
		sptxt = SpatialStringB(text,mks)
		self.spatialstrings.append(sptxt)
		self.spstrByText[text].append(sptxt)
		if "textID" in kwargs:
			self.spstrByID[kwargs["textID"]] = sptxt
		return t

def demo():
	thetext = "BAAB"
	pyx.unit.set(uscale=10)
	pyx.unit.set(wscale=0.2)
	rnd = random.Random()
	rnd.seed(2)
	rnd2 = random.Random()
	#rnd2.seed(16)
	can = ProtocolCanvas()
	
	#can.placeText(rnd.random(),rnd.random(),thetext,[pyx.trafo.rotate(360*rnd.random(),rnd.random(),rnd.random())])
	can.placeText(rnd.random(),rnd.random(),argv[1],[pyx.trafo.rotate(360*rnd.random(),rnd.random(),rnd.random())])
	for i in range(1):
		cuts = list(set([rnd2.randrange(len(thetext)) for a in range(len(thetext)/1)]))
		cuts.sort()
		c0 = cuts[0]
		shuffledtext = [thetext[:c0]]
		for c1 in cuts[1:]:
			print c0,c1 
			shuffledtext.append(thetext[c0:c1])
			c0 = c1
		shuffledtext.append(thetext[c1:])
		print shuffledtext
		rnd2.shuffle(shuffledtext)
		####shuffle on:#### thetext = reduce((lambda a,b:a+b),shuffledtext)
		print thetext
		can.placeText(rnd.random(),rnd.random(),argv[2],[pyx.trafo.rotate(360*rnd.random(),rnd.random(),rnd.random())])
	
	minlen = 1
	for i in range(40):
		s = rnd2.choice(can.spatialstrings)
		a, b =0, 0
		while b - a <= minlen: 
			a = rnd2.randrange(len(s))
			b = rnd2.randrange(a,len(s)+1)
		
		pat = s[a:b]
		try:
			regexp = re.compile(pat)
			s2 = rnd2.choice(can.spatialstrings)
			for m in regexp.finditer(s2):
				(x1,y1),(x2,y2) = pat.getStartStopPos()
				(x3,y3),(x4,y4) = s2[m.start(0):m.end(0)].getStartStopPos()										
				polypath = pyx.path.path()
				polypath.append(pyx.path.moveto(x1,y1))
				polypath.append(pyx.path.lineto(x2,y2))
				polypath.append(pyx.path.lineto(x4,y4))
				polypath.append(pyx.path.lineto(x3,y3))
				polypath.append(pyx.path.closepath())
				thecolor = pyx.color.rgb(rnd2.random()*0.9,rnd2.random()*0.7,rnd2.random()*0.7)
				can.stroke(polypath, [thecolor,pyx.color.transparency(0.70),pyx.deco.filled([thecolor,pyx.color.transparency(0.90)])])	
		except re.error:
			pass
	can.writePDFfile("out.pdf")

demo()