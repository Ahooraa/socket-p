import io
import socket
import threading

import pandas as pd


def receive_messages(client_socket):
    buffer = ""
    while True:
        try:
            # Receive and decode a chunk of data
            response = client_socket.recv(4096).decode('utf-8')

            if not response:  # If no more data is received, break
                break

            buffer += response  # Append the chunk to the buffer

            if "END_OF_DATA" in buffer:
                buffer = buffer.replace("END_OF_DATA", "")  # Remove the signal

                if buffer.startswith("DATAFRAME:"):
                    csv_data = buffer[len("DATAFRAME:"):]  # Extract the CSV part
                    df = pd.read_csv(io.StringIO(csv_data))
                    print("Received DataFrame:")
                    print(df)
                elif buffer.startswith("TEXT:"):
                    text_message = buffer[len("TEXT:"):]  # Extract the text part
                    print("Received message:", text_message)
                    if "chat ended" in text_message:
                        break
                else:
                    print(f"Unknown message format: {type(buffer)} received")
                    print(buffer)

                buffer = ""  # Clear the buffer after processing

        except Exception as e:
            print(f"Error: {e}")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 5555))

    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.start()


    print("Enter your message or type 'finish' to end the chat:")
    while True:
        command = input()
        if command.lower() !="get records":
            client.send(command.encode("utf-8"))
        if command.lower() == "finish":
            client.shutdown(socket.SHUT_WR) # Stop sending data to the server
            break
        elif command.lower() == "get records":
            print("please enter indexes of the records you want:")
            indexes = input()
            message= "INDEXES:"+indexes
            client.send(message.encode("utf-8"))
    thread.join()  # Wait for the receive thread to finish before closing the socket
    client.close()


if __name__ == "__main__":
    main()
