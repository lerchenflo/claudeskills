// OCR page images with the macOS Vision framework (German + English).
// Usage: swift ocr.swift img1.png img2.png ...  -> prints "## <file>" and recognized lines (top to bottom).
import Foundation
import Vision
import AppKit

for path in CommandLine.arguments.dropFirst() {
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("## \(path)\n[could not load]"); continue
    }
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["de-DE", "en-US"]
    request.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([request])
    let obs = (request.results ?? []).sorted {
        // two-column layouts: sort by column (left half first), then top to bottom
        let ca = $0.boundingBox.midX < 0.5 ? 0 : 1, cb = $1.boundingBox.midX < 0.5 ? 0 : 1
        return ca != cb ? ca < cb : $0.boundingBox.maxY > $1.boundingBox.maxY
    }
    print("## \((path as NSString).lastPathComponent)")
    for o in obs { if let t = o.topCandidates(1).first { print(t.string) } }
    print("")
}
