import os, codecs, re, datetime, sys, hashlib
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
                    node.data.update( yaml.load( yaml_content ) )
            
            # Done with this file
            content_file.close()
                
class BlogPostProcessor( SitePreProcessor ):
    tag_slug_re = re.compile("[^a-z0-9-]", re.IGNORECASE )
    
    def process( self, site ):
        # TODO: Deal with missing options['path']
        
        # Find all blog posts
        posts = site.content_root.find( self.options[ 'path' ] )

        # Exclude listings pages
        # TODO: Allow listings page URLs to come from global config
        posts = [ post for post in posts if not post.name == "index.html" ]
                
        # Convert 'postdate' data item into datetime stored on node
        for post in posts:
            try:
                post.postdate = datetime.datetime.strptime( str(post.data['postdate']), '%Y-%m-%dT%H:%M:%S' );
            except KeyError:
                sys.stderr.write("Couldn't find postdate in '%s'" % post.path);
                raise

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


class StaticAssetBundleGenerator( SitePreProcessor ):
    class _StaticAssetBundleNode( lanyon.structure.ContentNode ):
        def __init__(self, path, content):
            super(self.__class__, self).__init__( path )
            self._content = content

        def get_content( self, content_path ):
            return self._content
    
    def process( self, site ):
        for bundle_name in self.options['bundles']:
            bundle = self.options['bundles'][bundle_name]
            print "#   Creating: /" + bundle['output_path']
            
            content = ""
            for path in bundle['files']:
                for node in site.content_root.find(path):
                    print "##            - concatenating: /" + node.path
                    content += node.get_content(self.config['content_path'])
                    node.parent.remove_child(node)
            
            # Calculate version number based on content
            version = hashlib.sha1(content).hexdigest()[:16]
            print "##            - version: " + version

            # TODO: Create target dir (and any missing ancestors) if it doesn't 
            #       exist
            target_dir_node = site.content_root.find_first(
                os.path.dirname(bundle['output_path'])
            )

            # Add bundle node to target dir
            bundle_node = self.__class__._StaticAssetBundleNode(
                bundle['output_path'],
                content
            )
            bundle_node.data['version'] = version
            target_dir_node.add_child( bundle_node )


