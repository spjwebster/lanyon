from lanyon import structure
import nose.tools

class TestDirectoryFind:
    def setUp(self):
        self.root = structure.RootNode( '' )
        self.root.add_child( structure.ContentNode( 'index.html' ) )
        self.posts_dir = self.root.add_child( structure.DirectoryNode( 'posts' ) )
        self.posts_dir.add_child( structure.ContentNode( 'posts/index.html') )
        self.posts_dir.add_child( structure.ContentNode( 'posts/test.html') )
        
    def test_directory_find_wildcard_filename( self ):
        matches = self.root.find( '*.html' )
        nose.tools.eq_( len( matches ), 1 )
        
        matches = self.root.find( '**.html' )
        nose.tools.eq_( len( matches ), 3 )
        
        matches = self.root.find( 'posts/*.html' )
        nose.tools.eq_( len( matches ), 2 )
        
    def test_directory_find_exact_filename( self ):
        matches = self.root.find( 'index.html' )
        nose.tools.eq_( len( matches ), 1 )
        
        matches = self.root.find( '*/index.html' )
        nose.tools.eq_( len( matches ), 1 )
        
        matches = self.root.find( '*/test.html' )
        nose.tools.eq_( len( matches ), 1 )

    def test_directory_find_wildcard_filename_with_path( self ):
        matches = self.root.find( 'posts/*.html' )
        nose.tools.eq_( len( matches ), 2 )

    def test_local_find_wildcard_filename( self ):
        matches = self.posts_dir.find( '*.html' )
        nose.tools.eq_( len( matches ), 2 )       
         
    def test_local_find_exact_filename( self ):
        matches = self.posts_dir.find( 'test.html' )
        nose.tools.eq_( len( matches ), 1 )