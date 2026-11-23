"""Bosh sahifa (dashboard) — `apps/dashboard/views.py::index` bilan bir xil agregatsiya
so'rovlari, matn ko'rinishida (TZ.txt 25-bo'limdagi mock bilan mos)."""
from decimal import Decimal

from django.conf import settings
from django.db.models import Sum
from django.utils import timezone
from django.utils.html import escape

from apps.bot import keyboards
from apps.bot.bot_instance import bot
from apps.bot.formatters import kg, som
from apps.bot.handlers.common import register_menu
from apps.customers.models import Customer
from apps.expenses.models import Expense
from apps.inventory.services import inventory_service
from apps.inventory.services.alerts import low_stock_products
from apps.kassa.services import cash_service
from apps.payments.models import Payment, active_payments, net_payment_sum
from apps.products.models import Product
from apps.purchases.models import Purchase
from apps.sales.models import Sale, SaleItem
from apps.suppliers.models import Supplier


@register_menu(keyboards.MENU_DASHBOARD)
def dashboard(message, tg_user):
    bot.send_message(message.chat.id, dashboard_text())


def dashboard_text():
    """Dashboard matni — bot menyusi va kunlik hisobot uchun umumiy."""
    today = timezone.localdate()

    todays_sales = Sale.objects.filter(date=today, status=Sale.Status.CONFIRMED)
    todays_sale_items = SaleItem.objects.filter(sale__in=todays_sales)
    today_sales_count = todays_sales.count()
    today_sales_total = todays_sales.aggregate(s=Sum('total_amount'))['s'] or Decimal('0')
    today_gross_profit = todays_sale_items.aggregate(s=Sum('profit'))['s'] or Decimal('0')
    today_expenses = Expense.objects.filter(date=today).aggregate(s=Sum('amount'))['s'] or Decimal('0')
    today_net_profit = today_gross_profit - today_expenses

    customers_opening = Customer.objects.aggregate(s=Sum('opening_balance'))['s'] or Decimal('0')
    total_sales_all = Sale.objects.filter(status=Sale.Status.CONFIRMED).aggregate(s=Sum('total_amount'))['s'] or Decimal('0')
    total_customer_payments_all = net_payment_sum(
        active_payments(Payment.objects.filter(customer__isnull=False)),
        positive_direction=Payment.Direction.IN)
    debitor_total = customers_opening + total_sales_all - total_customer_payments_all

    suppliers_opening = Supplier.objects.aggregate(s=Sum('opening_balance'))['s'] or Decimal('0')
    total_purchases_all = Purchase.objects.filter(status=Purchase.Status.CONFIRMED).aggregate(s=Sum('total_amount'))['s'] or Decimal('0')
    total_supplier_payments_all = net_payment_sum(
        active_payments(Payment.objects.filter(supplier__isnull=False)),
        positive_direction=Payment.Direction.OUT)
    creditor_total = suppliers_opening + total_purchases_all - total_supplier_payments_all

    total_stock = Decimal('0')
    stock_rows = []
    for product in Product.objects.filter(active=True):
        qty = inventory_service.get_stock(product)
        total_stock += qty
        if qty > 0:
            stock_rows.append((product.name, qty))
    stock_rows.sort(key=lambda r: r[1], reverse=True)

    kassa_balance = '\n'.join(f"   • {b['register'].name}: {som(b['balance'])}" for b in cash_service.get_balances())

    lines = [
        f'🏠 {settings.APP_NAME} — bosh sahifa',
        f"📅 {today.strftime('%d.%m.%Y')}",
        '',
        f'🛍 Bugungi savdo: {som(today_sales_total)} ({today_sales_count} ta sotuv)',
        f'📈 Yalpi foyda: {som(today_gross_profit)}',
        f'✅ Sof foyda: {som(today_net_profit)}',
        '',
        f'🟡 Debitor (mijozlar qarzi): {som(debitor_total)}',
        f'🔴 Kreditor (bizning qarz): {som(creditor_total)}',
        '',
        '👛 Kassa:',
        kassa_balance,
        '',
        f'🏬 Ombor (jami): {kg(total_stock)}',
    ]
    low = low_stock_products()
    if low:
        lines += ['', f'⚠️ Kam qolgan mahsulotlar: {len(low)} ta']
        for row in low[:5]:
            lines.append(f"   • {escape(row['product'].name)} — {kg(row['stock'])} (min {kg(row['min_stock'])})")
    if stock_rows:
        lines += ['', "📦 Ombor qoldig'i (top 10):"]
        for name, qty in stock_rows[:10]:
            lines.append(f'   • {escape(name)} — {kg(qty)}')

    return '\n'.join(lines)
