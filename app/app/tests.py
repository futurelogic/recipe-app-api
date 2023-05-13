"""
Sample Tests
"""

from django.test import SimpleTestCase
from calc import add, subtract


class CalcTests(SimpleTestCase):
    """
    Test the calc module
    """

    def test_add_numbers(self):
        """
        Test adding two numbers together
        """
        result = add(5, 6)
        self.assertEquals(result, 11)

    def test_subtract_number(self):
        """
        Test subtracting two numbers
        """
        result = subtract(6, 5)
        self.assertEquals(result, 1)
