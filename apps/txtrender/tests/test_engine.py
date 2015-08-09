"""
Test suite for the text rendering engine of the text rendering app.
"""

from django.test import SimpleTestCase

from ..utils import (parse_html,
                     render_html_source,
                     remove_tags_if_not_allowed,
                     get_unique_slug,
                     preprocess_code_blocks,
                     filter_allowed_tags_and_attrs,
                     fix_old_tags,
                     strip_comments,
                     strip_cdata,
                     force_rel_no_follow,
                     sanitize_uri,
                     make_auto_paragraph,
                     highlight_code_blocks,
                     handle_custom_tags,
                     grab_all_ids,
                     replace_entities,
                     render_html,
                     strip_html)


class TextRenderingEngineTestCase(SimpleTestCase):
    """
    Test suite for the text rendering engine.
    """

    def test_parse_html_fragment(self):
        """
        Test the output of the ``parse_html`` function with a fragment of HTML page.
        """
        input_html = "<p>Foo <i>Bar</i></p>"
        excepted_output = "<p>Foo <i>Bar</i></p>"
        output_html = str(parse_html(input_html))
        self.assertEqual(excepted_output, output_html)

    def test_parse_html_full_document(self):
        """
        Test the output of the ``parse_html`` function with a full HTML page.
        """
        input_html = "<html><head><title>Test</title></head><body><p>Foo <i>Bar</i></p></body></html>"
        excepted_output = "<p>Foo <i>Bar</i></p>"
        output_html = str(parse_html(input_html))
        self.assertEqual(excepted_output, output_html)

    def test_render_html_source(self):
        """
        Test the output of the ``render_html_source`` function with a simple document tree.
        """
        input_html = "<p>Foo <i>Bar</i></p>"
        excepted_output = "<p>Foo <i>Bar</i></p>"
        output_html = render_html_source(parse_html(input_html))
        self.assertEqual(excepted_output, output_html)

    def test_render_html_source_prettify(self):
        """
        Test the output of the ``render_html_source`` function with a simple document tree and pretty output enabled.
        """
        input_html = "<p>Foo <i>Bar</i></p>"
        excepted_output = "<p>\n Foo\n <i>\n  Bar\n </i>\n</p>"
        output_html = render_html_source(parse_html(input_html), prettify=True)
        self.assertEqual(excepted_output, output_html)

    def test_remove_tags_if_not_allowed_with_allowed_tags(self):
        """
        Test the result of the ``remove_tags_if_not_allowed`` with some allowed tags.
        """
        allowed_tags = {'a', 'b', 'c'}
        tag_names = ('b', 'c')
        remove_tags_if_not_allowed(allowed_tags, tag_names, True)
        self.assertEqual({'a', 'b', 'c'}, allowed_tags)

    def test_remove_tags_if_not_allowed_with_not_allowed_tags(self):
        """
        Test the result of the ``remove_tags_if_not_allowed`` with some non-allowed tags.
        """
        allowed_tags = {'a', 'b', 'c'}
        tag_names = ('b', 'c')
        remove_tags_if_not_allowed(allowed_tags, tag_names, False)
        self.assertEqual({'a', }, allowed_tags)

    def test_remove_tags_if_not_allowed_with_not_allowed_but_non_existing_tags(self):
        """
        Test the result of the ``remove_tags_if_not_allowed`` with some non-allowed tags, but - plot twist - theses tags
        does not exist in the allowed tag set.
        """
        allowed_tags = {'a', }
        tag_names = ('b', 'c')
        remove_tags_if_not_allowed(allowed_tags, tag_names, False)
        self.assertEqual({'a', }, allowed_tags)

    def test_preprocess_code_blocks(self):
        input_html = '<code>#include <stdio.h>\n\nint main(void) ' \
                     '{\n  puts("Hello worlds!");\nreturn 0;\n}</code>'
        excepted_html = '<code>#include &lt;stdio.h&gt;\n\nint main(void) ' \
                        '{\n  puts("Hello worlds!");\nreturn 0;\n}</code>'
        output_html = preprocess_code_blocks(input_html)
        self.assertEqual(excepted_html, output_html)

    def test_preprocess_code_blocks_extra_spaces(self):
        input_html = '< code >#include <stdio.h>\n\nint main(void) ' \
                     '{\n  puts("Hello worlds!");\nreturn 0;\n}< / code >'
        excepted_html = '< code >#include &lt;stdio.h&gt;\n\nint main(void) ' \
                        '{\n  puts("Hello worlds!");\nreturn 0;\n}< / code >'
        output_html = preprocess_code_blocks(input_html)
        self.assertEqual(excepted_html, output_html)

    def test_preprocess_code_blocks_double_encode(self):
        input_html = '<code>&lt;&gt;</code>'
        excepted_html = '<code>&amp;lt;&amp;gt;</code>'
        output_html = preprocess_code_blocks(input_html)
        self.assertEqual(excepted_html, output_html)

    def test_preprocess_code_blocks_with_args(self):
        input_html = '<code foo="bar">#include <stdio.h>\n\nint main(void) ' \
                     '{\n  puts("Hello worlds!");\nreturn 0;\n}</code>'
        excepted_html = '<code foo="bar">#include &lt;stdio.h&gt;\n\nint main(void) ' \
                        '{\n  puts("Hello worlds!");\nreturn 0;\n}</code>'
        output_html = preprocess_code_blocks(input_html)
        self.assertEqual(excepted_html, output_html)

    def test_filter_allowed_tags_and_attrs(self):
        input_html = '<q cite="someone" onload="alert(/XSS/)"><p class="toto">Foo <i>Bar</i><span> Fish</span></p></q>'
        excepted_html = '<q cite="someone"><p class="toto">Foo <i>Bar</i></p></q>'
        allowed_tags = {'p', 'i', 'q'}
        allowed_attrs = {'q': {'cite', }}
        allowed_attrs_global = {'class', }
        document_tree = parse_html(input_html)
        filter_allowed_tags_and_attrs(document_tree, allowed_tags, allowed_attrs, allowed_attrs_global)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)

    def test_fix_old_tags(self):
        input_html = '<p><strike>Foo Bar</strike></p>'
        excepted_html = '<p><del>Foo Bar</del></p>'
        old_tag_replacements = {'strike': 'del'}
        document_tree = parse_html(input_html)
        fix_old_tags(document_tree, old_tag_replacements)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)

    def test_strip_comments(self):
        input_html = '<p>Foo Bar</p><!-- Nobody look at me -->'
        excepted_html = '<p>Foo Bar</p>'
        document_tree = parse_html(input_html)
        strip_comments(document_tree)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)

    def test_strip_cdata(self):
        input_html = '<p><![CDATA[Get the fuck out XML]]></p>'
        excepted_html = '<p></p>'
        document_tree = parse_html(input_html)
        strip_cdata(document_tree)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)
        # This test always fail with html5lib.

    def test_force_rel_no_follow(self):
        input_html = '<a href="/about/">Ze link</a>'
        excepted_html = '<a href="/about/" rel="nofollow">Ze link</a>'
        document_tree = parse_html(input_html)
        force_rel_no_follow(document_tree)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)

    def test_force_rel_no_follow_overwrite(self):
        input_html = '<a href="/about/" rel="help">Ze link</a>'
        excepted_html = '<a href="/about/" rel="nofollow">Ze link</a>'
        document_tree = parse_html(input_html)
        force_rel_no_follow(document_tree)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)

    def test_handle_custom_tags(self):
        input_html = '<not>INPUT</not>'
        excepted_html = '<span style="text-decoration:overline;">INPUT</span>'
        document_tree = parse_html(input_html)
        handle_custom_tags(document_tree)
        output_html = render_html_source(document_tree)
        self.assertEqual(excepted_html, output_html)

    def test_get_unique_slug(self):
        slug = get_unique_slug('Hello World', {})
        self.assertEqual('hello-world', slug)

    def test_get_unique_slug_exist(self):
        slug = get_unique_slug('Hello World', {'hello-world', })
        self.assertEqual('hello-world-2', slug)

    def test_strip_html(self):
        """
        Test if the ``strip_html`` effectively strip HTML tags.
        """
        input_html = "<p>Hello World!</p>"
        excepted_output = "Hello World!"
        output_html = strip_html(input_html)
        self.assertEqual(excepted_output, output_html)

    def test_strip_html_comments(self):
        """
        Test if the ``strip_html`` strip HTML comments
        """
        input_html = "<!-- I'm hiding -->"
        excepted_output = ""
        output_html = strip_html(input_html)
        self.assertEqual(excepted_output, output_html)

    def test_strip_html_unescape(self):
        """
        Test if the ``strip_html`` correctly unescape HTML entities.
        """
        input_html = "&lt;&num;&#x00023;&#35;&gt;"
        excepted_output = "<###>"
        output_html = strip_html(input_html)
        self.assertEqual(excepted_output, output_html)
