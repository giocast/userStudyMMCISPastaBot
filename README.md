# userStudyMMCISPastaBot
User study for Distributed System Course Project - Master Course of Software Engineering at Politecnico di Bari
(https://github.com/giocast/DistributedSystem-Project-PastaBot)

The aim of this project is producing a multimodal Pasta recommendation system (Pasta MMCIS).
After an intense research process, a Telegram bot has been developed using Telegram Chatbot python library.

SCENARIO: A multimodal recommendation systems allows the user to communicate with a chatbot which uses both text and images. After the communication process, the chatbot has to provide a pasta dish recommendation based on user preferences.


Two possibile interaction:
- Ingredients-oriented recommendation: provide a set of dishes by filtering the menu with respect of dishes ingredients (textual processing)
- Image-oriented recommendation: provide pasta dishes with a certain level of images mutual similarity (visual processing)


INGREDIENTS-ORIENTED RECOMMENDATION STEPS:
1) User emotion acquisition (ask for user actial mood: Happy 😁, Neutral 😐, Sad ☹️, Angry 😡)
2) User preferences acquisition (which ingredients the user likes, dislikes or is allergic to). This step is personalized according to the acquired mood
3) Recommendation based on preferences: identification and selection of pasta dishes of the menu which respect the provided conditions. Share with the user the name and image of the selected dish but also the ingredients and a friendly human-like recommendation.

IMAGE-ORIENTED RECOMMENDATION STEPS:
1) User emotion acquisition (ask for user actial mood: Happy 😁, Neutral 😐, Sad ☹️, Angry 😡)
2) Direct recommendation of a random dish of the menu. The user can accept it or ask for a similar dish or for a different one.
3) If the user ask for a new dish, a similarity algorithm identify the most similar or most different dish based on the dish images
4) Recommendation includes the name and image of the selected dish but also the ingredients and a friendly human-like recommendation.


# User study

The user study consists of somministrating 3 different chatbots to users and retrieve ratings for user satisfaction. 



Case A:
          Interaction -> Text
          Processing -> Text          
Case B: 
          Interaction -> Text+Visual
          Processing -> Visual                   
Case C:
          Interaction -> Text+Visual
          Processing -> Text
          
                 
CASE A
Textual conversation between user and chatbot. The chatbot asks questions in order to acquire user preferences. COnversation duration varies with user's mood. Preferences (ingr. liked, disliked or allergies) are used to filter the menu and recommend the perfect dish based on the tastes (the first element of the produced list of dishes). 

CASE B
Conversation with text and which starts with a random image recommendation. The user can acccept it or ask for a similar dish or for a different dish, which is selected using a image similarity algorithm. 

CASE C
Conversation with text which starts with the pasta dish of the day. If the user likes this dish the conversation ends. If he doesn't like it, a normal textual conversation starts (the bot asks questions and provide the first dish of the generated list). 


For each conversation a user rating is stored into a text file. It will be possible to identify which case is better in order to satisfy users' needs. 
