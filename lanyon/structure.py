import os, codecs, inspect
import lanyon.glob

class SiteNode( object ):
    def __init__( self, path ):
        self.path = path
        self.name = os.path.basename( path )
        pass

    def relative_path_to( self, descendant ):
        path = descendant.path
        if self.path and path.startswith( self.path + '/' ):
            path = path[ len( self.path ) + 1 : ]
        return path
        
    def visit( self, visitor ):
        class_hierarchy = inspect.getmro(self.__class__)
        visit_methods = ['visit' + x.__name__ for x in class_hierarchy]
        for method in visit_methods:
            if hasattr( visitor, method ) and callable( getattr( visitor, method ) ):
                return getattr( visitor, method )( self )
        
        return visitor.visit(self);
        

class DirectoryNode( SiteNode ):
    def __init__( self, path ):
        super( DirectoryNode, self ).__init__( path )
        self.children = {}
        
    def add_child( self, child ):
        # TODO: Make this work
        # if child.parent:
        #     child.prent.remove_child(child)
        
        self.children[ child.name ] = child
        child.parent = self
        return child

    def find( self, path_pattern, start_node = None ):
        matches = []
        
        start_node = start_node or self
        
        for name, child in self.children.items():
            
            relative_path = start_node.relative_path_to( child )
            
            if lanyon.glob.match( relative_path, path_pattern ):
                matches.append( child )
            
            if child.__class__ == DirectoryNode:
                matches.extend( child.find( path_pattern, start_node ) or [] )
        
        return matches
        
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
        self.extension = os.path.splitext( self.name )[ 1 ][ 1 : ]
        self.data = {}
        self._output_path = None
    
    # TODO: Allow output_path to be overridden for directories too
    def _get_output_path( self ):
        return self._output_path or self.path
    
    def _set_output_path( self, path ):
        self._output_path = path
    
    output_path = property( _get_output_path, _set_output_path )

    #TODO: Find a cleaner way for content nodes to know how to find their
    #      underlying files.
    def get_content( self, content_path ):
        # Read content from content file
        file_path = os.path.abspath(os.path.join( content_path, self.path ))
        content_file = codecs.open( file_path, 'r', 'utf-8' )
        content = content_file.read()
        content_file.close()

        return content


class SiteNodeVisitor( object ):
    def __init__( self, config ):
        self.config = config
    
    def visit( self, node ):
        pass