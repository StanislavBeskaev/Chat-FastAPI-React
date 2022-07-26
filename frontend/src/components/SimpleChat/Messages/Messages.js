import React, {useCallback} from 'react'
import {observer} from 'mobx-react-lite'

import TextMessage from './TextMessage'
import InfoMessage from './InfoMessage'
import UnreadLine from './UnreadLine'
import messagesStore from '../../../stores/messagesStore'


const Messages = ({messages, login}) => {
  const {needScrollToNewMessage} = messagesStore
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true})
    }
  }, [])

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
        const needScrollToLastMessage = isLastMessage && !isFindUnreadMessage || needScrollToNewMessage

        // TODO придумать прокрутку вниз, когда не видно последнее сообщение
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