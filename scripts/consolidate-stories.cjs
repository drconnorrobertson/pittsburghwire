'use strict';
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'..'),map=require('./story-consolidation.json');
function final(u){const abs=u.startsWith('https://www.thepittsburghwire.com');const local=abs?u.slice('https://www.thepittsburghwire.com'.length):u;const [base]=local.split(/[?#]/),tail=local.slice(base.length);const dest=map[base.replace(/\/$/,'')];return dest?(abs?'https://www.thepittsburghwire.com':'')+dest+tail:u;}
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){if(e.name.startsWith('.')||['scripts','node_modules'].includes(e.name))continue;const p=path.join(dir,e.name);if(e.isDirectory()){walk(p);continue;}if(!p.endsWith('.html'))continue;let t=fs.readFileSync(p,'utf8');const n=t.replace(/(href=")([^"]+)(")/g,(_,a,u,b)=>a+final(u)+b);if(n!==t)fs.writeFileSync(p,n);}}
walk(root);
for(const name of fs.readdirSync(root).filter(n=>n.endsWith('.xml')&&n.includes('sitemap'))){const p=path.join(root,name),t=fs.readFileSync(p,'utf8');fs.writeFileSync(p,t.replace(/<url>[^]*?<\/url>/g,entry=>{const u=entry.match(/<loc>([^<]+)<\/loc>/)?.[1];return u&&final(u)!==u?'':entry;}));}
for(const target of new Set(Object.values(map)))if(!fs.existsSync(path.join(root,target,'index.html')))throw Error('Missing story target '+target);
console.log('Consolidated '+Object.keys(map).length+' repeated story URLs; normalized discovery links.');
