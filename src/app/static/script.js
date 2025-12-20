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
                // 1. 生成リクエストを送信 (Wait for response which initiates the background process/file write)
                const generateResponse = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!generateResponse.ok) {
                    const errorMsg = await generateResponse.text();
                    throw new Error('Generate Request Failed: ' + errorMsg);
                }

                // 2. ポーリング開始
                let lastMtime = 0;
                const pollInterval = window.setInterval(async () => {
                    try {
                        const checkResponse = await fetch(`/api/check_update?last_mtime=${lastMtime}`);
                        if (checkResponse.status === 404) {
                            // File not ready yet, continue waiting
                            return;
                        }

                        const checkData = await checkResponse.json();

                        if (checkData.status === 'updated') {
                            // Update UI with new content
                            lastMtime = checkData.mtime;
                            const responseArea = document.querySelector('.response-area');
                            const responseContent = document.querySelector('.response-content');

                            if (responseArea && responseContent) {
                                responseContent.innerHTML = marked.parse(checkData.result);
                                responseArea.style.display = 'block';
                                responseArea.scrollIntoView({ behavior: 'smooth' });
                            }

                            // Stop polling and reset UI
                            clearInterval(pollInterval);
                            resetUI();
                        } else if (checkData.status === 'error') {
                            throw new Error(checkData.message);
                        }
                        // if status is 'not_modified' or 'waiting', just continue to next tick

                    } catch (pollError) {
                        console.error('Polling Error:', pollError);
                        clearInterval(pollInterval);
                        showError(pollError.message);
                        resetUI();
                    }
                }, 3000); // 3秒ごとにチェック

            } catch (error) {
                console.error('Error:', error);
                showError(error.message);
                resetUI();
            }
        });

        function resetUI() {
            loader.style.display = 'none';
            submitBtn.style.opacity = '1';
            submitBtn.textContent = '生産する'; // Back to localized text
            submitBtn.disabled = false;
        }

        function showError(message) {
            const resultElement = document.querySelector('.response-content');
            const responseArea = document.querySelector('.response-area');
            if (resultElement) {
                resultElement.innerHTML = `<pre style="color: red; text-align: left;">${message}</pre>`;
                if (responseArea) responseArea.style.display = 'block';
            } else {
                alert('エラーが発生しました:\n' + message);
            }
        }
    }
});
