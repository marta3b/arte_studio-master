import streamlit as st
import requests
import json
import random
import time


class DescriptionGenerator:
    def __init__(self, use_real_api=True):
        self.use_real_api = use_real_api
        if self.use_real_api:
            self.api_key = st.secrets["openrouter"]["api_key"]
            self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def _get_artwork_specific_facts(self, artwork_id):
        
        facts_map = {
            "10661-17csont.jpg": """
- L'artista è Tivadar Csontváry Kosztka
- Dipinto nel 1907 (circa)
- Tecnica: Olio su tela
- L'albero di cedro simboleggia la persona dell'artista stesso
- L'albero centrale ha un doppio tronco
- Attorno all'albero si svolge una celebrazione che ricorda antichi rituali
- Ci sono figure di uomini e animali
- I colori sono irreali e simbolici
- Scritti di Csontváry menzionano l'albero come simbolo della sua persona
""",
            "24610-moneylen.jpg": """
- L'artista è Quentin Massys
- Dipinto nel 1514
- Tecnica: Olio su tavola
- Lo specchio convesso riflette l'autoritratto dell'artista
- La moglie sta sfogliando un libro
- L'artista cita Jan van Eyck attraverso lo specchio
- Genere: pittura di genere
- Espressioni dei personaggi: indifferenti e distaccate
- Segna un passo importante verso la natura morta pura
""",
            "02502-5season.jpg": """
- L'artista è Giuseppe Arcimboldo
- Dipinto circa nel 1590
- Tecnica: Olio su legno di pioppo
- Realizzato per Don Gregorio Comanini, un letterato mantovano
- La barba è fatta di ciuffi di muschio
- Dall'orecchio pendono ciliegie
- Il tronco spoglio simbolizza l'inverno che non produce nulla
- Il piccolo fiore sul petto simboleggia la primavera
- Il dipinto rappresenta le quattro stagioni in una sola testa
"""
        }
        
        return facts_map.get(artwork_id)
    
    def _call_openrouter_api(self, prompt, retries=3):
        for attempt in range(retries):    
            try:
                response = requests.post(
                    url=self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://artestudio.streamlit.app/",
                        "X-Title": "Arte studio",
                    },
                    data=json.dumps({
                        "model": "openai/gpt-4o-mini-2024-07-18",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.7
                    }),
                    timeout=60
                )
                
                response.raise_for_status()
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("Risposta API priva del campo 'choices'")
                
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                print(f"[OpenRouter API Error] {e}")
                return None
    
    def get_negative_personalized_description(self, artwork_data):
        if self.use_real_api:
            artwork_specific_facts = self._get_artwork_specific_facts(artwork_data['id'])
            prompt = f"""
Sei una guida museale esperta. Crei descrizioni FOCALIZZATE e ESSENZIALI di opere d'arte, rimuovendo tutte le informazioni superflue.

STRUTTURA OBBLIGATORIA (3-4 PARAGRAFI)

PARAGRAFO 1 - Identificazione essenziale (3-4 frasi)
- Artista, titolo, anno, tecnica, dimensioni
- Solo movimento artistico PRINCIPALE (nessun contesto storico esteso)
- Committenza SOLO se rilevante per l'interpretazione

PARAGRAFO 2 - Analisi visiva selettiva (5-6 frasi totali)
- Descrizione SOLO degli elementi visivi MENSIONATI nelle informazioni specifiche
- Composizione essenziale senza dettagli superflui
- Solo dettagli tecnici PERTINENTI all'opera
- Solo particolarità formali SIGNIFICATIVE

PARAGRAFO 3 - Significato focalizzato (4-5 frasi)
- Interpretazione simbolica SOLO degli elementi presenti nell'opera
- Temi iconografici PRINCIPALI (massimo 2-3)
- Solo riferimenti culturali DIRETTAMENTE collegati

LUNGHEZZA: 250-300 parole (CONCISA ma COMPLETA)

VINCOLI ASSOLUTI

OBBLIGATORIO (NECESSARIO PER RISPONDERE ALLE DOMANDE):
- Includere TUTTI i fatti specifici da: {artwork_specific_facts}
- Ogni numero/data/tecnica deve essere esatta
- Ogni elemento simbolico menzionato deve essere spiegato
- Struttura logica: identificazione → descrizione → significato
- Informazioni SUFFICIENTI per rispondere a domande su:
  * Identificazione artista/titolo/anno
  * Tecnica e materiali
  * Elementi visivi specifici
  * Significati simbolici chiave
  * Committenza/destinazione (se rilevante)

SEVERAMENTE VIETATO (INFORMAZIONI SUPERFLUE):
- Biografia dell'artista non collegata all'opera
- Confronti con altre opere dello stesso artista
- Contesti storici estesi non pertinenti
- Analogie con altre opere o artisti
- Aggettivi descrittivi non necessari
- Informazioni ripetitive o ridondanti
- Riferimenti a movimenti artistici secondari
- Descrizioni di elementi non visibili o non menzionati
- Teorie interpretative non basate sui fatti forniti

STRATEGIA DI CONTENUTO:
1. Solo fatti VERIFICABILI dalle informazioni fornite
2. Solo elementi VISIBILI nell'opera
3. Solo interpretazioni BASATE SUI DATI
4. Nessuna speculazione o ipotesi
5. Nessuna informazione "interessante ma non essenziale"

DATI OBBLIGATORI DA INCLUDERE:
Titolo: {artwork_data['title']} (esatto)
Artista: {artwork_data['artist']} (nome completo)
Anno: {artwork_data['year']} (esatto)
Tecnica/Dimensioni: {artwork_data['style']} (preciso)

INFORMAZIONI SPECIFICHE ASSOLUTAMENTE NECESSARIE:
{artwork_specific_facts}

IMPORTANTE: Questa descrizione sarà usata per un test di memoria. Deve contenere 
TUTTE le informazioni necessarie per rispondere a domande specifiche sull'opera, 
ma NIENTE di più. La concisione è fondamentale, ma la completezza dei concetti chiave 
è essenziale.
"""
            description = self._call_openrouter_api(prompt)
            if description:
                description = description.replace('**', '')
            return description if description else artwork_data['standard_description']
        else:
            return artwork_data['standard_description']