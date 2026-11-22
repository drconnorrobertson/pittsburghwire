(() => {
  const controls = document.getElementById('category-search-controls');
  const search = document.getElementById('category-search');
  const clear = document.getElementById('category-search-clear');
  const count = document.getElementById('category-search-count');
  const empty = document.getElementById('category-search-empty');
  const grid = document.getElementById('category-directory-results');
  if (!controls || !search || !clear || !count || !empty || !grid) return;
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const cards = [...grid.querySelectorAll('.biz-card')].map(card => ({card, text: normalize(card.dataset.search || card.textContent)}));
  const total = cards.length;
  function apply() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    let matched = 0;
    for (const row of cards) {
      row.card.hidden = !terms.every(term => row.text.includes(term));
      if (!row.card.hidden) matched++;
    }
    count.textContent = terms.length
      ? `${matched.toLocaleString()} matching ${matched === 1 ? 'profile' : 'profiles'} of ${total.toLocaleString()}`
      : `${total.toLocaleString()} profiles in this category`;
    empty.hidden = matched !== 0;
    clear.disabled = search.value.length === 0;
  }
  search.addEventListener('input', apply);
  search.addEventListener('search', apply);
  search.addEventListener('keydown', event => {
    if (event.key === 'Escape') { search.value = ''; apply(); }
  });
  clear.addEventListener('click', () => { search.value = ''; apply(); search.focus(); });
  controls.hidden = false;
  apply();
})();
