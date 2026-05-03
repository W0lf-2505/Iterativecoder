// src/lib/socket.ts
export function createSocket(path: string) {
  return new WebSocket(`${import.meta.env.VITE_WS_URL}${path}`)
}