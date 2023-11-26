/*
 * ocr.swift
 * usage: swift scripts/macos/ocr.swift IMAGE_FILEPATH
 */

import Cocoa
import Vision
import Foundation

func main(files: [String]) {
    print(files)
    let lang: [String] = ["en"]

    let request = VNRecognizeTextRequest { (request, error) in
        let observations = request.results as? [VNRecognizedTextObservation] ?? []
        let obs : [String] = observations.map { $0.topCandidates(1).first?.string ?? "" }
        print(obs.joined(separator: "\n"))
    }

    request.recognitionLevel = VNRequestTextRecognitionLevel.accurate
    request.usesLanguageCorrection = true
    request.revision = VNRecognizeTextRequestRevision2
    request.recognitionLanguages = lang

    for url in files.map({ URL(fileURLWithPath: $0) }) {
        print(url)
        guard let imgRef = NSImage(byReferencing: url).cgImage(forProposedRect: nil, context: nil, hints: nil) else {
            fatalError("Error: could not convert NSImage to CGImage - '\(url)'")
        }
        try? VNImageRequestHandler(cgImage: imgRef, options: [:]).perform([request])
    }
}


if CommandLine.argc < 2 {
    print("no images passed")
    exit(1)
} else {
    main(files: Array(CommandLine.arguments[1...]))
    exit(0)
}
