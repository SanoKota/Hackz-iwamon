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
                    const sires = horses.filter(h => h.sex === '牡'); // 父
                    const dams = horses.filter(h => h.sex === '牝'); // 母

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

            // UI操作（ローディング開始）
            loader.style.display = 'flex';
            submitBtn.style.opacity = '0.7';
            submitBtn.textContent = 'Generating...';
            submitBtn.disabled = true;

            const payload = {
                sire_name: sire,
                dam_name: dam,
                child_name: childName
            };

            try {
                // --- 修正箇所: ここで待機して結果を直接受け取る ---
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await response.json(); // JSONをパース

                if (response.ok && data.status === 'success') {
                    // 成功したらすぐに表示処理へ
                    const responseArea = document.querySelector('.response-area');
                    const responseContent = document.querySelector('.response-content');

                    if (responseArea && responseContent) {
                        // marked.parse が使える前提
                        responseContent.innerHTML = marked.parse(data.result);
                        responseArea.style.display = 'block';
                        responseArea.scrollIntoView({ behavior: 'smooth' });
                    }
                } else {
                    // エラーの場合
                    throw new Error(data.message || 'Unknown error occurred');
                }

            } catch (error) {
                console.error('Error:', error);
                showError(error.message);
            } finally {
                // 成功しても失敗してもUIを元に戻す
                resetUI();
            }
        });

        function resetUI() {
            loader.style.display = 'none';
            submitBtn.style.opacity = '1';
            submitBtn.textContent = '生産する';
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