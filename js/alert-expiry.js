(() => {
 for(const notice of document.querySelectorAll('[data-alert-expires]')){
  if(Date.now()<Date.parse(notice.dataset.alertExpires))continue;
  const label=document.createElement('strong');label.textContent='Coverage window ended. ';
  notice.replaceChildren(label,document.createTextNode('This notice’s published coverage window has ended. It remains available as an archive; this does not establish that the road, trail or service is now operating normally. Check the linked operator for current conditions.'));
 }
})();
