from websocket import create_connection;

def main():
    url = 'ws://127.0.0.1:5001/echo'
    ws = create_connection(url)

    print()

    ws.send("Hello")
    response = ws.recv();
    ws.close()

if __name__ == '__main__':
    main();