import time
import asyncio
from telethon.sync import TelegramClient
from fastapi import FastAPI

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def list_chats(self):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w")
        # Print information about each chat
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")

        chats_file.close()
        print("List of groups printed successfully!")

    async def forward_messages_to_groups(self, source_chat_ids, destination_group_ids, keywords):
        await self.client.connect()

        # Ensure you're authorized
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            await self.client.sign_in(self.phone_number, input('Enter the code: '))

        last_message_ids = {chat_id: (await self.client.get_messages(chat_id, limit=1))[0].id for chat_id in source_chat_ids}

        while True:
            print("Checking for messages and forwarding them...")
            for source_chat_id in source_chat_ids:
                # Get new messages since the last checked message for the current chat
                messages = await self.client.get_messages(source_chat_id, min_id=last_message_ids[source_chat_id], limit=None)

                for message in reversed(messages):
                    # Check if the message text includes any of the keywords
                    if keywords:
                        if message.text and any(keyword in message.text.lower() for keyword in keywords):
                            print(f"Message from {source_chat_id} contains a keyword: {message.text}")

                            # Forward the message to all destination groups
                            for destination_group_id in destination_group_ids:
                                await self.client.send_message(destination_group_id, message.text)
                                print(f"Message forwarded to group {destination_group_id}")

                    else:
                        # Forward the message to all destination groups
                        for destination_group_id in destination_group_ids:
                            await self.client.send_message(destination_group_id, message.text)
                            print(f"Message forwarded to group {destination_group_id}")

                    # Update the last message ID for the current source chat
                    last_message_ids[source_chat_id] = max(last_message_ids[source_chat_id], message.id)

            # Add a delay before checking for new messages again
            await asyncio.sleep(5)  # Adjust the delay time as needed


# Function to read credentials from file
def read_credentials():
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = int(lines[0].strip())  # Ensure this is converted to int
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials file not found.")
        return None, None, None
    except ValueError:
        print("Invalid API ID format. Please ensure it's an integer.")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(f"{api_id}\n")
        file.write(f"{api_hash}\n")
        file.write(f"{phone_number}\n")

async def main():
    # Attempt to read credentials from file
    api_id, api_hash, phone_number = read_credentials()
    
    print(f"API ID: {api_id}, API Hash: {api_hash}, Phone Number: {phone_number}")  # Debugging line
    
    # If credentials not found in file, prompt the user to input them
    if api_id is None or api_hash is None or phone_number is None:
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)

    print("Choose an option:")
    print("1. List Chats")
    print("2. Forward Messages")

    choice = input("Enter your choice: ")

    if choice == "1":
        await forwarder.list_chats()
    elif choice == "2":
        # Prompt for the number of source groups
        num_sources = int(input("How many source groups do you want to fetch messages from? "))
        source_chat_ids = []

        for i in range(num_sources):
            chat_id = int(input(f"Enter the source chat ID {i + 1}: "))
            source_chat_ids.append(chat_id)

        # Prompt for the number of destination groups
        num_destinations = int(input("How many destination groups do you want to send messages to? "))
        destination_group_ids = []

        for i in range(num_destinations):
            group_id = int(input(f"Enter the destination group ID {i + 1}: "))
            destination_group_ids.append(group_id)

        print("Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
        keywords = input("Put keywords (comma separated if multiple, or leave blank): ").split(",")

        await forwarder.forward_messages_to_groups(source_chat_ids, destination_group_ids, keywords)
    else:
        print("Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())
