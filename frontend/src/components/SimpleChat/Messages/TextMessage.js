import React from 'react'
import {observer} from 'mobx-react-lite'
import {useInView} from 'react-intersection-observer'
import {ContextMenuTrigger} from 'react-contextmenu'

import {useSocket} from '../../../contexts/SocketProvider'

import authStore from '../../../stores/authStore'
import addContactModalStore from '../../../stores/modals/addContactModalStore'
import contactStore from '../../../stores/contactStore'
import messagesStore from '../../../stores/messagesStore'
import messageContextMenuStore from '../../../stores/messageContextMenuStore'

import UserAvatar from '../../Avatars/UserAvatar'


const TextMessage = ({message, fromMe}) => {
  const {text, time, login, is_view: isView, message_id: messageId, change_time: changeTime} = message
  const {login: ownLogin} = authStore.user
  const {sendReadMessage} = useSocket()
  const { ref, inView } = useInView({
    threshold: 0
  })

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

  const isMessageFromOther = login !== ownLogin

  return (
    <>
      <div
        ref={ref}
        className={`d-flex ${fromMe ? 'flex-row-reverse' : 'flex-row'}`}
      >
        <div
          style={isMessageFromOther ? {cursor: 'pointer'} : null}
          onClick={isMessageFromOther ? showAddContactModal : null}
        >
          <UserAvatar login={login} size="sm" />
        </div>
        {/*TODO надо сделать что бы можно было редактировать столько свои сообщения*/}
        <ContextMenuTrigger id="message-context-menu">
          <div
            id={message.message_id}
            className={`text-break mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
            style={{cursor: 'context-menu'}}
            onContextMenu={onContextMenu}
          >
            {text}
          </div>
        </ContextMenuTrigger>
      </div>
      <div className={`text-muted small ${fromMe ? 'text-end' : ''}`}>
        {fromMe ? 'Вы' : contactStore.getDisplayName(login)}, {time}
        {
          changeTime
            ? <span className="text-primary fst-italic" style={{marginLeft: 6}}>изменено</span>
            : null
        }
      </div>
    </>
  )
}

export default observer(TextMessage)