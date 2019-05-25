class XFSCommon(object):
	CLASSTYPES = {
		0: "undefined",
		1: "class",
		2: "classref",
		3: "bool",
		4: "u8",
		5: "u16",
		6: "u32",
		7: "u64",
		8: "s8",
		9: "s16",
		10: "s32",
		11: "s64",
		12: "f32",
		13: "f64",
		14: "string",
		15: "color",
		16: "point",
		17: "size",
		18: "rect",
		19: "matrix44",
		20: "vector3",
		21: "vector4",
		22: "quaternion",
		23: "property",
		24: "event",
		25: "group",
		26: "pagebegin",
		27: "pageend",
		28: "event32",
		29: "array",
		30: "propertylist",
		31: "groupend",
		32: "cstring",
		33: "time",
		34: "float3",
		35: "float4",
		36: "float3x3",
		37: "float4x3",
		38: "float4x4",
		39: "easecurve",
		40: "line",
		41: "linesegment",
		43: "plane",
		44: "sphere",
		45: "capsule",
		46: "aabb",
		48: "cylinder",
		49: "triangle",
		50: "cone",
		51: "torus",
		52: "ellpsoid",
		53: "range",
		54: "rangef",
		55: "rangeu16",
		56: "hermitecurve",
		57: "enumlist",
		58: "float3x4",
		59: "linesegment4",
		60: "aabb4",
		61: "oscillator",
		62: "variable",
		63: "vector2",
		64: "matrix33",
		65: "rect3d_xz",
		66: "rect3d",
		67: "rect3d_collision",
		68: "plane_xz",
		69: "ray_y",
		70: "pointf",
		71: "sizef",
		72: "rectf",
		128: "resource"
	}

	def __init__(self, filename, ios=False, oldIos=False):
		self.file = open(filename, "rb")
		self.ios = ios
		self.oldIos = oldIos
		self.logFile = None
		if self.file.read(4) != b"XFS\x00":
			raise ValueError("Invalid XFS")

	def readIntDword(self):
		return self.unpack("<i",self.file.read(4))[0]

	def getAndReadIntDword(self):
		tmp = self.file.read(4)
		return (tmp, self.unpack("<i",tmp)[0])

	def writeIntDword(self, arg):
		self.output.write(self.pack("<i",arg))

	def formatIntDword(self, arg):
		return self.pack("<i", arg)

	def readIntWord(self):
		return self.unpack("<h",self.file.read(2))[0]		

	def readIntQword(self):
		return self.unpack("<q",self.file.read(8))[0]

	def getAndReadIntQword(self):
		tmp = self.file.read(8)
		return (tmp, self.unpack("<q",tmp)[0])

	def readGeneralInt(self):
		if self.ios:
			return self.readIntQword()
		else:
			return self.readIntDword()

	def getAndReadGeneralInt(self):
		if self.ios:
			return self.getAndReadIntQword()
		else:
			return self.getAndReadIntDword()

	def formatGeneralInt(self, arg):
		if self.ios:
			return self.pack("<i",arg)
		else:
			return self.pack("<q",arg)

	def formatIntWord(self, arg):
		return self.pack("<H", arg)

	def readStringFromOffset(self, offset):
		returnOffset = self.file.tell()
		self.file.seek(offset)
		output = ""
		while True:
			buf = self.file.read(1)
			if buf == b"\x00":
				break
			output += buf.decode("ascii")
		self.file.seek(returnOffset)
		return output

	def readNullTerminatedString(self):
		output = ""
		while True:
			buf = self.file.read(1)
			if buf == b"\x00":
				break
			output += buf.decode("ascii")
		return output

	def readSingleByteInt(self):
		return self.unpack("B",self.file.read(1))[0]

	def getAndReadIntWord(self):
		try:
			tmp = self.file.read(2)
			return (tmp, self.unpack("<h",tmp)[0])
		except Exception as e:
			print(self.file.tell())
			raise e

	def writeIntWord(self, arg):
		self.output.write(self.pack("<h",arg))

	def dPrint(self, log, *args):
		if log:
			print(args)
			if not self.logFile:
				self.logFile = open("log.txt", "w")
			self.logFile.write(args[0] + str(args[1]) + "\n")

	def readHeader(self, log=False):
		self.version = self.readIntDword()
		self.dPrint(log,"XFS Version: ", self.version)
		self.int1 = self.readIntDword()
		self.dPrint(log,"int1: ", self.int1)
		self.xfsType = self.readIntDword()
		self.dPrint(log,"XFS Type: ", self.xfsType)
		self.structCount = self.readIntDword()
		self.dPrint(log,"Struct Count: ", self.structCount)
		self.startOffset = self.readIntDword() + 0x18
		self.dPrint(log,"Adjusted Start Offset: ", self.startOffset)
		self.structOffsets = []
		self.names = []
		for x in range(self.structCount):
			offset = self.readGeneralInt()
			self.dPrint(log,"Struct offset ", x, ": ", offset)
			self.structOffsets.append(offset)
		self.structList = []
		for x in range(self.structCount):
			self.dPrint(log,"==> Struct ", x, ":")
			struct = {}
			structhash = self.readGeneralInt()
			self.dPrint(log,"==> Hash: ", structhash)
			subcount = self.readGeneralInt()
			self.dPrint(log,"==> Subclass count: ", subcount)
			subclasses = []
			for x in range(subcount):
				self.dPrint(log,"====> Subclass ", x, ":")
				nameOffset = self.readGeneralInt() + 0x18
				name = self.readStringFromOffset(nameOffset)
				self.dPrint(log,"====> Name: ", name)
				subtype = self.readSingleByteInt()
				self.dPrint(log,"====> Type: ", subtype)
				unknown = self.readSingleByteInt()
				self.dPrint(log,"====> Unknown: ", unknown)
				size = self.readSingleByteInt()
				self.dPrint(log,"====> Size: ", size)
				if(self.ios):
					self.file.seek(0x45, 1)
				elif (self.oldIos):
					self.file.seek(0x21, 1)
				else:
					self.file.seek(0x11, 1)
				self.names.append(name)
				subclasses.append({"name": name,
									"type": subtype,
									"size": size,
									"unk": unknown})
			self.structList.append({"structhash": structhash,
									"subcount": subcount,
									"subclasses": subclasses})

	def writeHeader(self):
		#first, write out the base header
		self.output.write(b"XFS\x00")
		self.writeIntDword(self.version)
		self.writeIntDword(self.int1)
		self.writeIntDword(self.xfsType)
		self.writeIntDword(self.structCount)
		#also, we have to calculate total length first for name...
		totalLen = 0
		generalIntLen = 8
		subclassLen = 0x50
		structOffsetHeader = b""
		nameString = b""
		nameMap = {}
		for name in self.names:
			if name not in nameMap:
				nameMap[name] = len(nameString)
				nameString += name.encode() + b"\x00"
		if self.ios:
			generalIntLen = 4
			subclassLen = 0x18
		for struct in self.structList:
			structOffsetHeader += self.formatGeneralInt(totalLen + (generalIntLen * self.structCount))
			totalLen += generalIntLen * 2
			totalLen += struct['subcount'] * subclassLen
		#now we can get where the name offset will be
		structHeader = b""
		for struct in self.structList:
			structHeader += self.formatGeneralInt(struct['structhash'])
			structHeader += self.formatGeneralInt(struct['subcount'])
			for subclass in struct['subclasses']:
				structHeader += self.formatGeneralInt(totalLen + len(structOffsetHeader) + nameMap[subclass['name']])
				if subclass['type'] in [1,2,128]:
					if self.ios:
						subclass['size'] = 4
					else:
						subclass['size'] = 8
				structHeader += bytes([subclass['type']])
				structHeader += bytes([subclass['unk']])
				structHeader += bytes([subclass['size']])
				structHeader += b"\x00" * (subclassLen - 0x03 - generalIntLen)
		pad = (len(structHeader) + len(nameString) + len(structOffsetHeader) + 0x02) % 0x04 #pad to 0x04 width
		print("Padding:",pad)
		self.writeIntDword(len(structHeader) + pad + len(nameString) + len(structOffsetHeader))
		self.output.write(structOffsetHeader)
		self.output.write(structHeader)
		self.output.write(nameString)
		self.output.write(b"\x00" * pad)

class XFSToXML(XFSCommon):
	from struct import unpack
	typeHandlers = {}

	def __init__(self, filename, ios=False, oldIos=False):
		XFSCommon.__init__(self, filename, ios, oldIos)
		self.defineHandler(1, None)
		self.defineHandler(2, None)
		self.defineHandler(3, self.boolHandler)
		self.defineHandler(6, self.u32Handler)
		self.defineHandler(12, self.f32Handler)
		self.defineHandler(10, self.s32Handler)
		self.defineHandler(16, self.pointHandler)
		self.defineHandler(32, self.cstringHandler)
		self.defineHandler(128, self.resourceHandler)

	def boolHandler(self):
		a = self.file.read(1)
		if a != b"\x00":
			return ' value="true"'
		else:
			return ' value="false"'

	def f32Handler(self):
		return ' value="%s"' % self.unpack("<f", self.file.read(4))[0]

	def s32Handler(self):
		return ' value="%s"' % self.unpack("<i",self.file.read(4))[0]

	def u32Handler(self):
		return ' value="%s"' % self.readIntDword()

	def pointHandler(self):
		return ' x="%s" y="%s"' % self.unpack("<ii",self.file.read(8))

	def cstringHandler(self):
		return ' value="%s"' % self.readNullTerminatedString()

	def resourceHandler(self, recursionLevel, out, name, length):
		test = self.readSingleByteInt()
		if test is 2 or length is not 1:
			self.file.seek(-0x01, 1)
			for x in range(length):
				resType = self.readSingleByteInt()
				if resType is not 2:
					raise ValueError("Bad resource (list)!")
				output = ' value="'
				out.write("\t" * recursionLevel + "<resource type=\"")
				out.write(self.readNullTerminatedString())
				out.write('" value="')
				out.write(self.readNullTerminatedString())
				out.write('"/>\n')
			if length is 1:
				self.file.seek(0x04, 1)
		else:
			#nothing here!
			self.file.seek(-0x01 + -0x04, 1)

	def defineHandler(self, type, function):
		self.typeHandlers[type] = function

	def classHandler(self, recursionLevel, out):
		classNo = self.readIntWord() >> 1
		self.file.seek(0x02, 1)
		out.write('type="%s" length="%s">\n' % (self.structList[classNo]["structhash"],self.readGeneralInt()))
		for element in self.structList[classNo]['subclasses']:
			length = self.readIntDword()
			if length != 1:
				out.write("\t" * recursionLevel + '<array name="%s" type="%s" count="%s">\n' % (element["name"], self.CLASSTYPES[element["type"]], length))
				recursionLevel += 1
			if element["type"] == 128:
				self.resourceHandler(recursionLevel, out, element["name"], length)
			for x in range(length):
				if element["type"] not in self.typeHandlers:
					raise ValueError("Unsupported type: %s @ %s" % (element["type"],self.file.tell()))
				if element["type"] == 1:
					out.write("\t" * recursionLevel + '<class name="%s" ' % element["name"])
					self.classHandler(recursionLevel + 1, out)
					out.write("\t" * (recursionLevel) + "</class>\n")
				elif element["type"] == 2:
					out.write("\t" * (recursionLevel) + "<classref ")
					self.classHandler(recursionLevel + 1, out)
					out.write("\t" * (recursionLevel) + "</classref>\n")
				elif element["type"] == 128:
					pass
				else:
					value = self.typeHandlers[element["type"]]()
					out.write("\t" * recursionLevel + '<%s name="%s"%s/>\n' % (self.CLASSTYPES[element["type"]], element["name"], value))
			if length != 1:
				out.write("\t" * (recursionLevel - 1) + "</array>\n")

	def parseData(self):
		self.file.seek(self.startOffset + 0x04) #assuming top level is not array...
		out = open(self.file.name + ".xml", "w")
		out.write("""<?xml version="1.0" encoding="utf-8"?>
<xfs>
	<meta name="properties">
		<tag name="version">%s</tag>
		<tag name="type">%s</tag>
		<tag name="int1">%s</tag>
		<tag name="platform">%s</tag>
	</meta>
	<meta name="structs">\n""" % (self.version, self.xfsType, self.int1, "ios" if self.ios else "ac"))
		for struct in self.structList:
			out.write("""\t\t<struct>
			<tag name="hash">%s</tag>
			<tag name="classcount">%s</tag>\n""" % (struct["structhash"], struct["subcount"]))
			for subclass in struct["subclasses"]:
				out.write("""\t\t\t<class name="%s">
				<tag name="type">%s</tag>
				<tag name="size">%s</tag>
				<tag name="unknown">%s</tag>
			</class>\n""" % (subclass["name"], subclass["type"], subclass["size"], subclass["unk"]))
			out.write("""\t\t</struct>\n""")
		out.write("""\t</meta>
\t<class name="XFS" type="%s" length="%s">\n""" % (self.structList[0]["structhash"],self.readGeneralInt()))
		for topElement in self.structList[0]["subclasses"]:
			length = self.readIntDword()
			recursionLevel = 2
			if length != 1:
				out.write("\t" * recursionLevel + '<array name="%s" type="%s" count="%s">\n' % (topElement["name"], self.CLASSTYPES[topElement["type"]], length))
				recursionLevel += 1
			if topElement["type"] == 128:
				self.resourceHandler(recursionLevel, out, topElement["name"], length)
			for x in range(length):
				if topElement["type"] not in self.typeHandlers:
					raise ValueError("Unsupported type: %s @ %s" % (topElement["type"],self.file.tell()))
				if topElement["type"] == 1:
					out.write("\t" * recursionLevel + '<class name="%s" ' % topElement["name"])
					self.classHandler(recursionLevel + 1, out)
					out.write("\t" * (recursionLevel) + "</class>\n")
				elif topElement["type"] == 2:
					out.write("\t" * (recursionLevel) + "<classref ")
					self.classHandler(recursionLevel + 1, out)
					out.write("\t" * (recursionLevel) + "</classref>\n")
				elif topElement["type"] == 128:
					pass
				else:
					value = self.typeHandlers[topElement["type"]]()
					out.write("\t" * recursionLevel + '<%s name="%s"%s/>\n' % (self.CLASSTYPES[topElement["type"]], topElement["name"], value))
			if length != 1:
				out.write("\t" * (recursionLevel - 1) + "</array>\n")

		out.write("\t</class>\n</xfs>")
		print("Written to %s.xml" % self.file.name)

class XMLToXFS(XFSCommon):
	import xml.etree.ElementTree as ET
	from struct import pack

	formatHandlers = {}

	def __init__(self, filename, output, outputAc=False, fixChartForiOS=False):
		self.logFile = None
		self.xml = self.ET.parse(filename).getroot()
		self.output = open(output, "wb")
		self.fixIosStruct = fixChartForiOS
		self.version, self.xfsType, self.int1, self.origin = (int(self.xml[0][0].text),
																int(self.xml[0][1].text),
																int(self.xml[0][2].text),
																self.xml[0][3].text)
		self.originIos = True if self.origin == "ios" else False
		self.ios = outputAc #odd name but for writeHeader kinda...
		self.classtypesFromName = {v:k for k,v in self.CLASSTYPES.items()}
		self.defineHandler(1, None)
		self.defineHandler(2, None)
		self.defineHandler(3, self.boolHandler)
		self.defineHandler(6, self.u32Handler)
		self.defineHandler(12, self.f32Handler)
		self.defineHandler(10, self.s32Handler)
		self.defineHandler(16, self.pointHandler)
		self.defineHandler(32, self.cstringHandler)
		self.defineHandler(128, self.resourceHandler)

	def defineHandler(self, type, handler):
		self.formatHandlers[type] = handler

	def readHeader(self, log=False):
		self.structCount = len(self.xml[1].getchildren())
		if self.fixIosStruct and len(self.xml.findall("./class/class/array/classref[@type='8867325']")) > 0:
			self.structCount -= 1
		self.dPrint(log, "Struct Count: ", self.structCount)
		self.names = []
		self.structList = []
		self.structDict = {}
		self.hashToNumber = {}
		counter = 0
		for struct in self.xml[1]:
			if self.fixIosStruct and struct[0].text == "8867325":
				continue
			self.dPrint(log,"==> Struct ", ":")
			structhash = int(struct[0].text)
			self.dPrint(log,"==> Hash: ", structhash)
			subcount = int(struct[1].text)
			self.dPrint(log,"==> Subclass count: ", subcount)
			subclasses = []
			for x in range(subcount):
				self.dPrint(log,"====> Subclass ", x, ":")
				name = struct[2 + x].attrib['name']
				self.dPrint(log,"====> Name: ", name)
				subtype = int(struct[2 + x][0].text)
				self.dPrint(log,"====> Type: ", subtype)
				unknown = int(struct[2 + x][2].text)
				self.dPrint(log,"====> Unknown: ", unknown)
				size = int(struct[2 + x][1].text)
				self.dPrint(log,"====> Size: ", size)
				self.names.append(name)
				subclasses.append({"name": name,
									"type": subtype,
									"size": size,
									"unk": unknown})
			self.structList.append({"structhash": structhash,
									"subcount": subcount,
									"subclasses": subclasses})
			self.structDict[structhash] = {"subcount": subcount,
									"subclasses": subclasses}
			self.hashToNumber[structhash] = counter
			counter += 1

	def boolHandler(self, data):
		temp = True if data.attrib['value'] == "true" else False
		return self.pack("<b", int(temp))

	def f32Handler(self, data):
		return self.pack("<f", float(data.attrib['value']))

	def s32Handler(self, data):
		return self.pack("<i", int(data.attrib['value']))

	def u32Handler(self, data):
		return self.pack("<I", int(data.attrib['value']))

	def pointHandler(self, data):
		return self.pack("<ii", int(data.attrib['x']), int(data.attrib['y']))

	def cstringHandler(self, data):
		return data.attrib['value'].encode() + b"\x00"

	def resourceHandler(self, data):
		#different than others since we know there must be a resource here
		buf = b"\x02"
		buf += data.attrib['type'].encode() + b"\x00"
		buf += data.attrib['value'].encode() + b"\x00"
		return buf

	def parseSingle(self, data, eType, log=False):
		if eType in [1,2]:
			if self.fixIosStruct and data.attrib['type'] == "8867325":
				return b""
			return self.classHandler(data, log)
		else:
			return self.formatHandlers[eType](data)

	def internalClassHandler(self, data, log=False):
		buf = b""
		for element in data:
			if element.tag == "array":
				length = int(element.attrib['count'])
				eType = self.classtypesFromName[element.attrib['type']]
			else:
				length = 1
				eType = self.classtypesFromName[element.tag]
			if "name" in element.attrib and element.attrib["name"] == "mNoteSum":
				length = 8 if self.ios else 4 #ok because will be at end
			if self.fixIosStruct and element.attrib['name'] == "mpArray":
				printLen = length
				printLen -= len(self.xml.findall("./class/class/array/classref[@type='8867325']"))
				buf += self.formatIntDword(printLen)
			else:
				buf += self.formatIntDword(length)
			if length > 1:
				for x in range(length):
					buf += self.parseSingle(element[x], eType, log)
			elif length == 0:
				pass
			else:
				buf += self.parseSingle(element, eType, log)
				if eType == 128:
					buf += b"\x00" * 0x04
		return buf

	def classHandler(self, data, log=False):
		classNo = self.hashToNumber[int(data.attrib['type'])]
		classNo = (classNo << 1) + 1
		base = self.formatIntWord(classNo)
		base += self.formatIntWord(self.trueCounter)
		self.trueCounter += 1
		buf = self.internalClassHandler(data, log)
		return base + self.formatGeneralInt(len(buf) + len(self.formatGeneralInt(0))) + buf

	def parseData(self, log=False):
		self.output.write(self.formatIntDword(1))
		self.trueCounter = 1
		buf = self.internalClassHandler(self.xml[2])
		self.output.write(self.formatGeneralInt(len(buf) + len(self.formatGeneralInt(0))) + buf)
		self.output.close()
		print("Written to %s" % self.output.name)

class ConvertACIOS(XFSCommon):
	from struct import unpack, pack

	def __init__(self, filename, output, ios=False, oldIos=False): #ios means "is input ios"
		XFSCommon.__init__(self, filename, ios, oldIos)
		self.output = open(output, "wb")

	def resourceHandler(self,  length):
		test = self.readSingleByteInt()
		if test is 2 or length is not 1:
			buf = self.formatIntDword(length) + b"\x02"
			self.file.seek(-0x01, 1)
			for x in range(length):
				resType = self.readSingleByteInt()
				if resType is not 2:
					raise ValueError("Bad resource (list)!")
				buf += self.readNullTerminatedString().encode() + b"\x00"
				buf += self.readNullTerminatedString().encode() + b"\x00"
			if length is 1:
				self.file.seek(0x04, 1)
				buf += b"\x00" * 4
			return buf
		else:
			#nothing here!
			self.file.seek(-0x01 + -0x04, 1)
			return b""

	def classHandler(self, log=False):
		buf = b""
		temp, classNo = self.getAndReadIntWord()
		base = temp
		classNo = classNo >> 1
		base += self.getAndReadIntWord()[0]
		self.readGeneralInt() #skip the offset
		for element in self.structList[classNo]['subclasses']:
			temp, length = self.getAndReadIntDword()
			if element["type"] == 128:
				buf += self.resourceHandler(length)
			else:
				buf += temp
			for x in range(length):
				if element["type"] in [1,2]:
					buf += self.classHandler()
				elif element["type"] == 32:
					buf += readNullTerminatedString().encode() + b"\x00"
				elif element["type"] == 128:
					pass
				else:
					#print(element)
					buf += self.file.read(element["size"])
		return base + self.formatGeneralInt(len(buf) + len(self.formatGeneralInt(0))) + buf

	def parseData(self, log=False):
		self.file.seek(self.startOffset) #assuming top level is not array...
		self.output.write(self.getAndReadIntDword()[0])
		#need to buffer output recursively so can get total length hh
		self.readGeneralInt()
		buf = b""
		for topElement in self.structList[0]["subclasses"]:
			temp, length = self.getAndReadIntDword()
			#specific case
			if topElement["name"] == "mNoteSum":
				length = 8 if self.ios else 4 #ok because will be at end
				temp = b"\x04" + ("\x00" * 7 if self.ios else "\x00" * 3)
			if topElement["type"] == 128:
				k = self.resourceHandler(length)
				#print(k)
				buf += k
			else:
				buf += temp
			for x in range(length):
				if topElement["type"] in [1,2]:
					buf += self.classHandler(log)
				elif topElement["type"] == 32:
					buf += readNullTerminatedString().encode() + b"\x00"
				elif topElement["type"] == 128:
					pass
				else:
					buf += self.file.read(topElement["size"])
		self.output.write(self.formatGeneralInt(len(buf) + len(self.formatGeneralInt(0))) + buf)
		self.output.close()
		print("Written to %s" % self.output.name)