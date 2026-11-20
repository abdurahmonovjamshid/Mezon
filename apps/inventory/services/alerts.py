"""Kam qoldiq ogohlantirishlari: `Product.min_stock` belgilangan va jami
qoldig'i (barcha omborlar bo'yicha) shu chegaraga tushgan yoki undan kam
bo'lgan faol mahsulotlar."""
from decimal import Decimal

from apps.inventory.services import inventory_service


def low_stock_products():
    """[{'product', 'stock', 'min_stock', 'shortage'}, ...] — eng kami birinchi."""
    from apps.products.models import Product

    products = list(Product.objects.filter(active=True, min_stock__isnull=False).select_related('category'))
    if not products:
        return []
    stock = inventory_service.get_all_stock()
    rows = []
    for product in products:
        qty = stock.get(product.id, Decimal('0'))
        if qty <= product.min_stock:
            rows.append({
                'product': product,
                'stock': qty,
                'min_stock': product.min_stock,
                'shortage': product.min_stock - qty,
            })
    rows.sort(key=lambda r: (r['stock'] - r['min_stock'], r['product'].name))
    return rows


def crossed_min_stock(product, before, after) -> bool:
    """Chiqim natijasida qoldiq chegaradan yuqoridan pastga tushdimi."""
    return product.min_stock is not None and before > product.min_stock >= after
