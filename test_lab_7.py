import book
import pytest
import library
import user


@pytest.mark.unit
def test_borrow_book():
    book1 = book.Book("Orgullo y prejuicio", "Tenoch M", 2026, "ISBN0001")
    assert book1.title == "Orgullo y prejuicio"

    book1.borrow()
    assert book1.borrowed


@pytest.mark.unit
def test_borrow_two_times_book():
    book1 = book.Book("Orgullo y prejuicio", "Tenoch M", 2026, "ISBN0001")
    book1.borrow()
    assert book1.borrowed == True
    with pytest.raises(ValueError, match="The book is already borrowed"):
        book1.borrow()


@pytest.mark.unit
def test_return_book():
    book1 = book.Book("Orgullo y prejuicio", "Tenoch M", 2026, "ISBN0001")
    assert book1.title == "Orgullo y prejuicio"

    book1.borrow()
    assert book1.borrowed
    book1.return_book()
    assert book1.borrowed == False


@pytest.mark.unit
def test_borrow_and_try_exception():
    book1 = book.Book("Orgullo y prejuicio", "Tenoch M", 2026, "ISBN0001")
    book1.borrow()
    assert book1.borrowed == True
    with pytest.raises(ValueError, match="The book is already borrowed"):
        book1.borrow()


@pytest.fixture
def lib_init():
    lib = library.Library()
    book_tenoch = book.Book("Orgullo y prejuicio", "Tenoch M", 2026, "ISBN0001")
    lib.add_book(book_tenoch)
    Tenoch = user.User("Tenoch", "0001")
    lib.add_user(Tenoch)

    return lib

@pytest.mark.unit
def test_library_init(lib_init):
    lib = lib_init
    lib.borrow_book("ISBN0001", "0001")

    assert lib.books[0].borrowed == True


@pytest.mark.wip
def test_library_init_ID_not_registered(lib_init):
    lib = lib_init

    with pytest.raises(ValueError, match="User ID not registered"):
        lib.borrow_book("ISBN0001", "0002")

@pytest.mark.unit
def test_book_initialization():
    book1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    assert book1.title == "1984"
    assert book1.borrowed == False


@pytest.mark.system
def test_system_path_1_full_cycle():
    # Camino 1: Registro, préstamo exitoso y devolución.
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    
    lib.add_book(b1)
    lib.add_user(u1)
    
    # Préstamo
    lib.borrow_book("ISBN001", "001")
    assert lib.books[0].borrowed == True
    
    # Devolución
    lib.return_book("ISBN001") # Asumiendo que tu método recibe el ISBN
    assert lib.books[0].borrowed == False

@pytest.mark.system
def test_system_path_2_multiple_interactions():
    # Camino 2: Múltiples usuarios y rechazo por libro no disponible.
    lib = library.Library()
    b1 = book.Book("To Kill a Mockingbird", "Harper Lee", 1960, "ISBN002")
    u1 = user.User("Alice", "001")
    u2 = user.User("Bob", "002")
    
    lib.add_book(b1)
    lib.add_user(u1)
    lib.add_user(u2)
    
    # Alice pide el libro
    lib.borrow_book("ISBN002", "001")
    
    # Bob intenta pedir el mismo libro que tiene Alice
    with pytest.raises(ValueError, match="The book is already borrowed"):
        lib.borrow_book("ISBN002", "002")