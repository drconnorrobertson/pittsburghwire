(() => {
  const search = document.getElementById('biz-search');
  const category = document.getElementById('biz-category');
  const count = document.getElementById('biz-count');
  if (!search || !category || !count) return;
  const cards = [...document.querySelectorAll('.biz-card[data-search]')];
  function filter() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const card of cards) {
      card.hidden = !terms.every(term => card.dataset.search.includes(term)) ||
        Boolean(category.value && card.dataset.category !== category.value);
      if (!card.hidden) visible++;
    }
    count.textContent = `${visible.toLocaleString()} business profile${visible === 1 ? '' : 's'}${visible === 0 ? ' — try another name, address, or category.' : ''}`;
  }
  search.addEventListener('input', filter);
  category.addEventListener('change', filter);
})();
