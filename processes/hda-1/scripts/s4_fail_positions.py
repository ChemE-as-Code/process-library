"""Fail positions of the actuated valves on P-01 to P-06 (S4, D-026, review 2026-11-04-basic-pids#29).

Provenance only, like the draft scripts (the sheets are hand-maintained): it was run once with
    cheme run scripts/s4_fail_positions.py
and is never rerun over the sheets. For each actuated valve that has no fail position yet it
sets FailAction and FailActionRepresentation on the controlled actuator (the authoring API's
`set_values`, as `cheme set` does) and draws a FailActionLabel next to the actuator symbol (the
label of `cheme fragment label`, as a FailActionLabel, sized as the four labels S3b drew on P-01 (2 mm text, left aligned) and placed at the upper
right of the actuator circle (2.6 mm right of and 7.5 mm above the actuator symbol's origin,
which sits at the valve stem); labels that then touch a line were moved with `cheme move`).

The positions and their reasons are D-026; control/loops.yaml repeats them per final element.
"""

from pathlib import Path

from lxml import etree

from chemeascode.domains.piping.authoring.edit import (
    Document,
    EditResult,
    finish,
    insert_child,
    set_values,
)
from chemeascode.domains.piping.authoring.fragment import _symbol_at, make_fragment

FC = ("FailClose", "F.C.")
FO = ("FailOpen", "F.O.")

# sheet -> [(actuator id, valve tag, fail position)]
VALVES = {
    "P-01": [
        ("Inst_US112_Actuator", "XV-112", FC),   # fuel trip block valve (double block with XV-125)
        ("Inst_LIC102_Actuator", "LV-102", FC),  # fresh toluene make-up: no overfill of V-100
        ("Inst_FIC103_Actuator", "FV-103", FC),  # reactor toluene feed: no feed without control
        ("Inst_PIC104_Actuator", "PV-104", FO),  # V-100 vent to flare: no overpressure of the drum
        ("Inst_FIC106_Actuator", "FV-106", FO),  # P-101 minimum flow: pump protection
        ("Inst_FIC108_Actuator", "FV-108", FC),  # make-up hydrogen: no hydrogen into the loop
        ("Inst_TIC111_Actuator", "TV-111", FC),  # H-101 fuel: no firing
        ("Inst_TIC115_Actuator", "TV-115", FO),  # quench: full quench, E-101 inlet not overheated
    ],
    "P-02": [
        ("Inst_LIC202_Actuator", "LV-202", FC),  # V-101 let-down: no gas blow-by into C-201
        ("Inst_LZ203_Actuator", "XV-204", FC),   # V-101 shutdown valve (I-201)
        ("Inst_UIC207_Actuator", "UV-207", FO),  # K-101 anti-surge: recycle open
        ("Inst_HS209_Actuator", "XV-209", FO),   # loop depressuring (I-102, HS-209)
        ("Inst_FIC211_Actuator", "FV-211", FC),  # purge to the PSA: loop held, PSA isolated
    ],
    "P-03": [
        ("Inst_PIC301_Actuator", "PV-301", FC),  # PSA hydrogen to K-101: PSA held at feed pressure
        ("Inst_PIC303_Actuator", "PV-303", FO),  # K-102 spillback: machine protection
    ],
    "P-04": [
        ("Inst_TIC402_Actuator", "TV-402", FC),  # MP steam to E-202: no heat input
        ("Inst_PIC404_Actuator", "PV-404", FO),  # off-gas to fuel gas: no overpressure of C-201
        ("Inst_LIC405_Actuator", "LV-405", FO),  # reflux: column top kept cool
        ("Inst_LIC408_Actuator", "LV-408", FC),  # bottoms to C-202: no vapour blow-by downstream
    ],
    "P-05": [
        ("Inst_TIC502_Actuator", "TV-502", FC),  # LP steam to E-204: no heat input
        ("Inst_PIC504_Actuator", "PV-504", FO),  # V-202 vent to flare: no overpressure of the drum
        ("Inst_LIC506_Actuator", "LV-506", FC),  # distillate: nothing off-spec to storage
        ("Inst_FIC507_Actuator", "FV-507", FO),  # reflux: column top kept cool
        ("Inst_LIC508_Actuator", "LV-508", FC),  # bottoms to C-203: no blow-by downstream
    ],
    "P-06": [
        ("Inst_TIC602_Actuator", "TV-602", FC),  # HP steam to E-206: no heat input
        ("Inst_PIC604_Actuator", "PV-604", FC),  # PK-201 suction: column isolated from the vent
        ("Inst_LIC606_Actuator", "LV-606", FC),  # toluene recycle to V-100: no overfill
        ("Inst_FIC607_Actuator", "FV-607", FO),  # reflux: column top kept cool
        ("Inst_LIC608_Actuator", "LV-608", FC),  # biphenyl to storage: sump not drained
    ],
}


def _label_like_p01(xml: str) -> etree._Element:
    """The fragment's label with the placement of the S3b labels on P-01."""
    label = etree.fromstring(xml)
    # The fragment gives a CustomLabel for an actuator's attribute; DEXPI has FailActionLabel,
    # the class of the S3b labels on P-01.
    label.set("type", "Plant/Diagram.FailActionLabel")
    text = label.find(".//Object[@type='Core/Diagram.Text']")
    text.find("Data[@property='Alignment']/DataReference").set(
        "data", "Core/Diagram.TextAlignment.LeftCenter"
    )
    text.find("Data[@property='Size']/Double").text = "2.0"
    return label


def main() -> None:
    for sheet_id, valves in VALVES.items():
        path = Path("pid") / f"{sheet_id}.xml"
        for actuator, tag, (enum_value, shown) in valves:
            set_values(
                path,
                actuator,
                [("FailAction", enum_value), ("FailActionRepresentation", shown)],
                fmt=False,
            )
            doc = Document.load(path)
            drawing = doc.sheet.drawings[actuator][0]
            sx, sy = _symbol_at(drawing)
            fragment = make_fragment(
                "label",
                f"{actuator}_FailAction",
                for_id=actuator,
                attribute="FailActionRepresentation",
                at=f"{sx + 2.6},{sy - 7.5}",
                sheet=path,
            )
            part = fragment.part("DRAWING")
            groups = drawing.find("Components[@property='Groups']")
            insert_child(groups, _label_like_p01(part.xml))
            finish(doc, EditResult(doc.name), write=True, fmt=True)
            print(f"{sheet_id} {tag}: {shown} ({actuator})")


if __name__ == "__main__":
    main()
