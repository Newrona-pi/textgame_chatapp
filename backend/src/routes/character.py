from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.character_service import CharacterService
from src.models.nfc import NfcRecord, NfcConversation
from src.models.user import db
from datetime import datetime

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

@character_bp.route("/dialogue/character", methods=["POST"])
@cross_origin()
def character_dialogue():
    """キャラクター発言のみを生成"""
    try:
        data = request.get_json()
        character_id = data.get("character_id", "mano")
        user_choice = data.get("user_choice")
        conversation_history = data.get("conversation_history", [])
        lat = data.get("lat")
        lon = data.get("lon")
        affection_level = data.get("affection_level")

        # キャラクター発言のみ生成
        response = character_service.generate_character_message(character_id, user_choice, conversation_history, lat, lon, affection_level)
        return jsonify({
            "success": True,
            "message": response["message"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@character_bp.route("/dialogue/options", methods=["POST"])
@cross_origin()
def options_dialogue():
    """4択選択肢のみを生成"""
    try:
        data = request.get_json()
        character_id = data.get("character_id", "mano")
        character_message = data.get("character_message")
        user_choice = data.get("user_choice")
        conversation_history = data.get("conversation_history", [])
        lat = data.get("lat")
        lon = data.get("lon")
        affection_level = data.get("affection_level")

        # 4択選択肢のみ生成
        response = character_service.generate_options(character_id, character_message, user_choice, conversation_history, lat, lon, affection_level)
        return jsonify({
            "success": True,
            "options": response["options"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@character_bp.route("/characters", methods=["GET"])
@cross_origin()
def get_characters():
    """利用可能なキャラクター一覧を取得"""
    try:
        characters = []
        for char_id, char_data in character_service.characters.items():
            characters.append({
                "id": char_id,
                "name": char_data["名前"],
                "gender": char_data["性別"],
                "personality": char_data["性格"],
                "first_person": char_data["一人称"],
                "fan_name": char_data["ファンの名称"],
                "tone": char_data["口調"],
                "setting": char_data["背景・設定"],
                "character_image_url": char_data.get("キャラクター画像URL", ""),
                "background_image_url": char_data.get("背景画像URL", "")
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
                "name": character_data["名前"],
                "gender": character_data["性別"],
                "personality": character_data["性格"],
                "first_person": character_data["一人称"],
                "fan_name": character_data["ファンの名称"],
                "tone": character_data["口調"],
                "setting": character_data["背景・設定"],
                "character_image_url": character_data.get("キャラクター画像URL", ""),
                "background_image_url": character_data.get("背景画像URL", "")
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@character_bp.route('/nfc/<character_id>/<nfc_uid>/log', methods=['POST'])
@cross_origin()
def log_nfc_data(character_id, nfc_uid):
    """NFCタグごとに位置情報・会話・好感度を保存"""
    data = request.get_json()
    lat = data.get('lat')
    lon = data.get('lon')
    affection_level = data.get('affection_level')
    message = data.get('message')
    sender = data.get('sender')  # 'user' or 'character'
    now = datetime.utcnow()

    # nfc_uid + character_idでレコードを検索
    nfc_record = NfcRecord.query.filter_by(character_id=character_id, nfc_uid=nfc_uid).first()
    if not nfc_record:
        nfc_record = NfcRecord(character_id=character_id, nfc_uid=nfc_uid)
        db.session.add(nfc_record)

    # 位置情報・好感度を更新
    if lat is not None:
        nfc_record.last_location_lat = lat
    if lon is not None:
        nfc_record.last_location_lon = lon
    nfc_record.last_location_time = now
    if affection_level is not None:
        nfc_record.affection_level = affection_level
    nfc_record.updated_at = now

    # 会話内容があれば履歴に追加
    if message:
        conv = NfcConversation(nfc_record=nfc_record, message=message, sender=sender, timestamp=now)
        db.session.add(conv)

    db.session.commit()
    return jsonify({'success': True})

@character_bp.route('/nfc/<character_id>/<nfc_uid>/history', methods=['GET'])
@cross_origin()
def get_nfc_history(character_id, nfc_uid):
    """NFCタグごとの履歴取得"""
    nfc_record = NfcRecord.query.filter_by(character_id=character_id, nfc_uid=nfc_uid).first()
    if not nfc_record:
        return jsonify({'success': False, 'error': 'NFC record not found'}), 404
    conversations = [
        {
            'message': conv.message,
            'sender': conv.sender,
            'timestamp': conv.timestamp.isoformat()
        }
        for conv in nfc_record.conversations
    ]
    return jsonify({
        'success': True,
        'character_id': nfc_record.character_id,
        'nfc_uid': nfc_record.nfc_uid,
        'last_location_lat': nfc_record.last_location_lat,
        'last_location_lon': nfc_record.last_location_lon,
        'last_location_time': nfc_record.last_location_time.isoformat() if nfc_record.last_location_time else None,
        'affection_level': nfc_record.affection_level,
        'conversations': conversations
    })


