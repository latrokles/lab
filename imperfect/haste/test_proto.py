import pytest
import time

from pathlib import Path
from shutil import copytree, rmtree

from imperfect.haste.proto import get_system_image


def setup_test_image(rootdir):
    src = Path(rootdir) / 'testdata/image01'
    dst = Path(f'/tmp/dol-{int(time.time())}')
    if dst.exists():
        return dst

    copytree(src, dst)
    return dst


@pytest.fixture(scope='session')
def image(request):
    image_pathname = setup_test_image(request.config.rootdir)
    image = get_system_image(image_pathname)
    image.restore()
    yield image
    rmtree(image_pathname)


def test_restore(image):
    assert len(image.find_all('Object')) == 1
    assert len(image.find_all('Person')) == 2
    assert len(image.find_all('Pet')) == 2
    assert len(image.find_with_slots('Person', name='bob')) == 1


def test_create_new_objects(image):
    Book = image.object.clone('Book', title=None, author=None)
    mindstorms = Book.clone(title='Mindstorms', author='Seymour Papert')
    mindstorms.set_slot('year', '1980')
    demian = Book.clone(title='Demian', author='Herman Hesse')

    assert len(image.find_all('Book')) == 3
    assert image.find_with_slots('Book', title='Demian') == [demian]
