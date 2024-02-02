#----------------
import sys
import time
import threading
import itertools
#----------------
import db
from application.client import Client
#----------------
from application.app import App
#----------------

def connect_to_db():
    done = False
    # animation
    def animate():
        for char in itertools.cycle(['', '.', '..', '...']):
            sys.stdout.write('\rConnecting to database. ' + char)
            sys.stdout.flush()
            time.sleep(0.1)
            if done: break
    thread = threading.Thread(target=animate)
    thread.start()
    client = db.connect("localhost", 27017)
    done = True
    # inject the client
    Client().set_client(client)


if __name__ == "__main__":
    connect_to_db()
    # create app
    app = App()
    # run mainloop
    app.run()
