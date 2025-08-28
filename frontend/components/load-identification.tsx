"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Zap } from "lucide-react"

interface LoadIdentificationResult {
  type: "resistiva" | "indutiva" | "capacitiva"
  phase_angle: number
}

interface LoadIdentificationProps {
  result: LoadIdentificationResult | null
  onIdentify: () => void
  isLoading: boolean
}

export function LoadIdentification({ result, onIdentify, isLoading }: LoadIdentificationProps) {
  const getLoadTypeColor = (type: string) => {
    switch (type) {
      case "resistiva":
        return "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20"
      case "indutiva":
        return "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/20"
      case "capacitiva":
        return "text-purple-600 bg-purple-100 dark:text-purple-400 dark:bg-purple-900/20"
      default:
        return "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Identificar Carga</CardTitle>
        <CardDescription>Análise automática de padrões de consumo</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center space-y-4">
          {result ? (
            <div className="p-6 border rounded-lg space-y-3">
              <Zap className="h-12 w-12 mx-auto text-primary" />
              <div className="space-y-2">
                <p className="text-sm font-medium text-foreground">Tipo de Carga Identificada:</p>
                <div
                  className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getLoadTypeColor(result.type)}`}
                >
                  Carga {result.type.charAt(0).toUpperCase() + result.type.slice(1)}
                </div>
                <p className="text-xs text-muted-foreground">Defasagem: {result.phase_angle}°</p>
              </div>
            </div>
          ) : (
            <div className="p-6 border rounded-lg">
              <Zap className="h-12 w-12 mx-auto text-muted-foreground" />
            </div>
          )}
          <Button onClick={onIdentify} disabled={isLoading} className="w-full" size="lg">
            {isLoading ? "Identificando..." : "Identificar Carga"}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
