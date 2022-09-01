import React from 'react'
import {Link} from 'react-router-dom'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import messagesStore from '../../stores/messagesStore'
import newChatModalStore from '../../stores/modals/newChatModalStore'
import socketStore from '../../stores/socketStore'
import FileAvatar from '../Avatars/FileAvatar'


const SidebarFooter = ({login}) => {
  const {selectedChatTyping, selectedChatId} = messagesStore

  const logout = async () => {
    if (selectedChatTyping) {
      socketStore.sendStopTyping(selectedChatId)
    }
    await authStore.logout()
  }

  return (
    <div className="p-3 border-top border-end small">
      <div className="d-flex flex-column">
        <div>
          <FileAvatar fileName={authStore.avatarFile} size="sm"/>
          <span className="ms-2">
            Ваш логин: <span className="text-muted">{login}</span>
          </span>
        </div>
        <div className="mt-3 d-flex gap-3">
          <Button size="sm" variant="primary" onClick={() => newChatModalStore.open()}>
            Новый чат
          </Button>
          <Button size="sm" variant="danger" onClick={logout}>
            Выход
          </Button>
        </div>
      </div>
      <div className="mt-3">
        <Link to="/user-data/">Данные пользователя</Link>
      </div>
    </div>
  )
}

export default observer(SidebarFooter)