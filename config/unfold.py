"""Admin panel (django-unfold) ko'rinishi: Mezon ranglari, logotip va
guruhlangan chap menyu."""
from django.templatetags.static import static
from django.urls import reverse_lazy


def _cl(app, model):
    return reverse_lazy(f'admin:{app}_{model}_changelist')


def _item(title, icon, app, model):
    return {'title': title, 'icon': icon, 'link': _cl(app, model)}


TEAL = {
    '50': 'oklch(98.4% .014 180.72)',
    '100': 'oklch(95.3% .051 180.801)',
    '200': 'oklch(91% .096 180.426)',
    '300': 'oklch(85.5% .138 181.071)',
    '400': 'oklch(77.7% .152 181.912)',
    '500': 'oklch(70.4% .14 182.503)',
    '600': 'oklch(60% .118 184.704)',
    '700': 'oklch(51.1% .096 186.391)',
    '800': 'oklch(43.7% .078 188.216)',
    '900': 'oklch(38.6% .063 188.416)',
    '950': 'oklch(27.7% .046 192.524)',
}


def build_unfold_config(app_name, tagline):
    return {
        'SITE_TITLE': f'{app_name} admin',
        'SITE_HEADER': app_name,
        'SITE_SUBHEADER': tagline,
        'SITE_URL': '/',
        'SITE_ICON': lambda request: static('img/logo.svg'),
        'SITE_SYMBOL': 'balance',
        'SITE_FAVICONS': [
            {'rel': 'icon', 'sizes': 'any', 'type': 'image/svg+xml', 'href': lambda request: static('img/logo.svg')},
        ],
        'SHOW_HISTORY': True,
        'SHOW_VIEW_ON_SITE': True,
        'SHOW_BACK_BUTTON': True,
        'COLORS': {'primary': TEAL},
        'LOGIN': {
            'image': lambda request: static('img/admin-login.svg'),
        },
        'SIDEBAR': {
            'show_search': True,
            'show_all_applications': True,
            'navigation': [
                {
                    'title': 'Umumiy',
                    'items': [
                        {'title': 'Saytga qaytish', 'icon': 'arrow_back', 'link': reverse_lazy('dashboard:index')},
                        {'title': 'Admin bosh sahifa', 'icon': 'dashboard', 'link': reverse_lazy('admin:index')},
                    ],
                },
                {
                    'title': 'Savdo',
                    'collapsible': True,
                    'items': [
                        _item('Sotuvlar', 'shopping_cart', 'sales', 'sale'),
                        _item('Sotuv qatorlari', 'list_alt', 'sales', 'saleitem'),
                        _item('Mijozlar', 'group', 'customers', 'customer'),
                    ],
                },
                {
                    'title': 'Xarid',
                    'collapsible': True,
                    'items': [
                        _item('Xaridlar', 'shopping_bag', 'purchases', 'purchase'),
                        _item('Xarid xarajatlari', 'request_quote', 'purchases', 'purchaseexpense'),
                        _item('Yetkazib beruvchilar', 'local_shipping', 'suppliers', 'supplier'),
                    ],
                },
                {
                    'title': 'Ombor',
                    'collapsible': True,
                    'items': [
                        _item('Mahsulotlar', 'inventory_2', 'products', 'product'),
                        _item('Kategoriyalar', 'sell', 'products', 'productcategory'),
                        _item('Omborlar', 'warehouse', 'inventory', 'warehouse'),
                        _item('Ombor harakatlari', 'swap_vert', 'inventory', 'stockmovement'),
                        _item("Ko'chirishlar", 'sync_alt', 'inventory', 'stocktransfer'),
                        _item('Inventarizatsiya', 'fact_check', 'inventory', 'inventorycount'),
                        _item("Bo'laklash", 'content_cut', 'butchering', 'butchering'),
                        _item("Bo'laklash natijalari", 'call_split', 'butchering', 'butcheringoutput'),
                        _item('Spetsifikatsiyalar', 'account_tree', 'butchering', 'butcheringspecification'),
                    ],
                },
                {
                    'title': 'Moliya',
                    'collapsible': True,
                    'items': [
                        _item('Kassalar', 'account_balance_wallet', 'kassa', 'cashregister'),
                        _item('Kassa harakatlari', 'receipt_long', 'kassa', 'cashtransaction'),
                        _item("To'lovlar", 'payments', 'payments', 'payment'),
                        _item('Xarajatlar', 'receipt', 'expenses', 'expense'),
                        _item('Xarajat turlari', 'category', 'expenses', 'expensecategory'),
                    ],
                },
                {
                    'title': 'Foydalanuvchilar',
                    'collapsible': True,
                    'items': [
                        _item('Foydalanuvchilar', 'person', 'auth', 'user'),
                        _item('Rollar', 'shield_person', 'auth', 'group'),
                        _item('Telegram foydalanuvchilar', 'send', 'bot', 'tguser'),
                    ],
                },
            ],
        },
    }
