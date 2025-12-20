document.addEventListener('DOMContentLoaded', () => {
    // 辞書
    const sires = [
        { name: "ディープインパクト", id: "deep_impact" },
        { name: "オルフェーヴル", id: "orfevre" },
        { name: "キタサンブラック", id: "kitasan_black" },
        { name: "ロードカナロア", id: "lord_kanaloa" },
        { name: "エピファネイア", id: "epiphaneia" },
        { name: "キングカメハメハ", id: "king_kamehameha" },
        { name: "ハーツクライ", id: "hearts_cry" },
        { name: "ゴールドシップ", id: "gold_ship" },
        { name: "コントレイル", id: "contrail" },
        { name: "ドゥラメンテ", id: "duramente" }
    ];

    const dams = [
        { name: "アーモンドアイ", id: "almond_eye" },
        { name: "ジェンティルドンナ", id: "gentildonna" },
        { name: "ブエナビスタ", id: "buena_vista" },
        { name: "クロノジェネシス", id: "chrono_genesis" },
        { name: "リスグラシュー", id: "lys_gracieux" },
        { name: "グランアレグリア", id: "gran_alegria" },
        { name: "ウォッカ", id: "vodka" },
        { name: "ダイワスカーレット", id: "daiwa_scarlet" },
        { name: "エアグルーヴ", id: "air_groove" },
        { name: "シーザリオ", id: "cesario" }
    ];

    const sireSelect = document.getElementById('sire');
    const damSelect = document.getElementById('dam');

    if (sireSelect && damSelect) {
        populateSelect(sireSelect, sires);
        populateSelect(damSelect, dams);
    }

    function populateSelect(element, data) {
        data.forEach(horse => {
            const option = document.createElement('option');
            option.value = horse.name; // Use name directly for the prompt
            option.textContent = horse.name;
            element.appendChild(option);
        });
    }

    // Handle Form Submission
    const form = document.querySelector('form');
    const loader = document.getElementById('loader');
    const submitBtn = document.querySelector('button[type="submit"]');

    if (form) {
        form.addEventListener('submit', async (e) => {
            // デフォルトのフォーム送信（画面遷移）を止める
            e.preventDefault();

            // 値の取得
            const sire = sireSelect.value;
            const dam = damSelect.value;
            const childName = document.getElementById('child-name').value;

            // バリデーション
            if (!sire || !dam || !childName) {
                alert('全ての項目を入力してください。');
                return;
            }

            // UI操作（ローディング表示など）
            loader.style.display = 'flex';
            submitBtn.style.opacity = '0.7';
            submitBtn.textContent = 'Generating...';
            submitBtn.disabled = true;

            // 送信するJSONデータを作成
            const payload = {
                sire_name: sire,
                dam_name: dam,
                child_name: childName
            };

            try {
                // fetchでPythonにJSONを投げる
                const response = await fetch('/api/generate', { // Pythonのエンドポイント
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json', // JSONであることを明示
                    },
                    body: JSON.stringify(payload) // オブジェクトを文字列化
                });

                if (!response.ok) {
                    // エラーメッセージ取得
                    const errorData = await response.json();
                    const errorMsg = errorData.detail || errorData.message || '不明なサーバーエラー';
                    throw new Error(errorMsg);
                }

                // Pythonからの返答を受け取る
                const data = await response.json();

                // 結果を画面に表示する
                if (data.status === 'success' && data.result) {
                    const responseArea = document.querySelector('.response-area');
                    const responseContent = document.querySelector('.response-content');

                    if (responseArea && responseContent) {
                        // Markdownをレンダリングして表示
                        responseContent.innerHTML = marked.parse(data.result);
                        responseArea.style.display = 'block';

                        // スクロールして結果を見せる
                        responseArea.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    console.error('Error in response:', data);
                    alert('生成に失敗しました: ' + (data.message || 'Unknown error'));
                }

            } catch (error) {
                console.error('Error:', error);

                // 画面に詳細を表示する（alertだと読みづらいので、画面内に表示するのがおすすめ）
                const resultElement = document.getElementById('response-content'); // 結果表示エリア
                if (resultElement) {
                    resultElement.innerHTML = `<pre style="color: red; text-align: left;">${error.message}</pre>`;
                    document.getElementById('responseArea').style.display = 'block';
                } else {
                    // 表示エリアがなければアラートで出す
                    alert('エラーが発生しました:\n' + error.message);
                }
            } finally {
                // UIを元に戻す
                loader.style.display = 'none';
                submitBtn.style.opacity = '1';
                submitBtn.textContent = 'Generate';
                submitBtn.disabled = false;
            }
        });
    }
});
