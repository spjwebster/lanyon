import re, datetime
import jinja2, yaml, markdown
from subprocess import Popen, PIPE
import tempfile, os, codecs, sys

class ContentProcessor(object):
    def __init__( self, config, options = {} ):
        self.config = config
        self.options = options
    
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
    def __init__( self, config, options ):
        super( Jinja2Renderer, self ).__init__( config, options )
        
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
    def __init__( self, config, options ):
        super( MarkdownRenderer, self ).__init__( config, options )
        
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

class ExternalProcessor( ContentProcessor ):
    """ 
        Processes content through an external process.

        External process must accept input from stdin and write output to
        stdout.
    """
    def process( self, node, content ):
        output = None;

        if self.options.has_key('pipe') and self.options['pipe'] == True:
            #TODO: Throw a more useful exception for command not found errors
            proc = Popen([self.options['cmd']], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            
            (output, err) = proc.communicate(input=content)
            if err:
                raise Exception( 'ExternalProcessor: ' + err)
        else:
            # Write content to temp input file
            input_file = None
            try:
                input_file = tempfile.NamedTemporaryFile(mode='w')
                input_file.write( content.encode('utf-8') )
                input_file.close()
            except IOError:
                print >> sys.stderr, "## Error: Couldn't open " + input_filename + " for writing"

            # Create temp output filename
            output_filename = input_file.name + '_output'

            # Call command, replacing {input} with filename and {output} with output
            command = self.options['cmd']
            command = command.replace('{input}', input_file.name)
            command = command.replace('{output}', output_filename)

            status = os.system(command)

            # Read content from output file
            try:
                with codecs.open( output_filename, 'r', 'utf-8' ) as f:
                    content = f.read()
                    f.close()
            except IOError:
                print >> sys.stderr, "## Error: Couldn't open " + output_filename + " for reading"

            # Delete temp input and output files
            try:
                os.remove(input_file.name)
            except:
                pass

            try:
                os.remove(output_filename)
            except:
                pass

        return output
