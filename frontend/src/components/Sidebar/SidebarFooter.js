import React from 'react'
import {useHistory} from 'react-router-dom'
import {Button} from 'react-bootstrap'
import {observer} from 'mobx-react-lite'

import authStore from '../../stores/authStore'
import messagesStore from '../../stores/messagesStore'
import socketStore from '../../stores/socketStore'
import FileAvatar from '../Avatars/FileAvatar'
import NewChatButton from './NewChatButton'


const SidebarFooter = ({login}) => {
  const {selectedChatTyping, selectedChatId} = messagesStore
  const history = useHistory()
  const statusClassName = socketStore.isOnline() ? "bg-success" : "bg-danger"

  const onProfileClick = () => {
    history.push("/user-data/")
  }

  const logout = async () => {
    if (selectedChatTyping) {
      socketStore.sendStopTyping(selectedChatId)
    }
    await authStore.logout()
  }

  return (
    <div className="p-4 border-top border-end small">
      <div className="d-flex flex-column">
        <div className="d-flex justify-content-between">
          <FileAvatar fileName={authStore.avatarFile} size="xs"/>
          <NewChatButton />
        </div>
        <span className="mt-2 fs-6 d-flex align-items-center">
          <div>
            Ваш логин: <span className="text-muted">{login}</span>
          </div>
          <div
              className={`ms-2 align-self-center rounded-circle ${statusClassName}`}
              style={{width: 13, height: 13}}
          ></div>
        </span>
        <div className="mt-3 d-flex gap-3">
          <Button size="md" variant="primary" onClick={onProfileClick}>
            Профиль
          </Button>
          <Button size="md" variant="danger" onClick={logout} style={{width: 100}}>
            Выход
          </Button>
        </div>
      </div>
    </div>
  )
}

export default observer(SidebarFooter)