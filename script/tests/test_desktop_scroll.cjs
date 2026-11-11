/* Retour de fiche après pagination réelle JS : les positions suivent l'URL courante. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

function fixture({page='',desktop=true,storage=new Map()}={}) {
  const elements = [], events = {}, documentEvents = {}, restored = [];
  function element(tag='a') {
    const node = {tag,children:[],attributes:{},events:{},hidden:false,
      setAttribute(key,value) { this.attributes[key]=value; },
      append(...children) { this.children.push(...children); },
      replaceChildren(...children) { this.children=[...children]; },
      before() {}, after() {},
      addEventListener(type,callback) { this.events[type]=callback; },
      closest(selector) { return selector==='a' && this.tag==='a' ? this : null; },
      focus() {}, scrollIntoView() {}};
    elements.push(node); return node;
  }
  const cards = Array.from({length:25},()=>element());
  const grid = element('section'); grid.children=cards; grid.dataset={pageLabel:'Personnalités'};
  const profile = element(); profile.href='https://wiki.test/createurs/exemple?retour=%2Fcreateurs-reunionnais';
  let address = new URL('https://wiki.test/createurs-reunionnais?q=creation'+(page ? '&page='+page : ''));
  const location = {};
  for (const key of ['href','pathname','search','origin']) Object.defineProperty(location,key,{get:()=>address[key]});
  const history = {
    pushState(_state,_unused,url) { address=new URL(url,address); },
    replaceState(_state,_unused,url) { address=new URL(url,address); }};
  const document = {body:{classList:{contains:()=>true},dataset:{finalPage:'personnalites'}},
    createElement:element,
    querySelectorAll(selector) {
      if (selector==='[data-desktop-pagination]') return [grid];
      if (selector==='a[href]') return elements.filter(node=>node.tag==='a' && node.href);
      return [];
    },
    querySelector() { return null; }, getElementById() { return null; },
    addEventListener(type,callback) { documentEvents[type]=callback; }};
  const context = vm.createContext({document,location,history,URL,
    matchMedia:()=>({matches:desktop,addEventListener(){}}),
    addEventListener:(type,callback)=>{events[type]=callback;},
    sessionStorage:{getItem:key=>storage.get(key),setItem:(key,value)=>storage.set(key,value)},
    requestAnimationFrame:callback=>callback(),scrollTo:(x,y)=>restored.push([x,y]),scrollY:0});
  for (const filename of ['desktop.js','public.js']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname,'../../static/refonte',filename),'utf8'),context);
  }
  return {storage,restored,profile,location,
    remember(y) { context.scrollY=y; documentEvents.click({target:profile}); },
    leave(y) { context.scrollY=y; events.pagehide(); },
    goPage(number) {
      const nav=elements.find(node=>node.tag==='nav');
      const anchor=nav.children.find(node=>node.textContent===String(number));
      assert.ok(anchor);
      nav.events.click({target:anchor,button:0,preventDefault(){}});
      documentEvents.click({target:anchor});
    },
    backTo(url) { address=new URL(url,address); events.popstate(); }};
}

test('page 1 → page 2 → fiche conserve deux positions distinctes et le retour page 2',()=>{
  const f=fixture();
  f.remember(300); f.goPage(2); f.remember(900);
  assert.equal(f.storage.get('rw-public-position:/createurs-reunionnais?q=creation'),'300');
  assert.equal(f.storage.get('rw-public-position:/createurs-reunionnais?q=creation&page=2'),'900');
  assert.equal(new URL(f.profile.href,f.location.href).searchParams.get('retour'),'/createurs-reunionnais?q=creation&page=2');
  const returned=fixture({page:'2',storage:f.storage});
  assert.deepEqual(returned.restored,[[0,900]]);
});

test('retour historique puis sortie mémorise la page courante sans écraser page 2',()=>{
  const f=fixture(); f.goPage(2); f.remember(900);
  f.backTo('/createurs-reunionnais?q=creation'); f.leave(220);
  assert.equal(f.storage.get('rw-public-position:/createurs-reunionnais?q=creation'),'220');
  assert.equal(f.storage.get('rw-public-position:/createurs-reunionnais?q=creation&page=2'),'900');
});

test('mobile sans pagination conserve le retour et la restauration existants',()=>{
  const f=fixture({desktop:false}); f.remember(430);
  const returned=fixture({desktop:false,storage:f.storage});
  assert.deepEqual(returned.restored,[[0,430]]);
  assert.equal(f.storage.size,1);
});
