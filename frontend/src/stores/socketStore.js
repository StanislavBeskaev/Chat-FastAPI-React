import {makeAutoObservable} from "mobx"
import {toast} from 'react-toastify'

import authStore from './authStore'
import messagesStore from './messagesStore'
import chatMembersModalStore from './modals/chatMembersModalStore'


class SocketStore {
  socket = null
  login = null

  constructor() {
    makeAutoObservable(this)
    console.log("Создан SocketStore")
  }

  async connect(login) {
    if (!login) {
      console.log("SocketStore, connect передан пустой login выходим")
      return
    }

    const serverUrl = process.env.NODE_ENV === 'development' ? 'localhost:8000' : process.env.REACT_APP_WS_ADDRESS
    console.log(`SocketStore, устанавливаем ws соединение, адрес сервера: ${serverUrl}, login=${login}`)
    const ws = new WebSocket(`ws://${serverUrl}/ws/${login}`)
    this.setSocket(ws)
    this.setLogin(login)

    await this._addWSMessagesListener()

    ws.onclose = () => {
      if (authStore.isAuth && this.login) {
        setTimeout(() => {
          console.log(`SocketStore WS закрыт, авторизован, переподключаемся, login=${authStore.user.login}`)
          this.connect(this.login)
        }, 200)
      } else {
        console.log('SocketStore WS закрыт, не авторизован, не переподключаемся')
      }
    }
  }

  disconnect() {
    if (!this.socket) {
      console.log("SocketStore, disconnect не выполняется, сокет не определён")
      return
    }
    console.log('SocketStore, disconnect')
    this.login = null
    this.socket.close()
    this.socket = null
  }

  sendText(text, chatId) {
    this._sendMessage({text, chatId}, "TEXT")
  }

  sendStartTyping(chatId) {
    this._sendMessage({chatId}, "START_TYPING")
  }

  sendStopTyping(chatId) {
    this._sendMessage({chatId}, "STOP_TYPING")
  }

  sendReadMessage(messageId) {
    this._sendMessage({messageId}, "READ_MESSAGE")
  }

  _sendMessage(messageData, messageType) {
    const message = JSON.stringify(
      {
        type: messageType,
        data: messageData
      }
    )
    console.log(`SocketStore, отправка сообщения: ${message}`)
    this.socket.send(message)
  }

  async _addWSMessagesListener() {
    this.socket.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      console.log('SocketStore, сообщение из ws: ', msg)

      switch (msg.type) {
        case 'TEXT':
          messagesStore.addMessage(msg.data, this.sendReadMessage.bind(this))
          break
        case 'STATUS':
          await this._handleStatusMessage(msg.data)
          break
        case 'START_TYPING':
          messagesStore.addTypingLogin(msg.data.chat_id, msg.data.login)
          break
        case 'STOP_TYPING':
          messagesStore.deleteTypingLogin(msg.data.chat_id, msg.data.login)
          break
        case 'NEW_CHAT':
          messagesStore.addNewChat(msg.data)
          this._showAddNewChatNotification(msg.data)
          break
        case 'CHANGE_CHAT_NAME':
          this._handleChangeChatNameMessage(msg.data)
          break
        case 'ADD_TO_CHAT':
          await this._handleAddToChatMessage(msg.data)
          break
        case 'DELETE_FROM_CHAT':
          await this._handleDeleteFromChatMessage(msg.data)
          break
        case 'CHANGE_MESSAGE_TEXT':
          messagesStore.changeMessageText(msg.data)
          break
        case 'DELETE_MESSAGE':
          messagesStore.deleteMessage(msg.data)
          break
        default:
          console.log('SocketStore, неожиданное сообщение из ws:', msg)
      }
    }
  }

  async _handleStatusMessage(messageData) {
    const {login: msgLogin, text, online_status: onlineStatus} = messageData

    if (this.login === msgLogin) return

    if (onlineStatus === "ONLINE") {
      toast.success(text)
    } else {
      toast.error(text)
      // Для случая, что бы не зависало печатание для этого логина, если он ещё печатал и внезапно отключился
      messagesStore.deleteTypingLoginFromAllChats(msgLogin)
    }

    if (chatMembersModalStore.show) {
      await chatMembersModalStore.loadChatMembers()
    }
  }

  _handleChangeChatNameMessage(messageData) {
    const chatId = messageData["chat_id"]
    const previousChatName = messagesStore.getChatNameById(chatId)
    messagesStore.changeChatName(messageData)
    const currentChatName = messagesStore.getChatNameById(chatId)
    this._showChangeChatNameNotification(previousChatName, currentChatName)
  }

  async _handleAddToChatMessage(messageData) {
    if (messageData.login === this.login) {
      console.log('Меня добавляют в чат')
      this._showAddToChatNotification(messageData)
      await messagesStore.addChat(messageData.chat_id)
      return
    }
    const {show, chatId} = chatMembersModalStore
    if (show && chatId === messageData.chat_id) {
      await chatMembersModalStore.loadChatMembers()
    }
  }

  async _handleDeleteFromChatMessage(messageData){
    const messageChatId = messageData.chat_id
    if (messageData.login === this.login) {
      console.log('Меня удаляют из чата')
      if (messageChatId === messagesStore.selectedChatId) this.sendStopTyping(messageChatId)
      if (chatMembersModalStore.show && messageChatId === chatMembersModalStore.chatId) chatMembersModalStore.close()
      messagesStore.deleteChat(messageChatId)
      this._showDeleteFromChatNotification(messageData)
    }
    const {show, chatId} = chatMembersModalStore
    if (show && chatId === messageChatId) {
      await chatMembersModalStore.loadChatMembers()
    }
  }

  _showAddNewChatNotification (messageData) {
    const {chat_name: chatName} = messageData
    toast.info(`Создан новый чат: ${chatName}`)
  }

  _showChangeChatNameNotification(previous, current) {
    toast.info(`Название чата "${previous}" изменено на "${current}"`)
  }

  _showAddToChatNotification(messageData) {
    const {chat_name: chatName} = messageData
    toast.success(`Вы добавлены к чату: ${chatName}`)
  }

  _showDeleteFromChatNotification(messageData) {
    const {chat_name: chatName} = messageData
    toast.error(`Вы удалены из чата: ${chatName}`)
  }

  setSocket(socket) {
    this.socket = socket
  }

  setLogin(login) {
    this.login = login
  }
}

export default new SocketStore()
