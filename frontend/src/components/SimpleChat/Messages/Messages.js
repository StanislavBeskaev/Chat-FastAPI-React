import React, {useCallback} from 'react'
import {observer} from 'mobx-react-lite'

import TextMessage from './TextMessage'
import InfoMessage from './InfoMessage'


const Messages = ({messages, login}) => {
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true})
    }
  }, [])

  if (messages.length === 0) {
    return <div className="m-3">Сообщений пока нет</div>
  }

  // TODO сделать разделение непрочитанных сообщений
  return (
    <>
      {messages.map((message, index) => {
        const lastMessage = index === messages.length - 1
        const fromMe = message.login === login
        // TODO сделать нормально, сейчас будет ломаться при одном сообщении
        const needUnreadLine = message.is_read === false && messages[index - 1]?.is_read !== false
        if (message.type === "TEXT") {
          return (
            <div
              ref={lastMessage ? setRef : null}
              key={message.message_id}
              className={`w-50 my-1 d-flex flex-column ${fromMe ? 'align-self-end align-items-end' : 'align-items-start'}`}
            >
              {/*TODO отдельный компоннент для отделения*/}
              {
                needUnreadLine
                  ? <div className="text-primary align-self-center m-3">Дальше не прочитанные сообщения</div>
                  : null
              }
              <TextMessage fromMe={fromMe} message={message} />
            </div>
          )
        } else {
          return (
            <div
              ref={lastMessage ? setRef : null}
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