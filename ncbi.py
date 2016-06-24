import requests
import urllib
import urlparse
import xml.etree.ElementTree as ET


def extract_pmids(result_raw):
    """
    Parse NCBI Entrez result for PMIDs.

    Parameters
    ----------
    result_raw : str
        Raw XML from NCBI.

    Returns
    -------
    list
        A list of PUBMED IDs.
    """
    e = ET.fromstring(result_raw)
    return [id_elem.text for id_elem in e.find('IdList').getchildren()]


def _entrez(scheme, netloc, path, **params):
    """
    Perform a call to the NCBI Entrez API.

    .. todo:: Make ``tool`` and ``email`` parameters configurable.
    """
    params.update({
        'tool': 'modelorgspeirson',
        'email': 'erick.peirson@asu.edu',
    })
    query = urllib.urlencode(params)
    target = urlparse.urlunsplit((scheme, netloc, path, query, ''))
    return requests.get(target).text


def esearch(scheme='http', netloc='eutils.ncbi.nlm.nih.gov',
            path='entrez/eutils/esearch.fcgi',
            handler=extract_pmids, **params):
    """
    Perform an ESearch request.

    See http://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch.
    """
    return handler(_entrez(scheme, netloc, path, **params))


def efetch(scheme='http', netloc='eutils.ncbi.nlm.nih.gov',
           path='entrez/eutils/efetch.fcgi',
           handler=lambda d: ET.fromstring(d.encode('utf-8')), **params):
    return handler(_entrez(scheme, netloc, path, **params))
