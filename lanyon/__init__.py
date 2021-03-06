import codecs, os, sys, shutil
import structure, content_processors, pre_processors, post_processors

class Site( object ):
    def __init__( self, config ):
        self.config = config
        self.config[ 'site' ] = self
        self.content_root = None

        # Must have front matter preprocessor
        self.site_preprocessors = [
            pre_processors.YAMLFrontMatterLoader( config ),
        ]

        # Populate remaining pre-processors from configuration
        for processor in self.config['pre_processors']:
            # Allow just class naem as plain string
            if isinstance(processor, basestring):
                processor = {
                    'class': processor,
                    'options': {},
                }

            processor_class = self._get_class( processor['class'] )

            self.site_preprocessors.append(
                processor_class( config, processor['options'] )
            )
        
        # Poplate content processors from config
        self.content_processors = {}
        for processor in self.config['content_processors']:
            if not processor.has_key('options'):
                processor['options'] = {}

            processor_class = self._get_class( processor['class'] )

            try:
                processor_instance = processor_class( config, processor['options'] )
                for extension in processor['extensions']:
                    if self.content_processors.has_key(extension) == False:
                        self.content_processors[extension] = []
                    self.content_processors[extension].append( processor_instance )
            except:
                print "### Could not instantiate '" + processor['class'] + "' content processor"
                

        # Populate rpost-processors from configuration
        self.site_postprocessors = []
        for processor in self.config['post_processors']:
            # Allow just class naem as plain string
            if isinstance(processor, basestring):
                processor = {
                    'class': processor,
                    'options': {},
                }

            processor_class = self._get_class( processor['class'] )

            self.site_postprocessors.append(
                processor_class( config, processor['options'] )
            )
    
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
                directory_node = parent_node.add_child( structure.DirectoryNode( relative_path ) )
                directory_nodes[ full_path ] = directory_node
        
            # Add all files as ContentNode instances
            for filename in files:
                full_path = os.path.join( path, filename )
                relative_path = os.path.relpath( full_path, content_path )
                parent_node.add_child( structure.ContentNode( relative_path ) )
        
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


class OutputGeneratorVisitor( structure.SiteNodeVisitor ):
    
    def __init__( self, config, content_processors ):
        super( OutputGeneratorVisitor, self ).__init__( config )
        self.content_processors = content_processors
    
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
        output_path = os.path.join( self.config['output_path'], node.output_path )

        # Build a list of content processors for th enode
        node_content_processors = []
        
        
        if self.config.has_key( 'yaml_extensions' ) and node.extension in self.config[ 'yaml_extensions' ]:
            node_content_processors.append( content_processors.YAMLFrontMatterRemover( self.config ) )
        
        # Find all processors that are registered for the node file extension. The first set of 
        # processors match wins, which is necessary as content processor order needs to be 
        # preserved.
        for extensions, processors in self.content_processors.items():
            if node.extension in extensions:
                node_content_processors.extend( processors )
                break
        
        # If processors have been registered for the node extension, run them against the node 
        # content and write that to the output file.
        if node_content_processors:
            print "# Processing: /" + node.path
            try:
                content = node.get_content( self.config['content_path'] )

                # Apply registered processors to content
                for processor in node_content_processors:
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
            print "#    Copying: /" + node.path
            try:
                shutil.copy2( content_path, output_path )
            except shutil.Error:
                print >> sys.stderr, "## Error: Couldn't copy " + content_path + " to " + output_path
