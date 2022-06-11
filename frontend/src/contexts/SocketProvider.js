import React, { useContext, useEffect, useState } from 'react'

import {toast} from 'react-toastify'
import messagesStore from '../stores/messagesStore'


const SocketContext = React.createContext()

export function useSocket() {
  return useContext(SocketContext)
}

export function SocketProvider({ login, children }) {
  const [socket, setSocket] = useState()

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${login}`)
    setSocket(ws)

    ws.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      console.log('Сообщение из ws: ', msg)
      // TODO какие ещё нужны типы?
      switch (msg.type) {
        case 'TEXT':
          messagesStore.addMessage(msg)
          break
        case 'STATUS':
          addNotification(msg)
          break
      }
    }

    return () => ws.close()
  }, [login])

  const addNotification = msg => {
    const {login: msgLogin, text, type, online_status: onlineStatus} = msg

    if (login === msgLogin) return

    // TODO обновить формат сообщения
    if (type === 'STATUS') {
      if (onlineStatus === "ONLINE") {
        toast.success(text)
      } else {
        toast.error(text)
      }
    }
  }

  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  )
}