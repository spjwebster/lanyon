import os, codecs, re, datetime
import yaml, lanyon.structure

class SitePreProcessor(object):
    def __init__( self, config, options = {} ):
        self.config = config
        self.options = options
    
    def process( self, site ):
        pass


class YAMLFrontMatterLoader( SitePreProcessor ):
    """ Extracts YAML front matter from all content nodes and stores it the node data """
    def process( self, site ):
        yaml_visitor = self._YAMLDataExtractor( self.config )
        site.content_root.visit( yaml_visitor )
    
    class _YAMLDataExtractor( lanyon.structure.SiteNodeVisitor ):
        front_matter_re = re.compile( r"^---\s*\n((?:.|\n)+?)\n---\s*\n" )

        def visitContentNode( self, node ):
            
            # Only process known YAML extensions
            if not ( self.config.has_key( 'yaml_extensions' ) and node.extension in self.config[ 'yaml_extensions' ] ):
                return

            try:
                # Open up content file for node
                content_path = os.path.join( self.config[ 'content_path' ], node.path )
                content_file = codecs.open( content_path, 'r', 'utf-8' )
                
                # Peek at the file to see if it might contain YAML front matter
                if content_file.read( 3 ) == "---":
                    # Read in file content
                    content_file.seek( 0 )
                    content = content_file.read()

                    # Extract YAML data into node data
                    match = re.match( self.front_matter_re, content )
                    if match:
                        content = content[match.end():]
                        yaml_content = match.group( 1 )
                        try:
                            node.data.update( yaml.load( yaml_content ) )
                        except:
                            # TODO: Handle malformed YAML data
                            pass
            except:
                # TODO: Handle file read error
                pass
                
            finally:
                content_file.close()
                
class BlogPostProcessor( SitePreProcessor ):
    tag_slug_re = re.compile("[^a-z0-9-]", re.IGNORECASE )

    def __init__( self, config, options ):
        super( BlogPostProcessor, self ).__init__( config )
        self.options = options
    
    def process( self, site ):
        # TODO: Deal with missing options['path']
        
        # Find all blog posts
        posts = site.content_root.find( self.options[ 'path' ] )

        # Exclude listings pages
        # TODO: Allow listings page URLs to come from global config
        posts = [ post for post in posts if not post.name == "index.html" ]
                
        # Convert 'postdate' data item into datetime stored on node
        for post in posts:
            post.postdate = datetime.datetime.strptime( str(post.data['postdate']), '%Y-%m-%dT%H:%M:%S' );

        # Sort posts by datetime and store on site object
        posts.sort( key = lambda post: post.postdate )
        site.posts = posts

        # Collate tags and posts
        tags = {}
        for post in posts:
            if not post.data.has_key('tags'):
                continue
            for tag_name in post.data['tags']:
                if not tags.has_key(tag_name):
                    tags[tag_name] = {
                        'name': tag_name,
                        'slug': self.slugify( tag_name ),
                        'posts': [],
                    }
                tags[tag_name]['posts'].append( post )
                
        # Posts are already date-ordered, so no need to wort twice
        site.tags = tags
        
    def slugify( self, tag_name ):
        slug = re.sub( self.tag_slug_re, '-', tag_name.lower() )
        slug = re.sub( '-+', '-', slug )
        return slug
        

class MarkdownOutputRenamer( SitePreProcessor ):
    def process( self, site ):
        # Find all markdown files
        # TODO: Allow markdown path pattern to come from processor config
        markdown_nodes = site.content_root.find( '**.{markdown,mdown,md}' )

        # Rename markdown posts to .html
        for node in markdown_nodes:
            node.output_path = os.path.splitext( node.path )[ 0 ] + '.html'