#!/usr/bin/env python

import os, sys
from optparse import OptionParser
import cherrypy
from lanyon import Site

#TODO: Load this config from the current working directory
_config = {
    # Paths
    'layout_path': os.path.join( os.getcwdu(), 'layout' ),
    'content_path': os.path.join( os.getcwdu(), 'content' ),
    'output_path': os.path.join( os.getcwdu(), 'output' ),
    
    # File extensions to examine for YAML front matter
    'yaml_extensions': ( 'html', 'markdown', 'mdown', 'md', 'js', 'css' ),
    
    # Site pre-processors
    'pre_processors': [
        'lanyon.pre_processors.MarkdownOutputRenamer',
        {
            'class': 'lanyon.pre_processors.BlogPostProcessor',
            'options':  {
                'path': '20[0-9][0-9]/**.{markdown,html}'
            },
        },
    ],

    # Content processors
    'content_processors': {
        ('html','rss','atom'): [
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
        {
            'class': 'lanyon.post_processors.TagPageGenerator',
            'options': {
                'template': '_tag.html'
            },
        },
        {
            'class': 'lanyon.post_processors.TagFeedGenerator',
            'options': {
                'template': '_tag.atom'
            },
        },
    ],
}
    
def main( argv ):
    parser = OptionParser( 'usage: %prog [options]' )
    parser.add_option( '-g', '--generate', dest="generate", action="store_true",
        help="Generate the site from the current working directory" )
    parser.add_option( '-s', '--server', dest="server", action="store_true",
        help="Start a server on port 8080 using the output directory as the site root" )
    
    (options, args) = parser.parse_args( argv )

    if options.generate:
        _generate()
    
    elif options.server:
        _start_server()
    
    else:
        parser.error( 'Generate or server?' )

def _start_server( port = 8080 ):
    print "# Starting server on port %s: " % str( port )
    
    class WebRoot:
        pass
        
    cherrypy.config.update( {
        'environment': 'production',
        'log.error_file': 'site.log',
        'log.screen': True
    } )
    
    cherrypy.quickstart( WebRoot(), '/', config = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': _config[ 'output_path' ],
            'tools.staticdir.index': 'index.html'
        }
    } )

def _generate():
    site = Site( config = _config )    
    print "# Generating site: "
    site.generate()

if __name__ == "__main__":
    main(sys.argv[1:])