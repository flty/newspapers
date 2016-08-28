from distutils.core import setup
import py2exe

setup( console=['get_rmrb_pdf1.py'],
	   zipfile=None,
	   options={'py2exe' : {"bundle_files":1}
	   }

	   )