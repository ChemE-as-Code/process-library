"""Read the first worksheet of an .xlsx or a BIFF5/BIFF8 .xls file with the standard library only.

cheme-as-code's interpreter (`cheme run`) has no spreadsheet package, so scripts/adapt_4tu.py
reads the 4TU raw files with this module. It returns the cells of the first sheet as
{(row, col): value}, 0-based; a value is a float (numbers, dates and times as Excel serial
numbers) or a str. Formulas give their cached result. Nothing else (formats, styles, merged
cells) is read. Enough for the instrument exports of the dataset, not a general reader.
"""

from __future__ import annotations

import io
import re
import struct
import zipfile
from xml.etree import ElementTree

__all__ = ["read_sheet", "xls_cells", "xlsx_cells"]

_NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
       "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
       "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


def read_sheet(name: str, data: bytes) -> dict[tuple[int, int], float | str]:
    """The cells of the first worksheet of *data*, by the extension of *name*."""
    if name.lower().endswith(".xlsx"):
        return xlsx_cells(data)
    if name.lower().endswith(".xls"):
        return xls_cells(data)
    raise ValueError(f"{name}: neither .xlsx nor .xls")


# -- xlsx (Office Open XML) ----------------------------------------------------------------------


def _col_index(ref: str) -> tuple[int, int]:
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    if not m:
        raise ValueError(f"cell reference {ref!r}")
    col = 0
    for ch in m.group(1):
        col = col * 26 + ord(ch) - 64
    return int(m.group(2)) - 1, col - 1


def xlsx_cells(data: bytes) -> dict[tuple[int, int], float | str]:
    z = zipfile.ZipFile(io.BytesIO(data))
    names = set(z.namelist())
    shared: list[str] = []
    if "xl/sharedStrings.xml" in names:
        root = ElementTree.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", _NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{_NS['m']}}}t")))
    # the first sheet of the workbook, through its relationship
    wb = ElementTree.fromstring(z.read("xl/workbook.xml"))
    first = wb.find("m:sheets/m:sheet", _NS)
    rid = first.get(f"{{{_NS['r']}}}id")
    rels = ElementTree.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = next(r.get("Target") for r in rels.findall("rel:Relationship", _NS) if r.get("Id") == rid)
    path = target.lstrip("/") if target.startswith("/") else "xl/" + target
    sheet = ElementTree.fromstring(z.read(path))
    cells: dict[tuple[int, int], float | str] = {}
    for c in sheet.iter(f"{{{_NS['m']}}}c"):
        kind = c.get("t", "n")
        v = c.find("m:v", _NS)
        if kind == "inlineStr":
            text = "".join(t.text or "" for t in c.iter(f"{{{_NS['m']}}}t"))
            cells[_col_index(c.get("r"))] = text
            continue
        if v is None or v.text is None:
            continue
        if kind == "s":
            value: float | str = shared[int(v.text)]
        elif kind in ("str", "e"):
            value = v.text
        elif kind == "b":
            value = float(v.text)
        else:
            value = float(v.text)
        cells[_col_index(c.get("r"))] = value
    return cells


# -- xls (BIFF5 or BIFF8 in an OLE2 compound file) --------------------------------------------------------

_FREE, _END = 0xFFFFFFFF, 0xFFFFFFFE


def _ole_stream(data: bytes, wanted: tuple[str, ...]) -> bytes:
    if data[:8] != bytes.fromhex("D0CF11E0A1B11AE1"):
        raise ValueError("not an OLE2 compound file")
    ss = 1 << struct.unpack_from("<H", data, 0x1E)[0]
    mss = 1 << struct.unpack_from("<H", data, 0x20)[0]
    n_fat, first_dir = struct.unpack_from("<II", data, 0x2C)[0], struct.unpack_from("<I", data, 0x30)[0]
    cutoff, first_minifat, n_minifat, first_difat, n_difat = struct.unpack_from("<IIIII", data, 0x38)

    def sector(i: int) -> bytes:
        return data[(i + 1) * ss:(i + 2) * ss]

    difat = [x for x in struct.unpack_from("<109I", data, 0x4C) if x not in (_FREE, _END)]
    nxt = first_difat
    for _ in range(n_difat):
        if nxt in (_FREE, _END):
            break
        entries = struct.unpack(f"<{ss // 4}I", sector(nxt))
        difat += [x for x in entries[:-1] if x not in (_FREE, _END)]
        nxt = entries[-1]
    fat: list[int] = []
    for s in difat[:n_fat]:
        fat += struct.unpack(f"<{ss // 4}I", sector(s))

    def chain(start: int, table: list[int]) -> list[int]:
        out, seen = [], set()
        while start not in (_FREE, _END) and start < len(table):
            if start in seen:
                raise ValueError("cyclic sector chain")
            seen.add(start)
            out.append(start)
            start = table[start]
        return out

    directory = b"".join(sector(s) for s in chain(first_dir, fat))
    entries = []
    for off in range(0, len(directory), 128):
        e = directory[off:off + 128]
        nlen = struct.unpack_from("<H", e, 64)[0]
        name = e[:max(nlen - 2, 0)].decode("utf-16-le")
        kind = e[66]
        start, size = struct.unpack_from("<II", e, 116)
        entries.append((name, kind, start, size))
    root = next(e for e in entries if e[1] == 5)
    entry = next((e for e in entries if e[1] == 2 and e[0] in wanted), None)
    if entry is None:
        raise ValueError(f"no stream {' or '.join(wanted)} in the compound file")
    _, _, start, size = entry
    if size >= cutoff or root[3] == 0:
        return b"".join(sector(s) for s in chain(start, fat))[:size]
    minifat: list[int] = []
    for s in chain(first_minifat, fat)[:n_minifat]:
        minifat += struct.unpack(f"<{ss // 4}I", sector(s))
    ministream = b"".join(sector(s) for s in chain(root[2], fat))[:root[3]]
    return b"".join(ministream[m * mss:(m + 1) * mss] for m in chain(start, minifat))[:size]


def _records(stream: bytes, pos: int = 0):
    while pos + 4 <= len(stream):
        rtype, length = struct.unpack_from("<HH", stream, pos)
        yield rtype, stream[pos + 4:pos + 4 + length], pos
        pos += 4 + length


def _rk(rk: int) -> float:
    if rk & 2:
        value = float(rk >> 2 if not rk & 0x80000000 else (rk >> 2) - (1 << 30))
    else:
        value = struct.unpack("<d", struct.pack("<Q", (rk & 0xFFFFFFFC) << 32))[0]
    return value / 100 if rk & 1 else value


class _Chunks:
    """The SST record and its CONTINUE records, read across their boundaries."""

    def __init__(self, parts: list[bytes]):
        self.parts, self.i, self.pos = parts, 0, 0

    def _ensure(self) -> None:
        while self.pos >= len(self.parts[self.i]) and self.i + 1 < len(self.parts):
            self.i, self.pos = self.i + 1, 0

    def take(self, n: int) -> bytes:
        out = b""
        while n:
            self._ensure()
            part = self.parts[self.i]
            chunk = part[self.pos:self.pos + n]
            if not chunk:
                raise ValueError("SST ends early")
            out += chunk
            self.pos += len(chunk)
            n -= len(chunk)
        return out

    def chars(self, count: int, wide: bool) -> str:
        """*count* characters; at a CONTINUE boundary a new option byte gives the width."""
        text = ""
        while count:
            self._ensure()
            part = self.parts[self.i]
            if self.pos >= len(part):
                raise ValueError("SST ends early")
            width = 2 if wide else 1
            n = min(count, (len(part) - self.pos) // width)
            if n == 0:
                raise ValueError("SST string split inside a character")
            raw = part[self.pos:self.pos + n * width]
            text += raw.decode("utf-16-le" if wide else "latin-1")
            self.pos += n * width
            count -= n
            if count:
                self.i, self.pos = self.i + 1, 0
                wide = bool(self.take(1)[0] & 1)
        return text


def _sst(parts: list[bytes]) -> list[str]:
    ch = _Chunks(parts)
    _, unique = struct.unpack("<II", ch.take(8))
    out = []
    for _ in range(unique):
        count = struct.unpack("<H", ch.take(2))[0]
        flags = ch.take(1)[0]
        runs = struct.unpack("<H", ch.take(2))[0] if flags & 8 else 0
        ext = struct.unpack("<I", ch.take(4))[0] if flags & 4 else 0
        out.append(ch.chars(count, bool(flags & 1)))
        if runs:
            ch.take(4 * runs)
        if ext:
            ch.take(ext)
    return out


def _text(raw: bytes, offset: int, biff8: bool) -> str:
    """A string of a LABEL, RSTRING or STRING record: a 16-bit count, then (BIFF8) an option
    byte and 8- or 16-bit characters, or (BIFF5) 8-bit characters."""
    count = struct.unpack_from("<H", raw, offset)[0]
    if not biff8:
        return raw[offset + 2:offset + 2 + count].decode("cp1252")
    flags = raw[offset + 2]
    body = raw[offset + 3:]
    return body[:2 * count].decode("utf-16-le") if flags & 1 else body[:count].decode("latin-1")


def xls_cells(data: bytes) -> dict[tuple[int, int], float | str]:
    """The cells of the first worksheet of a BIFF8 (Excel 97-2003) or BIFF5 (Excel 5/95)
    workbook."""
    # Excel 97 and later name the stream Workbook, Excel 5/95 (BIFF5) Book
    stream = _ole_stream(data, ("Workbook", "Book"))
    rtype, rec, _ = next(_records(stream))
    version = struct.unpack_from("<H", rec)[0] if rtype == 0x0809 else 0
    if version not in (0x0500, 0x0600):
        raise ValueError(f"not a BIFF5 or BIFF8 workbook (BOF version {version:#06x})")
    biff8 = version == 0x0600
    sst_parts: list[bytes] = []
    sheets: list[int] = []
    in_sst = False
    for rtype, rec, _pos in _records(stream):
        if rtype == 0x00FC:
            sst_parts, in_sst = [rec], True
        elif rtype == 0x003C and in_sst:
            sst_parts.append(rec)
        else:
            in_sst = False
            if rtype == 0x0085:
                sheets.append(struct.unpack_from("<I", rec, 0)[0])
            elif rtype == 0x000A:  # EOF of the workbook globals
                break
    strings = _sst(sst_parts) if sst_parts else []
    if not sheets:
        raise ValueError("no worksheet in the workbook")
    cells: dict[tuple[int, int], float | str] = {}
    pending: tuple[int, int] | None = None
    for rtype, rec, _pos in _records(stream, sheets[0]):
        if rtype == 0x000A:
            break
        if rtype == 0x0203:  # NUMBER
            r, c = struct.unpack_from("<HH", rec)
            cells[(r, c)] = struct.unpack_from("<d", rec, 6)[0]
        elif rtype == 0x027E:  # RK
            r, c = struct.unpack_from("<HH", rec)
            cells[(r, c)] = _rk(struct.unpack_from("<I", rec, 6)[0])
        elif rtype == 0x00BD:  # MULRK
            r, c0 = struct.unpack_from("<HH", rec)
            n = (len(rec) - 6) // 6
            for k in range(n):
                cells[(r, c0 + k)] = _rk(struct.unpack_from("<I", rec, 4 + 6 * k + 2)[0])
        elif rtype == 0x00FD:  # LABELSST
            r, c = struct.unpack_from("<HH", rec)
            cells[(r, c)] = strings[struct.unpack_from("<I", rec, 6)[0]]
        elif rtype in (0x0204, 0x00D6):  # LABEL, RSTRING
            r, c = struct.unpack_from("<HH", rec)
            cells[(r, c)] = _text(rec, 6, biff8)
        elif rtype == 0x0006:  # FORMULA: the cached result
            r, c = struct.unpack_from("<HH", rec)
            result = rec[6:14]
            if result[6:8] == b"\xff\xff":
                if result[0] == 0:  # a string, in the STRING record that follows
                    pending = (r, c)
                elif result[0] == 1:
                    cells[(r, c)] = float(result[2])
                # 2: error, 3: empty string: left out
            else:
                cells[(r, c)] = struct.unpack("<d", result)[0]
        elif rtype == 0x0207 and pending is not None:  # STRING (a formula's text result)
            cells[pending] = _text(rec, 0, biff8)
            pending = None
    return cells
