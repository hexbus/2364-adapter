# PCB fabrication verification

Jon requires thorough verification before delivering PCB fabrication files.
This follows the 68764 adapter solder-mask omission identified by JLCPCB
on 21 October 2026.

- Clean ERC/DRC is not proof of fabrication readiness.
- Verify pins, orientation, voltages and footprint dimensions against component
  documentation. Label unresolved assumptions.
- Inspect exported copper, outline, drills (position, size and plating), masks
  on every solderable pad, and silkscreen clearance/readability in the exact ZIP.
  Check paste when delivering stencil/assembly files.
- Render and visually inspect fabrication layers, not only source previews.
  Compare intended pad/opening geometry with exported mask/drill geometry.
- Ensure ZIPs match the checked design/exports; preserve superseded evidence
  separately and clearly label corrected deliveries.
- For corrections, check intended changes and unchanged electrical geometry.
  Add a regression check where practical and show it rejects the defect.
- Report verified scope and pending hardware evidence. Never infer physical
  fit, solderability, timing or operation from CAD checks alone.

This is a standalone repository. Do not modify the original CC-40 workspace
as a side effect of builds here. Preserve Jon Guidry / hexbus attribution
and the LICENSE terms on derivatives and physical reproductions.
