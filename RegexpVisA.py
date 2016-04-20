# -*- encoding: utf-8 -*-

import re

import pyx
from pyx.unit import w_mm,x_mm,x_pt,v_mm,u_mm

import LatexCodec
LatexCodec.register()

from WSpatialText import SpatialStringB
from WCanvas import ProtocolCanvas

### Arguments ###
import argparse
parser = argparse.ArgumentParser(description='...')
parser.add_argument('-o','--outfilename', type=str, default="out.pdf", help='Output image filename')
args = parser.parse_args()

class SparseObjectField(object):
	def __init__(self,NA_value=None,validKey=(lambda x:True)):
		self.field = {}
		self.setNA(NA_value)
		self.validKey = validKey
	
	def setNA (self,NA_value=None):
		self.NA = NA_value
	
	def getElement(self,key):
		if not self.validKey(key): raise (KeyError("Invalid Key: %s" % repr(key)))
		if key in self.field:	return self.field[key]
		else: return self.NA
	
	def setElement(self,key,element):
		if not self.validKey(key): raise (KeyError("Invalid Key: %s" % repr(key)))
		self.field[key] = element

	def apply(self,f=(lambda x:x)):
		for key,value in self.field.iteritems():
			self.field[key] = f(value)

		
	def __repr__(self):
		return repr(self.field)

	
class ScatteredString(SparseObjectField):
	def __init__(self,str):
		#print "Text:", repr(str), "len:",len(str)
		self.str = str
		SparseObjectField.__init__( self, "", ( lambda (i,j) : ((0<=i) and (i <=len(str)) and (1<=j) and (j <=0,len(str)+1)) ) )
		for i in range(0,len(self.str)):
			for j in range(i+1,len(self.str)+1):
				print "X", i, j, repr(str[i:j]) 
				self.setElement((i,j),str[i:j])
		
class RegexpField(ScatteredString):
	def compileAll(self):
		self.regexps = {}
		for key in self.field.keys():
			try:
				regexp = re.compile(self.field[key])
				#print "OK ", repr(self.field[key])
				self.regexps[key] = regexp
			except re.error:
				#print "NO ", repr(self.field[key])
				del self.field[key]
			
					
class StringFieldVisualiser(object):
	def __init__(self,yscale=1):
		self.xmargpos = -1*u_mm
		self.ymargpos = +1*u_mm
		self.yscale = yscale
		
	def makeLaTeXt(self,str):
		#return str.encode('latex').replace("\\","$\\backslash$").replace("^","$\\wedge$").replace("|","$|$").replace("<","$<$").replace(">","$>$").replace("&","\&")
		return pyx.text.escapestring(str)
		
	def completePlotSCT(self,can,scatteredstring,style=[],bullet=""):
		for i in range(0,len(scatteredstring.str)):
			for j in range(1,len(scatteredstring.str)+1):
				el = scatteredstring.getElement((i,j))
				texstr = self.makeLaTeXt(scatteredstring.getElement((i,j)))
				print i, j, str, texstr 				
				can.text(i*u_mm,-j*u_mm*self.yscale-2*x_mm,"%d/%d"%(i,j),[pyx.text.size.tiny])
				if scatteredstring.getElement((i,j)) != "":
					can.text(i*u_mm,-j*u_mm*self.yscale,texstr,style)
					can.text(i*u_mm,-j*u_mm*self.yscale,bullet,style)

					
	def plotUnderlinesByLength(self,can,scatteredstring):
		for i in range(0,len(scatteredstring.str)):
			for j in range(1,len(scatteredstring.str)+1):
				el = scatteredstring.getElement((i,j))
				if el != "":
					x1 = i*u_mm
					#y1 = -j+i*v_mm
					y1 = -j*u_mm*self.yscale-i*0.40*w_mm
					#print i, j, y1
					x2 = x1 + (len(el)-1)*u_mm + 5*x_mm
					style = [pyx.color.rgb(0,0.7,0),pyx.color.transparency(0.50)]
					can.stroke(pyx.path.line(x1, y1,  x2, y1), style)
					#can.stroke(pyx.path.rect(x1, y1, w_mm, w_mm), style)
					#can.stroke(pyx.path.rect(i*self.xscale-offset,j*self.yscale+offset+i*offset2,(len(el)-1)*self.xscale+2*offset,0.2),[pyx.color.rgb(0,0.7,0),pyx.color.transparency(0.75)])
		
	def plotStringMatrix(self,can,scatteredstring,style=[],supressY=False):
		for i in range(0,len(scatteredstring.str)):
			texstr = self.makeLaTeXt(scatteredstring.str[i])
			can.text(i*u_mm,self.ymargpos*self.yscale,'{\\tt '+texstr+'}',style)
			if not supressY:
				can.text(self.xmargpos,-(i+1)*u_mm*self.yscale,'{\\tt '+texstr+'}',style+[pyx.text.halign.boxright])	
			#can.stroke(pyx.path.line(i*u_mm, 0,  i*u_mm, -len(scatteredstring.str)*u_mm*self.yscale),[pyx.color.rgb(0.7,0.7,0.7)])
#		for j in range(0,len(scatteredstring.str)+1):
#			texstr = self.makeLaTeXt(scatteredstring.str[j])
		

class MatchVisualiser(StringFieldVisualiser):
	def __init__(self,Text,yscale=1):
		StringFieldVisualiser.__init__(self,yscale=yscale)
		self.txt = SpatialStringB(Text)
		
	def plotText(self,can,style=[]):
		markers = []
		markedsnippet = u""
		for i,c  in enumerate(self.txt):
			#print i, c
			markers.append("M%05d" % i)
			markedsnippet += "\\PyXMarker{%s}{\\tt %s}" % (markers[i],  self.makeLaTeXt(c))		
		markers.append("M%05d" % (i+1))
		markedsnippet += "\\PyXMarker{%s}" % markers[i+1]
		
		t = can.text(self.xmargpos,0,markedsnippet,style+[pyx.text.halign.boxright,pyx.trafo.rotate(90,x=0,y=0)])
		mks = [ t.marker(m) for m in markers ]
		#print mks,self.txt
		self.txt.setAllPos(mks)

	def plotMatches(self,can,REField):
		print REField
		for i in range(0,len(REField.str)):
			for j in range(1,len(REField.str)+1):
				el = REField.getElement((i,j))
				print el
				if el:
					for m in re.compile(el).finditer(self.txt):
						#print "A",m,m.start(0), m.end(0)
						if m.start(0) != m.end(0):
							#x1,y1 = self.txt[].pos
							#x2,y2 = self.txt[m.end(0)].pos
							(x1,y1),(x2,y2) = self.txt[m.start(0):m.end(0)].getStartStopPos()
							
							can.stroke(pyx.path.line(i*u_mm,     y1,         j*u_mm,            y2),[pyx.color.rgb(0,0.7,0),pyx.color.transparency(0.70)])
							can.stroke(pyx.path.rect(i*u_mm+0.5*w_mm,y1+0.5*w_mm,j*u_mm-i*u_mm-w_mm,y2-y1-w_mm) , [pyx.color.rgb(0,0.7,0),pyx.color.transparency(0.70),pyx.deco.filled([pyx.color.rgb(0,0.7,0),pyx.color.transparency(0.96)])])

	def plotStringMatrix(self,can,scatteredstring,style=[],supressY=True):
		StringFieldVisualiser.plotStringMatrix(self,can,scatteredstring,style,supressY)

	#def plotMarkedText
	#	""" plot something somewhere -- but remember what and where """

thetext3 = """<div class="tabContent hide" id="Thu"><h4>THURSDAY, APRIL 3, 2014</h4><br><div><h4>Time &amp; Program</h4><p><strong>00:00</strong> <a href="http://www.cnbc.com/id/46189136" target="_self">The Tonight Show Starring Jimmy Fallon</a><br><strong>00:30</strong> <a href="http://www.nbcnews.com/nightly-news" target="_blank">NBC Nightly News</a><br><strong>01:00</strong> <a href="http://www.cnbc.com/id/15838831" target="_self">Asia Squawk Box</a><br><strong>04:00</strong> <a href="http://www.cnbc.com/id/101495499" target="_self">Street Signs (Asia)</a><br><strong>06:00</strong> <a href="http://www.cnbc.com/id/17501773" target="_self">Capital Connection</a><br><strong>07:00</strong> <a href="http://www.cnbc.com/id/15838831" target="_self">Squawk Box</a><br><strong>08:00</strong> <a href="http://www.cnbc.com/id/15838831" target="_self">Squawk Box</a><br><strong>10:00</strong> <a href="http://www.cnbc.com/id/15838355" target="_self">Worldwide Exchange</a><br><strong>12:00</strong> <a href="http://www.cnbc.com/id/15838368" target="_self">US Squawk Box </a><br><strong>12:45</strong> <a href="http://www.cnbc.com/id/" target="_self">Strictly Rates</a><br><strong>01:45</strong> <a href="http://www.cnbc.com/id/15838368" target="_self">US Squawk Box</a><br><strong>14:30</strong> <a href="http://www.cnbc.com/id/" target="_self">ECB Presser</a><br><strong>14:45</strong> <a href="http://www.cnbc.com/id/" target="_self">US CNBC</a><br><strong>15:00</strong> <a href="http://www.cnbc.com/id/15838381" target="_self">Squawk On The Street</a><br><strong>17:00</strong> <a href="http://www.cnbc.com/id/15838629" target="_self">European Closing Bell </a><br><strong>18:00</strong> <a href="http://www.cnbc.com/id/30809994" target="_self">Fast Money Half Time Report</a><br><strong>19:00</strong> <a href="http://www.cnbc.com/id/15838342" target="_self">US Power Lunch</a><br><strong>20:00</strong> <a href="http://www.cnbc.com/id/15838408" target="_self">US Street Signs</a><br><strong>21:00</strong> <a href="http://www.cnbc.com/id/15838421" target="_self">US Closing Bell</a><br><strong>23:00</strong> <a href="http://www.cnbc.com/id/47984825" _self"="">Access Middle East</a><br><strong>23:30</strong> <a href="http://www.cnbc.com/id/1010035721" target="_self">The Edge</a><br> </p><p></p>"""
thetext3 = """<div class="tabContent hide" id="Thu"><h4>THURSDAY, APRIL 3, 2014</h4><br><div><h4>Time &amp; Program</h4><p><strong>00:00</strong> <a href="http://www.cnbc.com/id/46189136" target="_self">The Tonight Show Starring Jimmy Fallon</a>"""
#thetext3 = """<div class="tabContent hide" id="Thu"><h4>THURSDAY, APRIL 3, 2014</h4><br><div><h4>Time &amp; Program</h4>"""

def demo3 ():
	#can = pyx.canvas.canvas()
	can = ProtocolCanvas()
	#pyx.unit.set(xscale=0.5)	
	pyx.unit.set(uscale=4.5)
	pyx.unit.set(wscale=0.3)
	#sc = RegexpField(u'l')
	sc = RegexpField(u'<a (?:[^<>\s]+\s+)+href="[^"<>]*"[^<>]*>(.*?)<\/a>')
	sc.compileAll()
	vis = MatchVisualiser(thetext3,yscale=0.4)
	vis.plotStringMatrix(can,sc)
	vis.plotText(can)
	vis.plotMatches(can,sc)

	print "writing file", args.outfilename
	can.writePDFfile(args.outfilename)
	
	
def demo ():
	#ACHTUNG: DAUERT LANGE!
	####sc = ScatteredString(u"Ein gescheiter Text mit vernünftiger Länge. Nach einem ersten Vorversuch weiß ich, durch schauen, auch wenn man es sich logisch hätte klarmachen können: Es gibt einen umgedrehten Tannenbaum. Das überrascht auch nach Jahren immer wieder -- Der Kopf ist eben doch keine formale Visualisierungsmaschine.")
	
	#sc = ScatteredString(u"Ein gescheiter Text.")
	sc = ScatteredString(u"Ein Text.")
	can = pyx.canvas.canvas()
	vis = StringFieldVisualiser()
	vis.completePlotSCT(can,sc)
	print "writing file", args.outfilename	
	can.writePDFfile(args.outfilename)

def demo2 ():
	can = pyx.canvas.canvas()
	#pyx.unit.set(xscale=0.5)	
	pyx.unit.set(uscale=4.5)
	pyx.unit.set(wscale=0.3)
	#sc = RegexpField(u'^.*?<div class="b-g-p [^"<>]*programmes-page"[^<>]*>.*?<div class="[^"<>]*broadcast[^"<>]*"[^<>]*>')
	sc = RegexpField(u'^(.*?(?:film|serie)[^\d]*?)\s+\(?,?(\d\d\d\d)\)?\s*([^\d]*) js')
	vis = StringFieldVisualiser(yscale=0.4)
	vis.plotStringMatrix(can,sc)
	#vis.completePlotSCT(can,sc,style=[pyx.color.transparency(0.8)])
	sc.compileAll()
	#vis.completePlotSCT(can,sc,style=[pyx.color.rgb(1.0,0,0)])
	vis.plotUnderlinesByLength(can,sc)
	print "writing file", args.outfilename
	can.writePDFfile(args.outfilename)
	
demo3()