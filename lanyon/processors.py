from jinja2 import Environment, FileSystemLoader

class ContentProcessor(object):
    def __init__( self, config ):
        self.config = config
    
    def process( self, node, content ):
        pass
        
class IdentityRenderer( ContentProcessor ):
    def process( self, node, content ):
        return content
        
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