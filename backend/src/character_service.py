import csv
import os
import random
import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from dateutil import tz
from geopy.geocoders import Nominatim
from cachetools import TTLCache

load_dotenv()

_geocoder = Nominatim(user_agent="chat-app")
_geo_cache = TTLCache(maxsize=500, ttl=60*60*6) 

def _latlon_to_pref_city(lat, lon):
    """都道府県 + 市区町村 名を返す（どちらか片方でも可）"""
    if lat is None or lon is None:
        return None, None              # (pref, city)

    key = f"{round(lat,3)},{round(lon,3)}"
    if key in _geo_cache:
        return _geo_cache[key]

    try:
        loc = _geocoder.reverse(
            (lat, lon),
            language="ja",    # 日本語優先
            zoom=10,          # 10～12 で市区町村レベル
            timeout=2,
        )
        addr = loc.raw.get("address", {}) if loc else {}

        # 都道府県
        pref = addr.get("state") or addr.get("region") or addr.get("province")

        # 市区町村（優先順位順にフォールバック）
        city = (
            addr.get("city") or addr.get("town") or addr.get("village")
            or addr.get("municipality") or addr.get("county")
        )

        _geo_cache[key] = (pref, city)
        return pref, city

    except Exception as e:
        logger.warning("Geocode failed: %s", e)
        return None, None


class CharacterService:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set in .env file")
        self.openai_client = OpenAI(api_key=api_key)
        self.characters = self._load_characters()
        


    def _load_characters(self):
        characters = {}
        csv_path = os.path.join(os.path.dirname(__file__), 'characters.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    characters[row['character_id']] = row
        except FileNotFoundError:
            print(f"Warning: {csv_path} not found")
        return characters

    def _get_current_context(self, lat=None, lon=None):
        now = datetime.now(tz=tz.gettz("Asia/Tokyo"))
        month = now.month
        if month in [12, 1, 2]:
            season = "冬"
            season_detail = "寒い季節で、雪が降ったり、暖かい飲み物が恋しくなる時期"
        elif month in [3, 4, 5]:
            season = "春"
            season_detail = "桜が咲き、新学期が始まる暖かくなってきた時期"
        elif month in [6, 7, 8]:
            season = "夏"
            season_detail = "暑い季節で、夏休みや海、祭りなどが楽しい時期"
        else:
            season = "秋"
            season_detail = "涼しくなり、紅葉が美しく、文化祭などがある時期"
        
        hour = now.hour
        if 5 <= hour < 12:
            time_period = "朝"
            time_detail = "朝の爽やかな時間帯"
        elif 12 <= hour < 17:
            time_period = "昼"
            time_detail = "昼間の明るい時間帯"
        elif 17 <= hour < 21:
            time_period = "夕方"
            time_detail = "夕方の落ち着いた時間帯"
        else:
            time_period = "夜"
            time_detail = "夜の静かな時間帯"
        
        weekdays = ["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"]
        weekday = weekdays[now.weekday()]
        
        pref = _latlon_to_pref_city(lat, lon) or "場所不明"
        return {
            "date": now.strftime("%Y年%m月%d日"),
            "season": season,
            "season_detail": season_detail,
            "time_period": time_period,
            "time_detail": time_detail,
            "weekday": weekday,
            "hour": now.hour,
            "pref": pref, 
        }

    def generate_initial_dialogue(self, character_id, lat=None, lon=None):
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。", "options": []}

        context = self._get_current_context(lat, lon)
        prompt = self._build_initial_prompt(character_data, context)
        
        try:
            response_text = self._generate_with_openai(prompt)
            message, options = self._parse_ai_response(response_text)
            random.shuffle(options)
            return {"message": message, "options": options}
        except Exception as e:
            return {"message": f"初期会話生成エラー: {str(e)}", "options": []}

    def generate_next_dialogue(self, character_id, user_choice, conversation_history, lat=None, lon=None):
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。", "options": []}

        context = self._get_current_context(lat, lon)
        prompt = self._build_next_prompt(character_data, user_choice, conversation_history, context)

        try:
            response_text = self._generate_with_openai(prompt)
            message, options = self._parse_ai_response(response_text)
            random.shuffle(options)
            return {"message": message, "options": options}
        except Exception as e:
            return {"message": f"次の会話生成エラー: {str(e)}", "options": []}

    def _build_initial_prompt(self, character_data, context):
        name        = character_data['name']
        age         = character_data['age']
        personality = character_data['personality']
        tone        = character_data['tone']
        setting     = character_data['setting']
        background  = character_data['background']
        

        return f"""
あなたは{name}という{age}歳の{personality}キャラクターです。
{tone}で話し、{setting}という設定です。
{background}

現在の状況:
- 日付: {context['date']} ({context['weekday']})
- 季節: {context['season']} ({context['season_detail']})
- 時間帯: {context['time_period']} ({context['time_detail']})
- 現在地: {context['pref']}

その返答では必ず、
「{context['pref']}」らしさ（位置情報から取得した場所の名物・今日開催している地元行事・天気・おすすめのお店の具体名など）を多く盛り込み、
続けて新しい 4 択を提示してください。
▼フォーマット（厳守）
メッセージ: ～
1. 「～」 #v-good
2. 「～」 #good
3. 「～」 #bad
4. 「～」 #v-bad

▼ルール
- #v-good が 1 行、#good が 1 行、#bad が 1 行、#v-bad が 1 行 **ちょうど**。
- 行頭の番号と「.」は半角固定。
- 各行は主人公の台詞／行動を 1 文で。
- 余計な説明や注釈は書かない。
"""


    def _build_next_prompt(self, character_data, user_choice, conversation_history, context):
        name        = character_data['name']
        age         = character_data['age']
        personality = character_data['personality']
        tone        = character_data['tone']
        setting     = character_data['setting']
        background  = character_data['background']

        history_str = "\n".join(
            f"ユーザー: {h['user']}\n{name}: {h['character']}" for h in conversation_history
        )

        return f"""
あなたは{name}という{age}歳の{personality}キャラクターです。
{tone}で話し、{setting}という設定です。
{background}

現在の状況:
- 日付: {context['date']} ({context['weekday']})
- 季節: {context['season']} ({context['season_detail']})
- 時間帯: {context['time_period']} ({context['time_detail']})
- 現在地: {context['pref']}

これまでの会話履歴:
{history_str}

ユーザーは「{user_choice}」を選びました。
その反応として「{context['pref']}」らしさ（位置情報から取得した場所の名物・今日開催している地元行事・天気・おすすめのお店の具体名など）を盛り込んだ 1 つのメッセージを返し、続けて新しい 4 択を提示してください。

▼フォーマット（厳守）
メッセージ: ～
1. 「～」 #v-good
2. 「～」 #good
3. 「～」 #bad
4. 「～」 #v-bad
"""


    def _generate_with_openai(self, prompt):
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは指定されたキャラクターになりきって、自然で親しみやすいメッセージと、それに対する4つの選択肢を生成するアシスタントです。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300, # メッセージと選択肢の両方を生成するため、max_tokensを増やす
            temperature=0.8
        )
        return response.choices[0].message.content.strip()

    def _parse_ai_response(self, response_text):
        message = ""
        options = []
        lines = [line.strip() for line in response_text.splitlines() if line.strip()]

        # Find the start of the options
        options_start_index = -1
        for i, line in enumerate(lines):
            if line[:2] in {"1.", "2.", "3.", "4."} and "#" in line:
                options_start_index = i
                break
        
        # If no options found, treat the whole response as a message
        if options_start_index == -1:
            return response_text, []

        # Extract message and option lines
        message_lines = lines[:options_start_index]
        option_lines = lines[options_start_index:]

        # Join message lines and clean up
        if message_lines:
            raw_message = " ".join(message_lines)
            if raw_message.startswith("メッセージ:"):
                message = raw_message.replace("メッセージ:", "", 1).strip()
            else:
                message = raw_message
        
        # Parse option lines
        for line in option_lines:
            try:
                # 「番号. テキスト #tag」の形式を分解
                num, rest = line.split(".", 1)
                text, tag = rest.rsplit("#", 1)
                options.append({"text": text.strip(" 「」"), "type": tag.strip()})
            except ValueError:
                # Ignore malformed option lines
                continue
        
        return message, options
  
    

    def get_characters(self):
        return list(self.characters.keys())


