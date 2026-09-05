import unittest
from unittest.mock import patch
from main import MoneyMachine

# 前述のクラスが定義されているモジュールから読み込む前提


class TestMoneyMachine(unittest.TestCase):
    def setUp(self):
        """各テストの実行前に独立したインスタンスを生成する。"""
        self.machine = MoneyMachine()

    @patch("builtins.input", side_effect=["4", "0", "0", "0"])
    def test_process_coins_valid_input(self, mock_input):
        """クォーター4枚（$1.00）を正しく計算できるか。"""
        total = self.machine.process_coins()
        self.assertEqual(total, 1.0)

    @patch("builtins.input", side_effect=["invalid", "-5", "2", "0", "0", "0"])
    def test_get_valid_coin_count_recovery(self, mock_input):
        """不正文字や負数が入力されてもクラッシュせず、正常値（2枚）を再要求して受け取れるか。"""
        count = self.machine._get_valid_coin_count("quarters")
        self.assertEqual(count, 2)

    @patch.object(MoneyMachine, "process_coins")
    def test_make_payment_exact_amount(self, mock_process_coins):
        """投入額と商品価格が完全一致した場合、売上が加算されTrueを返すか。"""
        self.machine.money_received = 2.50
        cost = 2.50

        result = self.machine.make_payment(cost)

        self.assertTrue(result)
        self.assertEqual(self.machine.profit, 2.50)
        self.assertEqual(self.machine.money_received, 0.0)

    @patch.object(MoneyMachine, "process_coins")
    def test_make_payment_insufficient(self, mock_process_coins):
        """投入額が不足していた場合、売上に加算されずFalseを返すか。"""
        self.machine.money_received = 1.00
        cost = 2.50

        result = self.machine.make_payment(cost)

        self.assertFalse(result)
        self.assertEqual(self.machine.profit, 0.0)
        self.assertEqual(self.machine.money_received, 0.0)


if __name__ == "__main__":
    unittest.main()
