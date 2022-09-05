import React, {useCallback, useEffect, useRef} from 'react'
import {observer} from 'mobx-react-lite'

import TextMessage from './TextMessage'
import InfoMessage from './InfoMessage'
import UnreadLine from './UnreadLine'
import messagesStore from '../../../stores/messagesStore'
import logMessages from '../../../log'


const Messages = ({messages, login}) => {
  const unreadLineRef = useRef()
  const {needScrollToNewMessage, selectedChatId} = messagesStore
  const setRef = useCallback(node => {
    if (node) {
      logMessages('Messages scroll to last message')
      node.scrollIntoView({behavior: 'smooth'})
    }
  }, [])

  useEffect(() => {
    logMessages('Messages change chat, current chatId', selectedChatId)
    logMessages('Messages chatWasOpened', messagesStore.isSelectedChatWasOpened())
    if (!messagesStore.isSelectedChatWasOpened()) {
      messagesStore.setSelectedChatWasOpened()
      if (messagesStore.getChatNotViewedMessagesCount(selectedChatId) > 0) {
        unreadLineRef.current.scrollIntoView({behavior: 'auto', block: 'center'})
        logMessages('прокрутка до UnreadLine')
        return
      }

      const lastChatMessageId = messagesStore.getSelectedChatLastMessageId()
      if (!lastChatMessageId) return
      const lastMessage = document.getElementById(lastChatMessageId)
      if (!lastMessage) return
      lastMessage.scrollIntoView({behavior: 'auto'})
      logMessages(`Messages первый раз в чате ${selectedChatId} прокрутка до последнего сообщения`)
    } else {
      const lastChatMessageInView = messagesStore.getSelectedChatLastMessageInView()
      if (!lastChatMessageInView) return
      const lastMessage = document.getElementById(lastChatMessageInView.message_id)
      if (!lastMessage) return
      lastMessage.scrollIntoView({behavior: 'auto', block: 'end'})
      logMessages(`Messages уже были в чате ${selectedChatId} прокрутка до последнего видимого сообщения: ${lastChatMessageInView.text}`)

      if (messagesStore.getChatNotViewedMessagesCount(selectedChatId) > 0) {
        unreadLineRef.current.scrollIntoView({behavior: 'smooth', block: 'center'})
        logMessages('прокрутка до UnreadLine')
      }
    }
  }, [selectedChatId])

  if (messages.length === 0) {
    return <div className="m-3">Сообщений пока нет</div>
  }

  let isFindUnreadMessage = false

  return (
    <>
      {messages.map((message, index) => {
        const fromMe = message.login === login

        let needUnreadLine = false
        // как только нашли первое непрочитанное сообщение, то показывает строку отделения новых сообщений от старых
        if (message.is_read === false && isFindUnreadMessage === false) {
          isFindUnreadMessage = true
          needUnreadLine = true
        }
        const isLastMessage = index === messages.length - 1
        const needScrollToLastMessage = isLastMessage && !isFindUnreadMessage && messagesStore.isSelectedChatLastMessageInView() || needScrollToNewMessage

        if (message.type === "TEXT") {
          return (
            <>
              {
                needUnreadLine
                  ? <div ref={unreadLineRef} className="align-self-center m-3">
                      <UnreadLine />
                    </div>
                  : null
              }
              <div
                ref={needScrollToLastMessage ? setRef : null}
                key={message.message_id}
                className={`w-50 my-1 d-flex flex-column ${fromMe ? 'align-self-end align-items-end' : 'align-items-start'}`}
              >
                <TextMessage fromMe={fromMe} message={message} />
              </div>
            </>
          )
        } else {
          return (
            <div
              ref={needScrollToLastMessage ? setRef : null}
              key={message.message_id}
              className="align-self-center my-1"
            >
              <InfoMessage message={message} />
            </div>
          )
        }
      })}
    </>
  )
}

export default observer(Messages)