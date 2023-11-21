# Ekvivalens python forráskódpárok generálása és adathalmaz összeállítása

Egy python kódokat, mélyneuronhálókkal refaktoráló, kutatásban egy kódok ekvivalenciáját eldöntő hálóhoz, **ekvivalens kódpárokat** tartalmazó, adathalmazt készítek.
Az adathalmaz minél változatosabb, egymással **garantáltan** ekvivalens kódpárokat kell tartalmazzon, és **százezres nagyságrendű** kell legyen.
Az adathalmaz egy **többoszlopos** tábla, aminben az első oszlop az eredeti forráskódot tartalmazza, a további oszlopok a forráskód egy vagy több átalakítását.
Az adathalmaz létrhozásához több eszközt alkalmazok, ezek két fő kategóriába sorolhatók:

- létező, python kódok ekvivalens módosítására alkalmas eszközök, (pl.: `isort`, `autopep`, `modernize`)

- saját, python kódokat ekvivalensen átalakító program

A szakdolgozatomban leginkább az utóbbi, python kódokat átalakító, programot szeretném részletezni.
A program célja, hogy minél több ekvivalens python átalakítást végezzen el, ezek például lehetnek lehetnek:

- egyszerű átalakítások (formázások, átnevezések)

- összetett átalakítások (python kódokon gyakran végzett átalakítások, például egy kollekciót változtató `for` ciklus *"comprehension"* kifejezéssé alakítása)

Az átalakítások az absztrakt szintaxisfa módosításával működnek. Egy átalakítás egy adott csúcsra mintailleszt, ha a csúcs megfelel alkalmazza az átalakítást, megváltoztatva a absztrakt szintaxisfát. Ennek megvalósítására a `RedBaron` könyvtárat használom.
