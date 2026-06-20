# FileMorph Stage 4.2 Lite Release Functional Acceptance

## Summary

- Test time: 2026-06-20 20:27 CST
- Commit: `dc70634`
- Build command: `./scripts/release_macos.sh v0.7.0-dev --profile lite`
- Result: DMG path accepted. PKG payload accepted; direct `installer` automation was blocked by macOS administrator permission requirements.
- Recommendation: Proceed toward `v0.7.0` release after one manual PKG installer click-through check on an admin account.

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
| `dist/FileMorph-macOS.dmg` | 135,877,018 bytes / 130M | `b195e856c4ea0be57bd76e68559e8df0631ad1203acf0472f54d7a79a73a0acf` |
| `dist/FileMorph-Installer.pkg` | 88,448,535 bytes / 84M | `efd754580e849211679ff5d6afc824eba53093987efde35f2bebf1a444a2e1d8` |

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
| Checked package payload | Passed. Payload contains `Applications/FileMorph.app`. |
| Expanded package payload | Passed. Expanded App found at `/tmp/FileMorph-pkg-expanded/Payload/Applications/FileMorph.app`. |
| Copied expanded payload App to `/Applications` | Passed as a non-installer fallback validation of the packaged App contents. |
| Opened App from PKG payload | Passed |
| External browser behavior | Passed. Launcher log shows WebView startup and no fallback browser. |
| Page load | Passed. Streamlit health check succeeded. |
| Quit cleanup | Passed. After quitting, no `FileMorph.app` or `streamlit run ... FileMorph.app` processes remained. |

Note: direct PKG installation needs an admin password in this environment. A final manual double-click installer check is recommended before publishing `v0.7.0`.

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
| PKG payload App quit | Passed. No matching `FileMorph.app` or App-owned `streamlit` processes remained. |

## Findings

- PKG automation could not run through `installer` without administrator credentials. This is expected for a package targeting `/Applications`, but a manual admin-user installer check remains before public release.
- `pkgutil --payload-files` showed AppleDouble `._*` metadata entries in the PKG payload even though `dist/FileMorph.app` itself had no `._*` files. This did not affect functional launch, but it is a packaging hygiene item to revisit.

## Release Recommendation

Recommended to enter `v0.7.0` release preparation after:

1. Manual PKG install click-through with an admin password.
2. Optional cleanup of AppleDouble metadata in the PKG payload if desired.

The lite DMG path, lite runtime, core conversions, optional dependency messaging, logs, output paths, and process cleanup all passed.
