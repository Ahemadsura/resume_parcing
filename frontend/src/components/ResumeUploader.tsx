'use client'
import { useState, useCallback } from 'react'

interface ResumeData {
  skills: string[]
  skills_by_category: Record<string, string[]>
  experience_years: string
  keywords: string[]
  contact: {
    email?: string
    phone?: string
    linkedin?: string
    github?: string
  }
  resume_score: number
  suggestions: Array<{
    category: string
    priority: string
    title: string
    description: string
    impact: string
  }>
  word_count: number
}

interface ParseResponse {
  resume_data: ResumeData
  match_score?: number
}

export default function ResumeUploader() {
  const [jobDesc, setJobDesc] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [results, setResults] = useState<ParseResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isDragging, setIsDragging] = useState(false)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile?.type === 'application/pdf') {
      setFile(droppedFile)
      setError('')
    } else {
      setError('Please upload a PDF file')
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile)
        setError('')
      } else {
        setError('Please upload a PDF file')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setLoading(true)
    setError('')
    setResults(null)

    const formData = new FormData()
    formData.append('file', file)
    formData.append('job_desc', jobDesc)

    try {
      const res = await fetch(`${API_URL}/parse-resume`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.detail || 'Failed to parse resume')
      }

      const data = await res.json()
      setResults(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'from-green-500 to-emerald-500'
    if (score >= 60) return 'from-yellow-500 to-orange-500'
    return 'from-red-500 to-pink-500'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-400 bg-red-400/10 border-red-400/20'
      case 'medium': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      case 'low': return 'text-blue-400 bg-blue-400/10 border-blue-400/20'
      default: return 'text-gray-400 bg-gray-400/10 border-gray-400/20'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-white mb-3">Resume Analyzer</h1>
          <p className="text-gray-300 text-lg">Upload your resume to get instant feedback and improvement suggestions</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Inputs */}
          <div className="space-y-6">
            {/* Job Description */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
              <label className="block text-sm font-medium text-gray-300 mb-3">
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Job Description (Optional)
                </span>
              </label>
              <textarea
                value={jobDesc}
                onChange={(e) => setJobDesc(e.target.value)}
                placeholder="Paste the job description here to see how well your resume matches..."
                className="w-full h-40 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 resize-none"
              />
            </div>

            {/* File Upload */}
            <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
              <label className="block text-sm font-medium text-gray-300 mb-3">
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Resume (PDF)
                </span>
              </label>
              
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-200 cursor-pointer ${
                  isDragging 
                    ? 'border-purple-500 bg-purple-500/10' 
                    : file 
                      ? 'border-green-500/50 bg-green-500/10' 
                      : 'border-white/20 hover:border-purple-500/50 hover:bg-white/5'
                }`}
              >
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                />
                
                {file ? (
                  <div className="space-y-2">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-green-500/20 flex items-center justify-center">
                      <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <p className="text-white font-medium">{file.name}</p>
                    <p className="text-gray-400 text-sm">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <div className="w-12 h-12 mx-auto rounded-xl bg-white/10 flex items-center justify-center">
                      <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <p className="text-gray-300">Drag & drop your resume or click to browse</p>
                    <p className="text-gray-500 text-sm">PDF files only</p>
                  </div>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="w-full py-4 px-6 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-bold text-lg shadow-lg hover:shadow-purple-500/25 hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100 transition-all duration-200 flex items-center justify-center gap-3"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing Resume...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Analyze Resume
                </>
              )}
            </button>

            {/* Error Message */}
            {error && (
              <div className="p-4 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300 text-center">
                {error}
              </div>
            )}
          </div>

          {/* Right Column - Results */}
          <div className="space-y-6">
            {results ? (
              <div className="space-y-6 animate-fadeIn">
                {/* Scores Row */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Resume Score */}
                  <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wider">Resume Score</h3>
                    <div className="flex items-end gap-2">
                      <span className={`text-4xl font-bold bg-gradient-to-r ${getScoreColor(results.resume_data.resume_score)} bg-clip-text text-transparent`}>
                        {results.resume_data.resume_score}
                      </span>
                      <span className="text-gray-400 mb-1">/ 100</span>
                    </div>
                  </div>

                  {/* Match Score */}
                  <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2 uppercase tracking-wider">Job Match</h3>
                    {results.match_score !== undefined ? (
                      <div className="flex items-end gap-2">
                        <span className={`text-4xl font-bold bg-gradient-to-r ${getScoreColor(results.match_score)} bg-clip-text text-transparent`}>
                          {results.match_score}%
                        </span>
                      </div>
                    ) : (
                      <span className="text-gray-500 text-sm">Add job description to see match</span>
                    )}
                  </div>
                </div>

                {/* Improvement Suggestions */}
                <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Improvement Suggestions
                  </h3>
                  <div className="space-y-4">
                    {results.resume_data.suggestions && results.resume_data.suggestions.length > 0 ? (
                      results.resume_data.suggestions.map((suggestion, index) => (
                        <div key={index} className="bg-white/5 rounded-xl p-4 border border-white/10">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-semibold text-white">{suggestion.title}</h4>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityColor(suggestion.priority)} uppercase`}>
                              {suggestion.priority}
                            </span>
                          </div>
                          <p className="text-gray-300 text-sm mb-2">{suggestion.description}</p>
                          <div className="flex items-center gap-2 text-xs text-green-400">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                            </svg>
                            Predicted Impact: {suggestion.impact}
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-6 text-green-400">
                        <p>Great job! No major improvements needed.</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Skills */}
                <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                    Skills Detected
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {results.resume_data.skills.map((skill, index) => (
                      <span key={index} className="px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-200 text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Contact & Experience */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2">Experience</h3>
                    <p className="text-xl font-bold text-white">{results.resume_data.experience_years} years</p>
                  </div>
                  <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-6 border border-white/20">
                    <h3 className="text-sm font-semibold text-gray-300 mb-2">Contact</h3>
                    <div className="space-y-1 text-sm text-gray-300">
                      {results.resume_data.contact.email && <p className="truncate">{results.resume_data.contact.email}</p>}
                      {results.resume_data.contact.phone && <p>{results.resume_data.contact.phone}</p>}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="backdrop-blur-xl bg-white/10 rounded-2xl p-12 border border-white/20 text-center h-full flex flex-col items-center justify-center min-h-[500px]">
                <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-white/10 flex items-center justify-center">
                  <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">Ready to Analyze</h3>
                <p className="text-gray-400 max-w-sm mx-auto">
                  Upload your resume to get a detailed analysis, score, and personalized improvement suggestions.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
