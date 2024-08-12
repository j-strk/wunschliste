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
   

# %% st.data_editor anzeigen

# if st.session_state.passwort == st.secrets.passwort_edit:
#     column_order = ["Wunsch", "Link"]
#     disabled = []
# else:
#     column_order = wunschliste_df.columns.to_list()
#     disabled = ["Wunsch", "Link"]

# wunschliste_bearbeitet_df = st.data_editor(
#     wunschliste_df,
#     hide_index=True,
#     use_container_width=True,
#     column_order=column_order,
#     disabled=disabled,
#     column_config={
#         "Link": st.column_config.LinkColumn()#display_text="Hier klicken")
#     }
# )


# %% alle Wünsche nacheinander auflisten

st.write("---")

key = 0
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
    st.write("---")    #########################
    

# %% Neuen Wunsch ergänzen (edit)

if st.session_state.passwort == st.secrets.passwort_edit:
    st.write("---")
    st.header("Wunsch ergänzen")
    wunsch = st.text_input(
        label="Wunsch:",
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
        if [wunsch, link] != ["", ""]:
            wunschliste_bearbeitet_df = pd.concat(
                (
                    wunschliste_bearbeitet_df, 
                    pd.DataFrame(
                        {
                            "Wunsch": [wunsch],
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
            