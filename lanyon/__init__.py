import codecs, os, sys, shutil
import structure, content_processors, pre_processors, post_processors

class Site( object ):
    def __init__( self, config ):
        self.config = config
        self.config[ 'site' ] = self
        self.content_root = None

        # TODO: Populate pre-processors from configuration
        self.site_preprocessors = [
        ]
        
        self.content_processors = {}
        try:
            for extensions, processors in self.config['content_processors'].items():
                self.content_processors[ extensions ] = []
                for processor in processors:
                    # TODO: Import processor class with try/except to handle import errors
                    try:
                        processor_class = self._get_class( processor )
                        self.content_processors[ extensions ].append( processor_class( config ) )
                    except:
                        print "### Could not instantiate '" + processor + "' content processor"
        except:
            pass

        # TODO: Populate post-processors from configuration
        self.site_postprocessors = [
            post_processors.MarkdownFileRenamer( config )
        ]
    
    def build_content_tree( self, content_path ):
        root = structure.RootNode( content_path )
    
        # TODO: Possibly move this lookup-node-by-path functionality into the DirectoryNode class
        directory_nodes = { content_path: root }
    
        for path, directories, files in os.walk( content_path ):

            # Get node for parent path
            parent_node = directory_nodes[ path ]

            # Add all directories as DirectoryNode instances
            for directory in directories:
                full_path = os.path.join( path, directory )
                relative_path = os.path.relpath( full_path, content_path )
                directory_node = parent_node.addChild( structure.DirectoryNode( relative_path ) )
                directory_nodes[ full_path ] = directory_node
        
            # Add all files as ContentNode instances
            for filename in files:
                full_path = os.path.join( path, filename )
                relative_path = os.path.relpath( full_path, content_path )
                parent_node.addChild( structure.ContentNode( relative_path ) )
        
        return root
    
    def _get_class( self, class_name ):
        parts = class_name.split('.')
        module_name = ".".join( parts[ :-1 ] )

        module = __import__( module_name )

        for part in parts[ 1: ]:
            module = getattr( module, part )            

        return module
        
    def generate( self ):
        if self.content_root == None:
            self.content_root = self.build_content_tree( self.config['content_path'] )
    
        # Attempt to create output directory if it doesn't exist
        if not os.path.exists( self.config['output_path'] ):
            os.makedirs( self.config['output_path'] )
        
        # Run site preprocessors
        for processor in self.site_preprocessors:
            processor.process( self )
        
        # Generate output from content tree
        self.content_root.visit( OutputGeneratorVisitor( self.config, self.content_processors ) );

        # Run site postprocessors
        for processor in self.site_postprocessors:
            processor.process( self )


class OutputGeneratorVisitor(object):
    
    def __init__( self, config, content_processors ):
        self.config = config;
        self.content_processors = content_processors
    
    def visit( self, node ):
        pass
    
    def visitDirectoryNode( self, node ):
        # Get full path to content and output files
        content_path = os.path.join( self.config['content_path'], node.path )
        output_path = os.path.join( self.config['output_path'], node.path )

        if not os.path.exists( output_path ):
            print "#   Creating: /" + node.path
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
            print "# Processing: /" + node.path
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
                    # TODO: Allow overriding of output filename from node data or similar
                    with codecs.open( output_path, 'w', 'utf-8' ) as f:
                        f.write( content )
                        f.close()
                except IOError:
                    print >> sys.stderr, "## Error: Couldn't open " + output_path + " for writing"
            except IOError:
                print >> sys.stderr, "## Error: Couldn't read " + content_path + " for processing"

        # If no processors registered, just copy the file to the output folder
        else:
            print "#    Copying: /" + node.path
            try:
                shutil.copy2( content_path, output_path )
            except shutil.Error:
                print >> sys.stderr, "## Error: Couldn't copy " + content_path + " to " + output_path
