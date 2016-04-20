import LatexCodec
LatexCodec.register()


import pyx, os

suffixes = ['','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y',
			'ZAAAA','ZAAAB','ZAAAC','ZAAAD','ZAAAE','ZAAAF','ZAAAG','ZAAAH','ZAAAI','ZAAAJ','ZAAAK','ZAAAL','ZAAAM','ZAAAN','ZAAAO','ZAAAP','ZAAAQ','ZAAAR','ZAAAS','ZAAAT','ZAAAU','ZAAAV','ZAAAW','ZAAAX','ZAAAY','ZAAAZ',
			'ZAABA','ZAABB','ZAABC','ZAABD','ZAABE','ZAABF','ZAABG','ZAABH','ZAABI','ZAABJ','ZAABK','ZAABL','ZAABM','ZAABN','ZAABO','ZAABP','ZAABQ','ZAABR','ZAABS','ZAABT','ZAABU','ZAABV','ZAABW','ZAABX','ZAABY','ZAABZ']


class PyXMultipageRenderer(object):
	black = pyx.color.rgb(0,0,0)
	red = pyx.color.rgb(1,0,0)
	yellow = pyx.color.rgb(0.9,0.8,0)
	gray4 = pyx.color.rgb(0.4,0.4,0.4)
	
	def __init__(self,outFilename,simulate=False,makePDF=True,makeEPS=False,maxPages=500,bbox=None,parameterInfo=None):
		self.bbox = bbox
		self.pagecount = 0	
		self.pageopen = False

		self.makePDF = makePDF
		self.makeEPS = makeEPS

		
		self.simulate=simulate
		self.fnameCnt = 0				

		i = 0
		self.outFilename = outFilename+suffixes[i]
		while os.path.exists(self.nextPDFName()) or os.path.exists(self.nextEPSName()):
			i+=1
			self.outFilename = outFilename+suffixes[i]
		
		if not self.simulate:			
			if self.makePDF:
				self.pdfDoc = pyx.document.document(pages=[])
				self.maxPages = maxPages	# every X pages a new pdf file is started / for saving memory
				
			#if parameterInfo:
			#	self.newPage()
			#	textX,textY = self.bbox.center()
			#	textY = self.bbox.top()
			#	for key,value in parameterInfo.iteritems():
			#		print key, value
			#		self.can.text(0,0,'X')
			#		self.can.text(textX+pyx.unit.x_pt*-2,textY,str(key).encode('latex'),[pyx.text.halign.right])
			#		self.can.text(textX+pyx.unit.x_pt*7,textY,str(value).encode('latex'),[pyx.text.halign.left])
			#		textY -= pyx.unit.x_pt * 15
			#	self.outputCurrentPage()

	def nextPDFName(self):
		return "%s_%03d.pdf" % (self.outFilename,int(self.fnameCnt))
		
	def nextEPSName(self):
		return "%s_p%04d.eps" % (self.outFilename,int(self.pagecount))
			
	#def renderPageInfo:
		
	def outputCurrentPage(self):	
		if not self.simulate:
			#if self.putPageInfo:	self.putPageInfo():

			if (self.makePDF):	self.pdfDoc.append( pyx.document.page(self.can,paperformat=pyx.document.paperformat.A4,margin=5*pyx.unit.t_mm,fittosize=1,rotated=1,bbox=self.bbox) )
			if (self.makeEPS):	self.can.writeEPSfile(self.nextEPSName())
			if (self.makePDF and (self.pagecount % self.maxPages == 0)):
				self.pdfDoc.writePDFfile(self.nextPDFName())		
				print "wrote file " + self.nextPDFName()
				self.pdfDoc = pyx.document.document(pages=[])
				self.fnameCnt += 1
				self.pageopen = False
			

	def newPage(self):
		if not self.simulate:
			#print "XX"
			self.can = pyx.canvas.canvas()
			self.pageopen = True
			self.pagecount+=1
			
	def __del__(self):
		#self.outputCurrentPage()
		if not self.simulate:
			if (self.pageopen and self.makePDF):
				print "write final file " + self.nextPDFName()
				self.pdfDoc.writePDFfile(self.nextPDFName())		
			if (self.pageopen and self.makeEPS):
				print "write final file " + self.nextEPSName()
				self.can.writeEPSfile(self.nextEPSName())
		else:
			if self.makePDF:
				print "write final DUMMY file " + self.nextPDFName()
				f = open(self.nextPDFName(),'w')
				f.write("DUMMY.")
				f.close()
			if self.makeEPS:
				print "write final DUMMY file " + self.nextEPSName()
				f = open(self.nextEPSName(),'w')
				f.write("DUMMY.")
				f.close()
			