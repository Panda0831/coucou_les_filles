from openai import OpenAI
from django.conf import settings
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
)
def generer_conseil_ia(user, suivi, foetus_info):
    if not suivi:
        return {
            "resume": "Aucun suivi n'est encore disponible.",
            "conseils": [
                "Complétez votre premier suivi hebdomadaire pour recevoir des conseils personnalisés."
            ]
        }

    prompt = f"""
Tu es un assistant médical bienveillant spécialisé dans le suivi simple de grossesse.

Tu dois analyser les données suivantes et répondre uniquement en JSON.
Données de la patiente :
- Semaine de grossesse : {user.semaine_actuelle}
- IMC de départ : {user.imc}
- Catégorie IMC : {user.categorie_imc}
- Poids actuel : {suivi.poids}
- Prise de poids : {suivi.prise_poids}
- Niveau de stress : {suivi.niveau_stress}/5
- Qualité du sommeil : {suivi.qualite_sommeil}/5
- Risque global : {user.risque_global()}
- Taille moyenne du bébé : {foetus_info.taille_moyenne if foetus_info else 'Inconnue'}
- Poids moyen du bébé : {foetus_info.poids_moyen if foetus_info else 'Inconnu'}

Réponds dans ce format JSON exact :

{{
    "resume": "petit résumé rassurant",
    "conseils": [
        "conseil 1",
        "conseil 2",
        "conseil 3"
    ],
    "alerte": "message éventuel ou chaîne vide"
}}

Règles :
- Réponse courte
- Ton rassurant
- Pas de diagnostic médical
- Pas de mention de maladie grave
- Conseils simples et pratiques
"""

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            extra_body={
                "reasoning": {
                    "enabled": True
                }
            }
        )

        content = response.choices[0].message.content

        import json
        return json.loads(content)

    except Exception as e:
        return {
            "resume": "Votre suivi semble globalement stable cette semaine.",
            "conseils": [
                "Hydratez-vous suffisamment.",
                "Essayez de dormir davantage.",
                "Marchez un peu chaque jour si vous vous sentez bien."
            ],
            "alerte": "",
            "erreur": str(e)
        }