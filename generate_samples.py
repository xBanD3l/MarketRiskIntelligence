import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_samples():
    os.makedirs('sample_data', exist_ok=True)
    
    categories = ['Earnings', 'Macro', 'Regulation / Legal', 'Leadership', 'Speculative / Hype']
    sources = ['Reuters', 'Bloomberg', 'Financial Times', 'Wall Street Journal', 'CNBC']
    
    events = [
        ("NVIDIA reports 200% revenue growth as AI demand surges.", "Earnings", 0.9, 45, "Confirmed record beat."),
        ("Fed signals 'higher for longer' interest rates as inflation remains sticky.", "Macro", -0.4, 38, "Official policy signal."),
        ("SEC investigates major tech firm for potential antitrust violations.", "Regulation / Legal", -0.7, 32, "High-stakes legal risk."),
        ("Microsoft CEO announces massive investment in quantum computing.", "Leadership", 0.8, 25, "Strategic growth signal."),
        ("Rumors of a secret Apple car prototype sent EV stocks soaring.", "Speculative / Hype", 0.95, 30, "Meme-stock energy."),
        ("Global oil prices stabilize as war concerns in Middle East ease slightly.", "Macro", 0.1, 42, "Geopolitical stabilization."),
        ("Tesla misses Q4 delivery targets, stock drops in after-hours trading.", "Earnings", -0.8, 15, "Individual stock impact."),
        ("European Union passes landmark AI safety regulations.", "Regulation / Legal", -0.2, 28, "Systemic compliance risk."),
        ("Goldman Sachs appoints new Head of Global Equities.", "Leadership", 0.3, 12, "Management transition."),
        ("Reddit IPO sparks massive retail interest and speculative volatility.", "Speculative / Hype", 0.85, 35, "Retail mania signal."),
        # Add 40 more variants
    ]
    
    # Expand to 50+ items by duplicating and varying
    full_list = []
    base_date = datetime.now()
    
    for i in range(50):
        base_event = events[i % len(events)]
        variation = f" (Update {i//len(events) + 1})" if i >= len(events) else ""
        
        full_list.append({
            'source': np.random.choice(sources),
            'text': f"{base_event[0]}{variation}",
            'date': (base_date - timedelta(days=i)).strftime('%Y-%m-%d'),
            'type': 'news',
            'category': base_event[1],
            'sentiment': base_event[2] + np.random.uniform(-0.1, 0.1),
            'risk_score': max(5, min(50, base_event[3] + np.random.randint(-5, 5))),
            'risk_reason': base_event[4],
            'speculative_flag': (base_event[1] == 'Speculative / Hype' and base_event[3] > 25),
            'intelligence_summary': f"AI analysis indicates a {base_event[1]} event with meaningful risk magnitude."
        })
    
    df = pd.DataFrame(full_list)
    df.to_csv('sample_data/market_samples.csv', index=False)
    print(f"Generated {len(df)} samples in sample_data/market_samples.csv")

if __name__ == "__main__":
    generate_samples()
