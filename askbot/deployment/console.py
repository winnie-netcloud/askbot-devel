from askbot.utils import console as console_utils

PREAMBLE = """\nDeploying Askbot - Django Q&A forum application
Problems installing? -> please email support@askbot.com

To CANCEL - press Ctr-C.\n"""

class Console:
    def __init__(self):
        self.preamble_printed = False

    def simple_dialog(self, prompt, required=False, default=None):
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        return console_utils.simple_dialog(prompt, required=required, default=default)

    def print_line(self, line):
        """Prints a line, preceded by the preamble,
        if necessary."""
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        print(line)

    def print_error(self, line):
        if not self.preamble_printed:
            self.print_preamble()
            self.preamble_printed = True
        print('\033[31m' + line + '\33[0m')

    def print_preamble(self):
        print('\33[33m' + PREAMBLE + '\33[0m')

    def print_postamble(self): 
        """Help text describing the next steps"""
        print("""Done. Please find further instructions at http://askbot.org/doc/
You will probably want to edit the settings.py file.""")

        if options['database_engine'] == 'postgresql_psycopg2':
            try:
                import psycopg2
            except ImportError:
                print('\nNEXT STEPS: install python binding for postgresql')
                print('pip install psycopg2-binary\n')
        elif options['database_engine'] == 'mysql':
            try:
                import _mysql
            except ImportError:
                print('\nNEXT STEP: install python binding for mysql')
                print('pip install mysql-python\n')
