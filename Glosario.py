import pytest
import book
import library
import user


# ==================================================================
# TEMA 1: monkeypatch.setattr()
# ==================================================================

@pytest.mark.tema1
def test_borrow_book_with_monkeypatch(monkeypatch):
    """
    Verifica que Library.borrow_book invoca el método borrow() de Book
    aislando la clase Book mediante una función simulada.
    """
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)

    borrow_called = False
    def fake_borrow():
        nonlocal borrow_called
        borrow_called = True

    # Sustituye temporalmente el método borrow de b1
    monkeypatch.setattr(b1, "borrow", fake_borrow)

    lib.borrow_book("001", "ISBN001")

    # Comprueba que el mock se ejecutó y que el estado real no cambió
    assert borrow_called is True
    assert b1.borrowed is False


@pytest.mark.tema1
def test_return_book_with_monkeypatch(monkeypatch):
    """
    Verifica que Library.return_book invoca return_book() de Book
    interceptando la llamada con una función controlada.
    """
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)
    
    # Préstamo inicial real para poner borrowed en True
    lib.borrow_book(u1.user_id, b1.isbn)

    return_called = False
    def fake_return():
        nonlocal return_called
        return_called = True

    # Sustituye temporalmente return_book de b1
    monkeypatch.setattr(b1, "return_book", fake_return)

    lib.return_book("001", "ISBN001")

    # Comprueba que se invocó el mock y que b1.borrowed sigue en True
    assert return_called is True
    assert b1.borrowed is True


# ==================================================================
# TEMA 2: monkeypatch.delattr()
# ==================================================================

@pytest.mark.tema2
def test_borrow_book_missing_method(monkeypatch):
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)

    # 1. Se elimina de la CLASE book.Book, no de la instancia b1
    monkeypatch.delattr(book.Book, "borrow")

    # 2. Ahora sí Library encuentra al libro, pero al hacer b.borrow() lanza AttributeError
    with pytest.raises(AttributeError):
        lib.borrow_book("001", "ISBN001")

@pytest.mark.tema2
def test_register_return_missing_method(monkeypatch):
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)
    lib.borrow_book(u1.user_id, b1.isbn)

    # 1. Se elimina de la CLASE book.Book, no de la instancia b1
    monkeypatch.delattr(user.User, "register_return")

    # 2. Ahora sí Library encuentra al libro, pero al hacer b.borrow() lanza AttributeError
    with pytest.raises(AttributeError):
        lib.return_book(u1.user_id, b1.isbn)

# ==================================================================
# TEMA 3: monkeypatch.setitem()
# ==================================================================

@pytest.mark.tema3
def test_borrow_book_loans_disabled(monkeypatch):
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)

    # 1. Modificamos temporalmente el diccionario settings del módulo library
    monkeypatch.setitem(library.settings, "loans_enabled", False)

    # 2. Intentamos realizar el préstamo
    lib.borrow_book(u1.user_id, b1.isbn)

    # 3. Comprobamos que la operación se canceló y el libro sigue sin prestarse
    assert b1.borrowed is False

# ==================================================================
# TEMA 6: Parametrize
# ==================================================================

@pytest.mark.tema6
@pytest.mark.parametrize("isbn_input, expected_title", [
    ("ISBN001", "1984"),
    ("ISBN002", "To Kill a Mockingbird"),
    ("ISBN003", "The Great Gatsby"),
])
def test_find_book_parametrized(isbn_input, expected_title):
    """
    Verifica que Library._find_book localice correctamente el libro 
    esperado para 3 combinaciones distintas de ISBN y título.
    """
    lib = library.Library()
    lib.add_book(book.Book("1984", "George Orwell", 1949, "ISBN001"))
    lib.add_book(book.Book("To Kill a Mockingbird", "Harper Lee", 1960, "ISBN002"))
    lib.add_book(book.Book("The Great Gatsby", "F. Scott Fitzgerald", 1925, "ISBN003"))

    found_book = lib._find_book(isbn_input)

    assert found_book.title == expected_title

@pytest.mark.tema6
@pytest.mark.parametrize("isbn_input, expected_history", [
    ("ISBN001", "Borrwed: 1984"),
    ("ISBN002", "Borrwed: To Kill a Mockingbird"),
    ("ISBN003", "Borrwed: The Great Gatsby"),
])
def test_user_history_parametrized(isbn_input, expected_history):

    lib = library.Library()
    u1 = user.User("Alice", "001")
    lib.add_user(u1)
    lib.add_book(book.Book("1984", "George Orwell", 1949, "ISBN001"))
    lib.add_book(book.Book("To Kill a Mockingbird", "Harper Lee", 1960, "ISBN002"))
    lib.add_book(book.Book("The Great Gatsby", "F. Scott Fitzgerald", 1925, "ISBN003"))

    lib.borrow_book(u1.user_id, isbn_input)

    assert u1.get_history()[0] == expected_history

# ==================================================================
# TEMA 7: Fixtures
# ==================================================================

@pytest.fixture
def setup_library():
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)
    return lib, b1, u1


@pytest.mark.tema7
def test_borrow_success_with_fixture(setup_library):
    lib, b1, u1 = setup_library  # Recibimos los datos listos de la fixture

    lib.borrow_book(u1.user_id, b1.isbn)

    assert b1.borrowed is True
    assert f"Borrwed: {b1.title}" in u1.get_history()


@pytest.mark.tema7
def test_return_success_with_fixture(setup_library):
    lib, b1, u1 = setup_library

    lib.borrow_book(u1.user_id, b1.isbn)
    lib.return_book(u1.user_id, b1.isbn)

    assert b1.borrowed is False
    assert f"Reurned: {b1.title}" in u1.get_history()


@pytest.fixture
def setup_library2():
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)
    lib.borrow_book(u1.user_id, b1.isbn)
    return lib, b1, u1


@pytest.mark.tema7
def test_borrow_faild_with_fixture(setup_library2):
    lib, b1, u1 = setup_library2  # Recibimos los datos listos de la fixture
    with pytest.raises(ValueError, match="The book is already borrowed"):
            lib.borrow_book(u1.user_id, b1.isbn)


@pytest.mark.tema7
def test_return_success_with_fixture2(setup_library2):
    lib, b1, u1 = setup_library2

    lib.return_book(u1.user_id, b1.isbn)

    assert b1.borrowed is False
    assert f"Reurned: {b1.title}" in u1.get_history()

@pytest.mark.tema8
def test_find_user_faild(setup_library2):
    lib = library.Library()
    with pytest.raises(ValueError, match="User not found"):
            lib._find_user(1)

# ==================================================================
# TEMA 10: try-except
# ==================================================================

@pytest.mark.tema10
def test_borrow_exception_handled_with_try_except():

    lib = library.Library()
    # No agregamos nada a la librería para forzar un fallo al buscar
    
    error_capturado = None
    try:
        # Intentamos buscar un usuario que no existe
        lib._find_user("ID_INEXISTENTE")
    except ValueError as e:
        # Capturamos la excepción y almacenamos su mensaje
        error_capturado = str(e)

    # Verificamos que la excepción realmente ocurrió y fue atrapada
    assert error_capturado == "User not found"

@pytest.mark.tema10
def test_borrow_already_borrowed_try_except():

    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)
    lib.borrow_book(u1.user_id, b1.isbn)
    # No agregamos nada a la librería para forzar un fallo al buscar
    
    error_capturado = None
    try:
        # Intentamos buscar un usuario que no existe
        lib.borrow_book(u1.user_id, b1.isbn)
    except ValueError as e:
        # Capturamos la excepción y almacenamos su mensaje
        error_capturado = str(e)

    # Verificamos que la excepción realmente ocurrió y fue atrapada
    assert error_capturado == "The book is already borrowed"

# ==================================================================
# TEMA 11: capsys
# ==================================================================

@pytest.mark.tema11
def test_borrow_book_loans_disabled_print_output(monkeypatch, capsys):
    """
    Verifica que al intentar pedir un libro cuando loans_enabled es False,
    el sistema imprima en consola 'Loans are disabled' usando capsys.
    """
    lib = library.Library()
    b1 = book.Book("1984", "George Orwell", 1949, "ISBN001")
    u1 = user.User("Alice", "001")
    lib.add_book(b1)
    lib.add_user(u1)

    # 1. Deshabilitamos los préstamos temporalmente
    monkeypatch.setitem(library.settings, "loans_enabled", False)

    # 2. Ejecutamos la función que dispara el print()
    lib.borrow_book(u1.user_id, b1.isbn)

    # 3. Capturamos la salida estándar con capsys.readouterr()
    captured = capsys.readouterr()

    # 4. Comprobamos que el mensaje esperado esté dentro de captured.out
    assert "Loans are disabled" in captured.out