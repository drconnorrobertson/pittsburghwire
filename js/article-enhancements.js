/* Pittsburgh Wire - Article Page Enhancements
   Auto-injects: social share buttons, sticky newsletter bar, ad zones */
(function(){
  /* ---- SOCIAL SHARE BUTTONS ---- */
  var meta = document.querySelector('.article-meta');
  if(meta){
    var url = encodeURIComponent(window.location.href);
    var title = encodeURIComponent(document.querySelector('.article-headline') ? document.querySelector('.article-headline').textContent.trim() : document.title);
    var btnBase = 'display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;border:1px solid #c8bfad;color:#6b6355;font-size:13px;font-family:Barlow Condensed,sans-serif;font-weight:700;transition:all .15s;text-decoration:none;';
    var shareHtml = '<div class="share-buttons" style="display:flex;gap:8px;margin-left:auto;">';
    shareHtml += '<a href="https://twitter.com/intent/tweet?url='+url+'&text='+title+'" target="_blank" rel="noopener" title="Share on X" style="'+btnBase+'">X</a>';
    shareHtml += '<a href="https://www.linkedin.com/sharing/share-offsite/?url='+url+'" target="_blank" rel="noopener" title="Share on LinkedIn" style="'+btnBase+'">in</a>';
    shareHtml += '<a href="https://www.facebook.com/sharer/sharer.php?u='+url+'" target="_blank" rel="noopener" title="Share on Facebook" style="'+btnBase+'">f</a>';
    shareHtml += '</div>';
    meta.insertAdjacentHTML('beforeend', shareHtml);

    // Hover effects
    document.querySelectorAll('.share-buttons a').forEach(function(btn){
      var colors = {X:'#000',in:'#0077b5',f:'#1877f2'};
      var c = colors[btn.textContent] || '#b5001f';
      btn.addEventListener('mouseenter', function(){ btn.style.background=c; btn.style.color='#fff'; btn.style.borderColor=c; });
      btn.addEventListener('mouseleave', function(){ btn.style.background=''; btn.style.color='#6b6355'; btn.style.borderColor='#c8bfad'; });
    });
  }

  /* ---- BOTTOM SHARE BAR (after article tags) ---- */
  var tags = document.querySelector('.article-tags');
  if(tags){
    var url2 = encodeURIComponent(window.location.href);
    var title2 = encodeURIComponent(document.querySelector('.article-headline') ? document.querySelector('.article-headline').textContent.trim() : document.title);
    var bottomShare = document.createElement('div');
    bottomShare.style.cssText = 'display:flex;align-items:center;gap:12px;margin-top:24px;padding-top:24px;border-top:1px solid #c8bfad;';
    bottomShare.innerHTML = '<span style="font-family:Barlow Condensed,sans-serif;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#a09585;">Share This Story</span>'
      + '<a href="https://twitter.com/intent/tweet?url='+url2+'&text='+title2+'" target="_blank" rel="noopener" style="font-family:Barlow Condensed,sans-serif;font-size:11px;font-weight:700;letter-spacing:1px;color:#6b6355;border:1px solid #c8bfad;padding:5px 12px;text-decoration:none;transition:all .15s;">X / Twitter</a>'
      + '<a href="https://www.linkedin.com/sharing/share-offsite/?url='+url2+'" target="_blank" rel="noopener" style="font-family:Barlow Condensed,sans-serif;font-size:11px;font-weight:700;letter-spacing:1px;color:#6b6355;border:1px solid #c8bfad;padding:5px 12px;text-decoration:none;transition:all .15s;">LinkedIn</a>'
      + '<a href="https://www.facebook.com/sharer/sharer.php?u='+url2+'" target="_blank" rel="noopener" style="font-family:Barlow Condensed,sans-serif;font-size:11px;font-weight:700;letter-spacing:1px;color:#6b6355;border:1px solid #c8bfad;padding:5px 12px;text-decoration:none;transition:all .15s;">Facebook</a>';
    tags.insertAdjacentElement('afterend', bottomShare);
  }

  /* ---- AD ZONES ---- */
  var adStyle = 'background:#ede8dc;border:1px dashed #c8bfad;min-height:90px;display:flex;align-items:center;justify-content:center;font-family:Barlow Condensed,sans-serif;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#a09585;margin:32px 0;';
  var sidebar = document.querySelector('.article-sidebar');
  if(sidebar){
    var adDiv = document.createElement('div');
    adDiv.className = 'sidebar-module ad-zone';
    adDiv.style.cssText = adStyle + 'min-height:250px;';
    sidebar.appendChild(adDiv);
  }
  var moreStories = document.querySelector('.more-stories');
  if(moreStories){
    var adDiv2 = document.createElement('div');
    adDiv2.className = 'ad-zone ad-zone-leaderboard';
    adDiv2.style.cssText = adStyle + 'max-width:728px;margin:20px auto 0;';
    moreStories.parentNode.insertBefore(adDiv2, moreStories);
  }

  /* ---- STICKY NEWSLETTER BAR ---- */
  var stickyEl = document.createElement('div');
  stickyEl.id = 'sticky-newsletter';
  stickyEl.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#0f0e0c;border-top:2px solid #b5001f;padding:12px 28px;z-index:9998;display:flex;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap;transform:translateY(100%);transition:transform .4s ease;';
  stickyEl.innerHTML = '<span style="font-family:Barlow Condensed,sans-serif;font-size:13px;font-weight:600;letter-spacing:1px;color:#f5f0e8;">Get Pittsburgh’s best business news weekly. <strong style="color:#8a6a00">Join 5,000+ readers.</strong></span>'
    + '<form style="display:flex;gap:0;" action="https://formspree.io/f/xpwddjla" method="POST" onsubmit="this.querySelector(\'button\').textContent=\'Done!\';this.querySelector(\'button\').disabled=true;document.getElementById(\'sticky-newsletter\').style.display=\'none\';return true;">'
    + '<input type="email" name="email" placeholder="your@email.com" required style="font-family:Source Serif 4,Georgia,serif;font-size:13px;padding:7px 14px;border:1px solid #333;border-right:none;background:#1a1a1a;color:#f5f0e8;outline:none;min-width:200px;" />'
    + '<button type="submit" style="font-family:Barlow Condensed,sans-serif;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;background:#b5001f;color:#fff;border:1px solid #b5001f;padding:7px 16px;cursor:pointer;">Subscribe</button>'
    + '</form>'
    + '<button onclick="document.getElementById(\'sticky-newsletter\').style.display=\'none\';" style="background:none;border:none;color:#666;font-size:18px;cursor:pointer;padding:0 4px;line-height:1;">×</button>';
  document.body.appendChild(stickyEl);
  var stickyShown = false;
  window.addEventListener('scroll', function(){
    if(!stickyShown && window.scrollY > document.body.scrollHeight * 0.35){
      stickyEl.style.transform = 'translateY(0)';
      stickyShown = true;
    }
  });
})();
