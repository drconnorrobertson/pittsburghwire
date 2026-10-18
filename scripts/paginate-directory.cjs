'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),file=path.join(root,'directory/index.html'),dataFile=path.join(root,'data/directory-search.json');
const escape=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const decode=s=>s.replace(/&amp;/g,'&').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>');
let html=fs.readFileSync(file,'utf8');
const pattern=/<a class="biz-card" data-search="([^"]*)" data-category="([^"]*)" href="([^"]*)"><div class="biz-name">([^]*?)<\/div><div class="biz-owner">([^]*?)<\/div><\/a>/g;
const matches=[...html.matchAll(pattern)];
let data;if(!html.includes('<!-- directory-pagination:start -->')){data=matches.map(m=>({search:decode(m[1]),category:m[2],url:m[3],name:decode(m[4]),detail:decode(m[5])}));if(data.length<100)throw Error('Unexpected catalog size');fs.writeFileSync(dataFile,JSON.stringify(data));}else data=JSON.parse(fs.readFileSync(dataFile,'utf8'));
const size=60,total=Math.ceil(data.length/size),site='https://www.thepittsburghwire.com';
const card=r=>`<a class="biz-card" data-search="${escape(r.search)}" data-category="${escape(r.category)}" href="${escape(r.url)}"><div class="biz-name">${escape(r.name)}</div><div class="biz-owner">${escape(r.detail)}</div></a>`;
// Use the existing page design and all collection/service links.
const first=matches[0];if(!first)throw Error('No directory cards');const last=matches.at(-1);const template=html.slice(0,first.index)+'<!-- DIRECTORY_CARDS -->'+html.slice(last.index+last[0].length);
const nav=n=>`<!-- directory-pagination:start --><nav id="directory-pages" aria-label="Directory pages"><p>Browse ${data.length.toLocaleString()} profiles. Page ${n} of ${total}. Search checks all profiles.</p>${Array.from({length:total},(_,i)=>{const p=i+1;return `<a href="${p===1?'/directory':'/directory/page/'+p+'/'}"${p===n?' aria-current="page"':''}>${p}</a>`;}).join(' · ')}</nav><!-- directory-pagination:end -->`;
for(let n=1;n<=total;n++){
 const rows=data.slice((n-1)*size,n*size),url=site+(n===1?'/directory':'/directory/page/'+n+'/');let page=template.replace('<!-- DIRECTORY_CARDS -->',rows.map(card).join('\n'));
 page=page.replace(/<!-- directory-pagination:start -->[^]*?<!-- directory-pagination:end -->/g,'');
 page=page.replace('<p id="biz-count"',nav(n)+'<p id="biz-count"');
 page=page.replace(/<p id="biz-count"[^>]*>[^]*?<\/p>/,`<p id="biz-count" aria-live="polite">Showing ${(n-1)*size+1}–${Math.min(n*size,data.length)} of ${data.length.toLocaleString()} profiles</p>`);
 page=page.replace(/<noscript>[^]*?<\/noscript>/,'<noscript><p>Use the page links to browse all profiles without JavaScript.</p></noscript>');
 page=page.replace(/business-directory\.js\?v=[^" ]+/g,'business-directory.js?v=20261018');
 page=page.replace(/<link rel="canonical" href="[^"]*"\s*\/?>/,`<link rel="canonical" href="${url}">`).replace(/<meta property="og:url" content="[^"]*"\s*\/?>/,`<meta property="og:url" content="${url}">`);
 if(n>1)page=page.replace(/<title>[^]*?<\/title>/,`<title>Pittsburgh Business Directory — Page ${n} | The Pittsburgh Wire</title>`);
 page=page.replace(/<script type="application\/ld\+json">([^]*?)<\/script>/g,(tag,body)=>{const graph=JSON.parse(body);function walk(o){if(!o||typeof o!=='object')return; if(o['@type']==='CollectionPage'){o.url=url;delete o.dateModified;}if(o['@type']==='ItemList'&&Array.isArray(o.itemListElement)){o.numberOfItems=rows.length;o.itemListElement=rows.map((r,i)=>({'@type':'ListItem',position:(n-1)*size+i+1,name:r.name,url:site+r.url}));}for(const v of Object.values(o))if(typeof v==='object')Array.isArray(v)?v.forEach(walk):walk(v);}walk(graph);return '<script type="application/ld+json">'+JSON.stringify(graph).replace(/</g,'\\u003c')+'</script>';});
 const dest=n===1?file:path.join(root,'directory/page',String(n),'index.html');fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,page);
}
let sitemap=fs.readFileSync(path.join(root,'sitemap.xml'),'utf8').replace(/<url>\s*<loc>https:\/\/www\.thepittsburghwire\.com\/directory\/page\/\d+\/[^]*?<\/url>/g,'');
sitemap=sitemap.replace('</urlset>',Array.from({length:total-1},(_,i)=>`<url><loc>${site}/directory/page/${i+2}/</loc></url>`).join('\n')+'\n</urlset>');fs.writeFileSync(path.join(root,'sitemap.xml'),sitemap);
console.log(`Paginated ${data.length} intact listings into ${total} pages. First page: ${fs.statSync(file).size} bytes.`);
