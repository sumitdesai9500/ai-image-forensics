import argparse
from app.controllers.detection_controller import DetectionController
from app.views.cli_view import print_report


def main():
    parser = argparse.ArgumentParser(description="AI Image Forensics — Layers 1–3")
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("analyze", help="Analyze an image")
    a.add_argument("image", help="Path to image")
    args = parser.parse_args()
    if args.command == "analyze":
        evidence, assessment, stored_path = DetectionController().analyze(args.image)
        print_report(evidence, assessment, stored_path)


if __name__ == "__main__":
    main()
