import sys
import time
import threading
import itertools

from application.app import App, AppState

import db

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
    connection = db.connect("localhost", 27017)
    
    done = True
    # inject the connection
    AppState.set_connection(connection)


if __name__ == "__main__":
    connect_to_db()
    # create app
    app = App()
    # run mainloop
    app.run()
