# TURA 04 — inwentaryzacja i wdrożenie

Źródła: `UWAGI TURA 04.pdf` (18 slajdów, tekst + zrzuty), `barwy i powierzchnie.xlsx`, ikony pieszy/pojazd.

`seed_cms` tylko uzupełnia braki (`get_or_create`). Nie kasować treści produktów, Do pobrania, punktów sprzedaży, SurfaceItem, ofert pracy, testowego bloku O nas.

**CMS dla klienta:** Do pobrania i Gdzie kupić można uzupełniać bez przerwy (poza 1–2 min restartu `web`). Barwy i powierzchnie w CMS — nie ruszać do końca tej tury. Produkty są w 100% — rekordów nie nadpisujemy.

---

## Slajd 1 — Kolory na pasku kategorii

**Prośba:** wszystkie paski kategorii w całości szare z paskami (jak Produkty / Porady po lewej), bez drugiego (burgundowego) koloru.

**Wdrożenie:** usunąć klin `rgba(225, 25, 70, …)` z `.page-hero::before` i `.product-filters__pattern`. Zostaje szare tło + ukośne paski.

---

## Slajdy 2–3 — Barwy i powierzchnie

**Prośba:** bez filtrów. Najpierw nazwy kolorów z małym oknem ilustracji. Po kliknięciu w kolor — produkty w tym kolorze: (a) zdjęcie faktury z powiększeniem jak Bruk-Bet (1. klik = powiększenie w rzędzie, 2. klik = lightbox), (b) nazwa produktu, (c) mała ikona rodzaju powierzchni. CMS: ikony powierzchni, nowe kolory, zdjęcia.

**Excel (mapa, nie import do bazy):**

| Rodzaj powierzchni | Kolory | Produkty (przykłady) |
|---|---|---|
| AVANGARDE | onyx, agat, topaz, jaspis | CORTINA, MONTE CARLO, WENECJA, LAPPARE, GRADO |
| TOP ARTE | topaz, onyx, opal, dioryt | MUSSO |
| COLORATTO | pastelowy, kasztanowy, muszelkowy, marengo, antracytowy, torfowy | DESIO, FERRARA, WENECJA, CORTINA, … |
| ONE COLOR | platyna, inox, lawa, sahara, ochra, kobaltowy, popielaty, polarny | MUSSO, LAMEZIA, LARINO, … |
| DIAMENTI | CRISTAL | MUSSO |
| MAŁA ARCHITEKTURA | perla, grafit, brąz, marengo, antracytowy | CENTO, MERSANO, obrzeża, stopnie |

**Wdrożenie:** `/barwy-i-powierzchnie/` = lista kolorów; `/barwy-i-powierzchnie/<slug>/` = produkty. Match atrybut KOLOR ↔ `SurfaceItem.title`. Pole ikony na `SurfaceType`. Filtry `filter_*` zostają w modelu, schowane na froncie. Bez kasowania SurfaceItem.

---

## Slajdy 4–5 — Praca i kariera

**Prośba:** wiatr między tekstem a ofertami. Intro wyłączone w CMS nadal pokazuje Lorem i stare dane. Możliwość całkowitego wyłączenia sekcji, gdy nie ma ofert.

**Wdrożenie:** brak fallbacku Lorem; intro tylko gdy blok aktywny. Ścisnąć lukę CSS. Brak aktywnych ofert → ukryć pozycję w menu i stopce.

---

## Slajdy 6–7, 9 — O nas

**Prośba:** nieaktywny blok dalej na stronie (podziękowanie rekrutacyjne wygląda jak podpis pod zdjęciem). Nowy blok „test o nas podstrony” nie jest osobną podstroną — klient prosi o instrukcję.

**Wdrożenie:** `reserved` += `page-careers-thanks`. Help w CMS: nowy blok = sekcja na `/o-nas/` lub custom na home, nie nowy URL. Nie usuwać testowego bloku.

---

## Slajd 8 — Produkty, kategoria z 1 produktem

**Prośba:** przy jednym produkcie (Piasek fugowy, Beton towarowy) pominąć listing kategorii.

**Wdrożenie:** karta grupy z 1 produktem linkuje prosto na kartę. Listing kategorii → 302 na produkt.

---

## Slajd 10 — Podtytuł produktu

**Prośba:** za co odpowiada i gdzie się wyświetla.

**Wdrożenie:** `page_lead` w hero karty. Help CMS: tekst pod nazwą na pasku kategorii, może być pusty.

---

## Slajdy 11–12 — Atrybuty

**Prośba:** kasowanie nazw atrybutów z listy (np. „Powierzchnia”). Przesuwanie kart góra/dół.

**Wdrożenie:** endpoint kasowania `ProductAttribute` z potwierdzeniem. ↑↓ na kartach → `sort_order` przypisań.

---

## Slajd 13 — Ikony nośności

**Prośba:** czarne → ciemnoszare (załączniki). Klient nie może tego zmienić w CMS.

**Wdrożenie:** podmiana `load-pedestrian.png` i `load-car.png`.

---

## Slajd 14 — Hover na nazwie koloru

**Prośba:** najechanie na nazwę koloru w atrybutach przewija do kafelka w sekcji Kolory.

**Wdrożenie:** kotwice + scroll/highlight. Brak matchu = zwykły tekst.

---

## Slajd 15 — Packshot i porady w CMS

**Prośba:** skasować wybór liczby kolumn packshotów. Ukryć kartę „Porady na karcie produktu”, bo sekcja jest nieaktywna.

**Wdrożenie:** UI kolumn znika, pole w DB zostaje. Karta porad znika z formularza, M2M zostaje.

---

## Slajd 16 — Biblioteka plików

**Prośba:** szukaj po nazwie. Po skasowaniu pliku nie wracać na górę strony.

**Wdrożenie:** filtr client-side. Usuwanie AJAX / zachowanie scrollY.

---

## Slajd 17 — Piny GRADO

**Prośba:** tylko kostka GRADO (`/produkty/23/`) wywala błąd przy pinach. Nie kasować treści.

**Wdrożenie:** diagnoza na serwerze, poprawka formsetu/JS.

---

## Slajd 18 — Mapa Gdzie kupić (pytanie, bez kodu)

Mapa z pinami już działa na **vestone.eu**. Zrzut to stary vestone.pl. Punkty dodaje się w CMS → Punkty sprzedaży (współrzędne). Nie czekać na przeniesienie domeny.
