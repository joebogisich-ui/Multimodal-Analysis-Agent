export interface Task {
  id: string
  task_type: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  result?: any
  error?: any
  created_at: string
  started_at?: string
  completed_at?: string
  metadata?: Record<string, any>
}

export interface AnalysisResult {
  summary?: Record<string, any>
  descriptive?: Record<string, any>
  trend?: Record<string, any>
  clustering?: Record<string, any>
  correlation?: Record<string, any>
  regression?: Record<string, any>
  distribution?: Record<string, any>
}

export interface ChartConfig {
  type: string
  data?: any
  parameters?: Record<string, any>
  html?: string
  image?: string
}

export interface DashboardConfig {
  charts: ChartConfig[]
  layout?: {
    columns: number
    row_height: number
    theme: string
  }
}

export interface UploadResult {
  file_id: string
  filename: string
  size: number
  type: string
}

export interface PlanTask {
  id: string
  type: string
  dependencies: string[]
  parameters: Record<string, any>
}

export interface TaskPlan {
  data_type: string
  analysis_type: string
  tasks: PlanTask[]
  parameters: Record<string, any>
  estimated_duration: number
}

export type AnalysisType = 'statistics' | 'trend' | 'clustering' | 'correlation' | 'regression' | 'distribution'

export type ChartType = 'line' | 'bar' | 'scatter' | 'pie' | 'histogram' | 'box' | 'heatmap' | 'radar' | 'treemap' | 'wordcloud'

export type DataType = 'tabular' | 'text' | 'image' | 'audio' | 'video' | 'mixed'
