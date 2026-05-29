document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const ticker = document.getElementById('tickerInput').value.trim().toUpperCase();
    if (!ticker) return;
    
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loading = document.getElementById('loading');
    const resultsSection = document.getElementById('resultsSection');
    const errorBox = document.getElementById('errorBox');
    
    const verdictCard = document.getElementById('verdictCard');
    const verdictText = document.getElementById('verdictText');
    const confidenceScore = document.getElementById('confidenceScore');
    const reasoningText = document.getElementById('reasoningText');
    const latestPrice = document.getElementById('latestPrice');
    const latestVolume = document.getElementById('latestVolume');
    
    analyzeBtn.disabled = true;
    loading.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    errorBox.classList.add('hidden');
    
    try {
        const response = await fetch('http://127.0.0.1:8000/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ticker: ticker })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.error || "Analysis failed");
        }
        
        // Simulate a slight delay to allow the beautiful spinner to be seen
        setTimeout(() => {
            verdictText.textContent = data.verdict;
            confidenceScore.textContent = `${data.confidence}% Confidence`;
            reasoningText.textContent = data.reasoning;
            
            latestPrice.textContent = `₹ ${data.latest_price.toFixed(2)}`;
            latestVolume.textContent = new Intl.NumberFormat('en-IN').format(data.latest_volume);
            
            verdictCard.className = 'result-card glass-panel'; 
            if (data.verdict === 'FAKE') verdictCard.classList.add('verdict-fake');
            else if (data.verdict === 'REAL') verdictCard.classList.add('verdict-real');
            else verdictCard.classList.add('verdict-warn');
            
            renderChart(data.chart_data.dates, data.chart_data.prices, data.chart_data.volumes);
            
            loading.classList.add('hidden');
            resultsSection.classList.remove('hidden');
            resultsSection.style.animation = 'fadeInUp 0.8s ease';
            analyzeBtn.disabled = false;
        }, 800);
        
    } catch (err) {
        loading.classList.add('hidden');
        errorBox.textContent = "Error: " + err.message;
        errorBox.classList.remove('hidden');
        analyzeBtn.disabled = false;
    }
});
