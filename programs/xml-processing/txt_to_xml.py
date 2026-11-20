import re


def escape_xml(text):
    """텍스트에 포함된 XML 특수 문자 이스케이프"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def convert_txt_to_xml(input_file, output_file):
    """구조 표시와 개체 태그가 포함된 TXT 파일을 XML로 변환"""
    tag_mapping = {
        "<인명>": "<Person>", "</인명>": "</Person>",
        "<지명>": "<Place>", "</지명>": "</Place>",
        "<시간>": "<Date>", "</시간>": "</Date>",
        "<기관명>": "<Organization>", "</기관명>": "</Organization>",
        "<서명>": "<Book>", "</서명>": "</Book>",
        "<문화유산>": "<Heritage>", "</문화유산>": "</Heritage>",
        "<사건명>": "<Event>", "</사건명>": "</Event>",
        "<작품명>": "<Work>", "</작품명>": "</Work>",
    }

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        xml_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<root>",
        ]

        in_p = False
        waiting_meta = None

        for raw_line in raw_lines:
            line = raw_line.strip()
            if not line:
                continue

            if line == "#Title":
                waiting_meta = "title"
                continue
            if line == "#Publisher":
                waiting_meta = "publisher"
                continue
            if line == "#Chapter":
                waiting_meta = "chapter"
                continue
            if re.fullmatch(r"#Topic\d*", line):
                waiting_meta = "topic"
                continue

            if waiting_meta:
                level_map = {
                    "title": "level1",
                    "publisher": "level2",
                    "chapter": "level3",
                    "topic": "level4",
                }
                xml_lines.append(
                    f'<{waiting_meta} type="{level_map[waiting_meta]}">'
                    f"{escape_xml(line)}</{waiting_meta}>"
                )
                waiting_meta = None
                continue

            # 기존 문단을 닫고 새 문단 열기
            if line.startswith("#txt_"):
                if in_p:
                    xml_lines.append("</p>")
                p_id = line.replace("#", "")
                xml_lines.append(f'<p id="{p_id}">')
                in_p = True
                continue

            # 한글 개체 태그 -> 영문 태그로 변환
            for kor, eng in tag_mapping.items():
                line = line.replace(kor, eng)

            # 특수 문자를 처리 & 예외 복원
            line = escape_xml(line)
            for eng in tag_mapping.values():
                line = line.replace(escape_xml(eng), eng)

            xml_lines.append(line)

        if in_p:
            xml_lines.append("</p>")

        xml_lines.append("</root>")

        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(xml_lines))

        print(f"변환 완료: {output_file}")

    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    convert_txt_to_xml("input.txt", "output.xml")
