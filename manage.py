import subprocess
from itertools import tee, islice, izip_longest
from polyglot import APP
from flask.ext.script import Manager

manager = Manager(APP)

@manager.command
def base():
    APP.run(port=5010, debug=True)


if __name__ == "__main__":
    manager.run()
