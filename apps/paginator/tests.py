"""
Tests suite for the pagination app.
"""

from unittest.mock import MagicMock, Mock

from django.http import Http404, QueryDict
from django.test import SimpleTestCase

from .shortcut import (get_page_number,
                       paginate,
                       update_context_for_pagination)


class PaginatorTestCase(SimpleTestCase):
    """
    Tests suite for the pagination app.
    """

    def test_get_page_number_with_page(self):
        """
        Test the ``get_page_number`` method with a ``page=n`` argument set.
        """
        request = MagicMock(GET={'page': '3'})
        page = get_page_number(request)
        self.assertEqual(page, '3')

    def test_get_page_number_without_page(self):
        """
        Test the ``get_page_number`` method without a ``page=n`` argument set.
        """
        request = MagicMock(GET={})
        page = get_page_number(request)
        self.assertEqual(page, 1)

    def test_get_page_number_with_page_empty(self):
        """
        Test the ``get_page_number`` method with ``page=''``.
        """
        request = MagicMock(GET={'page': ''})
        page = get_page_number(request)
        self.assertEqual(page, 1)

    def test_paginate(self):
        """
        Simple test of the ``paginate`` method with invalid page number.
        """

        with self.assertRaises(Http404):
            queryset = MagicMock()
            request = MagicMock(GET={'page': '-1'})
            paginate(queryset, request)

    def test_update_context_for_pagination(self):
        context = {}
        request = MagicMock(GET=QueryDict(''))
        paginator = MagicMock()
        page = MagicMock(number=1, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=True)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': True,
            'is_paginated': True,
            'test': [1, 2, 3],
            'get_params': '',
            'get_params_union': '',
        })

    def test_update_context_for_pagination_not_first_page(self):
        context = {}
        request = MagicMock(GET=QueryDict(''))
        paginator = MagicMock()
        page = MagicMock(number=2, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=True)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': False,
            'is_paginated': True,
            'test': [1, 2, 3],
            'get_params': '',
            'get_params_union': '',
        })

    def test_update_context_for_pagination_no_more_pages(self):
        context = {}
        request = MagicMock(GET=QueryDict(''))
        paginator = MagicMock()
        page = MagicMock(number=1, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=False)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': True,
            'is_paginated': False,
            'test': [1, 2, 3],
            'get_params': '',
            'get_params_union': '',
        })

    def test_update_context_for_pagination_page_arg_removed(self):
        context = {}
        request = MagicMock(GET=QueryDict('page=1'))
        paginator = MagicMock()
        page = MagicMock(number=1, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=True)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': True,
            'is_paginated': True,
            'test': [1, 2, 3],
            'get_params': '',
            'get_params_union': '',
        })

    def test_update_context_for_pagination_extra_args(self):
        context = {}
        request = MagicMock(GET=QueryDict('foo=bar'))
        paginator = MagicMock()
        page = MagicMock(number=1, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=True)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': True,
            'is_paginated': True,
            'test': [1, 2, 3],
            'get_params': 'foo=bar',
            'get_params_union': '&foo=bar',
        })

    def test_update_context_for_pagination_extra_args_and_page(self):
        context = {}
        request = MagicMock(GET=QueryDict('page=1&foo=bar'))
        paginator = MagicMock()
        page = MagicMock(number=1, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=True)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': True,
            'is_paginated': True,
            'test': [1, 2, 3],
            'get_params': 'foo=bar',
            'get_params_union': '&foo=bar',
        })

    def test_update_context_for_pagination_extra_args_with_slash(self):
        context = {}
        request = MagicMock(GET=QueryDict('foo=/bar/'))
        paginator = MagicMock()
        page = MagicMock(number=1, object_list=[1, 2, 3])
        page.has_other_pages = Mock(return_value=True)
        update_context_for_pagination(context, 'test', request, paginator, page)
        self.assertEqual(context, {
            'paginator': paginator,
            'page_obj': page,
            'is_first_page': True,
            'is_paginated': True,
            'test': [1, 2, 3],
            'get_params': 'foo=%2Fbar%2F',
            'get_params_union': '&foo=%2Fbar%2F',
        })
