// Renders the page in WebKit, clicks the busiest box and prints what happened. macOS only.
// Build: swiftc -O -o /tmp/render_check render_check.swift -framework Cocoa -framework WebKit
// Run:   /tmp/render_check /abs/path/domain-model.html /tmp/page.png
import Cocoa
import WebKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("usage: render_check <page.html> <out.png>")
    exit(2)
}
let page = args[1], output = args[2]

let check = #"""
(function () {
  const errors = [];
  window.addEventListener('error', (e) => errors.push(e.message));
  const tops = () => [...document.querySelectorAll('svg#canvas g.box')].filter((g) => !g.parentNode.closest('g.box'));
  const rects = tops().map((g) => {
    const m = /translate\(([-\d.]+)[ ,]+([-\d.]+)\)/.exec(g.getAttribute('transform'));
    const b = g.getBBox();
    return { id: g.dataset.id, x: +m[1], y: +m[2], w: b.width, h: b.height };
  });
  const overlaps = [];
  rects.forEach((a, i) => rects.slice(i + 1).forEach((b) => {
    if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) overlaps.push(a.id + '/' + b.id);
  }));
  const model = JSON.parse(document.getElementById('model').textContent);
  const degree = {};
  model.relations.forEach((r) => { degree[r.from] = (degree[r.from] || 0) + 1; degree[r.to] = (degree[r.to] || 0) + 1; });
  const busiest = rects.map((r) => r.id).sort((a, b) => (degree[b] || 0) - (degree[a] || 0))[0];
  let click = null;
  if (busiest) {
    tops().find((g) => g.dataset.id === busiest).dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
    click = {
      box: busiest,
      faded: tops().filter((g) => g.classList.contains('faded')).length,
      litLabels: document.querySelectorAll('svg#canvas text.rel.on').length,
      inspector: document.querySelector('#panel input') ? document.querySelector('#panel input').value : null,
    };
  }
  document.getElementById('showAll').click();
  document.getElementById('showAll').click();
  document.getElementById('view3d').click();
  const view3d = !document.getElementById('sheet3d').hidden;
  document.getElementById('view3d').click();
  for (let i = 0; i < 8; i++) document.getElementById('zoomOut').click();
  return JSON.stringify({ boxes: rects.length, overlaps, click, view3d, overview: document.querySelectorAll('.ov-card').length, errors });
})()
"""#

final class Loader: NSObject, WKNavigationDelegate {
    func webView(_ view: WKWebView, didFinish navigation: WKNavigation!) {
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            view.evaluateJavaScript(check) { result, error in
                print(result ?? "nil")
                if let error = error { print("JS ERROR:", error) }
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.8) {
                    view.takeSnapshot(with: WKSnapshotConfiguration()) { image, _ in
                        let bitmap = NSBitmapImageRep(data: image!.tiffRepresentation!)!
                        try! bitmap.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: output))
                        exit(error == nil ? 0 : 1)
                    }
                }
            }
        }
    }
}

let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
let view = WKWebView(frame: NSRect(x: 0, y: 0, width: 1700, height: 1200))
let window = NSWindow(contentRect: view.frame, styleMask: [.borderless], backing: .buffered, defer: false)
window.contentView = view
let loader = Loader()
view.navigationDelegate = loader
let url = URL(fileURLWithPath: page)
view.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
DispatchQueue.main.asyncAfter(deadline: .now() + 30) {
    print("timeout")
    exit(1)
}
app.run()
