from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

# Connexion à la base de données PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "mydb"),
        user=os.getenv("POSTGRES_USER", "user"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("POSTGRES_HOST", "db"),  # Nom du service défini dans docker-compose
        port=os.getenv("POSTGRES_PORT", "5432")
    )

# Récupération des recommandations
def get_recommendations(item_ids, num_recommendations=5):
    # Vérifier que le nombre de recommandations demandé est valide
    if num_recommendations not in [1, 3, 5, 7, 10]:
        raise ValueError("Le nombre de recommandations doit être 1, 3, 5, 7 ou 10.")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT item_id FROM (
            SELECT tp.item_id, tp.date AS event_date
            FROM train_sessions ts
            JOIN train_purchases tp ON ts.session_id = tp.session_id
            WHERE ts.item_id IN %s
            
            UNION
            
            SELECT ts2.item_id, ts2.date AS event_date
            FROM train_sessions ts1
            JOIN train_sessions ts2 ON ts1.session_id = ts2.session_id
            WHERE ts1.item_id IN %s AND ts2.item_id NOT IN %s
        ) AS combined
        ORDER BY event_date DESC
        LIMIT %s
    """
    cursor.execute(query, (item_ids, item_ids, item_ids, num_recommendations))
    recommendations = [item[0] for item in cursor.fetchall()]

    query_purchases = """
        SELECT tp.item_id, COUNT(*) as frequency
        FROM train_sessions ts
        JOIN train_purchases tp ON ts.session_id = tp.session_id
        WHERE ts.item_id IN %s
        GROUP BY tp.item_id
        ORDER BY frequency DESC
    """
    cursor.execute(query_purchases, (item_ids,))
    purchase_recommendations = [item[0] for item in cursor.fetchall()]
    
    query_views = """
        SELECT DISTINCT ts2.item_id
        FROM train_sessions ts1
        JOIN train_sessions ts2 ON ts1.session_id = ts2.session_id
        WHERE ts1.item_id IN %s AND ts2.item_id NOT IN %s
    """
    cursor.execute(query_views, (item_ids, item_ids))
    view_recommendations = [item[0] for item in cursor.fetchall()]
    
    conn.close()
    
    return {
        "merged_recommendations": recommendations,
        "purchased_items": purchase_recommendations,
        "viewed_items": view_recommendations
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommendations', methods=['GET'])
def recommendations():
    try:
        # Récupérer les item_ids depuis la requête GET
        item_ids = tuple(map(int, request.args.get('item_ids', '').split(',')))
        
        # Vérifier si les item_ids sont valides
        if len(item_ids) < 1:
            return jsonify({"error": "Veuillez fournir au moins un item_id."}), 400
        
        # Récupérer le paramètre num_recommendations avec une valeur par défaut de 5
        num_recommendations = request.args.get('num_recommendations', 5, type=int)
        
        # Valider si le nombre de recommandations est valide
        if num_recommendations not in [1, 3, 5, 7, 10]:
            return jsonify({"error": "Le nombre de recommandations doit être 1, 3, 5, 7 ou 10."}), 400
        
        # Retourner les recommandations sous format JSON
        return jsonify(get_recommendations(item_ids, num_recommendations))
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
