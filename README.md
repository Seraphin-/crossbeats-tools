Crossbeats Tools
================

These are tools for working with crossbeats iOS and arcade game data.
They may not work with Python 2.

arctool
-------
**Before using with arcade, you must replace the default key on lines 68 and 222 with the proper value**

**Requirements**

pycryptodomex (install with `pip install pycryptodomex`)

**Usage**

Unpack an archive

	import arctool
	obj = arctool.ARCDecrypter('archive.arc')
	obj.unpack()
This will also generate a .unknowns.txt and .order.txt file for repacking.

(Re)pack a folder

	import arctool
	obj = arctool.ARCEncrypter('archive')
	obj.pack()

For a folder to be repacked accurately, a .unknowns.txt and .order.txt file must be present.

Constructor parameters

	keyFolderPath
		Optional path to a folder containing text files with the .key extension with respective archive keys. If not present, uses default key.
	encrypt
		*ARCEncrypter* Determines whether to actually encrypt the archive. Defaults to true.
	baseOffset
		*ARCEncrypter* Determines base file pack offset. Defaults to 0x8000.
	allowInvalid
		*ARCDecrypter* Allows files that can't be decrypted properly.

The fileDetail method can be used to get information about the archive.

The .unknowns.txt contains type information for the file, which is the first number after the filename.

xfstool
-------
**Usage**

Convert an XFS file to XML

	import xfstool
	obj = xfstool.XFSToXML('input')
	obj.readHeader()
	obj.parseData()  # Will be output to "input.xml"

Convert an XML file outputted by the tool back to XFS

	import xfstool
	obj = xfstool.XMLToXFS('input.xml')
	obj.readHeader()
	obj.parseData()  # Will be output to "input"

Convert an AC format XFS to iOS'

	import xfstool
	obj = xfstool.ConvertACIOS('input_ac', 'output_ios')
	obj.readHeader()
	obj.parseData()

Convert an iOS format XFS to AC's

	import xfstool
	obj = xfstool.ConvertACIOS('input_ios', 'output_ac', ios=True)
	obj.readHeader()
	obj.parseData()	

Constructor parameters

	XFSToXML and ConvertACIOS
		ios
			Should be set to true when the input is in iOS format and false if AC format.
		oldIos
			For iOS XFS files from early versions of the game.
	XMLToXFS
		outputAc
			Set this to true for the output to be in AC format.
		fixChartForiOS
			Set this to true to fix song charts from AC format to iOS format.

Many functions also accept a log parameter for debugging.

Credits
-------
einsys - ARC reversing
