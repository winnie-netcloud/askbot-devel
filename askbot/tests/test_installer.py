from askbot.tests.utils import AskbotTestCase
from askbot.deployment import AskbotSetup
from askbot.deployment.parameters import *
from askbot.deployment.deployables import *
from unittest.mock import patch, MagicMock, mock_open

import tempfile
import os.path

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
        manager = databaseManager
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
        self.manager = databaseManager
        self.manager.reset()

    def test_database_engine(self):
        new_empty = lambda: dict([(k, None) for k in self.manager.keys])

        # DbConfigManager is supposed to test database_engine first
        # here: engine is NOT acceptable and name is NOT acceptable
        parameters = new_empty() # includes ALL database parameters
        try:
            self.manager.complete(parameters)
        except ValueError as e:
            self.assertIn('database_engine', str(e))

        # With a database_engine set, users must provide a database_name
        # here: engine is acceptable and name is NOT acceptable
        engines = self.manager._catalog['database_engine'].database_engines
        parameters = {'database_engine': None, 'database_name': None}
        caught_exceptions = 0
        for db_type in [e[0] for e in engines]:
            parameters['database_engine'] = db_type
            try:
                self.manager.complete(parameters)
            except ValueError as ve:
                caught_exceptions += 1
                self.assertIn('database_name', str(ve))
        self.assertEquals(caught_exceptions, len(engines))

        # here: engine is not acceptable and name is acceptable
        parameters = {'database_engine': None, 'database_name': 'acceptable_value'}
        e = None
        try:
            self.manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIn('database_engine', str(e))

        # here: engine is acceptable and name is acceptable
        acceptable_engine = self.manager._catalog['database_engine'].database_engines[0][0]
        parameters = {'database_engine': acceptable_engine, 'database_name': 'acceptable_value'}
        e = None
        try:
            self.manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIsNone(e)

    # at the moment, the  parameter parse does not have special code for
    # mysql and oracle, so we do not provide dedicated tests for them
    def test_database_postgres(self):
        new_empty = lambda: dict([(k, None) for k in self.manager.keys])
        parameters = new_empty()
        parameters['database_engine'] = 1

        ordered_acceptable_answers = (
            ('database_name', 'testDB'),
            ('database_user', 'askbot'),
            ('database_password', 'd34db33f'),
        )

        acceptable_answers = dict(ordered_acceptable_answers)
        expected_issues = [item[0] for item in ordered_acceptable_answers]
        met_issues = set()
        for i in expected_issues:
            e = None
            try:
                self.manager.complete(parameters)
            except ValueError as ve:
                e = ve
                matches = [issue for issue in expected_issues if issue in str(e)]
                self.assertEqual(len(matches), 1, str(e))

            issue = matches[0]
            cnt_old = len(met_issues)
            met_issues.update({issue})
            cnt_new = len(met_issues)
            self.assertNotEqual(cnt_new, cnt_old)
            parameters[issue] = acceptable_answers[issue]
        self.assertEqual(len(expected_issues), len(met_issues))
        e = None
        try:
            self.manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIsNone(e)

    def test_database_sqlite(self):
        new_empty = lambda: dict([(k, None) for k in self.manager.keys])
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
                self.manager.complete(parameters)
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
            self.manager.complete(parameters)
        except ValueError as ve:
            e = ve
        self.assertIsNone(e)

## Cache config related tests
class CacheEngineTest(AskbotTestCase):

    def setUp(self):
        self.installer = AskbotSetup()
        self.parser = self.installer.parser
        self.manager = cacheManager
        self.manager.reset()

    def _setUpTest(self):
        engines = self.manager._catalog['cache_engine'].cache_engines
        new_empty = lambda: dict([(k, None) for k in self.manager.keys])
        return self.manager, engines, new_empty

    @staticmethod
    def run_complete(manager, parameters):
        try:
            manager.complete(parameters)
        except ValueError as error:
            return error
        return None

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
        self.manager = filesystemManager
        self.manager.reset()

    def _setUpTest(self):
        new_empty = lambda: dict([(k, None) for k in self.manager.keys])
        return self.manager, new_empty

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
        for name in failing_dir_names[-1:]:
            parameters = {'dir_name': name}
            error = self.run_complete(manager, parameters)
            self.assertIs(type(error), ValueError)

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
        parameters = {'dir_name': ''}

        #with patch('askbot.utils.console.simple_dialog', return_value='validDeployment'), patch('askbot.utils.console.choice_dialog', return_value='yes'):
        with patch('builtins.input', new=MockInput('martin', 'yes')):
            e = self.run_complete(self.manager, parameters)
            self.assertIsNone(e)

class MainInstallerTests(AskbotTestCase):
    def setUp(self):
        self.installer = AskbotSetup(interactive=True, verbosity=0)

    def test_propagate_attributes(self):
        collection = self.installer.configManagers
        managers = [collection.configManager(key) for key in collection.keys]
        fields = [m.configField(k) for m in managers for k in m.keys]

        has_verbosity = [ self.installer, collection ]
        has_verbosity.extend(managers)
        has_verbosity.extend(fields)
        for obj in has_verbosity:
            self.assertEqual(obj.verbosity, self.installer.verbosity)

        for new_verbosity in [2, 5, 13, 23, 42, 666, 1337, 16061, self.installer.verbosity]:
            self.installer.verbosity = new_verbosity
            for obj in has_verbosity:
                self.assertEqual(obj.verbosity, new_verbosity)

        interactive_fields = [m.configField(k)
                              for m in managers
                              for k in m.keys
                              if hasattr(m.configField(k),'interactive')]
        has_interactive = [ collection ]
        has_interactive.extend(managers)
        has_interactive.extend(interactive_fields)
        for obj in has_interactive:
            self.assertEqual(obj.interactive, collection.interactive)

        for new_interactive in [True, False, True, collection.interactive]:
            collection.interactive = new_interactive
            for obj in has_interactive:
                self.assertEqual(obj.interactive, new_interactive)

    def test_flow_dry_run(self):
        destdir = tempfile.TemporaryDirectory()
        self.installer.configManagers.interactive=False
        # minimal_viable_argument_set
        mva = ['--dir-name', destdir.name,
               '--db-engine', '2',
               '--db-name', '/tmp/AskbotTest.db',
               '--cache-engine', '3']

        run_opts = ['--dry-run', '-v', '0']
        with patch('sys.exit') as mock:
            opts = self.installer.parser.parse_args(mva + run_opts)
            parse_args = MagicMock(name='parse_args', return_value=opts)
            self.installer.parser.parse_args = parse_args
            self.installer()
            self.assertEqual(mock.call_count, 1)

    def test_flow_skip_deploy(self):
        destdir = tempfile.TemporaryDirectory()
        mva = ['--dir-name', destdir.name,
               '--db-engine', '2',
               '--db-name', '/tmp/AskbotTest.db',
               '--cache-engine', '3']
        run_opts = ['-v', '0']

        opts = self.installer.parser.parse_args(mva + run_opts)
        parse_args = MagicMock(name='parse_args', return_value=opts)
        deploy_askbot = MagicMock()
        self.installer.parser.parse_args = parse_args
        self.installer.deploy_askbot = deploy_askbot
        try:
            self.installer()
        except Exception as error:
            self.fail(f'Running the installer raised {error}')

    def test_flow_mock_deployment(self):
        destdir = tempfile.TemporaryDirectory()
        mva = ['--dir-name',destdir.name,
               '--db-engine', '2',
               '--db-name', '/tmp/AskbotTest.db',
               '--cache-engine', '3']
        run_opts = ['-v', '0']
        opts = self.installer.parser.parse_args(mva + run_opts)
        parse_args = MagicMock(name='parse_args', return_value=opts)
        self.installer.parser.parse_args = parse_args
        fake_open = mock_open(read_data='foobar')
        #with patch('askbot.deployment.path_utils.create_path'), patch('shutil.copy'), patch('builtins.open', fake_open):
        self.installer()


class DeployObjectsTest(AskbotTestCase):
    def setUp(self):
        """creates two temporary directories:
        - project_root, not contents
        - setup_templates, source files for installation tests:
            - jinja2_template a minimal jinja2 template that can be rendered
            - text_file a plain text file
        setUp() also sets self.jinja2_target, which is the filename (not the
        path!) that must be used with RenderedFile, so that it will load
        jinja2_template.
        """
        self.jinja2 = "Hello {{ world }}! <-- This should read Hello World!\n"
        self.hello = "Hello World.\n"

        self.project_root = tempfile.TemporaryDirectory()
        self.setup_templates = tempfile.TemporaryDirectory()

        self.jinja2_template = tempfile.NamedTemporaryFile(suffix='.jinja2', delete=False, dir=self.setup_templates.name)
        self.jinja2_template.write(self.jinja2.encode('utf-8'))
        self.jinja2_template.close()

        self.jinja2_target = os.path.splitext(
                                os.path.basename(
                                    self.jinja2_template.name))[0]

        self.text_file = tempfile.NamedTemporaryFile(delete=False, dir=self.setup_templates.name)
        self.text_file.write(self.hello.encode('utf-8'))
        self.text_file.close()

    def tearDown(self):
        del self.project_root
        del self.setup_templates

    def test_individualCopiedFile(self):
        basename = os.path.basename(self.text_file.name)

        test = CopiedFile(basename, self.setup_templates.name, self.project_root.name + '_target_does_not_exist')
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        test = CopiedFile(basename, self.setup_templates.name + '_source_does_not_exist', self.project_root.name)
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        test = CopiedFile(basename + '_bogus', self.setup_templates.name, self.project_root.name)
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        # this should just work and copy the file
        test = CopiedFile(basename, self.setup_templates.name, self.project_root.name)
        test.verbosity = 0
        test.deploy()

        new_file = os.path.join(self.project_root.name, basename)
        try:
            with open(new_file, 'rb') as file:
                buf = file.read()
                self.assertGreater(len(buf), 0)
                self.assertEqual(buf.decode('utf-8'), self.hello)
        except FileNotFoundError:
            self.fail(FileNotFoundError('Copying the file did not work!'))

        # do it again. Should yield a user notification and then succeed by
        # not doing anything.
        test.deploy()

    def test_individualRenderedFile(self):
        basename = self.jinja2_target

        test = RenderedFile(basename, self.setup_templates.name, self.project_root.name + '_target_does_not_exist')
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        test = RenderedFile(basename, self.setup_templates.name + '_source_does_not_exist', self.project_root.name)
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        test = RenderedFile(basename + '_bogus', self.setup_templates.name, self.project_root.name)
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        test = RenderedFile(basename, self.setup_templates.name, self.project_root.name)
        test.verbosity = 0
        test.context = {'world': 'World'}
        test.deploy()

        new_file = os.path.join(self.project_root.name, basename)
        try:
            with open(new_file, 'rb') as file:
                buf = file.read()
                self.assertGreater(len(buf), 0)
                self.assertNotEqual(buf.decode('utf-8'), self.jinja2)
        except FileNotFoundError:
            self.fail(FileNotFoundError('Rendering the file did not work!'))

        # do it again. Should yield a user notification and then succeed by
        # not doing anything.
        test.deploy()

    def test_individualEmptyFile(self):
        basename = os.path.basename(self.text_file.name)

        test = EmptyFile(basename, self.setup_templates.name, self.project_root.name + '_target_does_not_exist')
        test.verbosity = 0
        self.assertRaises(FileNotFoundError, test.deploy)

        # this should just work and copy the file
        test = EmptyFile(basename, self.setup_templates.name, self.project_root.name)
        test.verbosity = 0
        test.deploy()

        new_file = os.path.join(self.project_root.name, basename)
        try:
            with open(new_file, 'rb') as file:
                buf = file.read()
        except FileNotFoundError:
            self.fail(FileNotFoundError('Copying the file did not work!'))

        # do it again. Should yield a user notification and then succeed by
        # not doing anything.
        test.deploy()

    def test_individualDirectory(self):
        basename = 'foobar'

        test = Directory(basename, self.project_root.name)
        test.verbosity = 0
        test.deploy()

        new_dir = os.path.join(self.project_root.name, basename)

        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))

        # do it again. This should succeed by
        # not doing anything.
        test.deploy()


class DeployableComponentsTest(AskbotTestCase):
    def _flatten_components(self, components):
        found = [i for i in components
                 if i[1] is RenderedFile
                 or i[1] is CopiedFile
                 or i[1] is LinkedDir]

        for descent in [list(i[1].items()) for i in components
                        if isinstance(i[1], dict)]:
            found.extend(
                self._flatten_components(descent)
            )
        return found

    def setUp(self):
        """creates two temporary directories:
        - project_root, not contents
        - setup_templates, source files for installation tests:
        All supported DeployableComponents are registered here and then searched
        for the files they want to deploy. corresponding templates are then
        generated in setup_templates, so that the deployment may succeed.
        """

        self.jinja2 = "Hello {{ world }}! <-- This should read Hello World!\n"
        self.hello = "Hello World.\n"

        self.project_root = tempfile.TemporaryDirectory()
        self.setup_templates = tempfile.TemporaryDirectory()

        x, y, z = AskbotApp(), AskbotSite(), ProjectRoot(self.project_root.name)
        self.deployableComponents = {
            x.name: x,
            y.name: y,
            z.name: z,
        }

        for cname, comp in self.deployableComponents.items():
            for fname, ftype in self._flatten_components(list(comp.contents.items())):
                if ftype is RenderedFile:
                    with open(os.path.join(
                            self.setup_templates.name,
                            f'{fname}.jinja2'), 'wb') as f:
                        f.write(self.jinja2.encode('utf-8'))
                elif ftype is CopiedFile:
                    with open(os.path.join(
                            self.setup_templates.name, fname), 'wb') as f:
                        f.write(self.hello.encode('utf-8'))
                elif ftype is LinkedDir:
                    os.makedirs(os.path.join(
                            self.setup_templates.name, fname), exist_ok=True)

    def tearDown(self):
        del self.project_root
        del self.setup_templates

    def test_TestSetup(self):
        self.assertTrue(os.path.isdir(self.project_root.name))
        self.assertTrue(os.path.isdir(self.setup_templates.name))
        self.assertFalse(self.project_root.name == self.setup_templates.name)


    def test_ProjectRoot(self):
        mock_doc_dir = tempfile.TemporaryDirectory()
        os.mkdir(os.path.join(mock_doc_dir.name, 'doc'))
        test = ProjectRoot(self.project_root.name)
        test.src_dir = self.setup_templates.name
        test.verbosity = 0

        # ProiectRoot.deploy works under the assumption that 'setup_templates'
        # and 'doc' are directories inside the same parent directory. While
        # this holds true for an actual Askbot installation, it doesn't in this
        # unittest. We use the following patch context to align the
        # directory structure assumption of ProjectRoot.deploy with the
        # test environment, which is auto-generated temporary directories.
        with patch('os.path.dirname', return_value=mock_doc_dir.name):
            test.deploy()

        comp = self.deployableComponents[test.name]
        root_path = self.project_root.name
        message = f"\n{root_path}"
        message += ' exists' if os.path.isdir(root_path) else ' does not exist'
        for name, value in comp.contents.items():
            name_path = os.path.join(self.project_root.name, name)
            message += f"\n{name_path}"
            message += ' exists' if os.path.exists(name_path) else ' does not exist'
            self.assertTrue(os.path.exists(name_path), message)


    def test_AskbotSite(self):
        test = AskbotSite()
        test.src_dir = self.setup_templates.name
        test.dst_dir = self.project_root.name
        test.verbosity = 0
        test.deploy()

        comp = self.deployableComponents[test.name]
        root_path = self.project_root.name
        comp_path = os.path.join(root_path, comp.name)
        message  = f"\n{root_path}"
        message += ' exists' if os.path.isdir(root_path) else ' does not exist'
        message += f"\n{comp_path}"
        message += ' exists' if os.path.isdir(comp_path) else ' does not exist'
        for name, value in comp.contents.items():
            name_path = os.path.join(self.project_root.name, comp.name, name)
            message += f"\n{name_path}"
            message += ' exists' if os.path.isdir(name_path) else ' does not exist'
            self.assertTrue(os.path.exists(name_path),message)

    def test_AskbotApp(self):
        test = AskbotApp()
        test.src_dir = self.setup_templates.name
        test.dst_dir = self.project_root.name
        test.verbosity = 0
        test.deploy()

        comp = self.deployableComponents[test.name]
        root_path = self.project_root.name
        comp_path = os.path.join(root_path, comp.name)
        message = f"\n{root_path}"
        message += ' exists' if os.path.isdir(root_path) else ' does not exist'
        message += f"\n{comp_path}"
        message += ' exists' if os.path.isdir(comp_path) else ' does not exist'
        for name, value in comp.contents.items():
            name_path = os.path.join(self.project_root.name, comp.name, name)
            message += f"\n{name_path}"
            message += ' exists' if os.path.isdir(name_path) else ' does not exist'
            self.assertTrue(os.path.exists(name_path), message)


    def test_addFileBeforeDeploy(self):
        another_file = os.path.join(self.setup_templates.name, 'additional.file')
        with open(another_file, 'wb') as f:
            f.write(self.hello.encode('utf-8'))

        test = AskbotSite()
        test.contents.update({'additional.file': CopiedFile})

        test.src_dir = self.setup_templates.name
        test.dst_dir = self.project_root.name
        test.verbosity = 0
        test.deploy()

        del test.contents['additional.file']

        comp = self.deployableComponents[test.name]
        name_path = os.path.join(self.project_root.name, comp.name, 'additional.file')
        message  = f"\n{name_path}"
        message += ' exists' if os.path.isdir(name_path) else ' does not exist'
        self.assertTrue(os.path.exists(name_path), message)


    def test_addDirBeforeDeploy(self):
        another_file = os.path.join(self.setup_templates.name, 'additional.file')
        with open(another_file, 'wb') as f:
            f.write(self.hello.encode('utf-8'))

        test = AskbotSite()
        test.contents.update({'additionalDir': {'additional.file': CopiedFile}})

        test.src_dir = self.setup_templates.name
        test.dst_dir = self.project_root.name
        test.verbosity = 0
        test.deploy()

        del test.contents['additionalDir']

        comp = self.deployableComponents[test.name]
        name_path = os.path.join(self.project_root.name, comp.name, 'additionalDir', 'additional.file')
        message = f"\n{name_path}"
        message += ' exists' if os.path.isdir(name_path) else ' does not exist'
        self.assertTrue(os.path.exists(name_path), message)
