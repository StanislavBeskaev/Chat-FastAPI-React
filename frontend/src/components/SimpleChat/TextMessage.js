import React from 'react'
import {observer} from 'mobx-react-lite'

import AvatarMini from '../Avatars/AvatarMini'
import authStore from '../../stores/authStore'
import addContactModalStore from '../../stores/modals/addContactModalStore'
import contactStore from '../../stores/contactStore'


const TextMessage = ({message, fromMe}) => {
  const {avatar_file: avatarFile, text, time, login} = message
  const {login: ownLogin} = authStore.user

  const showAddContactModal = async () => {
    await addContactModalStore.showModalWithLogin(login)
  }

  const isMessageFromOther = login !== ownLogin

  return (
    <>
      <div className={`d-flex ${fromMe ? 'flex-row-reverse' : 'flex-row'}`}>
        <div
          style={isMessageFromOther ? {cursor: 'pointer'} : null}
          onClick={isMessageFromOther ? showAddContactModal : null}
        >
          <AvatarMini fileName={avatarFile}/>
        </div>
        <div
          className={`mx-2 rounded px-2 py-1 ${fromMe ? 'bg-primary text-white' : 'border'}`}
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