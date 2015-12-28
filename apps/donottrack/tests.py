"""
Tests suite for the DoNotTrack app.
"""

from django.test import SimpleTestCase
from django.http import HttpRequest, HttpResponse

from .context_processors import do_not_track
from .middleware import DoNotTrackMiddleware
from .utils import get_do_not_track_flag


class DoNotTrackUtilitiesTestCase(SimpleTestCase):
    """
    Tests case for all utilities functions.
    """

    def test_get_do_not_track_flag_with_dnt_header_not_set(self):
        """
        Test the ``get_do_not_track_flag`` function result when the ``DNT`` flag header is NOT set.
        """
        request = HttpRequest()
        do_not_track_flag = get_do_not_track_flag(request)
        self.assertFalse(do_not_track_flag)

    def test_get_do_not_track_flag_with_dnt_header_set(self):
        """
        Test the ``get_do_not_track_flag`` function result when the ``DNT`` flag header IS set.
        """
        request = HttpRequest()
        request.META['HTTP_DNT'] = '1'
        do_not_track_flag = get_do_not_track_flag(request)
        self.assertTrue(do_not_track_flag)

    def test_get_do_not_track_flag_with_dnt_header_set_but_invalid(self):
        """
        Test the ``get_do_not_track_flag`` function result when the ``DNT`` flag header is set to an invalid value.
        """
        request = HttpRequest()
        request.META['HTTP_DNT'] = '0'
        do_not_track_flag = get_do_not_track_flag(request)
        self.assertFalse(do_not_track_flag)

        request.META['HTTP_DNT'] = 'abc'
        do_not_track_flag = get_do_not_track_flag(request)
        self.assertFalse(do_not_track_flag)


class DoNotTrackMiddlewareTestCase(SimpleTestCase):
    """
    Tests case for the ``DoNotTrackMiddleware`` middleware.
    """

    def test_default_attr_name(self):
        """
        Test the default name value of the injected attribute.
        """
        mw = DoNotTrackMiddleware()
        self.assertEqual('do_not_track', mw.do_not_track_attr_name)

    def test_process_request_set_do_not_track_attribute_true(self):
        """
        Test the ``process_request`` method of the middleware when the ``DNT`` flag header IS set.
        """
        request = HttpRequest()
        request.META['HTTP_DNT'] = '1'
        result = DoNotTrackMiddleware().process_request(request)

        # Verify the result
        self.assertIsNone(result)
        self.assertTrue(hasattr(request, 'do_not_track'))
        self.assertTrue(getattr(request, 'do_not_track', False))

    def test_process_request_set_do_not_track_attribute_false(self):
        """
        Test the ``process_request`` method of the middleware when the ``DNT`` flag header is NOT set.
        """
        request = HttpRequest()
        result = DoNotTrackMiddleware().process_request(request)

        # Verify the result
        self.assertIsNone(result)
        self.assertTrue(hasattr(request, 'do_not_track'))
        self.assertFalse(getattr(request, 'do_not_track', True))

    def test_process_response_add_dnt_to_vary(self):
        """
        Test if the ``process_response`` method of the middleware update the ``Vary`` HTTP header.
        """
        request = HttpRequest()
        request.META['HTTP_DNT'] = '1'
        response = HttpResponse()
        self.assertNotIn('DNT', response.get('VARY', []))
        response = DoNotTrackMiddleware().process_response(request, response)

        # Test the result
        self.assertIn('DNT', response['VARY'])


class DoNotTrackContextProcessorTestCase(SimpleTestCase):
    """
    Tests case for the context processor.
    """

    def test_do_not_track_added_to_context_true(self):
        """
        Test if the ``do_not_track`` context processor add the ``DNT`` flag value into the context when set.
        """
        request = HttpRequest()
        request.META['HTTP_DNT'] = '1'
        result = do_not_track(request)
        self.assertEqual(result, {
            'DO_NOT_TRACK': True,
        })

    def test_do_not_track_added_to_context_false(self):
        """
        Test if the ``do_not_track`` context processor add the ``DNT`` flag value into the context when not set.
        """
        request = HttpRequest()
        result = do_not_track(request)
        self.assertEqual(result, {
            'DO_NOT_TRACK': False,
        })
