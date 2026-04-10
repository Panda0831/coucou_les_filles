from google import genai
import json

def analyser_grossesse_gemini(data_contexte):
    # Remplace par ta clé valide
    API_KEY = "AIzaSyD16qhYbVivbnCK1p787lLoFtw-AvLfZsY" 
    client = genai.Client(api_key=API_KEY)
    
    # Prompt optimisé pour des conseils concrets
    prompt = f"""
    Tu es Ryan, un assistant virtuel expert en suivi de grossesse. 
    Analyse les données de la patiente et fournis un rapport structuré.

    DONNÉES PATIENTE :
    - Profil : {data_contexte['profil']}
    - Derniers relevés (Poids, Tension, Symptômes, Sommeil) : {data_contexte['historique']}

    TES DIRECTIVES :
    1. ANALYSE : Dis ce qui va bien et ce qui est préoccupant (Tension, prise de poids, stress).
    2. ALIMENTATION : Donne un conseil nutritionnel spécifique basé sur ses relevés (ex: plus de fer si fatigue, moins de sel si tension).
    3. HABITUDES : Suggère une habitude de vie (sommeil, activité physique).
    4. ALERTE : Si la tension est > 14/9 ou s'il y a des symptômes graves, passe la vigilance en 'Alerte' et conseille de consulter immédiatement.

    RÉPONDS UNIQUEMENT AU FORMAT JSON SUIVANT :
    {{
        "analyse": "Ton analyse concise en 2-3 phrases maximum.",
        "vigilance": "Stable" ou "Attention" ou "Alerte",
        "conseils": [
            "Conseil médical (ex: consultation si besoin ou suivi normal)",
            "Conseil alimentaire spécifique",
            "Conseil hygiène de vie/habitude"
        ]
    }}
    """

    try:
        # Tentative avec Gemini 2.0 Flash
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        if response and response.text:
            # Nettoyage de sécurité pour extraire uniquement le JSON
            res_text = response.text.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
                
            return res_text
        print("⚠️ Réponse vide ou inattendue de Gemini 2.0 Flash.")
        return None
        
    except Exception as e:
        print(f"❌ ERREUR API GEMINI : {str(e)}")
        # Fallback sur 1.5 Flash en cas d'erreur sur la 2.0
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            return response.text.strip()
        except:
            return None