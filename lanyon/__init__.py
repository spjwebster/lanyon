import codecs, os, sys, shutil
import processors

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
        
        # toto: run site preprocessors
        
        # Generate output from content tree
        self.content_root.visit( OutputGeneratorVisitor( self.config ) );

        # toto: run site postprocessors
        

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
        self.extension = os.path.splitext( path )[ 1 ][1:]
        self.data = {}


class OutputGeneratorVisitor(object):
    
    def __init__( self, config ):
        self.config = config;
        self.content_processors = {
            'html': [
                processors.Jinja2Renderer( config )
            ],
            'css': [
                processors.IdentityRenderer( config )
            ]            
        }
    
    def visit( self, node ):
        pass
    
    def visitDirectoryNode( self, node ):
        relative_path = os.path.relpath( node.path, self.config['content_path'] )
        output_path = os.path.join( self.config['output_path'], relative_path )

        if not os.path.exists( output_path ):
            print "#   Creating: " + relative_path
            os.makedirs( output_path );
    
    def visitContentNode( self, node ):
        # Truncate path to just the relative path from within the content directory, the append to
        # the output path to get the full path to the output file
        relative_path = os.path.relpath( node.path, self.config['content_path'] )
        output_path = os.path.join( self.config['output_path'], relative_path )

        # If processors have been registered for the node extension, run them against the node 
        # content and write that to the output file.
        if self.content_processors.has_key( node.extension ):
            print "# Processing: " + relative_path
            try:
                # Read content from content file
                content_file = codecs.open( node.path, 'r', 'utf-8' )
                content = content_file.read()
                content_file.close()

                # Apply registered processors to content
                for processor in self.content_processors[ node.extension ]:
                    content = processor.process( node, content )

                try:
                    # Write processed content to same named file in the output directory
                    with codecs.open( output_path, 'w', 'utf-8' ) as f:
                        f.write( content )
                        f.close()
                except IOError:
                    print >> sys.stderr, "## Error: Couldn't open " + output_path + " for writing"
            except IOError:
                print >> sys.stderr, "## Error: Couldn't read " + node.path + " for processing"

        # If no processors registered, just copy the file to the output folder
        else:
            print "#    Copying: " + relative_path
            try:
                shutil.copy2( node.path, output_path )
            except shutil.Error:
                print >> sys.stderr, "## Error: Couldn't copy " + node.path + " to " + output_path