import os

class SitePostProcessor():
    def __init__( self, config ):
        self.config = config
    
    def process( self, site ):
        pass


class MarkdownFileRenamer( SitePostProcessor ):
    # TODO: These extensions should probably come from configuration
    _extensions = ('.markdown','.mdown','.md')
    
    def process( self, site ):
        # TODO: Might be better to walk the content tree rather than raw output directory files
        for path, directories, files in os.walk( self.config[ 'output_path' ] ):
            for filename in files:
                ( basename, extension ) = os.path.splitext( filename )
                if extension in self._extensions:
                    os.rename( os.path.join( path, filename ), os.path.join( path, basename + '.html' ) )