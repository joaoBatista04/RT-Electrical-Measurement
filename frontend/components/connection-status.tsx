"use client"

import { Wifi, WifiOff } from "lucide-react"

interface ConnectionStatusProps {
  isConnected: boolean
}

export function ConnectionStatus({ isConnected }: ConnectionStatusProps) {
  return (
    <div
      className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
        isConnected
          ? "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400"
          : "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400"
      }`}
    >
      {isConnected ? (
        <>
          <Wifi className="h-4 w-4" />
          Dispositivo Conectado
        </>
      ) : (
        <>
          <WifiOff className="h-4 w-4" />
          Dispositivo Desconectado
        </>
      )}
    </div>
  )
}
