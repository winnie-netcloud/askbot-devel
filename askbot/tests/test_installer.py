from askbot.tests.utils import AskbotTestCase
from askbot.deployment import AskbotSetup
from askbot.deployment.parameters import *

from unittest.mock import patch

class MockInput:
  def __init__(self, *args):
    self.return_values = iter(args)

  def __call__(self, *args):
    value = next(self.return_values)
    #print(f'MockInput called with >>>{args}<<<; answering >>>{value}<<<', file=sys.stderr)
    return value


## Database config related tests
class DbConfigManagerTest(AskbotTestCase):

    def setUp(self):
        self.installer = AskbotSetup()
        self.parser = self.installer.parser

    def test_get_options(self):
        default_opts = self.parser.parse_args([])
        default_dict = vars(default_opts)

    def test_db_configmanager(self):
        manager = DbConfigManager(interactive=False, verbosity=0)
        new_empty = lambda:dict([(k,None) for k in manager.keys])

        parameters = new_empty()  # includes ALL database parameters
        self.assertGreater(len(parameters), 0)

        engines = manager._catalog['database_engine'].database_engines
        self.assertGreater(len(engines), 0)

        # with interactive=False ConfigManagers (currently) raise an exception
        # if a required parameter is not set or not acceptable
        # the ConfigManager must trip over missing/empty database settings
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIs(type(e), ValueError)


class DatabaseEngineTest(AskbotTestCase):

    def setUp(self):
        self.installer = AskbotSetup()
        self.parser = self.installer.parser

    def test_database_engine(self):
        manager = DbConfigManager(interactive=False, verbosity=0)
        new_empty = lambda: dict([(k, None) for k in manager.keys])


        # DbConfigManager is supposed to test database_engine first
        # here: engine is NOT acceptable and name is NOT acceptable
        parameters = new_empty() # includes ALL database parameters
        try:
            manager.complete(parameters)
        except ValueError as e:
            self.assertIn('database_engine', str(e))

        # With a database_engine set, users must provide a database_name
        # here: engine is acceptable and name is NOT acceptable
        engines = manager._catalog['database_engine'].database_engines
        parameters = {'database_engine': None, 'database_name': None}
        caught_exceptions = 0
        for db_type in [e[0] for e in engines]:
            parameters['database_engine'] = db_type
            try:
                manager.complete(parameters)
            except ValueError as ve:
                caught_exceptions += 1
                self.assertIn('database_name', str(ve))
        self.assertEquals(caught_exceptions, len(engines))

        # here: engine is not acceptable and name is acceptable
        parameters = {'database_engine': None, 'database_name': 'acceptable_value'}
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIn('database_engine', str(e))

        # here: engine is acceptable and name is acceptable
        acceptable_engine = manager._catalog['database_engine'].database_engines[0][0]
        parameters = {'database_engine': acceptable_engine, 'database_name': 'acceptable_value'}
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIsNone(e)

    # at the moment, the  parameter parse does not have special code for
    # mysql and oracle, so we do not provide dedicated tests for them
    def test_database_postgres(self):
        manager = DbConfigManager(interactive=False, verbosity=0)
        new_empty = lambda: dict([(k, None) for k in manager.keys])
        parameters = new_empty()
        parameters['database_engine'] = 1

        acceptable_answers = {
            'database_name': 'testDB',
            'database_user': 'askbot',
            'database_password': 'd34db33f',
        }
        expected_issues = acceptable_answers.keys()
        met_issues = set()
        for i in expected_issues:
            e = None
            try:
                manager.complete(parameters)
            except ValueError as ve:
                e = ve
                matches = [issue for issue in expected_issues if issue in str(e)]
                self.assertEqual(len(matches), 1, str(e))
            self.assertIs(type(e), ValueError)

            issue = matches[0]
            cnt_old = len(met_issues)
            met_issues.update({issue})
            cnt_new = len(met_issues)
            self.assertNotEqual(cnt_new, cnt_old)
            parameters[issue] = acceptable_answers[issue]
        self.assertEqual(len(expected_issues), len(met_issues))
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIsNone(e)

    def test_database_sqlite(self):
        manager = DbConfigManager(interactive=False, verbosity=0)
        new_empty = lambda: dict([(k, None) for k in manager.keys])
        parameters = new_empty()
        parameters['database_engine'] = 2

        acceptable_answers = {
            'database_name': 'testDB',
        }
        expected_issues = acceptable_answers.keys()
        met_issues = set()
        for i in expected_issues:
            e = None
            try:
                manager.complete(parameters)
            except ValueError as ve:
                e = ve
                matches = [issue for issue in expected_issues if issue in str(e)]
                self.assertEqual(len(matches), 1, str(e))
            self.assertIs(type(e), ValueError)

            issue = matches[0]
            cnt_old = len(met_issues)
            met_issues.update({issue})
            cnt_new = len(met_issues)
            self.assertNotEqual(cnt_new, cnt_old)
            parameters[issue] = acceptable_answers[issue]
        self.assertEqual(len(expected_issues), len(met_issues))
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIsNone(e)

## Cache config related tests
class CacheEngineTest(AskbotTestCase):

    def setUp(self):
        self.installer = AskbotSetup()
        self.parser = self.installer.parser

    @staticmethod
    def _setUpTest():
        manager = CacheConfigManager(interactive=False, verbosity=0)
        engines = manager._catalog['cache_engine'].cache_engines
        new_empty = lambda: dict([(k, None) for k in manager.keys])
        return manager, engines, new_empty

    @staticmethod
    def run_complete(manager, parameters):
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        return e

    def test_cache_configmanager(self):
        manager, engines, new_empty = self._setUpTest()

        parameters = new_empty()  # includes ALL cache parameters
        self.assertGreater(len(parameters), 0)
        self.assertGreater(len(engines), 0)

        # with interactive=False ConfigManagers (currently) raise an exception
        # if a required parameter is not set or not acceptable
        # the ConfigManager must trip over missing/empty cache settings
        parameters = {'cache_engine': None}
        e = self.run_complete(manager, parameters)
        self.assertIs(type(e), ValueError)

    def test_cache_engine(self):
        manager, engines, new_empty = self._setUpTest()

        # CacheConfigManager is supposed to test cache_engine first
        # here: engine is NOT acceptable and nodes is NOT acceptable
        parameters = new_empty()  # includes ALL cache parameters

        e = self.run_complete(manager, parameters)
        self.assertIs(type(e), ValueError)
        self.assertIn('cache_engine', str(e))

        # here: engine is acceptable and nodes is NOT acceptable
        parameters = {'cache_engine': None, 'cache_nodes': None}
        caught_exceptions = 0
        for db_type in [e[0] for e in engines if e[2] != 'LocMem']:
            parameters['cache_engine'] = db_type
            e = self.run_complete(manager, parameters)
            if type(e) is ValueError:
                caught_exceptions += 1
                self.assertIn('cache_nodes', str(e))
        self.assertEquals(caught_exceptions, len(engines) - 1)

        # here: engine is not acceptable and nodes is acceptable
        parameters = {'cache_engine': None, 'cache_nodes': ['127.0.0.1:1234']}
        e = self.run_complete(manager, parameters)
        self.assertIs(type(e), ValueError)
        self.assertIn('cache_engine', str(e))

        # here: engine is acceptable and nodes is acceptable
        not_locmem = engines[0]
        if not_locmem[2] == 'LocMem':
            not_locmem = engines[1]
        acceptable_engine = not_locmem[0]
        parameters = {'cache_engine': acceptable_engine, 'cache_nodes': ['127.0.0.1:1234']}
        e = self.run_complete(manager, parameters)
        self.assertIsNone(e)

    def test_locmem_engine(self):
        manager, engines, new_empty = self._setUpTest()

        # when the engine is locmem, the default must be acceptable for all
        # other cache_* parameters, because locmem does not require any of them
        locmem = [ e for e in engines if e[2] == 'LocMem'][0]
        parameters = new_empty()
        parameters.update({'cache_engine': locmem[0]})
        e = self.run_complete(manager, parameters)
        self.assertIsNone(e)

    def test_cache_redis(self):
        manager, engines, new_empty = self._setUpTest()

        redis = [e for e in engines if e[2] == 'Redis'][0]
        parameters = new_empty()
        parameters['cache_engine'] = redis[0]

        acceptable_answers = {
            'cache_nodes': '127.0.0.1:6379',
            'cache_db': 1,
            'cache_password': 'd34db33f',
        }
        expected_issues = acceptable_answers.keys()
        met_issues = set()
        for i in expected_issues:
            e = self.run_complete(manager, parameters)
            self.assertIs(type(e), ValueError)

            matches = [issue for issue in expected_issues if issue in str(e)]
            self.assertEqual(len(matches), 1, str(e))
            issue = matches[0]
            cnt_old = len(met_issues)
            met_issues.update({issue})
            cnt_new = len(met_issues)
            self.assertNotEqual(cnt_new, cnt_old)

            parameters[issue] = acceptable_answers[issue]
        self.assertEqual(len(expected_issues), len(met_issues))
        e = self.run_complete(manager, parameters)
        self.assertIsNone(e)

    def test_cache_memcached(self):
        manager, engines, new_empty = self._setUpTest()

        memcached = [e for e in engines if e[2] == 'Memcached'][0]
        parameters = new_empty()
        parameters['cache_engine'] = memcached[0]

        acceptable_answers = {
            'cache_nodes': '127.0.0.1:11211',
        }
        expected_issues = acceptable_answers.keys()
        met_issues = set()
        for i in expected_issues:
            e = self.run_complete(manager, parameters)
            self.assertIs(type(e), ValueError)

            matches = [issue for issue in expected_issues if issue in str(e)]
            self.assertEqual(len(matches), 1, str(e))
            issue = matches[0]
            cnt_old = len(met_issues)
            met_issues.update({issue})
            cnt_new = len(met_issues)
            self.assertNotEqual(cnt_new, cnt_old)

            parameters[issue] = acceptable_answers[issue]
        self.assertEqual(len(expected_issues), len(met_issues))
        e = self.run_complete(manager, parameters)
        self.assertIsNone(e)

class FilesystemTests(AskbotTestCase):

    def setUp(self):
        self.installer = AskbotSetup()
        self.parser = self.installer.parser

    @staticmethod
    def _setUpTest():
        manager = FilesystemConfigManager(interactive=False, verbosity=0)
        new_empty = lambda: dict([(k, None) for k in manager.keys])
        return manager, new_empty

    @staticmethod
    def run_complete(manager, parameters):
        e = None
        try:
            manager.complete(parameters)
        except ValueError as ve:
            e = ve
        return e

    def test_filesystem_configmanager(self):
        manager, new_empty = self._setUpTest()

        parameters = new_empty()  # includes ALL cache parameters
        self.assertGreater(len(parameters), 0)

        # with interactive=False ConfigManagers (currently) raise an exception
        # if a required parameter is not set or not acceptable
        # the ConfigManager must trip over missing/empty cache settings
        parameters = {'dir_name': ''}
        e = self.run_complete(manager, parameters)
        self.assertIs(type(e), ValueError)

    def test_project_dir(self):
        manager, new_empty = self._setUpTest()

        failing_dir_names = [
            '', # empty string violates name restriction
            'os', # name of a module in PYTHONPATH causes a name collision
            'askbot',  # name of a module in PYTHONPATH causes a name collision
            '/bin/bash', # is a file
            '/root', # cannot write there
            '/usr/local/lib/python3.x/dist-packages/some-package/module/submodule/subsubmodule', # practice recursion
        ]
        for name in failing_dir_names:
            parameters = {'dir_name': name}
            e = self.run_complete(manager, parameters)
            self.assertIs(type(e), ValueError)

        valid_dir_names = [
            'validDeployment',
            '/tmp/validDeployment',
        ]
        for name in valid_dir_names:
            parameters = {'dir_name': name}
            e = self.run_complete(manager, parameters)
            self.assertIsNone(e)

    def test_app_name(self):
        manager, new_empty = self._setUpTest()

        failing_app_names = [
            '',  # empty string violates name restriction
            'os',  # name of a module in PYTHONPATH causes a name collision
            'askbot',  # name of a module in PYTHONPATH causes a name collision
            'bin/bash',  # is a file
            '/root',  # cannot write there
            '\/root',
            'usr/local/',
            'usr\/local\/',
            'usr/',
            'usr\/',
            'me\no\like\this',
            'me\\no\\like\\this',
            'me\\\no\\\like\\\this',
        ]
        for name in failing_app_names:
            parameters = {'app_name': name}
            e = self.run_complete(manager, parameters)
            self.assertIs(type(e), ValueError, parameters)

        valid_app_names = [
            'validDeployment',
            'askbot_app',
        ]
        for name in valid_app_names:
            parameters = {'app_name': name}
            e = self.run_complete(manager, parameters)
            self.assertIsNone(e)

    def __test_project_dir_interactive(self):
        """The console functions contain endless loops, which impedes
        testability. If we mock the console functions, then there is no merrit
        in testing interactively at all."""
        manager = FilesystemConfigManager(interactive=True, verbosity=1)
        parameters = {'dir_name': ''}

        #with patch('askbot.utils.console.simple_dialog', return_value='validDeployment'), patch('askbot.utils.console.choice_dialog', return_value='yes'):
        with patch('builtins.input', new=MockInput('martin', 'yes')):
            e = self.run_complete(manager, parameters)
            self.assertIsNone(e)
