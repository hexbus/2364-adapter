# Rebuilding

Open `hardware/rev-a/68764-to-28pin.kicad_pro` with KiCad 10. Local symbol
and footprint libraries are beside the project. The historical `68764-to-28pin`
filenames are retained so the imported project and routing session stay intact.

On Windows, run from the repository root:

```powershell
./hardware/rebuild.ps1
python tools/verify_fabrication.py
python tools/render_fabrication.py
```

The rebuild uses KiCad's Python (`pcbnew`) and CLI. The fabrication verifier
and renderer use Python with the versions in `tools/requirements.txt`.
The verifier checks the exports, the exact ZIP and the preserved missing-mask
regression fixture. The renderer reads the ZIP, not a source-board preview.
Inspect the rendered top, bottom and individual layers before any delivery.

`rebuild.ps1` checks ERC/DRC and the independent pin audit, exports the existing
routed PCB, checks the mask Gerbers and packages the manufacturing files.
`tools/package_fabrication.py` includes LICENSE and NOTICE in the ZIP and
checks every archived file against its input and SHA-256 manifest.
No paste layers, stencil files or assembly service package are supplied.

The files under `reports/` describe the published credit edition. Update them
after intentional design changes. The baseline geometry hashes protect the
unchanged copper, drill, mask and outline geometry; a new electrical design
needs a new revision and review, not an updated baseline to silence a failure.

## Placement generator

`hardware/build_adapter.py` is the preserved source generator, with the
designer credit added. **Running it replaces the routed board with an
unrouted placement.** Use a disposable copy for experiments. Its `import`
argument imports `hardware/rev-a/68764-to-28pin.ses` and enforces 0.25 mm
minimum track width. The historical generator and router session are not a
substitute for the final native PCB and full export inspection.

The final native PCB is authoritative. Do not use a regenerated board for
fabrication until its placement, silkscreen, all manufacturing layers and
independent pin map have been checked again.
