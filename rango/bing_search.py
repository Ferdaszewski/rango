import json
import os
import urllib
import urllib2


# Get Bing API key
BING_API_KEY = os.environ["BING_API_KEY"]

def run_query(search_terms):
    root_url = 'https://api.datamarket.azure.com/Bing/Search/v1/'
    source = 'Web'
    results_per_page = 10
    offset = 0

    # As required by the BING API, wrap the query in quotes
    query = "'{0}'".format(search_terms)
    query = urllib.quote(query)

    # Create search URL string
    search_url = "{0}{1}?$format=json&$top={2}&$skip={3}&Query={4}".format(
        root_url,
        source,
        results_per_page,
        offset,
        query)

    # Bing server authentication requires empty string
    username = ''

    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, search_url, username, BING_API_KEY)

    # Result list to populate
    results = []

    try:
        # Prep for connecting to Bing's servers
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

        # Read response data
        response = urllib2.urlopen(search_url).read()

        # Load the JSON data into python dict
        json_response = json.loads(response)

        for result in json_response['d']['results']:
            results.append({
                'title': result['Title'],
                'link': result['Url'],
                'summary': result['Description']})
    except urllib2.URLError, e:
        print "Error when querying the Bing API: ", e

    return results


if __name__ == '__main__':
    # Test the BING search API
    test_queries = [
        'rango',
        'Ferdaszewski',
        'Tango with Django'
    ]

    for query in test_queries:
        print '=' * 20
        print "Search results for: ", query
        print run_query(query)
