document.addEventListener('DOMContentLoaded', () => {
    // Famous Japanese Racehorses Data
    const sires = [
        { name: "ディープインパクト (Deep Impact)", id: "deep_impact" },
        { name: "オルフェーヴル (Orfevre)", id: "orfevre" },
        { name: "キタサンブラック (Kitasan Black)", id: "kitasan_black" },
        { name: "ロードカナロア (Lord Kanaloa)", id: "lord_kanaloa" },
        { name: "エピファネイア (Epiphaneia)", id: "epiphaneia" },
        { name: "キングカメハメハ (King Kamehameha)", id: "king_kamehameha" },
        { name: "ハーツクライ (Heart's Cry)", id: "hearts_cry" },
        { name: "ゴールドシップ (Gold Ship)", id: "gold_ship" },
        { name: "コントレイル (Contrail)", id: "contrail" },
        { name: "ドゥラメンテ (Duramente)", id: "duramente" }
    ];

    const dams = [
        { name: "アーモンドアイ (Almond Eye)", id: "almond_eye" },
        { name: "ジェンティルドンナ (Gentildonna)", id: "gentildonna" },
        { name: "ブエナビスタ (Buena Vista)", id: "buena_vista" },
        { name: "クロノジェネシス (Chrono Genesis)", id: "chrono_genesis" },
        { name: "リスグラシュー (Lys Gracieux)", id: "lys_gracieux" },
        { name: "グランアレグリア (Gran Alegria)", id: "gran_alegria" },
        { name: "ウォッカ (Vodka)", id: "vodka" },
        { name: "ダイワスカーレット (Daiwa Scarlet)", id: "daiwa_scarlet" },
        { name: "エアグルーヴ (Air Groove)", id: "air_groove" },
        { name: "シーザリオ (Cesario)", id: "cesario" }
    ];

    // Populate Select Elements
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
    const hiddenPrompt = document.getElementById('hidden-prompt');
    const loader = document.getElementById('loader');
    const submitBtn = document.querySelector('button[type="submit"]');

    if (form) {
        form.addEventListener('submit', (e) => {
            // Get values
            const sire = sireSelect.value;
            const dam = damSelect.value;
            const childName = document.getElementById('child-name').value;

            // Simple validation
            if (!sire || !dam || !childName) {
                e.preventDefault();
                alert('全ての項目を入力してください。');
                return;
            }

            // Construct formatted prompt
            // Using the requested format: "Father: {sire}, Mother: {dam}, Child: {child_name}..."
            const formattedPrompt = `父馬: ${sire}\n母馬: ${dam}\n子馬の名前: ${childName}\n\n上記の血統を持つ競走馬の4歳までの戦績と特徴を作成してください。`;
            
            // Set hidden input value
            hiddenPrompt.value = formattedPrompt;

            // Show loader
            loader.style.display = 'flex';
            submitBtn.style.opacity = '0.7';
            submitBtn.textContent = 'Generating...';
            submitBtn.disabled = true;

            // Allow form to submit naturally
        });
    }
});
