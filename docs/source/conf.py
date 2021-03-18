
from recommonmark.parser import CommonMarkParser
source_parsers = {
    '.md': CommonMarkParser,
}
source_suffix = ['.md']

import sphinx_rtd_theme
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]