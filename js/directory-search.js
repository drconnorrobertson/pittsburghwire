document.addEventListener('DOMContentLoaded', function () {
  var shell = document.getElementById('directory-search-shell');
  var input = document.getElementById('directory-search');
  var status = document.getElementById('directory-search-status');
  if (!shell || !input || !status) return;

  var profiles = Array.from(document.querySelectorAll('#featured-businesses .biz-card, #more-businesses a'));
  shell.hidden = false;

  input.addEventListener('input', function () {
    var query = input.value.trim().toLocaleLowerCase();
    var shown = 0;
    profiles.forEach(function (profile) {
      var match = !query || profile.textContent.toLocaleLowerCase().includes(query);
      profile.hidden = !match;
      if (match) shown += 1;
    });
    status.textContent = query ? shown + (shown === 1 ? ' profile matches.' : ' profiles match.') : '';
  });
});
