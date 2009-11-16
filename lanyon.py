#!/usr/bin/env python

import os, sys, codecs

from optparse import OptionParser
from jinja2 import Environment, FileSystemLoader

# parse content into tree of nodes
# extract data from {% lanyon %} tags
# run site preprocessors
# for each content file
    # render template to output file
    # run registered content processors on output file
# run site postprocessors

class SiteNode( object ):
    name = ""
    path = ""
    
    def __init__( self, path ):
        self.path = path
        self.name = os.path.split( path )[ 1 ]
        pass

    def visit( self, visitor ):
        pass

class DirectoryNode( SiteNode ):
    children = {}

    def __init__( self, path ):
        SiteNode.__init__( self, path )
        
    def addChild( self, child ):
        self.children[ self.name ] = child
        return child

    def visit( self, visitor ):
        for name, child in self.children.items():
            child.visit( visitor )

class RootNode( DirectoryNode ):

    def __init__( self, path ):
        DirectoryNode.__init__( self, path )
    
class ContentNode( SiteNode ):
    data = {}
    
    def __init__( self, path ):
        SiteNode.__init__( self, path )

    def visit( self, visitor ):
        visitor.visit( self )

def build_content_tree( content_path ):
    root = RootNode( content_path )
    
    for path, dirs, files in os.walk( content_path ):
        for filename in files:
            file_path = os.path.join( path, filename )
            print file_path
            if os.path.isdir( file_path ):
                root.addChild( DirectoryNode( file_path ) )
            else:
                root.addChild( ContentNode( file_path ) )
    
    return root        

def main(argv):
    layout_dir = os.path.join( os.getcwdu(), 'layout' )
    content_dir = os.path.join( os.getcwdu(), 'content' )
    output_dir = os.path.join( os.getcwdu(), 'output' )
    
    content_tree = build_content_tree( content_dir )
    
    # Attempt to create output directory if it doesn't exist
    if not os.path.exists( output_dir ):
        os.makedirs( output_dir )
    
    # Set up jinja2 environment to load templates from content and layout directories
    env = Environment(
        loader = FileSystemLoader( [ content_dir, layout_dir ] ),
    )
    
    content_tree.visit( GeneratorNodeVisitor( content_dir, output_dir, env ) );
    
    # # Loop through all files in the content dir
    # for filename in os.listdir( content_dir ):
    #     # Use jinja2 environment to create Template instance for file
    #     template = env.get_template( filename )
    #     
    #     # Render template and write to the same name file in the output directory
    #     with codecs.open( os.path.join( output_dir, filename ), 'w', 'utf-8' ) as f:
    #         f.write( template.render() )
    #         f.close()

class GeneratorNodeVisitor(object):
    def __init__( self, content_dir, output_dir, env ):
        self.content_dir = content_dir
        self.output_dir = output_dir
        self.env = env
        pass
        
    def visit( self, node ):
        filename = node.path[len(self.content_dir)+1:];
        
        output_path = os.path.join( self.output_dir, filename )
                
        # Use jinja2 environment to create Template instance for file
        template = self.env.get_template( filename )

        # Create output path if it doesn't exist
        parent_path = os.path.split( output_path )[ 0 ]        
        if not os.path.exists( parent_path ):
            os.makedirs( parent_path );
        
        # Render template and write to the same name file in the output directory
        with codecs.open( output_path, 'w', 'utf-8' ) as f:
            f.write( template.render() )
            f.close()
        pass
        
if __name__ == "__main__":
    main(sys.argv[1:])