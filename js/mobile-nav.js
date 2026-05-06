(function() {
  function initMobileNav() {
    var nav = document.querySelector('.nav');
    var navInner = document.querySelector('.nav-inner');
    if (!nav || !navInner) return;
    if (document.querySelector('.hamburger-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'hamburger-btn';
    btn.setAttribute('aria-label', 'Toggle navigation menu');
    btn.innerHTML = '<span></span><span></span><span></span>';
    nav.insertBefore(btn, navInner);
    btn.addEventListener('click', function() {
      btn.classList.toggle('open');
      navInner.classList.toggle('open');
    });
    navInner.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        btn.classList.remove('open');
        navInner.classList.remove('open');
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMobileNav);
  } else {
    initMobileNav();
  }
})();
