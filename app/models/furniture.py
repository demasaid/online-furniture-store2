from dataclasses import dataclass


# @dataclass: Automatically creates __init__ from class fields.
# @dataclass: ينشئ __init__ تلقائيًا بناءً على المتغيرات داخل الكلاس.
@dataclass
class Furniture:
    # Core attributes for any furniture item.
    # خصائص أساسية لأي قطعة أثاث.
    id: int
    name: str
    description: str
    price: float
    dimensions: str
    stock: int
    category: str

    def apply_discount(self, percentage: float) -> float:
        # Returns the price after discount (example: 10%).
        # تحسب السعر بعد الخصم (مثال: 10%).
        if not 0 <= percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        return round(self.price * (1 - percentage / 100), 2)

    def apply_tax(self, tax_rate: float) -> float:
        # Returns the price after adding tax.
        # تحسب السعر بعد إضافة الضريبة.
        if tax_rate < 0:
            raise ValueError("Tax rate must be non-negative.")
        return round(self.price * (1 + tax_rate / 100), 2)

    def is_available(self, quantity: int = 1) -> bool:
        # Checks whether requested quantity exists in stock.
        # تفحص إذا الكمية المطلوبة موجودة في المخزون.
        return self.stock >= quantity


# Chair inherits all Furniture fields and methods.
# Chair يرث كل خصائص ودوال Furniture. نضيف سلوك خاص لاحقًا إذا لزم.
class Chair(Furniture):
    pass


# Sofa inherits from Furniture.
# Sofa يرث من Furniture.
class Sofa(Furniture):
    pass


# Table inherits from Furniture.
# Table يرث من Furniture.
class Table(Furniture):
    pass


# Bed inherits from Furniture.
# Bed يرث من Furniture.
class Bed(Furniture):
    pass


# Cabinet inherits from Furniture.
# Cabinet يرث من Furniture.
class Cabinet(Furniture):
    pass
