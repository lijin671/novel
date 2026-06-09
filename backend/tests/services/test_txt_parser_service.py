from app.services.txt_parser_service import txt_parser_service


def test_split_chapters_recognizes_spaced_numeric_headings_with_long_titles():
    text = """
第 1 章  第1章 很长很长很长很长很长的标题一

第一章正文。

第 2 章  第2章 很长很长很长很长很长的标题二

第二章正文。

第 3 章  第3章 很长很长很长很长很长的标题三

第三章正文。
""".strip()

    chapters = txt_parser_service.split_chapters(text)

    assert [chapter["title"] for chapter in chapters] == [
        "第 1 章  第1章 很长很长很长很长很长的标题一",
        "第 2 章  第2章 很长很长很长很长很长的标题二",
        "第 3 章  第3章 很长很长很长很长很长的标题三",
    ]
    assert [chapter["content"] for chapter in chapters] == [
        "第一章正文。",
        "第二章正文。",
        "第三章正文。",
    ]
