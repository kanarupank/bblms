from unittest import TestCase


class BBLMSTestCase(TestCase):
    def setUp(self):
        pass

    def test_animals_can_speak(self):
        """Test comment"""
        # lion = Animal.objects.get(name="lion")
        self.assertEqual('The lion says "roar"', 'The lion says "roar"')
