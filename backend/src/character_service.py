import csv
import os
import random
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
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
    """都道府県 + 市区町村 + 町名 + 丁目 + 番地 などを返す"""
    if lat is None or lon is None:
        return None, None, None

    key = f"{round(lat,3)},{round(lon,3)}"
    if key in _geo_cache:
        return _geo_cache[key]

    try:
        loc = _geocoder.reverse(
            (lat, lon),
            language="ja",
            zoom=16,  # より詳細な住所を取得
            timeout=2,
        )
        addr = loc.raw.get("address", {}) if loc else {}

        # 都道府県
        pref = addr.get("state") or addr.get("region") or addr.get("province")
        # 市区町村
        city = (
            addr.get("city") or addr.get("town") or addr.get("village")
            or addr.get("municipality") or addr.get("county")
        )
        # 町名・丁目・番地など
        suburb = addr.get("suburb")
        neighbourhood = addr.get("neighbourhood")
        road = addr.get("road")
        house_number = addr.get("house_number")
        # 詳細住所文字列を生成
        detailed_address = f"{pref or ''}{city or ''}{suburb or ''}{neighbourhood or ''}{road or ''}{house_number or ''}"
        _geo_cache[key] = (pref, city, detailed_address)
        return pref, city, detailed_address

    except Exception as e:
        logger.warning("Geocode failed: %s", e)
        return None, None, None


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
                    if 'キャラクターID' not in row:
                        print(f"Missing キャラクターID in row: {row}")
                        continue
                    characters[row['キャラクターID']] = row
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
        
        pref, city, detailed_address = _latlon_to_pref_city(lat, lon) or ("場所不明", "", "")
        return {
            "date": now.strftime("%Y年%m月%d日"),
            "season": season,
            "season_detail": season_detail,
            "time_period": time_period,
            "time_detail": time_detail,
            "weekday": weekday,
            "hour": now.hour,
            "pref": pref, 
            "city": city,
            "detailed_address": detailed_address,
        }

    def generate_initial_dialogue(self, character_id, lat=None, lon=None, affection_level=40):
        print("TEST")
        print(f"Generating initial dialogue for character_id: {character_id} with affection_level: {affection_level}")
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。", "options": [], "debug_affection_level": affection_level}

        context = self._get_current_context(lat, lon)
        character_prompt = self._build_initial_character_prompt(character_data, context, affection_level)
        
        try:
            # キャラクター発言を生成
            character_response = self._generate_with_openai(character_prompt, is_character=True)
            message = character_response.strip()
            
            # キャラクター発言内容を4択選択肢生成プロンプトに渡す
            gender = character_data['性別']
            options_prompt = self._build_initial_options_prompt(character_data, message, gender)
            options_response = self._generate_with_openai(options_prompt, is_character=False)
            options = self._parse_options_only(options_response)
            
            random.shuffle(options)
            return {"message": message, "options": options, "debug_affection_level": affection_level}
        except Exception as e:
            return {"message": f"初期会話生成エラー: {str(e)}", "options": [], "debug_affection_level": affection_level}

    def generate_next_dialogue(self, character_id, user_choice, conversation_history, lat=None, lon=None, affection_level=None):
        print("TEST")
        print(f"Generating next dialogue for character_id: {character_id} with affection_level: {affection_level}")
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。", "options": [], "debug_affection_level": affection_level}

        context = self._get_current_context(lat, lon)
        character_prompt = self._build_next_character_prompt(character_data, user_choice, conversation_history, context, affection_level)

        try:
            # キャラクター発言を生成
            character_response = self._generate_with_openai(character_prompt, is_character=True)
            message = character_response.strip()
            
            # キャラクター発言内容を4択選択肢生成プロンプトに渡す
            gender = character_data['性別']
            options_prompt = self._build_next_options_prompt(character_data, message, user_choice, conversation_history, gender)
            options_response = self._generate_with_openai(options_prompt, is_character=False)
            options = self._parse_options_only(options_response)
            
            random.shuffle(options)
            return {"message": message, "options": options, "debug_affection_level": affection_level}
        except Exception as e:
            return {"message": f"次の会話生成エラー: {str(e)}", "options": [], "debug_affection_level": affection_level}

    def generate_character_message(self, character_id, user_choice, conversation_history, lat=None, lon=None, affection_level=None):
        print(f"[character_message] affection_level: {affection_level}")
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"message": "キャラクターが見つかりません。"}

        context = self._get_current_context(lat, lon)
        character_prompt = self._build_next_character_prompt(character_data, user_choice, conversation_history, context, affection_level)
        try:
            character_response = self._generate_with_openai(character_prompt, is_character=True)
            message = character_response.strip()
            return {"message": message}
        except Exception as e:
            return {"message": f"キャラクター発言生成エラー: {str(e)}"}

    def generate_options(self, character_id, character_message, user_choice, conversation_history, lat=None, lon=None, affection_level=None):
        print(f"[options] affection_level: {affection_level}")
        character_data = self.characters.get(character_id)
        if not character_data:
            return {"options": []}
        gender = character_data['性別']
        options_prompt = self._build_next_options_prompt(character_data, character_message, user_choice, conversation_history, gender)
        try:
            options_response = self._generate_with_openai(options_prompt, is_character=False)
            options = self._parse_options_only(options_response)
            random.shuffle(options)
            return {"options": options}
        except Exception as e:
            return {"options": []}

    def _build_initial_character_prompt(self, character_data, context, affection_level):
        name        = character_data['名前']
        gender      = character_data['性別']
        personality = character_data['性格']
        first_person = character_data['一人称']
        fan_name    = character_data['ファンの名称']
        tone        = character_data['口調']
        setting     = character_data['背景・設定']
        
        # キャラクター発言生成用プロンプト
        character_prompt = f"""
あなたは{gender}の{personality}キャラクターです。
一人称は「{first_person}」で、ファンのことを「{fan_name}」と呼びます。
{tone}で話し、{setting}という設定です。

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
- 現在地: {context['detailed_address']} 

好感度{affection_level}に適した言葉遣いで、「{context['detailed_address']} 」らしさ（位置情報から取得した場所の名所など）を盛り込んだ自然なメッセージを生成してください。
質問文は一回の会話につき、一つだけにしてください。

▼ルール
- {name}のセリフのみを生成する
- 好感度{affection_level}の言葉遣いを必ず適用する
- Pythonで200文字以内になるように生成する
"""

        return character_prompt

    def _build_initial_options_prompt(self, character_data, character_message, gender):
        name = character_data['名前']
        
        # システムによる4択選択肢生成用プロンプト
        options_prompt = f"""
あなたは{name}とは別人で、{name}の{gender}とは違う性別の同級生です。一人称は「僕」です。{name}というキャラクターに対して、返答となるセリフの選択肢を4つ生成してください。
必ず一人称視点のセリフを生成してください。セリフの中に{name}を含めないでください。

直前の{name}の発言: 「{character_message}」


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
- 必須: キャラクターの直前セリフに
明確な質問（Who / What / When / Where / Why / How / どんな…?）が含まれる場合、候補a は必ず“質問に直接答える具体的な返答” にする。
"""

        return options_prompt

    def _build_next_character_prompt(self, character_data, user_choice, conversation_history, context, affection_level=None):
        name        = character_data['名前']
        gender      = character_data['性別']
        personality = character_data['性格']
        first_person = character_data['一人称']
        fan_name    = character_data['ファンの名称']
        tone        = character_data['口調']
        setting     = character_data['背景・設定']

        history_str = "\n".join(
            f"ユーザー: {h['user']}\n{name}: {h['character']}" for h in conversation_history
        )

        # キャラクター発言生成用プロンプト
        character_prompt = f"""
# キャラクター設定
あなたは{gender}の{personality}キャラクター「{name}」です。
- 一人称: {first_person}
- ファンの呼び方: {fan_name}
- 口調: {tone}
- 背景: {setting}

# 応答生成の思考プロセス
以下のステップに従って、論理的で一貫性のある応答を生成してください。

1.  **会話の文脈分析:**
    -   これまでの会話履歴を読み、現在の主要な話題を特定します。
    -   ユーザーが選択した「{user_choice}」という発言の意図（例：同意、質問、感情表現、話題転換など）を分析します。

2.  **応答方針の決定:**
    -   分析した意図に基づき、応答の方針を決定します。（例：「ユーザーの意見に共感し、関連する自分の体験を話す」「ユーザーの質問に具体的に答え、逆質問を投げかける」など）

3.  **発言の生成:**
    -   決定した方針と、以下の【絶対厳守ルール】に従って、{name}としての自然なセリフを生成します。

# 【絶対厳守ルール】
- **好感度レベルの適用:** 現在の好感度「{affection_level}」に応じて、下記の対応表から適切な言葉遣いを厳密に選択してください。
    - 81~100: 好意的で甘い表現（例：「素敵ですね♪」「大好き」「一緒にいると楽しい」）
    - 61~80: 友達のようなフランクで親しみやすい表現（例：「そうだね！」「いいじゃん」「楽しそう」）
    - 41~60: 普通の丁寧で標準的な表現（例：「そうですね」「はい」「いいと思います」）
    - 21~40: そっけない、少し距離のある表現（例：「ふーん」「そうですか」）
    - 0~20: 憤りや拒絶を感じさせる冷たい表現（例：「意味が分かりません」「もういいです」）
- **セリフのみ出力:** {name}のセリフのみを生成し、思考プロセスや説明は一切含めないでください。
- **文字数:** 200文字以内で簡潔にまとめてください。
- **質問:** 質問は1回の発言につき1つまでです。

# 状況
- 現在の状況: {context['date']} {context['weekday']} {context['time_period']} ({context['time_detail']})
- 現在地: {context['detailed_address']} （この情報を会話に自然に含めても良い）

# 会話履歴
{history_str}
ユーザー: 「{user_choice}」

上記すべてを考慮し、{name}の次のセリフを生成してください。
"""

        return character_prompt

    def _build_next_options_prompt(self, character_data, character_message, user_choice, conversation_history,gender):
        name = character_data['名前']
        
        history_str = "\n".join(
            f"ユーザー: {h['user']}\n{name}: {h['character']}" for h in conversation_history
        )

        # システムによる4択選択肢生成用プロンプト
        options_prompt = f"""
あなたは{name}とは別人で、{name}の{gender}とは違う性別の同級生です。一人称は「僕」です。{name}というキャラクターに対して、返答となるセリフの選択肢を4つ生成してください。
必ず一人称視点のセリフを生成してください。セリフの中に{name}を含めないでください。

直前の{name}の発言: 「{character_message}」
ユーザーの直前の選択: 「{user_choice}」

これまでの会話履歴:
{history_str}

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
- 必須: キャラクターの直前セリフに
明確な質問（Who / What / When / Where / Why / How / どんな…?）が含まれる場合、候補a は必ず“質問に直接答える具体的な返答” にする。
- **トーンの幅**を持たせる  
- a) 共感・肯定  
- b) 質問・深掘り  
- c) ユーモア・軽口  
- d) 行動提案 or 別視点  
- 直前の話題や直前の履歴に沿った自然な選択肢のみを生成する
"""
        return options_prompt

    def _generate_with_openai(self, prompt, is_character=True):
        if is_character:
            system_content = "あなたは指定されたキャラクターになりきって、自然なメッセージを生成するVtuberです。"
        else:
            system_content = "あなたはVtuberの同級生の男性です。"
            
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
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