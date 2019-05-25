class Tools(object):
	import struct

	@staticmethod
	def byteToSmallInt(byte1, byte2):
		return int(('00'+hex(byte2)[2:])[-2:]+('00'+hex(byte1)[2:])[-2:], 16)
	@staticmethod
	def byteToSmallLong(byte1, byte2, byte3, byte4):
		return int(('00'+hex(byte4)[2:])[-2:]+('00'+hex(byte3)[2:])[-2:]+('00'+hex(byte2)[2:])[-2:]+('00'+hex(byte1)[2:])[-2:], 16)
	@classmethod
	def binaryToByteList(cls, binary):
		return cls.struct.unpack('B' * len(binary), binary)
	@staticmethod
	def byteListToBinary(byteList):
		return bytearray(byteList)
	@classmethod
	def smallIntToByteList(cls,integer):
		return cls.struct.unpack('BB', cls.struct.pack('h', integer))
	@classmethod
	def smallLongToCharByteList(cls,longInt):
		return cls.struct.unpack('BBBB', cls.struct.pack('L', longInt))
	@staticmethod
	def filenameToUnix(input):
		return input.replace("\\", "/")
	@staticmethod
	def filenameToWindows(input):
		return input.replace("/", "\\")

class ARCDecrypter(object):
	import shutil
	import zlib
	import os
	import Tools
	import base64
	from Cryptodome.Cipher import Blowfish

	def __init__(self, fileName, keyFolderPath = None, allowInvalid = False):
		self.allowInvalid = allowInvalid;
		self.readStructure(fileName, keyFolderPath)
		self.findKey()
		self.readHeader()

	def readStructure(self, fileName, keyFolderPath):
		self.fileName = self.os.path.realpath(fileName)
		if not self.fileName:
			raise ValueError('ARCDecrypter: File does not exist')
		self.filePath = self.os.path.join(self.os.path.dirname(self.fileName),self.os.path.basename(self.fileName).split(".")[0])
		self.keyFolderPath = self.os.path.realpath(keyFolderPath) if (keyFolderPath is not None) else None
		handle = open(self.fileName, 'rb') 
		filesize = self.os.path.getsize(self.fileName)
		byteList = handle.read(filesize)
		handle.close()
		self.fileByteList = byteList
		self.isArcc = (byteList[0x3] is 67)
		self.arcVersion = Tools.byteToSmallInt(byteList[0x4], byteList[0x5])
		self.fileCount = Tools.byteToSmallInt(byteList[0x6], byteList[0x7])

	def findKey(self):
		if self.keyFolderPath:
			name = self.os.path.basename(self.fileName).split(".")[0].split("_")[0]
			if self.os.path.exists(self.os.path.join(self.keyFolderPath, name + '.arc.key')):
				handle = open(self.os.path.join(self.keyFolderPath, name + '.arc.key'), 'r')
				self.key = handle.read()
				handle.close()
			else:
				raise ValueError('ARCDecrypter: Key file does not exist')
		else:
			self.key = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'

	def readHeader(self):
		self.fileList = []
		for i in range(self.fileCount):
			headerByteList = []
			for j in range(0x50):
				headerByteList.append(self.fileByteList[0x8 + i * 0x50 + j])
			data = self.bf_decode(headerByteList) if self.isArcc else headerByteList
			nameByteList = []
			for j in range(0x50):
				if data[j] > 0:
					nameByteList.append(data[j])
				else:
					break
			sizeAndUnk = Tools.byteToSmallLong(data[72], data[73], data[74], data[75])
			self.fileList.append({
				'name': Tools.filenameToUnix(Tools.byteListToBinary(nameByteList).decode('utf-8')),
				'type': Tools.byteToSmallLong(data[64], data[65], data[66], data[67]),
				'size': Tools.byteToSmallLong(data[68], data[69], data[70], data[71]),
				'originalSize': sizeAndUnk % 134217728, #2^27 - gives last 28 bits
				'unknown': int((sizeAndUnk - sizeAndUnk % 134217728) / 134217728), #2^27 - gives first 4 bits - no intdiv to prevent floating point problems sosad
				'offset': Tools.byteToSmallLong(data[76], data[77], data[78], data[79])
			})
		self.createUnkFile()

	def bf_decode(self, byteList):
		decrypted = []
		for i in range(len(byteList) // 8):
			bList = [byteList[i * 8 + 3], byteList[i * 8 + 2], byteList[i * 8 + 1], byteList[i * 8 + 0], byteList[i * 8 + 7], byteList[i * 8 + 6], byteList[i * 8 + 5], byteList[i * 8 + 4]]
			string = Tools.byteListToBinary(bList)
			bfDecrypter = self.Blowfish.new(self.key.encode('utf-8'), self.Blowfish.MODE_ECB)
			decryptedByteList = Tools.binaryToByteList(bfDecrypter.decrypt(string))
			decrypted.extend([decryptedByteList[3], decryptedByteList[2], decryptedByteList[1], decryptedByteList[0], decryptedByteList[7], decryptedByteList[6], decryptedByteList[5], decryptedByteList[4]])
		return decrypted

	def fileDetail(self):
		return {
			'fileName': self.fileName,
			'key': self.key,
			'keyFolderPath': self.keyFolderPath,
			'isArcc': self.isArcc,
			'fileCount': self.fileCount,
			'arcVersion': self.arcVersion
		}

	def createUnkFile(self):
		write = []
		folderPath = self.os.path.join(self.filePath)
		h = open(folderPath+".unknowns.txt","w")
		for file in self.fileList:
			if file['name'] in write:
				file['name'] += '_'
			write.append(file['name'])
			h.write(Tools.filenameToWindows(file['name'])+" "+str(file['type'])+" "+str(file['unknown'])+"\n")
		h.close()

	def unpack(self):
		string = ''
		folderPath = self.os.path.join(self.filePath,"")
		if self.os.path.exists(folderPath):
			self.shutil.rmtree(folderPath)
		orderList = []
		for file in self.fileList:
			orderList.append(file['name'])
			savePath = self.os.path.join(self.filePath,file['name'])
			basePath = self.os.path.join(self.filePath,'/'.join(file['name'].split("/")[:-1]))
			if not self.os.path.exists(basePath):
				self.os.makedirs(basePath)
			fileByteList = []
			for j in range(file['size']):
				fileByteList.append(self.fileByteList[file['offset'] + j])
			if self.isArcc:
				fileByteList = self.bf_decode(fileByteList)
			if self.os.path.exists(savePath):
				savePath += '_'
				orderList[len(orderList) - 1] += '_'
			string += 'Unpacked: '+savePath+"\n"
			h = open(savePath, "wb")
			try:
				h.write(self.zlib.decompress(Tools.byteListToBinary(fileByteList)))
			except Exception as e:
				if self.allowInvalid:
					print("Failed: " + savePath)
					print("Binary: " + self.base64.b64encode(Tools.byteListToBinary(fileByteList)).decode())
				else:
					raise e
			h.close()
		o = open(self.filePath+'.order.txt', "w")
		o.write("\n".join(orderList))
		o.close()
		return string

class ARCEncrypter(object):
	import shutil
	import zlib
	import os
	import Tools
	import glob
	from Cryptodome.Cipher import Blowfish

	def __init__(self, fileName, keyFolderPath = None, encrypt = True, baseOffset = 0x8000):
		self.isArcc = encrypt
		self.arcVersion = 7
		self.fileList = []
		self.unknownLookup = False
		self.realFileList = []
		self.comp = {}
		self.unknownLookup = {}
		self.baseOffset = baseOffset
		self.readStructure(fileName, keyFolderPath)
		self.findKey()
		self.readHeader()

	def readStructure(self, folderName, keyFolderPath):
		folderName = self.os.path.realpath(folderName)
		if not folderName:
			raise ValueError('ARCEncrypter: Folder does not exist')
		self.keyFolderPath = self.os.path.realpath(keyFolderPath) if (keyFolderPath is not None) else None
		self.fileName = folderName+'.arc'
		fileList = self.glob.glob(folderName + "/**", recursive=True)
		for file in fileList:
			if self.os.path.isfile(file):
				self.realFileList.append(file)
		if self.os.path.exists(folderName+'.order.txt'):
			h = open(folderName+'.order.txt',"r")
			orderList = h.readlines()
			h.close()
			orderedRealFileList = []
			for orderListEntry in orderList:
				for realFileListEntry in self.realFileList:
					if orderListEntry.strip() in Tools.filenameToUnix(realFileListEntry):
						orderedRealFileList.append(realFileListEntry)
						break
			self.realFileList = orderedRealFileList
		if self.os.path.exists(folderName+'.unknowns.txt'):
			h = open(folderName+'.unknowns.txt',"r")
			f = h.read()
			for line in f.split("\n"):
				if line is not "":
					c = line.split(" ")
					self.unknownLookup[c[0]] = [int(c[1]), int(c[2])]
		self.fileCount = len(self.realFileList)

	def findKey(self):
		if self.keyFolderPath:
			name = self.os.path.basename(self.fileName).split("_")[0]
			if self.os.path.exists(self.os.path.join(self.keyFolderPath, name + '.arc.key')):
				handle = open(self.os.path.join(self.keyFolderPath, name + '.arc.key'), 'r')
				self.key = handle.read()
				handle.close()
			else:
				raise ValueError('ARCEncrypter: Key file does not exist')
		else:
			self.key = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'

	def readHeader(self):
		basePath = self.os.path.join(self.os.path.dirname(self.os.path.join(self.fileName[:-4],'a')),"")
		totalSize = 0
		for realFile in self.realFileList:
			fileName = Tools.filenameToWindows(realFile.replace(basePath, ''))
			fileSize = self.os.path.getsize(realFile)
			h = open(realFile, "rb")
			self.comp[fileName] = self.zlib.compress(h.read())
			h.close()
			encryptedSize = len(self.comp[fileName])
			encryptedSize = encryptedSize + (8 - (encryptedSize % 8) if encryptedSize % 8 > 0 else 0)
			self.fileList.append({
				'name': fileName,
				'type': self.unknownLookup[fileName][0] if self.unknownLookup else 0x0,
				'size': encryptedSize,
				'originalSize': fileSize,
				'unknown': self.unknownLookup[fileName][1] if self.unknownLookup else 0x8,
				'offset': self.baseOffset + totalSize
			})
			totalSize += encryptedSize

	def bf_encode(self, byteList):
		encrypted = []
		for i in range(len(byteList) // 8):
			bList = [byteList[i * 8 + 3], byteList[i * 8 + 2], byteList[i * 8 + 1], byteList[i * 8 + 0], byteList[i * 8 + 7], byteList[i * 8 + 6], byteList[i * 8 + 5], byteList[i * 8 + 4]]
			string = Tools.byteListToBinary(bList)
			bfEncrypter = self.Blowfish.new(self.key.encode('utf-8'), self.Blowfish.MODE_ECB)
			encryptedByteList = Tools.binaryToByteList(bfEncrypter.encrypt(string))
			encrypted.extend([encryptedByteList[3], encryptedByteList[2], encryptedByteList[1], encryptedByteList[0], encryptedByteList[7], encryptedByteList[6], encryptedByteList[5], encryptedByteList[4]])
		return encrypted

	def fileDetail(self):
		return {
			'fileName': self.fileName,
			'key': self.key,
			'keyFolderPath': self.keyFolderPath,
			'isArcc': self.isArcc,
			'fileCount': self.fileCount,
			'arcVersion': self.arcVersion
		}

	def pack(self):
		string = ''
		writeCount = 0
		handle = open(self.fileName, 'wb')
		handle.write(b'ARCC' if self.isArcc else b'ARC\x00')
		handle.write(Tools.byteListToBinary(Tools.smallIntToByteList(self.arcVersion)))
		handle.write(Tools.byteListToBinary(Tools.smallIntToByteList(self.fileCount)))
		for file in self.fileList:
			#print(file, handle.tell())
			fileName = file['name']
			byteList = []
			if fileName[-1:] is "_":
				fileName = fileName[:-1]
			typeByteList = Tools.smallLongToCharByteList(file['type'])
			sizeByteList = Tools.smallLongToCharByteList(file['size'])
			originalSizeByteList = Tools.smallLongToCharByteList(file['originalSize'] + (file['unknown'] * 134217728))
			offsetByteList = Tools.smallLongToCharByteList(file['offset'])
			nameByteList = Tools.binaryToByteList(fileName.encode('utf-8'))
			for j in range(0x50):
				if j < len(nameByteList):
					byteList.append(nameByteList[j]) 
				elif j >= 64 and j <= 67:
					byteList.append(typeByteList[j - 64])
				elif j >= 68 and j <= 71:
					byteList.append(sizeByteList[j - 68])
				elif j >= 72 and j <= 75:
					byteList.append(originalSizeByteList[j - 72])
				elif j >= 76 and j <= 79:
					byteList.append(offsetByteList[j - 76])  
				else:
					byteList.append(0)
			if self.isArcc:
				handle.write(Tools.byteListToBinary(self.bf_encode(byteList)))
			else:
				handle.write(Tools.byteListToBinary(byteList))
		for file in self.fileList:
			writeCount = writeCount + 1
			handle.seek(file['offset'])
			fileName = file['name']
			string += 'Packed: '+fileName+"\n"
			byteList = list(Tools.binaryToByteList(self.comp[file['name']]))
			if len(byteList) % 8 is not 0:
				for j in range(8 - (len(byteList) % 8)):
					byteList.append(0)
			if self.isArcc:
				handle.write(Tools.byteListToBinary(self.bf_encode(byteList)))
			else:
				handle.write(Tools.byteListToBinary(byteList))
		handle.close()
		return string