#!/usr/bin/env python

import codecs, os, sys, yaml

from optparse import OptionParser
from jinja2 import Environment, FileSystemLoader

# parse content into tree of nodes
# extract data from {% lanyon %} tags
# run site preprocessors
# for each content file
    # if type == 'markdown'
        # fetch template name and other data from YAML front matter a la jekyll
        # generate markdown output and store in 'content' context data
        # copy all other front matter values to context data
        # render template to output file using context data
    # if type == 'html'
        # copy all front matter values to context data
        # let jinja2 {% extends %} handle the template selection
    # render template to output file
    # run registered content processors on output file
# run site postprocessors

class Site( object ):
    config = None
    content_root = None
    
    def __init__( self, config ):
        self.config = config
    
    def build_content_tree( self, content_path ):
        root = RootNode( content_path )
    
        # TODO: Possibly move this lookup-node-by-path functionality into the DirectoryNode class
        directory_nodes = { content_path: root }
    
        for path, directories, files in os.walk( content_path ):

            # Get node for parent path
            parent_node = directory_nodes[ path ]

            # Add all directories as DirectoryNode instances
            for directory in directories:
                full_path = os.path.join( path, directory )
                directory_node = parent_node.addChild( DirectoryNode( full_path ) )
                directory_nodes[ full_path ] = directory_node
        
            # Add all files as ContentNode instances
            for filename in files:
                full_path = os.path.join( path, filename )
                parent_node.addChild( ContentNode( full_path ) )
        
        return root             
    
    def generate( self ):
        if self.content_root == None:
            self.content_root = self.build_content_tree( self.config['content_path'] )
    
        # Attempt to create output directory if it doesn't exist
        if not os.path.exists( self.config['output_path'] ):
            os.makedirs( self.config['output_path'] )
    
        # Generate output from content tree
        self.content_root.visit( OutputGeneratorVisitor( self.config ) );
        

class SiteNode( object ):
    name = None
    path = None
    
    def __init__( self, path ):
        self.path = path
        self.name = os.path.basename( path )
        pass

    def visit( self, visitor ):
        method = 'visit' + self.__class__.__name__;
        if not hasattr( visitor, method ) or not callable( getattr( visitor, method ) ):
            method = 'visit'
        getattr( visitor, method )( self )


class DirectoryNode( SiteNode ):

    def __init__( self, path ):
        super( DirectoryNode, self ).__init__( path )
        self.children = {}
        
    def addChild( self, child ):
        self.children[ child.name ] = child
        return child

    def visit( self, visitor ):
        super( DirectoryNode, self ).visit( visitor )
        for name, child in self.children.items():
            child.visit( visitor )
        

class RootNode( DirectoryNode ):

    def __init__( self, path ):
        super( RootNode, self ).__init__( path )
    

class ContentNode( SiteNode ):
    data = None
    
    def __init__( self, path ):
        super( ContentNode, self ).__init__( path )
        self.extension = os.path.splitext( path )[ 1 ]
        self.data = {}


class OutputGeneratorVisitor(object):
    
    def __init__( self, config ):
        self.config = config;
        self.content_processors = [
            Jinja2Renderer( config )
        ]
    
    def visit( self, node ):
        pass
    
    def visitDirectoryNode( self, node ):
        relative_path = os.path.relpath( node.path, self.config['content_path'] )
        output_path = os.path.join( self.config['output_path'], relative_path )

        if not os.path.exists( output_path ):
            print "#   Creating: " + relative_path
            os.makedirs( output_path );
    
    def visitContentNode( self, node ):
        # todo: find processors based on node.path and node.extension

        # Truncate path to just the relative path from within the content directory, the append to
        # the output path to get the full path to the output file
        relative_path = os.path.relpath( node.path, self.config['content_path'] )
        output_path = os.path.join( self.config['output_path'], relative_path )

        print "# Processing: " + relative_path

        # Read content from content file
        content_file = codecs.open( node.path, 'r', 'utf-8' )
        content = content_file.read()
        content_file.close()
        
        # Apply processors to content
        for processor in self.content_processors:
            content = processor.process( node, content )

        # Write processed content to same named file in the output directory
        with codecs.open( output_path, 'w', 'utf-8' ) as f:
            f.write( content )
            f.close()


class ContentProcessor(object):
    def __init__( self, config ):
        self.config = config
    
    def process( self, node, content ):
        pass


class Jinja2Renderer( ContentProcessor ):
    def __init__( self, config ):
        super( Jinja2Renderer, self ).__init__( config )
        
        # Set up jinja2 environment to load templates from layout directory
        self.env = Environment(
            loader = FileSystemLoader( [ self.config['layout_path'] ] ),
        )
        
    def process( self, node, content ):
        template = self.env.from_string( content )
        return template.render( node.data )


class IdentityRenderer( ContentProcessor ):
    def process( self, node, content ):
        return content


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