import React, {useCallback} from 'react'

import AvatarMini from '../Avatars/AvatarMini'


const Messages = ({messages, login}) => {
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true})
    }
  }, [])

  return (
    <>
      {messages.map((message, index) => {
        const lastMessage = index === messages.length - 1
        const fromMe = message.login === login
        return (
          <div
            ref={lastMessage ? setRef : null}
            key={index}
            className={`my-1 d-flex flex-column ${fromMe ? 'align-self-end align-items-end' : 'align-items-start'}`}
          >
            <div className={`d-flex ${fromMe ? 'flex-row-reverse' : 'flex-row'}`}>
              <AvatarMini fileName={message.avatar_file}/>
              <div
                className={`mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
              >
                {message.text}
              </div>
            </div>
            <div className={`text-muted small ${fromMe ? 'text-end' : ''}`}>
              {fromMe ? 'Вы' : message.login}, {message.time}
            </div>
          </div>
        )
      })}
    </>
  )
}

export default Messages