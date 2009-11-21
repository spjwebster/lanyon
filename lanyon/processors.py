import re
import jinja2, yaml

# TODO: create YAML data extractor to extract data from YAML front matter and store in node data
# TODO: create MarkdownRenderer that uses template from node data

class ContentProcessor(object):
    def __init__( self, config ):
        self.config = config
    
    def process( self, node, content ):
        pass
        
class IdentityRenderer( ContentProcessor ):
    def process( self, node, content ):
        return content

class YAMLFrontMatterExtractor( ContentProcessor ):
    """ Extracts YAML "front matter" from the top of the content """
    def process( self, node, content ):
        # TODO: compile regex for class and reuse
        match = re.match( r"^---\n(.+)\n---\n", content )
        print match
        if match:
            content = content[match.end():]
            yaml_content = match.group( 1 )
            node.data.update( yaml.load( yaml_content ) )
        
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
        return template.render( node.data )