(() => {
  const search=document.getElementById('biz-search'),category=document.getElementById('biz-category'),count=document.getElementById('biz-count'),grid=document.querySelector('.biz-grid'),pages=document.getElementById('directory-pages');
  if(!search||!category||!count||!grid||!pages)return;
  const initial=grid.innerHTML,label=count.textContent;
  const normalize=s=>s.normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
  let dataPromise,version=0,limit=60;
  async function filter(){const run=++version,terms=normalize(search.value).split(/\s+/).filter(Boolean),cat=category.value;
    if(!terms.length&&!cat){grid.innerHTML=initial;count.textContent=label;pages.hidden=false;document.getElementById('directory-more')?.remove();return;}
    count.textContent='Searching all business profiles…';
    try{dataPromise??=fetch('/data/directory-search.json').then(r=>{if(!r.ok)throw Error('Directory unavailable');return r.json();}).catch(e=>{dataPromise=undefined;throw e;});const data=await dataPromise;if(run!==version)return;
      const found=data.filter(r=>(!cat||r.category===cat)&&terms.every(t=>normalize(r.search).includes(t)));grid.replaceChildren();pages.hidden=true;
      for(const r of found.slice(0,limit)){const a=document.createElement('a');a.className='biz-card';a.href=r.url;for(const [cls,text] of [['biz-name',r.name],['biz-owner',r.detail]]){const d=document.createElement('div');d.className=cls;d.textContent=text;a.append(d);}grid.append(a);}
      count.textContent=`${found.length.toLocaleString()} matching profiles; showing ${Math.min(limit,found.length).toLocaleString()}.`;document.getElementById('directory-more')?.remove();
      if(found.length>limit){const b=document.createElement('button');b.id='directory-more';b.type='button';b.textContent='Show more results';b.addEventListener('click',()=>{limit+=60;filter();});grid.after(b);}
    }catch{if(run===version){grid.innerHTML=initial;pages.hidden=false;count.textContent='Search is temporarily unavailable. Use the directory pages and category links to browse all profiles.';}}
  }
  let timer;search.addEventListener('input',()=>{limit=60;clearTimeout(timer);timer=setTimeout(filter,180);});category.addEventListener('change',()=>{limit=60;filter();});search.addEventListener('search',filter);if(search.value||category.value)filter();
})();
