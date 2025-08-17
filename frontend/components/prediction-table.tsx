"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { TrendingUp, RefreshCw } from "lucide-react"

interface PredictionData {
  kwh: number
  ah: number
}

interface PredictionTableProps {
  data: PredictionData
  onUpdate: () => void
  isLoading: boolean
}

export function PredictionTable({ data, onUpdate, isLoading }: PredictionTableProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            <div>
              <CardTitle>Predição de Consumo</CardTitle>
              <CardDescription>Previsões de consumo energético baseadas em análise preditiva</CardDescription>
            </div>
          </div>
          <Button
            onClick={onUpdate}
            disabled={isLoading}
            variant="outline"
            size="sm"
            className="flex items-center gap-2 bg-transparent"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            {isLoading ? "Atualizando..." : "Atualizar Predição"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>KWh</TableHead>
              <TableHead>Ah</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>
                <span className="font-semibold text-primary text-lg">{data.kwh.toFixed(1)} kWh</span>
              </TableCell>
              <TableCell>
                <span className="font-semibold text-secondary-foreground text-lg">{data.ah.toFixed(1)} Ah</span>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}
