import re
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer


STOPWORDS = {
    "그리고", "그러나", "하지만", "또한", "이는", "이러한", "통해", "위해",
    "대한", "있는", "한다", "된다", "수", "등", "및", "에서", "으로", "에게",
    "문서", "기능", "시스템", "기술", "작업",
    "the", "a", "an", "and", "or", "but", "is", "are", "to", "of", "in", "for",
}


def simple_tokenizer(text: str) -> List[str]:
    """
    Tokenize Korean/English mixed text.
    """
    tokens = re.findall(r"[가-힣A-Za-z0-9]+", text.lower())

    return [
        token for token in tokens
        if len(token) >= 2 and token not in STOPWORDS
    ]


def extract_keywords(text: str, top_k: int = 5) -> List[Tuple[str, float]]:
    """
    Extract top keywords from a single document using TF-IDF.
    """
    tokens = simple_tokenizer(text)

    if not tokens:
        return []

    cleaned_text = " ".join(tokens)

    vectorizer = TfidfVectorizer(
        tokenizer=lambda x: x.split(),
        token_pattern=None
    )

    tfidf_matrix = vectorizer.fit_transform([cleaned_text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]

    keyword_scores = list(zip(feature_names, scores))

    keyword_scores = sorted(
        keyword_scores,
        key=lambda item: item[1],
        reverse=True
    )

    return keyword_scores[:top_k]