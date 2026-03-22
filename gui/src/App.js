import { useState } from "react";
const STYLE = `
  @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;500;600;700&display=swap');
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  .tilsam-root {
    min-height: 100px;
    background: #1a1c20;
    color: #c8cdd6;
    font-family: 'Rajdhani', sans-serif;
    font-size: 15px;
    display: flex;
    flex-direction: column;
  }

  .tls-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    height: 52px;
    border-bottom: 1px solid #2e3138;
  }
  .tls-logo {
    font-family: 'Share Tech Mono', monospace;
    font-size: 22px;
    letter-spacing: 4px;
    color: #4ea8f5;
  }
  .tls-version {
    font-size: 12px;
    color: #555b66;
    font-family: 'Share Tech Mono', monospace;
  }

  .tls-main {
    flex: 1;
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    gap: 20px;
    max-width: 1260px;
    width: 100%;
    margin: 0 auto;
  }

  .tls-panel {
    background: #20232a;
    border: 1px solid #2e3138;
    border-radius: 6px;
    padding: 18px 20px;
  }
  .tls-panel-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1.5px;
    color: #8a909c;
    text-transform: uppercase;
    margin-bottom: 14px;
  }

  .tls-config-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 18px;
  }
  .tls-field {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .tls-label {
    font-size: 13px;
    color: #6e7480;
    white-space: nowrap;
  }
  .tls-select, .tls-input-num {
    background: #16181e;
    border: 1px solid #333843;
    border-radius: 4px;
    color: #c8cdd6;
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    padding: 5px 10px;
    outline: none;
    transition: border-color 0.15s;
  }
  .tls-select { padding-right: 28px; cursor: pointer; min-width: 150px; }
  .tls-select:focus, .tls-input-num:focus { border-color: #4ea8f5; }
  .tls-input-num { width: 70px; text-align: center; }

  .tls-mode-group {
    display: flex;
    gap: 6px;
    margin-top: 14px;
  }
  .tls-mode-btn {
    padding: 6px 18px;
    border-radius: 4px;
    border: 1px solid #3a4050;
    background: transparent;
    color: #8a909c;
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .tls-mode-btn:hover { border-color: #4ea8f5; color: #c8cdd6; }
  .tls-mode-btn.active {
    background: #4ea8f5;
    border-color: #4ea8f5;
    color: #0e1117;
  }

  .tls-io-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
  }
  .tls-io-actions { display: flex; gap: 6px; }
  .tls-action-btn {
    padding: 3px 12px;
    border-radius: 4px;
    border: 1px solid #3a4050;
    background: transparent;
    color: #6e7480;
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .tls-action-btn:hover { border-color: #4ea8f5; color: #c8cdd6; }

  .tls-textarea {
    width: 100%;
    min-height: 140px;
    resize: vertical;
    background: #16181e;
    border: 1px solid #2e3138;
    border-radius: 4px;
    color: #c8cdd6;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    padding: 12px;
    outline: none;
    transition: border-color 0.15s;
    line-height: 1.6;
  }
  .tls-textarea:focus { border-color: #4ea8f5; }
  .tls-textarea[readonly] { cursor: default; color: #9da3af; }

  .tls-execute-wrap {
    display: flex;
    justify-content: center;
  }
  .tls-execute-btn {
    padding: 10px 48px;
    border-radius: 4px;
    border: none;
    background: #4ea8f5;
    color: #0e1117;
    font-family: 'Rajdhani', sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    cursor: pointer;
    transition: background 0.15s, transform 0.1s;
  }
  .tls-execute-btn:hover { background: #6fbcf8; }
  .tls-execute-btn:active { transform: scale(0.97); }

  /* Substitution key grid */
  .tls-sub-grid {
    display: grid;
    grid-template-columns: repeat(26, 1fr);
    gap: 4px;
    margin-top: 14px;
  }
  .tls-sub-cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
  }
  .tls-sub-plain {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #555b66;
  }
  .tls-sub-input {
    width: 100%;
    background: #16181e;
    border: 1px solid #2e3138;
    border-radius: 3px;
    color: #4ea8f5;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    text-align: center;
    padding: 3px 0;
    outline: none;
    text-transform: uppercase;
    transition: border-color 0.15s;
  }
  .tls-sub-input:focus { border-color: #4ea8f5; }

  /* Frequency analysis */
  .tls-freq-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }
  .tls-freq-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    user-select: none;
  }
  .tls-checkbox {
    appearance: none;
    width: 16px;
    height: 16px;
    border: 1px solid #3a4050;
    border-radius: 3px;
    background: #16181e;
    cursor: pointer;
    position: relative;
    flex-shrink: 0;
  }
  .tls-checkbox:checked { background: #4ea8f5; border-color: #4ea8f5; }
  .tls-checkbox:checked::after {
    content: '';
    position: absolute;
    left: 4px; top: 1px;
    width: 5px; height: 9px;
    border: 2px solid #0e1117;
    border-top: none; border-left: none;
    transform: rotate(45deg);
  }
  .tls-analyze-btn {
    padding: 5px 18px;
    border-radius: 4px;
    border: none;
    background: #4b5bef;
    color: #e8ecf8;
    font-family: 'Rajdhani', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s;
  }
  .tls-analyze-btn:hover { background: #6370f5; }

  .tls-freq-chart {
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 90px;
    padding-top: 8px;
    overflow-x: auto;
  }
  .tls-bar-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    min-width: 22px;
  }
  .tls-bar {
    width: 16px;
    background: #4ea8f5;
    border-radius: 2px 2px 0 0;
    min-height: 2px;
  }
  .tls-bar-lbl {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #555b66;
  }

  .tls-statusbar {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 6px 28px;
    border-top: 1px solid #2e3138;
    background: #1a1c20;
  }
  .tls-status-item {
    font-size: 12px;
    color: #555b66;
    font-family: 'Share Tech Mono', monospace;
  }
  .tls-status-sep { color: #2e3138; }
  .tls-copy-flash { color: #4ea8f5 !important; }
  .tls-error {
    color: #f87171;
    background: #2a1a1a;
    border: 1px solid #7f1d1d;
    border-radius: 4px;
    padding: 8px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
  }
`;

const ALPHABET = Array.from({ length: 26 }, (_, i) => String.fromCharCode(65 + i));

const API_BASE = process.env.REACT_APP_API_BASE || '';

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error || `HTTP ${res.status}`);
  return json;
}

export default function Tilsam() {
  const CIPHERS = ['Caesar', 'Affine', 'Substitution'];
  const LANGS = ['English', 'French', 'Arabic'];

  const [cipher, setCipher] = useState('Caesar');
  const [language, setLanguage] = useState('English');
  const [mode, setMode] = useState('Encrypt');
  const [shift, setShift] = useState(3);
  const [affineA, setAffineA] = useState(5);
  const [affineB, setAffineB] = useState(8);
  const [subKey, setSubKey] = useState(Object.fromEntries(ALPHABET.map(l => [l, ''])));
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [freqOpen, setFreqOpen] = useState(false);
  const [freqData, setFreqData] = useState([]);
  const [copyFlash, setCopyFlash] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleCopy = () => {
    if (output) {
      navigator.clipboard.writeText(output).catch(() => {});
      setCopyFlash(true);
      setTimeout(() => setCopyFlash(false), 1200);
    }
  };

  const handleSubKey = (letter, val) =>
    setSubKey(prev => ({ ...prev, [letter]: val.slice(0, 1).toUpperCase() }));

  const handleCipherChange = (c) => {
    setCipher(c);
    setOutput('');
    setError('');
  };

  const handleExecute = async () => {
    if (!input.trim()) {
      setError('Please enter some input text.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const body = { cipher, language, mode, text: input, shift, affineA, affineB, subKey };
      const data = await apiPost('/api/execute', body);
      setOutput(data.result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!input.trim()) {
      setError('Please enter some input text to analyze.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await apiPost('/api/analyze', { text: input, language, showBigrams: false });
      setFreqData(data.frequencies || []);
      setFreqOpen(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const maxRel = freqData.length > 0 ? Math.max(...freqData.map(d => d.rel)) : 1;

  return (
    <>
      <style>{STYLE}</style>
      <div className="tilsam-root">

        <header className="tls-header">
          <div className="tls-logo">TILSAM</div>
          <div className="tls-version">version1</div>
        </header>

        <main className="tls-main">

          {/* Configuration */}
          <div className="tls-panel">
            <div className="tls-panel-title">Configuration</div>

            <div className="tls-config-row">
              <div className="tls-field">
                <span className="tls-label">Cipher</span>
                <select className="tls-select" value={cipher} onChange={e => handleCipherChange(e.target.value)}>
                  {CIPHERS.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>

              <div className="tls-field">
                <span className="tls-label">Language</span>
                <select className="tls-select" value={language} onChange={e => setLanguage(e.target.value)}>
                  {LANGS.map(l => <option key={l}>{l}</option>)}
                </select>
              </div>

              {cipher === 'Caesar' && (
                <div className="tls-field">
                  <span className="tls-label">Shift</span>
                  <input className="tls-input-num" type="number" min={0} max={25} value={shift}
                    onChange={e => setShift(Number(e.target.value))} />
                </div>
              )}

              {cipher === 'Affine' && (
                <>
                  <div className="tls-field">
                    <span className="tls-label">a</span>
                    <input className="tls-input-num" type="number" min={1} max={25} value={affineA}
                      onChange={e => setAffineA(Number(e.target.value))} />
                  </div>
                  <div className="tls-field">
                    <span className="tls-label">b</span>
                    <input className="tls-input-num" type="number" min={0} max={25} value={affineB}
                      onChange={e => setAffineB(Number(e.target.value))} />
                  </div>
                </>
              )}
            </div>

            {cipher === 'Substitution' && (
              <div className="tls-sub-grid">
                {ALPHABET.map(l => (
                  <div key={l} className="tls-sub-cell">
                    <span className="tls-sub-plain">{l}</span>
                    <input className="tls-sub-input" maxLength={1} value={subKey[l]}
                      onChange={e => handleSubKey(l, e.target.value)} />
                  </div>
                ))}
              </div>
            )}

            <div className="tls-mode-group">
              {['Encrypt', 'Decrypt', 'Crack'].map(m => (
                <button key={m}
                  className={`tls-mode-btn${mode === m ? ' active' : ''}`}
                  onClick={() => { setMode(m); setOutput(''); setError(''); }}>
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Input */}
          <div className="tls-panel">
            <div className="tls-io-header">
              <div className="tls-panel-title" style={{ margin: 0 }}>Input</div>
              <div className="tls-io-actions">
                <button className="tls-action-btn" onClick={() => { setInput(''); setError(''); }}>Clear</button>
                <button className="tls-action-btn" onClick={() => { setInput(output); setOutput(''); setError(''); }}>Swap</button>
              </div>
            </div>
            <textarea className="tls-textarea" value={input}
              onChange={e => { setInput(e.target.value); setError(''); }}
              placeholder="Enter text here…" rows={6} />
          </div>

          {/* Error message */}
          {error && (
            <div className="tls-error">{error}</div>
          )}

          {/* Execute */}
          <div className="tls-execute-wrap">
            <button className="tls-execute-btn" onClick={handleExecute} disabled={loading}>
              {loading ? 'Working…' : 'Execute'}
            </button>
          </div>

          {/* Output */}
          <div className="tls-panel">
            <div className="tls-io-header">
              <div className="tls-panel-title" style={{ margin: 0 }}>Output</div>
              <div className="tls-io-actions">
                <button className="tls-action-btn" onClick={() => setOutput('')}>Clear</button>
                <button className={`tls-action-btn${copyFlash ? ' tls-copy-flash' : ''}`} onClick={handleCopy}>
                  {copyFlash ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>
            <textarea className="tls-textarea" value={output} readOnly
              placeholder="Output will appear here…" rows={6} />
          </div>

          {/* Frequency Analysis */}
          <div className="tls-panel">
            <div className="tls-freq-bar">
              <label className="tls-freq-toggle">
                <input type="checkbox" className="tls-checkbox" checked={freqOpen}
                  onChange={e => setFreqOpen(e.target.checked)} />
                <span>Frequency Analysis</span>
              </label>
              <button className="tls-analyze-btn" onClick={handleAnalyze} disabled={loading}>Analyze</button>
            </div>

            {freqOpen && (
              <div className="tls-freq-chart">
                {freqData.length > 0
                  ? freqData.map(({ letter, rel }) => (
                      <div key={letter} className="tls-bar-wrap">
                        <div className="tls-bar" style={{ height: `${Math.max(2, Math.round((rel / maxRel) * 70))}px` }} />
                        <span className="tls-bar-lbl">{letter}</span>
                      </div>
                    ))
                  : ALPHABET.map(l => (
                      <div key={l} className="tls-bar-wrap">
                        <div className="tls-bar" style={{ height: '2px' }} />
                        <span className="tls-bar-lbl">{l}</span>
                      </div>
                    ))
                }
              </div>
            )}
          </div>

        </main>

        <footer className="tls-statusbar">
          <span className="tls-status-item">{cipher}</span>
          <span className="tls-status-sep">|</span>
          <span className="tls-status-item">{language}</span>
          <span className="tls-status-sep">|</span>
          <span className="tls-status-item">{mode}</span>
          {cipher === 'Caesar' && <>
            <span className="tls-status-sep">|</span>
            <span className="tls-status-item">Shift {shift}</span>
          </>}
          {cipher === 'Affine' && <>
            <span className="tls-status-sep">|</span>
            <span className="tls-status-item">a={affineA} b={affineB}</span>
          </>}
        </footer>

      </div>
    </>
  );
}