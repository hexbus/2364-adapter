# Verification and provenance

The design originated as the compact MCM68764 adapter in the CC-40 / Hexbus
research project. This standalone repository carries the corrected Revision A
and a bottom silkscreen designer credit added on 9 November 2026. The original
project and its superseded evidence were left unchanged.

## Evidence boundaries

- Design checks: pin/net correspondence; bottom connector numbering; 2.54 mm
  pitch; 15.24 mm row spacing; 23 × 37 mm outline; 0.80 mm component drills;
  address/data mapping and select logic; JP1 isolation; unused U1 pin 26.
- ERC and DRC include schematic parity and unconnected-item checks. The
  custom connector symbols use passive pins, so ERC cannot validate operating
  voltage, memory timing or the host's behavior.
- Export checks cover both copper layers, outline, plated component holes,
  solder-mask openings and silkscreen clearance. The exact ZIP is checked
  against the exports, with hashes in its manifest.
- Manufacturing layer previews are rendered from the exact ZIP for visual
  inspection. The bottom composite is mirrored for underside viewing.
- No stencil or assembly package is delivered, so paste is outside this release.

See the machine-readable [pin audit](../hardware/rev-a/independent-audit.json),
[ERC](../hardware/rev-a/erc.json), [DRC](../hardware/rev-a/drc.json),
[fabrication audit](../reports/fabrication-audit.json) and
[package report](../reports/package-report.json).

## Solder-mask correction

JLCPCB identified missing openings on the original October 19 connector pads.
The corrected October 21 version exposes **all 52 through-hole pads on both
sides**, plus the four C1/JP1 pads on top. The correction preserved copper,
drills and outline, and adjusted three silkscreen labels for clearance.

The defective top/bottom mask Gerbers are retained only as a labeled regression
fixture under `tests/fixtures/missing-mask/`. They are not fabrication files.
The verifier must reject them. The original complete defective package remains
in the source project's superseded archive and is not an ordering download here.

## Published credit edition

The intentional CAD changes from corrected October 21 Rev A are the
bottom silkscreen credit `hexbus.com (c) 2026` (on two lines) and moving the
C1/JP1 labels 0.20 mm toward the top edge to increase their mask clearance.
The fabrication verifier compares
copper, masks, outline and drill geometry against baseline hashes. The
original imported CAD hashes and license provenance are recorded in
[import-provenance.json](../reports/import-provenance.json).

The [first-board photograph](images/first-boards.jpg) was supplied by Jon in
the chat “Check ROM Adapters.” That review identified the component side,
JP1 setting and capacitor requirements from the photograph. It was a photo
review, not a measured continuity or operational test. Jon uses JLCPCB's
order-time QR option for JDG identifiers, for example JDG001 through JDG025.
These order-level markings are not present in the source CAD or generated
by this fabrication package; the photograph's QR payload was not decoded here.

**Pending:** assembled-board continuity, soldering quality, socket engagement,
component/enclosure clearance, supply and timing measurements, and read
operation in any host. Fabricated bare boards and passing CAD/export checks
do not establish hardware qualification. No ROM firmware is included.

## Authoritative component references

- [Motorola MCM68764 datasheet](https://deramp.com/downloads/mfe_archive/050-Component%20Specifications/Motorola/Memory%20Components/Motorola%20MCM68764.pdf),
  page 1: 24-pin assignment, +5 V supply and read-mode chip enable.
- [Microchip AT28C64B, DS20006432B](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/AT28C64B-64-Kbit-8Kx8-Parallel-EEPROM-with-Page-Write-and-Software-Data-Protection-DS20006432.pdf),
  pages 4–5 and 9–11: DIP28 assignment, read conditions and timing.
- [ST M27C64A datasheet](https://media.digikey.com/pdf/Data%20Sheets/ST%20Microelectronics%20PDFS/m27c64a_Rev2006.pdf),
  pages 7–8 and 11: DIP28 assignment and read-mode VPP/control conditions.
- [MOS/Commodore component catalog](https://www.bitsavers.org/pdf/commodore/Commodore_Component_Data_Catalog_1981.pdf),
  printed page 2-112: 2364 pinout and selectable chip-select polarity.
- [Commodore C64/C64C service manual](https://www.retro-kit.co.uk/user/custom/Commodore/C64/manuals/C64C_Service_Manual.pdf):
  separate BASIC/KERNAL 2364 sockets versus other ROM configurations.

The PCB uses generic socket-strip footprints, not a qualified manufacturer
part number. Hole/pitch/row geometry is checked; actual strip dimensions,
finished-hole tolerance, mating pin length and assembled height must be
checked against the parts used. Different 2764 manufacturers or speed grades
require their exact device documentation and host timing to be checked.
