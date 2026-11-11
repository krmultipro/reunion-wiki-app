/* UX-PC-006 : pagination progressive du catalogue public déjà filtré par Flask. */
(() => {
  'use strict';
  if (!document.body.classList.contains('desktop-responsive')) return;
  const desktop = matchMedia('(min-width:1000px)');
  document.querySelectorAll('[data-desktop-pagination]').forEach(grid => {
    const cards = [...grid.children];
    if (!cards.length) return;
    const label = grid.dataset.pageLabel;
    const status = document.createElement('p');
    status.className = 'desktop-only desktop-page-status';
    status.setAttribute('role','status');
    status.tabIndex = -1;
    grid.before(status);
    const nav = document.createElement('nav');
    nav.className = 'desktop-only desktop-pagination';
    nav.setAttribute('aria-label',label === 'Personnalités' ? 'Pages des personnalités' : 'Pages des sites');
    grid.after(nav);
    const pageURL = number => {
      const url = new URL(location.href);
      if (number === 1) url.searchParams.delete('page'); else url.searchParams.set('page',String(number));
      return url.pathname + url.search;
    };
    function refreshReturns() {
      const current = location.pathname + location.search;
      document.querySelectorAll('a[href]').forEach(anchor => {
        const url = new URL(anchor.href,location.href);
        if (url.origin === location.origin && url.searchParams.has('retour')) {
          url.searchParams.set('retour',current);
          anchor.href = url.pathname + url.search;
        }
      });
    }
    function render(focus = false) {
      nav.replaceChildren();
      if (!desktop.matches) {
        cards.forEach(card => { card.hidden = false; });
        nav.hidden = status.hidden = true;
        return;
      }
      const pages = Math.ceil(cards.length / 12);
      const params = new URL(location.href).searchParams;
      const requested = Number(params.get('page') || 1);
      const number = Number.isFinite(requested) ? Math.max(1,Math.min(pages,Math.floor(requested))) : 1;
      if (requested !== number || number === 1 && params.has('page')) history.replaceState(null,'',pageURL(number));
      cards.forEach((card,index) => { card.hidden = index < (number - 1) * 12 || index >= number * 12; });
      status.textContent = `Page ${number} sur ${pages} · ${label}`;
      nav.hidden = pages < 2;
      status.hidden = pages < 2 && label === 'Personnalités';
      function pageLink(index,text,accessible) {
        const link = document.createElement('a');
        link.href = pageURL(index);
        link.textContent = text;
        link.setAttribute('aria-label',accessible);
        if (index === number) link.setAttribute('aria-current','page');
        nav.append(link);
      }
      if (number > 1) pageLink(number - 1,'← Précédent','Page précédente');
      for (let index = 1; index <= pages; index += 1) pageLink(index,String(index),`Page ${index}`);
      if (number < pages) pageLink(number + 1,'Suivant →','Page suivante');
      refreshReturns();
      if (focus) { status.focus({preventScroll:true}); status.scrollIntoView({block:'start'}); }
    }
    nav.addEventListener('click',event => {
      const link = event.target.closest('a');
      if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      history.pushState(null,'',link.href);
      render(true);
    });
    addEventListener('popstate',() => render());
    desktop.addEventListener('change',() => render());
    render();
  });
})();
