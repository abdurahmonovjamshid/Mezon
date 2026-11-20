/* Mezon: umumiy interfeys — menyuni yig'ish, yorug'/qorong'i rejim, umumiy qidiruv. */
(function () {
    'use strict';
    var root = document.documentElement;

    function store(key, value) {
        try { localStorage.setItem(key, value); } catch (e) { /* maxfiy rejimda saqlanmaydi */ }
    }

    // Chap menyuni yig'ish / yoyish
    document.querySelectorAll('[data-action="toggle-sidebar"]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var mini = root.classList.toggle('sidebar-mini');
            store('mz-sidebar', mini ? 'mini' : 'full');
        });
    });

    // Yorug' / qorong'i rejim
    document.querySelectorAll('[data-action="toggle-theme"]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var next = root.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            root.setAttribute('data-bs-theme', next);
            store('mz-theme', next);
            document.dispatchEvent(new CustomEvent('mz:theme', { detail: next }));
        });
    });

    // Telefonda menyuni havola orqali ochish: /dashboard/#menu
    if (window.location.hash === '#menu' && window.bootstrap && window.innerWidth < 992) {
        var sidebar = document.getElementById('appSidebar');
        if (sidebar) window.bootstrap.Offcanvas.getOrCreateInstance(sidebar).show();
    }

    // Umumiy qidiruv (yuqori panel)
    var input = document.getElementById('globalSearch');
    var box = document.getElementById('searchDropdown');
    if (!input || !box) return;
    var form = input.form;
    var timer = null;
    var lastQuery = '';
    var activeIndex = -1;

    function esc(text) {
        var div = document.createElement('div');
        div.textContent = text == null ? '' : String(text);
        return div.innerHTML;
    }

    function links() { return box.querySelectorAll('a.search-item'); }

    function setActive(index) {
        var items = links();
        items.forEach(function (a) { a.classList.remove('active'); });
        if (!items.length) { activeIndex = -1; return; }
        activeIndex = (index + items.length) % items.length;
        items[activeIndex].classList.add('active');
        items[activeIndex].scrollIntoView({ block: 'nearest' });
    }

    function render(data) {
        activeIndex = -1;
        if (!data.groups.length) {
            box.innerHTML = '<div class="search-empty">Hech narsa topilmadi</div>';
        } else {
            box.innerHTML = data.groups.map(function (g) {
                return '<div class="search-group"><div class="search-group-title"><i class="bi bi-' + esc(g.icon) + '"></i> ' + esc(g.title) + '</div>' +
                    g.items.map(function (item) {
                        return '<a class="search-item" href="' + esc(item.url) + '"><span class="search-item-title">' + esc(item.title) +
                            '</span><span class="search-item-sub">' + esc(item.subtitle) + '</span></a>';
                    }).join('') + '</div>';
            }).join('') +
                '<a class="search-all" href="' + form.action + '?q=' + encodeURIComponent(data.q) + '">Barcha natijalar <i class="bi bi-arrow-right"></i></a>';
        }
        box.hidden = false;
    }

    function query() {
        var q = input.value.trim();
        if (q.length < 2) { box.hidden = true; lastQuery = ''; return; }
        if (q === lastQuery) { box.hidden = false; return; }
        lastQuery = q;
        fetch(form.action + '?format=json&q=' + encodeURIComponent(q), { headers: { 'X-Requested-With': 'fetch' } })
            .then(function (r) { return r.ok ? r.json() : null; })
            .then(function (data) { if (data && data.q.trim() === input.value.trim()) render(data); })
            .catch(function () { /* tarmoq xatosi — jim */ });
    }

    input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(query, 220);
    });
    input.addEventListener('focus', query);
    input.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); setActive(activeIndex + 1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(activeIndex - 1); }
        else if (e.key === 'Escape') { box.hidden = true; input.blur(); }
        else if (e.key === 'Enter' && activeIndex >= 0) {
            e.preventDefault();
            window.location.href = links()[activeIndex].href;
        }
    });
    document.addEventListener('click', function (e) {
        if (!form.contains(e.target)) box.hidden = true;
    });
    // "/" tugmasi — qidiruvga o'tish (matn maydonida yozilayotganda emas)
    document.addEventListener('keydown', function (e) {
        var tag = (e.target.tagName || '').toLowerCase();
        if (e.key === '/' && tag !== 'input' && tag !== 'textarea' && tag !== 'select' && !e.target.isContentEditable) {
            e.preventDefault();
            input.focus();
        }
    });
})();
