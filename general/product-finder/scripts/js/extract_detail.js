// Reads one listing page. finder.py prepends `var CFG = {...};` (fields: sel = {name: selector}, max = chars).
(function (CFG) {
  function clean(s) { return (s || '').replace(/\s+/g, ' ').trim(); }
  var res = { page: location.href, title: document.title, status: 'ok', fields: {} };
  var probe = (document.title + ' ' + (document.body ? document.body.innerText.slice(0, 2000) : '')).toLowerCase();
  if (/just a moment|captcha|sicherheitscheck|are you a robot|access denied/.test(probe) && !document.querySelector('h1')) {
    res.status = 'blocked';
    return JSON.stringify(res);
  }
  var found = false;
  Object.keys(CFG.sel || {}).forEach(function (k) {
    var s = CFG.sel[k], attr = null;
    if (s.indexOf('src:') === 0) { attr = 'src'; s = s.slice(4); }  // e.g. eBay description iframe URL
    var e = document.querySelector(s);
    if (e) { res.fields[k] = attr ? e.getAttribute(attr) : clean(e.innerText).slice(0, CFG.max || 1500); found = true; }
  });
  if (!found) {
    var h = document.querySelector('h1');
    res.fields.title = h ? clean(h.innerText) : document.title;
    var main = document.querySelector('main') || document.body;
    res.fields.text = clean(main.innerText).slice(0, CFG.max || 2500);
  }
  return JSON.stringify(res);
})(CFG);
