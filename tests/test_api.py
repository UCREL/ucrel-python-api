from time import sleep
import requests
from typing import Optional

import pytest
import requests
import responses

from ucrel_api.ucrel_doc import UCREL_Doc
from ucrel_api.ucrel_token import UCREL_Token
from ucrel_api.api import UCREL_API


def test_requests() -> None:
    test_api = UCREL_API(email='a.moore@lancaster.ac.uk', 
                         server_address='http://ucrel-api.lancaster.ac.uk')
    # One sentence and token
    value = test_api.usas('hello')
    _doc = UCREL_Doc('hello', tokens=[DOC_TOKENS[0]], 
                     sentence_indexes=[(0,1)])
    assert value == _doc

def test_ucrel_api_repr() -> None:
    base_parameters = {'email':'test@example.com', 'server_address':'127.0.0.1'}
    
    server_address_only = UCREL_API(**base_parameters)
    assert 'UCREL API, server address 127.0.0.1, timeout 60 seconds' == str(server_address_only)

    port_and_server = UCREL_API(**base_parameters, port='8070')
    assert 'UCREL API, server address 127.0.0.1, port 8070, timeout 60 seconds' == str(port_and_server)

    timeout_different = UCREL_API(**base_parameters, port='8070', timeout=1)
    assert 'UCREL API, server address 127.0.0.1, port 8070, timeout 1 seconds' == str(timeout_different)


DOC_TOKENS = [UCREL_Token('hello', 'hello','UH', 'Z4'), UCREL_Token('how', 'how', 'RRQ', 'Z5'), 
              UCREL_Token('are', 'be','VBR', 'A3+'), UCREL_Token('you', 'you', 'PPY', 'Z8mf'),
              UCREL_Token('it', 'it', 'PPH1', 'Z8'), UCREL_Token("'s", "be", 'VBZ', 'A3+'),
              UCREL_Token('.', 'PUNCT','.', None), UCREL_Token('Great', 'great', 'JJ', 'A5.1+'),
              UCREL_Token('day', 'day', 'NNT1', 'T1.3')]

def test_ucrel_api_usas(port: Optional[str] = None) -> None:
    test_api = UCREL_API(email='a.moore@lancaster.ac.uk', 
                         server_address='http://ucrel-api.lancaster.ac.uk')
    # Test port
    if port is not None:
        test_api = UCREL_API(email='a.moore@lancaster.ac.uk', 
                             server_address='http://ucrel-api.lancaster.ac.uk',
                             port=port)
    # None case
    value = test_api.usas('')
    empty_doc = UCREL_Doc("", tokens=[], sentence_indexes=[])
    assert value == empty_doc
    # sleeps are to ensure not too many calls are made to the API
    sleep(0.5)

    # One sentence and token
    value = test_api.usas('hello')
    _doc = UCREL_Doc('hello', tokens=[DOC_TOKENS[0]], 
                     sentence_indexes=[(0,1)])
    assert value == _doc

    sleep(0.5)
    # One sentence many tokens
    value = test_api.usas("hello how are you it's")
    _doc = UCREL_Doc("hello how are you it's", tokens=DOC_TOKENS[:6], 
                     sentence_indexes=[(0,6)])
    assert value == _doc

    sleep(0.5)
    # Two sentences
    value = test_api.usas("hello how are you it's. Great day")
    _doc = UCREL_Doc("hello how are you it's. Great day", tokens=DOC_TOKENS, 
                     sentence_indexes=[(0,7), (7,9)])
    
    sleep(0.5)
    # Test the un-escaping of SGML entities
    value = test_api.usas("hello []")
    sgml_tokens = [UCREL_Token('hello', 'hello', 'NN1%', 'S1.1.1'), 
                   UCREL_Token('[', '[', '(', None), 
                   UCREL_Token(']', ']', ')', None)]
    assert value == UCREL_Doc("hello []", tokens=sgml_tokens, sentence_indexes=[(0,3)])

    sleep(0.5)
    value = test_api.usas("hello £100")
    sgml_tokens = [UCREL_Token('hello', 'hello', 'UH', 'Z4'), 
                   UCREL_Token('£100', '£100', 'NNU', 'I1')]
    assert value == UCREL_Doc("hello £100", tokens=sgml_tokens, sentence_indexes=[(0,2)])

    sleep(0.5)
    value = test_api.usas("hello <>")
    sgml_tokens = [UCREL_Token('hello', 'hello', 'UH', 'Z4'), 
                   UCREL_Token('<>', '<>', 'FO', 'Z99')]
    assert value == UCREL_Doc("hello <>", tokens=sgml_tokens, sentence_indexes=[(0,2)])

    sgml_tokens = [UCREL_Token('hello', 'hello', 'UH', 'Z4'),
                   UCREL_Token('&', '&', 'CC', 'Z5'),
                   UCREL_Token('another', 'another', 'DD1', 'A6.1-'),
                   UCREL_Token('£100', '£100', 'NNU', 'I1'),
                   UCREL_Token('<>', '<>', 'FO', 'Z99'),
                   UCREL_Token('[', '[', '(', None),
                   UCREL_Token(']', ']', ')', None),
                   UCREL_Token('André', 'andré', 'NP1', 'Z99'),
                   UCREL_Token('&', '&', 'CC', 'Z5')]

    sleep(0.5)
    value = test_api.usas("hello & another £100 <> [] André &")
    assert value == UCREL_Doc("hello & another £100 <> [] André &", tokens=sgml_tokens, 
                              sentence_indexes=[(0,9)])
    # MWE
    sleep(0.5)
    new_york_tokens = [UCREL_Token('hello', 'hello', 'UH', 'Z4'),
                       UCREL_Token('New', 'new', 'NP1', 'Z2', '2.2.1'),
                       UCREL_Token('York', 'york', 'NP1', 'Z2', '2.2.2')]
    value = test_api.usas("hello New York")
    assert value == UCREL_Doc("hello New York", tokens=new_york_tokens, 
                              sentence_indexes=[(0,3)])

SERVER_ADDRESS = 'http://ucrel-api.lancaster.ac.uk'
ENDPOINT = '/cgi-bin/usas.pl'
TAGSET = 'c7'
TEST_API = UCREL_API(email='a.moore@lancaster.ac.uk', 
                     server_address=SERVER_ADDRESS)

@responses.activate
def test__timeout_ucrel_post_request():
    responses.add('POST', f'{SERVER_ADDRESS}{ENDPOINT}', body=requests.exceptions.Timeout())
    with pytest.raises(requests.exceptions.Timeout):
        TEST_API._ucrel_post_request(ENDPOINT, 'hello', tagset=TAGSET)
    return None

@responses.activate
def test__status_code_ucrel_post_request():
    responses.add('POST', f'{SERVER_ADDRESS}{ENDPOINT}', status=301)
    with pytest.raises(requests.exceptions.HTTPError):
        TEST_API._ucrel_post_request(ENDPOINT, 'hello', tagset=TAGSET)
    return None

@responses.activate
def test__general_exception_ucrel_post_request():
    responses.add('POST', f'{SERVER_ADDRESS}{ENDPOINT}', body=Exception('Unknown error.'))
    with pytest.raises(Exception):
        TEST_API._ucrel_post_request(ENDPOINT, 'hello', tagset=TAGSET)
    return None

def test__escaping_sgml_entities_ucrel_post_request():
    # Test the escaping of SGML entities
    sleep(0.5)
    hello_square_brackets = ('\n<s>\n</s>\n<s>\n'
                             'hello\tNN1%\thello\tS1.1.1 \n'
                             '&lsqb;\t(\t&lsqb;\t\n'
                             '&rsqb;\t)\t&rsqb;\t\n'
                             '</s>\n')
    assert TEST_API._ucrel_post_request(ENDPOINT, "hello []", tagset=TAGSET) == hello_square_brackets

    sleep(0.5)
    hello_pound_sign = ('\n<s>\n</s>\n<s>\n'
                        'hello\tUH\thello\tZ4 \n'
                        '&pound;100\tNNU\t&pound;100\tI1 \n'
                        '</s>\n')
    assert TEST_API._ucrel_post_request(ENDPOINT, "hello £100", tagset=TAGSET) == hello_pound_sign

    sleep(0.5)
    hello_greater_less_sign = ('\n<s>\n</s>\n<s>\n'
                               'hello\tUH\thello\tZ4 \n'
                               '&lt;&gt;\tFO\t&lt;&gt;\tZ99 \n'
                               '</s>\n')
    assert TEST_API._ucrel_post_request(ENDPOINT, "hello <>", tagset=TAGSET) == hello_greater_less_sign
    
    sleep(0.5)
    all_sgml_values = ('\n<s>\n</s>\n<s>\n'
                       'hello\tUH\thello\tZ4 \n'
                       '&amp;\tCC\t&amp;\tZ5 \n'
                       'another\tDD1\tanother\tA6.1- N5++ \n'
                       '&pound;100\tNNU\t&pound;100\tI1 \n'
                       '&lt;&gt;\tFO\t&lt;&gt;\tZ99 \n'
                       '&lsqb;\t(\t&lsqb;\t\n'
                       '&rsqb;\t)\t&rsqb;\t\n'
                       'Andr&eacute;\tNP1\tandr&eacute;\tZ99 \n'
                       '&amp;\tCC\t&amp;\tZ5 \n'
                       '</s>\n')
    sgml_text = "hello & another £100 <> [] André &"
    assert TEST_API._ucrel_post_request(ENDPOINT, sgml_text, tagset=TAGSET) == all_sgml_values