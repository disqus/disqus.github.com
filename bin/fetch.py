#!/usr/bin/env python

from feedreader.parser import from_url
import bleach
import cgi
import codecs
import datetime
import logging
import os.path
import re

try:
    from settings import *
except ImportError:
    pass

FEEDS = (
    # ('DISQUS USERNAME', 'DISQUS FORUM SHORTNAME', 'FEED URL'),
    ('zeeg', 'davidcramer', 'http://justcramer.com/feeds/disqus.xml'),
    ('dz', 'nodnod', 'http://blog.nodnod.net/tagged/disqus/rss'),
    # ('disqus', 'disqus', 'http://blog.disqus.com/tagged/dev/rss'),
    ('bretthoerner', 'bretthoerner', 'http://bretthoerner.com/tags/disqus/feed.atom'),
    ('antonkovalyov', 'self', 'http://anton.kovalyov.net/disqus.xml'),
)

# slugify, linebreaks, and truncate_html_words are from Django

def summarize(value):
    # remove headings
    r = re.compile(r'<(h[1-6])[^<]*>[^<]*<\/(h[1-6])[^<]*>', re.I)
    value = r.sub('', value)
    # remove paragraphs/linebreaks
    # value = re.sub(r'<\/?(br|p)>', '', value)
    value = bleach.clean(value, tags=[], strip=True)
    value = value.replace('"', '')
    return '<p>%s</p>' % truncate_html_words(value, 100).replace('\n', '   ')

def strip_tags(value):
    return bleach.clean(value, tags=['a', 'b', 'strong', 'i', 'em', 'p', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'code', 'cite', 'pre', 'blockquote'], strip=True)

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = re.sub('[-\s]+', '-', value)
    return value

def linebreaks(value, autoescape=False):
    """Converts newlines into <p> and <br />s."""
    value = re.sub(r'\r\n|\r|\n', '\n', unicode(value)) # normalize newlines
    paras = re.split('\n{2,}', value)
    if autoescape:
        paras = [u'<p>%s</p>' % cgi.escape(p).replace('\n', '<br />') for p in paras]
    else:
        paras = [u'<p>%s</p>' % p.replace('\n', '<br />') for p in paras]
    return u''.join(paras)

def truncate_html_words(s, num, end_text='...'):
    """Truncates html to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    html. Takes an optional argument of what should be used to notify that the
    string has been truncated, defaults to ellipsis (...)."""
    length = int(num)
    if length <= 0:
        return u''
    html4_singlets = ('br', 'col', 'link', 'base', 'img', 'param', 'area', 'hr', 'input')
    # Set up regular expressions
    re_words = re.compile(r'&.*?;|<.*?>|(\w[\w-]*)', re.U)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?: (/)| .*?)?>')
    # Count non-HTML words and keep note of open tags
    pos = 0
    end_text_pos = 0
    words = 0
    open_tags = []
    while words <= length:
        m = re_words.search(s, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word
            words += 1
            if words == length:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or end_text_pos:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        tagname = tagname.lower()  # Element names are always case-insensitive
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag, all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i+1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)
    if words <= length:
        # Don't try to close tags if we don't need to truncate
        return s
    out = s[:end_text_pos]
    if end_text:
        out += ' ' + end_text
    # Close any tags still open
    for tag in open_tags:
        out += '</%s>' % tag
    # Return string
    return out

class FeedAggregator(object):
    def collect(self, author, forum, feed_url):
        feed = from_url(feed_url)
        for entry in feed.entries:
            slug = '%s-%s' % (author, slugify(unicode(entry.title)))
            self.write(author, forum, entry.link, entry.title,
                       entry.description, entry.published, slug)
    
    def write(self, disqus_username, disqus_forum, url, title, body, date=None, slug=None):
        if not url:
            return
        
        print "Saving", url

        if not date:
            date = datetime.datetime.now()
        
        filename = date.strftime('%Y-%m-%d-%%s.html') % slug
        
        outfile = codecs.open(os.path.join(os.path.dirname(__file__), '..', '_posts', filename), 'wb', 'utf-8')
        
        template = open(os.path.join(os.path.dirname(__file__), '..', '_templates', 'post.html'), 'r').read()
        
        if not body.startswith('<'):
            body = linebreaks(body)
            
        body = body.replace('{', '&#123;')\
                   .replace('}', '&#125;')
        
        data = {
            'disqus_forum': disqus_forum,
            'title': title,
            'url': url,
            'slug': slug,
            'body': strip_tags(body),
            'summary': summarize(body),
            'disqus_username': disqus_username,
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        outfile.write(template % data)
        outfile.close()

def main():
    agg = FeedAggregator()
    for author, forum, feed in FEEDS:
        try:
            agg.collect(author, forum, feed)
        except Exception, e:
            logging.exception(e)

if __name__ == '__main__':
    main()