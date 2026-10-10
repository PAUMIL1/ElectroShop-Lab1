"""ElectroShop — каталог электроники."""


from abc import ABC, abstractmethod


from dataclasses import dataclass


from decimal import Decimal, InvalidOperation


class ShopError(Exception):
    """Базовая ошибка магазина."""


class ValidationError(ShopError):
    """Некорректные значения полей."""


class DuplicateProductError(ShopError):
    """Товар с таким артикулом уже существует."""


class ProductNotFoundError(ShopError):
    """Товар с указанным артикулом отсутствует."""


class DataFormatError(ShopError):
    """Ошибка чтения, записи или структуры файла."""


def check_text(value: str) -> str:
    """Проверить непустой текст и убрать крайние пробелы."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Ожидается непустая строка")
    return value.strip()


def check_integer(value: int, minimum: int = 1) -> int:
    """Не считать bool допустимым количеством или характеристикой."""
    if type(value) is not int or value < minimum:
        raise ValidationError(f"Ожидается целое число от {minimum}")
    return value


def check_price(value: Decimal | str | int) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, str, int)):
        raise ValidationError("Цена должна быть Decimal, строкой или целым")
    try:
        price = Decimal(value)
    except InvalidOperation as error:
        raise ValidationError("Цена не является числом") from error
    if not price.is_finite() or price <= 0:
        raise ValidationError("Цена должна быть конечной и больше нуля")
    # Проверяем дробную часть без округления суммы.
    fraction = format(price, "f").partition(".")[2].rstrip("0")
    if len(fraction) > 2:
        raise ValidationError("Цена не должна содержать доли копейки")
    return price


@dataclass(frozen=True)
class Brand:
    """Бренд производителя."""

    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", check_text(self.name))


@dataclass(frozen=True)
class Category:
    """Категория товаров каталога."""

    name: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", check_text(self.name))


class Product(ABC):
    """Общие поля товара; конкретные характеристики задают наследники."""

    kind: str

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int,
    ) -> None:
        self.product_id = check_text(product_id)
        self.name = check_text(name)
        if not isinstance(brand, Brand) or not isinstance(category, Category):
            raise ValidationError("Требуются объекты Brand и Category")
        self.brand = brand
        self.category = category
        self.price = check_price(price)
        self.stock = check_integer(stock, minimum=0)

    @abstractmethod
    def details(self) -> dict[str, str | int]:
        """Вернуть специфическую характеристику товара."""


    def __str__(self) -> str:
        details = ", ".join(f"{key}={value}"
                            for key, value in self.details().items())
        return (f"[{self.product_id}] {self.brand.name} {self.name}; "
                f"{self.price:.2f} руб.; остаток: {self.stock}; {details}")


class Smartphone(Product):
    """Смартфон с объёмом памяти в ГБ."""

    kind = "smartphone"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, storage_gb: int,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.storage_gb = check_integer(storage_gb)

    def details(self) -> dict[str, str | int]:
        return {"storage_gb": self.storage_gb}


class Laptop(Product):
    """Ноутбук с объёмом оперативной памяти в ГБ."""

    kind = "laptop"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, ram_gb: int,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.ram_gb = check_integer(ram_gb)

    def details(self) -> dict[str, str | int]:
        return {"ram_gb": self.ram_gb}


class Tablet(Product):
    """Планшет с ёмкостью аккумулятора в мА·ч."""

    kind = "tablet"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, battery_mah: int,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.battery_mah = check_integer(battery_mah)

    def details(self) -> dict[str, str | int]:
        return {"battery_mah": self.battery_mah}


class Monitor(Product):
    """Монитор с частотой обновления в Гц."""

    kind = "monitor"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, refresh_hz: int,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.refresh_hz = check_integer(refresh_hz)

    def details(self) -> dict[str, str | int]:
        return {"refresh_hz": self.refresh_hz}


class Keyboard(Product):
    """Клавиатура с обозначением раскладки."""

    kind = "keyboard"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, layout: str,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.layout = check_text(layout)

    def details(self) -> dict[str, str | int]:
        return {"layout": self.layout}


class Mouse(Product):
    """Мышь с разрешением сенсора в DPI."""

    kind = "mouse"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, dpi: int,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.dpi = check_integer(dpi)

    def details(self) -> dict[str, str | int]:
        return {"dpi": self.dpi}


class Headphones(Product):
    """Наушники с типом подключения."""

    kind = "headphones"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, connection: str,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.connection = check_text(connection)

    def details(self) -> dict[str, str | int]:
        return {"connection": self.connection}


class Charger(Product):
    """Зарядное устройство с мощностью в Вт."""

    kind = "charger"

    def __init__(
        self, product_id: str, name: str, brand: Brand, category: Category,
        price: Decimal | str | int, stock: int, power_w: int,
    ) -> None:
        super().__init__(product_id, name, brand, category, price, stock)
        self.power_w = check_integer(power_w)

    def details(self) -> dict[str, str | int]:
        return {"power_w": self.power_w}


def main() -> None:
    """Показать характеристики разных видов электроники."""
    brand = Brand("ElectroDemo")
    mobile = Category("Мобильная электроника")
    computers = Category("Компьютеры и периферия")
    accessories = Category("Аксессуары")
    products = [
        Smartphone("P1", "Phone One", brand, mobile, "29990.00", 5, 128),
        Laptop("P2", "Book One", brand, computers, "79990.00", 3, 16),
        Tablet("P3", "Tab One", brand, mobile, "24990.00", 4, 8000),
        Monitor("P4", "Display One", brand, computers, "19990.00", 6, 144),
        Keyboard("P5", "Keys One", brand, computers, "2990.00", 8, "RU/EN"),
        Mouse("P6", "Mouse One", brand, computers, "1490.00", 10, 3200),
        Headphones("P7", "Sound One", brand, accessories,
                   "4990.00", 7, "Bluetooth"),
        Charger("P8", "Charge One", brand, accessories, "1990.00", 9, 65),
    ]
    for product in products:
        print(product)



if __name__ == "__main__":
    try:
        main()
    except ShopError as error:
        print(f"Не удалось выполнить демонстрацию: {error}")
