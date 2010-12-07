from feedreader.parser import from_url
import datetime
import os.path
import re
import sqlite3

try:
    from settings import *
except ImportError:
    pass

conn = sqlite3.connect('db.sqlite')
conn.isolation_level = None

FEEDS = (
    # ('DISQUS_USERNAME', 'FEED URL'),
    ('zeeg', 'http://www.davidcramer.net/disqus/feed'),
)

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

class FeedAggregator(object):
    def collect(self, author, feed_url): 
        feed = from_url(feed_url)
        for entry in feed.entries:
            cursor = conn.cursor()
            cursor.execute('select 1 from entries where url = ? limit 1', [unicode(entry.link)])
            if not cursor.fetchall():
                slug = '%s-%s' % (author, slugify(unicode(entry.title)))
                self.write(author, entry.link, entry.title, entry.description, entry.published, slug)
                cursor.execute('insert into entries values(?)', [unicode(entry.link)])
    
    def write(self, disqus_username, url, title, body, date=None, slug=None):
        print "Saving", url
        if not date:
            date = datetime.datetime.now()
        
        filename = date.strftime('%Y-%m-%d-%%s.html') % slug
        
        outfile = open(os.path.join(os.path.dirname(__file__), '..', '_posts', filename), 'wb')
        
        template = open(os.path.join(os.path.dirname(__file__), '..', '_templates', 'post.html'), 'r').read()
        
        data = {
            'title': title,
            'url': url,
            'slug': slug,
            'body': body,
            'disqus_username': disqus_username,
            'date': date.strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        outfile.write(template % data)
        outfile.close()

def main():
    conn.execute('create table if not exists entries (url text)')
    
    agg = FeedAggregator()
    for author, feed in FEEDS:
        agg.collect(author, feed)

if __name__ == '__main__':
    main()