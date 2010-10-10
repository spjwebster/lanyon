import sys, os, re, datetime, codecs
import jinja2
import lanyon.structure

class SitePostProcessor():
    def __init__( self, config ):
        self.config = config
    
    def process( self, site ):
        pass

class TagPageGenerator( SitePostProcessor ):
    
    def __init__( self, config, options ):
        # TODO: Fix
        SitePostProcessor.__init__( self, config )
        self.options = options

        # Set up jinja2 environment to load templates from layout directory
        env = jinja2.Environment(
            loader = jinja2.FileSystemLoader( [ self.config['layout_path'] ] ),
        )
        self.template = env.get_template( self.options['template'] )
        
        
    def process( self, site ):
        print '# TagPageGenerator: Generating tag pages'
        tags_output_path = os.path.join( self.config['output_path'], 'tags' )
        
        if not os.path.exists( tags_output_path ):
            os.makedirs( tags_output_path )
        
        for tag_name in site.tags.keys():
            tag = site.tags[tag_name];
            
            node = lanyon.structure.ContentNode( os.path.join( 'tags', tag['slug'] + '.html' ) )
            
            print '## Generating: /' + node.path;
            
            output_path = os.path.join(  self.config['output_path'], node.output_path )
            
            template_data = {
                'site': site,
                'tag': tag,
                'node': node,
                'now': datetime.datetime.utcnow().replace( microsecond=0 )
            }

            content = self.template.render( template_data )
            
            try:
                # Write processed content to same named file in the output directory
                with codecs.open( output_path, 'w', 'utf-8' ) as f:
                    f.write( content )
                    f.close()
            except IOError:
                print >> sys.stderr, "## Error: Couldn't open " + output_path + " for writing"
            

        