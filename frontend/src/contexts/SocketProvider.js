import React, { useContext, useEffect, useState } from 'react'

import {toast} from 'react-toastify'
import messagesStore from '../stores/messagesStore'
import authStore from '../stores/authStore'
import chatMembersModalStore from '../stores/modals/chatMembersModalStore'


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

  useEffect(() => {
    if (!socket) return

    socket.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      console.log('Сообщение из ws: ', msg)
      let chatId

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
          chatId = msg.data["chat_id"]
          const previousChatName = messagesStore.getChatNameById(chatId)
          messagesStore.changeChatName(msg.data)
          const currentChatName = messagesStore.getChatNameById(chatId)
          changeChatNameNotification(previousChatName, currentChatName)
          break
        case 'ADD_TO_CHAT':
          await handleAddToChatMessage(msg.data)
          break
        case 'DELETE_FROM_CHAT':
          await handleDeleteFromChatMessage(msg.data)
          break
      }
    }
  }, [socket])

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

  const handleAddToChatMessage = async (data) => {
    const {login} = authStore.user
    if (data.login === login) {
      console.log('Меня добавляют в чат')
      addToChatNotification(data)
      await messagesStore.addChat(data.chat_id)
      return
    }
    const {show, chatId} = chatMembersModalStore
    if (show && chatId === data.chat_id) {
      await chatMembersModalStore.loadChatMembers()
    }
  }

  const handleDeleteFromChatMessage = async (data) => {
    const {login} = authStore.user
    if (data.login === login) {
      console.log('Меня удаляют из чата')
      if (data.chat_id === messagesStore.selectedChatId) sendStopTyping(data.chat_id)
      if (chatMembersModalStore.show && data.chat_id === chatMembersModalStore.chatId) chatMembersModalStore.close()
      messagesStore.deleteChat(data.chat_id)
      deleteFromChatNotification(data)
    }
    const {show, chatId} = chatMembersModalStore
    if (show && chatId === data.chat_id) {
      await chatMembersModalStore.loadChatMembers()
    }
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

  const addToChatNotification = data => {
    const {chat_name: chatName} = data
    toast.success(`Вы добавлены к чату: ${chatName}`)
  }

  const deleteFromChatNotification = data => {
    const {chat_name: chatName} = data
    toast.error(`Вы удалены из чата: ${chatName}`)
  }

  const addNewChatNotification = data => {
    const {chat_name: chatName} = data
    toast.info(`Создан новый чат: ${chatName}`)
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