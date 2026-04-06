from app.services.pdf_processor import ExtractedPaper, _extract_abstract, extract_paper


class TestExtractPaper:
    def test_extracts_pages(self, sample_pdf):
        result = extract_paper(sample_pdf)
        assert isinstance(result, ExtractedPaper)
        assert len(result.pages) == 3
        assert result.metadata.page_count == 3

    def test_extracts_full_text(self, sample_pdf):
        result = extract_paper(sample_pdf)
        assert len(result.full_text) > 0
        assert "machine learning" in result.full_text.lower()

    def test_extracts_title(self, sample_pdf):
        result = extract_paper(sample_pdf)
        # Should pick up some title text from the first page
        assert result.metadata.title != "Untitled"
        assert len(result.metadata.title) > 5


class TestExtractAbstract:
    def test_finds_abstract(self):
        text = (
            "Title of Paper\n\n"
            "Abstract\n\n"
            "This paper explores novel techniques for natural language processing. "
            "We present a method that achieves state-of-the-art results.\n\n"
            "Introduction\n\n"
            "NLP has made great progress."
        )
        abstract = _extract_abstract(text)
        assert abstract is not None
        assert "novel techniques" in abstract
        assert "Introduction" not in abstract

    def test_returns_none_when_no_abstract(self):
        text = "Just some regular text without any abstract section markers."
        abstract = _extract_abstract(text)
        assert abstract is None

    def test_handles_abstract_with_colon(self):
        text = (
            "Abstract: This study investigates the effects of temperature "
            "on the growth rate of crystals in a controlled environment. "
            "Our findings suggest a strong correlation between temperature and growth.\n\n"
            "1. Introduction\n\n"
            "Crystal growth has been studied extensively."
        )
        abstract = _extract_abstract(text)
        assert abstract is not None
        assert "investigates" in abstract

    def test_short_abstract_rejected(self):
        text = "Abstract\nShort.\n\nIntroduction\nReal content here."
        abstract = _extract_abstract(text)
        # Too short to be a real abstract (< 50 chars)
        assert abstract is None
