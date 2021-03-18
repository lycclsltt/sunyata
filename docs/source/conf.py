from recommonmark.parser import CommonMarkParser
source_parsers = {
    '.md': CommonMarkParser,
}

project = 'agileutil'
copyright = '2021, tank'
author = 'tank'

# The full version, including alpha/beta/rc tags
release = 'v0.0.1'

source_suffix = ['.md']

import sphinx_rtd_theme
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]