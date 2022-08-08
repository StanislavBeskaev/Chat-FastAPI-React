import React, {useCallback, useEffect} from 'react'
import {observer} from 'mobx-react-lite'

import TextMessage from './TextMessage'
import InfoMessage from './InfoMessage'
import UnreadLine from './UnreadLine'
import messagesStore from '../../../stores/messagesStore'


const Messages = ({messages, login}) => {
  const {needScrollToNewMessage, selectedChatId} = messagesStore
  console.log('needScrollToNewMessage', needScrollToNewMessage)
  const setRef = useCallback(node => {
    if (node) {
      console.log('Messages scroll to last message')
      node.scrollIntoView({behavior: 'auto'})
    }
  }, [])

  useEffect(() => {
    console.log('Messages change chat, current chatId', selectedChatId)
    console.log('Messages chatWasOpened', messagesStore.isSelectedChatWasOpened())
    if (!messagesStore.isSelectedChatWasOpened()) {
      messagesStore.setSelectedChatWasOpened()
      if (messagesStore.getChatNotViewedMessagesCount(selectedChatId) > 0) return
      const lastChatMessageId = messagesStore.getSelectedChatLastMessageId()
      if (!lastChatMessageId) return
      const lastMessage = document.getElementById(lastChatMessageId)
      if (!lastMessage) return
      lastMessage.scrollIntoView({behavior: 'auto'})
      console.log(`Messages первый раз в чате ${selectedChatId} прокрутка до последнего сообщения`)
    } else {
      if (messagesStore.getChatNotViewedMessagesCount(selectedChatId) > 0) return
      const lastChatMessageInView = messagesStore.getSelectedChatLastMessageInView()
      if (!lastChatMessageInView) return
      const lastMessage = document.getElementById(lastChatMessageInView.message_id)
      if (!lastMessage) return
      lastMessage.scrollIntoView({behavior: 'auto', block: 'end'})
      console.log(`Messages уже были в чате ${selectedChatId} прокрутка до последнего видимого сообщения: ${lastChatMessageInView.text}`)
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
        console.log('needScrollToLastMessage=',  needScrollToLastMessage)

        if (message.type === "TEXT") {
          return (
            <>
              { needUnreadLine ? <UnreadLine /> : null}
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