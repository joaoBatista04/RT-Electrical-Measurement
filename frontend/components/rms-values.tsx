"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Zap, Activity, ScanEye } from "lucide-react"

interface RMSValues {
  tensaoRMS: number
  correnteRMS: number
  potenciaRMS: number
}

interface RMSValuesProps {
  values: RMSValues
}

export function RMSValues({ values }: RMSValuesProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ScanEye className="h-5 w-5 text-blue-500" />
            Potência
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">{values.potenciaRMS}</div>
            <div className="text-lg text-muted-foreground">W</div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-500" />
            Tensão RMS
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 dark:text-blue-400">{values.tensaoRMS}</div>
            <div className="text-lg text-muted-foreground">V</div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-red-500" />
            Corrente RMS
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center">
            <div className="text-4xl font-bold text-red-600 dark:text-red-400">{values.correnteRMS}</div>
            <div className="text-lg text-muted-foreground">A</div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
