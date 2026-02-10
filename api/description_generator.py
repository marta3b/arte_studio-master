import streamlit as st
import requests
import json
import random
import time


class DescriptionGenerator:
    def __init__(self, use_real_api=True):
        self.use_real_api = use_real_api
        if self.use_real_api:
            # DEBUG: Controlla se l'API key esiste
            try:
                self.api_key = st.secrets["openrouter"]["api_key"]
                print(f"DEBUG: API Key trovata (primi 10 caratteri): {self.api_key[:10]}...")
            except Exception as e:
                print(f"DEBUG ERRORE: API Key non trovata: {e}")
                self.api_key = None
                
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
        print(f"\n{'='*50}")
        print(f"DEBUG OPENROUTER API CALL")
        print(f"{'='*50}")
        
        # DEBUG: Controlla se abbiamo l'API key
        if not self.api_key:
            print("DEBUG ERRORE: Nessuna API key disponibile")
            return None
            
        for attempt in range(retries):    
            try:
                print(f"DEBUG: Tentativo {attempt + 1}/{retries}")
                print(f"DEBUG: Model: openai/gpt-4o-mini-2024-07-18")
                print(f"DEBUG: Prompt length: {len(prompt)} caratteri")
                print(f"DEBUG: Prompt preview:\n{prompt[:300]}...\n")
                
                # Prepara la richiesta
                data = {
                    "model": "openai/gpt-4o-mini-2024-07-18",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                
                print(f"DEBUG: Invio richiesta a {self.api_url}")
                start_time = time.time()
                
                response = requests.post(
                    url=self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://artestudio.streamlit.app/",
                        "X-Title": "Arte studio",
                    },
                    data=json.dumps(data),
                    timeout=60
                )
                
                end_time = time.time()
                print(f"DEBUG: Tempo risposta: {end_time - start_time:.2f} secondi")
                print(f"DEBUG: Status code: {response.status_code}")
                
                # Controlla lo status
                response.raise_for_status()
                
                # Prova a parsare la risposta
                try:
                    result = response.json()
                    print(f"DEBUG: Risposta JSON ricevuta")
                    
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0]["message"]["content"]
                        print(f"DEBUG: Successo! Contenuto ricevuto ({len(content)} caratteri)")
                        print(f"DEBUG: Primi 200 caratteri:\n{content[:200]}...\n")
                        return content
                    else:
                        print(f"DEBUG ERRORE: Risposta senza 'choices'")
                        print(f"DEBUG: Risposta completa: {json.dumps(result, indent=2)}")
                        raise ValueError("Risposta API priva del campo 'choices'")
                        
                except json.JSONDecodeError as e:
                    print(f"DEBUG ERRORE: JSON non valido nella risposta")
                    print(f"DEBUG: Risposta text: {response.text[:500]}")
                    raise e
                
            except requests.exceptions.Timeout:
                print(f"DEBUG ERRORE: Timeout dopo 60 secondi")
                if attempt < retries - 1:
                    print(f"DEBUG: Ritento tra 2 secondi...")
                    time.sleep(2)
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"DEBUG ERRORE: Errore di connessione: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                    
            except Exception as e:
                print(f"DEBUG ERRORE: Errore generico: {type(e).__name__}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
        
        print(f"DEBUG: Tutti i tentativi falliti")
        return None
    
    def get_negative_personalized_description(self, artwork_data):
        print(f"\n{'='*50}")
        print(f"DEBUG: Generazione descrizione per: {artwork_data['title']}")
        print(f"{'='*50}")
        
        if self.use_real_api:
            artwork_specific_facts = self._get_artwork_specific_facts(artwork_data['id'])
            print(f"DEBUG: Facts ottenuti: {artwork_specific_facts[:100]}...")
        
         # CREA IL PROMPT
            prompt = f"""
Sei una guida museale esperta. Scrivi una descrizione COMPLETA ma CONCENTRATA dell'opera d'arte.

STRUTTURA OBBLIGATORIA (3 PARAGRAFI):

PARAGRAFO 1 - Identificazione di base (3-4 frasi)
- Inizia con: {artwork_data['artist']}, "{artwork_data['title']}" ({artwork_data['year']})
- Poi: {artwork_data['style']}
- Menziona il movimento artistico principale SENZA approfondire il contesto storico
- Se c'è una committenza specifica, menzionala brevemente

PARAGRAFO 2 - Descrizione visiva essenziale (4-5 frasi)
- Descrivi SOLO gli elementi visivi presenti in queste informazioni:
{artwork_specific_facts}
- Non aggiungere dettagli visivi che non sono elencati sopra
- Descrivi la composizione in modo semplice
- Menziona i colori e la tecnica solo se rilevanti per l'opera

PARAGRAFO 3 - Significato e interpretazione (3-4 frasi)
- Spiega SOLO i significati simbolici presenti in queste informazioni:
{artwork_specific_facts}
- Non aggiungere interpretazioni personali o teorie non basate sui fatti forniti
- Mantieni l'interpretazione focalizzata sull'opera specifica

LUNGHEZZA TOTALE: 150-200 parole (CONCISA ma INFORMATIVA)

COSA NON DEVI INCLUIRE (INFORMAZIONI SUPERFLUE):
1. Biografia dell'artista non collegata a questa opera specifica
2. Confronti con altre opere dello stesso artista o di altri
3. Contesto storico esteso che non serve a capire l'opera
4. Analogie, metafore o paragoni non necessari
5. Aggettivi descrittivi eccessivi (bello, magnifico, straordinario)
6. Informazioni ripetitive o ridondanti
7. Teorie interpretative non basate sui fatti forniti
8. Riferimenti a movimenti artistici secondari o minori

RICORDA:
Devi includere TUTTE queste informazioni specifiche:
{artwork_specific_facts}

Ma non aggiungere NIENTE di più. La descrizione deve essere completa nei contenuti essenziali ma priva di informazioni superflue.
"""
        
            print(f"DEBUG: Prompt creato, lunghezza: {len(prompt)} caratteri")
            
            description = self._call_openrouter_api(prompt)
            
            if description:
                print(f"DEBUG: Descrizione generata con successo!")
                description = description.replace('**', '')
                return description
            else:
                print(f"DEBUG ERRORE: API ha restituito None, uso descrizione standard")
                return artwork_data['standard_description']
        else:
          print(f"DEBUG: use_real_api=False, uso descrizione standard")
          return artwork_data['standard_description']