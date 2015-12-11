"""
Tests suite for the countries app.
"""

from django.db import models
from django.test import SimpleTestCase

from .fields import CountryField
from .countries import (COUNTRIES_CHOICES,
                        ALPHA2_TO_ALPHA3_LUT,
                        ALPHA3_TO_ALPHA2_LUT)


class TestCountriesModel(models.Model):
    """
    Simple test model.
    """

    country = CountryField('country',
                           default='FRA')


class CountryFieldTestCase(SimpleTestCase):
    """
    Tests suite for the ``CountryField`` model field.
    """

    def test_model_instance(self):
        """
        Test if the model can be instantiated.
        """
        model = TestCountriesModel()
        self.assertIsNotNone(model)

    def test_default_value(self):
        """
        Test the default value of the field.
        """
        model = TestCountriesModel()
        self.assertEqual('FRA', model.country)
        field = TestCountriesModel._meta.get_field('country')
        self.assertEqual(3, field.max_length)
        self.assertEqual(COUNTRIES_CHOICES, field.choices)
        self.assertFalse(field.blank)

    def test_assignation(self):
        """
        Test the default value of the field.
        """
        model = TestCountriesModel(country='JPN')
        self.assertEqual('JPN', model.country)


class CountryListTestCase(SimpleTestCase):
    """
    Tests suite for the country list.
    """

    def test_all_country_listed(self):
        """
        Test if all 249 country listed on the ISO website (https://www.iso.org/obp/ui/#search) are
        listed in the ``countries.py`` file.
        """
        self.assertEqual(len(COUNTRIES_CHOICES), 249)

    def test_all_alpha_3_codes_in_alpha_3_to_2_table(self):
        """
        Test if all Alpha 3 code are listed in the Alpha 3 to Alpha 2 table.
        """
        for alpha3, alpha2 in ALPHA3_TO_ALPHA2_LUT.items():
            self.assertIn(alpha2, ALPHA2_TO_ALPHA3_LUT)
            self.assertEqual(ALPHA2_TO_ALPHA3_LUT[alpha2], alpha3)

    def test_all_alpha_2_codes_in_alpha_2_to_3_table(self):
        """
        Test if all Alpha 2 code are listed in the Alpha 2 to Alpha 3 table.
        """
        for alpha2, alpha3 in ALPHA2_TO_ALPHA3_LUT.items():
            self.assertIn(alpha3, ALPHA3_TO_ALPHA2_LUT)
            self.assertEqual(ALPHA3_TO_ALPHA2_LUT[alpha3], alpha2)

    def test_all_choices_in_alpha3(self):
        """
        Test if all choices in ``COUNTRIES_CHOICES`` are in the ``ALPHA3_TO_ALPHA2_LUT`` table.
        """
        choices = dict(COUNTRIES_CHOICES)
        for code in choices.keys():
            self.assertIn(code, ALPHA3_TO_ALPHA2_LUT)
