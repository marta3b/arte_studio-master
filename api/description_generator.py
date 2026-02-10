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
                messages = [
                    {
                        "role": "system",
                        "content": """SEI UNA GUIDA MUSEALE CHE DEVE ESSERE MOLTO CONCISA.
                        
    REGOLE DI SCRITTURA:
    1. SOLO FATTI, NIENTE INTERPRETAZIONI
    2. NIENTE "invita a", "suggerisce", "esplora", "celebra"
    3. NIENTE aggettivi descrittivi (ricca, unica, emblematica)
    4. NIENTE riflessioni filosofiche
    5. FRASI BREVI E DIRETTE
    6. SOLO informazioni dall'utente

    ESEMPIO DI COME SCRIVI:
    "Artista, 'Titolo' (anno). Tecnica.
    Elemento 1. Elemento 2.
    Significato 1. Significato 2."

    NON AGGIUNGERE NULLA DI TUO."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                response = requests.post(
                    url=self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    data=json.dumps({
                        "model": "openai/gpt-4o-mini-2024-07-18",
                        "messages": messages,
                        "max_tokens": 300,
                        "temperature": 0.0,  # ZERO creatività
                        "top_p": 0.1
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
            
            prompt = f"""
Sei una guida museale. Scrivi una descrizione CONCISA ma COMPLETA.

**REGOLE ASSOLUTE:**
1. Fornisci TUTTI i fatti rilevanti per le domande di memoria
2. Organizza le informazioni in modo LOGICO ma non esplicito
3. Usa un linguaggio DESCRITTIVO ma oggettivo
4. Non essere troppo diretto nelle risposte alle domande
5. Non semplificare eccessivamente - mantieni il contenuto informativo

**DATI OBBLIGATORI:**
{artwork_data['artist']}, "{artwork_data['title']}" ({artwork_data['year']})
{artwork_data['style']}

**FATTI DA INCLUIRE:**
{artwork_specific_facts}

**STRUTTURA:**
1. Identificazione completa (1-2 frasi)
2. Descrizione visiva dettagliata (3-4 frasi)
3. Contesto e significato (2-3 frasi)

**COME PRESENTARE LE INFORMAZIONI:**
- Non ripetere i fatti in modo meccanico
- Integra le informazioni in una narrazione coerente
- Usa frasi complesse che combinano più fatti
- Non evidenziare esplicitamente ciò che sarà testato
- Mantieni un tono da guida museale professionale

**ESEMPIO DI STILE CORRETTO:**
"L'opera 'Pellegrinaggio ai Cedri in Libano' di Tivadar Csontváry Kosztka risale al 1907 ed è realizzata con tecnica a olio su tela. 
La composizione presenta un imponente albero di cedro al centro della scena, caratterizzato da una particolare struttura a doppio tronco. 
Intorno ad esso si raduna una varietà di figure umane e animali, coinvolte in un'attività rituale che ricorda antiche celebrazioni. 
L'artista stesso, nei suoi scritti personali, ha spesso associato l'immagine dell'albero alla rappresentazione della propria identità, 
attribuendo al cedro un valore simbolico che trascende la semplice descrizione naturalistica."

**NOTA:**
- Le informazioni devono essere PRESENTI ma non SOTTOLINEATE
- Il testo deve essere abbastanza lungo da coprire tutti i punti (6-8 frasi)
- Non saltare alcun fatto rilevante dai dati forniti

**Scrivi ora una descrizione completa ma non esplicitamente didattica:**
"""
            
            description = self._call_openrouter_api(prompt)
            
            if description:
                description = description.strip()
                return description
            else:
                return artwork_data['standard_description']
        else:
            return artwork_data['standard_description']