import streamlit as st

if not hasattr(st, 'already_started_server'):
    # Hack the fact that Python modules (like st) only load once to
    # keep track of whether this file already ran.
    st.already_started_server = True

    st.write('''
        The first time this script executes it will run forever because it's
        running a Flask server.

        Just close this browser tab and open a new one to see your Streamlit
        app.
    ''')


    from flask import Flask, render_template

    app = Flask(__name__, template_folder='./')
    #app.debug = True

    @app.route('/map')
    def show_map():
        return render_template('map.html')

    app.run(debug=True, port=5000)