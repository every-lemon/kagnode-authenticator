"""Recovery codes remain encrypted, explicitly consumed, and backup-compatible."""
import base64
import json
import sqlite3
import tempfile
import unittest
import uuid
from cryptography.fernet import Fernet
from authentactor.server import create_app, derive_key, KDF


class BackupCodeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.app = create_app(directory.name)
        self.client = self.app.test_client()
        self.email = 'owner@backup.test'
        self.password = 'Disposable-backup-code-tests!2030'
        self.headers = {'X-Requested-With': 'Authentactor'}
        response = self.client.post('/api/setup', json={'email':self.email,'password': self.password}, headers=self.headers)
        self.headers['X-CSRF-Token'] = response.json['csrf']

    def send(self, path, body, method='POST', headers=None):
        if path in ('/setup', '/unlock'):
            body = {**body, 'email': self.email}
        return self.client.open('/api'+path, method=method, json=body, headers=self.headers if headers is None else headers)

    def add(self, codes='FIRST-1234-ABCD\nSECOND 5678 EFGH', **extra):
        response = self.send('/items', {'name': 'Example recovery', 'backup_codes': codes, **extra})
        self.assertEqual(response.status_code, 201, response.json)
        return response.json['id']

    def detail(self, identifier):
        return self.client.get('/api/items/'+identifier).json['item']

    def usage(self, identifier, code, used):
        return self.send(f'/items/{identifier}/backup-codes/{code}/usage', {'used': used})

    def test_code_only_item_is_encrypted_and_summaries_never_contain_codes(self):
        identifier = self.add()
        item = self.detail(identifier)
        self.assertEqual([c['code'] for c in item['backup_codes']], ['FIRST-1234-ABCD', 'SECOND 5678 EFGH'])
        for code in item['backup_codes']:
            uuid.UUID(code['id'])
            self.assertFalse(code['used'])
        response = self.client.get('/api/items')
        summary = response.json['items'][0]
        self.assertNotIn('backup_codes', summary)
        self.assertNotIn('FIRST-1234-ABCD', response.text)
        self.assertEqual((summary['backup_codes_total'], summary['backup_codes_remaining']), (2, 2))
        self.assertFalse(summary['has_password'])
        path = self.app.extensions['vault_testing']['db_path']
        self.assertNotIn(b'FIRST-1234-ABCD', path.read_bytes())
        self.assertNotIn(b'FIRST-1234-ABCD', self.client.get('/api/backup').data)

    def test_usage_is_explicit_idempotent_and_reversible(self):
        identifier = self.add()
        code = self.detail(identifier)['backup_codes'][0]['id']
        # Reading the code never consumes it.
        self.detail(identifier)
        self.assertFalse(self.detail(identifier)['backup_codes'][0]['used'])
        used = self.usage(identifier, code, True)
        self.assertEqual(used.json['remaining'], 1)
        first_time = used.json['used_at']
        self.assertEqual(self.usage(identifier, code, True).json['used_at'], first_time)
        response = self.usage(identifier, code, False)
        self.assertEqual(response.json['remaining'], 2)
        self.assertIsNone(response.json['used_at'])

    def test_multiline_edit_and_legacy_clients_preserve_used_code_metadata(self):
        identifier = self.add(password='An existing password')
        item = self.detail(identifier)
        code = item['backup_codes'][0]['id']
        self.usage(identifier, code, True)
        response = self.send('/items/'+identifier, {'name': 'Renamed', 'password': 'An existing password'}, 'PUT')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.detail(identifier)['backup_codes'][0]['used'])
        response = self.send('/items/'+identifier, {'name': 'Renamed', 'backup_codes': 'FIRST-1234-ABCD\nNEW-9012-IJKL'}, 'PUT')
        self.assertEqual(response.status_code, 200)
        codes = self.detail(identifier)['backup_codes']
        self.assertEqual(codes[0]['id'], code)
        self.assertTrue(codes[0]['used'])
        self.assertFalse(codes[1]['used'])

    def test_locked_or_cross_site_clients_cannot_read_or_change_codes(self):
        identifier = self.add()
        code = self.detail(identifier)['backup_codes'][0]['id']
        path = f'/items/{identifier}/backup-codes/{code}/usage'
        self.assertEqual(self.send(path, {'used': True}, headers={'X-Requested-With': 'Authentactor'}).status_code, 403)
        self.assertEqual(self.send(path, {'used': True}, headers={**self.headers, 'Origin': 'https://untrusted.example'}).status_code, 403)
        self.send('/lock', {})
        self.assertEqual(self.client.get('/api/items/'+identifier).status_code, 401)
        self.assertEqual(self.send(path, {'used': True}).status_code, 401)

    def test_malformed_codes_or_usage_do_not_modify_existing_item(self):
        identifier = self.add()
        before = self.detail(identifier)
        for invalid in [None, {}, 42, [''], ['bad\x00code'], ['bad\tcode'], ['same', 'same'], ['x'*513], [str(i) for i in range(101)], [{'code': 'valid-code', 'used': 'yes'}], [{'code': 'valid-code', 'id': 'invalid'}]]:
            response = self.send('/items/'+identifier, {'name': 'Changed', 'backup_codes': invalid}, 'PUT')
            self.assertEqual(response.status_code, 400, invalid)
            self.assertEqual(self.detail(identifier), before)
        code = before['backup_codes'][0]['id']
        for body in [{'used': 'true'}, {'used': 1}, {}, {'used': True, 'extra': True}]:
            self.assertEqual(self.send(f'/items/{identifier}/backup-codes/{code}/usage', body).status_code, 400)
        self.assertEqual(self.usage(identifier, str(uuid.uuid4()), True).status_code, 404)
        self.assertEqual(self.detail(identifier), before)

    def test_new_backup_round_trip_preserves_codes_and_used_state(self):
        identifier = self.add()
        code = self.detail(identifier)['backup_codes'][0]['id']
        self.usage(identifier, code, True)
        before = self.detail(identifier)['backup_codes']
        backup = self.client.get('/api/backup').json
        self.send('/items/'+identifier, {}, 'DELETE')
        response = self.send('/restore', {'backup': backup, 'password': self.password})
        self.assertEqual(response.json['imported'], 1)
        self.assertEqual(self.detail(identifier)['backup_codes'], before)
        self.assertEqual(self.send('/restore', {'backup': backup, 'password': self.password}).json['skipped'], 1)

    def test_original_backup_without_code_field_still_restores(self):
        identifier = self.add(password='Original password')
        item = self.detail(identifier)
        item.pop('backup_codes')
        item['id'] = str(uuid.uuid4())
        salt = b'old-backup-salt!'
        backup = {'format': 'authentactor-encrypted-v1', 'version': 1, 'kdf': KDF,
                  'salt': base64.b64encode(salt).decode(), 'payload': Fernet(derive_key(self.password, salt)).encrypt(json.dumps({'items': [item]}).encode()).decode()}
        response = self.send('/restore', {'backup': backup, 'password': self.password})
        self.assertEqual(response.json['imported'], 1)
        self.assertEqual(self.detail(item['id'])['backup_codes'], [])

    def test_master_password_rotation_and_restart_retain_code_state(self):
        identifier = self.add()
        code = self.detail(identifier)['backup_codes'][0]['id']
        self.usage(identifier, code, True)
        new_password = self.password+'-changed'
        response = self.send('/change-password', {'current': self.password, 'password': new_password})
        self.assertEqual(response.status_code, 200)
        directory = self.app.extensions['vault_testing']['db_path'].parent
        restarted = create_app(directory).test_client()
        response = restarted.post('/api/unlock', json={'email':self.email,'password': new_password}, headers={'X-Requested-With': 'Authentactor'})
        self.assertEqual(response.status_code, 200)
        codes = restarted.get('/api/items/'+identifier).json['item']['backup_codes']
        self.assertEqual(codes[0]['id'], code)
        self.assertTrue(codes[0]['used'])

    def test_original_item_without_code_field_can_be_read_and_edited(self):
        identifier = self.add(password='Original password')
        token = next(iter(self.app.extensions['vault_testing']['sessions'].values()))['key']
        path = self.app.extensions['vault_testing']['db_path']
        with sqlite3.connect(path) as db:
            payload = db.execute('SELECT payload FROM accounts').fetchone()[0]
            vault = json.loads(Fernet(token).decrypt(payload))
            vault['items'][0].pop('backup_codes')
            db.execute('UPDATE accounts SET payload=?', (Fernet(token).encrypt(json.dumps(vault).encode()),))
        summary = self.client.get('/api/items').json['items'][0]
        self.assertEqual(summary['backup_codes_total'], 0)
        self.assertEqual(self.send('/items/'+identifier, {'name': 'Legacy edit', 'password': 'Original password'}, 'PUT').status_code, 200)
        self.assertEqual(self.detail(identifier)['backup_codes'], [])
