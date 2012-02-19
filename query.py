import xapian

try:
    import json
except ImportError:
    import simplejson as json

import helper

class Query(object):
    def __init__(self, db_path):
        self.db = xapian.Database(db_path)

    def query(self, search_string, start_row=0, rows_per_page = -1):
        # do a raw search - we can tweak this by analizing the search string
        # but for now just throw it through the QueryParser and see if
        # the results are accurate enough with the limited data set we
        # have

        enquire = xapian.Enquire(self.db)
        qp = xapian.QueryParser()
        qp.set_database(self.db)
        query = qp.parse_query(search_string)
        print str(query)
        enquire.set_query(query)

        if rows_per_page < 0:
            # get all
            rows_per_page = self.db.get_doccount()

        matches = enquire.get_mset(start_row, rows_per_page)

        return matches

def search(search_string):
    query = Query('xapian_test')
    matches = query.query(search_string, 0, 10)

    # this number isn't always correct but should be
    # here since we grabbed all of the results
    count = matches.get_matches_estimated()
    print "We estimate %d matches" % count
    for m in matches:
      result = json.loads(m.document.get_data())
      print "Matched %s (%s <%s>): %s" % (result['name'], result['author'], result['author_email'], result['description'])

    print 'We found %s matches for search string "%s"' % (len(matches), search_string)

if __name__ == '__main__':
    import sys

    search(' '.join(sys.argv[1:]))
