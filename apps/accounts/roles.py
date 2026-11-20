"""Foydalanuvchi rollari.

Rol — oddiy Django guruhi (Group). Foydalanuvchini admin panelda
"Guruhlar" maydoni orqali bir yoki bir nechta rolga qo'shasiz; u holda
saytda (va botda) faqat o'sha rollarga ruxsat etilgan bo'limlar ko'rinadi.

- Superuser va hech qanday rolga biriktirilmagan foydalanuvchi — hamma
  bo'limni ko'radi (eski foydalanuvchilar uchun hech narsa o'zgarmaydi).
- Bir nechta rol bo'lsa, ruxsatlar qo'shiladi.

Bo'lim = URL namespace (masalan `sales`, `kassa`).
"""
RAHBAR = 'Rahbar'
SOTUVCHI = 'Sotuvchi'
OMBORCHI = 'Omborchi'
KASSIR = 'Kassir'

SECTIONS = (
    'dashboard', 'sales', 'customers', 'purchases', 'suppliers', 'products',
    'inventory', 'butchering', 'kassa', 'payments', 'expenses', 'reports',
)

ROLE_SECTIONS = {
    RAHBAR: set(SECTIONS),
    SOTUVCHI: {'dashboard', 'sales', 'customers', 'products', 'payments'},
    OMBORCHI: {'dashboard', 'products', 'inventory', 'butchering', 'purchases', 'suppliers'},
    KASSIR: {'dashboard', 'kassa', 'payments', 'expenses', 'sales', 'customers', 'suppliers'},
}

ROLE_DESCRIPTIONS = {
    RAHBAR: "Hamma bo'limlar, jumladan hisobotlar",
    SOTUVCHI: "Sotuvlar, mijozlar, mahsulotlar, to'lovlar",
    OMBORCHI: "Mahsulotlar, ombor, ko'chirish, bo'laklash, xaridlar, yetkazib beruvchilar",
    KASSIR: "Kassa, to'lovlar, xarajatlar, sotuvlar, mijozlar, yetkazib beruvchilar",
}


def allowed_sections(user):
    """Foydalanuvchi ko'ra oladigan bo'limlar to'plami."""
    if user is None or not getattr(user, 'is_authenticated', False):
        return set(SECTIONS)
    if user.is_superuser:
        return set(SECTIONS)
    cache = getattr(user, '_mz_sections', None)
    if cache is not None:
        return cache
    roles = [name for name in user.groups.values_list('name', flat=True) if name in ROLE_SECTIONS]
    if not roles:
        sections = set(SECTIONS)
    else:
        sections = set()
        for role in roles:
            sections |= ROLE_SECTIONS[role]
    user._mz_sections = sections
    return sections


def can_access(user, section):
    return section not in SECTIONS or section in allowed_sections(user)


def user_roles(user):
    if user is None or not getattr(user, 'is_authenticated', False):
        return []
    return [name for name in user.groups.values_list('name', flat=True) if name in ROLE_SECTIONS]
