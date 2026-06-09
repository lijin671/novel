from __future__ import annotations

from pathlib import Path

from app.services.bandao_regression_audit_service import audit_chapter, audit_pack

ARTIFACT_DIR = Path("tmp/book-remix-test-ban-dao-20260530")


def test_regression_audit_rejects_missing_stage_terms(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text("杨翠" * 10000, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=201,
        required_word_count=10000,
    )

    assert result["passed"] is False
    assert "missing_required_terms" in result["reasons"]
    assert "楼梯间" in result["missing_terms"]


def test_regression_audit_accepts_chapter_with_required_terms(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = "第200章 楼梯间 杨翠 张元英 崔叡娜 金珉周 权恩菲 2019-04-01 HEART*IZ Violeta " + ("杨翠保持原书日常群像和情感克制。" * 900)
    (output_dir / "chapter_0201.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=201,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert result["missing_terms"] == []
    assert result["forbidden_hits"] == []



def test_regression_audit_accepts_rene_alias_for_protagonist(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "\u7b2c221\u7ae0 Rene \u5f20\u5143\u82f1 \u5d14\u53e1\u5a1c \u91d1\u73c9\u5468"
        "\u7ee7\u7eed\u5728\u5bbf\u820d\u3001\u7ec3\u4e60\u5ba4\u548c\u884c\u7a0b\u91cc\u538b\u4f4f\u60c5\u7eea\u3002"
        + ("Rene\u7528\u73a9\u7b11\u548c\u6c89\u9ed8\u7ef4\u6301\u961f\u5185\u65e5\u5e38\u3002" * 900)
    )
    (output_dir / "chapter_0221.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=221,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "\u6768\u7fe0" not in result["missing_terms"]


def test_regression_audit_accepts_jang_wonyoung_common_transliteration_alias(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第329章 杨翠 张员瑛 崔叡娜 金珉周 "
        + ("张员瑛把杯面放到练习室地板上，和杨翠一起把未说完的话压回行程里。" * 900)
    )
    (output_dir / "chapter_0329.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=329,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "张元英" not in result["missing_terms"]


def test_regression_audit_accepts_chinese_date_for_reality_anchor(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "\u7b2c231\u7ae0 Rene \u5f20\u5143\u82f1 \u5d14\u53e1\u5a1c \u91d1\u73c9\u5468"
        "\u5728\u56db\u6708\u4e00\u65e5\u7684HEART*IZ\u56de\u5f52\u51c6\u5907\u91cc"
        "\u53cd\u590d\u7ec3Violeta\u3002"
        + (
            "\u6210\u5458\u4eec\u628a\u56db\u6708\u4e00\u65e5\u8fd9\u4e2a\u8282\u70b9"
            "\u85cf\u8fdb\u65e5\u7a0b\u548c\u821e\u53f0\u7ec6\u8282\u91cc\u3002"
            * 900
        )
    )
    (output_dir / "chapter_0231.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=231,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "2019-04-01" not in result["missing_terms"]


def test_regression_audit_accepts_chinese_month_and_fraud_words_for_2019_crisis(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第381章 杨翠 张元英 崔叡娜 金珉周 权恩菲 Produce "
        "2019年11月5日，投票造假争议让IZ*ONE活动暂停。"
        + ("成员们在宿舍、会议室和练习室里消化事业停摆的不安。" * 900)
    )
    (output_dir / "chapter_0381.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=381,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "2019-11" not in result["missing_terms"]
    assert "风波" not in result["missing_terms"]


def test_regression_audit_accepts_chinese_dates_for_2020_fiesta_and_swan(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第461章 杨翠 张元英 崔叡娜 金珉周 "
        "二月十七日的FIESTA回归日程之后，六月十五日的Oneiric Diary和Swan也压进行程表。"
        + ("成员们在回归后台、练习室和车里继续维持克制的情感暗线。" * 900)
    )
    (output_dir / "chapter_0461.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=461,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "2020-02-17" not in result["missing_terms"]
    assert "2020-06-15" not in result["missing_terms"]


def test_regression_audit_accepts_chinese_dates_for_panorama_and_izone_end(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第561章 杨翠 张元英 崔叡娜 金珉周 "
        "2020年12月7日，One-reeler 和 Panorama 的回归日程压进练习室。"
        "2021年4月29日，IZ*ONE组合活动正式结束。"
        + ("她们在最后舞台前维持世界观、队内关系和克制的情感暗线。" * 900)
    )
    (output_dir / "chapter_0561.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=561,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "2020-12-07" not in result["missing_terms"]
    assert "2021-04-29" not in result["missing_terms"]


def test_regression_audit_accepts_ive_stage_without_le_sserafim_every_chapter(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第761章 杨翠 张元英 崔叡娜 金珉周 安宥真 权恩菲 "
        "2021-04-29，2021年12月1日，IVE 出道准备推进到最后一步。"
        + ("张元英和安宥真把出道舞台的走位、镜头和呼吸节奏反复排练。" * 900)
    )
    (output_dir / "chapter_0761.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=761,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "2021-12-01" not in result["missing_terms"]
    assert "IVE" not in result["missing_terms"]
    assert "LE SSERAFIM" not in result["missing_terms"]


def test_regression_audit_requires_le_sserafim_on_late_stage_anchor(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第941章 杨翠 张元英 崔叡娜 金珉周 "
        "2021年4月29日之后，2021年12月1日的IVE节点与2022年5月2日的后续节点都被排进长期计划。"
        + ("她们围绕长期选择、公司会议和成员关系整理继续推进。" * 900)
    )
    (output_dir / "chapter_0941.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=941,
        required_word_count=1000,
    )

    assert result["passed"] is False
    assert "missing_required_terms" in result["reasons"]
    assert "LE SSERAFIM" in result["missing_terms"]


def test_regression_audit_does_not_require_group_boundary_slogans_every_solo_chapter(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第652章 杨翠 张元英 崔叡娜 金珉周 安宥真 权恩菲 "
        "IVE出道准备的消息在公司走廊里被压低声音谈起，杨翠把自己的solo企划书合上。"
        + ("她在解散后的日程、练习室和制作会议里维持原有人物关系和组织边界。" * 900)
    )
    (output_dir / "chapter_0652.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=652,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "不加入 IVE" not in result["missing_terms"]
    assert "LE SSERAFIM" not in result["missing_terms"]
    assert "不加入 LE SSERAFIM" not in result["missing_terms"]


def test_regression_audit_does_not_require_secondary_stage_characters_every_solo_chapter(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    text = (
        "第667章 杨翠 张元英 崔叡娜 金珉周 "
        "她们在解散后的电话、练习室和工作室日程里继续维持原有关系。"
        + ("solo起步阶段的事业线推进，不需要每章都让阶段扩展人物露面。" * 900)
    )
    (output_dir / "chapter_0667.txt").write_text(text, encoding="utf-8")

    result = audit_chapter(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        chapter_number=667,
        required_word_count=1000,
    )

    assert result["passed"] is True
    assert "安宥真" not in result["missing_terms"]
    assert "权恩菲" not in result["missing_terms"]


def test_regression_pack_report_records_failed_chapters(tmp_path):
    output_dir = tmp_path / "pack"
    output_dir.mkdir()
    (output_dir / "chapter_0201.txt").write_text("杨翠" * 1000, encoding="utf-8")

    report = audit_pack(
        artifact_dir=ARTIFACT_DIR,
        output_dir=output_dir,
        start_chapter=201,
        end_chapter=202,
        required_word_count=1000,
    )

    assert report["passed"] is False
    assert report["chapter_count"] == 2
    assert report["failed_chapter_count"] == 2
    assert Path(report["report_path"]).exists()
