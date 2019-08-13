from askbot.deployment.deployables import *

if __name__ == '__main__':
    test = CopiedFile('testfile', '/tmp/foo', '/tmp/bar')
    test.deploy()
    test = RenderedFile('testfile01', '/tmp/foo', '/tmp/bar')
    test.context = {'x': 'World'}
    test.deploy()
    test = Directory('baz', '/tmp')
    test.deploy()
    askbot_site = AskbotSite()
    askbot_app = AskbotApp()
    project_root = ProjectRoot('/tmp/project_root_install_dir')
    project_root.src_dir = '/tmp/foo'
    project_root.deploy()
