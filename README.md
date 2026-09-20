# Wywóz odpadów - Gmina Wejherowo

Niestandardowa integracja Home Assistant udostępniająca harmonogram odbioru odpadów dla miejscowości i rejonów Gminy Wejherowo.

Harmonogramy są przechowywane lokalnie jako pliki JSON. Integracja automatycznie wykrywa dostępne lata i rejony, a następnie tworzy osobne sensory dla poszczególnych frakcji odpadów.

Dokumentacja dotyczy wydania `v0.2.2`.

## Funkcje

- instalacja przez HACS,
- konfiguracja z interfejsu Home Assistanta,
- wybór roku i harmonogramu,
- automatyczne wykrywanie plików `data/*.json`,
- osobny sensor dla każdej frakcji odpadów,
- informacja o najbliższym terminie odbioru,
- liczba dni pozostałych do odbioru,
- status odbioru: `scheduled`, `tomorrow`, `today` albo `finished`,
- komunikat `Brak dodatkowych wywozów` po ostatnim odbiorze w danym roku,
- możliwość zmiany roku i harmonogramu bez ponownego instalowania integracji,
- możliwość tworzenia powiadomień oraz kart z dynamicznymi kolorami ikon.

## Instalacja przez HACS

1. Otwórz HACS w Home Assistant.
2. Otwórz menu w prawym górnym rogu.
3. Wybierz **Custom repositories**.
4. W polu repozytorium wpisz:

   ```text
   https://github.com/MajsterTukan/GW-Garbage_Schedule
   ```

5. Jako typ wybierz **Integration**.
6. Dodaj repozytorium.
7. Wyszukaj integrację **Wywóz odpadów - Gmina Wejherowo**.
8. Otwórz integrację i wybierz **Download**.
9. Uruchom ponownie Home Assistant.

## Instalacja ręczna

1. Pobierz najnowsze wydanie repozytorium.
2. Skopiuj katalog:

   ```text
   custom_components/waste_collection
   ```

   do katalogu:

   ```text
   /config/custom_components/waste_collection
   ```

3. Uruchom ponownie Home Assistant.

## Konfiguracja

Po instalacji przejdź do:

```text
Ustawienia → Urządzenia i usługi → Dodaj integrację
```

Wyszukaj:

```text
Wywóz odpadów
```

Następnie:

1. wybierz rok,
2. wybierz harmonogram dla miejscowości lub rejonu,
3. zatwierdź konfigurację.

Integracja utworzy jedno urządzenie zawierające sensory dostępnych frakcji, między innymi:

- odpady zmieszane,
- bio,
- plastik i metal,
- papier,
- szkło,
- popiół,
- odpady zielone,
- odpady wielkogabarytowe,
- choinki.

Lista sensorów zależy od zawartości wybranego harmonogramu.

## Zmiana roku lub harmonogramu

Po opublikowaniu harmonogramów na kolejny rok nie trzeba ponownie instalować integracji.

1. Zaktualizuj integrację w HACS.
2. Otwórz:

   ```text
   Ustawienia → Urządzenia i usługi → Wywóz odpadów
   ```

3. Wybierz **Konfiguruj**.
4. Wskaż rok i harmonogram.

## Stany i atrybuty

Jeżeli istnieje kolejny termin odbioru, stan sensora zawiera jego datę:

```text
2026-10-15
```

Po ostatnim odbiorze w danym roku sensor pokazuje:

```text
Brak dodatkowych wywozów
```

Każdy sensor udostępnia dodatkowe atrybuty:

```yaml
days_remaining: 1
status: tomorrow
year: 2026
source: harmonogram.pdf
collection_day: czwartek
upcoming:
  - "2026-10-15"
  - "2026-10-29"
```

Znaczenie pola `status`:

| Status | Znaczenie |
|---|---|
| `scheduled` | Odbiór odbędzie się później niż jutro |
| `tomorrow` | Odbiór odbędzie się jutro |
| `today` | Odbiór odbywa się dzisiaj |
| `finished` | Brak kolejnych odbiorów w harmonogramie |

## Karta z kolorowymi ikonami

Dynamiczne kolory ikon wymagają niestandardowej karty [button-card](https://github.com/custom-cards/button-card), którą można zainstalować przez HACS.

Przykład kafelka dla odpadów bio:

```yaml
type: custom:button-card
entity: sensor.wywoz_odpadow_bio
name: Bio
show_state: true
show_icon: true
color: >
  [[[
    const status = entity.attributes.status;

    if (status === "finished") {
      return "var(--disabled-text-color)";
    }

    if (status === "tomorrow") {
      return "#f9a825";
    }

    if (status === "today") {
      return "#43a047";
    }

    return "var(--state-icon-color)";
  ]]]
state_display: >
  [[[
    if (entity.attributes.status === "finished") {
      return "Brak dodatkowych wywozów";
    }

    if (entity.attributes.status === "today") {
      return "Dzisiaj";
    }

    if (entity.attributes.status === "tomorrow") {
      return "Jutro";
    }

    return entity.state;
  ]]]
```

Kolory ikon:

- standardowy - odbiór w późniejszym terminie,
- żółty - odbiór następnego dnia,
- zielony - odbiór danego dnia,
- szary - brak kolejnych odbiorów w harmonogramie.

Identyfikator `sensor.wywoz_odpadow_bio` należy zastąpić identyfikatorem encji utworzonej w danej instalacji Home Assistant.

## Powiadomienie dzień przed odbiorem

Poniższa automatyzacja codziennie o godzinie 19:00 sprawdza, które frakcje zostaną odebrane następnego dnia. Jeżeli znajdzie co najmniej jedną, wysyła jedno zbiorcze powiadomienie.

```yaml
alias: Przypomnienie o wywozie odpadów
description: Powiadomienie dzień przed odbiorem odpadów
triggers:
  - trigger: time
    at: "19:00:00"
variables:
  waste_entities:
    - sensor.wywoz_odpadow_zmieszane
    - sensor.wywoz_odpadow_bio
    - sensor.wywoz_odpadow_plastik_i_metal
    - sensor.wywoz_odpadow_papier
    - sensor.wywoz_odpadow_szklo
    - sensor.wywoz_odpadow_popiol
    - sensor.wywoz_odpadow_odpady_zielone
    - sensor.wywoz_odpadow_wielkogabarytowe
    - sensor.wywoz_odpadow_choinki
  tomorrow_collections: >
    {% set result = namespace(names=[]) %}
    {% for entity in expand(waste_entities) %}
      {% if state_attr(entity.entity_id, 'status') == 'tomorrow' %}
        {% set result.names = result.names + [entity.name] %}
      {% endif %}
    {% endfor %}
    {{ result.names | join(', ') }}
conditions:
  - condition: template
    value_template: >
      {{ tomorrow_collections | trim | length > 0 }}
actions:
  - action: notify.mobile_app_nazwa_telefonu
    data:
      title: "Jutro wywóz odpadów"
      message: >
        Zabierają: {{ tomorrow_collections }}.
        Pamiętaj o wystawieniu pojemników.
mode: single
```

Przed użyciem należy:

1. zastąpić identyfikatory sensorów ich rzeczywistymi identyfikatorami,
2. zastąpić `notify.mobile_app_nazwa_telefonu` usługą powiadomień właściwego telefonu.

Usługę powiadomień można znaleźć w:

```text
Narzędzia deweloperskie → Akcje
```

## Format harmonogramu JSON

Każdy plik w katalogu:

```text
custom_components/waste_collection/data
```

reprezentuje jeden harmonogram dla konkretnego roku i obszaru.

Zalecany format nazwy pliku:

```text
2027-Miejscowosc-Rejon.json
```

Przykład:

```json
{
  "zrodlo": "harmonogram-2027.pdf",
  "rok": 2027,
  "miejscowosc": "Miejscowość - rejon północny",
  "dzien_tygodnia": "czwartek",
  "daty": {
    "zmieszane": [
      "2027-01-07",
      "2027-01-21"
    ],
    "bio": [
      "2027-01-07",
      "2027-01-21"
    ],
    "plastik_metal": [
      "2027-01-14"
    ],
    "makulatura": [
      "2027-01-14"
    ],
    "szklo": [
      "2027-01-28"
    ],
    "popiol": [],
    "zielone": [],
    "wielkogabarytowe": [],
    "choinki": []
  }
}
```

Wymagania:

- `rok` musi być liczbą całkowitą,
- `miejscowosc` musi zawierać nazwę wyświetlaną w Home Assistant,
- `daty` musi być obiektem zawierającym frakcje i listy terminów,
- każda data musi mieć format `RRRR-MM-DD`,
- wszystkie daty muszą należeć do roku podanego w polu `rok`,
- daty danej frakcji powinny być unikalne i uporządkowane rosnąco.

Nazwa pliku jest wewnętrznym identyfikatorem harmonogramu. Nie należy jej zmieniać po udostępnieniu harmonogramu użytkownikom.

## Dodawanie miejscowości

Dodanie kolejnej miejscowości nie wymaga modyfikowania kodu Pythona:

1. przygotuj nowy plik JSON,
2. umieść go w katalogu `custom_components/waste_collection/data`,
3. zwiększ wersję integracji w `manifest.json`,
4. zatwierdź zmiany,
5. utwórz nowe wydanie GitHub,
6. zaktualizuj integrację w HACS.

Nowy harmonogram automatycznie pojawi się na liście dla właściwego roku.

## Aktualizacje

Po opublikowaniu nowej wersji:

1. otwórz HACS,
2. wybierz integrację **Wywóz odpadów - Gmina Wejherowo**,
3. zainstaluj aktualizację,
4. uruchom ponownie Home Assistant.

Jeżeli aktualizacja nie pojawia się od razu, wybierz z menu repozytorium opcję **Update information** albo **Redownload**.

## Rozwiązywanie problemów

### Integracja nie pojawia się po instalacji

Uruchom ponownie Home Assistant, a następnie wyszukaj integrację w:

```text
Ustawienia → Urządzenia i usługi → Dodaj integrację
```

### Brak harmonogramów na liście

Sprawdź, czy pliki JSON znajdują się w katalogu `data` oraz czy zawierają poprawne pola `rok`, `miejscowosc` i `daty`.

### Sensor pokazuje `Nieznane`

Sprawdź dzienniki Home Assistanta oraz poprawność dat w pliku JSON. W wersji 0.2.2 poprawnie zakończony harmonogram powinien pokazywać `Brak dodatkowych wywozów`, a nie `Nieznane`.

### Dzienniki

Błędy integracji można znaleźć w:

```text
Ustawienia → System → Dzienniki
```

Wyszukaj wpisy zawierające:

```text
waste_collection
```

## Źródło danych

Terminy odbioru są przepisywane z oficjalnych harmonogramów publikowanych dla Gminy Wejherowo. Przed wystawieniem odpadów warto zweryfikować termin z aktualnym harmonogramem operatora lub gminy.

## Licencja

Projekt jest udostępniany na licencji MIT.
