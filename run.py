#!/usr/bin/env python
"""Task runner for the nixbot project."""
from tempfile import NamedTemporaryFile
from textwrap import dedent
from pathlib import Path
import subprocess as sp
import os
import re

from shell_utils import shell, cd

import click


@click.group()
def main():
    """
    Development tasks for nixbot

    """

    # ensure we're running commands from project root

    root = Path(__file__).parent.absolute()
    cwd = Path().absolute()

    if root != cwd:
        click.secho(f'Navigating from {cwd} to {root}',
                    fg='yellow')
        os.chdir(root)


@main.command()
@click.option('--auto-commit', is_flag=True, help='auto-commit if files changed')
def autopep8(auto_commit):
    """Autopep8 modules."""

    def working_directory_dirty():
        """Return True if the git working directory is dirty."""
        return shell('git diff-index --quiet HEAD --', check=False).returncode != 0

    if auto_commit and working_directory_dirty():
        msg = click.style('working directory dirty. please commit pending changes',
                          fg='yellow')
        raise EnvironmentError(msg)

    shell('autopep8 -i -r nixbot/ tests/')

    if auto_commit and working_directory_dirty():
        shell('git add -u')
        shell("git commit -m 'autopep8 (autocommit)'", check=False)


@main.command()
def test_readme():
    """Test README.rst to ensure it will render correctly in warehouse."""
    shell('python setup.py check -r -s')


@main.command()
def uninstall():
    """Uninstalls all Python dependencies."""

    patt = re.compile(r'\w+=(\w+)')

    packages = []

    for line in sp.run(('pip', 'freeze'), stdout=sp.PIPE).stdout.decode().splitlines():
        if '==' in line:
            package, *_ = line.split('==')

        match = patt.search(line)

        if match:
            *_, package = match.groups()

        packages.append(package)

    stdin = os.linesep.join(packages).encode()

    with NamedTemporaryFile() as fn:
        fn.write(stdin)
        fn.seek(0)
        shell(f'cat {fn.name} | xargs pip uninstall -y')


@main.command()
@click.option('--idempotent', is_flag=True, help='uninstall current packages before installing.')
def install(idempotent):
    """
    Install Python dependencies.
    """
    click.secho("make sure you're using pipenv for dependency management", fg='yellow')

    context = click.get_current_context()
    if idempotent:
        context.invoke(uninstall)

    shell('pip install -e .[dev]')


@main.command()
def dist():
    """Build source and wheel package."""
    context = click.get_current_context()
    context.invoke(clean, build=True)
    shell('python setup.py sdist')
    shell('python setup.py bdist_wheel')


@main.command()
def release():
    """Package and upload a release to pypi."""
    context = click.get_current_context()

    context.invoke(test_readme)
    context.invoke(publish_docs)
    context.invoke(tox)
    context.invoke(clean, all=True)

    shell('python setup.py sdist bdist_wheel')
    shell('twine upload dist/*')


def clean_build():
    """Remove build artifacts."""
    click.confirm('This will uninstall the nixbot cli. '
                  'You may need to run `pip install -e .` to reinstall it. '
                  'Continue?',
                  abort=True)

    shell('rm -fr build/')
    shell('rm -fr dist/')
    shell('rm -rf .eggs/')
    shell("find . -name '*.egg-info' -exec rm -fr {} +")
    shell("find . -name '*.egg' -exec rm -f {} +")


def clean_pyc():
    """Remove Python file artifacts."""
    shell("find . -name '*.pyc' -exec rm -f {} +")
    shell("find . -name '*.pyo' -exec rm -f {} +")
    shell("find . -name '*~' -exec rm -f {} +")
    shell("find . -name '__pycache__' -exec rm -fr {} +")


def clean_test():
    """Remove test and coverage artifacts."""
    shell('rm -fr .tox/')
    shell('rm -f .coverage')
    shell('rm -fr htmlcov/')


@main.command()
@click.option('--pyc', is_flag=True, help=clean_pyc.__doc__)
@click.option('--test', is_flag=True, help=clean_test.__doc__)
@click.option('--build', is_flag=True, help=clean_build.__doc__)
@click.option('--all', is_flag=True, help='Clean all files. This is the default')
def clean(pyc, test, build, all):
    """Remove all build, test, coverage and Python artifacts."""
    fn_flag = (
        (clean_pyc, pyc),
        (clean_test, test),
        (clean_build, build)
    )

    if all or not any((pyc, test, build)):
        clean_pyc()
        clean_test()
        clean_build()
    else:
        for fn, flag in fn_flag:
            if flag:
                fn()


@main.command()
@click.option('--capture/--no-capture', default=False, help='capture stdout')
@click.option('--pdb', is_flag=True, help='enter debugger on test failure')
@click.option('--mypy', is_flag=True, help='type-check source code')
def test(capture, pdb, mypy):
    """
    Run tests quickly with default Python.
    """
    pytest_flags = ' '.join([
        '-s' if not capture else '',
        '--pdb' if pdb else ''
    ])

    shell('py.test tests/' + ' ' + pytest_flags)

    if mypy:
        shell('mypy nixbot tests/ --ignore-missing-imports')


@main.command()
def tox():
    """Run tests in isolated environments using tox."""
    shell('tox')


@main.command()
@click.option('--no-browser', is_flag=True, help="Don't open browser after building report.")
def coverage(no_browser):
    """Check code coverage quickly with the default Python."""
    shell('coverage run --source nixbot -m pytest')
    shell('coverage report -m')
    shell('coverage html')

    if no_browser:
        return

    shell('open htmlcov/index.html')


@main.command()
@click.option('--no-browser', is_flag=True, help="Don't open browser after building docs.")
def docs(no_browser):
    """
    Generate Sphinx HTML documentation, including API docs.
    """
    shell('python -m nixbot.cli dev update_module_docstring')
    shell('rm -f docs/nixbot.rst')
    shell('rm -f docs/modules.rst')
    shell('rm -f docs/nixbot*')
    shell('sphinx-apidoc -o docs/ nixbot')

    with cd('docs'):
        shell('make clean')
        shell('make html')

    shell('cp -rf docs/_build/html/ public/')

    if no_browser:
        return

    shell('open public/index.html')


@main.command()
def publish_docs():
    """
    Compile docs and publish to GitHub Pages.

    Logic borrowed from `hugo <https://gohugo.io/tutorials/github-pages-blog/>`
    """

    if shell('git diff-index --quiet HEAD --', check=False).returncode != 0:
        shell('git status')
        raise EnvironmentError('The working directory is dirty. Please commit any pending changes.')

    if shell('git show-ref refs/heads/gh-pages', check=False).returncode != 0:
        # initialized github pages branch
        shell(dedent("""
            git checkout --orphan gh-pages
            git reset --hard
            git commit --allow-empty -m "Initializing gh-pages branch"
            git push gh-pages
            git checkout master
            """).strip())
        click.secho('created github pages branch', fg='green')

    # deleting old publication
    shell('rm -rf public')
    shell('mkdir public')
    shell('git worktree prune')
    shell('rm -rf .git/worktrees/public/')
    # checkout out gh-pages branch into public
    shell('git worktree add -B gh-pages public gh-pages')
    # generating docs
    context = click.get_current_context()
    context.invoke(docs, no_browser=True)
    # push to github
    with cd('public'):
        shell('git add .')
        shell('git commit -m "Publishing to gh-pages (automated)"', check=False)
        shell('git push origin gh-pages --force')

    remotes = shell('git remote -v', capture=True).stdout.decode()

    match = re.search('github.com:(\w+)/(\w+).git', remotes)

    if match:
        user, repo = match.groups()
        click.secho(f'Your documentation is viewable at '
                    f'https://{user}.github.io/{repo}',
                    fg='green')


@main.command()
def update_setup_requires():
    """Update required vendored libraries required for package installation."""
    shell('rm -rf setup_requires/')
    shell('pip install pipenv --target setup_requires')


@main.command()
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=8000)
def runserver(host, port):
    """Runs local development server using nixbot's own cli."""
    shell(f'python -m nixbot.cli runserver --host {host} --port {port}')


@main.command()
def vendor():
    """Vendor dependencies for cloudfoundry."""
    context = click.get_current_context()

    try:
        click.secho('freezing only required dependencies', fg='yellow')

        context.invoke(uninstall)

        shell('pipenv install')

        click.secho('dependencies frozen', fg='green')

        click.secho('vendoring dependencies', fg='yellow')

        shell('rm -rf vendor')
        shell('mkdir -p vendor')

        shell('pip freeze > requirements.txt')
        shell('pip download -r requirements.txt -d vendor --no-binary :all:')

        click.secho('dependencies vendored', fg='green')

    finally:

        click.secho('reinstalling uninstalled packages', fg='yellow')

        context.invoke(install, development=True, idempotent=True)

        click.secho('packages reinstalled', fg='green')


@main.command()
def deploy():
    """Deploy to cloudfoundry."""
    context = click.get_current_context()

    context.invoke(vendor)

    click.secho('deploying to cloudfront', fg='yellow')

    shell('cf push')

    click.secho('deployed', fg='green')


if __name__ == '__main__':
    main()
