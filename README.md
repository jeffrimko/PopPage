# PopPage: a small static website generator
PopPage is a simple command-line utility that can generate static websites (or any documents) by applying content to Jinja2 templates. The content can be supplied via files or directly on the command-line. For more information on using PopPage, please refer to the documentation in the main `poppage.py` file.

The following is a quick example of using PopPage:

  - Template file (`template.jinja2`):

        `Hello {{name}}!`

  - PopPage command:

        `poppage template.jinja2 --string=world name`

  - Output to `stdout`:

        `Hello world!`

PopPage is written in Python 2.7 using the following third-party libraries:

  - [Docopt](http://docopt.org/)
  - [Jinja2](http://jinja.pocoo.org/)
  - [PyYaml](http://pyyaml.org/)
