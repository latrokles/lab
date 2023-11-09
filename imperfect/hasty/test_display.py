import pytest

from dataclasses import dataclass
from imperfect.hasty.display import proto


@proto
@dataclass
class Book:
    title: str
    authors: list[str]


@proto
@dataclass
class Section:
    name: str
    books: list[Book]


@proto
@dataclass
class Bookstore:
    sections: list[Section]


@pytest.fixture
def book():
    return Book('Mindstorms', ['Seymour Papert'])


@pytest.fixture
def bookstore(book):
    return Bookstore(
        [
            Section(
                'fiction',
                [Book('Cryptonomicon', ['Neal Stephenson'])]
            ),
            Section( 'computer science', [book])
        ]
    )


def test_dict_returns_object_attributes_as_dictionary(book):
    d = book.dict()

    assert isinstance(d, dict)
    assert d['uid'] == book.uid
    assert d['title'] == book.title
    assert d['authors'] == book.authors


def test_dictionary_representation_is_recursive(bookstore):
    d = bookstore.dict()
    print(d)

    assert len(d['sections']) == 2
    for section in d['sections']:
        assert isinstance(section, dict)
        for book in section['books']:
            assert isinstance(book, dict)
