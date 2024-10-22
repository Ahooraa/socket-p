import socket
import threading
import os
import pandas as pd
import numpy as np
# Create a directory for chat logs if it doesn't exist
if not os.path.exists("./chat_logs"):
    os.makedirs("./chat_logs")

clients = {}
client_count = 0
active_clients = 0  # Track the number of active clients

def send_dataframe(client_socket, df):
    df_csv= df.to_csv(index=False)
    message= "DATAFRAME:"+ df_csv
    client_socket.send(message.encode("utf-8"))
    client_socket.send("END_OF_DATA".encode("utf-8"))
def send_text(client_socket, text):
    message= "TEXT:" + text
    client_socket.send(message.encode("utf-8"))
    client_socket.send("END_OF_DATA".encode("utf-8"))

def handle_client(client_socket, client_id, user_records):
    global clients, active_clients
    log_file_path = f"chat_logs/client_{client_id}_chat_log.txt"

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if message:
                if message.lower() == "finish":
                    share_after_finish(client_id, user_records)
                    send_text(client_socket,"Chat ended. you can exit now")
                    break
                elif message.lower() == "hello":
                    send_text(client_socket,"Hi, how are you?")
                elif message.lower() == "clients":
                    send_text(client_socket,get_client_stats())
                elif message.lower() == "all":
                    send_dataframe(client_socket, user_records)
                elif message.lower() == "available":
                   send_dataframe(client_socket,get_client_records(0, user_records)) # client =0 shows server's records
                elif message.lower() == "retrieve":
                    # Generate an array of random indices
                    random_indices = np.random.randint(1, len(user_records), size=1000)
                    user_records.iloc[random_indices, user_records.columns.get_loc('client')] = client_id
                    print(f"random records were allocated to client{client_id}")
                    send_text(client_socket,"These are your records")
                    send_dataframe(client_socket, get_client_records(client_id, user_records))
                elif message.lower() == "my records":
                    send_dataframe(client_socket, get_client_records(client_id, user_records))
                elif message.startswith("others") : # the user enters a message like this: "others 3". and the server returns records of user3
                    try:
                        other_client_id= int(message.split(" ")[1])
                        send_text(client_socket, f"records allocated to client{other_client_id} are as follows:")
                        send_dataframe(client_socket, get_client_records(other_client_id, user_records))
                    except ValueError:
                        send_text(client_socket, "there is a probability that you've entered a non-integer value after writing 'others'")
                        continue
                    except IndexError:
                        send_text(client_socket, "Index error! try again")
                        continue
                elif message.startswith("IDS:") :
                    ids= message[len("IDS:"):] # Extract the string containing ids seperated by ,
                    ids_ls= ids.split(",")
                    for i, value in enumerate(ids_ls):
                        ids_ls[i] = f"'{value}'"

                    user_records.loc[user_records["'id'"].isin(ids_ls), 'client']= client_id
                    filtered_records = user_records[user_records["'id'"].isin(ids_ls)]
                    send_text(client_socket,"now those records are allocated to you")
                    send_dataframe(client_socket, filtered_records)

                else:
                    log_chat(log_file_path, f"Client[{client_id}]: {message}")
            else:
                break

        except Exception as e:
            print(f'error with client{client_id}: exception:{e}')
            break

    client_socket.close()
    del clients[client_id]
    active_clients -= 1  # Decrease active client count
    print(f"Client[{client_id}] disconnected.")
    print(get_client_stats())

    # Check if there are no active clients left
    if active_clients == 0:
        print("No active clients left. Closing server.")
        shutdown_server()

def log_chat(log_file_path, message):
    with open(log_file_path, "w") as log_file:  # Overwrite log file for each new chat
        log_file.write(message + "\n")

def load_data_from_csv(csv_file):
    records = pd.read_csv(csv_file)
    records.loc[:,"client"]= 0
    return records

def get_client_stats():
    global clients, active_clients, client_count
    return f'clients: {clients} \nactive clients: {active_clients} \nclients count: {client_count}'

def get_client_records(user_id, user_records):
    return user_records[user_records['client'] == user_id]

def share_after_finish(client_id, user_records):
    global clients, active_clients
    remaining_clients= clients.copy()
    remaining_clients.pop(client_id)
    if len(remaining_clients) > 0:
        number_of_records_to_share = len(user_records[user_records['client'] == client_id].index)
        records_per_client = number_of_records_to_share / (active_clients -1)
        remainder = number_of_records_to_share % (active_clients-1)
        for id,client in remaining_clients.items():
            if id != client_id:
                user_records.loc[user_records[user_records['client'] == client_id].index[:int(records_per_client)], 'client'] = id
        #allocates the remaining rows of records to the first client in the remaining_clients list
        user_records.loc[user_records[user_records['client'] == client_id].index[:int(remainder)], 'client'] = list(remaining_clients.keys())[0]
        print(f"records of user {client_id} were shared between clients with IDs {list(remaining_clients.keys())}")
    elif len(remaining_clients) == 0:
        user_records.loc[user_records['client'] == client_id, 'client'] = 0 #allocate records back to the server
        print(f"records of user {client_id} were returned back to the server")


def shutdown_server():
    for client_socket in clients.values():
        client_socket.close()
    print("Server socket closed.")
    exit(0)  # Exit the server application


def main():
    global client_count, active_clients
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)
    csv_file = './RandomData.csv'
    user_records= load_data_from_csv(csv_file)
    print("Server listening on port 5555")

    while True:
        client_socket, addr = server.accept()
        client_count += 1
        client_id = client_count
        clients[client_id] = client_socket
        active_clients += 1  # Increase active client count

        print(f"Accepted connection from {addr}, assigned client ID: {client_id}")
        thread = threading.Thread(target=handle_client, args=(client_socket, client_id, user_records))
        thread.start()


if __name__ == "__main__":
    main()
