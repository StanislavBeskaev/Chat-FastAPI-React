import React, { useContext, useEffect, useState } from 'react'

const SocketContext = React.createContext()

export function useSocket() {
  return useContext(SocketContext)
}

export function SocketProvider({ login, children }) {
  const [socket, setSocket] = useState()

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${login}`)
    setSocket(ws)

    return () => ws.close()
  }, [login])

  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  )
}