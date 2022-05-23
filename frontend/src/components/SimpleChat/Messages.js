import React, {useCallback} from 'react'

const Messages = ({messages, login}) => {
  const setRef = useCallback(node => {
    if (node) {
      node.scrollIntoView({smooth: true})
    }
  }, [])

  return (
    <div className="flex-grow-1 overflow-auto">
      <div className="d-flex flex-column align-items-start justify-content-end px-3">
        {messages.map((message, index) => {
          const lastMessage = index === messages.length - 1
          const fromMe = message.login === login
          return (
            <div
              ref={lastMessage ? setRef : null}
              key={index}
              className={`my-1 d-flex flex-column ${fromMe ? 'align-self-end align-items-end' : 'align-items-start'}`}
            >
              <div
                className={`rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
              >
                {message.text}
              </div>
              <div className={`text-muted small ${fromMe? 'text-end' : ''}`}>
                {fromMe ? 'Вы' : message.login}, {message.time}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default Messages