"""
Test suite for the gender app.
"""

from django.test import SimpleTestCase
from django.db import models

from .fields import GenderField
from .context_processors import gender as gender_ctx_proc
from .constants import (GENDER_CHOICES,
                        GENDER_UNKNOWN,
                        GENDER_FEMALE,
                        GENDER_MALE,
                        GENDER_OTHER)


class TestGenderModel(models.Model):
    """
    Simple test model.
    """

    gender = GenderField('gender')


class GenderFieldTestCase(SimpleTestCase):
    """
    Tests suite for the ``GenderField`` model field.
    """

    def test_model_instance(self):
        """
        Test if the model can be instantiated.
        """
        model = TestGenderModel()
        self.assertIsNotNone(model)

    def test_default_value(self):
        """
        Test the default value of the field.
        """
        model = TestGenderModel()
        self.assertEqual(GENDER_UNKNOWN, model.gender)
        field = TestGenderModel._meta.get_field('gender')
        self.assertEqual(1, field.max_length)
        self.assertEqual(GENDER_CHOICES, field.choices)
        self.assertTrue(field.blank)

    def test_assignation(self):
        """
        Test the default value of the field.
        """
        model = TestGenderModel(gender=GENDER_MALE)
        self.assertEqual(GENDER_MALE, model.gender)


class GenderContextProcessorTestCase(SimpleTestCase):
    """
    Tests suite for the gender context processor.
    """

    def test_gender_context_processor(self):
        request = None
        output = gender_ctx_proc(request)
        self.assertEqual(output, {
            'GENDER': {
                'FEMALE': GENDER_FEMALE,
                'MALE': GENDER_MALE,
                'OTHER': GENDER_OTHER,
                'UNKNOWN': GENDER_UNKNOWN,
            },
        })
