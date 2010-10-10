import re, datetime
import jinja2, yaml, markdown

class ContentProcessor(object):
    def __init__( self, config ):
        self.config = config
    
    def process( self, node, content ):
        pass

 
class IdentityRenderer( ContentProcessor ):
    def process( self, node, content ):
        return content


class YAMLFrontMatterRemover( ContentProcessor ):  
    """ Removes YAML front matter from content """
    front_matter_re = re.compile( r"^---\s*\n(?:(?:.|\n)+?)\n---\s*\n" )
    
    def process( self, node, content ):
        match = re.match( self.front_matter_re, content )
        if match:
            content = content[match.end():]
        return content


class Jinja2Renderer( ContentProcessor ):
    def __init__( self, config ):
        super( Jinja2Renderer, self ).__init__( config )
        
        # Set up jinja2 environment to load templates from layout directory
        self.env = jinja2.Environment(
            loader = jinja2.FileSystemLoader( [ self.config['layout_path'] ] ),
        )
        
    def process( self, node, content ):
        template = self.env.from_string( content )
        template_data = { 
            'node': node,
            'site': self.config[ 'site' ],
            'now': datetime.datetime.utcnow().replace( microsecond=0 )
        }

        return template.render( template_data )


class MarkdownRenderer( ContentProcessor ):
    def __init__( self, config ):
        super( MarkdownRenderer, self ).__init__( config )
        
        # Set up jinja2 environment to load templates from layout directory
        self.env = jinja2.Environment(
            loader = jinja2.FileSystemLoader( [ self.config['layout_path'] ] ),
        )

    def process( self, node, content ):
        if not node.data.has_key( 'template' ):
            raise Exception( 'MarkdownRenderer: Missing \'template\' data on node' )
        
        template = self.env.get_template( node.data['template'] )
        
        if not template:
            raise Exception( 'MarkdownRenderer: Template \'' + node.data['template'] + '\' not found' )
        
        md = markdown.Markdown()
        
        template_data = { 
            'node': node,
            'site': self.config[ 'site' ],
            'now': datetime.datetime.utcnow().replace( microsecond=0 ),
            'content': md.convert( content )
        }

        return template.render( template_data )