from tkinter import N
import scrapy
import datetime
from scrapy_splash import SplashRequest
from scrapy.utils.python import to_native_str

""" 
__________________________________________________ NB : __________________________________________________
    Ce scraper pour but récupérer les commentaires à partir du site "tripadvisor", mais dans ce site 
on distingue entre deux structures de pages l'une dédiée aux hôtels et l'autre pour les autres activités.
C'est pour cela on va traiter ces deux cas dans ce script.
__________________________________________________________________________________________________________
"""


# Une fontion pour la conversion du mois en nombre :
def month_converter(month):
    months = ['janvier', 
              'février', 
              'mars', 
              'avril', 
              'mai', 
              'juin', 
              'juillet', 
              'août', 
              'septembre', 
              'octobre', 
              'novembre', 
              'décembre']

    months_abrévé = ['janv.', 
                    'févr.', 
                    'mars', 
                    'avr.', 
                    'mai', 
                    'juin', 
                    'juil.', 
                    'août', 
                    'sept.', 
                    'oct.', 
                    'nov.', 
                    'déc.' ]

    try :            
        return str(months.index(month)+1)
    except :
        return str(months_abrévé.index(month)+1)


# Une fontion pour la conversion du date en format jj/mm/AAAA :
def format_date(day, month, year):

    if len(day) == 1 :
        day = '0'+str(day)
    
    month = month_converter(month)
    if len(month) == 1 :
        month = '0'+str(month)
    
    return day+"/"+month+"/"+str(year)


class ReviewsSpider(scrapy.Spider):
    id = 0
    name = 'reviews'
    allowed_domains = ['tripadvisor.fr']
    # Url par défaut :
    start_urls = ['https://www.tripadvisor.fr/Attraction_Review-g293732-d7980715-Reviews-Quartier_Habous-Casablanca_Casablanca_Settat.html']


    def __init__(self, url=None, *args, **kwargs):
        super(ReviewsSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]


    def start_requests(self):
        for url in self.start_urls:
            url = to_native_str(url)
            yield SplashRequest(url, callback=self.parse)


    def parse(self, response):
        # Récuperation des commentaires existent dans la page courant :
        reviews = response.xpath('//*[@data-automation="reviewCard"]')

        # Si le nombre des commentaires est différent de zéro alors on est dans la page dea activitées : 
        if len(reviews) != 0 :

            # On va parcourir la liste des commentaires afin de récupérer les attributs de chaque commentaire :
            for review in reviews :
                
                # Incrementation automatique d'attribut "id"
                ReviewsSpider.id += 1

                # Nom du commentateur :
                pr_name = review.xpath('.//*[@class="zpDvc"]/span/a/text()').get()

                # La recuperation de la localisation qui contient la ville + le pays : 
                localisation = review.xpath('.//*[@class="zpDvc"]/div/div/span/text()').get()

                rv_ville = ''
                rv_pays  = ''
                # Si la valeur de la localisation n'est pas null alor on doit traiter chaque attribut tout seul 
                if localisation is not None :
                    if ("contributions" not in localisation) and ("contribution" not in localisation) :
                        if ',' in localisation :
                            # La récuperation de la ville 
                            rv_ville = localisation.split(',')[0]
                            # La récuperation du pays 
                            rv_pays  = localisation.split(',')[1]
                        else :
                            rv_pays = localisation
                
                # Recuperation du nombre de likes :
                rv_likes = review.xpath('.//*[@class="kLqdM"]/span/text()').get()

                # Recuperation de la valeur du rating :
                rv_rating = review.xpath('.//*[@class="UctUV d H0"]/@aria-label').get()
                if rv_rating is not None :
                    rv_rating = rv_rating.replace('bulles','').split('sur')[0].strip()
                
                # La récuperation du tite 
                rv_title = review.xpath('.//*[@class="biGQs _P fiohW qWPrE ncFvv fOtGX"]/a/span/text()').get()
                if rv_title is None :
                    # Le cas du titre traduit :
                    rv_title = review.xpath('.//*[@class="biGQs _P fiohW qWPrE ncFvv fOtGX"]/a/span/span/text()').get()

                # La récuperation du body 
                rv_body = ''.join(review.xpath('.//*[@class="fIrGe _T bgMZj"]/div/span/text()').getall())
                if rv_body == '' :
                    # Le cas du body traduit :
                    rv_body = ''.join(review.xpath('.//*[@class="fIrGe _T bgMZj"]/div/span/span/text()').getall())

                # Récuperation de la date du commentaire 
                date = review.xpath('.//*[@class="TreSq"]/div/text()').get()
                if date is not None :
                    date = date.replace('Écrit le','').strip().split(" ")
                    rv_date = format_date(date[0],date[1],date[2])
            
                # Création d'objet commentaire avec ses attributs
                review = {
                    'id': ReviewsSpider.id,
                    
                    #Nombre d'étoiles :
                    'rv_stars_rating' : rv_rating,

                    #Titre
                    'rv_titre' : rv_title,

                    #Contenu du commentaire
                    'rv_body' : rv_body,

                    #Pays et ville
                    'rv_pays' : rv_pays,
                    'rv_ville' : rv_ville,
                    
                    #Date du commentaire :
                    'rv_date' : rv_date,
                    
                    #Nb personnes qu'ont trouvé le commentaire utile
                    'rv_utile' : rv_likes,                
                }
                
                yield review
        
        
            #Lien de la page suivante :
            page_suivante = response.xpath('//*[@class="xkSty"]/div/a/@href').get()

            if page_suivante is not None:
                yield response.follow(page_suivante, callback=self.parse)
                print("Next page")
               
        # Cas de la page des hôtéls :
        else :
            # Récuperation des commentaires existent dans la page courant :
            reviews = response.xpath('//*[@data-test-target="HR_CC_CARD"]')
            for review in reviews :
                
                # Incrementation automatique d'attribut "id"
                ReviewsSpider.id += 1

                #pr_name = review.xpath('.//*[@class="zpDvc"]/span/a/text()').get()
                
                # La recuperation de la localisation qui contient la ville + le pays : 
                localisation = review.xpath('.//*[@class="RdTWF"]/span/text()').get()

                rv_ville = ''
                rv_pays  = ''
                # Si la valeur de la localisation n'est pas null alor on doit traiter chaque attribut tout seul 
                if localisation is not None :
                    if ',' in localisation :
                        rv_ville = localisation.split(',')[0]
                        rv_pays  = localisation.split(',')[1]
                    else :
                        rv_pays = localisation
                
                # Recuperation du nombre de likes :
                rv_likes = ''
                spans = review.xpath('.//*[@class="phMBo"]')
                # tester si la liste des spans est n'est pas vide ...
                if spans :
                    # On va parcourir la liste des span qui ont cette classe pour récupere la velur du span convenable :  
                    for span in spans :
                        text_span = span.xpath('./span/text()').get()
                        if text_span is not None :
                            if ("contributions" not in text_span) and ("contribution" not in text_span) :
                                # Extraction du nombre de likes :
                                rv_likes = span.xpath('./span/span/text()').get()
                                
                        
                # Recuperation de la valeur du rating :
                rv_rating = review.xpath('.//*[@data-test-target="review-rating"]/span/@class').get()
                if rv_rating is not None :
                    rv_rating = int(rv_rating.split('_')[-1])/10

                # La récuperation du tite     
                rv_title = review.xpath('.//*[@data-test-target="review-title"]/a/span/span/text()').get()

                # La récuperation du body
                rv_body = ''.join(review.xpath('.//*[@class="fIrGe _T"]/q/span/text()').getall())

                # Récuperation de la date du commentaire 
                date = review.xpath('.//*[@class="cRVSd"]/span/text()').get()
                if date is not None :
                    date = date.replace('a écrit un avis','').replace('(','').replace(')','').strip().split(" ")
                    if date[0].isnumeric() :
                        rv_date = format_date('0',date[1],datetime.date.today().year)
                    else :
                        rv_date = format_date('0',date[0],date[1])

                # Récuperation de la date de séjour :
                date = review.xpath('.//*[@class="teHYY _R Me S4 H3"]/text()').get()
                if date is not None :
                    date = date.strip().split(" ")
                    rv_date_sejour = format_date('0',date[0],date[1])
            
                # Création d'objet commentaire avec ses attributs
                review = {
                    'id': ReviewsSpider.id,
                    
                    #Nombre d'étoiles :
                    'rv_stars_rating' : rv_rating,
                    
                    #Titre
                    'rv_titre' : rv_title,
                    
                    #Contenu du commentaire
                    'rv_body' : rv_body,

                    #Pays et ville
                    'rv_pays' : rv_pays,
                    'rv_ville' : rv_ville,

                    #Date du commentaire:
                    'rv_date' : rv_date,

                    #Date de séjour :
                    'rv_date_sejour' : rv_date_sejour,

                    #Nb personnes qu'ont trouvé le commentaire utile
                    'rv_utile' : rv_likes,                
                }
                
                yield review
            
            #Lien de la page suivante :
            page_suivante = response.xpath('//*[@class="ui_button nav next primary "]/@href').get()

            if page_suivante is not None:
                yield response.follow(page_suivante, callback=self.parse)
                print("Next page")
        
        pass
