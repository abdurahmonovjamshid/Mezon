from django.shortcuts import render

from apps.accounts.roles import SECTIONS, can_access


class RoleAccessMiddleware:
    """Rolga ruxsat etilmagan bo'lim sahifasini ochishga urinilganda 403
    sahifasini ko'rsatadi (menyuda bunday bo'limlar umuman ko'rinmaydi)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = getattr(request, 'user', None)
        match = getattr(request, 'resolver_match', None)
        if not user or not user.is_authenticated or not match:
            return None
        section = match.namespace
        if section in SECTIONS and not can_access(user, section):
            return render(request, 'errors/forbidden.html', status=403)
        return None
