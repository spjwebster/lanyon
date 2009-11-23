import re

def match( filename, pattern ):
    pattern_re = _build_regexp( pattern )
    return re.search( pattern_re, filename )
    
def _build_regexp( pattern ):
    pattern = pattern.replace( '.', '\\.' )
    pattern = pattern.replace( '?', '.' )
    pattern = pattern.replace( '**', '.+' )
    pattern = pattern.replace( '*', '[^/]+' )

    pattern = re.sub( r"\[:(.+?)\]", r"[^\1]", pattern )

    pattern = re.sub( r"\{(.+?)\}", _convert_sub_match_to_re, pattern )

    print pattern

    return '^' + pattern + '$'

def _convert_sub_match_to_re( match ):
    return '(' + ( '|'.join( match.group( 1 ).split( ',' ) ) ) + ')'