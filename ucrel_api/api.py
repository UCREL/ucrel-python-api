# AUTOGENERATED! DO NOT EDIT! File to edit: module_notebooks/00_api.ipynb (unless otherwise specified).

__all__ = ['UCREL_API']

# Cell

import functools
from typing import Optional, List, Tuple
import re
from xml.sax import saxutils

import requests

from .ucrel_doc import UCREL_Doc, UCREL_Token

class UCREL_API():

    SGML_ENTITY_MAPPER = {'£': '&pound;',
                          'é': '&eacute;', '<': '&lt;',
                          '>': '&gt;', '[': '&lsqb;',
                          ']': '&rsqb;'}
    REVERSE_SGML_ENTITY_MAPPER = {v: k for k, v in SGML_ENTITY_MAPPER.items()}

    @classmethod
    def _sgml_entity_escape(cls, text: str) -> str:
        '''
        The SGML entities that are escaped are those found in
        the [CLAWS input/output format guidelines.](http://ucrel.lancs.ac.uk/claws/format.html)

        1. **text**: Text to escape

        **returns** The text escaped from SGML entities
        '''
        # Need to escape & first as it is contained in the other escaped
        # entities
        if '&' in text:
            text = text.replace('&', '&amp;')
        for entity, escaped_entity in cls.SGML_ENTITY_MAPPER.items():
            if entity in text:
                text = text.replace(entity, escaped_entity)
        return text

    @classmethod
    def _sgml_entity_un_escape(cls, text: str) -> str:
        '''
        The SGML entities that are un-escaped are those found in
        the [CLAWS input/output format guidelines.](http://ucrel.lancs.ac.uk/claws/format.html)

        1. **text**: Text to un-escape

        **returns** The text un-escaped from SGML entities
        '''
        if '&amp;' in text:
            text = text.replace('&amp;', '&')
        for escaped_entity, entity in cls.REVERSE_SGML_ENTITY_MAPPER.items():
            if escaped_entity in text:
                text = text.replace(escaped_entity, entity)
        return text

    def __init__(self, email: str, server_address: str,
                 port: str = '', timeout: int = 60) -> None:
        '''
        Creates a UCREL API instance that is used to call the UCREL Tool chain.

        1. **email**: Email address of the user. This is used to identify the user
        calling the UCREL Tool Chain API.
        2. **server_address**: The address of the UCREL Tool Chain e.g.
        [http://ucrel-api.lancaster.ac.uk](http://ucrel-api.lancaster.ac.uk)
        3. **port**: The port to the server e.g. 8080. Can be left as empty string
        if port number is not required.
        4. **timeout**: The amount of time to allow each request to take before raising
        a [`requests.exceptions.Timeout`](https://requests.readthedocs.io/en/latest/api/#requests.Timeout)
        '''
        self.email = email
        self.server_address = server_address
        self.port = port
        self.timeout = timeout

    def _ucrel_post_request(self, endpoint: str, text: str, **data_kwargs) -> str:
        '''
        1. **endpoint**: The POST endpoint of the UCREL Tool Chain sevrer
        to call. The endpoint is expected to require `text` key in the
        multipart form data.
        2. **text**: The text to be processed by the given `endpoint`.
        3. **data_kwargs**: Optional, additional `key: value` data to
        be sent with the multipart form data.

        **returns**: The string response from the UCREL Tool Chain
        server after calling the given `endpoint` with the given `text`
        and any `data_kwargs`.

        **raises requests.exceptions.Timeout**: If the response from the POST request
        takes longer than `self.timeout`.
        **raises requests.exceptions.HTTPError**: If anything other than a status code 200
        is returned from the `endpoint`.
        **raises Exception**: If any error occurs while processing the POST request
        to the `endpoint`.
        '''
        url = f'{self.server_address}{endpoint}'
        if self.port:
            url = f'{self.server_address}:{self.port}{endpoint}'
        # Escape the SGML entities
        text = text.strip()
        escaped_text = self._sgml_entity_escape(text)
        # Type here refers to the fact we want to use the REST API
        # Style refers to the output type, in this case we use verticical
        # as the verticial format returns the most output e.g. all possible tags
        # and split into sentences.
        data = {'type': 'rest', 'email': self.email,
                **data_kwargs, 'style': 'tab',  'text': escaped_text}
        headers = {'Accept':'text/plain; charset=utf-8',
                   'Content-Type': 'text/plain; charset=utf-8'}
        try:
            post_response = requests.post(url, files=data, timeout=self.timeout,
                                          headers=headers)
            status_code = post_response.status_code
            if post_response.status_code != 200:
                error_msg = (f'Raised a status code of {status_code}. '
                             'Can only accept code 200.')
                raise requests.exceptions.HTTPError(error_msg)
            return post_response.text
        except requests.exceptions.Timeout:
            error_message = (f'URL: {url}. Failed due to a timeout for the ')
            raise requests.exceptions.Timeout(error_message)
        except Exception as e:
            raise type(e)(f'URL: {url}\nError: {str(e)}')

    def usas(self, text: str, tagset: str = 'c7') -> UCREL_Doc:
        '''
        1. **text**: The text to be tagged by USAS.
        2. **tagset**: The tagset to be used by USAS. Either `c5` or `c7`.

        **returns**: A `UCREL_Doc` representing the text and the
        lingustic attributes that are generared from tagging it
        with [USAS.](http://ucrel.lancs.ac.uk/usas/)
        '''
        # Call USAS endpoint.
        usas_endpoint = '/cgi-bin/usas.pl'
        usas_data = self._ucrel_post_request(usas_endpoint, text, tagset=tagset)
        usas_data = usas_data.strip()
        if not usas_data:
            return UCREL_Doc(text, tokens=[], sentence_indexes=[])

        ucrel_tokens: List[UCREL_Token] = []

        sentence_indexes: List[Tuple[int, int]] = []
        token_index = 0
        last_sentence_index = 0



        for sentence in usas_data.split('<s>'):
            sentence = sentence.strip().rstrip('</s>')
            if not sentence:
                continue
            for token_values in sentence.split('\n'):
                token_values = token_values.strip()
                if not token_values:
                    continue

                token_values = token_values.split('\t')
                token_text, pos_tag, lemma, usas_tags = None, None, None, None
                # Punctuation does not get tagged with USAS tags.
                if len(token_values) == 3:
                    token_text, pos_tag, lemma = token_values
                else:
                    token_text, pos_tag, lemma, usas_tags = token_values
                token_text = self._sgml_entity_un_escape(token_text)
                lemma = self._sgml_entity_un_escape(lemma)
                usas_tag = None
                mwe_tag = None
                if usas_tags is not None:
                    # Most likely USAS tag
                    usas_tag = usas_tags.split()[0]
                    # Get the MWE tag
                    usas_and_mwe = usas_tag.split('[i')
                    if len(usas_and_mwe) == 2:
                        usas_tag, mwe_tag = usas_and_mwe

                ucrel_tokens.append(UCREL_Token(token_text, lemma=lemma,
                                                pos_tag=pos_tag,
                                                usas_tag=usas_tag, mwe_tag=mwe_tag))
                token_index += 1
            sentence_indexes.append((last_sentence_index, token_index))
            last_sentence_index = token_index

        return UCREL_Doc(text, tokens=ucrel_tokens, sentence_indexes=sentence_indexes)

    def __repr__(self) -> str:
        '''
        String representation of the UCREL API instance, format:

        UCREL API, server address {self.server_address}, port {self.port}, timeout {self.timeout}

        `, port {self.port}` -- will only exist in string if `self.port!=''`
        '''
        base_repr = f'UCREL API, server address {self.server_address}'
        if self.port:
            base_repr += f', port {self.port}'
        base_repr += f', timeout {self.timeout} seconds'
        return base_repr