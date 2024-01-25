#----------------
import sys
import time
import threading
import itertools
#----------------
import db
from persistance.refactoring import Client
#----------------
from application.app import App, AppState
#----------------

def connect_to_db():
    #done = False
    #thread = threading.Thread(target=animate)
    #thread.start()
    client = db.connect("localhost", 27017)
    #done = True
    # inject the connection
    Client.set_client(client)


if __name__ == "__main__":
    connect_to_db()
    # create app
    app = App()
    # run mainloop
    app.run()


# animation
def animate(done):
    for char in itertools.cycle(['', '.', '..', '...']):
        sys.stdout.write('\rConnecting to database. ' + char)
        sys.stdout.flush()
        time.sleep(0.1)
        if done: break
