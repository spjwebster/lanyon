#!/usr/bin/env python

import os, sys
from optparse import OptionParser
from lanyon import Site

def main(argv):
    config = {
        'layout_path': os.path.join( os.getcwdu(), 'layout' ),
        'content_path': os.path.join( os.getcwdu(), 'content' ),
        'output_path': os.path.join( os.getcwdu(), 'output' )
    }
    
    site = Site( config = config )    
    site.generate()
        
if __name__ == "__main__":
    main(sys.argv[1:])