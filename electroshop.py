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


def main() -> None:
    """Создать справочные объекты каталога."""
    brand = Brand("ElectroDemo")
    category = Category("Электроника")
    print("Бренд:", brand.name)
    print("Категория:", category.name)
    try:
        Brand(" ")
    except ValidationError as error:
        print("Ошибка обработана:", error)



if __name__ == "__main__":
    try:
        main()
    except ShopError as error:
        print(f"Не удалось выполнить демонстрацию: {error}")
