import logging, csv
import cv2
import numpy
import math

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from operator import attrgetter
from difflib import SequenceMatcher

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


RATINGS, RACCOMANDAZIONE, MOSTRAALTRO = range(3)
stato = None
menu = []
urlPiatti = []
immagini = []
matrixSimilarity = []
matrixRecomm = []
indicePiattoSelez = 0 #indicePiatto -utile per fase matr simil
immaginePiattoSelez = 'url'

#MATRICE DI SIMILARITA
#    a     b     c
# a 0.0   99.x  99.z
# b 99.x  0.0   99.y  ----> mi interessa fattore dopo il 99 ---> 0.x 0.y e 0.z
# c 99.z  99.y  0.0

# indice i fisso, j varia, faccio confronti E AGGIUNGO NUOVA RIGA MATRICE (nuova lista nella lista)


#MATRICE DELLE RACCOMANDAZIONI
# Racc1    Racc2     Racc3
# RA1       RA2       RA3
# RB1       RB2       RB3
# RC1       RC2       RC3

#come lista contenente liste matrixRecomm = [ [ra1,ra2,ra3],[rb1,rb2,rb3],[rc1,rc2,rc3] ]


class Piatto:
    def __init__(self, numero, nome, ingredienti, immagine, tag):
	    self.numero = numero
	    self.nome = nome
	    self.ingredienti = ingredienti
	    self.immagine = immagine
	    self.tag = tag

def creaMenu()-> None:
    with open('datasetNewForImgRecomm.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 1
        global menu
        for row in csv_reader:
            #rimuovo primo e ultimo carattere degli ingredienti (le quadre e gli apici doppiu "[...]") e poi splitto 
            x = row[3]
            x = x [1:]
            x = x [:-1]
            x = x.split(',')
            #IMP: presenza di ingredienti con letttere maiuscole, risolvo con funzione lower()
            x = [each_string.lower() for each_string in x]
            
            y = row[4]
            y = y.split(',')
            menu.append( Piatto(line_count, row[1], x, row[2], y) )
            line_count += 1

def creaMatrixSimilitudine():
    global urlPiatti
    global immagini
    global matrixSimilarity
    
    f = numpy.loadtxt("nomi piatti.txt", dtype=str, skiprows=1)
    urlPiatti = list(f)
    
    print(urlPiatti)
    
    for elem in urlPiatti:
        imm = cv2.imread(elem)
        immagini.append(imm)
        
    for immagine in immagini:
        print(immagine)
        
    for i in range(0, len(immagini)):
        arrayRiga = []
        for j in range(0, len(immagini)):
            res = cv2.absdiff(immagini[i], immagini[j])
            res = res.astype(numpy.uint8)
            percentage = (numpy.count_nonzero(res) * 100)/ res.size
            fractional, whole = math.modf(percentage)
            arrayRiga.append(fractional) #aggiungo elementi riga (ossia coefficiente confronto immagine i e immagine j) 
        matrixSimilarity.append(arrayRiga) #aggiungo riga calcolata alla matrice

    list_as_array = numpy.array(matrixSimilarity)
    print(list_as_array)

def creaMatrixRecomm():
    with open('matrixRecomm.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        #linecount usato anche come numero piatto per identificare raccomandazione e asssocuazione con piatto (specialmente quando menu sarà filtrato e avremo certo numero di piatto che assoceremo al vettore racc corrisp)
        global matrixRecomm
        
        for row in csv_reader:
            if line_count == 0:
                line_count += 1 #scarto prima riga
            else:
                matrixRecomm.append([line_count,row[0],row[1],row[2]]) #potrei usare dictionary ma evito right now
                line_count += 1

def fornisciRaccCorrispondente(numeroPiatto):
    
    from random import randint
    
    raccomandazioneCasuale = 'I suggest this dish because it is healthy!'
    
    for elem in matrixRecomm:
            #devo vedere primo campo (numero piatto) e se corrisponde prendo casualmente uno degli elementi 1 2 e 3
            if elem[0] == numeroPiatto:
                #prendo casualmente uno tra elem[1],elem[2],elem[3]
                indice = randint(1,3)
                raccomandazioneCasuale = elem[indice]
    
    return raccomandazioneCasuale

def stampaMatr()-> None:
    for obj in matrixRecomm:
    	print( obj[0], obj[1], obj[2], obj[3])
   # accesso a attributi di singole istanze noto l'indice
   # list[0].name, list[0].roll and so on.

 
def stampaMenu()-> None:
    for obj in menu:
    	print( obj.numero, obj.nome, obj.ingredienti, obj.immagine, obj.tag )
   # accesso a attributi di singole istanze noto l'indice
   # list[0].name

def getPiattoByImg(img):
    for obj in menu:
        if obj.immagine == img:
            return obj  

def stampaLista(lista)-> None:
    for obj in lista:
        print( obj.numero, obj.nome, obj.ingredienti, obj.immagine, obj.tag )

def stampaVettore(lista) -> None:
    for obj in lista:
        print(obj)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()
    
def stampaIngredienti(lista):
    stringa = ''
    for obj in lista:
        stringa = stringa+', '+obj
    return stringa

def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their feeling."""
    
    #reply_keyboard = [['Happy 😁'], ['Neutral 😐'], ['Sad ☹️'], ['Angry 😡']]
    reply_keyboard = [['Happy 😁', 'Neutral 😐'], ['Sad ☹️', 'Angry 😡']]
    update.message.reply_text(
        'Hi! My name is Pasta Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'How do you feel today?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return RACCOMANDAZIONE

def statoAnimo(update: Update, context: CallbackContext) -> int:
    """Stores the selected feeling and and asks for information, with respect of the actual user feelling."""
    #user = update.message.from_user
    #logger.info("Feeling of %s: %s", user.first_name, update.message.text)
    #global stato 
    #stato = update.message.text
    #if stato == 'Happy 😁' or stato == 'Neutral 😐':
    #	update.message.reply_text('Well, I am going to show you a dish...tell me what do you think 🤪')
    #	return RACCOMANDAZIONE
    #else:
    #	update.message.reply_text('I am going to show you a dish...')
    #	return RACCOMANDAZIONE
    #--------------INUTILE PER ORA----------------------

def raccomandazione(update: Update, context: CallbackContext) -> int:
    logger.info('ci sonoooo')
    
    user = update.message.from_user
    logger.info("Feeling of %s: %s", user.first_name, update.message.text)
    global stato 
    stato = update.message.text
    
    #MESSAGGIO "Elaborando...."
    update.message.reply_text('Processing...')
    
    #Prelevo piatto causale da fornire all'utente
    lunghezza = len(menu)
    from random import randint
    indiceCasuale = randint(0,lunghezza-1)
    
    global indicePiattoSelez
    global immaginePiattoSelez
    piattoCasuale = menu[indiceCasuale]
    indicePiattoSelez = indiceCasuale
    immaginePiattoSelez = piattoCasuale.immagine
    
    
    raccNome = 'I think you would like this pasta dish: '+piattoCasuale.nome
    raccIngr = 'Ingredients: '+stampaIngredienti(piattoCasuale.ingredienti)
    racc = fornisciRaccCorrispondente(piattoCasuale.numero) #'RACCOMANDAZIONE SCELTA CASUALMENTE TRA QUELLE DISPONIBILI PER QUESTO PIATTO'
    update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
    logger.info('IMMMMMMMMM %s',piattoCasuale.immagine)
    
    strImm = '/home/parallels/PastaMMCIS/'+piattoCasuale.immagine
    print(strImm)
    update.message.reply_photo(photo=open(str(strImm),'rb'))
    update.message.reply_text(raccIngr, reply_markup=ReplyKeyboardRemove())
    
    reply_keyboard = [['I like it'], ['I want something similar'], ['I want something different']]
    
    update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Do you enjoy this dish?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )       
    #utente riceve piatto e gli viene chiesto se : GLI PIACE, VUOLE ALTRO SIMILE, VUOLE TUTT'ALTRO -> BASANDOCI SULLA SIMILITUDINE VISIVA
    #dato piatto che mi piace, trovo il più simile      
    
    return MOSTRAALTRO

def ratings(update: Update, context: CallbackContext) -> int:
    
    #CASO B - 5 stelle
    rateUser = update.message.text
    lineaDaInserire=''
    
    if rateUser == '1️⃣':
        lineaDaInserire = 'CASO B - 1 stella'
    elif rateUser =='2️⃣':
        lineaDaInserire = 'CASO B - 2 stelle'
    elif rateUser =='3️⃣':
        lineaDaInserire = 'CASO B - 3 stelle'
    elif rateUser =='4️⃣':
        lineaDaInserire = 'CASO B - 4 stelle'
    elif rateUser =='5️⃣':
        lineaDaInserire = 'CASO B - 5 stelle'
        
        
    f = open("ratings.txt", "a")
    f.write(lineaDaInserire+'\n')
    f.close()
    
    update.message.reply_text('Thanks for your rating!', reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END
        
def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! Thanks you for using PastaBot! I hope we can talk again some day 😁', reply_markup=ReplyKeyboardRemove()
    )

    reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
    update.message.reply_text(
        'Please rate our service 😘',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    
    #return ConversationHandler.END
    return RATINGS

def getPiattoSimile(immaginePiatto):

    #ci teniamo urlPiatti per avere mappatura tra url e indice (posizione nel vettore urlPiatti che coirrisp a indice di colonna/riga im Matricesimilitudine)
    #ES. urlPiattoSelezionato = 'bowties-shrimp.jpg' -> Piatto.immagine
    
    #scandisco array urlPiatti per vedere il numero, 5° piatto INDICE 4
    indice = urlPiatti.index(immaginePiatto)

    #prelevo colonna da matrice similitudine
    colonnaSelezionata = matrixSimilarity[indice]

    colonnaSelezionata.pop(indice) #tolgo lo zero che non ci serve (imm =  a se stessa)
    min = 1
    indiceMin = 0
    cont = 0
    for elem in colonnaSelezionata:
        if elem <= min:
            min = elem
            indiceMin = cont
        cont = cont+1
    
     
    if indiceMin >= indice:
        #devo incrementare perchè considero lista contenente anche lo zero
        indiceMin = indiceMin+1

    #ottengo min -> ho l'url della foto e potrò prendere pIatto corrispondnete dal menu
    return indiceMin


def getPiattoDiverso(immaginePiatto):
    indice = urlPiatti.index(immaginePiatto)

    #prelevo colonna da matrice similitudine
    colonnaSelezionata = matrixSimilarity[indice]

    max = colonnaSelezionata[0]
    indiceMax = 0
    cont = 0
    for elem in colonnaSelezionata:
        if elem >= max:
            max = elem
            indiceMax = cont
        cont = cont+1
    
     
    

    #ottengo MAX -> ho l'url della foto e potrò prendere pIatto corrispondnete dal menu
    return indiceMax




def mostraAltro(update: Update, context: CallbackContext) -> int:
    
    
    print('ciao, sezione mostraaltro')
    global immaginePiattoSelez
    #indicePiattoSelez
    #immaginePiattoSelez
    
    
    risposta = update.message.text
    
    if risposta == 'I like it':
        update.message.reply_text('Nice! Thanks you for using PastaBot!',reply_markup=ReplyKeyboardRemove())
        #qui faccio rating e magari return 0 cosi evito eccezione
        reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
        update.message.reply_text('Please rate our service 😘',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),)
    
        #return 0
        return RATINGS
        
    elif risposta == 'I want something similar':
        indicePiattoSimile = getPiattoSimile(immaginePiattoSelez)
        urlImmagineDaMostrare = urlPiatti[indicePiattoSimile]
        immaginePiattoSelez = urlImmagineDaMostrare
    
    elif risposta == 'I want something different':
        indicePiattoDiverso = getPiattoDiverso(immaginePiattoSelez)
        urlImmagineDaMostrare = urlPiatti[indicePiattoDiverso]
        immaginePiattoSelez = urlImmagineDaMostrare
    
    
    #oRA IDENTIFICARE OGG PIATTO CORRISP A QUELL'INDIRIZZO
    piattoPrescelto = getPiattoByImg(urlImmagineDaMostrare)
    
    
    raccNome = piattoPrescelto.nome
    raccIngr = 'Ingredients: '+stampaIngredienti(piattoPrescelto.ingredienti)
    racc = fornisciRaccCorrispondente(piattoPrescelto.numero) #'RACCOMANDAZIONE SCELTA CASUALMENTE TRA QUELLE DISPONIBILI PER QUESTO PIATTO'
    update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
    strImm = '/home/parallels/PastaMMCIS/'+piattoPrescelto.immagine
    print(strImm)
    update.message.reply_photo(photo=open(str(strImm),'rb'))
    update.message.reply_text(raccIngr, reply_markup=ReplyKeyboardRemove())
    #update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
    
    
    #update.message.reply_text('Do you enjoy this pasta dish? Click /somethingelse if you want to see another one...\n\nType /cancel if you want to leave this conversation', reply_markup=ReplyKeyboardRemove())
    #return cccc
    reply_keyboard = [['I like it'], ['I want something similar'], ['I want something different']]
    
    update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
    update.message.reply_text('Do you enjoy this dish?',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))       
    #utente riceve piatto e gli viene chiesto se : GLI PIACE, VUOLE ALTRO SIMILE, VUOLE TUTT'ALTRO -> BASANDOCI SULLA SIMILITUDINE VISIVA
    #dato piatto che mi piace, trovo il più simile      
    
    return MOSTRAALTRO
    

def main() -> None:
    """Run bot"""
    
    creaMenu()
    creaMatrixRecomm()
    creaMatrixSimilitudine()
    #stampaMatr()
    #stampaMenu()
    
    #print(len(menu))
    #print(len(matrixRecomm))
    
    # Create the Updater and pass it the bot's token.
    updater = Updater("1867453248:AAF_1-hJUc709RP6Pmi5PycSZm_OxmMqV2g")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states FEELING, RACCOMANDAZIONE, MOSTRAALTRO -> possibile reiterazione negli statui
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RACCOMANDAZIONE: [MessageHandler(Filters.regex('^(Happy 😁|Neutral 😐|Sad ☹️|Angry 😡)$'), raccomandazione)],
            MOSTRAALTRO: [MessageHandler(Filters.regex('^(I like it|I want something similar|I want something different)$'), mostraAltro)],
            RATINGS: [MessageHandler(Filters.regex('^(1️⃣|2️⃣|3️⃣|4️⃣|5️⃣)$'),ratings)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
