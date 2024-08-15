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
    passworteingabe = passworteingabe.strip()
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

conn = st.connection("gsheets", type=GSheetsConnection, ttl=5)
if "wunschliste_df" not in st.session_state:
    st.session_state.wunschliste_df = conn.read(worksheet="wunschliste").astype("string").fillna("")
    
wunschliste_df = st.session_state.wunschliste_df
wunschliste_bearbeitet_df = wunschliste_df.copy()
   

# %% ggf. Link-Button zur Emoji-Liste anzeigen

if st.session_state.passwort == st.secrets.passwort_edit:
    st.link_button("Emojis", "https://gist.github.com/rxaviers/7360908")


# %% Dictionary definieren, in das ggf. die Inidzes gespeichert werden, bei denen die Namen gelöscht werden sollen
#    Form: {index: Name, ...}

if "namensloeschung_dct" not in st.session_state:
    st.session_state.namensloeschung_dct = {}


# %% Toggle Button einfügen, der festlegt, ob nur offene Wünsche oder alle angezeigt werden sollen

st.write("  ")
nur_offene_wuensche_anzeigen = st.toggle(
    label="Nur Wünsche anzeigen, die von niemandem ausgewählt wurden",
    value=True
)    


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
        if nur_offene_wuensche_anzeigen and zeile["Name"].strip() != "":
            continue
        
        st.subheader(zeile["Wunsch"])
        if zeile["Beschreibung"].strip() != "":
            st.markdown(zeile["Beschreibung"])
        if zeile["Link"].strip() != "":
            st.link_button("Details", zeile["Link"])
        if zeile["Name"].strip() == "":
            s1, s2 = st.columns(2)
            wunschliste_bearbeitet_df.at[index, "Name"] = s1.text_input(
                label="Name:", 
                value=zeile["Name"], 
                key="text_input_name_" + str(index)
            )
        else:
            st.write(":warning: Dieser Wunsch wurde schon von jemandem ausgewählt!")
            s1, s2 = st.columns(2)
            expanded = True if index in st.session_state.namensloeschung_dct.keys() else False
            with s1.expander("Ich hab's mir anders überlegt", expanded=expanded):
                st.session_state.namensloeschung_dct[index] = st.text_input(
                    label="Name:",
                    value="",
                    key="text_input_namensloeschung_" + str(index)
                )
                st.markdown("Nach einem Klick auf **Speichern** (unten) wird deine Auswahl gelöscht")
                    
        st.write("---")
    

# %% Neuen Wunsch ergänzen (edit)

if st.session_state.passwort == st.secrets.passwort_edit:
    st.header("Wunsch ergänzen")
    wunsch = st.text_input(
        label="Wunsch:",
        value=""
    )
    beschreibung = st.text_area(
        label="Beschreibung:",
        value=""
    )
    link = st.text_input(
        label="Link:",
        value=""
    )
    st.write("---")


# %% Speichern

if st.button("Speichern", type="primary"):
    st.cache_data.clear()
    conn_neu = st.connection("gsheets", type=GSheetsConnection, ttl=5)
    wunschliste_neu_eingelesen_df = conn_neu.read(worksheet="wunschliste").astype("string").fillna("")
    if not wunschliste_df.equals(wunschliste_neu_eingelesen_df):
        st.write(
            """
            Die Wunschliste wurde in der Zwischenzeit verändert.
            Deswegen wird die Seite neu geladen...
            """
        )
        time.sleep(3)
        seite_neu_laden()
    
    # ggf. Namen löschen
    ungueltige_namenseingabe = False
    for index, name in st.session_state.namensloeschung_dct.items():
        if name.strip().lower() == wunschliste_bearbeitet_df.at[index, "Name"].strip().lower():
            wunschliste_bearbeitet_df.at[index, "Name"] = ""
        else:
            ungueltige_namenseingabe = True
            st.write(
                "Der für die Löschung angegebene Name beim Wunsch \"" + 
                wunschliste_bearbeitet_df.at[index, "Wunsch"] + 
                "\" stimmt nicht mit dem gespeicherten Namen in der Datenbank überein!"
            )
    del st.session_state.namensloeschung_dct
    if ungueltige_namenseingabe:
        time.sleep(3)
    
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
                            "Name": [" "]
                        }
                    )
                ),
                ignore_index=True
            )
        wunschliste_bearbeitet_df = wunschliste_bearbeitet_df[wunschliste_bearbeitet_df["Wunsch"] != ""]
        wunschliste_bearbeitet_df.fillna("", inplace=True)
            
    
    conn_neu.update(worksheet="wunschliste", data=wunschliste_bearbeitet_df)
    seite_neu_laden()
            