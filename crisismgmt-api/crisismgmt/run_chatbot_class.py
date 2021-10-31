
from chatbot_class import ChatBot
import breathing

def main():
    # Instantiation should handle setting up
    # reading from data.pickle, intents.json etc.
    chatbot = ChatBot()

    panic_flag = False

    # While loop outside of the class
    while True: 
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        if panic_flag == True and inp == "yes" or inp == "y":
            breathing.calmDown()
            panic_flag = False
            continue

        response, panic_flag = chatbot.send_message(inp, panic_flag)

        for msg in response:
            print(msg)

if __name__ == "__main__":
    main()
