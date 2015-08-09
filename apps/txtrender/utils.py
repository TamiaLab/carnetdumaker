"""
HTML cleaning and rendering module.
"""

import re
from urllib import parse as urlparse

import html
import bleach

from bs4 import BeautifulSoup, Comment, CData, NavigableString
from html5lib.html5parser import ParseError

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name

from django.template import loader
from django.utils.text import slugify
from django.utils.html import escape as escape_html

from .settings import (DEFAULT_TABULATION_SIZE,
                       DISPLAY_LINE_NUMBERS_BY_DEFAULT,
                       PYGMENTS_CSS_STYLE_NAME,
                       PYGMENTS_CSS_NAMESPACE)


# List of all allowed tags
ALLOWED_TAGS = {
    # SECTIONS:
    'section', 'nav', 'article', 'aside', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hgroup', 'header', 'footer', 'address',
    # BLOCS:
    'p', 'hr', 'pre', 'blockquote', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'figure', 'figcaption', 'div',
    # TEXTS:
    'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp', 'kbd', 'sub',
    'sup', 'i', 'b', 'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'br', 'wbr',
    # EDITION:
    'ins', 'del',
    # INCLUDE:
    'img', 'map', 'area',
    # TABLE:
    'table', 'caption', 'colgroup', 'col', 'tbody', 'thead', 'tfoot', 'tr', 'td', 'th',
    # INTERACTION:
    'details', 'summary',
    # CUSTOM:
    'not',
    # OLD:
    'strike', 'acronym', 'tt',
    # EXTRA:
    'audio', 'video', 'iframe'
}


# Map of all old HTML4 tags and corresponding HTML5 replacement
OLD_TAG_REPLACEMENTS = {
    'strike': 'del',
    'acronym': 'abbr',
    'tt': 'kbd',
    # Require CSS: big font center
}


# Map of all allowed attributes for a given tag
ALLOWED_ATTRS = {
    # GLOBAL ATTRIBUTES:
    '*': {'class', 'id', 'title', 'dir'},
    # SECTIONS:
    'section': (),
    'nav': (),
    'article': (),
    'aside': (),
    'h1': (),
    'h2': (),
    'h3': (),
    'h4': (),
    'h5': (),
    'h6': (),
    'hgroup': (),
    'header': (),
    'footer': (),
    'address': (),  # Really sections?
    # BLOCS:
    'p': (),
    'hr': (),
    'pre': (),
    'blockquote': {'cite', },
    'ol': {'reversed', 'start', 'type'},
    'ul': (),
    'li': {'value', },
    'dl': (),
    'dt': (),
    'dd': (),
    'figure': (),
    'figcaption': (),
    'div': (),
    # TEXTS:
    'a': {'download', 'href', 'ping', 'rel', 'target', 'hreflang', 'type'},
    'em': (),
    'strong': (),
    'small': (),
    's': (),
    'cite': (),
    'q': {'cite', },
    'dfn': (),
    'abbr': (),
    'data': {'value', },
    'time': {'datetime', 'pubdate'},
    'code': (),
    'var': (),
    'samp': (),
    'kbd': (),
    'sub': (),
    'sup': (),
    'i': (),
    'b': (),
    'u': (),
    'mark': (),
    'ruby': (),
    'rt': (),
    'rp': (),
    'bdi': (),
    'bdo': (),
    'span': (),
    'br': (),
    'wbr': (),
    # EDITION:
    'ins': {'cite', 'datetime'},
    'del': {'cite', 'datetime'},
    # INCLUDE:
    'img': {'alt', 'height', 'src', 'width'},
    'map': (),
    'area': {'alt', 'coords', 'download', 'href', 'hreflang', 'rel', 'shape', 'target', 'type'},
    # TABLE:
    'table': (),
    'caption': (),
    'colgroup': {'span', },
    'col': {'span', },
    'tbody': (),
    'thead': (),
    'tfoot': (),
    'tr': (),
    'td': {'colspan', 'headers', 'rowspan'},
    'th': {'colspan', 'headers', 'rowspan', 'scope'},
    # INTERACTION:
    'details': {'open', },
    'summary': (),
    # CUSTOM:
    'not': (),
    # OLD:
    'strike': (),
    'acronym': (),
    'tt': (),
    # EXTRA:
    'audio': {'autoplay', 'buffered', 'controls', 'loop', 'muted', 'preload', 'src', 'volume'},
    'video': {'autoplay', 'buffered', 'controls', 'height', 'loop', 'muted', 'poster', 'preload', 'src', 'width'},
}


# List of attributes name capable of storing URI
URI_ATTR_NAMES = (
    'href', 'src', 'cite', 'action',
    'longdesc', 'poster', 'background',
    'datasrc', 'dynsrc', 'lowsrc', 'ping',
    'poster', 'xlink:href', 'xml:base'
)


# List of allowed protocols
ALLOWED_PROTOCOLS = {
    'ftp', 'stfp',
    'http', 'https',
    'mailto',
    'irc', 'xmpp',
    'rsync', 'ssh',
    'rtsp'
}


# ASCII art to entities replacement map.
ENTITY_REPLACEMENTS = {
    '...': u'\u2026',
}


def remove_tags_if_not_allowed(allowed_tags, tag_names, allowed):
    """
    Remove the given tags from the allowed tags set if not allowed.
    :param allowed_tags: The set of allowed tags.
    :param tag_name: The list of tags name to be removed if not allowed.
    :param allowed: True if allowed, False otherwise.
    :return: None
    """
    for tag_name in tag_names:
        if not allowed and tag_name in allowed_tags:
            allowed_tags.remove(tag_name)


def get_unique_slug(value, slug_dict):
    """
    Return the unique slug for the given text value.
    :param value: Input text to be slugiflied.
    :param slug_dict: A dictionary of already used slug.
    :return The unique slug for the given text.
    """
    slug = slugify(value)
    final_slug = slug
    counter = 2
    while final_slug in slug_dict:
        final_slug = '%s-%d' % (slug, counter)
        counter += 1
    return final_slug


# Regex for code blocks
RE_CODE_BLOCKS = re.compile(r'(<\s*code[^>]*>)(.*)(?=<\s*\/\s*code\s*>)(<\s*\/\s*code\s*>)')


def preprocess_code_blocks(input_html):
    """
    Preprocess code blocks to avoid HTML parsing of them.
    """

    def escape_code_blocks(matchobj):
        """
        Escape the HTML content of ``\1``.
        """
        open_tag = matchobj.group(1)
        inner_code = escape_html(matchobj.group(2))
        close_tag = matchobj.group(3)
        print('OPEN', open_tag)
        print('INNER', inner_code)
        print('CLOSE', close_tag)
        return open_tag + inner_code + close_tag

    # Escape the content
    return RE_CODE_BLOCKS.sub(escape_code_blocks, input_html)


def parse_html(input_html):
    """
    Parse the given HTML input and return the document tree without any extra html/head/body tags.
    :param input_html: The input HTML source.
    :return: The parsed document tree.
    """

    # Parse the HTML document
    try:
        # Warning: Html5Lib is catching out-of-order and unclosed tags,
        # so markup can't leak out of comments and break the rest of the page.
        soup = BeautifulSoup(input_html, 'html5lib')
    except ParseError as e:
        # Should never happen with strict=False
        raise e

    # Get only the body inner html if the document was a full HTML document
    if soup.html is not None:
        soup.html.head.decompose()
        soup.html.body.unwrap()
        soup.html.unwrap()

    # Return the root document
    return soup


def render_html_source(document_tree, prettify=False):
    """
    Render the given document tree as HTML.
    :param document_tree: The document tree to be rendered.
    :param prettify: Set to ``True`` to enable pretty ouput with indentation and so.
    :return The rendered HTML source.
    """

    # Render the cleaned HTML
    # return content.encode_contents(formatter='html')
    if prettify:
        return document_tree.prettify(formatter='html')
    else:
        return document_tree.decode(formatter='html')


def filter_allowed_tags_and_attrs(document_tree, allowed_tags, allowed_attrs, allowed_attrs_global):
    """
    Filter the document tree based on the list of allowed tags and attributes.
    :param document_tree: The document tree to be cleaned.
    :param allowed_tags: The list of allowed tags.
    :param allowed_attrs: The map of allowed attributes by tag names.
    :param allowed_attrs_global: The list of attributes allowed for any tags.
    :return: None
    """

    # Whitelist based tags filtering
    for tag in document_tree.findAll():

        # Normalize the tag name
        tag_name = tag.name.lower()
        tag.name = tag_name

        # Check tags whitelist
        if tag_name not in allowed_tags:

            # Tag not allowed, remove it from the document
            tag.decompose()
        else:

            # Whitelist based attributes filtering
            new_attrs = {}  # The new (clean) attributes dict
            for attr_name, attr_value in tag.attrs.items():

                # Normalize the attribute name
                attr_name = attr_name.lower()

                # Check attributes whitelist (tag specific and global)
                if ((tag_name in allowed_attrs and attr_name in allowed_attrs[tag_name])
                        or attr_name in allowed_attrs_global):

                    # Store the cleaned attribute
                    new_attrs[attr_name] = attr_value

            # Assign the new attributes dictionary
            tag.attrs = new_attrs


def fix_old_tags(document_tree, old_tag_replacements):
    """
    Fix old HTML4 tag by replacing them with HTML5 equivalent.
    :param document_tree: The document tree to be fixed.
    :param old_tag_replacements: The map of old:new tags name.
    :return: None
    """

    # Search for old tags
    for tag in document_tree.findAll(name=old_tag_replacements.keys()):

        # Fix the tag name
        tag.name = old_tag_replacements[tag.name]


def strip_comments(document_tree):
    """
    Strip all HTML comments to avoid browser-dependent XSS
    :param document_tree: The document tree to be cleaned.
    :return: None
    """

    # Remove all HTML comments to avoid browser-dependent XSS
    for comment in document_tree.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()


def strip_cdata(document_tree):
    """
    Strip all HTML CData to avoid browser-dependent XSS
    :param document_tree: The document tree to be cleaned.
    :return: None
    """

    # Remove all HTML CData to avoid browser-dependent XSS
    for cdata in document_tree.findAll(text=lambda text: isinstance(text, CData)):
        cdata.extract()


def force_rel_no_follow(document_tree):
    """
    Force all link to be `rel="nofollow"`` to avoid spam.
    :param document_tree: The document tree to be cleaned.
    :return: None
    """

    # Get all links
    for link in document_tree.findAll(name='a'):

        # Fix the link relation
        link.attrs['rel'] = 'nofollow'


def sanitize_uri(document_tree, uri_attr_names, allowed_protocols):
    """
    Sanitize URI to avoid XSS.
    :param document_tree: The document tree to be cleaned.
    :param uri_attr_names: The list of URI attribute names to be cleaned.
    :param allowed_protocols: The lis of allowed protocols.
    :return: None
    """

    # Try to clean all tags for best security
    for tag in document_tree.findAll():

        # Check all uri attributes
        for attr_name in uri_attr_names:

            # Continue if the attribute don't exist
            if attr_name not in tag.attrs:
                continue

            # Get the attribute value
            uri = tag.attrs[attr_name].strip()

            # Shortcut for current URI
            if not uri:
                continue

            # Avoid any whitespace or XSS null-byte injection
            uri = re.sub(r"[`\000-\040\177-\240\s]+", '', uri)
            uri = uri.replace(u'\ufffd', '')

            # Parse the URI
            scheme, netloc, path, query, fragment = urlparse.urlsplit(uri)

            # Add protocol if not specified
            if netloc and not scheme:
                scheme = 'http'

            # Whitelist based filtering of protocol
            if scheme and scheme not in allowed_protocols:
                del tag.attrs[attr_name]
                continue

            # Saved the clean uri
            uri = urlparse.urlunsplit((scheme, netloc, path, query, fragment))
            tag.attrs[attr_name] = uri


# List of block who require auto paragraph
AUTO_P_BLOCK_TAGS = (
    'article',
    'aside',
    'blockquote',
    'dd',
    'div',
    'dl',
    'figure',
    'footer',
    'header',
    'ol',
    'ul',
    'pre',
    'section',
    'details',
    'summary',
)


# List of inline tag names
INLINE_TAG_NAMES = {
    # TEXTS:
    'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp', 'kbd', 'sub',
    'sup', 'i', 'b', 'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'br', 'wbr',
    # EDITION:
    'ins', 'del',
    # INCLUDE:
    'img', 'map',
    # CUSTOM:
    'not',
    # OLD:
    'strike', 'acronym', 'tt',
}


# Regex for matching consecutive blank lines
RE_BLANK_LINES = re.compile(r'(?:\r\n?|\n)(?:\s*(?:\r\n?|\n))+')


def _do_auto_p(document_tree, root_tag):
    """
    Take a tag and wrap all consecutive inline tags in a p tag.
    :param document_tree: The document tree.
    :param root_tag: The root tag for the processing.
    :return: None
    """
    cur_inline_group = []

    # For each immediate children
    for child in root_tag.children:

        # Special handling of raw text
        if isinstance(child, NavigableString):

            # Break paragraph with blank line in multiples paragraphs
            paragraphs = RE_BLANK_LINES.split(child.string)

            # Handle multi-paragraphs text
            nb_paragraphs = len(paragraphs)
            if nb_paragraphs > 1:

                # The first paragraph need special handling
                p = document_tree.new_tag('p')
                for tag in cur_inline_group:
                    p.append(tag)
                p.append(NavigableString(paragraphs[0]))
                cur_inline_group = []
                child.insert_before(p)

                # Add other paragraph (except the last one)
                for index in range(1, nb_paragraphs - 1):
                    p = document_tree.new_tag('p')
                    p.append(NavigableString(paragraphs[0]))
                    child.insert_before(p)

                # The last paragraph need special handling
                cur_inline_group.append(NavigableString(paragraphs[-1]))

                # Avoid infinite loop
                # TODO NUKE THE WHOLE CODE OF THIS MODULE AND GTFO!
                # HTML PARAGRAPH GENERATION IS FUCKING BROKEN BY DESIGN.
                # THIS ALGORITHM MODIFY THE TREE DURING ITERATION AND
                # BS4 DO NOT PROVIDE ANY INFORMATION ABOUT THE FUCKING
                # INFINITE LOOP CREATED BY INSERTING ELEMENTS BEFORE THE
                # CURRENT ITERATED ELEMENT OF THE GENERATOR.
                # I FUCKING PREFER TO WRITE MY OWN TEXTUAL PARSER THAN LOOSING
                # ONE DAY MORE WITH THIS FUCKING HTML LIBRARY. I QUIT!
                child.extract()  # Fuck this and everything else

            else:
                cur_inline_group.append(child.extract())

            continue

        # Group all inline tags together until a block tag is found
        if child.name in INLINE_TAG_NAMES:
            cur_inline_group.append(child.extract())
        elif cur_inline_group:
            # Wrap all inline tags into a paragraph
            p = document_tree.new_tag('p')
            for tag in cur_inline_group:
                p.append(tag)
            cur_inline_group = []
            child.insert_before(p)

    # Wrap remaining tag into a paragraph
    if cur_inline_group:
        p = document_tree.new_tag('p')
        for tag in cur_inline_group:
            p.append(tag)
        root_tag.append(p)


def make_auto_paragraph(document_tree):
    """
    Make auto paragraphs.
    :param document_tree: The document tree to be processed.
    :return: None
    """

    # Process the root level document
    _do_auto_p(document_tree, document_tree)

    # Pass over all block tags who need auto paragraph
    for block_tag in document_tree.findAll(name=AUTO_P_BLOCK_TAGS):
        _do_auto_p(document_tree, block_tag)


def highlight_code_blocks(document_tree):
    """
    Highlight code blocks with ``language`` attribute in the document.
    :param document_tree: The document tree to be analyzed.
    :return: None
    """

    # Handle code block with "language" attribute for highlighting
    for tag in document_tree.findAll('code'):

        # Detect "language" attribute
        if 'language' in tag.attrs:

            # Get optional attributes
            linenos = 'table' if bool(tag.attrs.pop('linenos', DISPLAY_LINE_NUMBERS_BY_DEFAULT)) else False
            hl_lines = tag.attrs.pop('hl_lines', '').strip()
            try:
                if hl_lines:
                    hl_lines = [int(l) for l in hl_lines.split(',')]
                else:
                    hl_lines = []
            except ValueError:
                hl_lines = []
            try:
                linenostart = int(tag.attrs.pop('linenostart', 1))
            except ValueError:
                linenostart = 1

            # Highlight the code
            language = tag.attrs.pop('language')
            lexer = get_lexer_by_name(language, stripall=True,
                                      tabsize=DEFAULT_TABULATION_SIZE,
                                      encoding='utf-8')
            style = get_style_by_name(PYGMENTS_CSS_STYLE_NAME)
            formatter = HtmlFormatter(style=style,
                                      linenos=linenos,
                                      hl_lines=hl_lines,
                                      linenostart=linenostart,
                                      cssclass=PYGMENTS_CSS_NAMESPACE,
                                      anchorlinenos=True,
                                      lineanchors='line')
            source_code = tag.string
            html_for_display = highlight(source_code, lexer, formatter)
            css_for_display = formatter.get_style_defs()

            # Turn the code tag into a placeholder
            code_block = parse_html('<style>%s</style>\n%s' % (css_for_display, html_for_display))
            tag.replace_with(code_block.html.body.table)


def handle_custom_tags(document_tree):
    """
    Handle cusom tags like ``<not>``.
    :param document_tree: The document tree to be analyzed.
    :return: None
    """

    # Handle custom HTML tag ``<not>``
    for tag in document_tree.findAll('not'):
        tag.name = 'span'
        tag.attrs = {'style': 'text-decoration:overline;'}


def grab_all_ids(document_tree):
    """
    Grab all ``id`` in the document and return them as a set.
    :param document_tree: The document tree to be analyzed.
    :return: A set of all ``id`` found in the document tree.
    """

    # Get all existing IDs
    ids_dict = set()
    for tag in document_tree.findAll(id=True):
        tag_id = tag['id']
        if tag_id not in ids_dict:
            ids_dict.add(tag_id)

    # Return the ids list
    return ids_dict


def replace_entities(document_tree, entity_replacements):
    """
    Replace entities in the document like ascii art and smiley.
    :param document_tree: The document tree to be analyzed.
    :param entity_replacements: The entity replacements map.
    :return: None
    """

    # Iterate over all texts in the document
    for text in document_tree.findAll(text=lambda t: isinstance(t, NavigableString)):

        # Dont mess with code block
        if text.parent.name == 'code':
            continue

        # Replace all entities
        # TODO handle emoticons and entities replacement here


def render_html(input_html,
                allowed_tags=None,
                old_tag_replacements=None,
                allowed_attrs=None,
                uri_attr_names=None,
                allowed_protocols=None,
                entity_replacements=None,
                allow_sections_tags=True,
                allow_quotes=True,
                allow_lists=True,
                allow_figures=True,
                allow_links=True,
                force_nofollow=True,
                allow_advanced_format=True,
                allow_bidir_format=True,
                allow_images=True,
                allow_tables=True,
                allow_extra=False,
                allow_iframe=False):
    """
    Render the given HTML text as HTML (wordpress-like filtering). Default settings are user-proof / production ready.
    :param input_html: The input HTML (not safe).
    :param allowed_tags: Allowed HTML tag's names list.
    :param allowed_attrs: Allowed HTML attribute's names per tag's name dictionary.
    :param force_nofollow: Set to ``False`` to avoid overwriting all link relatio to ``nofollow``.
    :return: The rendered HTML output text.
    """

    # Shortcut for empty documents
    input_html = input_html.strip()
    if not input_html:
        return ''

    # Default rules
    allowed_tags = set(allowed_tags or ALLOWED_TAGS)
    old_tag_replacements = dict(old_tag_replacements or OLD_TAG_REPLACEMENTS)
    allowed_attrs = dict(allowed_attrs or ALLOWED_ATTRS)
    uri_attr_names = set(uri_attr_names or URI_ATTR_NAMES)
    allowed_protocols = set(allowed_protocols or ALLOWED_PROTOCOLS)
    entity_replacements = dict(entity_replacements or ENTITY_REPLACEMENTS)
    allowed_attrs_global = allowed_attrs.pop('*', ())

    # Filter tags according to permissions
    remove_tags_if_not_allowed(allowed_tags, ('section', 'nav', 'article',
                                              'aside', 'h1', 'h2', 'h3',
                                              'h4', 'h5', 'h6', 'hgroup',
                                              'header', 'footer'), allow_sections_tags)
    remove_tags_if_not_allowed(allowed_tags, ('q', 'blockquote'), allow_quotes)
    remove_tags_if_not_allowed(allowed_tags, ('ol', 'ul', 'li', 'dl', 'dt', 'dd'), allow_lists)
    remove_tags_if_not_allowed(allowed_tags, ('figure', 'figcaption'), allow_figures)
    remove_tags_if_not_allowed(allowed_tags, ('a',), allow_links)
    remove_tags_if_not_allowed(allowed_tags, ('address', 'pre', 'cite', 'dfn',
                                              'abbr', 'data', 'time', 'code',
                                              'var', 'samp', 'kbd', 'sub',
                                              'sup', 'mark', 'ins', 'del',
                                              'not', 'details', 'summary',
                                              'acronym'), allow_advanced_format)
    remove_tags_if_not_allowed(allowed_tags, ('ruby', 'rt', 'rp', 'bdi', 'bdo'), allow_bidir_format)
    remove_tags_if_not_allowed(allowed_tags, ('img', 'map', 'area'), allow_images)
    remove_tags_if_not_allowed(allowed_tags, ('table', 'caption', 'colgroup',
                                              'col', 'tbody', 'thead', 'tfoot',
                                              'tr', 'td', 'th'), allow_tables)
    remove_tags_if_not_allowed(allowed_tags, ('audio', 'video'), allow_extra)
    remove_tags_if_not_allowed(allowed_tags, ('iframe',), allow_iframe)


    # Preprocess code block
    # input_html = preprocess_code_blocks(input_html)

    # Parse the HTML document
    document_tree = parse_html(input_html)

    # Whitelist based tags and attributes filtering
    filter_allowed_tags_and_attrs(document_tree, allowed_tags, allowed_attrs, allowed_attrs_global)

    # Special handling of style/class ?

    # Fix old HTML4 tags
    fix_old_tags(document_tree, old_tag_replacements)

    # Strip comments and CDATA to avoid XSS
    strip_comments(document_tree)
    strip_cdata(document_tree)

    # Force rel=nofollow if requested
    if force_nofollow:
        force_rel_no_follow(document_tree)

    # Sanitize URI
    sanitize_uri(document_tree, uri_attr_names, allowed_protocols)

    # Handle auto paragraph
    # _make_auto_paragraph(document_tree)

    # Replace all entities (ascii art, smileys, etc)
    # replace_entities(document_tree, entity_replacements)

    # Handle code block with "language" attribute for highlighting
    # _highlight_code_blocks(document_tree)

    # Handle custom HTML tag ``<not>``
    handle_custom_tags(document_tree)

    # Get all IDs in document
    # ids_dict = _grab_all_ids(document_tree)

    # Render the cleaned HTML
    output_html = render_html_source(document_tree)

    # Return the result
    return output_html


def render_quote(content,
                 from_author=None,
                 from_url=None,
                 pull_right=False,
                 template_name='txtrender/quote.html',
                 extra_context=None):
    """
    Render the given content (html safe) in a quote block.
    :param content: The HTML content (safe).
    :param from_author: The source author (optional).
    :param from_url: The source author url (optional).
    :param pull_right: Set to ``True`` to use right alignment instead of left alignment.
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: str with the HTML render quote block.
    """
    context = {
        'content': content,
        'from_author': from_author,
        'from_url': from_url,
        'pullright': pull_right
    }
    if extra_context is not None:
        context.update(extra_context)
    return loader.render_to_string(template_name, context)


def strip_html(html_text):
    """
    Strip any HTML tag and decode HTML entities.
    :param html_text: The input HTML text.
    """
    no_tags_res = bleach.clean(html_text, tags=[], attributes=[], styles=[], strip=True, strip_comments=True)
    return html.unescape(no_tags_res)
