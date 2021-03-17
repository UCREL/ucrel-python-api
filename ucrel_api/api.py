# AUTOGENERATED! DO NOT EDIT! File to edit: module_notebooks/00_api.ipynb (unless otherwise specified).

__all__ = ['UCREL_API']

# Cell

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
        [http://ucrel-api.lancaster.ac.uk/](http://ucrel-api.lancaster.ac.uk/)
        3. **port**: The port to the server e.g. 8080. Can be left as empty string
        if port number is not required.
        4. **timeout**: The amount of time to allow each request to take before raising
        a [`requests.exceptions.Timeout`](https://requests.readthedocs.io/en/latest/api/#requests.Timeout)
        '''
        self.email = email
        self.server_address = server_address
        self.port = port
        self.timeout = timeout

    def usas(self, text: str, tagset: str = 'c7') -> UCREL_Doc:
        '''
        Might be a good idea to allow as a optional argument a
        session object so that someone can keep a session going
        over multiple calls and thus keep credientials over multiple
        calls etc. Probably be best to do this way and have a method
        in the future that will allow you to create a session that
        has been authenticated.

        Need to encode SGML entities before sending

        This function returns the USAS tags for the given text.

        1. **text**: The text to be tagged by USAS.
        2. **tagset**: The tagset to be used by USAS. Either `c5` or `c7`.

        **returns**
        '''
        endpoint = '/cgi-bin/usas.pl'
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
                'tagset': tagset, 'style': 'vert', 'text': escaped_text}
        headers = {'Accept':'text/plain; charset=utf-8',
                   'Content-Type': 'text/plain; charset=utf-8'}
        post_response =  requests.post(url, files=data, timeout=self.timeout,
                                       headers=headers)
        usas_data = post_response.text

        ucrel_tokens: List[UCREL_Token] = []
        sentence_indexes: List[Tuple[int, int]] = []
        token_index = 0
        last_sentence_index = 0
        for token_line in usas_data.strip().split('\n'):
            usas_output_data = token_line.split()
            # If length is less than 4 it is normally the end of
            # the output
            if len(usas_output_data) < 4:
                continue
            ref_num, decision_id, pos_tag, token_text = usas_output_data[:4]
            # Check if the token is a sentence break
            if re.match(r'^-+$', token_text):
                if token_index != 0:
                    sentence_indexes.append((last_sentence_index, token_index))
                    last_sentence_index = token_index
                continue
            # un-escape token text from SGML entities
            token_text = self._sgml_entity_un_escape(token_text)
            # Check to see if USAS tag(s) exist
            if len(usas_output_data) == 4:
                ucrel_token = UCREL_Token(token_text, pos_tag)
            else:
                usas_tags = usas_output_data[4:]
                ucrel_token = UCREL_Token(token_text, pos_tag, usas_tags[0])
            token_index += 1
            ucrel_tokens.append(ucrel_token)
        if last_sentence_index != token_index:
            sentence_indexes.append((last_sentence_index, token_index))
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