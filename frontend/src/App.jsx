import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import characterImage from './assets/character.png'
import backgroundImage from './assets/background.png'
import heartIcon from './assets/heart.png' // 追加
import brokenHeartIcon from './assets/broken-heart.png' // 追加
import { getPrefectureFromLocation, getPrefectureImage, getDetailedAddress, formatAddress } from './utils/locationUtils.js'
import { getBestStreetViewImage, getPrefectureLandmark } from './utils/streetViewUtils.js'
import { API_ENDPOINTS } from './config/api.js'
import './App.css'
import { Routes, Route, useParams, useNavigate } from 'react-router-dom'

function CharacterChat() {
  const { characterId } = useParams();
  const navigate = useNavigate();

  const [message, setMessage] = useState('こんにちは！今日もお疲れさまです。')
  const [options, setOptions] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [characterName, setCharacterName] = useState('')
  const [currentDateTime, setCurrentDateTime] = useState(new Date())
  const [conversationHistory, setConversationHistory] = useState([])
  const [isDialogueMode, setIsDialogueMode] = useState(false)
  const [effects, setEffects] = useState([])
  const [location, setLocation] = useState({ lat: null, lon: null });
  const [currentBackground, setCurrentBackground] = useState(backgroundImage);
  const [currentPrefecture, setCurrentPrefecture] = useState(null);
  const [isLoadingBackground, setIsLoadingBackground] = useState(false);
  const [affectionLevel, setAffectionLevel] = useState(40);
  const [detailedAddress, setDetailedAddress] = useState(null);
  const [isMessageBoxVisible, setIsMessageBoxVisible] = useState(true);
  const [characters, setCharacters] = useState([]);
  const [currentCharacter, setCurrentCharacter] = useState(null);
  const [currentCharacterImage, setCurrentCharacterImage] = useState(characterImage);
  const [isLoadingCharacters, setIsLoadingCharacters] = useState(false);

  // 日付・時刻を1秒ごとに更新
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      pos  => setLocation({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
      ()   => setLocation({ lat: null, lon: null })
    );
  }, []);

  // キャラクター情報を読み込む
  useEffect(() => {
    loadCharacters();
  }, []);

  // キャラクター一覧を読み込む
  const loadCharacters = async () => {
    setIsLoadingCharacters(true);
    try {
      const response = await fetch(API_ENDPOINTS.CHARACTERS);
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setCharacters(data.characters);
          // URLのcharacterIdに一致するキャラを選択
          if (data.characters.length > 0) {
            const found = data.characters.find(c => c.id === characterId);
            if (found) {
              selectCharacter(found);
            } else {
              // 存在しないキャラIDならトップにリダイレクト
              navigate('/character/' + data.characters[0].id, { replace: true });
            }
          }
        }
      }
    } catch (error) {
      console.error('Error loading characters:', error);
    }
    setIsLoadingCharacters(false);
  };

  // キャラクターを選択する
  const selectCharacter = async (character) => {
    setCurrentCharacter(character);
    setCharacterName(character.name);
    if (character.character_image_url) {
      setCurrentCharacterImage(character.character_image_url);
    } else {
      setCurrentCharacterImage(characterImage);
    }
    if (character.background_image_url) {
      setCurrentBackground(character.background_image_url);
    } else {
      if (location.lat && location.lon) {
        const prefecture = getPrefectureFromLocation(location.lat, location.lon);
        if (prefecture) {
          const backgroundPath = getPrefectureImage(prefecture);
          setCurrentBackground(backgroundPath);
        } else {
          setCurrentBackground(backgroundImage);
        }
      } else {
        setCurrentBackground(backgroundImage);
      }
    }
    resetDialogue();
  };

  // 位置情報が変更されたときに背景画像を更新
  useEffect(() => {
    const updateBackground = async () => {
      if (location.lat && location.lon) {
        setIsLoadingBackground(true);
        const prefecture = getPrefectureFromLocation(location.lat, location.lon);
        setCurrentPrefecture(prefecture);
        
        // 詳細な住所情報を取得
        try {
          const addressInfo = await getDetailedAddress(location.lat, location.lon);
          setDetailedAddress(addressInfo);
        } catch (error) {
          console.error('住所取得エラー:', error);
          setDetailedAddress(null);
        }
        
        if (prefecture) {
          // まず現在地でStreet View画像を試行
          let streetViewUrl = await getBestStreetViewImage(location.lat, location.lon);
          
          // 現在地でStreet View画像が取得できない場合、都道府県の代表的な観光地を試行
          if (!streetViewUrl) {
            const landmark = getPrefectureLandmark(prefecture);
            if (landmark) {
              streetViewUrl = await getBestStreetViewImage(landmark.lat, landmark.lon);
            }
          }
          
          if (streetViewUrl) {
            setCurrentBackground(streetViewUrl);
          } else {
            // Street View画像が取得できない場合、ローカルの背景画像を使用
            const backgroundPath = getPrefectureImage(prefecture);
            const img = new Image();
            img.onload = () => {
              setCurrentBackground(backgroundPath);
            };
            img.onerror = () => {
              setCurrentBackground(backgroundImage);
            };
            img.src = backgroundPath;
          }
        } else {
          setCurrentBackground(backgroundImage);
        }
        setIsLoadingBackground(false);
      } else {
        setCurrentBackground(backgroundImage);
        setCurrentPrefecture(null);
        setDetailedAddress(null);
        setIsLoadingBackground(false);
      }
    };

    updateBackground();
  }, [location.lat, location.lon]);

  // 日付をフォーマット (YYYY/M/D/WeekdayName 形式)
  const formatDate = (date) => {
    const year = date.getFullYear()
    const month = date.getMonth() + 1 // 月は0から始まるため+1
    const day = date.getDate()
    const weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    const weekday = weekdays[date.getDay()]
    
    return `${year}/${month}/${day}/${weekday}`
  }

  // 時刻をフォーマット
  const formatTime = (date) => {
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    
    return `${hours}:${minutes}:${seconds}`
  }

  // 会話を開始する
  const startDialogue = async () => {
    if (!currentCharacter) {
      setMessage('キャラクターが選択されていません。');
      return;
    }
    
    setIsLoading(true)
    setIsDialogueMode(true)
    setConversationHistory([])
    
    try {
      const response = await fetch(API_ENDPOINTS.DIALOGUE_START, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_id: currentCharacter.id,
          lat: location.lat,
          lon: location.lon,
          affection_level: affectionLevel // 好感度パラメーターを追加
        }),
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage(data.message)
        setOptions(data.options)
      } else {
        setMessage('会話の開始に失敗しました。')
        setOptions([])
      }
    } catch (error) {
      console.error('Error starting dialogue:', error)
      setMessage('エラーが発生しました。')
      setOptions([])
    }
    setIsLoading(false)
  }

  // エフェクト表示ロジック
  const showEffect = (optionType) => {
    const newEffects = []
    let effectCount = 0
    let effectIcon = heartIcon
    
    // タイプに応じてエフェクトの数とアイコンを決定
    switch (optionType) {
      case 'v-good':
        effectCount = 6
        effectIcon = heartIcon
        break
      case 'good':
        effectCount = 2
        effectIcon = heartIcon
        break
      case 'bad':
        effectCount = 2
        effectIcon = brokenHeartIcon
        break
      case 'v-bad':
        effectCount = 6
        effectIcon = brokenHeartIcon
        break
      default:
        effectCount = 1
        effectIcon = heartIcon
    }
  
    // エフェクトを生成
    for (let i = 0; i < effectCount; i++) {
      const effect = {
        id: Date.now() + i,
        icon: effectIcon,
        x: Math.random() * 200 - 100, // -100px から 100px の範囲
        y: Math.random() * 200 - 100, // -100px から 100px の範囲
        delay: i * 200 // 200ms間隔で表示
      }
      newEffects.push(effect)
    }
  
    setEffects(newEffects)
  
    // 3秒後にエフェクトを削除
    setTimeout(() => {
      setEffects([])
    }, 3000)
  }

  // ユーザーの選択を処理する
  const handleOptionSelect = async (option) => { // optionオブジェクトを受け取るように変更
    if (!currentCharacter) {
      setMessage('キャラクターが選択されていません。');
      return;
    }
    
    setIsLoading(true)
    
    // 好感度を更新
    let newAffectionLevel = affectionLevel
    switch (option.type) {
      case 'v-good':
        newAffectionLevel = Math.min(100, affectionLevel + 10)
        break
      case 'good':
        newAffectionLevel = Math.min(100, affectionLevel + 5)
        break
      case 'bad':
        newAffectionLevel = Math.max(0, affectionLevel - 5)
        break
      case 'v-bad':
        newAffectionLevel = Math.max(0, affectionLevel - 10)
        break
    }
    setAffectionLevel(newAffectionLevel)
    
    // エフェクトを表示
    showEffect(option.type)
    
    // 会話履歴を更新
    const newHistory = [...conversationHistory, {
      user: option.text, // option.textを履歴に追加
      character: message
    }]
    setConversationHistory(newHistory)
    
    try {
      const response = await fetch(API_ENDPOINTS.DIALOGUE_NEXT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_id: currentCharacter.id,
          user_choice: option.text, // option.textを送信
          conversation_history: newHistory,
          lat: location.lat,
          lon: location.lon,
          affection_level: newAffectionLevel // 計算した新しい好感度を送信
        }),
      })
      
      if (response.ok) {
        const data = await response.json()
        setMessage(data.message)
        setOptions(data.options)
      } else {
        setMessage('次の会話の取得に失敗しました。')
        setOptions([])
      }
    } catch (error) {
      console.error('Error getting next dialogue:', error)
      setMessage('エラーが発生しました。')
      setOptions([])
    }
    setIsLoading(false)
  }

  // 会話をリセットする
  const resetDialogue = () => {
    setIsDialogueMode(false)
    setConversationHistory([])
    setOptions([])
    setMessage('やっほー！今日もお疲れ！')
    setAffectionLevel(40) // 好感度を初期値にリセット
  }

  useEffect(() => {
    // 初期メッセージを設定
    const initialMessages = [
      'こんにちは！今日もお疲れさまです。',
      'おはようございます！今日も一日頑張りましょうね。',
      'お疲れさまでした！今日はどんな一日でしたか？'
    ]
    setMessage(initialMessages[Math.floor(Math.random() * initialMessages.length)])
  }, [])

  // 好感度レベルに応じた色を取得する関数
  const getAffectionColor = (level) => {
    if (level >= 80) return '#ff6b9d'; // ピンク（最高）
    if (level >= 60) return '#ff8c42'; // オレンジ（高）
    if (level >= 40) return '#6bcf7f'; // 緑（中）
    if (level >= 20) return '#ffd93d'; // 黄色（低）
    return '#ff6b6b'; // 赤（最低）
  };

  // 好感度レベルに応じたメッセージを取得する関数
  const getAffectionMessage = (level) => {
    if (level >= 80) return '大好き！';
    if (level >= 60) return '好き';
    if (level >= 40) return '普通';
    if (level >= 20) return '苦手';
    return '大嫌い';
  };

  // メッセージボックスの表示/非表示を切り替える
  const toggleMessageBox = () => {
    setIsMessageBoxVisible(!isMessageBoxVisible);
  };

  return (
    <div className="game-container">
      {/* 日付・時刻表示を追加 */}
      <div className="datetime-display">
        <div className="date">{formatDate(currentDateTime)}</div>
        <div className="time">{formatTime(currentDateTime)}</div>
        
        {/* 詳細な住所表示を日付の下に追加 */}
        {detailedAddress && (
          <div className="address-display">
            <div className="address-text">{formatAddress(detailedAddress)}</div>
            {isLoadingBackground && (
              <div className="loading-indicator">背景画像読み込み中...</div>
            )}
          </div>
        )}
      </div>

      {/* 好感度表示を追加 */}
      <div className="affection-display">
        <div className="affection-label">好感度</div>
        <div className="affection-bar">
          <div 
            className="affection-fill"
            style={{ 
              width: `${affectionLevel}%`,
              backgroundColor: getAffectionColor(affectionLevel)
            }}
          ></div>
        </div>
        <div className="affection-level">
          {affectionLevel}
        </div>
        <div className="affection-message">
          {getAffectionMessage(affectionLevel)}
        </div>
      </div>

      {/* スクリーンショット用ボタン */}
      <div className="screenshot-controls">
        <Button 
          onClick={toggleMessageBox}
          variant="outline"
          className="screenshot-button"
          title="メッセージボックスを表示/非表示にしてスクリーンショットを撮りやすくします"
        >
          {isMessageBoxVisible ? '📷 メッセージ非表示' : '📷 メッセージ表示'}
        </Button>
      </div>

      <img 
        src={currentBackground} 
        alt="背景画像" 
        className="background-image"
        style={{ opacity: isLoadingBackground ? 0.5 : 1 }}
      />
      
      <div className="character-container">
        <img 
          src={currentCharacterImage} 
          alt="真乃ちゃん" 
          className="character-image"
        />
        {/* エフェクト表示 */}
        {effects.map((effect) => (
          <div
            key={effect.id}
            className="effect-heart"
            style={{
              left: `calc(50% + ${effect.x}px)`,
              top: `calc(50% + ${effect.y}px)`,
              animationDelay: `${effect.delay}ms`
            }}
          >
            <img src={effect.icon} alt="effect" className="effect-icon" />
          </div>
        ))}
      </div>

      <div className={`message-box ${!isMessageBoxVisible ? 'hidden' : ''}`}>
        <div className="character-name">
          {characterName}
        </div>
        <div className="message-text">
          {isLoading ? (
            <span className="loading-dots"> </span>
          ) : (
            message
          )}
        </div>
        
        {/* 4択選択肢を表示 */}
        {isDialogueMode && options.length > 0 && !isLoading && (
          <div className="options-container">
            {options.map((option, index) => (
              <Button
                key={index}
                onClick={() => handleOptionSelect(option)}
                className="option-button"
                variant="outline"
              >
                {option.text} {/* option.textを表示 */}
              </Button>
            ))}
          </div>
        )}
        
        {/* アクションボタン */}
        <div className="action-buttons">
          {!isDialogueMode ? (
            <Button 
              onClick={startDialogue} 
              ddisabled={isLoading || location.lat === null}
              className="bg-pink-500 hover:bg-pink-600 text-white px-6 py-2 rounded-full transition-colors duration-200"
            >
              会話を始める
            </Button>
          ) : (
            <Button 
              onClick={resetDialogue}
              disabled={isLoading}
              variant="outline"
              className="border-pink-500 text-pink-500 px-6 py-2 rounded-full transition-colors duration-200"
            >
              会話をリセット
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/character/:characterId" element={<CharacterChat />} />
      {/* 必要ならトップページや404ページも追加可能 */}
    </Routes>
  );
}


