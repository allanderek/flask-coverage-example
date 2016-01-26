import os

import flask
from flask.ext.script import Manager

from app.main import application, database

manager = Manager(application)


def run_command(command):
    """ We frequently inspect the return result of a command so this is just
        a utility function to do this. Generally we call this as:
        return run_command ('command_name args')
    """
    result = os.system(command)
    return 0 if result == 0 else 1


def run_with_test_server(test_command, coverage):
    """Run the test server and the given test command in parallel. If 'coverage'
    is True, then we run the server under coverage analysis and produce a
    coverge report."""
    import subprocess
    import urllib
    coverage_prefix = ["coverage", "run", "--source", "app.main"]
    server_command_prefx = coverage_prefix if coverage else ['python']
    server_command = server_command_prefx + ["manage.py", "run_test_server"]
    server = subprocess.Popen(server_command, stderr=subprocess.PIPE)
    # TODO: If we don't get this line we should  be able to detect that
    # and avoid the starting test process.
    for line in server.stderr:
        if line.startswith(b' * Running on'):
            break
    test_process = subprocess.Popen(test_command)
    test_process.wait(timeout=60)
    port = application.config['TEST_SERVER_PORT']
    shutdown_url = 'http://localhost:{}/shutdown'.format(port)
    response = urllib.request.urlopen(shutdown_url)
    print(bytes.decode(response.read()))
    server_return_code = server.wait(timeout=60)
    if coverage:
        os.system("coverage report -m")
        os.system("coverage html")
    return server_return_code

@manager.command
def test_main(nocoverage=False):
    """Run the python only tests within py.test app/main.py we still run
    the test server in parallel and produce a coverage report."""
    test_command = ['py.test', 'app/main.py']
    return run_with_test_server(test_command, not nocoverage)


@manager.command
def test():
    main_result = test_main()
    return main_result


def shutdown():
    """Shutdown the Werkzeug dev server, if we're using it.
    From http://flask.pocoo.org/snippets/67/"""
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:  # pragma: no cover
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


@manager.command
def run_test_server():
    """Used by the phantomjs tests to run a live testing server"""
    # running the server in debug mode during testing fails for some reason
    application.config['DEBUG'] = True
    application.config['TESTING'] = True
    port = application.config['TEST_SERVER_PORT']
    # Don't use the production database but a temporary test database.
    application.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
    database.create_all()
    database.session.commit()

    # Add a route that allows the test code to shutdown the server, this allows
    # us to quit the server without killing the process thus enabling coverage
    # to work.
    application.add_url_rule('/shutdown', 'shutdown', shutdown,
                             methods=['POST', 'GET'])

    application.run(port=port, use_reloader=False, threaded=True)

    database.session.remove()
    database.drop_all()


if __name__ == "__main__":
    manager.run()
