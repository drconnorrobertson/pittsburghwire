(function() {
  function initMobileNav() {
    var nav = document.querySelector('.nav');
    var navInner = document.querySelector('.nav-inner');
    if (!nav || !navInner) return;
    if (document.querySelector('.hamburger-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'hamburger-btn';
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Toggle navigation menu');
    btn.setAttribute('aria-expanded', 'false');
    navInner.id = navInner.id || 'primary-navigation';
    btn.setAttribute('aria-controls', navInner.id);
    btn.innerHTML = '<span></span><span></span><span></span>';
    nav.insertBefore(btn, navInner);
    function setOpen(open) {
      btn.classList.toggle('open', open);
      navInner.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', String(open));
    }
    btn.addEventListener('click', function() {
      setOpen(!navInner.classList.contains('open'));
    });
    nav.addEventListener('keydown', function(event) {
      if (event.key === 'Escape' && navInner.classList.contains('open')) {
        setOpen(false);
        btn.focus();
      }
    });
    navInner.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        setOpen(false);
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileNav);
  } else {
    initMobileNav();
  }
})();
