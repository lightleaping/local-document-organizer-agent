from dataclasses import dataclass
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class DuplicateCandidate:
    file_a: str
    file_b: str
    similarity: float


def detect_duplicates(documents, threshold: float = 0.85) -> List[DuplicateCandidate]:
    """
    Detect duplicate-like documents using TF-IDF cosine similarity.
    """
    if len(documents) < 2:
        return []

    texts = [document.text for document in documents]

    vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5)
    )

    tfidf_matrix = vectorizer.fit_transform(texts)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    candidates = []

    for i in range(len(documents)):
        for j in range(i + 1, len(documents)):
            similarity = similarity_matrix[i][j]

            if similarity >= threshold:
                candidates.append(
                    DuplicateCandidate(
                        file_a=documents[i].file_name,
                        file_b=documents[j].file_name,
                        similarity=round(float(similarity), 4),
                    )
                )

    candidates.sort(key=lambda item: item.similarity, reverse=True)

    return candidates