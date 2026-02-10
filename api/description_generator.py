import streamlit as st
import requests
import json
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
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 400,
                        "temperature": 0.2
                    }),
                    timeout=30
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    return None
                
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                return None
    
    def get_negative_personalized_description(self, artwork_data):
        if self.use_real_api:
            artwork_specific_facts = self._get_artwork_specific_facts(artwork_data['id'])
            
            # PROMPT PER PERSONALIZZAZIONE NEGATIVA
            prompt = f"""
Scrivi una descrizione concisa dell'opera d'arte seguendo queste regole:

**CONTENUTO OBBLIGATORIO (deve includere TUTTO):**
1. Artista: {artwork_data['artist']}
2. Titolo: "{artwork_data['title']}"
3. Anno: {artwork_data['year']}
4. Tecnica: {artwork_data['style']}
5. Tutti questi fatti specifici:
{artwork_specific_facts}

**REGOLE DI SCRITTURA (personalizzazione negativa):**
- Scrivi SOLO le informazioni essenziali
- Rimuovi TUTTE le informazioni superflue
- Mantieni OGNI concetto chiave dall'elenco sopra
- Usa frasi brevi e dirette
- Non aggiungere contesto storico
- Non aggiungere biografie
- Non usare aggettivi descrittivi non necessari
- Non fare confronti con altre opere
- Non spiegare movimenti artistici

**STRUTTURA:**
1. Primo paragrafo: Identificazione dell'opera (2-3 frasi)
2. Secondo paragrafo: Descrizione degli elementi visivi (3-4 frasi)
3. Terzo paragrafo: Significati e simboli (2-3 frasi)

**LUNGHEZZA:** Circa 150-200 parole totali

**ESEMPIO DI STILE:**
"Artista, 'Titolo' (anno). Tecnica.

Elemento visivo 1. Elemento visivo 2. Elemento visivo 3.

Significato 1. Significato 2."

**Scrivi ora la descrizione concisa:**
"""
            
            description = self._call_openrouter_api(prompt)
            
            if description:
                description = description.strip()
                return description
            else:
                return artwork_data['standard_description']
        else:
            return artwork_data['standard_description']