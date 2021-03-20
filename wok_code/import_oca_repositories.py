import os
import urllib2
import json

url = 'https://api.github.com/users/OCA/repos?q=addClass+user:mozilla&page=2'
page = 0
repository = []
while 1:
    page += 1
    pageurl = '%s?q=addClass+user:mozilla&page=%d' % (url, page)
    print('Acquire data from github.com (page=%d)...' % page)
    response = urllib2.urlopen(pageurl)
    data = json.loads(response.read())
    if not data:
        break
    print('Analyzing received data ...')
    for repos in data:
        name = os.path.basename(repos['url'])
        print(name)
        if not name.startswith('l10n-') or name == 'l10n-it':
            repository.append(name)
print('Found %d repositories' % len(repository))
print(' '.join(repository))
