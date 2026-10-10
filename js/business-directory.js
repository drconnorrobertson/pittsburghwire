(() => {
  const search = document.getElementById('biz-search');
  const category = document.getElementById('biz-category');
  const count = document.getElementById('biz-count');
  if (!search || !category || !count) return;
  const cards = [...document.querySelectorAll('.biz-card[data-search]')];
  const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const searchable = new Map(cards.map(card => [card, normalize(card.dataset.search)]));
  function filter() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      card.hidden = !terms.every(term => searchable.get(card).includes(term)) ||
        Boolean(category.value && card.dataset.category !== category.value);
      if (!card.hidden) visible++;
    }
    count.textContent = `${visible.toLocaleString()} business profile${visible === 1 ? '' : 's'}${visible === 0 ? ' — try another name, address, or category.' : ''}`;
  }
  search.addEventListener('input', filter);
  category.addEventListener('change', filter);
  search.addEventListener('search', filter);
  window.addEventListener('pageshow', filter);
  filter();
})();
