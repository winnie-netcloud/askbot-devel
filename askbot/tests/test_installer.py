from askbot.tests.utils import AskbotTestCase
from askbot.deployment import AskbotSetup
#from askbot.deployment.parameters import *
from askbot.deployment.deployables import *
import tempfile
import os.path

from unittest.mock import patch, MagicMock, mock_open



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

    def test_ProjectRoot(self):
        test = ProjectRoot(self.project_root.name)
        test.src_dir = self.setup_templates.name
        test.verbosity = 0
        test.deploy()

        comp = self.deployableComponents[test.name]
        comp = self.deployableComponents[test.name]
        root_path = self.project_root.name
        message = f"\n{root_path}"
        message += ' exists' if os.path.isdir(root_path) else ' does not exist'
        for name, value in comp.contents.items():
            name_path = os.path.join(self.project_root.name, name)
            message += f"\n{name_path}"
            message += ' exists' if os.path.isdir(name_path) else ' does not exist'
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
        test = ProjectRoot(self.project_root.name)

        another_file = os.path.join(self.setup_templates.name, 'additional.file')
        with open(another_file, 'wb') as f:
            f.write(self.hello.encode('utf-8'))
        test.contents.update({'additional.file': CopiedFile})

        test.src_dir = self.setup_templates.name
        test.verbosity = 0
        test.deploy()

        comp = self.deployableComponents[test.name]
        for name, value in comp.contents.items():
            self.assertTrue(os.path.exists(os.path.join(self.project_root.name, name)))
        self.assertTrue(os.path.exists(os.path.join(self.project_root.name, 'additional.file')))

    def test_addDirBeforeDeploy(self):
        test = ProjectRoot(self.project_root.name)

        another_file = os.path.join(self.setup_templates.name, 'additional.file')
        with open(another_file, 'wb') as f:
            f.write(self.hello.encode('utf-8'))
        test.contents.update({'additionalDir': {'additional.file': CopiedFile}})

        test.src_dir = self.setup_templates.name
        test.verbosity = 0
        test.deploy()

        comp = self.deployableComponents[test.name]
        for name, value in comp.contents.items():
            self.assertTrue(os.path.exists(os.path.join(self.project_root.name, name)))
        self.assertTrue(os.path.exists(os.path.join(self.project_root.name, 'additionalDir', 'additional.file')))
