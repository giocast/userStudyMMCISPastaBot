import sys
sys.path.append('/usr/local/lib/python3.8/dist-packages')

indice = 3
print(indice)

if indice == 1:
    #somministro caso A
    exec(compile(open('caseA.py', "rb").read(), 'caseA.py', 'exec'))
elif indice == 2:
    #somministro caso B -> copia di botImageSimil -> similitudine tra immagini a partire da una casuale
    print('B')
    exec(compile(open('caseB.py', "rb").read(), 'caseB.py', 'exec'))
elif indice == 3:
    #somministro caso C -> piatto del giorno (con calcolo sul giorno attuale) e poi se non accettato interazione testuale
    print('C')
    exec(compile(open('caseC.py', "rb").read(), 'caseC.py', 'exec'))
    

#FILE per somministrare una delle strategie di comunicazione scelte per il chatbot
#
# Caso A:              Caso B:                Caso C:
# Int -> Text          Int -> Text+Visual     Int-> Text+Visua
# Process -> Text      Process -> Visual      Process -> Text
#
# N.B. Vogliamo ottenere una interazione di tipo Text+Visual (CASO C) proponendo inizialmente un menu del giorno (1 foto scelta con un calcolo basato sul giorno attuale) oppure con interazione testuale con domande like/dislike/intolerant


#nel relativo caso (file python che verrà lanciato) si andrà ad inserire rating finale di utente per il caso somministrato -> es inserisco riga CASO A - 5 stelle

#database di valutazioni OGNI RIGA rappresenta ESPERIENZA UTENTE SINGOLA...più righe per utenti che rilanciano bot e a cui magari capita caso differente (NO id utente salvati)
print('ciao')
