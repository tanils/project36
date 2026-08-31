import subprocess, sys, pathlib

root=pathlib.Path(__file__).resolve().parent
main=root/"src"/"news_agent"/"main.py"

if not main.exists():
    candidates=list(root.rglob("main.py"))
    candidates=[p for p in candidates if "news_agent" in str(p).lower()]
    if not candidates:
        print("Could not locate src/news_agent/main.py")
        sys.exit(1)
    main=candidates[0]

cmd=[sys.executable, "-m", ".".join(main.relative_to(root).with_suffix("").parts), "--slot", "morning", "--dry-run"]
print("Running:", " ".join(cmd))
sys.exit(subprocess.call(cmd, cwd=root))
