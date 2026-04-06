import pymupdf
import pytest


@pytest.fixture
def sample_pdf(tmp_path):
    """Create a minimal PDF for testing."""
    pdf_path = tmp_path / "test_paper.pdf"
    doc = pymupdf.open()

    # Page 1: Title and abstract
    page1 = doc.new_page()
    page1.insert_text(
        (72, 100),
        "A Novel Approach to Machine Learning\n\n"
        "John Doe, Jane Smith\n\n"
        "Abstract\n\n"
        "This paper presents a novel approach to machine learning "
        "that improves accuracy by 15% over existing methods. "
        "We demonstrate our results on three benchmark datasets.\n\n"
        "Introduction\n\n"
        "Machine learning has become an essential tool in modern computing.",
        fontsize=11,
    )

    # Page 2: Methods and Results
    page2 = doc.new_page()
    page2.insert_text(
        (72, 100),
        "Methods\n\n"
        "We used a transformer-based architecture with attention mechanisms. "
        "The model was trained on 100k samples with a learning rate of 0.001. "
        "We applied cross-validation with 5 folds.\n\n"
        "Results\n\n"
        "Our method achieved 95.2% accuracy on the test set, "
        "outperforming the baseline by 15%. The F1 score was 0.93.",
        fontsize=11,
    )

    # Page 3: Discussion and References
    page3 = doc.new_page()
    page3.insert_text(
        (72, 100),
        "Discussion\n\n"
        "The results demonstrate that our approach is effective. "
        "Future work includes scaling to larger datasets.\n\n"
        "Conclusion\n\n"
        "We presented a novel machine learning approach with strong results.\n\n"
        "References\n\n"
        "[1] Smith et al. Deep Learning for NLP. Nature, 2020.\n"
        "[2] Johnson, A. Attention Is All You Need. NIPS, 2017.\n"
        "[3] Lee, B. Transformers in Practice. ICML, 2021.",
        fontsize=11,
    )

    doc.save(str(pdf_path))
    doc.close()
    return pdf_path
