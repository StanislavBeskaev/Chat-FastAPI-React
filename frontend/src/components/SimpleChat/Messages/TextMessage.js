import React, {useEffect} from 'react'
import {observer} from 'mobx-react-lite'
import {useInView} from 'react-intersection-observer'
import {ContextMenuTrigger} from 'react-contextmenu'

import {useSocket} from '../../../contexts/SocketProvider'

import addContactModalStore from '../../../stores/modals/addContactModalStore'
import contactStore from '../../../stores/contactStore'
import messagesStore from '../../../stores/messagesStore'
import messageContextMenuStore from '../../../stores/messageContextMenuStore'

import UserAvatar from '../../Avatars/UserAvatar'


const TextMessage = ({message, fromMe}) => {
  const {text, time, login, is_view: isView, message_id: messageId, change_time: changeTime} = message
  const {sendReadMessage} = useSocket()
  const { ref, inView, entry } = useInView({
    threshold: 1
  })

  useEffect(() => {
    if (!entry) return

    if (inView) {
      messagesStore.addMessageToInView(message)
    } else {
      messagesStore.deleteMessageFromInView(message)
    }
  }, [inView])

  if (isView === false) {
    if (inView) {
      messagesStore.markMessageAsView(messageId, sendReadMessage)
      console.log('viewed', messageId)
    }
  }

  const showAddContactModal = async () => {
    await addContactModalStore.showModalWithLogin(login)
  }

  const onContextMenu = e => {
    e.preventDefault()
    messageContextMenuStore.setMessageId(messageId)
  }

  return (
    <div id={message.message_id}>
      <div
        ref={ref}
        className={`d-flex ${fromMe ? 'flex-row-reverse' : 'flex-row'}`}
      >
        <div
          style={!fromMe ? {cursor: 'pointer'} : null}
          onClick={!fromMe ? showAddContactModal : null}
        >
          <UserAvatar login={login} size="sm" />
        </div>
        {/* Редактировать можно только свои сообщения */}
        {
          fromMe
            ? <ContextMenuTrigger id="message-context-menu">
                <div
                  className={`text-break mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
                  style={{cursor: 'context-menu'}}
                  onContextMenu={onContextMenu}
                >
                  {text}
                </div>
              </ContextMenuTrigger>
            : <div
                className={`text-break mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
              >
                {text}
              </div>
        }
      </div>
      <div className={`text-muted small ${fromMe ? 'text-end' : ''}`}>
        {fromMe ? 'Вы' : contactStore.getDisplayName(login)}, {time}
        {
          changeTime
            ? <span className="text-primary fst-italic" style={{marginLeft: 6}}>изменено</span>
            : null
        }
      </div>
    </div>
  )
}

export default observer(TextMessage)