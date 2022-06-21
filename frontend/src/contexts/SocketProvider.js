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
          messagesStore.addMessage(msg.data)
          break
        case 'STATUS':
          addStatusNotification(msg.data)
          break
        case 'START_TYPING':
          messagesStore.addTypingLogin(msg.data.chat_id, msg.data.login)
          break
        case 'STOP_TYPING':
          messagesStore.deleteTypingLogin(msg.data.chat_id, msg.data.login)
          break
        case 'NEW_CHAT':
          messagesStore.addNewChat(msg.data)
          addNewChatNotification(msg.data)
          break
        case 'CHANGE_CHAT_NAME':
          const chatId = msg.data["chat_id"]
          const previousChatName = messagesStore.getChatNameById(chatId)
          messagesStore.changeChatName(msg.data)
          const currentChatName = messagesStore.getChatNameById(chatId)
          changeChatNameNotification(previousChatName, currentChatName)
      }
    }

    return () => ws.close()
  }, [login])

  const sendText = (text, chatId) => {
    console.log(`Отправка сообщения:`, text)
    const textMessage = JSON.stringify(
      {
        type: "TEXT",
        data: {text, chatId}
      }
    )
    socket.send(textMessage)
  }

  const sendStartTyping = (chatId) => {
    const typingStartMessage = JSON.stringify(
      {
        type: "START_TYPING",
        data: {chatId}
      }
    )

    socket.send(typingStartMessage)
  }

  const sendStopTyping = (chatId) => {
    const typingStartMessage = JSON.stringify(
      {
        type: "STOP_TYPING",
        data: {chatId}
      }
    )

    socket.send(typingStartMessage)
  }

  const addStatusNotification = data => {
    const {login: msgLogin, text, online_status: onlineStatus} = data

    if (login === msgLogin) return

    if (onlineStatus === "ONLINE") {
      toast.success(text)
    } else {
      toast.error(text)
    }
  }

  const addNewChatNotification = data => {
    const {chat_name: chatName} = data
    toast.info(`Вы добавлены к чату: ${chatName}`)
  }

  const changeChatNameNotification = (previous, current) => {
    toast.info(`Название чата "${previous}" изменено на "${current}"`)
  }

  const value = {
    socket,
    sendStartTyping,
    sendStopTyping,
    sendText,
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}