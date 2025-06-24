// 都道府県の座標データ（簡略化版）
const prefectureCoordinates = {
  '北海道': { lat: 43.064359, lon: 141.346814 },
  '青森県': { lat: 40.824308, lon: 140.740259 },
  '岩手県': { lat: 39.703619, lon: 141.152684 },
  '宮城県': { lat: 38.268837, lon: 140.872103 },
  '秋田県': { lat: 39.718600, lon: 140.102334 },
  '山形県': { lat: 38.255438, lon: 140.339848 },
  '福島県': { lat: 37.750299, lon: 140.467521 },
  '茨城県': { lat: 36.341813, lon: 140.446793 },
  '栃木県': { lat: 36.565725, lon: 139.883565 },
  '群馬県': { lat: 36.390668, lon: 139.060406 },
  '埼玉県': { lat: 35.857428, lon: 139.648933 },
  '千葉県': { lat: 35.605058, lon: 140.123308 },
  '東京都': { lat: 35.689521, lon: 139.691704 },
  '神奈川県': { lat: 35.447753, lon: 139.642514 },
  '新潟県': { lat: 37.902418, lon: 139.023221 },
  '富山県': { lat: 36.695291, lon: 137.211338 },
  '石川県': { lat: 36.594682, lon: 136.625573 },
  '福井県': { lat: 36.065219, lon: 136.221642 },
  '山梨県': { lat: 35.664158, lon: 138.568449 },
  '長野県': { lat: 36.651289, lon: 138.181224 },
  '岐阜県': { lat: 35.391227, lon: 136.722291 },
  '静岡県': { lat: 34.976978, lon: 138.383054 },
  '愛知県': { lat: 35.180188, lon: 136.906564 },
  '三重県': { lat: 34.730283, lon: 136.508591 },
  '滋賀県': { lat: 35.004531, lon: 135.868590 },
  '京都府': { lat: 35.021004, lon: 135.755608 },
  '大阪府': { lat: 34.686316, lon: 135.519711 },
  '兵庫県': { lat: 34.690279, lon: 135.195475 },
  '奈良県': { lat: 34.685333, lon: 135.832744 },
  '和歌山県': { lat: 34.226034, lon: 135.167506 },
  '鳥取県': { lat: 35.503869, lon: 134.237672 },
  '島根県': { lat: 35.472297, lon: 133.050499 },
  '岡山県': { lat: 34.661772, lon: 133.934675 },
  '広島県': { lat: 34.396560, lon: 132.459622 },
  '山口県': { lat: 34.186121, lon: 131.470500 },
  '徳島県': { lat: 34.065770, lon: 134.559303 },
  '香川県': { lat: 34.340149, lon: 134.043444 },
  '愛媛県': { lat: 33.841660, lon: 132.765362 },
  '高知県': { lat: 33.559705, lon: 133.531080 },
  '福岡県': { lat: 33.606785, lon: 130.418314 },
  '佐賀県': { lat: 33.249367, lon: 130.298822 },
  '長崎県': { lat: 32.744839, lon: 129.873756 },
  '熊本県': { lat: 32.789828, lon: 130.741667 },
  '大分県': { lat: 33.238194, lon: 131.612591 },
  '宮崎県': { lat: 31.911096, lon: 131.423855 },
  '鹿児島県': { lat: 31.560148, lon: 130.557981 },
  '沖縄県': { lat: 26.212401, lon: 127.680932 }
};

// 2点間の距離を計算する関数（ハバーサイン公式）
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // 地球の半径（km）
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// 位置情報から最も近い都道府県を判定する関数
export function getPrefectureFromLocation(lat, lon) {
  if (!lat || !lon) return null;
  
  let closestPrefecture = null;
  let minDistance = Infinity;
  
  for (const [prefecture, coords] of Object.entries(prefectureCoordinates)) {
    const distance = calculateDistance(lat, lon, coords.lat, coords.lon);
    if (distance < minDistance) {
      minDistance = distance;
      closestPrefecture = prefecture;
    }
  }
  
  return closestPrefecture;
}

// 都道府県名から画像ファイル名を取得する関数
export function getPrefectureImage(prefecture) {
  if (!prefecture) return '/backgrounds/default.jpg';
  
  // 都道府県名をファイル名用に変換
  const imageName = prefecture.replace('県', '').replace('府', '').replace('都', '');
  return `/backgrounds/${imageName}.jpg`;
}

/**
 * 位置情報から詳細な住所を取得する関数
 * @param {number} lat - 緯度
 * @param {number} lon - 経度
 * @returns {Promise<Object|null>} 住所情報オブジェクト
 */
export async function getDetailedAddress(lat, lon) {
  if (!lat || !lon) return null;

  try {
    // 逆ジオコーディングAPIを使用して住所を取得
    const response = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1&accept-language=ja`
    );
    
    if (!response.ok) {
      throw new Error('住所取得に失敗しました');
    }

    const data = await response.json();
    
    if (data.address) {
      const address = data.address;
      
      // 日本の住所形式に変換
      const prefecture = address.state || address.province || '';
      const city = address.city || address.town || address.village || '';
      const district = address.suburb || address.neighbourhood || '';
      const street = address.road || '';
      
      return {
        prefecture: prefecture,
        city: city,
        district: district,
        street: street,
        fullAddress: data.display_name || ''
      };
    }
    
    return null;
  } catch (error) {
    console.error('住所取得エラー:', error);
    return null;
  }
}

/**
 * 住所情報をフォーマットする関数
 * @param {Object} addressInfo - 住所情報オブジェクト
 * @returns {string} フォーマットされた住所文字列
 */
export function formatAddress(addressInfo) {
  if (!addressInfo) return '';
  
  const parts = [];
  
  if (addressInfo.prefecture) parts.push(addressInfo.prefecture);
  if (addressInfo.city) parts.push(addressInfo.city);
  if (addressInfo.district) parts.push(addressInfo.district);
  
  return parts.join(' ');
} 