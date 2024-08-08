# -*- coding: utf-8 -*-


# %% Module

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time


# %% Seite konfigurieren

st.set_page_config(layout='wide')


# %% Passwort-Abfrage

@st.dialog("Passwort eingeben")
def passwortabfrage():
    passworteingabe = st.text_input(label="...", label_visibility="collapsed")
    if passworteingabe in [st.secrets.passwort, st.secrets.passwort_edit]:
        st.session_state.passwort = passworteingabe
        st.rerun()
    
if "passwort" not in st.session_state:
    passwortabfrage()


# %% Titel und Hinweise schreiben

st.title("Wunschliste von Johannes")
st.write(
    """
    Falls du dich für einen Wunsch aus der Liste entschieden hast, trag bitte deinen Namen in der entsprechenden Zeile ein.\n
    Klicke anschließend auf "Speichern" am Ende dieser Seite.
    """
)


# %% Datenbank laden

if "wunschliste_df" not in st.session_state:
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    st.session_state.wunschliste_df = conn.read(worksheet="wunschliste")
    

# %% st.data_editor anzeigen

wunschliste_bearbeitet_df = st.data_editor(
    st.session_state.wunschliste_df,
    hide_index=True,
    use_container_width=True,
    disabled=["Wunsch", "Link"],
    column_config={"Link": st.column_config.LinkColumn(display_text="Hier klicken")}
)



# %% Speichern

if st.button("Speichern"):
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    wunschliste_erneut_eingelesen_df = conn.read(worksheet="wunschliste")
    if not st.session_state.wunschliste_df.equals(wunschliste_erneut_eingelesen_df):
        st.write(
            """
            Die Wunschliste wurde in der Zwischenzeit verändert.
            Deswegen wird die Seite neu geladen...
            """
        )
        del st.session_state.wunschliste_df
        time.sleep(3)
        st.rerun()
    conn.update(worksheet="Tabellenblatt1", data=wunschliste_bearbeitet_df)
            