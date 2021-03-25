#from time import sleep
#import requests
#from typing import Optional

#import pytest
import requests
#import responses

#from ucrel_api.ucrel_doc import UCREL_Doc
#from ucrel_api.ucrel_token import UCREL_Token
#from ucrel_api.api import UCREL_API


def test_requests() -> None:
    r = requests.get('http://ucrel-api.lancaster.ac.uk')
    assert r.status_code == 200