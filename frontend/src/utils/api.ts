import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  async getTasks(status?: string) {
    const params = status ? { status } : {}
    const response = await this.client.get('/tasks', { params })
    return response.data
  }

  async createTask(taskType: string, inputData?: any, parameters?: Record<string, any>) {
    const response = await this.client.post('/tasks', {
      task_type: taskType,
      input_data: inputData,
      parameters: parameters || {},
    })
    return response.data
  }

  async getTask(taskId: string) {
    const response = await this.client.get(`/tasks/${taskId}`)
    return response.data
  }

  async executeTask(taskId: string) {
    const response = await this.client.post(`/tasks/${taskId}/execute`)
    return response.data
  }

  async deleteTask(taskId: string) {
    const response = await this.client.delete(`/tasks/${taskId}`)
    return response.data
  }

  async uploadFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await this.client.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  }

  async processText(data: any, options?: Record<string, any>) {
    const response = await this.client.post('/process/text', {
      data,
      options: options || {},
    })
    return response.data
  }

  async processImage(filePath?: string, imageData?: string, options?: Record<string, any>) {
    const response = await this.client.post('/process/image', {
      file_path: filePath,
      image_data: imageData,
      options: options || {},
    })
    return response.data
  }

  async analyzeData(data: any, analysisType: string, parameters?: Record<string, any>) {
    const response = await this.client.post('/analyze', {
      data,
      analysis_type: analysisType,
      parameters: parameters || {},
    })
    return response.data
  }

  async createVisualization(data: any, chartType: string, parameters?: Record<string, any>) {
    const response = await this.client.post('/visualize', {
      data,
      chart_type: chartType,
      parameters: parameters || {},
    })
    return response.data
  }

  async createDashboard(chartConfigs: any[]) {
    const response = await this.client.post('/dashboard', chartConfigs)
    return response.data
  }

  async generatePlan(userIntent: string, dataInfo: any) {
    const response = await this.client.post('/plan', {
      user_intent: userIntent,
      data_info: dataInfo,
    })
    return response.data
  }

  async getAnalysisTypes() {
    const response = await this.client.get('/analysis/types')
    return response.data
  }

  async getChartTypes() {
    const response = await this.client.get('/chart/types')
    return response.data
  }
}

export const apiClient = new ApiClient()
