/**
 * 多模态数据分析可视化 Agent 系统 - 主应用组件
 *
 * 提供完整的用户界面，支持数据上传、分析任务管理、
 * 可视化图表展示和仪表盘配置功能。
 */

import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Plot from 'react-plotly.js'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

interface Task {
  id: string
  task_type: string
  status: string
  progress: number
  created_at: string
}

interface AnalysisResult {
  summary?: any
  descriptive?: any
  trend?: any
  clustering?: any
  correlation?: any
}

interface ChartConfig {
  type: string
  data?: any
  parameters?: any
}

function App() {
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [analysisType, setAnalysisType] = useState('statistics')
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [chartType, setChartType] = useState('line')
  const [chartData, setChartData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks`)
      setTasks(response.data.tasks)
    } catch (err) {
      console.error('获取任务列表失败:', err)
    }
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('请选择要上传的文件')
      return
    }

    setLoading(true)
    setError(null)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadResult(response.data)
      setActiveTab('analyze')
    } catch (err: any) {
      setError(err.response?.data?.detail || '文件上传失败')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    if (!uploadResult) {
      setError('请先上传数据文件')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, {
        data: uploadResult,
        analysis_type: analysisType,
        parameters: {}
      })
      setAnalysisResult(response.data)
      setActiveTab('visualize')
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateChart = async () => {
    if (!analysisResult) {
      setError('请先执行数据分析')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/visualize`, {
        data: analysisResult.descriptive || {},
        chart_type: chartType,
        parameters: {
          title: `${analysisType} 可视化`,
          x: 'column',
          y: 'mean'
        }
      })
      setChartData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '可视化生成失败')
    } finally {
      setLoading(false)
    }
  }

  const renderUploadTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">文件上传</h2>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <input
            type="file"
            id="file-upload"
            className="hidden"
            onChange={handleFileSelect}
            accept=".csv,.xlsx,.xls,.json,.txt,.jpg,.jpeg,.png,.gif,.mp3,.wav,.mp4,.avi"
          />
          <label
            htmlFor="file-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <svg className="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="text-gray-600">
              {selectedFile ? selectedFile.name : '点击选择文件或拖拽文件到此处'}
            </span>
            <span className="text-sm text-gray-400 mt-2">
              支持 CSV、Excel、JSON、文本、图片、音频、视频格式
            </span>
          </label>
        </div>

        {selectedFile && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600">
              <strong>已选择:</strong> {selectedFile.name}
            </p>
            <p className="text-sm text-gray-600">
              <strong>大小:</strong> {(selectedFile.size / 1024).toFixed(2)} KB
            </p>
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {loading ? '上传中...' : '上传并处理'}
        </button>
      </div>

      {uploadResult && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-3">上传结果</h3>
          <div className="bg-gray-50 rounded-lg p-4">
            <p><strong>文件ID:</strong> {uploadResult.file_id}</p>
            <p><strong>文件名:</strong> {uploadResult.filename}</p>
            <p><strong>文件大小:</strong> {(uploadResult.size / 1024).toFixed(2)} KB</p>
            <p><strong>数据类型:</strong> {uploadResult.type}</p>
          </div>
        </div>
      )}
    </div>
  )

  const renderAnalyzeTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">数据分析</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            分析类型
          </label>
          <select
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="statistics">统计分析</option>
            <option value="trend">趋势分析</option>
            <option value="clustering">聚类分析</option>
            <option value="correlation">相关性分析</option>
            <option value="distribution">分布分析</option>
          </select>
        </div>

        <button
          onClick={handleAnalyze}
          disabled={!uploadResult || loading}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {loading ? '分析中...' : '执行分析'}
        </button>
      </div>

      {analysisResult && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-3">分析结果</h3>
          <pre className="bg-gray-50 rounded-lg p-4 overflow-auto max-h-96 text-sm">
            {JSON.stringify(analysisResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )

  const renderVisualizeTab = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">数据可视化</h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            图表类型
          </label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="line">折线图</option>
            <option value="bar">柱状图</option>
            <option value="scatter">散点图</option>
            <option value="pie">饼图</option>
            <option value="histogram">直方图</option>
            <option value="heatmap">热力图</option>
            <option value="box">箱线图</option>
            <option value="radar">雷达图</option>
          </select>
        </div>

        <button
          onClick={handleCreateChart}
          disabled={!analysisResult || loading}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
        >
          {loading ? '生成中...' : '生成图表'}
        </button>
      </div>

      {chartData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-3">可视化图表</h3>
          {chartData.html ? (
            <div dangerouslySetInnerHTML={{ __html: chartData.html }} />
          ) : chartData.data ? (
            <Plot
              data={chartData.data.data || []}
              layout={chartData.data.layout || {}}
              config={{ responsive: true }}
              style={{ width: '100%', height: '500px' }}
            />
          ) : (
            <p className="text-gray-500">暂无图表数据</p>
          )}
        </div>
      )}
    </div>
  )

  const renderTasksTab = () => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">任务管理</h2>

      <div className="space-y-4">
        {tasks.length === 0 ? (
          <p className="text-gray-500 text-center py-8">暂无任务</p>
        ) : (
          tasks.map((task) => (
            <div key={task.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <p className="font-medium">{task.task_type}</p>
                  <p className="text-sm text-gray-500">
                    创建时间: {new Date(task.created_at).toLocaleString()}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm ${
                  task.status === 'completed' ? 'bg-green-100 text-green-800' :
                  task.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  task.status === 'failed' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {task.status}
                </span>
              </div>
              {task.status === 'running' && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${task.progress}%` }}
                    />
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{task.progress}%</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <button
        onClick={fetchTasks}
        className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
      >
        刷新列表
      </button>
    </div>
  )

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            多模态数据分析可视化 Agent 系统
          </h1>
          <p className="text-gray-600 mt-1">
            基于人工智能的多模态内容理解与自动化数据分析平台
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div className="flex space-x-1 mb-6 bg-gray-200 rounded-lg p-1">
          {[
            { id: 'upload', label: '数据上传' },
            { id: 'analyze', label: '数据分析' },
            { id: 'visualize', label: '可视化' },
            { id: 'tasks', label: '任务管理' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition ${
                activeTab === tab.id
                  ? 'bg-white text-blue-600 shadow'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {activeTab === 'upload' && renderUploadTab()}
          {activeTab === 'analyze' && renderAnalyzeTab()}
          {activeTab === 'visualize' && renderVisualizeTab()}
          {activeTab === 'tasks' && renderTasksTab()}
        </div>
      </main>

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-gray-600">
          <p>多模态数据分析可视化 Agent 系统 v1.0.0</p>
          <p className="text-sm mt-1">Powered by AI & React</p>
        </div>
      </footer>
    </div>
  )
}

export default App
