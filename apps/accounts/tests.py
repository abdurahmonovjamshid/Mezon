"""Yangi imkoniyatlar: rollar, umumiy qidiruv, kam qoldiq, admin panel (Unfold)."""
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.roles import KASSIR, OMBORCHI, SOTUVCHI, allowed_sections
from apps.customers.models import Customer
from apps.inventory.services import inventory_service
from apps.inventory.services.alerts import low_stock_products
from apps.products.models import Product, ProductCategory

User = get_user_model()


def _user(username, *roles):
    user = User.objects.create_user(username=username, password='x')
    for role in roles:
        user.groups.add(Group.objects.get(name=role))
    return user


class RoleTests(TestCase):
    def test_roles_are_seeded(self):
        self.assertTrue(set(Group.objects.values_list('name', flat=True)) >= {'Rahbar', SOTUVCHI, OMBORCHI, KASSIR})

    def test_user_without_role_sees_everything(self):
        self.client.force_login(_user('eski'))
        self.assertEqual(self.client.get(reverse('reports:index')).status_code, 200)
        self.assertEqual(self.client.get(reverse('kassa:detail')).status_code, 200)

    def test_seller_is_limited(self):
        self.client.force_login(_user('sotuvchi', SOTUVCHI))
        self.assertEqual(self.client.get(reverse('sales:list')).status_code, 200)
        response = self.client.get(reverse('kassa:detail'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "ruxsatingiz yo'q", status_code=403)
        self.assertEqual(self.client.get(reverse('reports:index')).status_code, 403)

        menu = self.client.get(reverse('dashboard:index')).context['nav_groups']
        labels = {item['label'] for group in menu for item in group['items']}
        self.assertIn('Sotuvlar', labels)
        self.assertNotIn('Kassa', labels)
        self.assertNotIn('Hisobotlar', labels)

    def test_multiple_roles_add_up(self):
        user = _user('ikki', OMBORCHI, KASSIR)
        self.assertTrue({'inventory', 'kassa', 'purchases', 'expenses'} <= allowed_sections(user))
        self.assertNotIn('reports', allowed_sections(user))

    def test_superuser_ignores_roles(self):
        admin = User.objects.create_superuser(username='boss', email='b@b.uz', password='x')
        admin.groups.add(Group.objects.get(name=SOTUVCHI))
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse('reports:index')).status_code, 200)


class SearchTests(TestCase):
    def setUp(self):
        category = ProductCategory.objects.create(name='Umumiy', code='gen')
        Product.objects.create(name='Shakar', code='SH-1', category=category)
        Customer.objects.create(name='Shavkat aka', phone='+998901112233')

    def test_json_search_groups(self):
        self.client.force_login(_user('u'))
        data = self.client.get(reverse('search'), {'q': 'sha', 'format': 'json'}).json()
        titles = {g['section']: [i['title'] for i in g['items']] for g in data['groups']}
        self.assertEqual(titles['products'], ['Shakar'])
        self.assertEqual(titles['customers'], ['Shavkat aka'])

    def test_search_by_phone_and_page(self):
        self.client.force_login(_user('u'))
        response = self.client.get(reverse('search'), {'q': '1112233'})
        self.assertContains(response, 'Shavkat aka')

    def test_search_respects_roles(self):
        self.client.force_login(_user('ombor', OMBORCHI))
        data = self.client.get(reverse('search'), {'q': 'sha', 'format': 'json'}).json()
        self.assertEqual([g['section'] for g in data['groups']], ['products'])

    def test_short_query_returns_nothing(self):
        self.client.force_login(_user('u'))
        self.assertEqual(self.client.get(reverse('search'), {'q': 's', 'format': 'json'}).json()['groups'], [])


class LowStockTests(TestCase):
    def setUp(self):
        category = ProductCategory.objects.create(name='Umumiy', code='gen')
        self.product = Product.objects.create(name='Un', code='UN', category=category, min_stock=Decimal('20'))
        Product.objects.create(name='Tuz', code='TUZ', category=category)  # kuzatilmaydi
        inventory_service.stock_in(product=self.product, quantity=Decimal('50'), movement_type='PURCHASE',
                                   unit_cost=Decimal('100'), date=timezone.localdate())

    def _out(self, qty):
        inventory_service.stock_out(product=self.product, quantity=Decimal(qty), movement_type='SALE',
                                    unit_cost=Decimal('100'), date=timezone.localdate())

    def test_low_stock_detection(self):
        self.assertEqual(low_stock_products(), [])
        self._out('30')  # 20 qoldi — chegarada
        rows = low_stock_products()
        self.assertEqual([r['product'].name for r in rows], ['Un'])
        self.assertEqual(rows[0]['stock'], Decimal('20'))

    def test_dashboard_and_sidebar_show_warning(self):
        self._out('35')
        self.client.force_login(_user('u'))
        response = self.client.get(reverse('dashboard:index'))
        self.assertContains(response, 'Kam qolgan mahsulotlar')
        self.assertContains(response, 'nav-badge-warn')

    def test_admins_notified_once_when_crossing(self):
        with patch('apps.bot.admin_notify.notify_low_stock') as notify, \
                self.captureOnCommitCallbacks(execute=True):
            self._out('10')   # 40 — hali chegaradan yuqori
            self._out('25')   # 15 — chegaradan o'tdi
            self._out('5')    # 10 — allaqachon past, qayta xabar yo'q
        self.assertEqual(notify.call_count, 1)
        self.assertEqual(notify.call_args.args[1], Decimal('15'))


@patch('telebot.apihelper._make_request')
class BotRoleAndLowStockTests(TestCase):
    def _sent(self, mock):
        sent = []

        def fake(token, method_url, method='get', params=None, files=None):
            sent.append({'method': method_url, 'params': params or {}})
            if method_url == 'sendMessage':
                return {'message_id': 1, 'date': 0, 'chat': {'id': 1, 'type': 'private'}, 'text': ''}
            return True
        mock.side_effect = fake
        return sent

    def _message(self, text):
        return SimpleNamespace(text=text, message_id=5, chat=SimpleNamespace(id=1), from_user=SimpleNamespace(id=1))

    def test_menu_hidden_and_blocked_for_role(self, mock):
        from apps.bot import keyboards
        from apps.bot.handlers.common import on_text
        from apps.bot.models import TgUser
        sent = self._sent(mock)
        TgUser.objects.create(telegram_id=1, django_user=_user('tgsotuvchi', SOTUVCHI))

        on_text(self._message('/start'))
        import json
        rows = json.loads(sent[-1]['params']['reply_markup'])['keyboard']
        keyboard = [button['text'] for row in rows for button in row]
        self.assertIn(keyboards.MENU_SALES, keyboard)
        self.assertNotIn(keyboards.MENU_KASSA, keyboard)

        on_text(self._message(keyboards.MENU_KASSA))
        self.assertIn('ruxsat etilmagan', sent[-1]['params']['text'])

    def test_inventory_low_stock_button(self, mock):
        from apps.bot.handlers.inventory import low_stock
        from apps.bot.models import TgUser
        sent = self._sent(mock)
        category = ProductCategory.objects.create(name='Umumiy', code='gen')
        Product.objects.create(name='Guruch', code='GR', category=category, min_stock=Decimal('5'))
        tg_user = TgUser.objects.create(telegram_id=1)
        low_stock(SimpleNamespace(id='c', data='invlow:1', message=SimpleNamespace(chat=SimpleNamespace(id=1))), tg_user)
        self.assertIn('Guruch', sent[-1]['params']['text'])


class AdminPanelTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_superuser(username='a', email='a@a.uz', password='x'))

    def test_admin_index_and_changelists_render(self):
        from django.contrib import admin
        self.assertContains(self.client.get(reverse('admin:index')), 'Mezon')
        for model in admin.site._registry:
            meta = model._meta
            with self.subTest(model=meta.label):
                url = reverse(f'admin:{meta.app_label}_{meta.model_name}_changelist')
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_user_form_shows_roles(self):
        user = _user('x')
        response = self.client.get(reverse('admin:auth_user_change', args=[user.pk]))
        self.assertContains(response, 'Rollar')
