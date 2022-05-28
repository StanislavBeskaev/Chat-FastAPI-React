import React, {useCallback} from 'react'

import TextMessage from './TextMessage'
import StatusMessage from './StatusMessage'
import {observer} from 'mobx-react-lite'


const Messages = ({messages, login}) => {
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true})
    }
  }, [])

  const messageTypeMap = {
    "TEXT": TextMessage,
    "STATUS": StatusMessage
  }

  return (
    <>
      {messages.map((message, index) => {
        const lastMessage = index === messages.length - 1
        const fromMe = message.login === login
        const MessageTypeComponent = messageTypeMap[message.type]
        return (
          <div
            ref={lastMessage ? setRef : null}
            key={message.id}
            className={`my-1 d-flex flex-column ${fromMe ? 'align-self-end align-items-end' : 'align-items-start'}`}
          >
            <MessageTypeComponent fromMe={fromMe} message={message} />
          </div>
        )
      })}
    </>
  )
}

export default observer(Messages)