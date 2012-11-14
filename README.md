# BandPage
The Python interface to the BandPage API. Supports the full spec at [https://developers.bandpage.com/docs](https://developers.bandpage.com/docs).

## Installation
```
$ pip install bandpage
```

## Basic Usage
```python
import bandpage
bandpage.conf.CLIENT_ID = 'abc'
bandpage.conf.SECRET_KEY = 'xyz'

token = bandpage.get_access_token()

print bandpage.get('{{ band id }}', access_token=token)
```

## Configuration
There is a global configuration that can be set in `bandpage.conf`, or can be passed through on a specific request.

```python
# Configure globally
bandpage.conf.CLIENT_ID = '{{ client id }}'
bandpage.conf.SECRET_KEY = '{{ secret key }}'
```
```python
# Configure locally
bandpage.get_access_token(client_id='{{ client id }}', secret_key='{{ secret key }}')
```

## Getting an access token
An `access_token` is needed for every request other than, obviously, requesting an `access_token`.

`bandpage.get_access_token()` returns a dict that contains the access_token itself as well as an expiration key. The exact dict looks like:
```python
>>> bandpage.get_access_token()
{u'access_token': u'rqay894bkhzn9aa6gjvruxta',
 u'expires_in': 3600,
 u'mapi': u'ziuCriaPleni4wroe6ousoub5lusplaf',
 u'token_type': u'bearer'}
```

This full dict can be passed around to further requests.

**Recommendation**: Cache the access_token based on the `expires_in` key. This will prevent your server needing to request a new token for every single request.

## Making requests
*The following examples assume that a token has aleady been retrieved*

### Grab a specific `bid`
```python
>>> bid = '123'
>>> bandpage.get(bid, access_token=token)
```
`bandpage.get` responds with a dict which represents the exact JSON that is returned from BandPage.

BandPage recommends not making assumptions about which keys are available, so the recommended access pattern is as such:
```python
>>> band = bandpage.get('123', access_token=token)
>>> band.get('bio')  # Safely gets the 'bio' key without raising a KeyError
>>> if band.get('bio') is not None:
      # Do something with the bio
      print band.get('bio')
```

### Grabbing connections
BandPage allows you to query for sets of connections related to your original `bid`.
```python
>>> events = bandpage.get('123/events', access_token=token)
>>> for event in events:
      print event
```
Connections are explained at [https://developers.bandpage.com/docs/api_reference/Band_Object#connections](https://developers.bandpage.com/docs/api_reference/Band_Object#connections).

### Exceptions
When making a request for a specific `bid` or any connection, BandPage may respond with a number of errors:
 * 401 Unauthorized
 * 404 Not Found
 * Any other number of non-200 errors

`bandpage` provides a generic `BandpageError` exception which encompasses anything, and specific `BandpageUnauthorized` and `BandpageNotFound` exceptions.

```python
try:
  band = bandpage.get('123', access_token=token)
except bandpage.BandpageError:
  print "Oops, BandPage fail!"
```

## Protips™
### Access token caching pattern
```python
token = cache.get('BandPage:access_token')
if token is None:
  token = bandpage.get_access_token()
  cache.set('BandPage:access_token', token, token['expires_in'])
bandpage.get('123', access_token=token)
```

### Django
This library allows you to configure the `CLIENT_ID` and `SECRET_KEY` inside your `settings.py` for convenience. These settings will be applied globally for all access token requests, but can still be overridden by any of the aforementioned methods.
```python
BANDPAGE_CLIENT_ID = 'abc'
BANDPAGE_SECRET_KEY = 'xyz'
```


## Response object
```python
bandpage.get('123', access_token=token)