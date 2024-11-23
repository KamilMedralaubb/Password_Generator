# Password_Generator
Projekt na IO

## 🔒 Opis projektu
Password Generator to aplikacja umożliwiająca generowanie losowych, bezpiecznych haseł w zależności od preferencji użytkownika. Aplikacja została stworzona z wykorzystaniem **FastAPI** jako backendu, prostego frontendu opartego na **HTML, CSS i JavaScript**, oraz desktopowego interfejsu graficznego przy użyciu **Tkinter**.

Główne cele aplikacji to prostota obsługi, bezpieczeństwo generowanych haseł oraz dostępność na różnych platformach.

---

## 📝 Wymagania niefunkcjonalne
- **Wydajność**: Aplikacja backendowa powinna obsługiwać co najmniej 20 równoczesnych żądań.
- **Bezpieczeństwo**: Generowanie haseł musi odbywać się w sposób kryptograficznie bezpieczny przy użyciu biblioteki `secrets`.
- **Przenośność**: Aplikacja powinna działać na systemach Windows, macOS i Linux.
- **Dostępność**: Interfejs webowy powinien być lekki, oparty na czystym HTML, CSS i JavaScript.
- **Prostota użytkowania**: Intuicyjny interfejs zarówno dla wersji webowej, jak i desktopowej.

---

## 🎯 Wymagania funkcjonalne
1. **Generowanie haseł**:
   - Użytkownik może określić długość hasła (minimum 8 znaków).
   - Opcje wyboru:
     - Dodawanie znaków specjalnych.
     - Dodawanie cyfr.
     - Użycie wielkich i małych liter.

2. **Interfejs użytkownika**:
   - **Webowy**:
     - Formularz umożliwiający konfigurację hasła.
     - Przycisk do generowania hasła.
     - Opcja skopiowania wygenerowanego hasła do schowka.
   - **Desktopowy**:
     - Okno z polami wyboru i suwakami do konfiguracji hasła.
     - Przyciski do generowania i kopiowania hasła.

3. **Backend**:
   - API FastAPI z możliwością obsługi parametrów żądań:
     - Długość hasła.
     - Uwzględnienie znaków specjalnych, cyfr, wielkich i małych liter.
   - Endpoint zwracający listę ostatnio wygenerowanych haseł.

4. **Zarządzanie błędami**:
   - Walidacja danych wejściowych, np. minimalna długość hasła.
   - Odpowiednie komunikaty w przypadku błędów.

5. **Inne funkcje**:
   - Historia wygenerowanych haseł (z ograniczeniem do ostatnich 10).
   - Automatyczne kopiowanie do schowka po wygenerowaniu hasła (opcja w GUI).

---

## 📋 Uwagi końcowe
Aplikacja Password Generator to doskonałe narzędzie dla osób szukających prostego, ale skutecznego rozwiązania do generowania bezpiecznych haseł. Jej elastyczność i łatwość użycia sprawiają, że może być wykorzystywana zarówno przez osoby prywatne, jak i w środowisku biznesowym.

