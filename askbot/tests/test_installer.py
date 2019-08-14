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
        self.project_root = tempfile.TemporaryDirectory()
        self.setup_templates = tempfile.TemporaryDirectory()

        self.jinja2_template = tempfile.NamedTemporaryFile(suffix='.jinja2', delete=False, dir=self.setup_templates.name)
        jinja2 = "Hello {{ world }}! <-- This should read Hello World!\n"
        self.jinja2_template.write(jinja2.encode('utf-8'))
        self.jinja2_template.close()

        self.jinja2_target = os.path.splitext(
                                os.path.basename(
                                    self.jinja2_template.name))[0]

        self.text_file = tempfile.NamedTemporaryFile(delete=False, dir=self.setup_templates.name)
        self.text_file.write("Hello World.\n".encode('utf-8'))
        self.text_file.close()

    def tearDown(self):
        del(self.project_root)
        del(self.setup_templates)

    def test_individualCopiedFile(self):
        basename = os.path.basename(self.text_file.name)

        test = CopiedFile(basename, self.setup_templates.name, self.project_root.name + '_target_does_not_exist')
        self.assertRaises(FileNotFoundError, test.deploy)

        test = CopiedFile(basename, self.setup_templates.name + '_source_does_not_exist', self.project_root.name)
        self.assertRaises(FileNotFoundError, test.deploy)

        test = CopiedFile(basename + '_bogus', self.setup_templates.name, self.project_root.name)
        self.assertRaises(FileNotFoundError, test.deploy)

        # this should just work and copy the file
        test = CopiedFile(basename, self.setup_templates.name, self.project_root.name)
        test.deploy()

        new_file = os.path.join(self.project_root.name, basename)
        try:
            with open(new_file, 'r') as file:
                buf = file.read()
                self.assertGreater(len(buf), 0)
        except FileNotFoundError as e:
            self.fail(FileNotFoundError('Copying the file did not work!'))

        # do it again. Should yield a user notification and then succeed by
        # not doing anything.
        test.deploy()

    def test_individualRenderedFile(self):
        basename = self.jinja2_target

        test = RenderedFile(basename, self.setup_templates.name, self.project_root.name + '_target_does_not_exist')
        self.assertRaises(FileNotFoundError, test.deploy)

        test = RenderedFile(basename, self.setup_templates.name + '_source_does_not_exist', self.project_root.name)
        self.assertRaises(FileNotFoundError, test.deploy)

        test = RenderedFile(basename + '_bogus', self.setup_templates.name, self.project_root.name)
        self.assertRaises(FileNotFoundError, test.deploy)

        test = RenderedFile(basename, self.setup_templates.name, self.project_root.name)
        test.context = {'world': 'World'}
        test.deploy()

        new_file = os.path.join(self.project_root.name, basename)
        try:
            with open(new_file, 'r') as file:
                buf = file.read()
                self.assertGreater(len(buf), 0)
        except FileNotFoundError as e:
            self.fail(FileNotFoundError('Rendering the file did not work!'))

        # do it again. Should yield a user notification and then succeed by
        # not doing anything.
        test.deploy()


    def test_individualDirectory(self):
        basename = 'foobar'

        test = Directory(basename, self.project_root.name)
        test.deploy()

        new_dir = os.path.join(self.project_root.name, basename)

        self.assertTrue(os.path.exists(new_dir))
        self.assertTrue(os.path.isdir(new_dir))

        # do it again. This should succeed by
        # not doing anything.
        test.deploy()




if __name__ == '__main__':
    askbot_site = AskbotSite()
    askbot_app = AskbotApp()

