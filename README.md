# userStudyMMCISPastaBot
User study for Distributed System Course Project - Master Degree at Politecnico di Bari
(https://github.com/giocast/DistributedSystem-Project-PastaBot)

Somministrate 3 different chatbots to users and retrieve ratings for user satisfaction. 


Case A:________Interaction -> Text__________Processing -> Text          
Case B:________Interaction -> Text+Visual___Processing -> Visual                   
Case C:________Interaction -> Text+Visual___Processing -> Text
          
                 

CASE A
Textual conversation between user and chatbot. The chatbot asks questions in order to acquire user preferences. COnversation duration varies with user's mood. Preferences (ingr. liked, disliked or allergies) are used to filter the menu and recommend the perfect dish based on the tastes (the first element of the produced list of dishes). 

CASE B
Conversation with text and which starts with a random image recommendation. The user can acccept it or ask for a similar dish or for a different dish, which is selected using a image similarity algorithm. 

CASE C
Conversation with text which starts with the pasta dish of the day. If the user likes this dish the conversation ends. If he doesn't like it, a normal textual conversation starts (the bot asks questions and provide the first dish of the generated list). 


For each conversation a user rating is stored into a text file. It will be possible to identify which case is better in order to satisfy users' needs. 
