import argparse
import sys
import time
import os
from pytailwind import Tailwind


def main():
    parser = argparse.ArgumentParser(description="Generate Tailwind CSS from HTML files.")
    parser.add_argument("input", help="Input HTML file or directory")
    parser.add_argument("-o", "--output", help="Output CSS file", default="output.css")
    parser.add_argument("-w", "--watch", action="store_true", help="Watch for changes")
    parser.add_argument("-m", "--minify", action="store_true", help="Minify output CSS")
    parser.add_argument("-c", "--config", help="Path to config file (Python dictionary)")

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", args.config)
        config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config_module)
        if hasattr(config_module, "config"):
            config = config_module.config
        else:
            print(f"Warning: Config file {args.config} does not define a 'config' variable.")

    tailwind = Tailwind(config)

    def generate_css():
        content = ""
        if os.path.isdir(args.input):
            for root, dirs, files in os.walk(args.input):
                for file in files:
                    if file.endswith(".html"):
                        with open(os.path.join(root, file), "r") as f:
                            content += f.read()
        else:
            with open(args.input, "r") as f:
                content = f.read()

        css = tailwind.generate(content, minify=args.minify)

        with open(args.output, "w") as f:
            f.write(css)
        print(f"Generated CSS to {args.output}")

    generate_css()

    if args.watch:
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("watchdog module not found. Please install it with `pip install watchdog`")
            sys.exit(1)

        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if not event.is_directory and event.src_path.endswith(".html"):
                    print(f"File {event.src_path} modified. Regenerating...")
                    generate_css()

        observer = Observer()
        path = args.input if os.path.isdir(args.input) else os.path.dirname(args.input) or "."
        observer.schedule(Handler(), path, recursive=True)
        observer.start()
        print(f"Watching for changes in {path}...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
