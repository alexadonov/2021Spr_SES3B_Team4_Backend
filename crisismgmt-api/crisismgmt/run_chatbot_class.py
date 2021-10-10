
from chatbot import ChatBot

def main():
    # Instantation should hand setting up
    # reading from data.pickle, intents.json etc.
    chatbot = ChatBot()

    # While loop outside of the class
    while True: 
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        response = chatbot.send_message(inp)

        print(response)

if __name__ == "__main__":
    main()
