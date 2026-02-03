import { useState } from 'react'
import './App.css'

// API Base URL - relative path for production, absolute for development
const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8000'

function App() {
  const [studentId, setStudentId] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()

    if (!studentId.trim()) {
      setError('請輸入學號')
      return
    }

    setLoading(true)
    setError(null)
    setSearched(true)

    try {
      const response = await fetch(`${API_BASE}/api/exams/${studentId.trim()}`)

      if (!response.ok) {
        throw new Error('查詢失敗，請稍後再試')
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message || '網路錯誤，請檢查連線')
      setResults(null)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    setStudentId(e.target.value)
    // Reset states when input changes
    if (error) setError(null)
  }

  return (
    <>
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1 className="header-title">
            <span className="school-icon">🏫</span>
            臺北市立復興高級中學 學分補考查詢系統
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Search Section */}
        <section className="search-container">
          <h2 className="search-title">📝 補考查詢</h2>
          <p className="search-subtitle">請輸入學號查詢您的補考科目與時間</p>

          <form className="search-form" onSubmit={handleSearch}>
            <input
              type="text"
              className="search-input"
              placeholder="請輸入學號"
              value={studentId}
              onChange={handleInputChange}
              maxLength={20}
              autoFocus
            />
            <button type="submit" className="search-btn" disabled={loading}>
              {loading ? '查詢中...' : '🔍 查詢'}
            </button>
          </form>
        </section>

        {/* Results Section */}
        <section className="results-section">
          {/* Loading State */}
          {loading && (
            <div className="status-message loading">
              <div className="loading-spinner"></div>
              <p className="status-text">查詢中，請稍候...</p>
            </div>
          )}

          {/* Error State */}
          {!loading && error && (
            <div className="status-message error">
              <div className="status-icon">⚠️</div>
              <p className="status-text">{error}</p>
            </div>
          )}

          {/* No Data State */}
          {!loading && !error && searched && results && results.length === 0 && (
            <div className="status-message no-data">
              <div className="status-icon">❓</div>
              <p className="status-text">查無此學號的補考資料</p>
              <p className="status-hint">請確認輸入的學號是否正確，或該學號目前無補考紀錄。</p>
            </div>
          )}

          {/* Results Table */}
          {!loading && !error && results && results.length > 0 && (
            <div className="results-card">
              <div className="results-header">
                <h2>📋 補考科目清單</h2>
                {results[0]?.student_name && (
                  <div className="student-info">
                    <span>姓名：{results[0].student_name}</span>
                  </div>
                )}
              </div>
              <table className="results-table">
                <thead>
                  <tr>
                    <th>科目</th>
                    <th>日期</th>
                    <th>時間</th>
                    <th>地點</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((exam, index) => (
                    <tr key={index}>
                      <td>{exam.subject}</td>
                      <td>{exam.exam_date}</td>
                      <td>{exam.exam_time}</td>
                      <td>{exam.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </main>

      {/* Footer */}
      <footer className="footer">
        <p>© {new Date().getFullYear()} 臺北市立復興高級中學 教務處</p>
      </footer>
    </>
  )
}

export default App
