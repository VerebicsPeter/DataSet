## Címek

- Python kódok ekvivalenciáját vizsgáló neuronháló adathalmazának összeállítása
- Ekvivalens python forráskód-párok generálása és adathalmaz összeállítása
- Ekvivalens és inekvivalens forráskód-párok generálása pythonban

## Témabejelentő

Egy python kódokat, mély-neuronhálókkal refaktoráló, kutatásban egy kódok ekvivalenciáját eldöntő hálóhoz, ekvivalens és inekvivalens kódpárokat tartalmazó, adathalmazt készítek.

Az adathalmaz minél változatosabb, egymással garantáltan ekvivalens vagy inekvivalens kódpárokat kell tartalmazzon és legalább százezres nagyságrendű kell legyen, így az adathalmaz két többoszlopos tábla (ekvivalens és inekvivalens kódokat tartalmazó táblák), amiben az első oszlop az eredeti forráskódot tartalmazza, a további oszlopok a forráskód egy vagy több átalakításának eredményét.

Az adathalmaz létrehozásához több eszközt alkalmazok, ezek két fő kategóriába sorolhatók:

- létező, python kódok ekvivalens módosítására alkalmas eszközök, (pl.: `isort`, `autopep`)

- saját, python kódokat ekvivalensen átalakító program

A szakdolgozatomban leginkább az utóbbi, python kódokat átalakító, programot szeretném részletezni.
A program célja, hogy minél több ekvivalens python átalakítást végezzen el, ezek például lehetnek lehetnek:

- egyszerű átalakítások (formázások, átnevezések)

- összetett átalakítások (python kódokon gyakran végzett átalakítások, például egy kollekciót változtató `for` ciklus *"comprehension"* kifejezéssé alakítása)

Az átalakítások az **absztrakt szintaxisfa** módosításával működnek. Egy átalakítás egy adott absztrakt szintaxisfa beli csúcsra mintailleszt, ha a csúcs megfelel alkalmazza az átalakítást, megváltoztatva a absztrakt szintaxisfát. Ennek megvalósítására a `RedBaron` python könyvtárat használom, ami lehetőséget ad absztrakt szintaxisfa szintű lekérdezések és módosítások írására.
