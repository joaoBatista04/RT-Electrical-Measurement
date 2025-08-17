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
    tensaoRMS: 220.5,
    correnteRMS: 12.3,
  })
  const [predictionData, setPredictionData] = useState({
    kwh: 125.5,
    ah: 8.2,
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isPredictionLoading, setIsPredictionLoading] = useState(false)
  const [isFFTLoading, setIsFFTLoading] = useState(false)
  const [loadResult, setLoadResult] = useState<LoadIdentificationResult | null>(null)
  const [isDeviceConnected, setIsDeviceConnected] = useState(true)

  const generateFFTData = () => {
    const data = []

    data.push({
      frequency: 0,
      amplitude: 0.95,
    })

    for (let i = 50; i <= 500; i += 50) {
      data.push({
        frequency: i,
        amplitude: Math.max(0.1, 0.8 - i / 1000),
      })
    }

    data.push({
      frequency: 1000,
      amplitude: 0.35,
    })

    for (let i = 1500; i <= 25000; i += 1000) {
      data.push({
        frequency: i,
        amplitude: Math.random() * 0.1 + 0.05,
      })
    }

    return data
  }

  const updateRMSValues = () => {
    setRMSValues({
      tensaoRMS: Number((Math.random() * 20 + 210).toFixed(1)),
      correnteRMS: Number((Math.random() * 10 + 8).toFixed(1)),
    })
  }

  const fetchTimeSeriesData = async () => {
    setIsLoading(true)
    try {
      const simulatedData = Array.from({ length: 24 }, (_, i) => ({
        timestamp: `${String(i).padStart(2, "0")}:00`,
        tensao: Math.floor(Math.random() * 50) + 200,
        corrente: Math.floor(Math.random() * 20) + 5,
      }))

      setTimeSeriesData(simulatedData)
      setFFTData(generateFFTData())
      updateRMSValues()
    } catch (error) {
      console.error("Erro ao buscar dados:", error)
    } finally {
      setIsLoading(false)
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

  const handleUpdatePrediction = async () => {
    setIsPredictionLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))

      const newKwh = Math.floor(Math.random() * 100) + 80 + Math.random() * 50
      const newAh = Math.floor(Math.random() * 10) + 5 + Math.random() * 5

      setPredictionData({
        kwh: Number(newKwh.toFixed(1)),
        ah: Number(newAh.toFixed(1)),
      })
    } catch (error) {
      console.error("Erro ao atualizar predição:", error)
    } finally {
      setIsPredictionLoading(false)
    }
  }

  const handleUpdateFFT = async () => {
    setIsFFTLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500))
      setFFTData(generateFFTData())
    } catch (error) {
      console.error("Erro ao atualizar FFT:", error)
    } finally {
      setIsFFTLoading(false)
    }
  }

  useEffect(() => {
    fetchTimeSeriesData()
    const interval = setInterval(fetchTimeSeriesData, 30000)
    const rmsInterval = setInterval(updateRMSValues, 5000)
    const connectionInterval = setInterval(() => {
      setIsDeviceConnected((prev) => (Math.random() > 0.1 ? true : !prev))
    }, 10000)

    return () => {
      clearInterval(interval)
      clearInterval(rmsInterval)
      clearInterval(connectionInterval)
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
          <ConnectionStatus isConnected={isDeviceConnected} />
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

        <FFTChart data={fftData} onUpdate={handleUpdateFFT} isLoading={isFFTLoading} />

        <PredictionTable data={predictionData} onUpdate={handleUpdatePrediction} isLoading={isPredictionLoading} />
      </div>
    </div>
  )
}
