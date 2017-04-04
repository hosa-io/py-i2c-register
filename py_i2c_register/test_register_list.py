import unittest
from mock import MagicMock

from py_i2c_register.register_list import RegisterList
from py_i2c_register.register import Register

class TestRegisterListInit(unittest.TestCase):
    def test_perfect(self):
        i2c = MagicMock()
        list = RegisterList(1, i2c, {"key": "value"})

        self.assertEqual(list.dev_addr, 1)
        self.assertEqual(list.i2c, i2c)
        self.assertEqual(list.registers, {"key": "value"})

class TestRegisterListProxyMethods(unittest.TestCase):
    def setUp(self):
        self.i2c = MagicMock()
        self.i2c.readBytes = MagicMock(return_value=[170])
        self.i2c.writeBytes = MagicMock()

        self.lst = RegisterList(1, self.i2c, {})
        self.lst.add("REG1", 1, Register.READ + Register.WRITE, {})
        self.lst.get("REG1").add("SEG1", 0, 2, [0] * 3)

    def test_to_int_read_first(self):
        self.lst.get("REG1").get("SEG1").bytes_to_int = MagicMock()

        self.lst.to_int("REG1", "SEG1", read_first=True)

        self.lst.get("REG1").get("SEG1").bytes_to_int.assert_called_once()
        self.i2c.readBytes.assert_called_once_with(1, 1, 1)

    def test_to_int_dont_read_first(self):
        self.lst.get("REG1").get("SEG1").bytes_to_int = MagicMock()

        self.lst.to_int("REG1", "SEG1", read_first=False)

        self.lst.get("REG1").get("SEG1").bytes_to_int.assert_called_once()
        self.i2c.readBytes.assert_not_called()

    def test_to_int_keyerror_reg(self):
        with self.assertRaises(KeyError):
            self.lst.to_int("DOES_NOT_EXIST", "SEG1")

    def test_to_int_keyerror_seg(self):
        with self.assertRaises(KeyError):
            self.lst.to_int("REG1", "DOES_NOT_EXIST")

    def test_to_twos_comp_int_read_first(self):
        self.lst.get("REG1").get("SEG1").bytes_to_twos_comp_int = MagicMock()

        self.lst.to_twos_comp_int("REG1", "SEG1", read_first=True)

        self.lst.get("REG1").get("SEG1").bytes_to_twos_comp_int.assert_called_once()
        self.i2c.readBytes.assert_called_once_with(1, 1, 1)

    def test_to_twos_comp_int_dont_read_first(self):
        self.lst.get("REG1").get("SEG1").bytes_to_twos_comp_int = MagicMock()

        self.lst.to_twos_comp_int("REG1", "SEG1", read_first=False)

        self.lst.get("REG1").get("SEG1").bytes_to_twos_comp_int.assert_called_once()
        self.i2c.readBytes.assert_not_called()

    def test_to_twos_comp_int_keyerror_reg(self):
        with self.assertRaises(KeyError):
            self.lst.to_twos_comp_int("DOES_NOT_EXIST", "SEG1")

    def test_to_twos_comp_int_keyerror_seg(self):
        with self.assertRaises(KeyError):
            self.lst.to_twos_comp_int("REG1", "DOES_NOT_EXIST")

    def test_set_bits_perfect_write_after(self):
        seg1 = self.lst.get("REG1").get("SEG1")
        seg1.set_bits = MagicMock(side_effect=seg1.set_bits)

        self.lst.set_bits("REG1", "SEG1", [1, 1, 0], write_after=True)

        seg1.set_bits.assert_called_once_with([1, 1, 0])
        self.i2c.writeBytes.assert_called_once_with(1, 1, [3])

    def test_set_bits_perfect_dont_write_after(self):
        seg1 = self.lst.get("REG1").get("SEG1")
        seg1.set_bits = MagicMock(side_effect=seg1.set_bits)

        self.lst.set_bits("REG1", "SEG1", [1, 1, 0], write_after=False)

        seg1.set_bits.assert_called_once_with([1, 1, 0])
        self.i2c.writeBytes.assert_not_called()

    def test_set_bits_perfect_write_after_custom_write_fn(self):
        seg1 = self.lst.get("REG1").get("SEG1")
        seg1.set_bits = MagicMock(side_effect=seg1.set_bits)

        mock_write = MagicMock()
        self.lst.set_bits("REG1", "SEG1", [1, 1, 0], write_after=True, write_fn=mock_write)

        seg1.set_bits.assert_called_once_with([1, 1, 0])
        mock_write.assert_called_once_with("REG1")

    def test_set_bits_perfect_dont_write_after_custom_write_fn(self):
        seg1 = self.lst.get("REG1").get("SEG1")
        seg1.set_bits = MagicMock(side_effect=seg1.set_bits)

        mock_write = MagicMock()
        self.lst.set_bits("REG1", "SEG1", [1, 1, 0], write_after=False, write_fn=mock_write)

        seg1.set_bits.assert_called_once_with([1, 1, 0])
        mock_write.assert_not_called()

    def test_set_bits_from_int(self):
        self.lst.set_bits = MagicMock()

        mock_write = MagicMock()
        self.lst.set_bits_from_int("REG1", "SEG1", 3, write_after=True, write_fn=mock_write)

        self.lst.set_bits.assert_called_once_with("REG1", "SEG1", [1, 1, 0], write_after=True, write_fn=mock_write)
