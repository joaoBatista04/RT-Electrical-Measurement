"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface TimeSeriesData {
  timestamp: string
  tensao: number
  corrente: number
}

interface TimeSeriesChartProps {
  data: TimeSeriesData[]
}

export function TimeSeriesChart({ data }: TimeSeriesChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" hide={true} />
        <YAxis yAxisId="left" domain={[-240, 240]} label={{ value: "Tensão (V)", angle: -90, position: "insideLeft" }} />
        <YAxis
          yAxisId="right"
          orientation="right"
          domain={[-10, 10]}
          label={{ value: "Corrente (A)", angle: 90, position: "insideRight" }}
        />
        <Tooltip />
        <Legend />
        <Line yAxisId="left" type="monotone" dataKey="tensao" stroke="#3b82f6" strokeWidth={2} name="Tensão" />
        <Line yAxisId="right" type="monotone" dataKey="corrente" stroke="#ef4444" strokeWidth={2} name="Corrente" />
      </LineChart>
    </ResponsiveContainer>
  )
}
