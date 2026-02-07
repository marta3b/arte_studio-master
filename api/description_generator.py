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
Sei una guida museale esperta. Crei descrizioni complete e rigorose di opere d'arte.

STRUTTURA OBBLIGATORIA (4-5 PARAGRAFI)

PARAGRAFO 1 - Introduzione (4-5 frasi)
- Artista, titolo, anno, tecnica, dimensioni
- Movimento artistico e contesto storico
- Committenza o destinazione (se nota)

PARAGRAFI 2-3 - Analisi visiva completa (6-8 frasi ciascuno)
- Descrizione sistematica di TUTTI gli elementi visivi
- Composizione, prospettiva, uso della luce
- Dettagli tecnici (pennellate, colori, materiali)
- Particolarità formali e innovazioni

PARAGRAFO 4 - Simbologia e significato (5-6 frasi)
- Interpretazione simbolica degli elementi
- Temi iconografici e messaggi principali
- Riferimenti culturali e storici pertinenti

LUNGHEZZA MINIMA: 350-400 parole

STRATEGIA DI DISTRIBUZIONE
PARAGRAFO 1 (Introduzione)
PARAGRAFO 2 (Analisi visiva 1)
PARAGRAFO 3 (Analisi visiva 2)
PARAGRAFO 4 (Simbologia)

VINCOLI ASSOLUTI
OBBLIGATORIO:
- Minimo 350 parole
- Ogni elemento visivo rilevante descritto
- Dati storici precisi e verificabili
- Usare tutte le informazioni in {artwork_specific_facts}

SEVERAMENTE VIETATO:
- Inserire analogie, paragoni o confronti estranei all’opera
- Descrizioni superficiali o incomplete
- Paragrafi conclusivi riassuntivi
- Non dividere esplicitamente i paragrafi inserendo il titolo

DATI DELL'OPERA
Titolo: {artwork_data['title']}
Artista: {artwork_data['artist']}
Anno: {artwork_data['year']}
Tecnica/Dimensioni: {artwork_data['style']}
Descrizione di base: {artwork_data['standard_description']}
Informazioni specifiche da includere:
{artwork_specific_facts}
"""
            description = self._call_openrouter_api(prompt)
            if description:
                description = description.replace('**', '')
            return description if description else artwork_data['standard_description']
        else:
            return artwork_data['standard_description']