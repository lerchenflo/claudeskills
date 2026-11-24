// Reads a search-result page. finder.py prepends `var CFG = {...};`.
// CFG: mode ('willhaben' | 'cards' | 'links'), card (selector), link (selector), closest (selector), hrefAttr
(function (CFG) {
  function clean(s) { return (s || '').replace(/\s+/g, ' ').trim(); }
  var body = document.body ? document.body.innerText : '';
  var res = { page: location.href, title: document.title, status: 'ok', items: [] };

  var probe = (document.title + ' ' + body.slice(0, 2500)).toLowerCase();
  var hasResults = CFG.link && document.querySelector(CFG.link);
  if (!hasResults && /just a moment|captcha|sicherheitscheck|are you a robot|access denied|zugriff verweigert|unusual traffic|bot detection/.test(probe)) {
    res.status = 'blocked';
    res.text = clean(body).slice(0, 300);
    return JSON.stringify(res);
  }

  if (CFG.mode === 'willhaben') {
    var n = document.getElementById('__NEXT_DATA__');
    if (n) {
      try {
        var sr = JSON.parse(n.textContent).props.pageProps.searchResult;
        res.total = sr.rowsFound;
        (sr.advertSummaryList.advertSummary || []).forEach(function (a) {
          var m = {};
          (a.attributes.attribute || []).forEach(function (x) { m[x.name] = x.values[0]; });
          res.items.push({
            title: a.description,
            price: m.PRICE_FOR_DISPLAY || m.PRICE || '',
            location: [m.POSTCODE, m.LOCATION].filter(Boolean).join(' '),
            url: m.SEO_URL ? 'https://www.willhaben.at/iad/' + m.SEO_URL : '',
            text: clean(m.BODY_DYN || '').slice(0, 220)
          });
        });
        if (!res.items.length) res.status = 'empty';
        return JSON.stringify(res);
      } catch (e) { res.note = 'willhaben json failed: ' + e; }
    }
  }

  var seen = {};
  function add(href, text) {
    if (!href) return;
    href = href.split('#')[0];
    if (seen[href]) return;
    seen[href] = 1;
    res.items.push({ url: href, text: clean(text).replace(/Wird in neuem Fenster oder Tab geöffnet|Opens in a new window or tab/g, ' ').slice(0, 1500) });
  }

  if (CFG.card) {
    document.querySelectorAll(CFG.card).forEach(function (c) {
      var href = CFG.hrefAttr ? c.getAttribute(CFG.hrefAttr) : '';
      if (href && href.charAt(0) === '/') href = location.origin + href;
      if (!href) { var a = c.querySelector(CFG.link || 'a[href]'); href = a ? a.href : ''; }
      add(href, c.innerText);
    });
  }
  if (!res.items.length && CFG.link) {
    document.querySelectorAll(CFG.link).forEach(function (a) {
      var c = CFG.closest ? (a.closest(CFG.closest) || a) : a;
      add(a.href, c.innerText);
    });
  }
  if (!res.items.length) {
    res.status = 'empty';
    res.text = clean(body).slice(0, 1200);
  }
  return JSON.stringify(res);
})(CFG);
