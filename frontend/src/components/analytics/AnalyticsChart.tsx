'use client'

import React from 'react'
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts'
import { AnalysisResponse } from '@/lib/api/analytics'

interface AnalyticsChartProps {
  analyses: AnalysisResponse[]
  chartType: 'line' | 'area' | 'bar' | 'pie' | 'radar'
  dataType: 'sentiment' | 'confidence' | 'personality' | 'communication' | 'behavior'
  title: string
  className?: string
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

export function AnalyticsChart({ 
  analyses, 
  chartType, 
  dataType, 
  title, 
  className = '' 
}: AnalyticsChartProps) {
  
  // データの準備
  const prepareChartData = () => {
    switch (dataType) {
      case 'sentiment':
        return analyses
          .filter(a => a.sentiment_score !== undefined)
          .map(analysis => ({
            date: new Date(analysis.created_at).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' }),
            score: analysis.sentiment_score,
            label: analysis.sentiment_label,
            title: analysis.title
          }))
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

      case 'confidence':
        return analyses
          .map(analysis => ({
            date: new Date(analysis.created_at).toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' }),
            score: analysis.confidence_score,
            type: analysis.analysis_type,
            title: analysis.title
          }))
          .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

      case 'personality':
        const personalityAnalysis = analyses.find(a => a.analysis_type === 'personality')
        if (!personalityAnalysis?.personality_traits) return []
        
        return personalityAnalysis.personality_traits.map(trait => ({
          trait: trait.trait,
          score: trait.score,
          description: trait.description
        }))

      case 'communication':
        const communicationAnalysis = analyses.find(a => a.analysis_type === 'communication')
        if (!communicationAnalysis?.communication_patterns) return []
        
        return communicationAnalysis.communication_patterns.map(pattern => ({
          pattern: pattern.pattern,
          frequency: pattern.frequency,
          strength: pattern.strength
        }))

      case 'behavior':
        const behaviorAnalysis = analyses.find(a => a.analysis_type === 'behavior')
        if (!behaviorAnalysis?.behavior_scores) return []
        
        return behaviorAnalysis.behavior_scores.map(score => ({
          category: score.category,
          score: score.score,
          maxScore: score.max_score,
          trend: score.trend
        }))

      default:
        return []
    }
  }

  const chartData = prepareChartData()

  // チャートの描画
  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="score" 
                stroke="#8884d8" 
                strokeWidth={2}
                dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="score" 
                stroke="#8884d8" 
                fill="#8884d8" 
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        )

      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="score" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        )

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ trait, pattern, category, score }) => 
                  trait || pattern || category || `${score}`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="score"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        )

      case 'radar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={chartData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="trait" />
              <PolarRadiusAxis angle={30} domain={[0, 10]} />
              <Radar
                name="スコア"
                dataKey="score"
                stroke="#8884d8"
                fill="#8884d8"
                fillOpacity={0.3}
              />
              <Tooltip />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        )

      default:
        return <div>サポートされていないチャートタイプです</div>
    }
  }

  if (chartData.length === 0) {
    return (
      <div className={`p-6 text-center text-gray-500 ${className}`}>
        <p>表示するデータがありません</p>
      </div>
    )
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      <div className="p-4 border-b">
        <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      </div>
      <div className="p-4">
        {renderChart()}
      </div>
    </div>
  )
}
