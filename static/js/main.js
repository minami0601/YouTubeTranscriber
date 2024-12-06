document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('transcribeForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const resultCard = document.getElementById('resultCard');
    const transcriptText = document.getElementById('transcriptText');
    const errorAlert = document.getElementById('errorAlert');
    const copyButton = document.getElementById('copyButton');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = document.getElementById('youtubeUrl').value;
        
        // Reset UI
        errorAlert.classList.add('d-none');
        resultCard.classList.add('d-none');
        loadingSpinner.classList.remove('d-none');

        try {
            const response = await fetch('/transcribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}`
            });

            const data = await response.json();

            if (response.ok) {
                transcriptText.textContent = data.transcript;
                resultCard.classList.remove('d-none');
            } else {
                throw new Error(data.error || '文字起こしの取得に失敗しました');
            }
        } catch (error) {
            errorAlert.textContent = error.message;
            errorAlert.classList.remove('d-none');
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    });

    copyButton.addEventListener('click', async function() {
        try {
            await navigator.clipboard.writeText(transcriptText.textContent);
            
            // Visual feedback
            const originalText = copyButton.innerHTML;
            copyButton.innerHTML = '<i class="bi bi-check"></i> コピーしました！';
            setTimeout(() => {
                copyButton.innerHTML = originalText;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text:', err);
        }
    });
});
