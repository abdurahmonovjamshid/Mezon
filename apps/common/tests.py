from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.common.navigation import NAV_GROUPS


class NavigationRenderTests(TestCase):
    """Chap menyudagi har bir sahifa yangi dizaynda xatosiz ochiladi va
    faqat o'z bandi faol (active) bo'ladi."""

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(username='admin', email='a@a.com', password='x')
        self.client.force_login(self.user)

    def test_every_menu_page_renders_with_its_item_active(self):
        for group in NAV_GROUPS:
            for item in group['items']:
                with self.subTest(item=item['url']):
                    response = self.client.get(reverse(item['url']))
                    self.assertEqual(response.status_code, 200)
                    active = [i['label'] for g in response.context['nav_groups'] for i in g['items'] if i['active']]
                    self.assertEqual(active, [item['label']])
                    self.assertContains(response, 'class="sidebar')

    def test_create_pages_render(self):
        for name in ['sales:create', 'purchases:create', 'payments:create', 'expenses:create',
                     'butchering:create', 'inventory:transfer_create', 'inventory:count_create',
                     'customers:create', 'suppliers:create', 'products:create']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_login_page_shows_brand(self):
        self.client.logout()
        response = self.client.get(reverse('login'))
        self.assertContains(response, 'Mezon')
        self.assertNotContains(response, 'Qassobxona')
