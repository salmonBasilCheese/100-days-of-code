class MenuItem:
    """各ドリンクの属性（名前、材料、価格）を保持するモデル。"""

    def __init__(self, name: str, water: int, milk: int, coffee: int, cost: float):
        self.name = name
        self.cost = cost
        self.ingredients = {
            "water": water,
            "milk": milk,
            "coffee": coffee,
        }


class Menu:
    """提供可能なドリンクのカタログ管理を担当するクラス。"""

    def __init__(self):
        self.menu = [
            MenuItem(name="espresso", water=50, milk=0, coffee=18, cost=1.5),
            MenuItem(name="latte", water=200, milk=150, coffee=24, cost=2.5),
            MenuItem(name="cappuccino", water=250, milk=100, coffee=24, cost=3.0),
        ]

    def get_items(self) -> str:
        """選択肢として表示するドリンク名一覧を返す。"""
        return "/".join([item.name for item in self.menu])

    def find_drink(self, order_name: str) -> MenuItem | None:
        """指定された名前に一致するドリンクを検索して返す。"""
        for item in self.menu:
            if item.name == order_name:
                return item
        print("Sorry that item is not available.")
        return None


class CoffeeMaker:
    """リソース残量管理とドリンク抽出を担当するクラス。"""

    def __init__(self):
        self.resources = {
            "water": 300,
            "milk": 200,
            "coffee": 100,
        }

    def report(self) -> None:
        """現在のリソース残量を表示する。"""
        print(f"Water: {self.resources['water']}ml")
        print(f"Milk: {self.resources['milk']}ml")
        print(f"Coffee: {self.resources['coffee']}g")

    def is_resource_sufficient(self, drink: MenuItem) -> bool:
        """注文されたドリンクに対してリソースが足りているか判定する。"""
        can_make = True
        for item, amount in drink.ingredients.items():
            if amount > self.resources.get(item, 0):
                print(f"Sorry there is not enough {item}.")
                can_make = False
        return can_make

    def make_coffee(self, order: MenuItem) -> None:
        """リソースを減算し、ドリンクを提供する。"""
        # 防御的処理：負の値が含まれている場合は処理を中断し例外を発生させる、あるいは減算を拒否する
        for item, amount in order.ingredients.items():
            if amount < 0:
                print(f"Error: Cannot deduct negative amount for {item}.")
                return
            self.resources[item] -= amount
        print(f"Here is your {order.name}. Enjoy!")


class MoneyMachine:
    """硬貨の受付、判定、お釣り計算、売上管理を担当するクラス。"""

    CURRENCY = "$"
    COIN_VALUES = {
        "quarters": 0.25,
        "dimes": 0.10,
        "nickles": 0.05,
        "pennies": 0.01,
    }

    def __init__(self):
        self.profit = 0.0
        self.money_received = 0.0

    def report(self) -> None:
        """現在の売上高を表示する。"""
        print(f"Money: {self.CURRENCY}{self.profit}")

    def _get_valid_coin_count(self, coin: str) -> int:
        """不正な文字入力や負数を防ぎ、有効な正の整数のみを再帰的に要求する。"""
        while True:
            raw_input = input(f"how many {coin}?: ").strip()
            try:
                count = int(raw_input)
                if count < 0:
                    print("Please enter a positive number.")
                    continue
                return count
            except ValueError:
                print("Invalid input. Please enter a valid whole number.")

    def process_coins(self) -> float:
        """投入された硬貨から合計金額を計算する。"""
        print("Please insert coins.")
        self.money_received = 0.0
        for coin, value in self.COIN_VALUES.items():
            count = self._get_valid_coin_count(coin)
            self.money_received += count * value
        return self.money_received

    def make_payment(self, cost: float) -> bool:
        """支払い処理を実行し、売上加算とお釣り返却を制御する。"""
        self.process_coins()
        if self.money_received >= cost:
            change = round(self.money_received - cost, 2)
            if change > 0:
                print(f"Here is {self.CURRENCY}{change} dollars in change.")
            self.profit += cost
            self.money_received = 0.0
            return True
        else:
            print("Sorry that's not enough money. Money refunded.")
            self.money_received = 0.0
            return False


def main() -> None:
    menu = Menu()
    coffee_maker = CoffeeMaker()
    money_machine = MoneyMachine()

    is_on = True
    while is_on:
        options = menu.get_items()
        choice = input(f"What would you like? ({options}): ").strip().lower()

        if choice == "off":
            is_on = False
        elif choice == "report":
            coffee_maker.report()
            money_machine.report()
        else:
            drink = menu.find_drink(choice)
            if drink and coffee_maker.is_resource_sufficient(drink):
                if money_machine.make_payment(drink.cost):
                    coffee_maker.make_coffee(drink)


if __name__ == "__main__":
    main()
