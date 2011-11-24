#!/usr/bin/env python

import os, sys, codecs, json, cherrypy
from optparse import OptionParser
from lanyon import Site

    
def main( argv ):
    command = argv[0]

    if command == "generate":
        _generate( argv[1:] )
    
    elif command == "serve":
        _start_server( argv[1:] )
    
    else:
        print 'Usage: lanyon (generate|serve) [options]';

def _start_server( args ):
    parser = OptionParser( 'usage: %prog serve [options]' )
    parser.add_option( 
        '-p', '--port', 
        dest="port",
        default="8080",
        help="The port to listen on"
    )

    (options, args) = parser.parse_args( args )


    print "# Starting server on port %s: " % str( options.port )
    
    class WebRoot:
        pass
        
    cherrypy.config.update( {
        'environment': 'production',
        'log.error_file': 'site.log',
        'log.screen': True,
        'server.socket_port': int(options.port)
    } )
    
    cherrypy.quickstart( WebRoot(), '/', config = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': _config[ 'output_path' ],
            'tools.staticdir.index': 'index.html'
        }
    } )

def _generate( args ):
    parser = OptionParser( 'usage: %prog generate [options]' )
    parser.add_option( 
        '-c', '--config', 
        dest="config_path",
        default="site-config.json",
        help="The path to the configuration file to use for site genration"
    )
    (options, args) = parser.parse_args( args )

    # TODO: Add safety net
    print "# Reading config '" + options.config_path + "':"
    config_path = os.path.join( os.getcwdu(), options.config_path )
    config_file = codecs.open( config_path, 'r', 'utf-8' )
    config = json.load( config_file )
    config_file.close()
    config_file = None

    site = Site( config = config )
    print "# Generating site: "
    site.generate()

if __name__ == "__main__":
    main(sys.argv[1:])