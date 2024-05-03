from blogApp import createApp

app = createApp()

#this will only run when app.py is run directly using python.
#it will not run if this file is imported in another module, because then __name__ is not __main__
if __name__ == '__main__':
    app.run(debug = True)