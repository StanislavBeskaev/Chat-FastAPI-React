import React from 'react'
import {observer} from 'mobx-react-lite'
import {useInView} from 'react-intersection-observer'

import {useSocket} from '../../../contexts/SocketProvider'
import authStore from '../../../stores/authStore'
import addContactModalStore from '../../../stores/modals/addContactModalStore'
import contactStore from '../../../stores/contactStore'
import messagesStore from '../../../stores/messagesStore'
import UserAvatar from '../../Avatars/UserAvatar'


const TextMessage = ({message, fromMe}) => {
  const {sendReadMessage} = useSocket()
  const {text, time, login, is_read: isRead, message_id: messageId} = message
  const {login: ownLogin} = authStore.user
  const {selectedChatId} = messagesStore
  const { ref, inView } = useInView({
    threshold: 0
  })

  // TODO скорее всего надо выделить отдельный компонент не прочитанного сообщения
  if (isRead === false) {
    if (inView) {
      const currentChatId = selectedChatId
      setTimeout(() => {
        console.log("Отправляем запрос о прочтении:", messageId, text)
        sendReadMessage(messageId)
        messagesStore.markMessageAsRead(messageId,  currentChatId)
        // TODO константа для задержки
      }, 5000)
    }
  }

  const showAddContactModal = async () => {
    await addContactModalStore.showModalWithLogin(login)
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
        <div
          className={`text-break mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
        >
          {text}
        </div>
      </div>
      <div className={`text-muted small ${fromMe ? 'text-end' : ''}`}>
        {fromMe ? 'Вы' : contactStore.getDisplayName(login)}, {time}
      </div>
    </>
  )
}

export default observer(TextMessage)