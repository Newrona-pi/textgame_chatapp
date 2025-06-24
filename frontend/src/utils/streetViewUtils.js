// Google Street View Static APIの設定
const GOOGLE_API_KEY = import.meta.env.VITE_GOOGLE_API_KEY || 'YOUR_GOOGLE_API_KEY';
const STREET_VIEW_BASE_URL = 'https://maps.googleapis.com/maps/api/streetview';

/**
 * 位置情報からGoogle Street View画像のURLを生成
 * @param {number} lat - 緯度
 * @param {number} lon - 経度
 * @param {number} width - 画像の幅（デフォルト: 1920）
 * @param {number} height - 画像の高さ（デフォルト: 1080）
 * @param {number} heading - カメラの向き（0-360度、デフォルト: 0）
 * @param {number} pitch - カメラの傾き（-90-90度、デフォルト: 0）
 * @param {number} fov - 視野角（0-120度、デフォルト: 90）
 * @returns {string} Street View画像のURL
 */
export function getStreetViewUrl(lat, lon, width = 1920, height = 1080, heading = 0, pitch = 0, fov = 90) {
  if (!GOOGLE_API_KEY || GOOGLE_API_KEY === 'YOUR_GOOGLE_API_KEY') {
    console.warn('Google APIキーが設定されていません');
    return null;
  }

  const params = new URLSearchParams({
    size: `${width}x${height}`,
    location: `${lat},${lon}`,
    heading: heading.toString(),
    pitch: pitch.toString(),
    fov: fov.toString(),
    key: GOOGLE_API_KEY
  });

  return `${STREET_VIEW_BASE_URL}?${params.toString()}`;
}

/**
 * 位置情報から複数の角度のStreet View画像を取得
 * @param {number} lat - 緯度
 * @param {number} lon - 経度
 * @returns {Array} 複数の角度の画像URL配列
 */
export function getMultipleStreetViewUrls(lat, lon) {
  const angles = [0, 90, 180, 270]; // 北、東、南、西の4方向
  return angles.map(heading => getStreetViewUrl(lat, lon, 1920, 1080, heading));
}

/**
 * 画像の存在確認
 * @param {string} url - 画像URL
 * @returns {Promise<boolean>} 画像が存在するかどうか
 */
export async function checkImageExists(url) {
  if (!url) return false;
  
  try {
    const response = await fetch(url, { method: 'HEAD' });
    return response.ok;
  } catch (error) {
    console.error('画像の存在確認に失敗:', error);
    return false;
  }
}

/**
 * 位置情報から最適なStreet View画像を取得
 * @param {number} lat - 緯度
 * @param {number} lon - 経度
 * @returns {Promise<string|null>} 利用可能な画像URLまたはnull
 */
export async function getBestStreetViewImage(lat, lon) {
  if (!lat || !lon) return null;

  // 複数の角度で画像を試行
  const urls = getMultipleStreetViewUrls(lat, lon);
  
  for (const url of urls) {
    if (url && await checkImageExists(url)) {
      return url;
    }
  }
  
  return null;
}

/**
 * 位置情報から都道府県の代表的な観光地の座標を取得
 * @param {string} prefecture - 都道府県名
 * @returns {Object|null} 緯度・経度のオブジェクト
 */
export function getPrefectureLandmark(prefecture) {
  const landmarks = {
    '北海道': { lat: 43.0618, lon: 141.3545 }, // 札幌時計台
    '青森県': { lat: 40.8243, lon: 140.7403 }, // 青森市
    '岩手県': { lat: 39.7036, lon: 141.1527 }, // 盛岡市
    '宮城県': { lat: 38.2688, lon: 140.8721 }, // 仙台市
    '秋田県': { lat: 39.7186, lon: 140.1023 }, // 秋田市
    '山形県': { lat: 38.2554, lon: 140.3398 }, // 山形市
    '福島県': { lat: 37.7503, lon: 140.4675 }, // 福島市
    '茨城県': { lat: 36.3418, lon: 140.4468 }, // 水戸市
    '栃木県': { lat: 36.5657, lon: 139.8836 }, // 宇都宮市
    '群馬県': { lat: 36.3907, lon: 139.0604 }, // 前橋市
    '埼玉県': { lat: 35.8574, lon: 139.6489 }, // さいたま市
    '千葉県': { lat: 35.6051, lon: 140.1233 }, // 千葉市
    '東京都': { lat: 35.6895, lon: 139.6917 }, // 東京タワー
    '神奈川県': { lat: 35.4478, lon: 139.6425 }, // 横浜市
    '新潟県': { lat: 37.9024, lon: 139.0232 }, // 新潟市
    '富山県': { lat: 36.6953, lon: 137.2113 }, // 富山市
    '石川県': { lat: 36.5947, lon: 136.6256 }, // 金沢市
    '福井県': { lat: 36.0652, lon: 136.2216 }, // 福井市
    '山梨県': { lat: 35.6642, lon: 138.5684 }, // 甲府市
    '長野県': { lat: 36.6513, lon: 138.1812 }, // 長野市
    '岐阜県': { lat: 35.3912, lon: 136.7223 }, // 岐阜市
    '静岡県': { lat: 34.9770, lon: 138.3831 }, // 静岡市
    '愛知県': { lat: 35.1802, lon: 136.9066 }, // 名古屋市
    '三重県': { lat: 34.7303, lon: 136.5086 }, // 津市
    '滋賀県': { lat: 35.0045, lon: 135.8686 }, // 大津市
    '京都府': { lat: 35.0210, lon: 135.7556 }, // 京都駅
    '大阪府': { lat: 34.6863, lon: 135.5197 }, // 大阪城
    '兵庫県': { lat: 34.6903, lon: 135.1955 }, // 神戸市
    '奈良県': { lat: 34.6853, lon: 135.8327 }, // 奈良市
    '和歌山県': { lat: 34.2260, lon: 135.1675 }, // 和歌山市
    '鳥取県': { lat: 35.5039, lon: 134.2377 }, // 鳥取市
    '島根県': { lat: 35.4723, lon: 133.0505 }, // 松江市
    '岡山県': { lat: 34.6618, lon: 133.9347 }, // 岡山市
    '広島県': { lat: 34.3966, lon: 132.4596 }, // 広島市
    '山口県': { lat: 34.1861, lon: 131.4705 }, // 山口市
    '徳島県': { lat: 34.0658, lon: 134.5593 }, // 徳島市
    '香川県': { lat: 34.3401, lon: 134.0434 }, // 高松市
    '愛媛県': { lat: 33.8417, lon: 132.7654 }, // 松山市
    '高知県': { lat: 33.5597, lon: 133.5311 }, // 高知市
    '福岡県': { lat: 33.6068, lon: 130.4183 }, // 福岡市
    '佐賀県': { lat: 33.2494, lon: 130.2988 }, // 佐賀市
    '長崎県': { lat: 32.7448, lon: 129.8738 }, // 長崎市
    '熊本県': { lat: 32.7898, lon: 130.7417 }, // 熊本市
    '大分県': { lat: 33.2382, lon: 131.6126 }, // 大分市
    '宮崎県': { lat: 31.9111, lon: 131.4239 }, // 宮崎市
    '鹿児島県': { lat: 31.5601, lon: 130.5580 }, // 鹿児島市
    '沖縄県': { lat: 26.2124, lon: 127.6809 }  // 那覇市
  };

  return landmarks[prefecture] || null;
} 