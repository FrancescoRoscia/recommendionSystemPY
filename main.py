from website import create_app # we can do this only because website is a Python package, because of the __init__.py

app = create_app()

if __name__ == '__main__': # we want to run the webServer only if we actually run this file
    app.run(debug=True) # debug = True means that when we make a change in our code, it will refresh the webServer