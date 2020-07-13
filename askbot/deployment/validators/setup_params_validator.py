"""Validator for the directory parameters and
the setup procedure parameters"""
import os.path
from askbot.deployment import const
from askbot.deployment.exceptions import ValidationError

def dir_clashes_with_python_module(path):
    """Returns a boolean"""
    from askbot.utils.loading import load_module
    try:
        mod = load_module(os.path.basename(path))
    except ModuleNotFoundError:
        return False
    else:
        if path not in mod.__path__:
            return True
    return False

class SetupParamsValidator:
    def __init__(self, console, parser):
        self.console = console
        self.parser = parser
        self.options = parser.parse_args()

    def get_params(self):
        """Returns setup parameters"""
        root_dir = self.get_valid_root_dir()
        return {
            'force': self.options.force,
            'interactive': self.options.interactive,
            'root_dir': root_dir,
            'proj_name': self.get_valid_proj_name(root_dir),
            'media_root': self.get_valid_media_root(root_dir)
        }

    def get_valid_media_root(self, root_dir):
        """Returns valid value for the `MEDIA_ROOT` setting."""
        raw_value = self.options.media_root
        # if missing - return default
        if not raw_value:
            return os.path.join(root_dir, const.DEFAULT_MEDIA_ROOT_SUBDIR)

        return os.path.abspath(raw_value)


    def get_valid_root_dir(self):
        """Returns absolute path of valid root directory"""
        if not self.options.interactive:
            root_dir = os.path.abspath(self.options.root_dir)

            if dir_clashes_with_python_module(root_dir):
                mod_name = os.path.basename(root_dir)
                raise ValidationError(f'Value of --root-dir clashes with the `{mod_name}` python module.\nTry a different value.')

            if self.options.force:
                return root_dir #overwrite the project root, if necessary
            #not -force
            if os.path.exists(root_dir):
                # cannot overwrite silently - raise an exception
                raise ValidationError(f'{root_dir} already exists.\nUse a different value for the --root-dir parameter.')
            # accept the default value, since the directory does not exist
            return root_dir

        # interactive branch
        default = self.parser.get_default('root_dir')
        user_prompt = f'Enter {const.ROOT_DIR_HELP}.'
        entered_by_hand = False

        if not self.options.force and os.path.exists(os.path.abspath(default)):
            # don't use the default if the default directory already exists
            default = None

        if self.options.root_dir == default:
            if default:
                user_input = self.console.simple_dialog(user_prompt, default=default)
            else:
                user_input = self.console.simple_dialog(user_prompt, required=True)
            entered_by_hand = True
            root_dir = os.path.abspath(user_input)
        else:
            root_dir = os.path.abspath(self.options.root_dir)

        while True:
            if dir_clashes_with_python_module(root_dir):
                mod_name = os.path.basename(root_dir)
                if entered_by_hand:
                    self.console.print_error(f'Value clashes with the `{mod_name}` python module.\nTry a different value.')
                else:
                    self.console.print_error(f'Value of --root-dir clashes with the `{mod_name}` python module.\nTry a different value.')
                if default:
                    user_input = self.console.simple_dialog(user_prompt, default=default)
                else:
                    user_input = self.console.simple_dialog(user_prompt, required=True)
                entered_by_hand = True
                root_dir = os.path.abspath(user_input)

            if os.path.exists(root_dir):
                if self.options.force:
                    return root_dir

                self.console.print_error(f'{root_dir} already exists.')
                if default:
                    user_input = self.console.simple_dialog(user_prompt, default=default)
                else:
                    user_input = self.console.simple_dialog(user_prompt, required=True)
                entered_by_hand = True
                root_dir = os.path.abspath(user_input)
            else:
                return root_dir


    def get_valid_proj_name(self, root_dir):
        """Returns valid name of the django project,
        which will be the name of the directory
        to hold the settings.py file"""
        options = self.options
        parser = self.parser

        if not options.interactive:
            proj_dir = os.path.abspath(os.path.join(root_dir, options.proj_name))
            #todo: test for absence of slash
            if dir_clashes_with_python_module(proj_dir):
                mod_Name = options.proj_name
                raise ValidationError(f'Value of --proj-name clashes with the `{mod_name}` python module.\nTry a different value.')

            if options.force:
                return options.proj_name
            #not -force
            if os.path.exists(proj_dir):
                # cannot overwrite silently - raise an exception
                raise ValidationError(f'{proj_dir} already exists.\nUse a different value for the --proj-name parameter.')
            # accept the default value, since the directory does not exist
            return proj_dir

        # interactive branch
        default = parser.get_default('proj_name')
        user_prompt = f'Enter {const.PROJ_NAME_HELP}.'
        entered_by_hand = False

        default_proj_dir = os.path.join(root_dir, default)
        default_proj_dir = os.path.abspath(default_proj_dir)
        if not options.force and os.path.exists(default_proj_dir):
            # don't use the default if the default directory already exists
            default = None

        if self.options.proj_name == default:
            if default:
                user_input = self.console.simple_dialog(user_prompt, default=default)
            else:
                user_input = self.console.simple_dialog(user_prompt, required=True)
            entered_by_hand = True
            proj_name = os.path.abspath(user_input)
        else:
            proj_name = options.proj_name

        proj_dir = os.path.abspath(os.path.join(root_dir, proj_name))
        while True:
            # todo: test for absence of slash
            # test name clash with python module
            if dir_clashes_with_python_module(proj_dir):
                mod_name = proj_name
                if entered_by_hand:
                    self.console.print_error(f'Value clashes with the `{mod_name}` python module.\nTry a different value.')
                else:
                    self.console.print_error(f'Value of --proj-name clashes with the `{mod_name}` python module.\nTry a different value.')
                if default:
                    user_input = self.console.simple_dialog(user_prompt, default=default)
                else:
                    user_input = self.console.simple_dialog(user_prompt, required=True)
                entered_by_hand = True
                proj_dir = os.path.abspath(os.path.join(root_dir, user_input))

            if os.path.exists(proj_dir):
                if self.options.force:
                    return proj_dir

                self.console.print_error(f'{proj_dir} already exists.')
                if default:
                    user_input = self.console.simple_dialog(user_prompt, default=default)
                else:
                    user_input = self.console.simple_dialog(user_prompt, required=True)
                entered_by_hand = True
                proj_dir = os.path.abspath(os.path.join(root_dir, user_input))
            else:
                return proj_dir
