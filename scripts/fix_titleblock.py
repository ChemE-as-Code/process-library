"""Replace the pyDEXPI template title-block data on all sheets (review finding S1-1).

Sets MetaData values per property and refreshes the cached Text of every title-block label
that shows a MetaData attribute. Throwaway; kept for provenance.
Usage: python3 scripts/fix_titleblock.py pid/P-0*.xml
"""
import re
import sys

SECTIONS = {
    "P-01": ("1", "MAC and precooling"),
    "P-02": ("2", "Front-end purification"),
    "P-03": ("3", "Cold box"),
    "P-04": ("4", "Products and storage"),
}


def values(sheet):
    num, name = SECTIONS[sheet]
    return {
        "ApprovalDateRepresentation": "",
        "ApproverName": "",
        "ArchiveNumber": "ASU-1-" + sheet,
        "CheckerName": "",
        "CreationDateRepresentation": "2026-10-18",
        "CreatorName": "Process engineering",
        "DesignerName": "Process engineering",
        "DrafterName": "cheme-as-code",
        "LastModificationDateRepresentation": "2026-10-18",
        "ProjectName": "ASU-1 air separation unit",
        "ProjectNumber": "ASU-1",
        "ProjectRangeNumber": "ASU-1",
        "ReplacedDrawing": "",
        "ResponsibleDepartmentName": "Process",
        "RevisionNumber": "A",
        "SheetNumber": num,
        "SubProjectName": "Basic engineering",
        "SubProjectNumber": "ASU-1-BE",
        "UnitIdentificationCode": "ASU-1",
        "UnitName": "Air separation unit 1",
        "EnterpriseIdentificationCode": "CLIENT",
        "EnterpriseName": "Client (ASSUMED)",
        "IndustrialComplexIdentificationCode": "SITE",
        "IndustrialComplexName": "Coastal industrial site (ASSUMED)",
        "PlantAreaIdentificationCode": "ASU",
        "PlantAreaName": "Air separation",
        "PlantSectionIdentificationCode": sheet,
        "PlantSectionName": name,
        "PlantSystemIdentificationCode": "ASU-1",
        "PlantSystemName": "ASU-1",
        "PlantTrainIdentificationCode": "1",
        "PlantTrainName": "Train 1",
        "ProcessPlantIdentificationCode": "ASU-1",
        "ProcessPlantName": "ASU-1 air separation unit",
        "SiteIdentificationCode": "COAST",
        "SiteName": "Coastal site (ASSUMED)",
        "DrawingName": name,
    }


def main():
    for path in sys.argv[1:]:
        sheet = re.search(r"(P-\d\d)", path).group(1)
        s = open(path, encoding="utf-8").read()
        s = s.replace('<Model name="example"', '<Model name="ASU-1"', 1)
        head, sep, tail = s.partition('<Components property="Diagram">')
        v = values(sheet)
        for prop, new in v.items():
            pat = r'(<Data property="' + prop + r'">\s*<String>)[^<]*(</String>)'
            head = re.sub(pat, lambda m, n=new: m.group(1) + n + m.group(2), head, count=1)
        head = head.replace("<String>approved</String>", "<String>for review</String>")
        head = head.replace("<String>genehmigt</String>", "<String>zur Prüfung</String>")

        def fix_text(m):
            block = m.group(0)
            names = re.findall(r'<Data property="AttributeName">\s*<String>([^<]*)</String>', block)
            if len(names) == 1 and names[0] in v:
                block = re.sub(r'(<Data property="Text">\s*<String>)[^<]*(</String>)',
                               lambda t: t.group(1) + v[names[0]] + t.group(2), block)
            return block

        tail = re.sub(r'<Object id="[^"]*" type="Core/Diagram.Text">.*?'
                      r'<Data property="Text">\s*<String>[^<]*</String>',
                      fix_text, tail, flags=re.S)
        tail = tail.replace("<String>approved</String>", "<String>for review</String>")
        open(path, "w", encoding="utf-8").write(head + sep + tail)


main()
