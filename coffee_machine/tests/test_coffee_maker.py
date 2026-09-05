import unittest
from main import CoffeeMaker, MenuItem


class TestCoffeeMaker(unittest.TestCase):
    def setUp(self):
        self.coffee_maker = CoffeeMaker()

    def test_resources_deducted_correctly(self):
        """【観点2】注文後にリソースが正確に減算されるか。"""
        # 水: 200, ミルク: 150, 豆: 24 のラテを作成
        latte = MenuItem(name="latte", water=200, milk=150, coffee=24, cost=2.5)

        self.coffee_maker.make_coffee(latte)

        # 初期値 (300, 200, 100) から正確に減算されているか検証
        self.assertEqual(self.coffee_maker.resources["water"], 100)
        self.assertEqual(self.coffee_maker.resources["milk"], 50)
        self.assertEqual(self.coffee_maker.resources["coffee"], 76)

    def test_negative_ingredients_handling(self):
        """【観点1】負の値を持つ不正なレシピでリソースが不正増加しないか。"""
        invalid_drink = MenuItem(name="glitch", water=-50, milk=0, coffee=0, cost=1.0)

        # 本来はこのような不正な材料は例外を送出するか、減算を拒絶すべき
        # 現状のコードでは水が増えてしまう脆弱性があることを検知するテスト
        initial_water = self.coffee_maker.resources["water"]
        self.coffee_maker.make_coffee(invalid_drink)

        # 水が増加していないことをアサート（検証）する
        self.assertLessEqual(self.coffee_maker.resources["water"], initial_water)


if __name__ == "__main__":
    unittest.main()
