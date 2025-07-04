from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.character_service import CharacterService

character_bp = Blueprint("character", __name__)
character_service = CharacterService()


@character_bp.route("/dialogue/start", methods=["POST"])
@cross_origin()
def start_dialogue():
    """会話の初期メッセージと選択肢を生成"""
    try:
        data = request.get_json()
        character_id = data.get("character_id", "mano")
        lat = float(data["lat"]) if data.get("lat") is not None else None
        lon = float(data["lon"]) if data.get("lon") is not None else None
        response = character_service.generate_initial_dialogue(character_id, lat, lon)
        
        return jsonify({
            "success": True,
            "message": response["message"],
            "options": response["options"]
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@character_bp.route("/dialogue/next", methods=["POST"])
@cross_origin()
def next_dialogue():
    """ユーザーの選択に基づいて次のメッセージと選択肢を生成"""
    try:
        data = request.get_json()
        character_id = data.get("character_id", "mano")
        user_choice = data.get("user_choice")
        conversation_history = data.get("conversation_history", []) # 会話履歴を受け取る
        lat = data.get("lat")
        lon = data.get("lon")
        affection_level = data.get("affection_level")

        if user_choice is None:
            return jsonify({"success": False, "error": "user_choice is required"}), 400
        
        response = character_service.generate_next_dialogue(character_id, user_choice, conversation_history, lat, lon, affection_level)
        
        return jsonify({
            "success": True,
            "message": response["message"],
            "options": response["options"]
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@character_bp.route("/characters", methods=["GET"])
@cross_origin()
def get_characters():
    """利用可能なキャラクター一覧を取得"""
    try:
        characters = []
        for char_id, char_data in character_service.characters.items():
            characters.append({
                "id": char_id,
                "name": char_data["name"],
                "age": char_data["age"],
                "personality": char_data["personality"],
                "tone": char_data["tone"],
                "setting": char_data["setting"],
                "background": char_data["background"],
                "character_image_url": char_data.get("character_image_url", ""),
                "background_image_url": char_data.get("background_image_url", "")
            })
        
        return jsonify({
            "success": True,
            "characters": characters
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@character_bp.route("/characters/<character_id>", methods=["GET"])
@cross_origin()
def get_character(character_id):
    """特定のキャラクター情報を取得"""
    try:
        character_data = character_service.characters.get(character_id)
        if not character_data:
            return jsonify({
                "success": False,
                "error": "Character not found"
            }), 404
        
        return jsonify({
            "success": True,
            "character": {
                "id": character_id,
                "name": character_data["name"],
                "age": character_data["age"],
                "personality": character_data["personality"],
                "tone": character_data["tone"],
                "setting": character_data["setting"],
                "background": character_data["background"],
                "character_image_url": character_data.get("character_image_url", ""),
                "background_image_url": character_data.get("background_image_url", "")
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


