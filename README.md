# **Documentation**

## 1. Install requirements

- Python 3.7 or higher.

## 2. Docker :

### 2.1 Installation du Docker :

- Télecharger une version compatible du Docker d'aprés le site : www.docker.com
- Installer le docker sur votre machine

### 2.2 Installation de splash sur docker :

- Pull l'image avec :
  $ docker pull scrapinghub/splash
- Lancer container :
  $ docker run -it -p 8050:8050 --rm scrapinghub/splash
- Vérifier l'installation en tapant cette URL :
  $ http://localhost:8050/

## 3. Installation du scrapy :
    pip install scrapy


## 4. Installation scrapy-splash
    pip install scrapy-splash

## 5. Création du projet :  
    scrapy startproject NomDuProjet

## 6. Lier splash avec scrapy

- Ajouter ces lignes dans le fichier (settings.py)

SPLASH_URL = 'http://localhost:8050/'

DOWNLOADER_MIDDLEWARES = {
'scrapy_splash.SplashCookiesMiddleware': 723,
'scrapy_splash.SplashMiddleware': 725,
'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPIDER_MIDDLEWARES = {
'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

## 7. Quelque commandes d'utilisation : 

## 7.1 L'utilisation du Shell :

#### Lancer le shell interactive

    scrapy shell 

#### récupérer une réponse à partir de l'URL donnée et mettre à jour tous les objets associés en conséquence
    fetch('http://localhost:8050/render.html?url=URL')
exemple : fetch('http://localhost:8050/render.html?url=https://www.amazon.fr/product-reviews/B09D8L99FM/')

#### Recupération des balises à partir d'objet **response** 
    response.xpath('//*[@attribut="Valur"]')
    response.xpath('//*[@attribut="Valur"]').get()
    response.xpath('//*[@attribut="Valur"]').getall()
    response.xpath('//*[@attribut="Valur"]/balise1/..../baliseN/text()').get()


## 7.2 Manipulation des spiders :

#### Créer un spider
    scrapy genspider NomSpider Domaine/
Exemple : scrapy genspider TripAdvisor TripAdvisor.fr/

#### exécuter un spider et enregistrer la sortie dans un fichier csv
    scrapy crawl NomSpider -o file.csv


#### exécuter un spider avec l'envoie d'un argument au spider et enregistrer la sortie dans un fichier csv

scrapy crawl NomSpider -o file.csv -a NomArgument="Valeur"

