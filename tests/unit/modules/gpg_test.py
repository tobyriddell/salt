# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Jayesh Kariya <jayeshk@saltstack.com>`
'''

# Import Python Libs
from __future__ import absolute_import

# Import Salt Testing Libs
from salttesting import TestCase, skipIf
from salttesting.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

from salttesting.helpers import ensure_in_syspath
from mock import mock_open

ensure_in_syspath('../../')

# Import Salt Libs
from salt.modules import gpg
from salt.exceptions import SaltInvocationError

gpg.__salt__ = {}

RET = [{'created': '2014-07-25',
        'fingerprint': u'F321F',
        'keyLength': u'1024',
        'keyid': u'3F0C8E90D459D89A',
        'ownerTrust': 'Ultimately Trusted',
        'trust': 'u',
        'uids': [u'Autogenerated Key (Generated by SaltStack)']}]


class Mockgnupg(object):
    '''
    Mock smtplib class
    '''
    __version__ = '1.3.1'
    fingerprint = u'F321F'
    counts = {}
    count = ''
    imported = False
    imported_rsa = False
    results = [{'ok': '1', 'fingerprint': u'F321F'}]
    data = True
    trust_level = None
    ok = True
    unchanged = False
    not_imported = False

    class GPG(object):
        '''
        Mock smtplib class
        '''
        def __init__(self, gnupghome='/tmp/salt/.gnupg',
                     homedir='/tmp/salt/.gnupg'):
            self.gnupghome = gnupghome
            self.homedir = homedir
            self.text = None
            self.keyserver = None
            self.kwargs = None
            self.obj = None
            self.fingerprints = None
            self.keyserver = None
            self.secret = None
            self.keyids = None
            self.default_key = None
            self.recipients = None
            self.passphrase = None

        def search_keys(self, text, keyserver):
            '''
            Mock of search_keys method
            '''
            self.text = text
            self.keyserver = keyserver
            return RET

        def gen_key_input(self, **kwargs):
            '''
            Mock of gen_key_input method
            '''
            self.kwargs = kwargs
            return Mockgnupg

        def gen_key(self, obj):
            '''
            Mock of gen_key method
            '''
            self.obj = obj
            return Mockgnupg

        def list_keys(self, obj):
            '''
            Mock of list_keys method
            '''
            self.obj = obj
            return RET

        def delete_keys(self, fingerprints, secret=False):
            '''
            Mock of delete_keys method
            '''
            self.fingerprints = fingerprints
            self.secret = secret
            return 'ok'

        def import_keys(self, text):
            '''
            Mock of import_keys method
            '''
            self.text = text
            return Mockgnupg

        def export_keys(self, keyids, secret):
            '''
            Mock of export_keys method
            '''
            self.secret = secret
            self.keyids = keyids
            return (keyids, secret)

        def recv_keys(self, keyserver, *keyids):
            '''
            Mock of recv_keys method
            '''
            self.keyserver = keyserver
            self.keyids = keyids
            return Mockgnupg

        def sign(self, text, default_key, passphrase):
            '''
            Mock of sign method
            '''
            self.text = text
            self.default_key = default_key
            self.passphrase = passphrase
            return Mockgnupg

        def verify(self, text):
            '''
            Mock of verify method
            '''
            self.text = text
            return Mockgnupg

        def encrypt(self, text, recipients, passphrase):
            '''
            Mock of encrypt method
            '''
            self.text = text
            self.recipients = recipients
            self.passphrase = passphrase
            return Mockgnupg

        def decrypt(self, text, passphrase):
            '''
            Mock of decrypt method
            '''
            self.text = text
            self.passphrase = passphrase
            return Mockgnupg

gpg.gnupg = Mockgnupg()


@skipIf(NO_MOCK, NO_MOCK_REASON)
class GpgTestCase(TestCase):
    '''
    TestCase for salt.modules.gpg
    '''
    # 'search_keys' function tests: 1

    def test_search_keys(self):
        '''
        Tests if it search keys from keyserver.
        '''
        ret = [{'keyid': u'3F0C8E90D459D89A',
                'uids': [u'Autogenerated Key (Generated by SaltStack)']}]
        mock = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'user.info': mock}):
            self.assertListEqual(gpg.search_keys('user@example.com',
                                                 user='username'), ret)

            gpg.GPG_1_3_1 = True
            self.assertRaises(SaltInvocationError, gpg.search_keys,
                              'user@example.com')

    # 'list_keys' function tests: 1

    def test_list_keys(self):
        '''
        Tests if it list keys in GPG keychain
        '''
        ret = [{'fingerprint': u'F321F', 'keyid': u'3F0C8E90D459D89A',
                'trust': 'Ultimately Trusted',
                'uids': [u'Autogenerated Key (Generated by SaltStack)']}]

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertListEqual(gpg.list_keys(), ret)

    # 'list_secret_keys' function tests: 1

    def test_list_secret_keys(self):
        '''
        Tests if it list secret keys in GPG keychain
        '''
        ret = [{'fingerprint': u'F321F', 'keyid': u'3F0C8E90D459D89A',
                'trust': 'Ultimately Trusted',
                'uids': [u'Autogenerated Key (Generated by SaltStack)']}]

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertListEqual(gpg.list_secret_keys(), ret)

    # 'create_key' function tests: 1

    def test_create_key(self):
        '''
        Tests if it create a key in the GPG keychain
        '''
        ret = {'res': True, 'fingerprint': u'F321F',
               'message': 'GPG key pair successfully generated.'}

        ret1 = {'fingerprint': '', 'res': False,
                'message': 'gpg_passphrase not available in pillar.'}

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        mock_item = MagicMock(return_value=False)
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user,
                                       'pillar.item': mock_item}):
            self.assertDictEqual(gpg.create_key(), ret)

            self.assertDictEqual(gpg.create_key(use_passphrase=True), ret1)

    # 'delete_key' function tests: 1

    def test_delete_key(self):
        '''
        Tests if it delete a key from the GPG keychain
        '''
        ret = {'message': 'Only specify one argument, fingerprint or keyid',
               'res': False}

        ret1 = {'message': 'Required argument, fingerprint or keyid',
                'res': False}

        ret2 = {'message': ('Secret key exists, delete first'
                            ' or pass delete_secret=True.'), 'res': False}

        ret3 = {'message': ('Secret key for F321F deleted\nPublic'
                            ' key for F321F deleted'), 'res': True}

        ret4 = {'message': 'Key not available in keychain.', 'res': False}

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertDictEqual(gpg.delete_key(keyid='3FAD9F1E',
                                                fingerprint='53C'), ret)

            self.assertDictEqual(gpg.delete_key(), ret1)

            self.assertDictEqual(gpg.delete_key(keyid='3F0C8E90D459D89A'), ret2)

            self.assertDictEqual(gpg.delete_key(keyid='3F0C8E90D459D89A',
                                                delete_secret=True), ret3)

            self.assertDictEqual(gpg.delete_key(keyid='3F0C'), ret4)

    # 'get_key' function tests: 1

    def test_get_key(self):
        '''
        Tests if it get a key from the GPG keychain
        '''
        ret = {'fingerprint': u'F321F', 'keyid': u'3F0C8E90D459D89A',
               'trust': 'Ultimately Trusted',
               'uids': [u'Autogenerated Key (Generated by SaltStack)']}

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertFalse(gpg.get_key())

            self.assertDictEqual(gpg.get_key(keyid='3F0C8E90D459D89A'), ret)

    # 'get_secret_key' function tests: 1

    def test_get_secret_key(self):
        '''
        Tests if it get a secret key from the GPG keychain
        '''
        ret = {'fingerprint': u'F321F', 'keyid': u'3F0C8E90D459D89A',
               'trust': 'Ultimately Trusted',
               'uids': [u'Autogenerated Key (Generated by SaltStack)']}

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertFalse(gpg.get_secret_key())

            self.assertDictEqual(gpg.get_secret_key(keyid='3F0C8E90D459D89A'),
                                 ret)

    # 'import_key' function tests: 1

    def test_import_key(self):
        '''
        Tests if it import a key from text or file.
        '''
        ret = {'message': 'Unable to import key.', 'res': False}

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertRaises(SaltInvocationError, gpg.import_key)

            with patch('salt.utils.flopen', mock_open(read_data='')) as fp:
                fp.side_effect = IOError()
                self.assertRaises(SaltInvocationError, gpg.import_key,
                                  filename='/path/to/public-key-file')

            self.assertDictEqual(gpg.import_key(text='-BEGIN PGP PUBLIC KEY BLOCK-'), ret)

    # 'export_key' function tests: 1

    def test_export_key(self):
        '''
        Tests if it export a key from the GPG keychain
        '''
        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertTrue(gpg.export_key(keyids='3F0C8E90D459D89A'))

    # 'receive_keys' function tests: 1

    def test_receive_keys(self):
        '''
        Tests if it receive key(s) from keyserver and add them to keychain
        '''
        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user}):
            self.assertDictEqual(gpg.receive_keys(keys=['3F0C8E90D459D89A']),
                                 {'res': True,
                                  'message': ['Key F321F added to keychain'],
                                  'changes': {}})

    # 'trust_key' function tests: 1

    def test_trust_key(self):
        '''
        Tests if it set the trust level for a key in GPG keychain
        '''
        ret = {'message': 'Only specify one argument, fingerprint or keyid',
               'res': False}

        ret1 = {'message': 'KeyID 3F0C8 not in GPG keychain', 'res': False}

        ret2 = {'message': 'Required argument, fingerprint or keyid',
                'res': False}

        ret3 = ('ERROR: Valid trust levels - expired,unknown,'
                'not_trusted,marginally,fully,ultimately')

        ret4 = {'res': False,
                'message': 'Fingerprint not found for keyid 3F0C8E90D459D89A'}

        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        mock_cmd = MagicMock(return_value={'retcode': 1, 'stderr': 'error'})
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user,
                                       'cmd.run_all': mock_cmd}):
            self.assertDictEqual(gpg.trust_key(keyid='3F0C8E90D459D89A',
                                               fingerprint='53C'), ret)

            self.assertDictEqual(gpg.trust_key(keyid='3F0C8'), ret1)

            self.assertDictEqual(gpg.trust_key(), ret2)

            self.assertEqual(gpg.trust_key(fingerprint='53C9'), ret3)

            self.assertEqual(gpg.trust_key(fingerprint='53C96',
                                           trust_level='not_trusted'),
                             {'res': False, 'message': 'error'})

        with patch.object(gpg, 'get_key', MagicMock(return_value=RET)):
            self.assertDictEqual(gpg.trust_key(keyid='3F0C8E90D459D89A'),
                                 ret4)

    # 'sign' function tests: 1

    def test_sign(self):
        '''
        Tests if it sign message or file
        '''
        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        mock_pillar = MagicMock(return_value=False)
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user,
                                       'pillar.item': mock_pillar}):
            self.assertRaises(SaltInvocationError, gpg.sign,
                              use_passphrase=True)

            self.assertRaises(SaltInvocationError, gpg.sign)

            self.assertTrue(gpg.sign(text='Hello there.  How are you?'))

    # 'verify' function tests: 1

    def test_verify(self):
        '''
        Tests if it verify a message or file
        '''
        ret = {'message': 'The signature could not be verified.', 'res': False}
        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        mock_pillar = MagicMock(return_value=False)
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user,
                                       'pillar.item': mock_pillar}):
            self.assertRaises(SaltInvocationError, gpg.verify)

            self.assertDictEqual(gpg.verify(text='Hello there.  How are you?'),
                                 ret)

    # 'encrypt' function tests: 1

    def test_encrypt(self):
        '''
        Tests if it encrypt a message or file
        '''
        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        mock_pillar = MagicMock(return_value=False)
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user,
                                       'pillar.item': mock_pillar}):
            self.assertRaises(SaltInvocationError, gpg.encrypt,
                              use_passphrase=True)

            self.assertRaises(SaltInvocationError, gpg.encrypt)

            self.assertDictEqual(gpg.encrypt(text='Hello there.  How are you?'),
                                 {'comment': True, 'res': True})

    # 'decrypt' function tests: 1

    def test_decrypt(self):
        '''
        Tests if it decrypt a message or file
        '''
        mock_conf = MagicMock(return_value='')
        mock_user = MagicMock(return_value={'home': 'salt'})
        mock_pillar = MagicMock(return_value=False)
        with patch.dict(gpg.__salt__, {'config.option': mock_conf,
                                       'user.info': mock_user,
                                       'pillar.item': mock_pillar}):
            self.assertRaises(SaltInvocationError, gpg.decrypt,
                              use_passphrase=True)

            self.assertRaises(SaltInvocationError, gpg.decrypt)

            self.assertDictEqual(gpg.decrypt(text='Hello there.  How are you?'),
                                 {'comment': True, 'res': True})


if __name__ == '__main__':
    from integration import run_tests
    run_tests(GpgTestCase, needs_daemon=False)
