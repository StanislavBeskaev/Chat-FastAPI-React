import React, {useCallback} from 'react'
import {observer} from 'mobx-react-lite'

import TextMessage from './TextMessage'


const Messages = ({messages, login}) => {
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true})
    }
  }, [])

  if (messages.length === 0) {
    return <div className="m-3">Сообщений пока нет</div>
  }

  return (
    <>
      {messages.map((message, index) => {
        const lastMessage = index === messages.length - 1
        const fromMe = message.login === login
        return (
          <div
            ref={lastMessage ? setRef : null}
            key={message.message_id}
            className={`w-50 my-1 d-flex flex-column ${fromMe ? 'align-self-end align-items-end' : 'align-items-start'}`}
          >
            <TextMessage fromMe={fromMe} message={message} />
          </div>
        )
      })}
    </>
  )
}

export default observer(Messages)