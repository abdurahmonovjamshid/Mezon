"""Umumiy qidiruv: mijoz, yetkazib beruvchi, mahsulot, sotuv va xarid.
Natijalar foydalanuvchi roliga ruxsat etilgan bo'limlar bilan cheklanadi."""
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from apps.accounts.roles import allowed_sections
from apps.common.templatetags.uz_numbers import uzsum

PER_GROUP = 6


def _customers(q, limit):
    from apps.customers.models import Customer
    for c in Customer.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))[:limit]:
        yield {'title': c.name, 'subtitle': c.phone or 'Mijoz', 'url': reverse('customers:detail', args=[c.pk])}


def _suppliers(q, limit):
    from apps.suppliers.models import Supplier
    for s in Supplier.objects.filter(Q(name__icontains=q) | Q(phone__icontains=q))[:limit]:
        yield {'title': s.name, 'subtitle': s.phone or 'Yetkazib beruvchi', 'url': reverse('suppliers:detail', args=[s.pk])}


def _products(q, limit):
    from apps.products.models import Product
    qs = Product.objects.select_related('category').filter(Q(name__icontains=q) | Q(code__icontains=q))
    for p in qs[:limit]:
        yield {'title': p.name, 'subtitle': f'{p.code} · {p.category.name}', 'url': reverse('products:detail', args=[p.pk])}


def _sales(q, limit):
    from apps.sales.models import Sale
    qs = Sale.objects.select_related('customer').filter(
        Q(sale_number__icontains=q) | Q(customer__name__icontains=q)).order_by('-date', '-id')
    for s in qs[:limit]:
        who = s.customer.name if s.customer_id else ''
        yield {'title': s.sale_number, 'subtitle': f'{s.date:%d.%m.%Y} · {who} · {uzsum(s.total_amount)} so\'m',
               'url': reverse('sales:detail', args=[s.pk])}


def _purchases(q, limit):
    from apps.purchases.models import Purchase
    qs = Purchase.objects.select_related('supplier').filter(
        Q(purchase_number__icontains=q) | Q(supplier__name__icontains=q)).order_by('-date', '-id')
    for p in qs[:limit]:
        who = p.supplier.name if p.supplier_id else ''
        yield {'title': p.purchase_number, 'subtitle': f'{p.date:%d.%m.%Y} · {who} · {uzsum(p.total_amount)} so\'m',
               'url': reverse('purchases:detail', args=[p.pk])}


SOURCES = (
    ('customers', 'Mijozlar', 'people', _customers),
    ('suppliers', 'Yetkazib beruvchilar', 'truck', _suppliers),
    ('products', 'Mahsulotlar', 'box-seam', _products),
    ('sales', 'Sotuvlar', 'cart-check', _sales),
    ('purchases', 'Xaridlar', 'bag', _purchases),
)


def run_search(user, q, limit=PER_GROUP):
    q = (q or '').strip()
    if len(q) < 2:
        return []
    sections = allowed_sections(user)
    groups = []
    for section, title, icon, fn in SOURCES:
        if section not in sections:
            continue
        items = list(fn(q, limit))
        if items:
            groups.append({'section': section, 'title': title, 'icon': icon, 'items': items})
    return groups


@login_required
def search(request):
    q = request.GET.get('q', '')
    if request.GET.get('format') == 'json':
        return JsonResponse({'q': q, 'groups': run_search(request.user, q)})
    groups = run_search(request.user, q, limit=50)
    return render(request, 'common/search.html', {'q': q, 'groups': groups})
