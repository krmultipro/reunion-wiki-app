/* Tests de comportement en DOM minimal, sans navigateur ni données actives. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname,'../../static/refonte/desktop.js'),'utf8');

function fixture({count=25,page='',desktop=true,label='Sites',publicPage=true}={}) {
  const elements = [];
  function element(tag='a') {
    const node = {tag,children:[],attributes:{},events:{},hidden:false,
      setAttribute(key,value) { this.attributes[key]=value; },
      append(...children) { this.children.push(...children); },
      replaceChildren(...children) { this.children=[...children]; },
      before() {}, after() {},
      addEventListener(type,callback) { this.events[type]=callback; },
      closest(selector) { return selector === 'a' && this.tag === 'a' ? this : null; },
      focus() { this.focused=true; }, scrollIntoView() { this.scrolled=true; }};
    elements.push(node); return node;
  }
  const cards = Array.from({length:count},() => element());
  const grid = element('section'); grid.children=cards; grid.dataset={pageLabel:label};
  const profile = element(); profile.href='https://wiki.test/createurs/exemple?retour=%2Fsites%3Fq%3Dbus';
  let address = new URL('https://wiki.test/sites?q=bus&categorie=transport'+(page ? '&page='+page : ''));
  const location = {};
  for (const key of ['href','pathname','search','origin']) Object.defineProperty(location,key,{get:()=>address[key]});
  const history = {pushes:0,pushState(_state,_unused,url) { this.pushes++; address=new URL(url,address); },replaceState(_state,_unused,url) { address=new URL(url,address); }};
  const media = {matches:desktop,addEventListener(_type,callback) { this.changed=callback; }};
  const events = {};
  const document = {body:{classList:{contains:()=>publicPage}},createElement:element,
    querySelectorAll(selector) { return selector === '[data-desktop-pagination]' ? [grid] : elements.filter(node=>node.tag==='a' && node.href); }};
  vm.runInNewContext(source,{document,matchMedia:()=>media,location,history,URL,addEventListener:(type,callback)=>{events[type]=callback;}});
  const nav = elements.find(node=>node.tag==='nav');
  const status = elements.find(node=>node.tag==='p');
  return {cards,nav,status,location,history,profile,
    visible:()=>cards.filter(card=>!card.hidden),
    click(text) { const anchor=nav.children.find(node=>node.textContent===text); assert.ok(anchor,text); nav.events.click({target:anchor,button:0,preventDefault(){}}); },
    resize(value) { media.matches=value; media.changed(); },
    backTo(url) { address=new URL(url,address); events.popstate(); }};
}

test('12 résultats, pages et libellés accessibles sur PC',()=>{
  const f=fixture(); assert.equal(f.visible().length,12);
  assert.equal(f.status.textContent,'Page 1 sur 3 · Sites');
  assert.equal(f.nav.attributes['aria-label'],'Pages des sites');
  assert.equal(f.nav.children.find(a=>a.textContent==='1').attributes['aria-current'],'page');
});
test('page 2 conserve recherche, catégorie et retour de fiche',()=>{
  const f=fixture(); f.click('2');
  assert.equal(f.visible()[0],f.cards[12]); assert.equal(f.visible().length,12);
  const url=new URL(f.location.href); assert.equal(url.searchParams.get('q'),'bus');
  assert.equal(url.searchParams.get('categorie'),'transport'); assert.equal(url.searchParams.get('page'),'2');
  assert.equal(new URL(f.profile.href,'https://wiki.test').searchParams.get('retour'),f.location.pathname+f.location.search);
  assert.equal(f.history.pushes,1); assert.ok(f.status.focused && f.status.scrolled);
});
test('dernière page partielle et précédent sans perte de carte',()=>{
  const f=fixture(); f.click('3'); assert.deepEqual(f.visible(),[f.cards[24]]);
  assert.ok(!f.nav.children.some(a=>a.textContent==='Suivant →'));
  f.click('← Précédent'); assert.equal(f.visible()[0],f.cards[12]);
});
test('pages invalides bornées et URL canonique de première page',()=>{
  for (const page of ['erreur','-2','0','1.2']) {
    const f=fixture({page}); assert.equal(f.visible()[0],f.cards[0]);
    assert.equal(new URL(f.location.href).searchParams.get('page'),null);
  }
  const f=fixture({page:'999'}); assert.deepEqual(f.visible(),[f.cards[24]]);
  assert.equal(new URL(f.location.href).searchParams.get('page'),'3');
});
test('une seule page Personnalités ne montre pas de pagination ou compteur',()=>{
  for (const count of [3,12]) { const f=fixture({count,label:'Personnalités'}); assert.equal(f.visible().length,count); assert.ok(f.nav.hidden && f.status.hidden); }
});
test('mobile garde toutes les cartes et le changement de largeur est réversible',()=>{
  const f=fixture({desktop:false,page:'2'}); assert.equal(f.visible().length,25);
  assert.ok(f.nav.hidden); f.resize(true); assert.equal(f.visible()[0],f.cards[12]);
  f.resize(false); assert.equal(f.visible().length,25); assert.ok(f.nav.hidden && f.status.hidden);
});
test('historique navigateur restaure les cartes de la page demandée',()=>{
  const f=fixture(); f.click('2'); f.backTo('/sites?q=bus&categorie=transport');
  assert.equal(f.visible()[0],f.cards[0]); assert.equal(f.visible().length,12);
});
test('administration exclue de la pagination PC',()=>{
  const f=fixture({publicPage:false}); assert.equal(f.nav,undefined); assert.equal(f.visible().length,25);
});
