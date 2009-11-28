#!/usr/bin/env python

import os, sys
from optparse import OptionParser
from lanyon import Site

def main(argv):
    config = {
        # Paths
        'layout_path': os.path.join( os.getcwdu(), 'layout' ),
        'content_path': os.path.join( os.getcwdu(), 'content' ),
        'output_path': os.path.join( os.getcwdu(), 'output' ),
        
        # File extensions to examine for YAML front matter
        'yaml_extensions': ( 'html', 'markdown', 'mdown', 'md', 'js', 'css' ),
        
        # Content processors
        'content_processors': {
            ('html'): [
                'lanyon.content_processors.Jinja2Renderer'
            ],
            ('markdown','mdown','md'): [
                'lanyon.content_processors.MarkdownRenderer'
            ],
            ('js','css'): [
                'lanyon.content_processors.IdentityRenderer'
            ]
        },
        
        # Site post-processors
        'post_processors': [
            'lanyon.post_processors.MarkdownFileRenamer'
        ]
    }
    
    site = Site( config = config )    
    site.generate()
    
if __name__ == "__main__":
    main(sys.argv[1:])