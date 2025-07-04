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
                print(f"CSV columns: {reader.fieldnames}")
                for row in reader:
                    print(f"Row keys: {list(row.keys())}")
                    if 'character_id' not in row:
                        print(f"Missing character_id in row: {row}")
                        continue
                    characters[row['character_id']] = row
        except FileNotFoundError:
            print(f"Warning: {csv_path} not found")
        except Exception as e:
            print(f"Error loading CSV: {e}")
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

    def generate_initial_dialogue(self, character_id, lat=None, lon=None, affection_level=40):
        print(f"[DEBUG] affection_level: {affection_level}")
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。", "options": []}

        context = self._get_current_context(lat, lon)
        character_prompt = self._build_initial_character_prompt(character_data, context, affection_level)
        
        try:
            # キャラクター発言を生成
            character_response = self._generate_with_openai(character_prompt, is_character=True)
            message = character_response.strip()
            
            # キャラクター発言内容を4択選択肢生成プロンプトに渡す
            options_prompt = self._build_initial_options_prompt(character_data, message)
            options_response = self._generate_with_openai(options_prompt, is_character=False)
            options = self._parse_options_only(options_response)
            
            random.shuffle(options)
            return {"message": message, "options": options}
        except Exception as e:
            return {"message": f"初期会話生成エラー: {str(e)}", "options": []}

    def generate_next_dialogue(self, character_id, user_choice, conversation_history, lat=None, lon=None, affection_level=None):
        print(f"[DEBUG] affection_level: {affection_level}")
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。", "options": []}

        context = self._get_current_context(lat, lon)
        character_prompt = self._build_next_character_prompt(character_data, user_choice, conversation_history, context, affection_level)

        try:
            # キャラクター発言を生成
            character_response = self._generate_with_openai(character_prompt, is_character=True)
            message = character_response.strip()
            
            # キャラクター発言内容を4択選択肢生成プロンプトに渡す
            options_prompt = self._build_next_options_prompt(character_data, message, user_choice, conversation_history)
            options_response = self._generate_with_openai(options_prompt, is_character=False)
            options = self._parse_options_only(options_response)
            
            random.shuffle(options)
            return {"message": message, "options": options}
        except Exception as e:
            return {"message": f"次の会話生成エラー: {str(e)}", "options": []}

    def _build_initial_character_prompt(self, character_data, context, affection_level):
        name        = character_data['name']
        age         = character_data['age']
        personality = character_data['personality']
        tone        = character_data['tone']
        setting     = character_data['setting']
        background  = character_data['background']
        
        # キャラクター発言生成用プロンプト
        character_prompt = f"""
あなたは{age}歳の{personality}キャラクターです。
{tone}で話し、{setting}という設定です。
{background}

【重要】好感度パラメーター: {affection_level}（0〜100）
以下の好感度対応表に従って、必ず言葉遣いと表現を調整してください：

▼好感度対応表（絶対厳守）
- {affection_level}81~100: 好意的で甘い表現（「素敵ですね♪」「大好き」「一緒にいると楽しい」など）
- {affection_level}61~80: 友達のようなフランクで親しみやすい表現（「そうだね！」「いいじゃん」「楽しそう」など）
- {affection_level}41~60: 普通の丁寧で標準的な表現（「そうですね」「はい」「いいと思います」など）
- {affection_level}21~40: そっけない素っ気ない表現
- {affection_level}0~20: 憤怒する

現在の状況:
- 日付: {context['date']} ({context['weekday']})
- 時間帯: {context['time_period']} ({context['time_detail']})
- 現在地: {context['pref']}

好感度{affection_level}に適した言葉遣いで、「{context['pref']}」らしさ（位置情報から取得した場所の名物・今日開催している地元行事・天気・おすすめのお店の具体名など）を盛り込んだ自然なメッセージを生成してください。

▼ルール
- {name}のセリフのみを生成する
- 好感度{affection_level}の言葉遣いを必ず適用する
"""

        return character_prompt

    def _build_initial_options_prompt(self, character_data, character_message):
        name = character_data['name']
        
        # システムによる4択選択肢生成用プロンプト
        options_prompt = f"""
あなたはキャラクターの同級生です。{name}というキャラクターに対して、ユーザーが発するセリフの選択肢を4つ生成してください。

直前の{name}の発言: 「{character_message}」

必ず一人称視点のセリフを生成してください。セリフの中に{name}を含めないでください。

▼選択肢の種類（1つずつ生成）
- #v-good: ユーザーが{name}に対して発するとても好意的なセリフ（好感度+10）
- #good: ユーザーが{name}に対して発するやや好意的なセリフ（好感度+5）
- #bad: ユーザーが{name}に対して発するやや悪印象なセリフ（好感度-5）
- #v-bad: ユーザーが{name}に対して発する非常に悪印象なセリフ（好感度-10）

▼フォーマット（厳守）
1. 「～」 #v-good
2. 「～」 #good
3. 「～」 #bad
4. 「～」 #v-bad

▼ルール
- ユーザーの発言として自然で理解しやすい内容にする
- 行頭の番号と「.」は半角固定
- 直前の{name}の発言内容に適切に反応する選択肢を生成する
"""

        return options_prompt

    def _build_next_character_prompt(self, character_data, user_choice, conversation_history, context, affection_level=None):
        name        = character_data['name']
        age         = character_data['age']
        personality = character_data['personality']
        tone        = character_data['tone']
        setting     = character_data['setting']
        background  = character_data['background']

        history_str = "\n".join(
            f"ユーザー: {h['user']}\n{name}: {h['character']}" for h in conversation_history
        )

        # キャラクター発言生成用プロンプト
        character_prompt = f"""
あなたは{age}歳の{personality}キャラクターです。
{tone}で話し、{setting}という設定です。
{background}

【重要】好感度パラメーター: {affection_level}（0〜100）
以下の好感度対応表に従って、必ず言葉遣いと表現を調整してください：

▼好感度対応表（絶対厳守）
- {affection_level}81~100: 好意的で甘い表現（「素敵ですね♪」「大好き」「一緒にいると楽しい」など）
- {affection_level}61~80: 友達のようなフランクで親しみやすい表現（「そうだね！」「いいじゃん」「楽しそう」など）
- {affection_level}41~60: 普通の丁寧で標準的な表現（「そうですね」「はい」「いいと思います」など）
- {affection_level}21~40: そっけない素っ気ない表現
- {affection_level}0~20: 憤怒する

現在の状況:
- 日付: {context['date']} ({context['weekday']})
- 時間帯: {context['time_period']} ({context['time_detail']})
- 現在地: {context['pref']}
- 好感度パラメーター: {affection_level}

これまでの会話履歴:
{history_str}

ユーザーは「{user_choice}」を選びました。
好感度{affection_level}に適した言葉遣いで、ユーザーの選択に対して反応し、たまに「{context['pref']}」らしさ（位置情報から取得した場所の名物・今日開催している地元行事・おすすめのお店の具体名など）を盛り込んだ自然なメッセージを生成してください。

▼ルール
- {name}セリフのみを生成する
- 好感度{affection_level}の言葉遣いを必ず適用する
"""

        return character_prompt

    def _build_next_options_prompt(self, character_data, character_message, user_choice, conversation_history):
        name = character_data['name']
        
        history_str = "\n".join(
            f"ユーザー: {h['user']}\n{name}: {h['character']}" for h in conversation_history
        )

        # システムによる4択選択肢生成用プロンプト
        options_prompt = f"""
あなたはキャラクターの同級生です。{name}というキャラクターに対して、ユーザーが発するセリフの選択肢を4つ生成してください。

直前の{name}の発言: 「{character_message}」
ユーザーの直前の選択: 「{user_choice}」

これまでの会話履歴:
{history_str}

必ず一人称視点のセリフを生成してください。セリフの中に{name}を含めないでください。

▼選択肢の種類（1つずつ生成）
- #v-good: ユーザーが{name}に対して発するとても好意的なセリフ（好感度+10）
- #good: ユーザーが{name}に対して発するやや好意的なセリフ（好感度+5）
- #bad: ユーザーが{name}に対して発するやや悪印象なセリフ（好感度-5）
- #v-bad: ユーザーが{name}に対して発する非常に悪印象なセリフ（好感度-10）

▼フォーマット（厳守）
1. 「～」 #v-good
2. 「～」 #good
3. 「～」 #bad
4. 「～」 #v-bad

▼ルール
- ユーザーの発言として自然で理解しやすい内容にする
- 行頭の番号と「.」は半角固定
- 直前の{name}の発言内容に適切に反応する選択肢を生成する
- 会話の流れを考慮した自然な選択肢を生成する
"""

        return options_prompt

    def _generate_with_openai(self, prompt, is_character=True):
        if is_character:
            system_content = "あなたは指定されたキャラクターになりきって、自然なメッセージを生成するアシスタントです。"
        else:
            system_content = "あなたは会話システムの管理者として、ユーザーのセリフを生成するアシスタントです。"
            
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=1.0
        )
        return response.choices[0].message.content.strip()

    def _parse_options_only(self, response_text):
        options = []
        lines = [line.strip() for line in response_text.splitlines() if line.strip()]

        # Parse option lines
        for line in lines:
            try:
                # 「番号. テキスト #tag」の形式を分解
                num, rest = line.split(".", 1)
                text, tag = rest.rsplit("#", 1)
                options.append({"text": text.strip(" 「」"), "type": tag.strip()})
            except ValueError:
                # Ignore malformed option lines
                continue
        
        return options
  
    

    def get_characters(self):
        return list(self.characters.keys())


