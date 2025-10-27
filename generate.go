package main

// Use pipeline.py for automated generation:
//   python3 pipeline.py api-2-2-2.json
//
//go:generate go run github.com/ogen-go/ogen/cmd/ogen@latest --config .ogen.yml --target api --package api --clean api-2-2-2-final.json
