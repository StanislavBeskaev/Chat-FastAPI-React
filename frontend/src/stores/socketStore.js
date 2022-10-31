import {makeAutoObservable} from "mobx"
import {toast} from 'react-toastify'

import authStore from "./authStore"
import messagesStore from './messagesStore'
import chatMembersModalStore from './modals/chatMembersModalStore'
import logMessages from '../log'
import ConfirmDeleteModalStore from "./modals/confirmDeleteModalStore"


const SOCKET_OPEN_STATE = 1
const SOCKET_CLOSING_STATE = 2
const SOCKET_CLOSE_STATE = 3

class SocketStore {
  socket = null
  login = null
  reconnectAttempts = 0
  needLoadMessages = false
  closing = false

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан SocketStore")
  }

  isOnline() {
    return [SOCKET_CLOSING_STATE, SOCKET_CLOSE_STATE].indexOf(this.socket?.readyState) === -1 && !this.closing
  }

  async connect(login) {
    if (!login) {
      logMessages("SocketStore, connect передан пустой login выходим")
      return
    }

    const serverUrl = process.env.NODE_ENV === 'development' ? 'localhost:8000' : window.__ENV__.APP_WS_ADDRESS
    logMessages(`SocketStore, устанавливаем ws соединение, адрес сервера: ${serverUrl}, login=${login}`)
    const ws = new WebSocket(`ws://${serverUrl}/ws/${login}`)
    this.setSocket(ws)
    this.setLogin(login)
    ws.onopen = async e =>  {
      logMessages("ws.onopen", e)
      this.setReconnectAttempts(0)
      this.setClosing(false)
      if (this.needLoadMessages) {
        await messagesStore.loadMessages()
        this.setNeedLoadMessages(false)
      }
    }

    await this._addWSMessagesListener()

    ws.onclose = () => {
      logMessages("ws.onclose")
      this.setClosing(true)
      this.setNeedLoadMessages(true)
      this._askReconnect()
    }
  }

  _askReconnect() {
    logMessages("_askReconnect", authStore.isAuth, this.login)
    if (!(authStore.isAuth && this.login)) {
      logMessages('Не авторизован ничего не делаем')
      return
    }

    if (this.reconnectAttempts === 0) {
      ConfirmDeleteModalStore.open(
        "Потеряна связь с сервером. Переподключиться?",
        async () => {
          this.setReconnectAttempts(1)
          await this.connect(this.login)
        },
        () => {}
      )
    } else{
      ConfirmDeleteModalStore.open(
        "Не удалось переподключиться. Необходимо обновить страницу, обновляем?",
        () => window.location.reload(),
        () => {}
      )
    }
  }

  disconnect() {
    if (!this.socket) {
      logMessages("SocketStore, disconnect не выполняется, сокет не определён")
      return
    }
    logMessages('SocketStore, disconnect')
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
    logMessages('SocketStore start _sendMessage', this.socket)
    if (this.socket?.readyState !== SOCKET_OPEN_STATE) {
      this._askReconnect()
      return
    }
    const message = JSON.stringify(
      {
        type: messageType,
        data: messageData
      }
    )
    logMessages(`SocketStore, отправка сообщения: ${message}`)
    this.socket.send(message)
  }

  async _addWSMessagesListener() {
    this.socket.onmessage = async (e) => {
      const msg = JSON.parse(e.data)
      logMessages('SocketStore, сообщение из ws: ', msg)

      const messageHandlers = {
        "TEXT": this._handleTextMessage.bind(this),
        "STATUS": this._handleStatusMessage.bind(this),
        "START_TYPING": this._handleStartTypingMessage.bind(this),
        "STOP_TYPING": this._handleStopTypingMessage.bind(this),
        "NEW_CHAT": this._handleNewChatMessage.bind(this),
        "CHANGE_CHAT_NAME": this._handleChangeChatNameMessage.bind(this),
        "ADD_TO_CHAT": this._handleAddToChatMessage.bind(this),
        "DELETE_FROM_CHAT": this._handleDeleteFromChatMessage.bind(this),
        "CHANGE_MESSAGE_TEXT": this._handleChangeMessageTextMessage.bind(this),
        "DELETE_MESSAGE": this._handleDeleteMessageMessage.bind(this),
        "LEAVE_CHAT": this._handleLeaveFromChatMessage.bind(this),
        "DELETE_CHAT": this._handleDeleteChatMessage.bind(this),
        DEFAULT: async (data) => {logMessages('SocketStore, неожиданное сообщение из ws:', msg)}
      }

      const handler = messageHandlers[msg.type] || messageHandlers.DEFAULT
      await handler(msg.data)
    }
  }

  async _handleTextMessage(messageData) {
    messagesStore.addMessage(messageData, this.sendReadMessage.bind(this))
  }

  async _handleStartTypingMessage(messageData) {
    messagesStore.addTypingLogin(messageData.chat_id, messageData.login)
  }

  async _handleStopTypingMessage(messageData) {
    messagesStore.deleteTypingLogin(messageData.chat_id, messageData.login)
  }

  async _handleNewChatMessage(messageData) {
    messagesStore.addNewChat(messageData)
    this._showAddNewChatNotification(messageData)
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

  async _handleChangeChatNameMessage(messageData) {
    const chatId = messageData["chat_id"]
    const previousChatName = messagesStore.getChatNameById(chatId)
    messagesStore.changeChatName(messageData)
    const currentChatName = messagesStore.getChatNameById(chatId)
    this._showChangeChatNameNotification(previousChatName, currentChatName)
  }

  async _handleAddToChatMessage(messageData) {
    if (messageData.login === this.login) {
      logMessages('Меня добавляют в чат')
      this._showAddToChatNotification(messageData)
      await messagesStore.addChat(messageData.chat_id)
      return
    }
    const {show, chatId} = chatMembersModalStore
    if (show && chatId === messageData.chat_id) {
      await chatMembersModalStore.loadChatMembers()
    }
  }

  async _handleDeleteFromChatMessage(messageData) {
    const {chat_id: messageChatId} = messageData
    if (messageData.login === this.login) {
      logMessages('Меня удаляют из чата')
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

  async _handleChangeMessageTextMessage(messageData) {
    messagesStore.changeMessageText(messageData)
  }

  async _handleDeleteMessageMessage(messageData) {
    messagesStore.deleteMessage(messageData)
  }

  async _handleLeaveFromChatMessage(messageData) {
    const {chat_id: messageChatId} = messageData
    if (messageChatId === messagesStore.selectedChatId) this.sendStopTyping(messageChatId)
    if (chatMembersModalStore.show && messageChatId === chatMembersModalStore.chatId) chatMembersModalStore.close()
    messagesStore.deleteChat(messageChatId)
    this._showLeaveFromChatNotification(messageData)
  }

  async _handleDeleteChatMessage(messageData) {
    const {chat_id: messageChatId} = messageData
    if (messageChatId === messagesStore.selectedChatId) this.sendStopTyping(messageChatId)
    if (chatMembersModalStore.show && messageChatId === chatMembersModalStore.chatId) chatMembersModalStore.close()
    messagesStore.deleteChat(messageChatId)
    this._showDeleteChatNotification(messageData)
  }

  _showAddNewChatNotification(messageData) {
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

  _showLeaveFromChatNotification(messageData) {
    const {chat_name: chatName} = messageData
    toast.info(`Вы вышли из чата: ${chatName}`)
  }

  _showDeleteChatNotification(messageData) {
    const {login, chat_name: chatName} = messageData
    toast.error(`Пользователь ${login} удалил чат ${chatName}`)
  }

  setSocket(socket) {
    this.socket = socket
  }

  setLogin(login) {
    this.login = login
  }

  setReconnectAttempts(value) {
    this.reconnectAttempts = value
  }

  setNeedLoadMessages(bool) {
    this.needLoadMessages = bool
  }

  setClosing(bool) {
    this.closing = bool
  }
}

export default new SocketStore()
