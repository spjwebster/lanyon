#!/usr/bin/env python

import os, sys
from optparse import OptionParser
from lanyon import Site

def main(argv):
    config = {
        'layout_path': os.path.join( os.getcwdu(), 'layout' ),
        'content_path': os.path.join( os.getcwdu(), 'content' ),
        'output_path': os.path.join( os.getcwdu(), 'output' ),
        'content_processors': {
            ('html'): [
                'lanyon.content_processors.YAMLFrontMatterExtractor',
                'lanyon.content_processors.Jinja2Renderer'
            ],
            ('markdown','mdown'): [
                'lanyon.content_processors.YAMLFrontMatterExtractor',
                'lanyon.content_processors.MarkdownRenderer'
            ],
            ('js','css'): [
                'lanyon.content_processors.IdentityRenderer'
            ]
        },
        'post_processors': [
            'lanyon.post_processors.MarkdownFileRenamer'
        ]
    }
    
    site = Site( config = config )    
    site.generate()
    
if __name__ == "__main__":
    main(sys.argv[1:])