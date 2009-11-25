import os, re
import jinja2, yaml, markdown

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
        match = re.match( r"^---\n(.+?)\n---\n", content )
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
        html_content = md.convert( content )
        
        template_data = node.data.copy()
        template_data.update( { 'content': html_content } )

        return template.render( template_data )


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