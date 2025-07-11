import json
import xml.etree.ElementTree as ET

from collections import defaultdict
from pathlib import Path
from loguru import logger

BASE_JSONL_DIR = Path("jsonl/raw")
BASE_JSONL_DIR.mkdir(exist_ok=True)


def parse_ner(ner_elem):
    entities = defaultdict(list)
    for tag in ["PER", "LOC", "ORG", "TITLE", "TME", "NUM"]:
        for ent in ner_elem.findall(tag):
            entities[tag].append(ent.text)
    return dict(entities)


def extract_metadata(meta_elem):
    return {
        "title": meta_elem.findtext("TITLE"),
        "volume": meta_elem.findtext("VOLUME"),
        "author": meta_elem.findtext("AUTHOR"),
        "translator": meta_elem.findtext("TRANSLATOR"),
        "period": meta_elem.findtext("PERIOD"),
        "language": meta_elem.findtext("LANGUAGE"),
    }


def convert_xml_to_jsonl(xml_path, jsonl_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    file_elem = root.find("FILE")
    meta = extract_metadata(file_elem.find("meta"))

    with open(jsonl_path, "w", encoding="utf-8") as fout:
        for sect in file_elem.findall("SECT"):
            section_id = sect.get("ID")
            for page in sect.findall("PAGE"):
                page_id = page.get("ID")
                for stc in page.findall("STC"):
                    stc_id = stc.get("ID")
                    text = (stc.text or "").strip()

                    ner_elem = stc.find("NER")
                    entities = parse_ner(ner_elem) if ner_elem is not None else {}

                    record = {
                        "id": stc_id,
                        "text": text,
                        "entities": entities,
                        "meta": {
                            **meta,
                            "section_id": section_id,
                            "page_id": page_id,
                        },
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info(f"✅ Finished writing to: {jsonl_path}")


def main():
    XML_PATHS = [
        "xml/An-Si-Toan-Thu-DIEUPHAPAM-Dich-Am-Chat-Van-quyen-thuong_with_ner.xml",
        "xml/an-sy-toan-thu-q3-khuyen-bo-su-giet-hai_with_ner.xml",
        "xml/an-sy-toan-thu-q4-khuyen-bo-su-tham-duc_with_ner.xml",
        "xml/an-sy-toan-thu-q5-khuyen-niem-phat-sanh-tinh-do_with_ner.xml",
        "xml/kinhtuongungbo_with_ner.xml",
        "xml/quan-am-thi-kinh-tam-minh-ngo-tang-giao_with_ner.xml",
        "xml/Thien Uyen Tap Anh (txt Việt - LeManhThat)_with_ner.xml",
        "xml/Thien Uyen Tap Anh (txt Việt - NgoDucTho)_with_ner.xml",
    ]
    # Use jsonl for better handling of large files (streaming, etc.)
    xml_json_tuple = [
        (xml_path, xml_path.replace(".xml", ".jsonl").split("/")[-1])
        for xml_path in XML_PATHS
    ]

    for xml_path, jsonl_path in xml_json_tuple:
        convert_xml_to_jsonl(xml_path, BASE_JSONL_DIR / jsonl_path)


if __name__ == "__main__":
    main()
