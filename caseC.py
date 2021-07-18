import logging, csv

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
import numpy

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


FEELING, DOMANDELUNGHE, DOMANDECORTE, DOMANDELUNGHE2, DOMANDELUNGHE3, RACCOMANDAZIONE, PIATTOGIORNO, RATINGS = range(8)
stato = None
ingredientsLike = None
ingredientsDislike = None
allergies = None
menu = []
domandeCorteIndex = False
skipAllergieIndex = False
urlPiatti = []
arrayRacc = [] #copia del vettore racc utile per continuare in fase di scelta finale
indicePrescelto = 0 #indice di partenza per fase finale (array copia senza primo elemento già rifiutato dallutente

# possibile uso var globali: in qualsiasi parte del codice salvare preferenze utenti in file esterno
#idea profilare utenti salvando file con nome utente/codice utente (si possono reperire)->file strutturato, magari csv

matrixRecomm = []

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
    with open('datasetNew.csv') as csv_file:
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
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=False),
    )

    return PIATTOGIORNO

def piattoDelGiorno(update: Update, context: CallbackContext) -> int:
    
    #nel caso in cui utente non vuole piatto del giorno
    
    global stato 
    stato = update.message.text #prendo qui per poi scegliere tra domande lunghe e corte
    
    user = update.message.from_user
    logger.info("Feeling of %s: %s", user.first_name, update.message.text)
    
    #..............................................
    
    import datetime
    numeroOggi = datetime.datetime.today().day
    print('oggi')
    print(numeroOggi)
    
    lunghezza = len(menu)
    indiceCasuale = 0 #inizializzazione
    
    if numeroOggi < lunghezza:
        indiceCasuale = numeroOggi
    else:
        from random import randint
        indiceCasuale = randint(0,lunghezza-1)
    
    #prelevo piatto (numero del giorno o casuale se numero giorno maggiore o uguale lunghezza
    piattoCasuale = menu[indiceCasuale]
    indicePiattoSelez = indiceCasuale
    immaginePiattoSelez = piattoCasuale.immagine
    
    
    raccNome = 'Pasta dish of the day: '+piattoCasuale.nome
    raccIngr = 'Ingredients: '+stampaIngredienti(piattoCasuale.ingredienti)
    racc = fornisciRaccCorrispondente(piattoCasuale.numero) #'RACCOMANDAZIONE SCELTA CASUALMENTE TRA QUELLE DISPONIBILI PER QUESTO PIATTO'
    update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
    logger.info('IMMMMMMMMM %s',piattoCasuale.immagine)
    
    #strImm = '/home/giocast/pastaMMCIS_bot/'+urlPiatti[piattoCasuale.numero+1]
    strImm = '/home/parallels/PastaMMCIS/'+urlPiatti[indiceCasuale]
    print(strImm)
    update.message.reply_photo(photo=open(str(strImm),'rb'))
    update.message.reply_text(raccIngr, reply_markup=ReplyKeyboardRemove())
    
    reply_keyboard = [['I like this dish'], ['I do not like it']]
    
    update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Do you enjoy the pasta dish of the day?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )       
    
    
    
    #nota ora vado in feeling, che avrà già valore di stato, mentre prenderò valore di SI o NO per decidere se continuare o no conversazione
    
    #..............................................
    
    return FEELING

def statoAnimo(update: Update, context: CallbackContext) -> int:
    """Stores the selected feeling and and asks for information, with respect of the actual user feelling."""
    #user = update.message.from_user
    #logger.info("Feeling of %s: %s", user.first_name, update.message.text)
    
    
    #inserisco sezione del PIATTO DEL GIORNO (Visual interaaction)
    
    rispostaUser = update.message.text
    
    if rispostaUser == 'I like this dish':
        print('convintoutente')
        update.message.reply_text('See you, bye! Thanks for using PastaBot', reply_markup=ReplyKeyboardRemove())    
        #return 0
        reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
        update.message.reply_text('Please rate our service 😘',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),)
    
        #return ConversationHandler.END
        return RATINGS
    else:
        print('non convinto')
        #uso stato globale modificato sopra
        #global stato 
        #stato = update.message.text
        if stato == 'Happy 😁' or stato == 'Neutral 😐':
    	    update.message.reply_text('Let me ask a few questions!')
    	    update.message.reply_text('What are your favourite ingredients for a pasta dish?', reply_markup=ReplyKeyboardRemove())
    	    return DOMANDELUNGHE
        else:
    	    update.message.reply_text('What are your favourite ingredients for a pasta dish?', reply_markup=ReplyKeyboardRemove())
    	    return DOMANDECORTE

def domandeLunghePt1(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Ingredients liked by %s: %s", user.first_name, update.message.text)
    ingredients = update.message.text
    global ingredientsLike 
    ingredientsLike = ingredients.split(',') #utente che separa ingrediente finale con and
    ingredientsLike = [each_string.lower() for each_string in ingredientsLike] #lower case per evitare problemi uguaglianza
    ingredientsLike = [each_string.strip() for each_string in ingredientsLike] #rimozione di spazi che creano problemi prima e dopo delle stringhe
    #possibile errore da gestire: utente fesso che scrive ingredienti uguali->fix possibile rimuore l'elemento/i uguale/i
    update.message.reply_text('What ingredients you dislike?', reply_markup=ReplyKeyboardRemove())
    return DOMANDELUNGHE2
    
def domandeLunghePt2(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Ingredients disliked by %s: %s", user.first_name, update.message.text)
    global domandeCorteIndex
    domandeCorteIndex = False
    ingredients = update.message.text
    global ingredientsDislike 
    ingredientsDislike = ingredients.split(',')
    ingredientsDislike = [each_string.lower() for each_string in ingredientsDislike]
    ingredientsDislike = [each_string.strip() for each_string in ingredientsDislike]
    update.message.reply_text('Do you have any allergies or intolerances? Write specific ingredients or gluten or send /skip if you don\'t have any allergies.', reply_markup=ReplyKeyboardRemove())
    return RACCOMANDAZIONE
    
def raccomandazione(update: Update, context: CallbackContext) -> int:
    global allergies
    global arrayRacc
    logger.info("***** %s", domandeCorteIndex)
    
    #MESSAGGIO "Elaborando...."
    update.message.reply_text('Processing...', reply_markup=ReplyKeyboardRemove())
    
    if domandeCorteIndex:
        # domande corte
        
        #variabili utili
        filterMenuLike = []
        numeroIngrLike = len(ingredientsLike)
        logger.info("(corte) lunghezza ingre like %s",numeroIngrLike)
        
        for obj in menu:
            for i in range(0, numeroIngrLike):
                #confronto di ogni ingrLike con menu e tiro fuori nuova struttura
                # es. (a) elemento che mi piace
                if ingredientsLike[i] in obj.ingredienti:
                    print('tureeeee')
                    #controllo che il piatto inserito non sia già presente nella nuova struttura (ad esemoio per quanto riguarda caso: a c'è aggiungo, b (secondo inglIke) c'è e non va riaggiunto obj
                    if obj not in filterMenuLike:
                        filterMenuLike.append(obj)
                        break
                        #per evitare obj duplicati in lista uso break
                        #abbiamo il nostro filterMenuLike, che è una lista: devo ora filtrarla e togliere tutti piattoi che contengono degli ingrDislike
                else: #per evitare di perdere ingredienti che non rispettano correttamente nome (es tomato anzichè tomatoes), ritentiamo controllo di simulitudine per includere poatti che magari ingiustamente vengono rimossi
                    sonoEntrato = False
                    for elem in obj.ingredienti:
                        if similar(ingredientsLike[i], elem) >= 0.8:
                            filterMenuLike.append(obj)
                            sonoEntrato = True
                            break
                    if sonoEntrato == True:
                        break       
        print('FilterMenuLike:')
        stampaLista(filterMenuLike)
        #FASE DI ORDINAMENTO IN BASE AI GUSTI DELL'UTENTE, con l'biettivo di ottenere una lista ordinata in base ai gusti dell'utente: 
        #[Piatto1,Piatto2,Piatto3,....]
        
        #array di conteggi [conteggioIngredientiLikePerPiatto1, ....] -> lo ordino e alla fine ordino anche i piatti sulla base di ciò
        conteggiIngredientiLikeNeiPiattiDelMenuFiltrato = []
        
        for obj in filterMenuLike:
            sommaIngrPresenti = 0
            numeroIngrDelPiatto = len(obj.ingredienti) #prendo numero di ingredienti per ogni piatto [zucchini, tomatoes, ...]
            for i in range(0, numeroIngrDelPiatto):
                for ingredienteCheMiPiace in ingredientsLike: #es [a,b,c] CASO ERRORE: a,b,c sono scritti uguali dall'utente: verranno conteggiati
                    if ingredienteCheMiPiace == obj.ingredienti[i]: #a==zucchini (che sarebbe ingr[0])
                        sommaIngrPresenti = sommaIngrPresenti + 1 #nel caso corretto, questa può avvenire al massimo una volta per ogni ingrediente del menu
                    else:
                        #qui controllo similitudine del singolo ingrediente per evitrare di perdere ad es tomato che non è uguale a tomatoes
                        if similar(ingredienteCheMiPiace,obj.ingredienti[i]) >= 0.8:
                            sommaIngrPresenti = sommaIngrPresenti + 1 #nel caso corretto, questa può avvenire al massimo una volta per ogni ingrediente del menu
            conteggiIngredientiLikeNeiPiattiDelMenuFiltrato.append(sommaIngrPresenti)
        
        stampaVettore(conteggiIngredientiLikeNeiPiattiDelMenuFiltrato)
        #ORA abbiamo il vettore dei conteggi che serve per ordinare filterMenuLike
        #ORA ordinare filterMenuLike sulla base di conteggiIngredientiLikeNeiPiattiDelMenuFiltrato
        
        
        #vettoreRaccomandazione = [x for _,x in sorted(zip(conteggiIngredientiLikeNeiPiattiDelMenuFiltrato,filterMenuLike), reverse=True)]
        #SOLUZIONE A PROBLEMA: aggiungo attributo ad ogni oggetto (occorrenze) e poi faccio un sort su quell'attr
        for i in range(0,len(filterMenuLike)):
            setattr(filterMenuLike[i],'occorrenzeLikeIngr',conteggiIngredientiLikeNeiPiattiDelMenuFiltrato[i])
            
        #dopo aver aggiunto quell'attr, ordino tutti sulla base di quello
        
        vettoreRaccomandazione = sorted(filterMenuLike, key=attrgetter("occorrenzeLikeIngr"), reverse=True)
        
        print('vettoreRaccomandazione:')
        stampaLista(vettoreRaccomandazione)
        #propongo all'utente il primo piatto del vettoreRaccomandazione, stampando nome, ingredienti, immagine
        
        #check se vuota!
        
        if len(vettoreRaccomandazione) > 0:
            #MOSTRO PRIMO ELEMEMTNO DDEL VETTORE DI RACCOMANDAZIONI
            raccNome = 'I think you would like this pasta dish: '+vettoreRaccomandazione[0].nome
            raccIngr = 'Ingredients: '+stampaIngredienti(vettoreRaccomandazione[0].ingredienti)
            racc = fornisciRaccCorrispondente(vettoreRaccomandazione[0].numero) #'RACCOMANDAZIONE SCELTA CASUALMENTE TRA QUELLE DISPONIBILI PER QUESTO PIATTO'
            update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
            update.message.reply_photo(vettoreRaccomandazione[0].immagine)
            update.message.reply_text(raccIngr, reply_markup=ReplyKeyboardRemove())
            
            update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
            update.message.reply_text('Do you enjoy this dish? Click /somethingelse if you want another suggestion...\n\nType /cancel if you want to leave this conversation', reply_markup=ReplyKeyboardRemove())
            
            #salvo vettore raccomandazione
            #riciclato lo stato feeling (per qualche motivo, non concessa aggiunta di altri stati)
            
            arrayRacc = vettoreRaccomandazione
            cestino = arrayRacc.pop(0) #rimuovo primo elemento già mostrato all'utente e non gradito
            return FEELING
            
        else:
            logger.info('Non ho trovato piatto che rispetta richieste utente')
            update.message.reply_text('I am sorry. I did not find anything you would eat', reply_markup=ReplyKeyboardRemove())
    else:
        #per problemi logistici, ultima fase di domandeLunghe spostata qui (acquisizione valori allergie scritti da utente)
        
        
        #IMP: usare un indice globale per sapere se si è fatto SKIP ALLERGIES (skipAllergieIndex)
        allergies = []
        numeroAllergies = 0
        
        #se false, vuol dire che utente non ha skippato l'ultima domanda lunga
        if skipAllergieIndex == False:
            user = update.message.from_user
            logger.info("Allergies %s: %s", user.first_name, update.message.text)
            ingredientsAl = update.message.text
            allergies = ingredientsAl.split(',')
            allergies = [each_string.lower() for each_string in allergies]
            allergies = [each_string.strip() for each_string in allergies]
        
        #variabili utili
        filterMenuLike = []
        #andremo a filtrare ulteriormente filterMenuLike.
        
        
        #ingredientsLike, ingredientsDislike, allergies
        numeroIngrLike = len(ingredientsLike)
        logger.info("lunghezza ingre like %s",numeroIngrLike)
        numeroIngrDislike = len(ingredientsDislike)
        logger.info("lunghezza ingre dislike %s",numeroIngrDislike)
        
        if skipAllergieIndex == False:
            numeroAllergies = len(allergies)
            logger.info("lunghezza ingre all %s",numeroAllergies)
        
        for obj in menu:
            for i in range(0, numeroIngrLike):
                if ingredientsLike[i] in obj.ingredienti:
                    if obj not in filterMenuLike:
                        filterMenuLike.append(obj)
                        break
                else:
                    sonoEntrato = False
                    for elem in obj.ingredienti:
                        if similar(ingredientsLike[i], elem) >= 0.8:
                            filterMenuLike.append(obj)
                            sonoEntrato = True #boooleano per dife che hai fatto append (un solo brewak non basta per uscire da for grande)
                            break
                    #controllo sul booleano e break se si ED ESCO DAL FOR GRANDE (vado a obj/piatto successivo)
                    if sonoEntrato == True:
                        break
        print('FilterMenuLike:')
        stampaLista(filterMenuLike)
        
        #abbiamo filtermenuLike, ci occupiamo ORA di rimuovere piatti che contengono gli ingredientsDislike
        
        stampaVettore(ingredientsDislike)
        print('cccccccc')
        stampaVettore(ingredientsLike)
        
        #scansiono lista al contrario per FIXARE PROBLEMA CON REMOVE DI OGG IN LISTA DURANTE ITERAZIONE! -| uso reversed(lista)
        
        for obj in reversed(filterMenuLike):
            print('xxxxx')
            print('Oggetto numero ',obj.numero)
            for i in range(0, numeroIngrDislike):
                print('Indice iterazione ',i)
                if ingredientsDislike[i] in obj.ingredienti:
                    filterMenuLike.remove(obj) #rimuovo piatto che ha almeno 1 ingrediente che non mi piace
                    print('Rimuovo oggetto contenente ingrediente',obj,obj.numero,ingredientsDislike[i])
                    break
                else:
                    sonoEntrato = False
                    for elem in obj.ingredienti:
                        if similar(ingredientsDislike[i], elem) >= 0.8:
                            filterMenuLike.remove(obj) #mi basta che c'è un ingrediente che non mi piace per scartare piatto
                            print('Rimuovo DA SIMIL oggetto contenente ingrediente',obj,obj.numero,ingredientsDislike[i])
                            sonoEntrato = True
                            break
                    if sonoEntrato == True:
                        break        
        print('FilterMenuLike after IngrDislikeFiltering:')
        stampaLista(filterMenuLike)
        
        #continuo a filtrare filtermenulike solo se non è stato fatto skip
        
        if skipAllergieIndex == False:
            for obj in reversed(filterMenuLike):
                for i in range(0, numeroAllergies):
                    if allergies[i] == 'gluten' or similar(allergies[i],'gluten') >= 0.8:
                        glutenSi = False
                        for elem in obj.tag:
                            if elem == 'Gluten Free' or similar(elem,'Gluten Free') >= 0.8:
                                #qui situazione ok
                                glutenSi = True
                        
                        if glutenSi == False: 
                            #rimuovo perchè non contiene tag gliuten free
                            filterMenuLike.remove(obj)
                            break
                    else:
                        #non ho scritto gluten, lavoro con ingredienti che ho scritto
                        if allergies[i] in obj.ingredienti:
                            filterMenuLike.remove(obj) #rimuovo piatto che ha almeno 1 ingrediente a cui sono allergico
                            break
                        else:
                            for elem in obj.ingredienti:
                                if similar(allergies[i], elem) >= 0.8:
                                    filterMenuLike.remove(obj) #mi basta che c'è un ingrediente che non mi piace per scartare piatto
                                    break
                            
            print('FilterMenuLike after AllergiesFiltering:')
            stampaLista(filterMenuLike)    
        
        #------------------------------------raccomando con o senza allergies---------------------------------------
        #FASE DI ORDINAMENTO IN BASE AI GUSTI DELL'UTENTE, con l'biettivo di ottenere una lista ordinata in base ai gusti dell'utente: 
        #[Piatto1,Piatto2,Piatto3,....]
            
        #array di conteggi [conteggioIngredientiLikePerPiatto1, ....] -> lo ordino e alla fine ordino anche i piatti sulla base di ciò
        conteggiIngredientiLikeNeiPiattiDelMenuFiltrato = []
            
            
        for obj in filterMenuLike:
            sommaIngrPresenti = 0
            numeroIngrDelPiatto = len(obj.ingredienti)
            for i in range(0, numeroIngrDelPiatto):
                for ingredienteCheMiPiace in ingredientsLike:
                    if ingredienteCheMiPiace == obj.ingredienti[i]:
                        sommaIngrPresenti = sommaIngrPresenti + 1
                    else:
                        if similar(ingredienteCheMiPiace,obj.ingredienti[i]) >= 0.8:
                            sommaIngrPresenti = sommaIngrPresenti + 1
            conteggiIngredientiLikeNeiPiattiDelMenuFiltrato.append(sommaIngrPresenti)
        
        stampaVettore(conteggiIngredientiLikeNeiPiattiDelMenuFiltrato)
            
        #ORA abbiamo il vettore dei conteggi che serve per ordinare filterMenuLike
        #ORA ordinare filterMenuLike sulla base di conteggiIngredientiLikeNeiPiattiDelMenuFiltrato
            
        for i in range(0,len(filterMenuLike)):
            setattr(filterMenuLike[i],'occorrenzeLikeIngr',conteggiIngredientiLikeNeiPiattiDelMenuFiltrato[i])
                
        #dopo aver aggiunto quell'attr, ordino tutti sulla base di quello
        
        vettoreRaccomandazione = sorted(filterMenuLike, key=attrgetter("occorrenzeLikeIngr"), reverse=True)
        
        print('vettoreRaccomandazione:')
        stampaLista(vettoreRaccomandazione)
            
        #propongo all'utente il primo piatto del vettoreRaccomandazione, stampando nome, ingredienti, immagine
        
        #check se vuota!
            
        if len(vettoreRaccomandazione) > 0:
            #MOSTRO PRIMO ELEMEMTNO DDEL VETTORE DI RACCOMANDAZIONI
            raccNome = 'I think you would like this pasta dish: '+vettoreRaccomandazione[0].nome
            raccIngr = 'Ingredients: '+stampaIngredienti(vettoreRaccomandazione[0].ingredienti)
            racc = fornisciRaccCorrispondente(vettoreRaccomandazione[0].numero)#'RACCOMANDAZIONE SCELTA CASUALMENTE TRA QUELLE DISPONIBILI PER QUESTO PIATTO'
            update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
            update.message.reply_photo(vettoreRaccomandazione[0].immagine)
            update.message.reply_text(raccIngr, reply_markup=ReplyKeyboardRemove())
            
            
            update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
            update.message.reply_text('Do you enjoy this  dish? Click /somethingelse if you want another suggestion...\n\nType /cancel if you want to leave this conversation', reply_markup=ReplyKeyboardRemove())
            
            #salvo vettore raccomandazione
            #riciclato lo stato feeling (per qualche motivo, non concessa aggiunta di altri stati)
            arrayRacc = vettoreRaccomandazione
            cestino = arrayRacc.pop(0) #rimuovo primo elemento già mostrato all'utente e non gradito
            return FEELING
            
        else:
            logger.info('Non ho trovato piatto che rispetta richieste utente')
            update.message.reply_text('I am sorry. I did not find anything you would eat', reply_markup=ReplyKeyboardRemove())
    
    return 0
     
def skip_allergie(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s isn't allergic.", user.first_name)
    logger.info("aaaaaaaaaaaaaaaaaaaaaaaaa")
    global domandeCorteIndex
    domandeCorteIndex = False
    global skipAllergieIndex
    skipAllergieIndex = True
    return RACCOMANDAZIONE
    
def domandeCorte(update: Update, context: CallbackContext) -> int:
    global domandeCorteIndex
    domandeCorteIndex = True
    user = update.message.from_user
    logger.info("(Corte) Ingredients liked by %s: %s", user.first_name, update.message.text)
    ingredients = update.message.text
    global ingredientsLike
    ingredientsLike = ingredients.split(',')
    ingredientsLike = [each_string.lower() for each_string in ingredientsLike]
    ingredientsLike = [each_string.strip() for each_string in ingredientsLike]
    #possibile errore da gestire: utente fesso che scrive ingredienti uguali->fix possibile rimuore l'elemento/i uguale/i
    logger.info("BBBBBBBBBBBBB")
    logger.info("---- %s", domandeCorteIndex)
    raccomandazione(update, context)
    return 0   
        
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

def ratings(update: Update, context: CallbackContext) -> int:
    
    #CASO C - 5 stelle
    rateUser = update.message.text
    lineaDaInserire=''
    
    if rateUser == '1️⃣':
        lineaDaInserire = 'CASO C - 1 stella'
    elif rateUser =='2️⃣':
        lineaDaInserire = 'CASO C - 2 stelle'
    elif rateUser =='3️⃣':
        lineaDaInserire = 'CASO C - 3 stelle'
    elif rateUser =='4️⃣':
        lineaDaInserire = 'CASO C - 4 stelle'
    elif rateUser =='5️⃣':
        lineaDaInserire = 'CASO C - 5 stelle'
        
        
    f = open("ratings.txt", "a")
    f.write(lineaDaInserire+'\n')
    f.close()
    
    update.message.reply_text('Thanks for your rating!', reply_markup=ReplyKeyboardRemove())
    
    return ConversationHandler.END

def mostraAltro(update: Update, context: CallbackContext) -> int:
    print('ciao, sono fase finale di visione dellintero menuraccomandazione')
    global indicePrescelto
    
    if indicePrescelto < len(arrayRacc):
    
        piattoPrescelto = arrayRacc[indicePrescelto]
    
    
    
        raccNome = piattoPrescelto.nome
        raccIngr = 'Ingredients: '+stampaIngredienti(piattoPrescelto.ingredienti)
        racc = fornisciRaccCorrispondente(piattoPrescelto.numero) #'RACCOMANDAZIONE SCELTA CASUALMENTE TRA QUELLE DISPONIBILI PER QUESTO PIATTO'
        update.message.reply_text(raccNome, reply_markup=ReplyKeyboardRemove())
        update.message.reply_photo(piattoPrescelto.immagine)
        update.message.reply_text(raccIngr, reply_markup=ReplyKeyboardRemove())
        update.message.reply_text(racc,reply_markup=ReplyKeyboardRemove())
    
    
    
        update.message.reply_text('Do you enjoy this pasta dish? Click /somethingelse if you want to see another one...\n\nType /cancel if you want to leave this conversation', reply_markup=ReplyKeyboardRemove())
    
        
        indicePrescelto = indicePrescelto + 1
    
    
        return FEELING
    else:
        update.message.reply_text('Sorry, I have no more options based on the received information ...', reply_markup=ReplyKeyboardRemove())
        #return 0
        reply_keyboard = [['1️⃣'], ['2️⃣'], ['3️⃣'], ['4️⃣'], ['5️⃣']]
        update.message.reply_text('Please rate our service 😘',reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),)
        return RATINGS
    return 0
    

def main() -> None:
    """Run bot"""
    
    creaMenu()
    creaMatrixRecomm()
    
    global urlPiatti
    f = numpy.loadtxt("immagini piatti.txt", dtype=str) #skiprows=1 se voglio togliere header
    urlPiatti = list(f)
    
    for el in urlPiatti:
        print(el+'-----')
    
    #stampaMatr()
    #stampaMenu()
    
    #print(len(menu))
    #print(len(matrixRecomm))
    
    # Create the Updater and pass it the bot's token.
    updater = Updater("1867453248:AAF_1-hJUc709RP6Pmi5PycSZm_OxmMqV2g")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states FEELING, DOMANDELUNGHE, DOMANDELUNGHE2, DOMANDELUNGHE3, DOMANDECORTE, RACCOMANDAZIONE -> possibile reiterazione negli statui
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PIATTOGIORNO: [MessageHandler(Filters.regex('^(Happy 😁|Neutral 😐|Sad ☹️|Angry 😡)$'), piattoDelGiorno)],
            FEELING: [MessageHandler(Filters.regex('^(I like this dish|I do not like it)$'),statoAnimo),CommandHandler('somethingelse', mostraAltro)],
            DOMANDELUNGHE: [MessageHandler(Filters.text, domandeLunghePt1)],
            DOMANDELUNGHE2: [MessageHandler(Filters.text, domandeLunghePt2), CommandHandler('skip', skip_allergie)],
            DOMANDECORTE : [MessageHandler(Filters.text, domandeCorte)],
            RACCOMANDAZIONE: [MessageHandler(Filters.text, raccomandazione)],
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
