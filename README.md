# DisILike

### Matthijs Vollenbroek, Sam Tegel, Thomas Cool, Tim Zwiers
## Over onze site
'DisILike' is een social media site waarop je foto's en GIFs kan uploaden met beschrijving. Mensen kunnen jouw posts op verschillende manieren vinden:
- Door jou te volgen en op hun homepage de recente posts van mensen die zij volgen te zien.
- Door jouw post tegen te komen op de 'recent' page.
- Door jouw post op de 'hall of fame' of 'hall of shame' tegen te komen
Per account wordt bijgehouden hoeveel likes hun meest gelikete post heeft en hoeveel dislikes hun meest gedislikete post heeft. Op die manier komt er een vorm van competitie in de site waarbij je jouw scores met die van anderen kan vergelijken!
## De pagina's op de site
### Login/Register
Aanmelden als nieuwe gebruiker of inloggen als een bestaande gebeurt hier. Meerdere checks om te kijken dat de ingevulde velden correct zijn ingevuld en of de gegevens kloppen.
### Home
Zodra je ingelogd bent kom je hier terecht. Op deze pagina vind je een uitklapbaar volgend lijstje, waarin alle accounts staan die jij volgt. Je kan op een naam klikken en naar hun profielpagina gaan.
Op deze pagina is het ook mogelijk om de recente posts te zien van de mensen die jij volgt (en van jezelf).
### Wall of Fame (trending)
Hier worden de 5 meest gelikete foto's weergegeven, als een foto meer dislikes heeft dan likes, kan deze niet verschijnen op trending.
### Wall of Shame
Hier worden de 5 meest gedislikete foto's weergegeven, als een foto meer likes dan dislikes heeft, kan deze niet verschijnen op de Hall of Shame.
### Recent
Hier worden de 10 meest recent geuploade posts weergegeven, onafhankelijk van het feit of je iemand volgt of niet. Een goede plek om nieuwe accounts te leren kennen.
### Searching page
Hier is een soort leaderboard te vinden van de gebruikers van de site. Je kan ook vrienden vinden om ze te volgen of te kijken naar hun stats.
Je kan daarnaast sorteren op accounts met de meeste likes, meeste dislikes, meeste volgers en op naam.
### New Post
Hier kan je een eigen post maken! Je kan kiezen tussen een eigen afbeelding te uploaden, of te zoeken op GIFs met de GIPHY API. Een beschrijving toevoegen is ook mogelijk.
### Preview GIFS
Hier zie je 10 zoekresultaten van jouw GIPHY zoekterm. Niet tevreden over de resultaten? Dan kan je bovenin een andere zoekterm proberen.
### (My) Profile
Hier zie je per account de username, de meeste likes die dat account ooit heeft gehaald, de meeste dislikes en het aantal volgers. Ook kan je de bio lezen van het account.
Bij My profile kan je deze bio editen naar jouw wens.

## Features:
-	Post liken en disliken
-	Hall of Fame en Hall of Shame
-	Mensen Volgen
-	Mensen opzoeken via zoekbalk
-	Registreren
-	Inloggen
-	Tekst bij post plaatsen als poster van afbeelding of GIF
-	Sorteren op posts gemaakt door mensen die je volgt
-	Profiel bekijken met de meest gelikete post van dat profiel en de meeste gedislikete
- Bio schrijven bij profiel
- GIFs zoeken

## Databronnen:
API voor GIFs = http://api.giphy.com

## Afhankelijkheden:
Bootstrap voor ontwerp
phpliteadmin voor database
MD Bootstrap voor de tabel op search page (voor dit moesten we bestanden downloaden, wat betekent dat we veel regels code (ongeveer 10 duizend volgens github) niet zelf hebben geschreven)

## Concurrerende sites:
-	Instagram, bij ons kan je ook disliken en posts verdwijnen. Een highscore om naar te streven.
-	Snapchat, bij ons heb je langer de tijd om een post te bekijken.

 
## Moeilijkste delen van de site:
-	AJAX functies om likes, dislikes en volgen bij te houden.
-	GIFs posten met API.
- Het updaten van de meeste gelikete en meest gedislikete post, we wilden dit als achtergrondproces continue laten gebeuren (threading) maar dat zorgte ervoor dat flask altijd onveilig afsloot. We hebben ervoor gekozen dat bij iedere like opnieuw de meeste gelikete en gedislikete post van het account wordt geupdate.

## Overzicht van bestanden
### helpers.py
In helpers.py vind je alle communicatie met de database, als er bijvoorbeeld een lijst met posts nodig is of er moet een gebruikersnaam en wachtwoord uit de database gehaald worden, dan gebeurt dat hier.
### application.py
Hier staat in wat er bij het bezoeken van de verschillende webpagina's moet gebeuren of bij een POST of GET request. Zo worden hier de controles uitgevoerd of een gebruiker al een like heeft geplaatst en de site dan een andere respons moet geven aan de client. 
Maar ook het doorgeven van de juiste variabelen voor de html pagina's gebeurd hier. Het is dus de communicatie tussen database en client.
### project.db
Dit is de database van de site. Hierin worden onder andere de gebruikersgegevens opgeslagen, wie precies wie volgt en de postgegevens.

### images
In deze folder staan de afbeeldingen die gebruikt zijn in de markdown bestanden

### templates
In deze folder staan de html bestanden van de site

### static
In deze folder staan de map posts (waarin de geüploade afbeeldingen zijn opgeslagen), de map js (waarin onze eigen like script staat in sitescripts.js en overige scripts die gedownload zijn van MD bootstrap voor de search pagina), de map css (waarin de styles van MD bootstrap gedownload zijn) en stylesheets (waarin onze eigen styles.ccs staan)

