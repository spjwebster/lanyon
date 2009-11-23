import os, fnmatch

class SiteNode( object ):
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

    def find( self, path_pattern, deep = True ):
        matches = []
        
        for name, child in self.children.items():
            print path_pattern + " vs. " + child.path
            if fnmatch.fnmatch( child.path, path_pattern ):
                matches.append( child )
            
            if deep and child.__class__ == DirectoryNode:
                matches.extend( child.find( path_pattern, deep ) or [] )
        
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
        self.extension = os.path.splitext( path )[ 1 ][1:]
        self.data = {}