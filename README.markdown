vip (Virtual Python) is a simple library that makes your `python` and `pip`
aware of existing virtualenv underneath. In its design, it is inspired by Git 
and its way of handling its repositories.

## Philosophy

In its concept `vip` is similar to `git`. It assumes that your virtualenv is 
located in `.vip` directory, somewhere in the directory structure of your 
project.

In addition to the `.vip` directory, `.vipdeps` file is created, which lists 
all installed packages. Presence of this file allows to recreate virtualenv
later. It is designed to be includes in source control.

The `.vipdeps` file is updated anytime you install a package in environment. 
In order to keep things simple, it has a format of requirements file used by
`pip`.

No need to source `bin/activate` file any more!

## Usage

Initialization of a brand new virtual environment is as simple as typing:

    vip --init [directory]

In addition, `init` command automatically detects presence of `.vipdeps` file
and installs all packages listed inside, which is useful, when you checkout a
new repository somewhere, and you want to recreate the environment.

When you want to use Python interpreter from your environment, just prefix it
with `vip`:

    vip python -c "print 'Hi!'"

`pip` command is available in the same way:

    vip pip install requests fabric -i http://example.my.pypi/simple

In fact any command located in `.vip/bin` is available simply by prefixing its
name with `vip`. `vip` searches for `.vip` directory along the path up to the
root, and if it does find it, it delegates all command-line arguments to
desired executable inside `bin` directory.

You can find out where your environment is by typing:

    vip --locate

which is useful for locating Python interpreter, and running it from shell:

    time `vip --locate`/python script.py

In this case, performance of interpreter execution will not be affected at all.

You can get rid of a virtual environment by typing:

    vip --purge   # equivalent of rm -rf .vip

### Updating `.vipdeps` file

In most common case dependency listing is updated automatically, so whenever
you run `vip pip (un)install` or `vip easy_install` command, `.vipdeps` file is
updated on successful completion.

In case your dependencies changed in some other way, you can update dependency
listing by typing:

    vip --update   # which is roughly equivalent to vip pip freeze > .vipdeps


## Too much typing?

You can alias most frequently used commands to stop prefixing them constantly 
with `vip`. Add this to your `~/.bashrc` file:

    alias python="vip python"
    alias pip="vip pip"

Note, that it will fail when there will be no `.vip` directory up to the root.

## Use-cases

### No root privileges

You can type `vip init` in your home directory, add aliases to your `~/.bashrc` 
file and enjoy the new way of working with `python` and `pip` in a shell, where 
you cannot install packages globally in the system.

`rvm` does the same thing. 

### Self-contained projects

`.vipdeps` file allows to recreate environment when the project location 
changes, which is a simple workaround for experimental `--relocatable` option 
for `virtualenv`.

In addition, You can actually use `.vipdeps` file as your install requirements
source for `setup.py` script. 

## Installation

Simply type the following command into terminal to install the latest released
version:

    pip install vip

## Contribution

Feel free to file a bug report, or send a pull request. I will try my best to
look into it and merge your changes.