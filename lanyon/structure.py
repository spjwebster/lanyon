import os
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

    def find( self, path_pattern, deep = True, start_node = None ):
        matches = []
        
        start_node = start_node or self
        
        for name, child in self.children.items():
            
            relative_path = start_node.relative_path_to( child )
            
            if lanyon.glob.match( relative_path, path_pattern ):
                matches.append( child )
            
            if deep and child.__class__ == DirectoryNode:
                matches.extend( child.find( path_pattern, deep, start_node ) or [] )
        
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


class SiteNodeVisitor( object ):
    def __init__( self, config ):
        self.config = config
    
    def visit( self, node ):
        pass