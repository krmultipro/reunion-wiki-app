/* Interactions progressives ; les données et la visibilité restent côté serveur. */
(() => {
  'use strict';
  const fallback = '/static/refonte/profile-placeholder.svg';
  document.querySelectorAll('img[data-portrait],img[data-preview]').forEach(image => {
    const failed = () => {
      if (image.hasAttribute('data-portrait') && !image.src.endsWith('/profile-placeholder.svg')) {
        image.src = fallback;
        image.alt = 'Photo de profil indisponible';
      } else if (image.hasAttribute('data-preview')) image.hidden = true;
    };
    image.addEventListener('error', failed);
    if (image.complete && !image.naturalWidth) failed();
  });
  const listPage = ['sites','personnalites','recherche','home'].includes(document.body.dataset.finalPage);
  const positionKey = 'rw-public-position:' + location.pathname + location.search;
  if (listPage) {
    const remember = () => { try { sessionStorage.setItem(positionKey,String(scrollY)); } catch {} };
    document.addEventListener('click', event => { if (event.target.closest('a')) remember(); });
    addEventListener('pagehide', remember);
    try {
      const saved = Number(sessionStorage.getItem(positionKey));
      if (saved > 0) requestAnimationFrame(() => requestAnimationFrame(() => scrollTo(0,saved)));
    } catch {}
  }
  const share = document.getElementById('profile-share');
  const openShare = document.querySelector('[data-share-open]');
  if (share && openShare) {
    const input = document.getElementById('profile-share-url');
    const message = share.querySelector('[data-share-status]');
    openShare.addEventListener('click', () => { message.textContent = ''; share.showModal(); input.focus(); input.select(); });
    share.addEventListener('close', () => openShare.focus());
    share.querySelector('[data-share-copy]').addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(input.value);
        message.textContent = 'Lien copié.';
      } catch {
        input.focus(); input.select();
        message.textContent = 'Copie le lien sélectionné avec la commande Copier de ton appareil.';
      }
    });
  }
  const track = document.getElementById('home-profile-track');
  if (!track) return;
  const cards = [...track.children];
  const previous = document.getElementById('profile-previous');
  const next = document.getElementById('profile-next');
  const position = document.getElementById('carousel-position');
  const mobile = matchMedia('(max-width:680px)');
  let active = 0, start = null, suppressClick = false;
  track.dataset.ready = 'true';
  track.parentElement.querySelector('.carousel-controls').hidden = cards.length < 2;
  function refresh() {
    const step = Math.min(track.clientWidth * .23,86);
    cards.forEach((card,index) => {
      const distance = Math.abs(index - active);
      card.style.setProperty('--shift',(index - active) * step + 'px');
      card.style.setProperty('--scale',String(Math.max(.68,1 - distance * .14)));
      card.style.setProperty('--opacity',String(Math.max(.35,1 - distance * .25)));
      card.style.zIndex = String(10-distance);
      card.dataset.distance = String(Math.min(distance,3));
      card.tabIndex = mobile.matches && index !== active ? -1 : 0;
      if (mobile.matches && index !== active) card.setAttribute('aria-hidden','true'); else card.removeAttribute('aria-hidden');
    });
    track.style.setProperty('--carousel-height',(Math.max(...cards.map(card => card.offsetHeight)) + 28) + 'px');
    previous.disabled = active === 0;
    next.disabled = active === cards.length - 1;
    position.textContent = `${active + 1} sur ${cards.length}`;
  }
  function move(index) { active = Math.max(0,Math.min(cards.length - 1,index)); refresh(); }
  previous.addEventListener('click',() => move(active - 1));
  next.addEventListener('click',() => move(active + 1));
  track.addEventListener('keydown',event => {
    if (!mobile.matches || event.target !== track) return;
    const keys = {ArrowLeft:active-1,ArrowRight:active+1,Home:0,End:cards.length-1};
    if (Object.hasOwn(keys,event.key)) { event.preventDefault(); move(keys[event.key]); }
  });
  track.addEventListener('click',event => {
    if (!mobile.matches) return;
    if (suppressClick) { event.preventDefault(); suppressClick = false; return; }
    const card = event.target.closest('.creator-card');
    const index = cards.indexOf(card);
    if (index >= 0 && index !== active) { event.preventDefault(); move(index); }
  });
  track.addEventListener('pointerdown',event => { if (mobile.matches && event.isPrimary) start = {x:event.clientX,y:event.clientY,id:event.pointerId}; });
  track.addEventListener('pointerup',event => {
    if (!start || event.pointerId !== start.id) return;
    const dx = event.clientX - start.x, dy = event.clientY - start.y;
    start = null;
    if (Math.abs(dx) > 35 && Math.abs(dx) > Math.abs(dy) * 1.3) {
      move(active + (dx < 0 ? 1 : -1)); suppressClick = true;
      setTimeout(() => { suppressClick = false; },300);
    }
  });
  track.addEventListener('pointercancel',() => { start = null; });
  track.addEventListener('dragstart',event => { if (mobile.matches) event.preventDefault(); });
  const observer = new ResizeObserver(refresh);
  cards.forEach(card => observer.observe(card));
  observer.observe(track); mobile.addEventListener('change',refresh); refresh();
})();
