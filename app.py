import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Réponses scénarisées de la Pharmacie Santé Plus
RESPONSES = {
    'horaires': "🏥 *Pharmacie Santé Plus*\n\nNous sommes ouverts *tous les jours de 8h00 à 22h00*.\nNous assurons également un service de garde chaque 3ème semaine du mois à Abidjan pour vos urgences.",
    'disponibilite': "💊 *Disponibilité*\n\nPour vérifier la disponibilité d'un médicament, veuillez nous indiquer son nom exact ou nous envoyer une photo de la boîte. Nous vérifierons notre stock immédiatement !",
    'ordonnance': "📝 *Service Ordonnances*\n\nVous êtes au bon endroit ! Envoyez simplement la *photo de votre ordonnance* ici même. Nous préparerons votre commande à l'avance pour un retrait express en pharmacie.",
    'default': "👋 *Akwaba ! Bienvenue sur le service client WhatsApp de la Pharmacie Santé Plus.*\n\nComment puis-je vous aider aujourd'hui ? Répondez avec un des mots suivants ou un numéro :\n\n1️⃣ *Horaires* (ou Gardes)\n2️⃣ *Dispo* (Vérifier un médicament)\n3️⃣ *Ordonnance* (Envoyer votre prescription)"
}

VERIFY_TOKEN = "pharmacie2026"

@app.route("/webhook", methods=['GET'])
def verify_webhook():
    """
    Validation du Webhook pour l'API WhatsApp Cloud de Meta.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook vérifié avec succès !")
            return challenge, 200
        else:
            return "Forbidden", 403
    return "Bad Request", 400

@app.route("/webhook", methods=['POST'])
def whatsapp_bot():
    """
    Webhook qui reçoit et traite les messages WhatsApp entrants via Meta.
    """
    body = request.get_json()

    if body and body.get("object"):
        if body.get("entry") and body["entry"][0].get("changes") and body["entry"][0]["changes"][0].get("value") and body["entry"][0]["changes"][0]["value"].get("messages"):
            value = body["entry"][0]["changes"][0]["value"]
            message = value["messages"][0]
            phone_number_id = value["metadata"]["phone_number_id"]
            from_number = message["from"]
            
            if message.get("type") == "text":
                incoming_msg = message["text"]["body"].lower().strip()
                
                # Logique d'analyse simple par mots-clés
                if any(word in incoming_msg for word in ['horaire', 'heure', 'ouvert', 'fermé', 'garde', '1']):
                    response_text = RESPONSES['horaires']
                elif any(word in incoming_msg for word in ['dispo', 'médicament', 'medicament', 'stock', 'prix', '2']):
                    response_text = RESPONSES['disponibilite']
                elif any(word in incoming_msg for word in ['ordonnance', 'prescription', 'photo', '3']):
                    response_text = RESPONSES['ordonnance']
                else:
                    response_text = RESPONSES['default']

                # Envoi de la réponse via Meta Graph API
                send_message(phone_number_id, from_number, response_text)

        return "EVENT_RECEIVED", 200
    else:
        return "Not Found", 404

def send_message(phone_number_id, to_number, text):
    """
    Envoie un message via l'API WhatsApp Cloud de Meta.
    """
    token = os.environ.get("WHATSAPP_TOKEN")
    if not token:
        print("Erreur: WHATSAPP_TOKEN n'est pas configuré en variable d'environnement.")
        return
        
    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text
        }
    }
    
    try:
        requests.post(url, headers=headers, json=data)
    except Exception as e:
        print(f"Erreur d'envoi du message: {e}")

if __name__ == "__main__":
    print("Démarrage du serveur webhook de la Pharmacie Santé Plus !")
    print(f"En attente de requêtes sur le port {os.environ.get('PORT', 5001)} (Endpoint: /webhook) ...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=False)
