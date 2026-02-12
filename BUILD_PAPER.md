Building the Paper (LaTeX)
=========================

This repository includes an IEEE-style LaTeX paper in the `paper/` folder and a Windows build helper `build.ps1` to compile it.

Prerequisites
-------------
- A TeX distribution with `pdflatex` available on PATH. On Windows install MiKTeX: https://miktex.org/download

Quick build (PowerShell)
------------------------

Run from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

What the script does
--------------------
- Checks that `pdflatex` is installed and prints an instruction to install MiKTeX if not found.
- Compiles `paper/ieee_paper_main.tex` (falls back to `paper/ieee_paper.tex` if the main file is missing).
- Runs `pdflatex` twice and writes output to `paper/build.log`.
- On failure the script prints the last 40 lines of the log to help debug.
- On success the generated PDF is opened automatically.

Troubleshooting
---------------
- If `pdflatex` is not found, install MiKTeX and ensure the installation added the binaries to your PATH. After installing, reopen PowerShell and re-run the build command.
- If compilation fails, inspect `paper/build.log` for missing packages or LaTeX errors. Use the MiKTeX Package Manager to install any missing packages reported in the log.
- For CI or non-Windows environments, install TeX Live or a platform-appropriate TeX toolchain and run the equivalent `pdflatex` commands manually.

Notes
-----
- The master tex file is `paper/ieee_paper_main.tex`. If you prefer to edit a single source file, `paper/ieee_paper.tex` contains the current paper content.
- If you want, request layout or table placement tweaks and I will update the LaTeX source before you compile locally.

Automated install & build (auto_build.ps1)
----------------------------------------

A fully automated helper `auto_build.ps1` is provided at the repository root. It attempts to make the build zero-interaction by:

- Checking whether `pdflatex` is on PATH.
- If missing, attempting to install MiKTeX via `winget`, `choco`, or by downloading the basic installer and running it with unattended flags.
- Adding the discovered MiKTeX bin folder to the user PATH and refreshing the current session environment.
- Verifying `pdflatex --version` works.
- Compiling `paper/ieee_paper_main.tex` (falls back to `paper/ieee_paper.tex`) twice with:

	```powershell
	pdflatex -interaction=nonstopmode -output-directory paper paper\ieee_paper_main.tex
	```

- Saving output to `paper/build.log` and printing the last 50 lines if the build fails.
- Opening the generated PDF on success.

Usage (run from project root):

```powershell
powershell -ExecutionPolicy Bypass -File auto_build.ps1
```

Notes & permissions
-------------------
- The script attempts a user install when possible, but some systems require administrator privileges to install MiKTeX system-wide. If an installer requires elevation the script will attempt to run it and may prompt for elevation or fail; in that case please run the command from an elevated PowerShell prompt.
- If you prefer not to allow automatic installer actions, run the original `build.ps1` after installing MiKTeX/TeX Live manually.

CI Build (GitHub Actions)
-------------------------

If you prefer not to install MiKTeX locally, the repository includes a GitHub Actions workflow that builds the paper on `ubuntu-latest` and uploads the generated PDF as an artifact. The workflow file is at `.github/workflows/build-paper.yml` and can be triggered manually from the Actions tab or runs automatically on pushes to `main`/`master`.

Note: the CI workflow now installs the full `texlive-full` distribution on the runner to avoid missing LaTeX package errors during compilation.

To trigger the CI build manually:

1. Open the repository on GitHub.
2. Go to the `Actions` tab → `Build Paper (LaTeX)` → `Run workflow`.

The compiled PDF and `paper/build.log` will be available as workflow artifacts after the job completes.

