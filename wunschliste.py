# -*- coding: utf-8 -*-


# %% Module

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time


# %% Seite konfigurieren

st.set_page_config(layout='wide')


# %% Funktionen

def seite_neu_laden():
    del st.session_state.wunschliste_df
    st.cache_data.clear()
    st.rerun()
    

# %% Passwort-Abfrage

if "passwort" not in st.session_state:
    s1, s2 = st.columns(2)
    passworteingabe = s1.text_input(
        label="...",
        label_visibility="collapsed",
        placeholder="Passwort eingeben"
    )
    if passworteingabe != "" or s2.button("OK"):
        if passworteingabe in [st.secrets.passwort, st.secrets.passwort_edit]:
            st.session_state.passwort = passworteingabe
            st.rerun()
        else:
            st.write("Passwort nicht korrekt...")
    st.stop()


# %% Titel und Hinweise schreiben

st.title("Wunschliste von Johannes")
st.markdown(
    """
    Falls du dich für einen Wunsch aus der Liste entschieden hast, trag bitte deinen Namen in das entsprechende Feld ein.\n
    Klicke anschließend auf **Speichern** am Ende dieser Seite.
    """
)


# %% Datenbank laden

if "wunschliste_df" not in st.session_state:
    conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    st.session_state.wunschliste_df = conn.read(worksheet="wunschliste").astype("string").fillna(" ")
    
wunschliste_df = st.session_state.wunschliste_df
wunschliste_bearbeitet_df = wunschliste_df.copy()
   

# %% ggf. Link-Button zur Emoji-Liste anzeigen

if st.session_state.passwort == st.secrets.passwort_edit:
    st.link_button("Emojis", "https://gist.github.com/rxaviers/7360908")


# %% alle Wünsche nacheinander auflisten

st.write("---")

key = 0
if st.session_state.passwort == st.secrets.passwort_edit:
    for index, zeile in wunschliste_bearbeitet_df.iterrows():
        wunschliste_bearbeitet_df.at[index, "Wunsch"] = st.text_input(
            label="Wunsch:",
            value=zeile["Wunsch"],
            key=key
        )
        key += 1
        wunschliste_bearbeitet_df.at[index, "Beschreibung"] = st.text_area(
            label="Beschreibung:",
            value=zeile["Beschreibung"],
            key=key
        )
        key += 1
        wunschliste_bearbeitet_df.at[index, "Link"] = st.text_input(
            label="Link:",
            value=zeile["Link"],
            key=key
        )
        key += 1
        st.write("---")
else:
    for index, zeile in wunschliste_bearbeitet_df.iterrows():
        st.subheader(zeile["Wunsch"])
        if zeile["Beschreibung"].strip() != "":
            st.markdown(zeile["Beschreibung"])
        if zeile["Link"].strip() != "":
            st.link_button("Details", zeile["Link"])
        s1, s2 = st.columns(2)
        wunschliste_bearbeitet_df.at[index, "wird verschenkt von"] = s1.text_input(
            label="wird verschenkt von:", 
            value=zeile["wird verschenkt von"],
            placeholder="", 
            key=key
            )
        key += 1
        st.write("---")
    

# %% Neuen Wunsch ergänzen (edit)

if st.session_state.passwort == st.secrets.passwort_edit:
    st.header("Wunsch ergänzen")
    wunsch = st.text_input(
        label="Wunsch:",
        placeholder=""
    )
    beschreibung = st.text_area(
        label="Beschreibung:",
        placeholder=""
    )
    link = st.text_input(
        label="Link:",
        placeholder=""
    )
    st.write("---")


# %% Speichern

if st.button("Speichern"):
    st.cache_data.clear()
    conn_neu = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    wunschliste_neu_eingelesen_df = conn_neu.read(worksheet="wunschliste").astype("string").fillna(" ")
    if not wunschliste_df.equals(wunschliste_neu_eingelesen_df):
        st.write(
            """
            Die Wunschliste wurde in der Zwischenzeit verändert.
            Deswegen wird die Seite neu geladen...
            """
        )
        time.sleep(3)
        seite_neu_laden()
    
    if st.session_state.passwort == st.secrets.passwort_edit:
        if wunsch != "":
            wunschliste_bearbeitet_df = pd.concat(
                (
                    wunschliste_bearbeitet_df, 
                    pd.DataFrame(
                        {
                            "Wunsch": [wunsch],
                            "Beschreibung": [beschreibung],
                            "Link": [link],
                            "wird verschenkt von": [" "]
                        }
                    )
                ),
                ignore_index=True
            )
        wunschliste_bearbeitet_df = wunschliste_bearbeitet_df[wunschliste_bearbeitet_df["Wunsch"] != ""]
        wunschliste_bearbeitet_df.fillna(
            " ",
            inplace=True
        )
            
    
    conn_neu.update(worksheet="wunschliste", data=wunschliste_bearbeitet_df)
    seite_neu_laden()
            