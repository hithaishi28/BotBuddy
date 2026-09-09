import os

from groq import Groq

# Read the API key from the environment.
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY environment variable not set. "
        'Run in PowerShell: $env:GROQ_API_KEY = "your-key-here"'
    )

# Initialize Groq client
client = Groq(api_key=api_key)

# Select model
model = "openai/gpt-oss-120b"

# Chat function
def chat():

    # Welcome message
    print("Welcome to the chatbot! Type 'exit', 'quit', or 'end' to exit.")
    
    # Conversation history (list)
    conversation_history = []

    # Inifinite loop
    while True:
    
        # User input
        user_input = input("You: ")

        # Check for the exit condition (exit, quit, end)
        if user_input.lower() in ["exit", "quit", "end"]:
            print("Chatbot: Goodbye!")
            break

        # Add user input to conversation history
        conversation_history.append({"role": "user", "content": user_input})

        # Build a prompt using conversation history
        try:

            # Get the Groq response
            response = client.chat.completions.create(
                model=model,
                messages=conversation_history,
                max_tokens=150,
                temperature=0.7,
            )

            # extract the output text
            ai_output = response.choices[0].message.content

            # print the output text
            print(f"Chatbot: {ai_output}")

            # add the ai message into the conversation history as an object with a role
            conversation_history.append({"role": "assistant", "content": ai_output})

        except Exception as e:

            # Add an exception message
            print(f"AI: Sorry, I encountered an error: {str(e)}")

# run the chatbot
if __name__ == "__main__":
    chat()