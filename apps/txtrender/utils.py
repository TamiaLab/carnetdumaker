"""
HTML cleaning and rendering module.
"""

import calendar

from skcode import (parse_skcode,
                    render_to_html,
                    render_to_text)
from skcode.tags import (DEFAULT_RECOGNIZED_TAGS,
                         ErroneousTextTagOptions,
                         TextTagOptions,
                         NewlineTagOptions,
                         HardNewlineTagOptions)
from skcode.utility import (make_paragraphs,
                            extract_footnotes,
                            render_footnotes_html,
                            render_footnotes_text,
                            extract_titles,
                            make_titles_hierarchy,
                            make_auto_title_ids,
                            setup_smileys_replacement,
                            setup_cosmetics_replacement)
from skcode.tools import escape_attrvalue

from django.template import loader
from django.contrib.staticfiles.templatetags.staticfiles import static

from .settings import EMOTICONS_IMG_DIR


def copy_tags_if_allowed(tags, tags_array_in, tags_array_out, allowed):
    """
    Copy all ``tags`` from the ``tags_array_in`` to the ``tags_array_out`` if ``allowed`` is True.
    :param tags: The tag names list to be copied if allowed.
    :param tags_array_in: Input tags declaration dictionary.
    :param tags_array_out: Output tags declaration dictionary.
    :param allowed: Set to True to copy tags, or to False to do nothing.
    """
    if allowed:
        for tag_name in tags:
            tags_array_out[tag_name] = tags_array_in[tag_name]


# Recursive helper for HTML rendering
def recursive_render_title_html(title_groups, output):
    for parent_title, sub_titles in title_groups:
        title_id, tree_node, title_level = parent_title
        output.append('<li>')
        output.append('<a href="#%s">%s</a>' % (title_id, tree_node.get_raw_content()))
        if sub_titles:
            output.append('<ul>')
            recursive_render_title_html(sub_titles, output)
            output.append('</ul>')
        output.append('</li>')
    return output


# Recursive helper for text rendering
def recursive_render_title_text(title_groups, output, indent=0):
    for parent_title, sub_titles in title_groups:
        title_id, tree_node, title_level = parent_title
        output.append('%s %s' % ('#' * indent, tree_node.get_raw_content()))
        recursive_render_title_text(sub_titles, output, indent + 1)
    return output


def render_document(input_text,
                    allow_titles=False,
                    allow_code_blocks=False,
                    allow_alerts_box=False,
                    allow_text_formating=False,
                    allow_text_extra=False,
                    allow_text_alignments=False,
                    allow_text_directions=False,
                    allow_text_modifiers=False,
                    allow_text_colors=False,

                    allow_spoilers=False,
                    allow_figures=False,
                    allow_lists=False,
                    allow_todo_lists=False,
                    allow_definition_lists=False,
                    allow_tables=False,

                    allow_quotes=False,
                    allow_footnotes=False,
                    allow_acronyms=False,
                    allow_links=False,
                    allow_medias=False,

                    allow_cdm_extra=False,

                    force_nofollow=True,
                    preview_mode=False,
                    hard_newline=False,
                    render_text_version=False,
                    render_extra_dict=False,
                    merge_footnotes_html=False,
                    merge_footnotes_text=False,
                    make_auto_paragraphs=True):
    """
    Render the given document as HTML, text (if requested) and output extra runtime information.
    :param input_text: The input document text (not safe).
    """

    # Shortcut for empty documents
    input_text = input_text.strip()
    if not input_text:
        return '', '', {
            'footnotes_html': '',
            'footnotes_text': '',
            'summary_html': '',
            'summary_text': '',
        }

    # Filter tags according to permissions
    allowed_tags = {}
    copy_tags_if_allowed(('h1', 'h2', 'h3',
                          'h4', 'h5', 'h6'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_titles)
    copy_tags_if_allowed(('code', 'python', 'cpp',
                          'java', 'html', 'php'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_code_blocks)
    copy_tags_if_allowed(('alert', 'error', 'danger',
                          'warning', 'info', 'success',
                          'note', 'question'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_alerts_box)
    copy_tags_if_allowed(('b', 'bold', 'strong',
                          'i', 'italic', 'em',
                          's', 'strike', 'del',
                          'u', 'underline', 'ins',
                          'sub', 'sup', 'pre',
                          'icode', 'kbd', 'keyboard',
                          'glow', 'highlight', 'mark',
                          'cite', 'not'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_text_formating)
    copy_tags_if_allowed(('nobbc', 'noparse', 'hr', 'br'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_text_extra)
    copy_tags_if_allowed(('center', 'left', 'right'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_text_alignments)
    copy_tags_if_allowed(('bdo', 'ltr', 'rtl'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_text_directions)
    copy_tags_if_allowed(('lowercase', 'uppercase', 'capitalize'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_text_modifiers)
    copy_tags_if_allowed(('color', 'black', 'blue',
                          'gray', 'green', 'orange',
                          'purple', 'red', 'white', 'yellow'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_text_colors)
    copy_tags_if_allowed(('spoiler', 'hide', 'ispoiler'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_spoilers)
    copy_tags_if_allowed(('figure', 'figcaption'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_figures)
    copy_tags_if_allowed(('list', 'ul', 'ol', 'li'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_lists)
    copy_tags_if_allowed(('todolist', 'task'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_todo_lists)
    copy_tags_if_allowed(('dl', 'dt', 'dd'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_definition_lists)
    copy_tags_if_allowed(('table', 'tr', 'th', 'td'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_tables)
    copy_tags_if_allowed(('quote', 'blockquote'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_quotes)
    copy_tags_if_allowed(('footnote', 'fn', 'fnref'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_footnotes)
    copy_tags_if_allowed(('abbr', 'acronym'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_acronyms)
    copy_tags_if_allowed(('anchor', 'goto', 'url', 'link', 'email'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_links)
    copy_tags_if_allowed(('img', 'youtube'), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_medias)
    # copy_tags_if_allowed(('', ''), DEFAULT_RECOGNIZED_TAGS, allowed_tags, allow_cdm_extra)

    # Handle preview_mode and hard_newline options
    erroneous_text_opts = ErroneousTextTagOptions() if preview_mode else TextTagOptions()
    newlines_opts = HardNewlineTagOptions() if hard_newline else NewlineTagOptions()

    # Parse the document
    document = parse_skcode(input_text,
                            allow_tagvalue_attr=True,
                            allow_self_closing_tags=True,
                            erroneous_text_node_opts=erroneous_text_opts,
                            newline_node_opts=newlines_opts,
                            drop_unrecognized=False,
                            texturize_unclosed_tags=False)

    # Setup smileys and cosmetics replacement
    def _base_url(filename):
        return static(EMOTICONS_IMG_DIR + filename)
    setup_cosmetics_replacement(document)
    setup_smileys_replacement(document, _base_url)

    # Make paragraphs
    if make_auto_paragraphs:
        make_paragraphs(document)

    # Make auto titles IDs
    make_auto_title_ids(document)

    # Handle footnotes
    if allow_footnotes and (render_extra_dict or merge_footnotes_html or merge_footnotes_text):
        footnotes = extract_footnotes(document)
        footnotes_output_html = render_footnotes_html(footnotes)
        footnotes_output_text = render_footnotes_text(footnotes) if render_text_version else ''
    else:
        footnotes_output_html = ''
        footnotes_output_text = ''

    # Extra information dictionary
    if render_extra_dict:

        # Extract all titles
        titles = extract_titles(document)

        # Turn the titles list into a hierarchy
        titles_hierarchy = make_titles_hierarchy(titles)

        # Render titles hierarchy
        html_inner = '\n'.join(recursive_render_title_html(titles_hierarchy, []))
        titles_summary_output_html = '<ul>\n%s\n</ul>\n' % html_inner if html_inner else ''
        titles_summary_output_text = '\n'.join(recursive_render_title_text(titles_hierarchy, [])) if render_text_version else ''

    else:
        titles_summary_output_html = ''
        titles_summary_output_text = ''

    # Render the document
    content_html = render_to_html(document, force_nofollow)
    content_text = render_to_text(document) if render_text_version else ''

    # Merge footnotes if requested
    if merge_footnotes_html and footnotes_output_html:
        content_html += '<hr>\n' + footnotes_output_html
    if merge_footnotes_text and footnotes_output_text:
        content_text += '----------\n\n' + footnotes_output_text

    # Return the result
    return content_html, content_text, {
        'footnotes_html': footnotes_output_html,
        'footnotes_text': footnotes_output_text,
        'summary_html': titles_summary_output_html,
        'summary_text': titles_summary_output_text,
    }


def render_quote(content,
                 from_author=None,
                 from_url=None,
                 from_datetime=None,
                 template_name='txtrender/quote.html',
                 extra_context=None):
    """
    Wrap the given content in a quote block.
    :param content: The inner content.
    :param from_author: The source author (optional).
    :param from_url: The source author url (optional).
    :param template_name: The template name to be used.
    :param extra_context: Any extra context for the template.
    :return: The rendered quote block as string.
    """
    if from_author:
        from_author = escape_attrvalue(from_author)
    if from_url:
        from_url = escape_attrvalue(from_url)
    if from_datetime:
        from_timestamp = calendar.timegm(from_datetime.timetuple())
        from_timestamp = escape_attrvalue(from_timestamp)
    else:
        from_timestamp = None
    context = {
        'content': content,
        'from_author': from_author,
        'from_url': from_url,
        'from_timestamp': from_timestamp,
    }
    if extra_context is not None:
        context.update(extra_context)
    return loader.render_to_string(template_name, context)
