# PopPage: a small static website generator

## Introduction
PopPage is a simple command-line utility that can generate static websites (or any documents) by applying content to [Jinja2](http://jinja.pocoo.org/) templates. The content can be supplied via files or directly on the command-line. For more information on using PopPage, please refer to the documentation in the main `poppage.py` file.

## Examples
The following is a quick example of using PopPage:

  - Template file (`template.jinja2`):

        Hello {{foo}}!

  - PopPage command:

        poppage template.jinja2 --string foo world

  - Output to `stdout`:

        Hello world!

## Dependencies
PopPage is written in [Python 2.7](https://www.python.org/) using the following third-party libraries:

  - [Docopt](http://docopt.org/)
  - [Jinja2](http://jinja.pocoo.org/)
  - [PyYaml](http://pyyaml.org/)
