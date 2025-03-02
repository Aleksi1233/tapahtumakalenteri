# Tapahtumakalenteri

Tapahtumakalenteri on Flask-pohjainen verkkosovellus, jonka avulla käyttäjät voivat lisätä, hallita ja etsiä tapahtumia. Sovellus mahdollistaa myös tapahtumiin ilmoittautumisen, kommenttien lähettämisen sekä tapahtumien luokittelun.

## Ominaisuudet

- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan tapahtumia.
- Käyttäjä näkee sovellukseen lisätyt tapahtumat kalenterin kautta.
- Käyttäjä pystyy hakemaan tapahtumia hakutoiminnon avulla tai selaamalla kalenteria.
- Tapahtumat voidaan luokitella tapahtumatyypin ja tapahtumapaikan mukaan.
- Käyttäjä pystyy ilmoittautumaan tapahtumaan osallistujaksi.
- Käyttäjä pystyy kommentoimaan tapahtumia ja tarkastelemaan saamiaan kommentteja profiilisivullaan.

## Sovelluksen tilanne

### Tilanne 2.2.2025
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään.
- Käyttäjällä on mahdollisuus muokata ja poistaa omia tapahtumiaan.
- Käyttäjä pystyy selaamaan eri tilojen tapahtumia etusivulla kalenteria selaamalla.
- Tapahtumat ovat värikoodattuja tapahtumatyypin perusteella.
- Suunnitteilla kalenterisuodattimet tapahtumatyyppien mukaan.

### Tilanne 17.2.2025
- Käyttäjä pystyy katsomaan ja muokkaamaan omia tapahtumiaan My Events -sivulla.
- Käyttäjä pystyy lisäämään tapahtumalle luokituksen tapahtumatyypin muodossa.
- Käyttäjä pystyy kommentoimaan tapahtumia ja ilmoittautumaan osallistujaksi.
- Etusivun kalenterissa on suodattimet, joiden avulla voi rajata näytettäviä tapahtumia.
- Klikkaamalla tapahtumaa kalenterissa avautuu tapahtumasivu, jossa voi tarkastella tietoja ja lisätä kommentteja.

### Tilanne 02.03.2025
- Lisätty hakutoiminto, jolla voi etsiä tapahtumia.
- Profiilisivulla näkyvät omat tapahtumat, osallistumiset ja saadut kommentit.
- sovelluksen tietoturvallisuutta paranneltu estämällä csrf -haavoittuvuus

## Käyttöohjeet

### Rekisteröityminen ja kirjautuminen
1. Siirry "Luo tunnus" -sivulle ja syötä haluamasi käyttäjätunnus ja salasana.
2. Paina "Luo tunnus" ja kirjaudu sisään.
3. Jos sinulla on jo tunnus, siirry "Kirjaudu sisään" -sivulle ja syötä kirjautumistiedot.

### Tapahtumien hallinta

#### Uuden tapahtuman lisääminen
1. Kirjaudu sisään ja siirry "Ilmoita tapahtuma" -sivulle.
2. Syötä tapahtuman nimi, kuvaus, ajankohta ja tapahtumapaikka.
3. Valitse tapahtumalle luokitus (esim. koulutus, juhlat, kokous).
4. Paina "Luo tapahtuma".

#### Tapahtuman muokkaaminen ja poistaminen
1. Siirry "My Events" -sivulle.
2. Valitse tapahtuma, jota haluat muokata tai poistaa.
3. Klikkaa "Muokkaa" tai "Poista" tapahtumaa.

### Hakutoiminto ja tapahtumien selaaminen
1. Hakukentässä voit etsiä tapahtumia nimellä tai kuvauksella.
2. Kalenterissa voit selata tapahtumia ja suodattaa näkyviä tapahtumia tyypin mukaan.
3. Klikkaamalla tapahtumaa avautuu tapahtumasivu.

### Kommentointi ja tapahtumiin ilmoittautuminen
1. Siirry tapahtumasivulle.
2. Voit kommentoida tapahtumaa ja nähdä muiden kommentit.
3. Jos tapahtumaan voi ilmoittautua, pääset liittymään osallistujaksi "Ilmoittaudu" -painikkeella.

### Profiilisivu
1. Siirry "Profiili" -sivulle.
2. Näet omat tapahtumat, osallistumiset ja saadut kommentit.
3. Klikkaa tapahtumaa saadaksesi lisätietoja.

## Tekninen toteutus
- Backend: Flask (Python) + SQLite
- Frontend: HTML, CSS (ei JavaScriptiä)
- Tietokanta: SQL-kyselyt suoraan ilman ORM-kirjastoja
- Turvallisuus: Salasanat hashataan ja CSRF-suojaus käytössä kaikissa POST-pyynnöissä

## Asennusohjeet
Jos haluat ajaa sovelluksen paikallisesti:

### Asenna riippuvuudet
```bash
pip install flask
```

### Luo ja käynnistä sovellus
```bash
flask run
```

### Avaa selaimessa
```
http://127.0.0.1:5000
```





