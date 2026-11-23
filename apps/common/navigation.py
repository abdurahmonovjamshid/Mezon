"""Chap menyu (sidebar) tuzilmasi va brend sozlamalari.

Menyu bitta joyda — shu faylda — guruhlarga ajratib yozilgan. Har bir
band qaysi sahifalarda "faol" ko'rinishi `match` orqali belgilanadi:
(namespace, url nomi prefikslari yoki None — hammasi, istisno prefikslar).
"""
from django.conf import settings
from django.urls import reverse

from apps.accounts.roles import allowed_sections, user_roles

NAV_GROUPS = [
    {
        'title': None,
        'items': [
            {'label': 'Bosh sahifa', 'icon': 'grid-1x2', 'url': 'dashboard:index', 'match': ('dashboard', None, ())},
        ],
    },
    {
        'title': 'Savdo',
        'items': [
            {'label': 'Sotuvlar', 'icon': 'cart-check', 'url': 'sales:list', 'match': ('sales', None, ('due',))},
            {'label': "Muddati kelganlar", 'icon': 'bell', 'url': 'sales:due', 'match': ('sales', ('due',), ()),
             'badge': 'due_sales_count'},
            {'label': 'Mijozlar', 'icon': 'people', 'url': 'customers:list', 'match': ('customers', None, ())},
        ],
    },
    {
        'title': 'Xarid',
        'items': [
            {'label': 'Xaridlar', 'icon': 'bag', 'url': 'purchases:list', 'match': ('purchases', None, ())},
            {'label': 'Yetkazib beruvchilar', 'icon': 'truck', 'url': 'suppliers:list',
             'match': ('suppliers', None, ())},
        ],
    },
    {
        'title': 'Ombor',
        'items': [
            {'label': 'Mahsulotlar', 'icon': 'box-seam', 'url': 'products:list',
             'match': ('products', None, ('category',))},
            {'label': 'Kategoriyalar', 'icon': 'tags', 'url': 'products:category_list',
             'match': ('products', ('category',), ())},
            {'label': 'Qoldiqlar', 'icon': 'boxes', 'url': 'inventory:list',
             'match': ('inventory', None, ('transfer', 'count')), 'badge': 'low_stock_count'},
            {'label': "Ko'chirish", 'icon': 'arrow-left-right', 'url': 'inventory:transfer_list',
             'match': ('inventory', ('transfer',), ())},
            {'label': 'Inventarizatsiya', 'icon': 'clipboard-check', 'url': 'inventory:count_list',
             'match': ('inventory', ('count',), ())},
            {'label': "Bo'laklash", 'icon': 'scissors', 'url': 'butchering:list',
             'match': ('butchering', None, ('specification',))},
            {'label': 'Spetsifikatsiyalar', 'icon': 'diagram-3', 'url': 'butchering:specification_list',
             'match': ('butchering', ('specification',), ())},
        ],
    },
    {
        'title': 'Moliya',
        'items': [
            {'label': 'Kassa', 'icon': 'wallet2', 'url': 'kassa:detail', 'match': ('kassa', None, ())},
            {'label': "To'lovlar", 'icon': 'credit-card-2-front', 'url': 'payments:list',
             'match': ('payments', None, ())},
            {'label': 'Xarajatlar', 'icon': 'receipt', 'url': 'expenses:list', 'match': ('expenses', None, ())},
        ],
    },
    {
        'title': 'Tahlil',
        'items': [
            {'label': 'Hisobotlar', 'icon': 'bar-chart-line', 'url': 'reports:index', 'match': ('reports', None, ())},
        ],
    },
]


def _is_active(match, namespace, url_name):
    ns, include, exclude = match
    if namespace != ns:
        return False
    if exclude and url_name.startswith(exclude):
        return False
    return include is None or url_name.startswith(include)


def navigation(request):
    """Shablonlar uchun: brend nomi va faol band belgilangan menyu guruhlari."""
    context = {
        'allow_negative_stock': getattr(settings, 'ALLOW_NEGATIVE_STOCK', False),
        'APP_NAME': settings.APP_NAME,
        'APP_TAGLINE': settings.APP_TAGLINE,
    }
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return context

    resolver = getattr(request, 'resolver_match', None)
    namespace = resolver.namespace if resolver else ''
    url_name = (resolver.url_name or '') if resolver else ''

    sections = allowed_sections(request.user)
    groups, current = [], None
    for group in NAV_GROUPS:
        items = []
        for item in group['items']:
            if item['match'][0] not in sections:
                continue
            active = _is_active(item['match'], namespace, url_name)
            entry = {**item, 'href': reverse(item['url']), 'active': active}
            if item.get('badge') == 'low_stock_count':
                entry['badge_value'] = _low_stock_count()
            items.append(entry)
            if active:
                current = {'group': group['title'], 'label': item['label'], 'icon': item['icon']}
        if items:
            groups.append({'title': group['title'], 'items': items})
    context.update({
        'nav_groups': groups,
        'nav_current': current,
        'allowed_sections': sections,
        'user_roles': user_roles(request.user),
    })
    return context


def _low_stock_count():
    from apps.inventory.services.alerts import low_stock_products
    return len(low_stock_products())
