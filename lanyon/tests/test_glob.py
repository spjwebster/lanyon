from lanyon import glob
from nose.tools import *

def test_exact_match():
    assert_true( glob.match( 'test.html', 'test.html' ) )
    assert_true( glob.match( 'foo.html', 'foo.html' ) )
    assert_true( glob.match( 'bar.html', 'bar.html' ) )

def test_exact_mismatch():
    assert_false( glob.match( 'foo.html', 'bar.html' ) )
    assert_false( glob.match( 'test.html', 'est.html' ) )
    assert_false( glob.match( 'test.html', 'test.htm' ) )
    assert_false( glob.match( 'test.html', 'tes...tml' ) )
    
    
def test_char_wildcard_match():
    assert_true( glob.match( 'test.html', 'tes?.html' ) )
    assert_true( glob.match( 'test.html', 'test.htm?' ) )
    assert_true( glob.match( 'test.html', 't?s?.?t?l' ) )
    assert_true( glob.match( 'test.html', '????.html' ) )
    assert_true( glob.match( 'test.html', '?????????' ) )

def test_char_wildcard_mismatch():
    assert_false( glob.match( 'test.html', 'test.html?' ) )
    assert_false( glob.match( 'test.html', '?test.html' ) )
    assert_false( glob.match( 'test.html', 'test??html' ) )
    assert_false( glob.match( 'test.html', '?.html' ) )
    assert_false( glob.match( 'test.html', '?e?.html' ) )
    assert_false( glob.match( 'test.html', 'test.?' ) )
    assert_false( glob.match( 'test.html', '??????????' ) )
    
    
def test_single_star_wildcard_match():
    assert_true( glob.match( '/foo/bar/blatt.html', '/foo/bar/*.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/*/bar/blatt.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/*/*/blatt.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/*/*/*.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/*/*/bla*' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/*/*/*' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/*/*/*.html' ) )

def test_single_star_wildcard_mismatch():
    assert_false( glob.match( '/foo/bar/blatt.html', '*.html' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '/foo/*.html' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '/*/blatt.html' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '/*/*/blatt.foo' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '/*/*/*.foo' ) )
    

def test_double_star_wildcard_match():
    assert_true( glob.match( '/foo/bar/blatt.html', '**.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/**.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '**/bar/blatt.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '**/blatt.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '**oo/**/bl**tml' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/**/blatt.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/**/**.html' ) )
    
def test_double_star_wildcard_mismatch():
    assert_false( glob.match( '/foo/bar/blatt.html', '**/foo/bar/blatt.html' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '**/foo/blatt.html' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '/foo/bar/blatt.html**' ) )
    assert_false( glob.match( '/foo/bar/blatt.html', '**.html**' ) )


def test_char_class_match():
    assert_true( glob.match( 'test.html', '[Tt]est.html' ) )
    assert_true( glob.match( 'test.html', '[Tt][Ee][Ss][Tt].[Hh][Tt][Mm][Ll]' ) )
    assert_true( glob.match( 'test.html', '[Tt]e[Ss]t.[Hh]tm[Ll]' ) )
    assert_true( glob.match( 'test.html', 'test[.]html' ) )
    assert_true( glob.match( 'test.html', '[bfjlnprtvwz]est.html' ) )
    assert_true( glob.match( 'test.html', '[a-z]est.html' ) )
    assert_true( glob.match( 'test.html', '[r-u]est.html' ) )
    assert_true( glob.match( 'test.html', '[:a-su-z]est.html' ) )

def test_char_class_mismatch():
    assert_false( glob.match( 'test.html', '[xyz]est.html' ) )
    assert_false( glob.match( 'test.html', '[a-s]est.html' ) )
    assert_false( glob.match( 'test.html', '[u-z]est.html' ) )
    assert_false( glob.match( 'test.html', '[a-su-z]est.html' ) )
    assert_false( glob.match( 'test.html', '[:a-z]est.html' ) )


def test_sub_pattern_match():
    assert_true( glob.match( 'test.html', 'test.{html}' ) )
    assert_true( glob.match( 'test.html', 'test.{html,txt}' ) )
    assert_true( glob.match( 'test.html', '{te,tes}t.html' ) )
    assert_true( glob.match( 'test.html', 'test{.,_}{html,txt}' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '/foo/{foo,bar}/blatt.html' ) )
    assert_true( glob.match( '/foo/bar/blatt.html', '{/foo/bar,/fee/fie}/blatt.html' ) )

def test_sub_pattern_mismatch():
    assert_false( glob.match( 'test.html', 'test.{xml}' ) )
    assert_false( glob.match( 'test.html', 'test.{xml,txt}' ) )
    assert_false( glob.match( 'test.html', 'test.{xml,txt}' ) )
    assert_false( glob.match( 'test.html', '{a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,u,v,w,x,y,z}est.html' ) )


def test_complex_match():
    assert_true( glob.match( '/foo/bar/blatt/test.html', '**.{html,txt}' ) )
    assert_true( glob.match( '/foo/bar/blatt/test.html', '/*/**.{html,txt}' ) )
    assert_true( glob.match( '/foo/bar/blatt/test.html', '/*/**/te?t.{html,txt}' ) )
    assert_true( glob.match( '/foo/bar/blatt/test.html', '/*/**.{ht??,txt}' ) )
    assert_true( glob.match( '/foo/bar/blatt/test.html', '/*/**.{ht?,html}' ) )
    assert_true( glob.match( '/foo/bar/blatt/test.html', '**/[bc]a?/**/*.{txt,html}' ) )

