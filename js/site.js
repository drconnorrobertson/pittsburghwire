/* The Pittsburgh Wire — shared behaviour.
   Keeps the topbar dateline current instead of freezing whatever date the page
   happened to be generated on. */
(function () {
  function stampDate() {
    var els = document.querySelectorAll('[data-today]');
    if (!els.length) return;
    var text;
    try {
      text = new Date().toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
      });
    } catch (e) {
      return; // leave the static fallback in place
    }
    for (var i = 0; i < els.length; i++) {
      els[i].innerHTML = text + '  •  Pittsburgh, PA';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', stampDate);
  } else {
    stampDate();
  }
})();
