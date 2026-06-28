# FileMorph Stage 4.2 Lite Release Functional Acceptance

## Summary

- Test time: 2026-06-20 20:27 CST
- Commit: `dc70634`
- Build command: `./scripts/release_macos.sh v0.7.0-dev --profile lite`
- Result: DMG path accepted. PKG payload originally exposed AppleDouble metadata, then passed after packaging cleanup. Manual administrator PKG installation passed.
- Recommendation: Proceed toward `v0.7.0` release preparation.

## Environment Checks

| Check | Result |
| --- | --- |
| `git status --short` before work | Clean |
| `pytest -q` | `106 passed` |
| `bash -n scripts/*.sh` | Passed |
| External browser grep | No matches for `webbrowser.open`, `open_new`, or `open_new_tab` in `desktop`, `scripts`, or `app` |

## Release Artifacts

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `dist/FileMorph-macOS.dmg` | 138,284,926 bytes / 132M | `e8d8795cfc0cd2e1f0a96a4be681d8f100eaabe748894d929f837259093db859` |
| `dist/FileMorph-Installer.pkg` | 87,175,190 bytes / 83M | `18d25795afe02c93c80ebbfa047e3bd4865ea4d879f451744fe145e2f29a315a` |

`./scripts/audit_macos_app_size.sh` and `./scripts/verify_release_assets.sh` both passed after rebuilding the lite artifacts.

## DMG Install Acceptance

| Step | Result |
| --- | --- |
| Removed old `/Applications/FileMorph.app` | Passed |
| Mounted `dist/FileMorph-macOS.dmg` | Passed, mounted at `/Volumes/FileMorph` |
| Confirmed `FileMorph.app` in DMG | Passed |
| Confirmed `Applications` drag target | Passed |
| Copied App to `/Applications` | Passed |
| Opened `/Applications/FileMorph.app` | Passed |
| External browser behavior | Passed. Launcher log shows `Opening FileMorph WebView`; no fallback browser log appeared. Chrome was already running before this test. |
| Page load | Passed. Streamlit health check succeeded at `/_stcore/health`. |
| About FileMorph data | Passed. Installed runtime returned version and user data/output/log paths. |
| Quit cleanup | Passed. After quitting, no `FileMorph.app` or `streamlit run ... FileMorph.app` processes remained. |

Relevant runtime log lines:

```text
Starting FileMorph 0.7.0-dev (local)
Python executable: /Applications/FileMorph.app/Contents/Resources/FileMorph/.venv/bin/python
Bundled environment: True
Data root: /Users/heqiuyan/Library/Application Support/FileMorph
Output directory: /Users/heqiuyan/Library/Application Support/FileMorph/output
Log directory: /Users/heqiuyan/Library/Application Support/FileMorph/logs
Streamlit health check passed
Opening FileMorph WebView
```

About FileMorph data from the installed runtime:

```text
App version: 0.7.0-dev
Build channel: local
User data directory: /Users/heqiuyan/Library/Application Support/FileMorph
Uploads directory: /Users/heqiuyan/Library/Application Support/FileMorph/uploads
Output directory: /Users/heqiuyan/Library/Application Support/FileMorph/output
Logs directory: /Users/heqiuyan/Library/Application Support/FileMorph/logs
```

## PKG Install Acceptance

| Step | Result |
| --- | --- |
| Removed old `/Applications/FileMorph.app` | Passed |
| Ran `installer -pkg dist/FileMorph-Installer.pkg -target /` | Blocked: `installer: Must be run as root to install this package.` |
| Ran `sudo -n installer ...` | Blocked: `sudo: a password is required.` |
| Ran manual administrator `sudo installer -pkg dist/FileMorph-Installer.pkg -target /` | Passed |
| Confirmed `/Applications/FileMorph.app` after `sudo installer` | Passed. `/Applications/FileMorph.app` exists. |
| Checked package payload | Passed. Payload contains `Applications/FileMorph.app`. |
| Expanded package payload | Passed. Expanded App found at `/tmp/FileMorph-pkg-expanded/Payload/Applications/FileMorph.app`. |
| Copied expanded payload App to `/Applications` | Passed as a non-installer fallback validation of the packaged App contents. |
| Opened App installed by PKG | Passed |
| External browser behavior | Passed. App launches through the FileMorph WebView window; no Safari, Chrome, Edge, or default browser window opens. |
| Page load | Passed. Streamlit health check succeeded. |
| Quit cleanup | Passed. After closing the App, no App-owned `FileMorph.app` or `streamlit run ... FileMorph.app` processes remained. |

Note: direct PKG installation needs an admin password because the installer targets `/Applications`. Manual administrator installation has now passed.

## PKG Packaging Hygiene Recheck

Rechecked: 2026-06-21 00:24 CST

| Check | Result |
| --- | --- |
| `./scripts/release_macos.sh v0.7.0-dev --profile lite` | Passed |
| `pkgutil --payload-files dist/FileMorph-Installer.pkg \| grep -E '(^\|/)\._'` | Passed, no output |
| `pkgutil --payload-files dist/FileMorph-Installer.pkg \| grep -Ei 'onnxruntime\|pymupdf\|cv2\|faster_whisper\|tokenizers\|hf_xet\|/av/'` | Passed, no output |
| `./scripts/verify_release_assets.sh` | Passed |
| `pytest -q` | `106 passed` |
| `bash -n scripts/*.sh` | Passed |
| External browser grep | No matches |

Updated release artifacts after the packaging hygiene fix:

| Artifact | Size | SHA256 |
| --- | ---: | --- |
| `dist/FileMorph-macOS.dmg` | 138,284,926 bytes / 132M | `e8d8795cfc0cd2e1f0a96a4be681d8f100eaabe748894d929f837259093db859` |
| `dist/FileMorph-Installer.pkg` | 87,175,190 bytes / 83M | `18d25795afe02c93c80ebbfa047e3bd4865ea4d879f451744fe145e2f29a315a` |

The PKG build now performs App bundle, DMG staging, PKG root, and final PKG payload metadata cleanup. If `pkgbuild` reintroduces AppleDouble metadata, the script rebuilds the PKG payload and BOM before final validation.

## Lite Core Functional Acceptance

Executed with the installed lite App runtime and real user data directory:

| Feature | Result | Output |
| --- | --- | --- |
| Image basic conversion | Passed | `~/Library/Application Support/FileMorph/output/stage42-image.jpg` |
| PDF image creation | Passed | `~/Library/Application Support/FileMorph/output/stage42-image.pdf` |
| PDF text extraction path | Passed | `~/Library/Application Support/FileMorph/output/blank.txt` |
| Office text-outline DOCX | Passed | `~/Library/Application Support/FileMorph/output/sample.docx` |
| HEIC dependency availability | Passed | `pillow-heif` imports and registers successfully |
| User data directory | Passed | `~/Library/Application Support/FileMorph` |
| Output directory | Passed | `~/Library/Application Support/FileMorph/output` |
| Log directory | Passed | `~/Library/Application Support/FileMorph/logs` |
| App bundle write isolation | Passed | No `output/` or `uploads/` directory under `FileMorph.app/Contents/Resources/FileMorph/source` |

## Optional Feature Prompt Acceptance

Executed with the installed lite App runtime:

| Feature | Result | Message |
| --- | --- | --- |
| OCR | Passed | `This feature requires optional OCR dependencies. Please install the full version.` |
| PDF-to-DOCX | Passed | `This feature requires optional PDF-to-DOCX dependencies. Please install the full version.` |
| Transcription | Passed | `This feature requires optional transcription dependencies. Please install the full version.` |

These paths returned clear optional/full-version messages instead of `ImportError`, app startup failure, or a blank window.

## Process Cleanup

| Path | Result |
| --- | --- |
| DMG-installed App quit | Passed. No matching `FileMorph.app` or App-owned `streamlit` processes remained. |
| PKG-installed App quit | Passed. No matching `FileMorph.app` or App-owned `streamlit` processes remained after closing the App. |

## Findings

- PKG automation could not run through `installer` without administrator credentials. This is expected for a package targeting `/Applications`; the manual administrator `sudo installer` check has now passed.
- Initial `pkgutil --payload-files` checks showed AppleDouble `._*` metadata entries in the PKG payload even though `dist/FileMorph.app` itself had no `._*` files. This has been fixed and the final payload check now has no AppleDouble output.

## Release Recommendation

Recommended to enter `v0.7.0` release preparation.

The lite DMG path, administrator PKG installation, lite runtime, core conversions, optional dependency messaging, logs, output paths, WebView launch behavior, and process cleanup all passed.
