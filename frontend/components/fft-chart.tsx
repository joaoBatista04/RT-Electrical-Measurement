"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RefreshCw, BarChart3 } from "lucide-react"

interface FFTData {
  frequency: number
  amplitude: number
}

interface FFTChartProps {
  data: FFTData[]
  onUpdate: () => void
  isLoading: boolean
}

export function FFTChart({ data = [], onUpdate, isLoading }: FFTChartProps) {
  const formatFrequency = (value: number) => {
    if (value >= 1000) {
      return `${(value / 1000).toFixed(0)}k`
    }
    return value.toString()
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            <div>
              <CardTitle>Domínio Frequência</CardTitle>
              <CardDescription>Análise FFT - Espectro de frequência da tensão e corrente</CardDescription>
            </div>
          </div>
          <Button
            onClick={async () => {
              await onUpdate()
            }}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="flex items-center gap-2 bg-transparent"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            {isLoading ? "Atualizando..." : "Atualizar FFT"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="frequency"
              tickFormatter={formatFrequency}
              label={{ value: "Frequencial[Hz]", position: "insideBottom", offset: -10 }}
            />
            <YAxis domain={[0, 1]} label={{ value: "Amplitude[dB]", angle: -90, position: "insideLeft" }} hide={true} />
            <Tooltip
              formatter={(value: number) => [`${value.toFixed(3)} dB`, "Amplitude"]}
              labelFormatter={(label: number) => `Frequência: ${formatFrequency(label)}Hz`}
            />
            <Bar dataKey="amplitude">
              {data.map((entry, index) => {
                const amplitude = entry.amplitude ?? 0
                let color = "#3b82f6"
                if (amplitude > 0.7) color = "#ef4444"
                else if (amplitude > 0.3) color = "#f97316"

              return <Cell key={`cell-${index}`} fill={color} />
              })}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
