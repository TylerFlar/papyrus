from app.services.chunker import chunk_pages, chunk_text, detect_section


class TestDetectSection:
    def test_detects_introduction(self):
        assert detect_section("Introduction\nSome text here") == "Introduction"

    def test_detects_methods(self):
        assert detect_section("Methods\nWe used a novel approach") == "Methods"

    def test_detects_methodology_as_methods(self):
        assert detect_section("Methodology\nOur methodology") == "Methods"

    def test_detects_results(self):
        assert detect_section("Results\nThe results show") == "Results"

    def test_detects_discussion(self):
        assert detect_section("Discussion\nWe discuss") == "Discussion"

    def test_detects_conclusion(self):
        assert detect_section("Conclusion\nIn conclusion") == "Conclusion"

    def test_detects_references(self):
        assert detect_section("References\n[1] Smith") == "References"

    def test_detects_numbered_section(self):
        assert detect_section("2. Methods\nWe applied") == "Methods"

    def test_returns_none_for_no_section(self):
        assert detect_section("Some random paragraph text that is not a heading") is None

    def test_returns_none_for_long_lines(self):
        assert detect_section("x" * 200) is None

    def test_detects_abstract(self):
        assert detect_section("Abstract\nThis paper presents") == "Abstract"

    def test_detects_related_work(self):
        assert detect_section("Related Work\nPrior studies") == "Related Work"


class TestChunkText:
    def test_short_text_returns_single_chunk(self):
        chunks = chunk_text("Hello world", chunk_size=1000, chunk_overlap=200)
        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"
        assert chunks[0].chunk_index == 0

    def test_empty_text_returns_empty(self):
        chunks = chunk_text("", chunk_size=1000, chunk_overlap=200)
        assert len(chunks) == 0

    def test_whitespace_only_returns_empty(self):
        chunks = chunk_text("   \n\n  ", chunk_size=1000, chunk_overlap=200)
        assert len(chunks) == 0

    def test_splits_long_text(self):
        text = "word " * 500  # ~2500 chars
        chunks = chunk_text(text, chunk_size=500, chunk_overlap=100)
        assert len(chunks) > 1

    def test_chunks_have_sequential_indices(self):
        text = "paragraph one.\n\nparagraph two.\n\nparagraph three.\n\nparagraph four."
        chunks = chunk_text(text, chunk_size=30, chunk_overlap=5)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_no_chunk_exceeds_size_significantly(self):
        text = "This is a sentence. " * 100
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
        for chunk in chunks:
            # Allow some slack due to overlap
            assert len(chunk.text) < 500

    def test_detects_section_in_chunk(self):
        text = "Methods\nWe used a novel approach to solve the problem."
        chunks = chunk_text(text, chunk_size=1000, chunk_overlap=200)
        assert len(chunks) == 1
        assert chunks[0].section == "Methods"


class TestChunkPages:
    def test_tracks_page_numbers(self):
        pages = ["Page one content.", "Page two content.", "Page three content."]
        chunks = chunk_pages(pages, chunk_size=1000, chunk_overlap=200)
        assert all(c.page_number is not None for c in chunks)
        assert chunks[0].page_number == 1
        assert chunks[1].page_number == 2
        assert chunks[2].page_number == 3

    def test_empty_pages_skipped(self):
        pages = ["Content", "", "More content"]
        chunks = chunk_pages(pages, chunk_size=1000, chunk_overlap=200)
        assert len(chunks) == 2

    def test_section_propagates_across_chunks(self):
        pages = [
            "Introduction\nThis is the intro text that spans a while.",
            "More intro text continues on page two without a new heading.",
            "Methods\nNow we describe the methods used.",
        ]
        chunks = chunk_pages(pages, chunk_size=1000, chunk_overlap=200)
        # First chunk should detect Introduction
        assert chunks[0].section == "Introduction"
        # Second chunk should inherit Introduction
        assert chunks[1].section == "Introduction"
        # Third chunk should detect Methods
        assert chunks[2].section == "Methods"

    def test_indices_are_global(self):
        pages = ["Page one.", "Page two.", "Page three."]
        chunks = chunk_pages(pages, chunk_size=1000, chunk_overlap=200)
        indices = [c.chunk_index for c in chunks]
        assert indices == list(range(len(chunks)))
