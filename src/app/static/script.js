document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitButton = form.querySelector('button[type="submit"]');
    const loadingDiv = document.createElement('div');
    
    loadingDiv.className = 'loading';
    loadingDiv.textContent = 'Geminiが考え中...';
    form.after(loadingDiv);

    form.addEventListener('submit', function() {
        // 送信ボタンを無効化し、ローディング表示を出す
        submitButton.disabled = true;
        submitButton.textContent = '送信中...';
        loadingDiv.style.display = 'block';
        
        // 既存のレスポンスがあれば隠す（オプション）
        const existingResponse = document.querySelector('.response');
        if (existingResponse) {
            existingResponse.style.opacity = '0.5';
        }
    });
});
