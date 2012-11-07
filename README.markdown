[![Build Status](https://secure.travis-ci.org/dejw/vip.png)](http://travis-ci.org/dejw/vip)

`vip` is a simple library that makes your `python` and `pip` aware of existing
virtualenv underneath. In its design, it is inspired by Git and its way of
handling its repositories.


## Philosophy

In its concept `vip` is similar to `git`. It assumes that your virtualenv is
located in `.vip` directory, somewhere in the directory structure of your
project.

In addition to the `.vip` directory, it uses `requirements.txt` file, which
should list all dependent packages. Presence of this file allows to recreate
virtualenv later. It is should be included in a source control.

No need to source `bin/activate` any more!

## Usage

Initialization of a brand new virtual environment is as simple as typing:

    vip init [directory]

In addition, `init` command automatically detects presence of `requirements.txt`
file and installs all packages listed inside, which is useful, when you
checkout a new repository somewhere, and you want to recreate the environment.

Installing new packages can be done in two ways. After an update of your
'requirements.txt' file, you can run:

    vip install

to instruct vip to pick up packages from it. Basically, all it does is running:

    pip install -r requirements.txt

on your environment.

Also, you can also install packages individually:

    vip install requests fabric -i http://example.my.pypi/simple

To uninstall a package type:

    vip uninstall Package

With install/uninstall commands you can use any flag that is available in
corresponding pip install/uninstall commands.


When you want to use Python interpreter from your environment, just prefix it
with `vip`:

    vip python -c "print 'Hi!'"

In fact any command located in `.vip/bin` is available simply by prefixing its
name with `vip`. `vip` searches for `.vip` directory along the path up to the
root, and if it does find it, it delegates all command-line arguments to
desired executable inside `bin` directory.

You can find out where your environment is by typing:

    vip locate

which is useful for locating Python interpreter, and running it from shell:

    time `vip locate`/bin/python script.py

In this case, performance of interpreter execution will not be affected at all.

You can get rid of a virtual environment by typing:

    vip purge   # equivalent of rm -rf .vip

### Managing dependencies

Your direct dependencies should be listed in `requirements.txt` file, but every
time you install something using `(un)install` command `requirements.freeze.txt`
file is updated.

The contents of this file is roughly equivalent to the output of:

    vip pip --freeze > requirements.freeze.txt

Do not forget to include this file in next commit!


## Too much typing?

You can alias most frequently used commands to stop prefixing them constantly
with `vip`. Add this to your `~/.bashrc` file:

    alias python="`vip l`/bin/python"
    alias pip="`vip l`/bin/pip"

Note, that it will fail when there will be no `.vip` directory up to the root.


## Use-cases

### No root privileges

You can type `vip init` in your home directory, add aliases to your
`~/.bashrc` file and enjoy the new way of working with `python` and `pip` in a
shell, where you cannot install packages globally in the system.

`rvm` does the same thing.

### Self-contained projects

`requirements.txt` file allows to recreate environment when the project
location  changes, which is a simple workaround for experimental
`--relocatable` option for `virtualenv`.

In addition, You can actually use `requirements.txt` file as your install
requirements source for `setup.py` script.


## Limitations

To keep things simple, vip does not allow for user interactions with a child
process, so you cannot use interactive Python shell.

Simple workaround:

    `vip -l`/bin/python

Also, any pip uninstallations will fail, because user has to confirm deletion.
You can bypass this issue simply adding `-y` switch to uninstall command:

    vip pip uninstall -y tornado
    vip uninstall tornado       # -y is implied

## Installation

Simply type the following command into terminal to install the latest released
version:

    pip install vip


## Contribution

Feel free to file a bug report, or send a pull request. I will try my best to
look into it and merge your changes.