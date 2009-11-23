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
                relative_path = os.path.relpath( full_path, content_path )
                directory_node = parent_node.addChild( DirectoryNode( relative_path ) )
                directory_nodes[ full_path ] = directory_node
        
            # Add all files as ContentNode instances
            for filename in files:
                full_path = os.path.join( path, filename )
                relative_path = os.path.relpath( full_path, content_path )
                parent_node.addChild( ContentNode( relative_path ) )
        
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
        child.parent = self
        return child
    
    def visit( self, visitor ):
        super( DirectoryNode, self ).visit( visitor )
        for name, child in self.children.items():
            child.visit( visitor )
        

class RootNode( DirectoryNode ):

    def __init__( self, path ):
        super( RootNode, self ).__init__( path )
    

class ContentNode( SiteNode ):
    def __init__( self, path ):
        super( ContentNode, self ).__init__( path )
        self.extension = os.path.splitext( path )[ 1 ][1:]
        self.data = {}


class OutputGeneratorVisitor(object):
    
    def __init__( self, config ):
        self.config = config;

        # TODO: Allow processors to be registered only for specific content branches. This should be
        # in addition to node file extension, with the option to specify one or the other or both.
        self.content_processors = {
            ('html'): [
                processors.YAMLFrontMatterExtractor( config ),
                processors.Jinja2Renderer( config )
            ],
            ('css','js'): [
                processors.IdentityRenderer( config )
            ]            
        }
    
    def visit( self, node ):
        pass
    
    def visitDirectoryNode( self, node ):
        # Get full path to content and output files
        content_path = os.path.join( self.config['content_path'], node.path )
        output_path = os.path.join( self.config['output_path'], node.path )

        if not os.path.exists( output_path ):
            print "#   Creating: " + node.path
            os.makedirs( output_path );
    
    def visitContentNode( self, node ):
        # Get full path to content and output files
        content_path = os.path.join( self.config['content_path'], node.path )
        output_path = os.path.join( self.config['output_path'], node.path )

        # Find all processors that are registered for the node file extension. The first set of 
        # processors match wins, which is necessary as content processor order needs to be 
        # preserved.
        node_processors = None
        for extensions, processors in self.content_processors.items():
            if node.extension in extensions:
                node_processors = processors
                break
        
        # If processors have been registered for the node extension, run them against the node 
        # content and write that to the output file.
        if node_processors:
            print "# Processing: " + node.path
            try:
                # Read content from content file
                content_file = codecs.open( content_path, 'r', 'utf-8' )
                content = content_file.read()
                content_file.close()

                # Apply registered processors to content
                for processor in node_processors:
                    content = processor.process( node, content )

                try:
                    # Write processed content to same named file in the output directory
                    with codecs.open( output_path, 'w', 'utf-8' ) as f:
                        f.write( content )
                        f.close()
                except IOError:
                    print >> sys.stderr, "## Error: Couldn't open " + output_path + " for writing"
            except IOError:
                print >> sys.stderr, "## Error: Couldn't read " + content_path + " for processing"

        # If no processors registered, just copy the file to the output folder
        else:
            print "#    Copying: " + node.path
            try:
                shutil.copy2( content_path, output_path )
            except shutil.Error:
                print >> sys.stderr, "## Error: Couldn't copy " + content_path + " to " + output_path
