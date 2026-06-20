# FileMorph Stage 4.1 App Size Audit

Generated: 2026-06-20 20:22:52 CST

Current profile: lite

## Baseline Before Stage 4

| Artifact | Size |
| --- | ---: |
| dist/FileMorph.app | 701M |
| dist/FileMorph.app/Contents/Resources/FileMorph | 701M |
| dist/FileMorph.app/Contents/Resources/FileMorph/source | 1.2M |
| dist/FileMorph.app/Contents/Resources/FileMorph/.venv | 699M |
| dist/FileMorph-macOS.dmg | 295M |
| dist/FileMorph-Installer.pkg | 216M |

## Stage 4 Full Runtime Baseline

| Artifact | Size |
| --- | ---: |
| dist/FileMorph.app | 610M |
| dist/FileMorph.app/Contents/Resources/FileMorph/.venv | 610M |
| dist/FileMorph-macOS.dmg | 261M |
| dist/FileMorph-Installer.pkg | 195M |

## Current Build

| Artifact | Size | Bytes |
| --- | ---: | ---: |
| dist/FileMorph.app | 301M | 316067840 |
| dist/FileMorph.app/Contents/Resources/FileMorph | 301M | 315813888 |
| dist/FileMorph.app/Contents/Resources/FileMorph/source | 160K | 163840 |
| dist/FileMorph.app/Contents/Resources/FileMorph/.venv | 301M | 315645952 |
| dist/FileMorph-macOS.dmg | 130M | 135880704 |
| dist/FileMorph-Installer.pkg | 84M | 88449024 |

## Largest Files And Directories

```text
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents
301M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app
117M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow
 44M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow.2400.dylib
 25M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pandas
 24M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit
 19M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit/static/static
 19M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit/static
 19M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_flight.2400.dylib
 19M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/lxml
 16M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pandas/_libs
 15M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit/static/static/js
 15M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_compute.2400.dylib
 14M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/numpy
```

## Largest Files

```text
 44M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow.2400.dylib
 19M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_flight.2400.dylib
 15M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_compute.2400.dylib
9.0M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/lxml/etree.cpython-311-darwin.so
8.6M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pillow_heif/.dylibs/libx265.216.dylib
4.9M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/lxml/objectify.cpython-311-darwin.so
4.6M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libparquet.2400.dylib
4.6M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_substrait.2400.dylib
4.4M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit/static/static/js/PlotlyChart.DE72Bh5O.js
4.0M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pydeck/nbextension/static/index.js
3.5M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/lib.cpython-311-darwin.so
3.5M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-darwin.so
2.9M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/PIL/.dylibs/libavif.16.4.1.dylib
2.6M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit/static/static/js/DeckGlJsonChart.CTNT18ux.js
2.6M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_dataset.2400.dylib
2.3M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/streamlit/static/static/js/index.dkY5s53S.js
2.1M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_acero.2400.dylib
2.0M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pillow_heif/.dylibs/libheif.1.23.0.dylib
1.9M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_python.dylib
1.9M	/Users/heqiuyan/Desktop/ConvertKit/dist/FileMorph.app/Contents/Resources/FileMorph/.venv/lib/python3.11/site-packages/pyarrow/libarrow_python.2400.dylib
```

## Notes

- Stage 4.1 optimizes only the packaged app contents under dist/FileMorph.app.
- Repository source folders such as tests/, docs/, and audits/ are not deleted.
- dist/, .venv/, uploads/, output/, logs/, .dmg, and .pkg artifacts remain untracked release/build outputs.
