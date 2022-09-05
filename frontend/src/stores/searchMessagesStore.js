import {makeAutoObservable} from 'mobx'

import messagesStore from './messagesStore'
import logMessages from '../log'


class SearchMessagesStore {
  chats = {}

  constructor() {
    makeAutoObservable(this)
    logMessages("Создан SearchMessagesStore")
  }

  setDefaultState() {
    this.chats = {}
  }

  initialize(chatIds) {
    for (let chatId of chatIds) {
      this.chats[chatId] = this.getInitialSearchState()
    }
  }

  getInitialSearchState() {
    return {
      text: '',
      count: null,
      element: null,
      current: 0,
      messagesIds: []
    }
  }

  deleteChat(chatId) {
    delete this.chats[chatId]
  }

  addChat(chatId) {
    this.chats[chatId] = this.getInitialSearchState()
  }

  getSelectedChatId() {
    return messagesStore.selectedChatId
  }

  getSearchText() {
    return this._getAttribute('text')
  }

  _getAttribute(attributeName) {
    const currentChatSearchState = this._getCurrentChatSearchState()
    return currentChatSearchState[attributeName]
  }

  _setAttribute(attributeName, value) {
    const currentChatSearchState = this._getCurrentChatSearchState()
    currentChatSearchState[attributeName] = value
  }

  _getCurrentChatSearchState() {
    return this.chats[this.getSelectedChatId()]
  }

  setSearchText(text) {
    this._setAttribute('text', text)
    this.dropSelection()

    if (!text) {
      this.setMessagesIds([])  // важно сбросить ids сообщений, что бы не применилось выделение в setCurrent
      this.setCount(null)
      this.setCurrent(0)
      this.setElement(null)
      return
    }

    logMessages('Ищем текст:', text)
    const messagesIds = messagesStore.getMessagesIdsWithTextInCurrentChat(text)
    this.setMessagesIds(messagesIds)
    this.setCount(messagesIds.length)
    this.setCurrent(0)

    if (messagesIds.length > 0) {
      const firstMessage = document.getElementById(messagesIds[0])
      this.changeElement(firstMessage)
    }
  }

  changeElement(newElement) {
    this.dropSelection()

    newElement.scrollIntoView({block: "center"})
    newElement.parentElement.style.border = '3px solid dodgerblue'
    newElement.parentElement.style.borderRadius = '8px'
    newElement.parentElement.style.padding = '3px'
    this.setElement(newElement)
  }

  dropSelection() {
    const element = this.getElement()
    if (element) {
      element.parentElement.style.border = null
      element.parentElement.style.padding = null
    }
  }

  increaseCurrent() {
    const count = this.getCount()
    const current = this.getCurrent()

    if (!count || current === (count - 1)) {
      // для возможности хождения по кругу
      this.setCurrent(0)
      return
    }

    this.setCurrent(current + 1)
  }

  decreaseCurrent() {
    const count = this.getCount()
    const current = this.getCurrent()

    if (!count || current === 0) {
      // для возможности хождения по кругу
      this.setCurrent(count - 1)
      return
    }

    this.setCurrent(current - 1)
  }

  getCurrent() {
    return this._getAttribute('current')
  }

  setCurrent(current) {
    this._setAttribute('current', current)

    const messagesIds = this.getMessagesIds()
    if (messagesIds.length > 0) {
      this.changeElement(document.getElementById(messagesIds[current]))
    }
  }

  getElement() {
    return this._getAttribute('element')
  }

  setElement(element) {
    this._setAttribute('element', element)
  }

  getCount() {
    return this._getAttribute('count')
  }

  setCount(count) {
    this._setAttribute('count', count)
  }

  getMessagesIds() {
    return this._getAttribute('messagesIds')
  }

  setMessagesIds(messagesIds) {
    return this._setAttribute('messagesIds', messagesIds)
  }
}

export default new SearchMessagesStore()
