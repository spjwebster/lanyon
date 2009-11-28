import os, codecs, re
import yaml, lanyon.structure

class SitePreProcessor():
    def __init__( self, config ):
        self.config = config
    
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