
import pycurl as pycurl
from StringIO import StringIO


def put (url, data, headers={}):
    """Make a PUT request to the url, using data in the message body,
    with the additional headers, if any"""

    reply = -1 # default, non-http response

    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.REFERER, 'http://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/frameCriterioBusqueda.jsp')



    if len(headers) > 0:
        curl.setopt(pycurl.HTTPHEADER, [k+': '+v for k,v in headers.items()])
    curl.setopt(pycurl.PUT, 1)
    curl.setopt(pycurl.INFILESIZE, len(data))
    databuffer = StringIO(data)
    curl.setopt(pycurl.READFUNCTION, databuffer.read)
    try:
        curl.perform()
        reply = curl.getinfo(pycurl.HTTP_CODE)
    except Exception:
        pass
    curl.close()

    return reply