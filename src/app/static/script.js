document.addEventListener('DOMContentLoaded', () => {
    const sireSelect = document.getElementById('sire');
    const damSelect = document.getElementById('dam');

    // Fetch horse data from API
    fetch('/api/horses')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const horses = data.horses;
                if (sireSelect && damSelect) {
                    // Filter by sex (assuming '牡' = Male, '牝' = Female)
                    const sires = horses.filter(h => h.sex === '牡');
                    const dams = horses.filter(h => h.sex === '牝');

                    populateSelect(sireSelect, sires);
                    populateSelect(damSelect, dams);
                }
            } else {
                console.error('Failed to load horses:', data.message);
            }
        })
        .catch(error => {
            console.error('Error fetching horse data:', error);
        });

    function populateSelect(element, data) {
        data.forEach(horse => {
            const option = document.createElement('option');
            option.value = horse.name;
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
