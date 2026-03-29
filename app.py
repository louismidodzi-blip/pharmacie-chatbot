from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Réponses scénarisées de la Pharmacie Santé Plus
RESPONSES = {
    'horaires': "🏥 *Pharmacie Santé Plus*\n\nNous sommes ouverts *tous les jours de 8h00 à 22h00*.\nNous assurons également un service de garde chaque 3ème semaine du mois à Abidjan pour vos urgences.",
    'disponibilite': "💊 *Disponibilité*\n\nPour vérifier la disponibilité d'un médicament, veuillez nous indiquer son nom exact ou nous envoyer une photo de la boîte. Nous vérifierons notre stock immédiatement !",
    'ordonnance': "📝 *Service Ordonnances*\n\nVous êtes au bon endroit ! Envoyez simplement la *photo de votre ordonnance* ici même. Nous préparerons votre commande à l'avance pour un retrait express en pharmacie.",
    'default': "👋 *Akwaba ! Bienvenue sur le service client WhatsApp de la Pharmacie Santé Plus.*\n\nComment puis-je vous aider aujourd'hui ? Répondez avec un des mots suivants ou un numéro :\n\n1️⃣ *Horaires* (ou Gardes)\n2️⃣ *Dispo* (Vérifier un médicament)\n3️⃣ *Ordonnance* (Envoyer votre prescription)"
}

@app.route("/webhook", methods=['POST'])
def whatsapp_bot():
    """
    Webhook qui reçoit et traite les messages WhatsApp entrants via Twilio.
    """
    # Récupérer le message texte de l'utilisateur
    incoming_msg = request.values.get('Body', '').lower().strip()
    
    # Créer la réponse Twilio (TWiML)
    resp = MessagingResponse()
    msg = resp.message()

    # Logique d'analyse simple par mots-clés
    if any(word in incoming_msg for word in ['horaire', 'heure', 'ouvert', 'fermé', 'garde', '1']):
        msg.body(RESPONSES['horaires'])
    elif any(word in incoming_msg for word in ['dispo', 'médicament', 'medicament', 'stock', 'prix', '2']):
        msg.body(RESPONSES['disponibilite'])
    elif any(word in incoming_msg for word in ['ordonnance', 'prescription', 'photo', '3']):
        msg.body(RESPONSES['ordonnance'])
    else:
        # Message par défaut s'il ne reconnaît pas le contexte
        msg.body(RESPONSES['default'])

    return str(resp)

if __name__ == "__main__":
    print("Démarrage du serveur webhook de la Pharmacie Santé Plus !")
    print("En attente de requêtes sur le port 5001 (Endpoint: /webhook) ...")
    app.run(host='0.0.0.0', port=5001, debug=True)
