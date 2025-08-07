import unittest

from app.scheduler import Scheduler


class TestScheduler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scheduler = Scheduler()

    def test_get_busy_slots(self):
        result = self.scheduler.get_busy_slots("2025-02-15")
        self.assertEqual(result, [('09:00', '12:00'), ('17:30', '20:00')])

    def test_get_free_slots(self):
        result = self.scheduler.get_free_slots("2025-02-15")
        self.assertEqual(result, [('12:00', '17:30'), ('20:00', '21:00')])

    def test_is_available_true(self):
        self.assertTrue(self.scheduler.is_available("2025-02-15", "12:00", "12:30"))

    def test_is_available_false(self):
        self.assertFalse(self.scheduler.is_available("2025-02-15", "17:30", "18:00"))

    def test_find_slot_60(self):
        result = self.scheduler.find_slot_for_duration(60)
        self.assertEqual(result, ("2025-02-15", "12:00", "13:00"))

    def test_find_slot_90(self):
        result = self.scheduler.find_slot_for_duration(90)
        self.assertEqual(result, ("2025-02-15", "12:00", "13:30"))
