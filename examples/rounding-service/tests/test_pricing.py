import unittest

from app.pricing import format_brl, split_installments


class SplitInstallmentsTest(unittest.TestCase):
    def test_even_split_keeps_the_total(self):
        self.assertEqual(sum(split_installments(1200, 3)), 1200)

    def test_uneven_split_keeps_the_total(self):
        self.assertEqual(sum(split_installments(10000, 3)), 10000)

    def test_last_installment_absorbs_the_remainder(self):
        self.assertEqual(split_installments(10000, 3), [3333, 3333, 3334])

    def test_single_installment_is_the_total(self):
        self.assertEqual(split_installments(500, 1), [500])

    def test_rejects_non_positive_count(self):
        with self.assertRaises(ValueError):
            split_installments(100, 0)


class FormatTest(unittest.TestCase):
    def test_formats_cents_as_currency(self):
        self.assertEqual(format_brl(3334), "R$ 33,34")

    def test_keeps_trailing_zero(self):
        self.assertEqual(format_brl(1200), "R$ 12,00")


if __name__ == "__main__":
    unittest.main()
