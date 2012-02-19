import xapian

try:
    import json
except ImportError:
    import simplejson as json

import helper

class PluginIndexer(object):
    def __init__(self, db_path):
        self.db = xapian.WritableDatabase(db_path, xapian.DB_CREATE_OR_OPEN)

    def index(self, name, author, author_email, description):
        doc = xapian.Document()
        data = {'name': name,
                'author': author,
                'author_email': author_email,
                'description': description}
        name = name.lower()
        author = author.lower()
        author_email = author_email.lower()
        description = description.lower()

        json_data = json.dumps(data)

        # this adds arbitrary string data that is retrived when
        # you preform a search - you can put as much data or
        # as little data as you would like here - for instance
        # you can simply put the name in here and query the
        # master db to get the rest of the data or you can
        # cache the entire DB record here
        doc.set_data(json_data)

        description_indexer = xapian.TermGenerator()
        stemmer = xapian.Stem("english")
        description_indexer.set_stemmer(stemmer)
        nonstemmed_indexer = xapian.TermGenerator()

        description_indexer.set_document(doc)
        nonstemmed_indexer.set_document(doc)
        
        nonstemmed_indexer.index_text(name)
        description_indexer.index_text(description)
        # weight the name
        doc.add_term(name, 10)

        nonstemmed_indexer.index_text(author)
        nonstemmed_indexer.index_text(author_email)

        nonstemmed_indexer.index_text(description)

        # add values to slots
        doc.add_value(helper.NAME_SLOT, name)
        doc.add_value(helper.AUTHOR_SLOT, author)
        doc.add_value(helper.AUTHOR_EMAIL_SLOT, author_email)

        # Add the document to the database.
        self.db.add_document(doc)

def populate_test_data():
    # remember if the DB already exists you will be adding duplicate doc
    # there is two stratagies for updating db data
    #   1. always create a new db, erase the old db and move the new one in its place
    #   2. check to see if a document already exists (you will need to add boolean slot matches
    #      on the primary id which is name in this case) and update the document
    indexer = PluginIndexer('xapian_test')
    test_data = [{'name': 'test1_plugin',
                  'author': 'John (J5) Palmieri',
                  'author_email': 'johnp@redhat.com',
                  'description': 'This is a test plugin.  The first one in fact. I hope you like it!'
                 },
                 {'name': 'test2_plugin',
                  'author': 'John (J5) Palmieri',
                  'author_email': 'johnp@redhat.com',
                  'description': 'This is a test plugin.  The second one in fact. I hope you like it!'
                 },
                 {'name': 'Foo',
                  'author': 'Jasper St. Pierre',
                  'author_email': 'stpierre@mecheye.net',
                  'description': 'FooBar? YouBar! How do you like them apples?'
                 },
                 {'name': 'Bar',
                  'author': 'Jasper St. Pierre',
                  'author_email': 'stpierre@mecheye.net',
                  'description': 'Apples? I like oranges!'
                 }]

    for data in test_data:
        print "Indexing %s" % data['name']
        indexer.index(**data)

if __name__ == "__main__":
    populate_test_data()
