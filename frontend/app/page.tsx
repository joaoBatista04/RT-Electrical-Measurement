"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Zap, Activity } from "lucide-react"
import { TimeSeriesChart } from "@/components/time-series-chart"
import { FFTChart } from "@/components/fft-chart"
import { LoadIdentification } from "@/components/load-identification"
import { PredictionTable } from "@/components/prediction-table"
import { RMSValues } from "@/components/rms-values"
import { ConnectionStatus } from "@/components/connection-status"

interface TimeSeriesData {
  timestamp: string
  tensao: number
  corrente: number
}

interface FFTData {
  frequency: number
  amplitude: number
}

interface LoadIdentificationResult {
  type: "resistiva" | "indutiva" | "capacitiva"
  confidence: number
}

interface RMSValuesType {
  tensaoRMS: number
  correnteRMS: number
}

export default function EnergyDashboard() {
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([])
  const [fftData, setFFTData] = useState<FFTData[]>([])
  const [rmsValues, setRMSValues] = useState<RMSValuesType>({
    tensaoRMS: 0.0,
    correnteRMS: 0.0
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isFFTLoading, setIsFFTLoading] = useState(false)
  const [loadResult, setLoadResult] = useState<LoadIdentificationResult | null>(null)

  async function getFFTData() {
    try {
        await fetch("http://localhost:8000/rt_energy/get_fft/").then(async (response) => {
        if (!response.ok) {
          console.error("Erro ao buscar dados da FFT")
        }
        await response.json().then((data) => {
          const formatted = data.map((item: any) => ({
            frequency: item.frequency,
            amplitude: item.amplitude,
          }))

          return formatted
        })
      })
    } catch (error) {
      console.error("Erro no getFFTData:", error)
      return [];
    }
  }

  const updateRMSValues = async () => {
    fetch("http://localhost:8000/rt_energy/latest_rms/").then(async (response) => {
      if (!response.ok) {
        console.error("Erro ao buscar valores RMS")
        return
      }
      const data = await response.json()
      setRMSValues({
        tensaoRMS: data.v_rms.toFixed(1),
        correnteRMS: data.i_rms.toFixed(1),
      })
    })
  }

  const fetchTimeSeriesData = async () => {
    try {
      await fetch("http://localhost:8000/rt_energy/latest_batch/").then(async (response) => {
        if (!response.ok) {
          console.error("Erro ao buscar dados da série temporal")
          return
        }

        const data = await response.json()
        const formattedData = data.map((item: any) => ({
          timestamp: item.timestamp,
          tensao: item.voltage.toFixed(1),
          corrente: item.current.toFixed(1),
        }))

        setTimeSeriesData(formattedData)
      })
    } catch (error) {
      console.error("Erro ao buscar dados:", error)
    }
  }

  const handleIdentifyLoad = async () => {
    setIsLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 2000))

      const loadTypes: ("resistiva" | "indutiva" | "capacitiva")[] = ["resistiva", "indutiva", "capacitiva"]
      const randomType = loadTypes[Math.floor(Math.random() * loadTypes.length)]
      const confidence = Math.floor(Math.random() * 20) + 80

      setLoadResult({
        type: randomType,
        confidence,
      })
    } catch (error) {
      console.error("Erro ao identificar carga:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdateFFT = async () => {
    setIsFFTLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      setFFTData(getFFTData())
    } catch (error) {
      console.error("Erro ao atualizar FFT:", error)
    } finally {
      setIsFFTLoading(false)
    }
  }

  useEffect(() => {
    fetchTimeSeriesData()
    const interval = setInterval(fetchTimeSeriesData, 8000)
    const rmsInterval = setInterval(updateRMSValues, 5000)

    return () => {
      clearInterval(interval)
      clearInterval(rmsInterval)
    }
  }, [])

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Zap className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Painel de Controle de Energia</h1>
          </div>
        </div>

        <RMSValues values={rmsValues} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Monitoramento de Tensão e Corrente
              </CardTitle>
              <CardDescription>Série temporal de tensão (V) e corrente (A) em tempo real</CardDescription>
            </CardHeader>
            <CardContent>
              <TimeSeriesChart data={timeSeriesData} />
            </CardContent>
          </Card>

          <LoadIdentification result={loadResult} onIdentify={handleIdentifyLoad} isLoading={isLoading} />
        </div>

        {/* <FFTChart data={fftData} onUpdate={handleUpdateFFT} isLoading={isFFTLoading} /> */}
      </div>
    </div>
  )
}
